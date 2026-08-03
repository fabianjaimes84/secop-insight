from pydantic import BaseModel


class InfoGeneralHtmlDescarga(BaseModel):
    """Información general de un proceso SECOP I. Pestaña 'Información'."""

    entidad: str = ""
    nit_entidad: str = ""
    numero_proceso: str = ""
    titulo: str = ""
    descripcion: str = ""
    fase: str = ""
    fase_previa: str = ""
    estado: str = ""
    modalidad: str = ""
    tipo_contrato: str = ""
    limitado_mipyme: bool = False
    proceso_relacionado: str = ""
    sector: str = ""
    tiene_lotes: bool = False
    duracion_contrato: str = ""
    fecha_terminacion_contrato: str = ""
    direccion_ejecucion: str = ""
    usa_documentos_tipo: bool = False
    documentos_tipo_detalle: str = ""
    precio_estimado_total: str = ""


class EventoCronogramaHtmlDescarga(BaseModel):
    """Un hito del cronograma del proceso. Pestaña 'Cronograma'."""

    evento: str = ""
    fecha: str = ""
    zona_horaria: str = ""


class DocumentoHtmlDescarga(BaseModel):
    """Documento subido al proceso. Pestaña 'Documentos'."""

    nombre_documento: str = ""
    enlace: str = ""


class ProponenteHtmlDescarga(BaseModel):
    """Proveedor/proponente que respondió al proceso."""

    nombre: str = ""
    ciudad: str = ""


class ObservacionHtmlDescarga(BaseModel):
    """Observación o mensaje público del proceso. Pestaña 'Observaciones y mensajes'."""

    tipo: str = ""
    referencia: str = ""
    asunto: str = ""
    fecha: str = ""


class RequisitoHtmlDescarga(BaseModel):
    """Ítem del checklist de requisitos/documentos exigidos en el pliego."""

    item: str = ""
    descripcion: str = ""
    requiere_documento_adjunto: bool = False


class ProcesoHtmlDescargaExtraido(BaseModel):
    """Resultado completo de la extracción de un HTML de proceso SECOP I."""

    info_general: InfoGeneralHtmlDescarga
    cronograma: list[EventoCronogramaHtmlDescarga] = []
    documentos: list[DocumentoHtmlDescarga] = []
    proponentes: list[ProponenteHtmlDescarga] = []
    observaciones: list[ObservacionHtmlDescarga] = []
    requisitos: list[RequisitoHtmlDescarga] = []
