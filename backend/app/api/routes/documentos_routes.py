from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path
import tempfile

from app.db.base import obtener_db
from app.db.models import ProcesoHtmlDescarga, ProponentePerfil, AccionistaEmpresa
from app.services.catalogo_formatos import formatos_aplicables
from app.services.documentos_generador import generar_carta_presentacion

router = APIRouter(prefix="/documentos", tags=["documentos"])


class ItemChecklist(BaseModel):
    """Un documento que se puede generar para esta oferta."""

    codigo: str
    nombre: str
    # Nombre final del archivo, ya con el integrante si aplica
    nombre_archivo: str
    # Vacío si el documento es único para toda la oferta
    integrante: str = ""
    # Motivo por el que aplica (útil para entender el checklist)
    nota: str = ""


class RespuestaChecklist(BaseModel):
    numero_proceso: str
    entidad: str
    proponente: str
    tipo_proponente: str
    total: int
    items: list[ItemChecklist]


class FechasProceso(BaseModel):
    fecha_cierre: str = ""
    zona_cierre: str = ""
    fecha_carta_gerencia: str = ""


@router.get("/fechas/{codigo_proceso}", response_model=FechasProceso)
def obtener_fechas_proceso(codigo_proceso: str, db: Session = Depends(obtener_db)):
    """
    Trae la fecha de 'Presentación de Ofertas' del cronograma ya capturado
    del proceso, y calcula la fecha de la carta de gerencia (un día antes).
    """
    from datetime import datetime, timedelta
    import re

    proceso = (
        db.query(ProcesoHtmlDescarga)
        .filter(ProcesoHtmlDescarga.numero_proceso.like(f"{codigo_proceso}%"))
        .first()
    )
    if proceso is None:
        raise HTTPException(status_code=404, detail="El proceso no existe.")

    evento_cierre = next(
        (
            e
            for e in proceso.cronograma
            if "presentaci" in e.evento.lower() and "oferta" in e.evento.lower()
        ),
        None,
    )
    if evento_cierre is None:
        return FechasProceso()

    patron = re.compile(
        r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?",
        re.IGNORECASE,
    )
    coincidencia = patron.search(evento_cierre.fecha) or patron.search(
        evento_cierre.zona_horaria
    )

    fecha_cierre_formateada = ""
    fecha_carta = ""
    if coincidencia:
        dia, mes, anio, horas12, minutos, segundos, ampm = coincidencia.groups()
        horas = int(horas12)
        if ampm:
            es_pm = ampm.upper() == "PM"
            if es_pm and horas < 12:
                horas += 12
            if not es_pm and horas == 12:
                horas = 0
        try:
            fecha_cierre_dt = datetime(
                int(anio), int(mes), int(dia), horas, int(minutos), int(segundos or 0)
            )
            fecha_cierre_formateada = fecha_cierre_dt.strftime("%d/%m/%Y %H:%M")
            fecha_carta_dt = fecha_cierre_dt - timedelta(days=1)
            fecha_carta = fecha_carta_dt.strftime("%d/%m/%Y")
        except ValueError:
            fecha_cierre_formateada = evento_cierre.fecha

    return FechasProceso(
        fecha_cierre=fecha_cierre_formateada or evento_cierre.fecha,
        zona_cierre=evento_cierre.zona_horaria,
        fecha_carta_gerencia=fecha_carta,
    )


@router.get("/checklist", response_model=RespuestaChecklist)
def obtener_checklist(
    codigo_proceso: str,
    proponente_id: int,
    db: Session = Depends(obtener_db),
):
    """
    Arma la lista de documentos que hay que generar para una oferta,
    combinando el proceso (ya capturado de SECOP) con el proponente.

    Los formatos por integrante se repiten tantas veces como miembros
    tenga el consorcio o unión temporal, y los que dependen de un
    criterio solo aparecen para quienes lo cumplen.
    """
    proceso = (
        db.query(ProcesoHtmlDescarga)
        .filter(ProcesoHtmlDescarga.numero_proceso.like(f"{codigo_proceso}%"))
        .first()
    )
    if proceso is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No hay información de '{codigo_proceso}'. "
                "Ábrelo en SECOP con la extensión para capturarlo."
            ),
        )

    perfil = db.query(ProponentePerfil).filter_by(id=proponente_id).first()
    if perfil is None:
        raise HTTPException(status_code=404, detail="El proponente no existe.")

    items: list[ItemChecklist] = []

    for formato in formatos_aplicables(perfil.tipo):

        if formato.alcance == "proponente":
            items.append(
                ItemChecklist(
                    codigo=formato.codigo,
                    nombre=formato.nombre,
                    nombre_archivo=f"{formato.nombre}.docx",
                )
            )
            continue

        # Documentos que se generan una vez por integrante
        for integrante in perfil.integrantes:
            empresa = integrante.empresa

            if formato.criterio and not getattr(integrante, formato.criterio, False):
                continue

            nombre_integrante = empresa.nom_o_raz_social or "Integrante"

            items.append(
                ItemChecklist(
                    codigo=formato.codigo,
                    nombre=formato.nombre,
                    nombre_archivo=f"{formato.nombre} - {nombre_integrante}.docx",
                    integrante=nombre_integrante,
                    nota=(
                        f"Aplica porque acredita el criterio"
                        if formato.criterio
                        else ""
                    ),
                )
            )

    return RespuestaChecklist(
        numero_proceso=proceso.numero_proceso,
        entidad=proceso.entidad,
        proponente=perfil.nombre,
        tipo_proponente=perfil.tipo,
        total=len(items),
        items=items,
    )


