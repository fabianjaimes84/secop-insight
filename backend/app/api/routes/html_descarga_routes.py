import re
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

        repositorio = HtmlDescargaRepository(db)
        proceso_guardado = repositorio.guardar_proceso(datos_extraidos)

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


@router.get("/procesos", response_model=list[ProcesoHtmlDescargaResumen])
def listar_procesos(db: Session = Depends(obtener_db)):
    """Lista resumida de todos los procesos SECOP I guardados, más recientes primero."""
    return db.query(ProcesoHtmlDescarga).order_by(ProcesoHtmlDescarga.id.desc()).all()


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


@router.post("/actualizar/{codigo_proceso}", response_model=ProcesoHtmlDescargaDetalle)
def actualizar_desde_carpeta(codigo_proceso: str, db: Session = Depends(obtener_db)):
    """
    Busca en 'backend/documentos/{codigo_proceso}/' el HTML descargado
    manualmente de SECOP I, lo procesa y actualiza la base de datos. Devuelve
    el detalle completo ya actualizado, listo para mostrar en el modal.
    """
    carpeta = DESCARGAS_DIR / codigo_proceso

    if not carpeta.is_dir():
        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe la carpeta 'documentos/{codigo_proceso}'. "
                "Créala y guarda ahí el HTML descargado de SECOP I."
            ),
        )

    archivos_html = list(carpeta.glob("*.htm")) + list(carpeta.glob("*.html"))
    if not archivos_html:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No se encontró ningún archivo .htm/.html dentro de "
                f"'documentos/{codigo_proceso}'."
            ),
        )

    try:
        contenido_html = archivos_html[0].read_text(encoding="utf-8", errors="ignore")
        datos_extraidos = service.procesar_html(contenido_html)

        repositorio = HtmlDescargaRepository(db)
        proceso_guardado = repositorio.guardar_proceso(datos_extraidos)
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
