from typing import Optional

from fastapi import APIRouter

from app.models.busqueda import BusquedaProceso
from app.services.secop_service import SecopService

router = APIRouter(
    prefix="/procesos",
    tags=["Procesos"],
)

# Servicio principal de procesos
secop_service = SecopService()


@router.get("")
def obtener_procesos(
    limit: int = 5,
    buscar: Optional[str] = None,
    estado: Optional[str] = None,
):
    """Consulta rápida de procesos."""
    return secop_service.obtener_procesos(
        limit=limit,
        buscar=buscar,
        estado=estado,
    )


@router.get("/catalogos")
def obtener_catalogos():
    """Obtiene todos los catálogos."""
    return secop_service.obtener_catalogos()


@router.get("/catalogos/{campo}")
def obtener_catalogo(campo: str):
    """Obtiene un catálogo específico."""
    return secop_service.obtener_catalogo(campo)


@router.post("/busqueda")
def buscar_procesos(filtros: BusquedaProceso):
    """Realiza una búsqueda avanzada."""
    return secop_service.buscar_procesos(filtros)
