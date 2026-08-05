from pydantic import BaseModel, ConfigDict

from app.models.contador import ContadorRespuesta


class AccionistaEntrada(BaseModel):
    """Socio o accionista de una empresa."""

    nombre: str = ""
    cedula: str = ""

    # Participación
    orden: int = 1
    porcentaje: str = ""
    es_representante_legal: bool = False

    # Datos de contacto del accionista
    direccion: str = ""
    email: str = ""
    telefono: str = ""

    # Matrícula profesional
    tiene_matricula_profesional: bool = False
    matricula_profesional: str = ""


class AccionistaRespuesta(AccionistaEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EmpresaEntrada(BaseModel):
    """Datos de una empresa o persona natural del catálogo."""

    nom_o_raz_social: str = ""
    nit: str = ""
    es_persona_juridica: bool = False

    # Datos corporativos de la empresa
    direccion: str = ""
    ciudad: str = ""
    correo: str = ""
    telefono_fijo: str = ""
    telefono_celular: str = ""

    # Contador o revisor fiscal, del catálogo (opcional)
    contador_id: int | None = None

    accionistas: list[AccionistaEntrada] = []


class EmpresaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_o_raz_social: str
    nit: str
    es_persona_juridica: bool

    direccion: str
    ciudad: str
    correo: str
    telefono_fijo: str
    telefono_celular: str

    contador_id: int | None
    contador: ContadorRespuesta | None = None

    accionistas: list[AccionistaRespuesta] = []
