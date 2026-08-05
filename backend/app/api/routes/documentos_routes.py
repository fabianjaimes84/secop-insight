from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import obtener_db
from app.db.models import ProcesoHtmlDescarga, ProponentePerfil
from app.services.catalogo_formatos import formatos_aplicables

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
