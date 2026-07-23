from pydantic import BaseModel


class FiltrosProceso(BaseModel):
    buscar: str | None = None
    estado: str | None = None
    departamento: str | None = None
    ciudad: str | None = None
    entidad: str | None = None
    modalidad: str | None = None
    limit: int = 10
