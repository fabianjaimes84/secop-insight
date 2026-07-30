from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.services.secop_service import SecopService
from app.models.busqueda import BusquedaProceso
from app.models.proceso import Proceso
from app.core.logger import logger

# Definición del router (Debe estar al inicio y sin indentación)
router = APIRouter(prefix="/procesos", tags=["procesos"])

service = SecopService()


@router.get("/", response_model=List[Proceso])
async def listar_procesos(
    limit: int = Query(5, ge=1, le=50),
    buscar: Optional[str] = None,
    estado: Optional[str] = None,
):
    """Obtiene una lista rápida de procesos."""
    resultados = await service.obtener_procesos(
        limit=limit, buscar=buscar, estado=estado
    )

    # Si el servicio devuelve un dict de error
    if isinstance(resultados, dict) and "error" in resultados:
        raise HTTPException(status_code=503, detail=resultados)

    return resultados


@router.get("/catalogos")
async def listar_catalogos():
    """Obtiene los catálogos únicos para los filtros."""
    try:
        catalogos = await service.obtener_catalogos()
        return catalogos
    except Exception as e:
        logger.error(f"Error crítico en catálogos: {e}")
        raise HTTPException(status_code=500, detail="Error cargando catálogos")


@router.post("/busqueda", response_model=List[Proceso])
async def buscar_procesos(filtros: BusquedaProceso):
    """Realiza una búsqueda avanzada con filtros complejos."""
    resultados = await service.buscar_procesos(filtros)

    # Si el servicio devuelve un dict de error
    if isinstance(resultados, dict) and "error" in resultados:
        raise HTTPException(status_code=503, detail=resultados)

    return resultados
