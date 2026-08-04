import re
import unicodedata
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import obtener_db
from app.db.models import ProcesoHtmlDescarga
from app.models.html_descarga_consulta import ProcesoHtmlDescargaDetalle, ProcesoHtmlDescargaResumen
from app.repositories.html_descarga_repository import HtmlDescargaRepository
from app.services.html_descarga_service import HtmlDescargaService, HtmlDescargaServiceError
from app.core.logger import logger

router = APIRouter(prefix="/html-descarga", tags=["html-descarga"])

service = HtmlDescargaService()

# Marca de tiempo de la última captura registrada. El frontend la consulta
# periódicamente para saber si debe refrescar sus datos, sin recargar la
# página completa.
ULTIMA_CAPTURA = {"momento": "", "numero_proceso": ""}

EXTENSIONES_PERMITIDAS = (".htm", ".html")
TAMANO_MAXIMO_MB = 15

# Carpeta backend/documentos/{codigo_proceso}/, donde el usuario guarda
# manualmente el HTML descargado de SECOP I para cada proceso.
DESCARGAS_DIR = Path(__file__).resolve().parents[3] / "documentos"


class RespuestaImportacionHtmlDescarga(BaseModel):
    """Confirmación de que el proceso se guardó correctamente en la base de datos."""

    proceso_id: int
    numero_proceso: str
    mensaje: str
    total_eventos_cronograma: int
    total_documentos: int
    total_proponentes: int
    total_observaciones: int
    total_requisitos: int


