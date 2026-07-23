from pydantic import BaseModel


class Proceso(BaseModel):
    entidad: str
    nit_entidad: str
    departamento: str
    ciudad: str
    numero_proceso: str
    objeto: str
    modalidad: str
    estado: str
    fecha_publicacion: str
