from pydantic import BaseModel, ConfigDict

from app.models.empresa import EmpresaRespuesta


class IntegranteEntrada(BaseModel):
    """La participación de una empresa en un proponente, para esta oferta."""

    empresa_id: int
    orden: int = 1
    compromiso: str = ""
    es_lider: bool = False

    pertenece_grupo: bool = False
    cotiza_bolsa: bool = False

    acredita_mujeres: bool = False
    acredita_discapacidad: bool = False
    acredita_mipyme: bool = False


class ProponentePerfilEntrada(BaseModel):
    """Datos que se envían al crear o editar un proponente."""

    tipo: str = "natural"  # natural | consorcio | union_temporal
    nombre: str = ""
    codigo_proceso: str = ""

    representante_empresa_id: int | None = None

    entidad_telefono: str = ""
    entidad_pagina: str = ""
    entidad_horario: str = ""
    entidad_correo: str = ""

    fecha_cierre: str = ""
    fecha_carta_gerencia: str = ""

    pers_clave_eval: str = ""

    integrantes: list[IntegranteEntrada] = []


class IntegranteRespuesta(BaseModel):
    """La participación, ya con los datos completos de la empresa."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    orden: int
    compromiso: str
    es_lider: bool
    pertenece_grupo: bool
    cotiza_bolsa: bool
    acredita_mujeres: bool
    acredita_discapacidad: bool
    acredita_mipyme: bool
    empresa: EmpresaRespuesta


class ProponentePerfilRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    nombre: str
    codigo_proceso: str
    representante_empresa_id: int | None
    entidad_telefono: str
    entidad_pagina: str
    entidad_horario: str
    entidad_correo: str
    fecha_cierre: str
    fecha_carta_gerencia: str
    pers_clave_eval: str
    integrantes: list[IntegranteRespuesta] = []
    representante_empresa: EmpresaRespuesta | None = None


class ProponentePerfilResumen(BaseModel):
    """Fila para el selector de proponente."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    nombre: str
    codigo_proceso: str