@router.get("/generar/carta-presentacion/{proponente_id}")
def generar_carta_presentacion_endpoint(
    proponente_id: int,
    db: Session = Depends(obtener_db),
):
    """
    Genera la Carta de Presentación de Oferta para un proponente.
    Retorna el archivo Word descargable.
    """
    try:
        # Obtener proponente
        perfil = db.query(ProponentePerfil).filter(
            ProponentePerfil.id == proponente_id
        ).first()

        if not perfil:
            raise HTTPException(status_code=404, detail="Proponente no encontrado")

        # Validaciones
        if not perfil.codigo_proceso:
            raise HTTPException(
                status_code=400,
                detail="El proponente no tiene proceso asignado"
            )

        # Obtener datos del representante
        representante = perfil.representante_empresa
        if not representante:
            raise HTTPException(
                status_code=400,
                detail="El proponente no tiene empresa representante asignada. Ve a Paso 1 o Paso 2."
            )

        # Obtener accionista para obtener más datos
        accionista_principal = perfil.repre_principal
        if not accionista_principal:
            raise HTTPException(
                status_code=400,
                detail="El proponente no tiene representante legal (Paso 3) asignado"
            )

        # Crear documento temporal
        temp_dir = Path(tempfile.gettempdir()) / "secop_generados"
        temp_dir.mkdir(parents=True, exist_ok=True)

        nombre_archivo = f"Formato_1_{perfil.nombre.replace(' ', '_')}.docx"
        output_path = temp_dir / nombre_archivo

        # Obtener datos del proceso (buscar que contenga el código del proponente)
        proceso = db.query(ProcesoHtmlDescarga).filter(
            ProcesoHtmlDescarga.numero_proceso.like(f"{perfil.codigo_proceso}%")
        ).first()

        entidad = proceso.entidad if proceso else ""
        direccion_ejecucion = proceso.direccion_ejecucion if proceso else ""

        # Obtener accionistas de las empresas jurídicas que integran el proponente
        accionistas_data = []
        representante_legal_empresa = None
        if representante:
            # Obtener el representante legal de la empresa para datos de contacto
            accionistas_rep = db.query(AccionistaEmpresa).filter(
                AccionistaEmpresa.empresa_id == representante.id
            ).order_by(AccionistaEmpresa.orden).all()

            for accionista in accionistas_rep:
                if accionista.es_representante_legal:
                    representante_legal_empresa = accionista
                    break

        # Buscar empresas jurídicas entre los integrantes del proponente
        # y obtener sus accionistas
        for integrante in perfil.integrantes:
            if integrante.empresa and integrante.empresa.es_persona_juridica:
                # Esta es una empresa jurídica - obtener sus accionistas
                accionistas_empresa = db.query(AccionistaEmpresa).filter(
                    AccionistaEmpresa.empresa_id == integrante.empresa_id
                ).order_by(AccionistaEmpresa.orden).limit(2).all()

                # Agregar los accionistas de esta empresa jurídica
                for accionista in accionistas_empresa:
                    accionistas_data.append({
                        "nombre": accionista.nombre,
                        "cedula": accionista.cedula,
                        "porcentaje": accionista.porcentaje or "",
                    })

        # Obtener integrante para datos de grupo empresarial
        integrante_representante = None
        for integrante in perfil.integrantes:
            if integrante.empresa_id == perfil.representante_empresa_id:
                integrante_representante = integrante
                break

        # Usar datos del representante legal de la empresa si están disponibles
        # Si no, usar datos de la empresa como fallback
        direccion_contacto = ""
        correo_contacto = ""
        telefono_contacto = ""
        ciudad_contacto = ""
        matricula_profesional = ""

        if representante_legal_empresa:
            direccion_contacto = representante_legal_empresa.direccion or representante.direccion or ""
            correo_contacto = representante_legal_empresa.email or representante.correo or ""
            telefono_contacto = representante_legal_empresa.telefono or representante.telefono_fijo or representante.telefono_celular or ""
            ciudad_contacto = representante.ciudad or ""
            matricula_profesional = representante_legal_empresa.matricula_profesional or ""
        else:
            # Fallback: usar datos de la empresa
            direccion_contacto = representante.direccion or ""
            correo_contacto = representante.correo or ""
            telefono_contacto = representante.telefono_fijo or representante.telefono_celular or ""
            ciudad_contacto = representante.ciudad or ""

        # Generar carta
        exito = generar_carta_presentacion(
            nombre_proponente=perfil.nombre,
            numero_proceso=perfil.codigo_proceso,
            objeto_proceso=proceso.descripcion if proceso else "",
            nombre_representante=accionista_principal.nombre,
            cedula_representante=accionista_principal.cedula,
            direccion=direccion_contacto,
            correo=correo_contacto,
            telefono=telefono_contacto,
            ciudad=ciudad_contacto,
            matricula_profesional=matricula_profesional,
            tipo_proponente=perfil.tipo,
            pertenece_grupo=integrante_representante.pertenece_grupo if integrante_representante else False,
            tipo_grupo=integrante_representante.tipo_grupo_empresarial if integrante_representante else "",
            cotiza_bolsa=integrante_representante.cotiza_bolsa if integrante_representante else False,
            accionistas=accionistas_data,
            entidad=entidad,
            direccion_ejecucion=direccion_ejecucion,
            lotes=perfil.lotes_seleccionados,
            salida_path=output_path,
        )

        if not exito:
            raise HTTPException(
                status_code=500,
                detail="Error al generar el documento. Verifica que la plantilla exista."
            )

        # Retornar archivo descargable
        return FileResponse(
            path=output_path,
            filename=nombre_archivo,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
