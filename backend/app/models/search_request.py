from pydantic import BaseModel


class SearchRequest(BaseModel):
    search: str | None = None
    estado: str | None = None
    tipoProceso: str | None = None
    fechaPublicacionDesde: str | None = None
    fechaPublicacionHasta: str | None = None
