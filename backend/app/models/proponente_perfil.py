from pydantic import BaseModel, ConfigDict

from app.models.empresa import EmpresaRespuesta, AccionistaRespuesta


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

    tipo: str = "natural"  # natural | juridica | consorcio | union_temporal
    nombre: str = ""
    codigo_proceso: str = ""

    representante_empresa_id: int | None = None

    # Información de lotes
    presenta_por_lotes: bool = False
    lotes_seleccionados: str = ""

    # Representantes que firman (accionistas)
    repre_principal_accionista_id: int | None = None
    repre_suplente_accionista_id: int | None = None

    # Información especial de la oferta
    pers_clave_eval: str = ""
    experiencia_requerida: str = ""

    # Póliza
    poliza_numero: str = ""
    poliza_vigencia: str = ""
    poliza_valor: float | None = None

    # Datos de la entidad contratante
    entidad_telefono: str = ""
    entidad_correo: str = ""
    entidad_horario: str = ""
    entidad_url_web: str = ""
    entidad_url_politica_datos: str = ""

    fecha_cierre: str = ""
    fecha_carta_gerencia: str = ""

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
    presenta_por_lotes: bool
    lotes_seleccionados: str
    repre_principal_accionista_id: int | None
    repre_suplente_accionista_id: int | None
    pers_clave_eval: str
    experiencia_requerida: str
    poliza_numero: str
    poliza_vigencia: str
    poliza_valor: float | None
    entidad_telefono: str
    entidad_correo: str
    entidad_horario: str
    entidad_url_web: str
    entidad_url_politica_datos: str
    fecha_cierre: str
    fecha_carta_gerencia: str
    integrantes: list[IntegranteRespuesta] = []
    representante_empresa: EmpresaRespuesta | None = None
    repre_principal: AccionistaRespuesta | None = None
    repre_suplente: AccionistaRespuesta | None = None


class ProponentePerfilResumen(BaseModel):
    """Fila para el selector de proponente."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    nombre: str
    codigo_proceso: str
