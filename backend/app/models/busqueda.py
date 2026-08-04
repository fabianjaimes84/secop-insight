from datetime import date
from pydantic import BaseModel


class BusquedaProceso(BaseModel):
    buscar: str | None = None

    estado: str | None = None
    tipo_proceso: str | None = None
    tipo_contrato: str | None = None

    fecha_publicacion_desde: date | None = None
    fecha_publicacion_hasta: date | None = None

    limit: int = 50
