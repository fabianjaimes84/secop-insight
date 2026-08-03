from pydantic import BaseModel, ConfigDict


class ProcesoHtmlDescargaResumen(BaseModel):
    """Fila resumida para el listado de procesos guardados."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_proceso: str
    titulo: str
    entidad: str
    estado: str
    fase: str


class EventoCronogramaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evento: str
    fecha: str
    zona_horaria: str


class DocumentoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre_documento: str
    enlace: str


class ProponenteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str
    ciudad: str


class ObservacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: str
    referencia: str
    asunto: str
    fecha: str


class RequisitoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item: str
    descripcion: str
    requiere_documento: bool


class ProcesoHtmlDescargaDetalle(BaseModel):
    """
    Detalle completo de un proceso guardado: alimenta directamente las
    4 pestañas del modal (Información, Cronograma, Documentos, Observaciones).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_proceso: str
    titulo: str
    descripcion: str

    entidad: str
    nit_entidad: str
    ubicacion: str

    modalidad: str
    tipo_contrato: str
    limitado_mipyme: bool
    proceso_relacionado: str
    sector: str
    tiene_lotes: bool
    duracion_contrato: str
    fecha_terminacion_contrato: str
    direccion_ejecucion: str
    usa_documentos_tipo: bool
    documentos_tipo_detalle: str

    estado: str
    fase: str
    fase_previa: str

    precio_base: float | None
    valor_adjudicado: float | None

    cronograma: list[EventoCronogramaRespuesta]
    documentos: list[DocumentoRespuesta]
    proponentes: list[ProponenteRespuesta]
    observaciones: list[ObservacionRespuesta]
    requisitos: list[RequisitoRespuesta]
