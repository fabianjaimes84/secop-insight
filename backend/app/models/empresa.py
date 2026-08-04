from pydantic import BaseModel, ConfigDict

from app.models.contador import ContadorRespuesta


class AccionistaEntrada(BaseModel):
    """Socio o accionista de una empresa."""

    orden: int = 1
    nombre: str = ""
    cedula: str = ""
    porcentaje: str = ""


class AccionistaRespuesta(AccionistaEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EmpresaEntrada(BaseModel):
    """Datos de una empresa o persona natural del catálogo."""

    nom_o_raz_social: str = ""
    nit: str = ""
    es_persona_juridica: bool = False

    # Representante legal (una persona natural se representa a sí misma)
    repre_nombre: str = ""
    repre_cedula: str = ""
    repre_mat_profe: str = ""

    # Contacto, se usa cuando esta empresa lidera el proponente
    contac_direccion: str = ""
    contac_ciudad: str = ""
    contac_email: str = ""
    contac_tele: str = ""
    contac_telefax: str = ""

    # Contador o revisor fiscal, del catálogo (opcional)
    contador_id: int | None = None

    accionistas: list[AccionistaEntrada] = []


class EmpresaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_o_raz_social: str
    nit: str
    es_persona_juridica: bool

    repre_nombre: str
    repre_cedula: str
    repre_mat_profe: str

    contac_direccion: str
    contac_ciudad: str
    contac_email: str
    contac_tele: str
    contac_telefax: str

    contador_id: int | None
    contador: ContadorRespuesta | None = None

    accionistas: list[AccionistaRespuesta] = []