@router.post("/importar-html", response_model=RespuestaImportacionHtmlDescarga)
async def importar_html_descarga(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_db),
):
    """
    Recibe un archivo HTML de detalle de proceso descargado manualmente
    desde SECOP I, extrae su información y la guarda en la base de datos
    (crea el proceso si es nuevo, o lo actualiza si ya existía).
    """
    if not archivo.filename.lower().endswith(EXTENSIONES_PERMITIDAS):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un HTML (.htm o .html).",
        )

    contenido_bytes = await archivo.read()

    if len(contenido_bytes) > TAMANO_MAXIMO_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el tamaño máximo permitido ({TAMANO_MAXIMO_MB} MB).",
        )

    try:
        contenido_html = contenido_bytes.decode("utf-8", errors="ignore")
        datos_extraidos = service.procesar_html(contenido_html)

        # En una subida manual no hay archivo en disco del cual leer la fecha
        # de descarga, así que se usa el momento de la importación.
        repositorio = HtmlDescargaRepository(db)
        proceso_guardado = repositorio.guardar_proceso(
            datos_extraidos,
            fecha_descarga=datetime.now().isoformat(timespec="seconds"),
        )

        return RespuestaImportacionHtmlDescarga(
            proceso_id=proceso_guardado.id,
            numero_proceso=proceso_guardado.numero_proceso,
            mensaje="Proceso guardado correctamente.",
            total_eventos_cronograma=len(proceso_guardado.cronograma),
            total_documentos=len(proceso_guardado.documentos),
            total_proponentes=len(proceso_guardado.proponentes),
            total_observaciones=len(proceso_guardado.observaciones),
            total_requisitos=len(proceso_guardado.requisitos),
        )

    except HtmlDescargaServiceError as e:
        logger.error(f"Error de negocio importando HTML SECOP I: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.exception(f"Error inesperado importando HTML SECOP I: {e}")
        raise HTTPException(
            status_code=500, detail="Error interno procesando el archivo."
        )


def _normalizar(texto: str) -> str:
    """Quita tildes y pasa a minúsculas, para comparar nombres de eventos."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return sin_tildes.lower().strip()


_PATRON_FECHA = re.compile(
    r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?",
    re.IGNORECASE,
)


def _parsear_fecha_evento(fecha: str, zona_horaria: str) -> datetime | None:
    """
    Igual que en el modal (Angular): la fecha real puede venir directa en
    'fecha', o escondida dentro de 'zona_horaria' cuando el texto de 'fecha'
    es relativo (ej. '26 días de tiempo transcurrido').
    """
    coincidencia = _PATRON_FECHA.search(fecha) or _PATRON_FECHA.search(zona_horaria)
    if not coincidencia:
        return None

    dia, mes, anio, horas12, minutos, segundos, ampm = coincidencia.groups()
    horas = int(horas12)
    if ampm:
        es_pm = ampm.upper() == "PM"
        if es_pm and horas < 12:
            horas += 12
        if not es_pm and horas == 12:
            horas = 0

    try:
        return datetime(
            int(anio), int(mes), int(dia), horas, int(minutos), int(segundos or 0)
        )
    except ValueError:
        return None


def _buscar_evento_por_nombre(cronograma, nombre_exacto: str, contiene: list[str]):
    """Busca primero por nombre exacto; si no aparece, por coincidencia parcial."""
    exacto = next(
        (e for e in cronograma if _normalizar(e.evento) == nombre_exacto), None
    )
    if exacto:
        return exacto

    return next(
        (
            e
            for e in cronograma
            if all(palabra in _normalizar(e.evento) for palabra in contiene)
        ),
        None,
    )


def _proximo_evento_pendiente(cronograma):
    """El evento del cronograma con la fecha más próxima que aún no ha pasado."""
    ahora = datetime.now()
    candidatos = []

    for evento in cronograma:
        fecha = _parsear_fecha_evento(evento.fecha, evento.zona_horaria)
        if fecha and fecha >= ahora:
            candidatos.append((fecha, evento))

    if not candidatos:
        return None

    candidatos.sort(key=lambda par: par[0])
    return candidatos[0][1]


def _evento_anterior(cronograma):
    """
    El evento más reciente cuya fecha YA pasó, es decir, el hito
    inmediatamente anterior al próximo pendiente.
    """
    ahora = datetime.now()
    pasados = []

    for evento in cronograma:
        fecha = _parsear_fecha_evento(evento.fecha, evento.zona_horaria)
        if fecha and fecha < ahora:
            pasados.append((fecha, evento))

    if not pasados:
        return None

    pasados.sort(key=lambda par: par[0], reverse=True)
    return pasados[0][1]


class HtmlCapturado(BaseModel):
    """HTML de un proceso enviado directamente desde la extensión del navegador."""

    html: str
    url: str = ""


@router.post("/capturar", response_model=RespuestaImportacionHtmlDescarga)
def capturar_html_navegador(
    datos: HtmlCapturado,
    db: Session = Depends(obtener_db),
):
    """
    Recibe el HTML de un proceso capturado por la extensión del navegador,
    justo después de que el usuario pasó el reCAPTCHA. No se descarga ningún
    archivo: el HTML viaja directo del navegador al backend.
    """
    try:
        datos_extraidos = service.procesar_html(datos.html)

        if not datos_extraidos.info_general.numero_proceso:
            raise HTTPException(
                status_code=422,
                detail="El HTML recibido no corresponde a un proceso de SECOP.",
            )

        repositorio = HtmlDescargaRepository(db)
        proceso_guardado = repositorio.guardar_proceso(
            datos_extraidos,
            fecha_descarga=datetime.now().isoformat(timespec="seconds"),
        )

        logger.info(
            f"Proceso capturado desde el navegador: {proceso_guardado.numero_proceso}"
        )

        # Se deja constancia para que la app detecte la novedad y refresque
        # sus datos sin que el usuario recargue la página.
        ULTIMA_CAPTURA["momento"] = datetime.now().isoformat(timespec="seconds")
        ULTIMA_CAPTURA["numero_proceso"] = proceso_guardado.numero_proceso

        return RespuestaImportacionHtmlDescarga(
            proceso_id=proceso_guardado.id,
            numero_proceso=proceso_guardado.numero_proceso,
            mensaje="Proceso capturado y guardado correctamente.",
            total_eventos_cronograma=len(proceso_guardado.cronograma),
            total_documentos=len(proceso_guardado.documentos),
            total_proponentes=len(proceso_guardado.proponentes),
            total_observaciones=len(proceso_guardado.observaciones),
            total_requisitos=len(proceso_guardado.requisitos),
        )

    except HTTPException:
        raise
    except HtmlDescargaServiceError as e:
        logger.error(f"Error de negocio capturando HTML: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.exception(f"Error inesperado capturando HTML: {e}")
        raise HTTPException(
            status_code=500, detail="Error interno procesando el HTML capturado."
        )


@router.get("/procesos", response_model=list[ProcesoHtmlDescargaResumen])
def listar_procesos(db: Session = Depends(obtener_db)):
    """Lista resumida de todos los procesos SECOP I guardados, más recientes primero."""
    procesos = db.query(ProcesoHtmlDescarga).order_by(ProcesoHtmlDescarga.id.desc()).all()

    resultado = []
    for proceso in procesos:
        evento_ofertas = _buscar_evento_por_nombre(
            proceso.cronograma, "presentacion de ofertas", ["presentaci", "oferta"]
        )
        evento_adenda = _buscar_evento_por_nombre(
            proceso.cronograma,
            "plazo maximo para expedir adendas",
            ["plazo", "adenda"],
        )
        proximo = _proximo_evento_pendiente(proceso.cronograma)
        anterior = _evento_anterior(proceso.cronograma)

        resultado.append(
            ProcesoHtmlDescargaResumen(
                id=proceso.id,
                numero_proceso=proceso.numero_proceso,
                titulo=proceso.titulo,
                entidad=proceso.entidad,
                estado=proceso.estado,
                fase=proceso.fase,
                ultima_actualizacion=proceso.ultima_actualizacion or "",
                fecha_presentacion_ofertas=(
                    evento_ofertas.fecha if evento_ofertas else ""
                ),
                zona_presentacion_ofertas=(
                    evento_ofertas.zona_horaria if evento_ofertas else ""
                ),
                fecha_adenda=evento_adenda.fecha if evento_adenda else "",
                zona_adenda=evento_adenda.zona_horaria if evento_adenda else "",
                proximo_evento_nombre=proximo.evento if proximo else "",
                proximo_evento_fecha=proximo.fecha if proximo else "",
                proximo_evento_zona=proximo.zona_horaria if proximo else "",
                evento_anterior_nombre=anterior.evento if anterior else "",
                evento_anterior_fecha=anterior.fecha if anterior else "",
                evento_anterior_zona=anterior.zona_horaria if anterior else "",
            )
        )

    return resultado


@router.get("/procesos/{proceso_id}", response_model=ProcesoHtmlDescargaDetalle)
def obtener_proceso(proceso_id: int, db: Session = Depends(obtener_db)):
    """
    Detalle completo de un proceso guardado, con toda su información:
    cronograma, documentos, proponentes, observaciones y requisitos.
    Este es el endpoint que alimenta el modal con las 4 pestañas.
    """
    proceso = db.query(ProcesoHtmlDescarga).filter_by(id=proceso_id).first()
    if proceso is None:
        raise HTTPException(
            status_code=404, detail=f"No existe un proceso con id={proceso_id}."
        )
    return proceso


@router.get("/ultima-captura")
def obtener_ultima_captura():
    """
    Devuelve cuándo se capturó el último proceso. La app consulta este
    endpoint cada pocos segundos: si el valor cambió, refresca sus datos
    automáticamente, sin necesidad de recargar la página.
    """
    return ULTIMA_CAPTURA


@router.get("/proceso-por-codigo/{codigo_proceso}", response_model=ProcesoHtmlDescargaDetalle)
def obtener_proceso_por_codigo(codigo_proceso: str, db: Session = Depends(obtener_db)):
    """
    Devuelve, sin importar ni modificar nada, la información ya guardada de
    un proceso a partir de su código base (ej. 'CM-GB-010-2026'). Es lo que
    consulta el modal al abrirse.
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
                f"Aún no hay información ampliada de '{codigo_proceso}'. "
                "Ábrelo en SECOP con la extensión activa para capturarlo."
            ),
        )

    return proceso


