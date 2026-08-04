from pydantic import BaseModel, ConfigDict


class ContadorEntrada(BaseModel):
    nombre: str = ""
    cedula: str = ""
    mat_profe: str = ""
    rol: str = "contador"  # contador | revisor_fiscal


class ContadorRespuesta(ContadorEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int