@router.post("/actualizar/{codigo_proceso}", response_model=ProcesoHtmlDescargaDetalle)
def actualizar_desde_carpeta(codigo_proceso: str, db: Session = Depends(obtener_db)):
    """
    Busca en 'backend/documentos/{codigo_proceso}/' el HTML descargado
    manualmente de SECOP II, lo procesa y actualiza la base de datos. Devuelve
    el detalle completo ya actualizado, listo para mostrar en el modal.

    Si no hay carpeta (por ejemplo, porque el proceso llegó a través de la
    extensión del navegador y nunca se descargó un archivo), se devuelve la
    información que ya está guardada en la base de datos.
    """
    carpeta = DESCARGAS_DIR / codigo_proceso
    archivos_html = []

    if carpeta.is_dir():
        archivos_html = list(carpeta.glob("*.htm")) + list(carpeta.glob("*.html"))

    if not archivos_html:
        guardado = (
            db.query(ProcesoHtmlDescarga)
            .filter(ProcesoHtmlDescarga.numero_proceso.like(f"{codigo_proceso}%"))
            .first()
        )

        if guardado:
            logger.info(
                f"Sin archivo local para '{codigo_proceso}'. "
                "Se devuelve la información ya guardada en la base de datos."
            )
            return guardado

        raise HTTPException(
            status_code=404,
            detail=(
                f"No hay información de '{codigo_proceso}'. Ábrelo en SECOP con "
                "la extensión activa, o guarda su HTML en "
                f"'documentos/{codigo_proceso}'."
            ),
        )

    try:
        archivo_html = archivos_html[0]
        contenido_html = archivo_html.read_text(encoding="utf-8", errors="ignore")
        datos_extraidos = service.procesar_html(contenido_html)

        # La "última actualización" es la fecha real en que se descargó el
        # archivo HTML desde SECOP II (fecha de modificación del archivo en
        # disco), NO el momento en que se importó a la base de datos.
        fecha_archivo = datetime.fromtimestamp(
            archivo_html.stat().st_mtime
        ).isoformat(timespec="seconds")

        repositorio = HtmlDescargaRepository(db)
        proceso_guardado = repositorio.guardar_proceso(
            datos_extraidos, fecha_descarga=fecha_archivo
        )
        return proceso_guardado

    except HtmlDescargaServiceError as e:
        logger.error(f"Error de negocio actualizando desde carpeta: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.exception(f"Error inesperado actualizando desde carpeta: {e}")
        raise HTTPException(
            status_code=500, detail="Error interno actualizando el proceso."
        )
