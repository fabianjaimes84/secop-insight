"""
Tablas de la base de datos para procesos de SECOP I extraídos de HTML.

Comportamiento al volver a importar el HTML del mismo proceso:
    - ProcesoHtmlDescarga        -> se ACTUALIZA (estado, fase, fase_previa, etc.)
    - CronogramaHtmlDescarga     -> se ACTUALIZA la fecha; si cambió, se registra
                               en CronogramaHistorialHtmlDescarga
    - DocumentoHtmlDescarga      -> se ACUMULA (solo se agregan los nuevos)
    - ProponenteHtmlDescarga     -> se ACUMULA (fijo una vez creado)
    - ObservacionHtmlDescarga    -> se ACUMULA (orden cronológico)
    - RequisitoHtmlDescarga      -> se ACTUALIZA (uso futuro: formatos)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class ProcesoHtmlDescarga(Base):
    """Tabla principal: un registro por proceso importado. Pestaña 'Información'."""

    __tablename__ = "procesos_html_descarga"

    id = Column(Integer, primary_key=True, index=True)

    numero_proceso = Column(String, unique=True, index=True)
    titulo = Column(String, default="")
    descripcion = Column(String, default="")

    entidad = Column(String, default="")
    nit_entidad = Column(String, default="")
    ubicacion = Column(String, default="")

    modalidad = Column(String, default="")
    tipo_contrato = Column(String, default="")
    limitado_mipyme = Column(Boolean, default=False)

    proceso_relacionado = Column(String, default="")
    sector = Column(String, default="")
    tiene_lotes = Column(Boolean, default=False)
    duracion_contrato = Column(String, default="")
    fecha_terminacion_contrato = Column(String, default="")
    direccion_ejecucion = Column(String, default="")
    usa_documentos_tipo = Column(Boolean, default=False)
    documentos_tipo_detalle = Column(String, default="")

    estado = Column(String, default="")
    fase = Column(String, default="")
    fase_previa = Column(String, default="")

    precio_base = Column(Float, nullable=True)
    valor_adjudicado = Column(Float, nullable=True)

    cronograma = relationship(
        "CronogramaHtmlDescarga", back_populates="proceso", cascade="all, delete-orphan"
    )
    documentos = relationship(
        "DocumentoHtmlDescarga", back_populates="proceso", cascade="all, delete-orphan"
    )
    proponentes = relationship(
        "ProponenteHtmlDescarga", back_populates="proceso", cascade="all, delete-orphan"
    )
    observaciones = relationship(
        "ObservacionHtmlDescarga", back_populates="proceso", cascade="all, delete-orphan"
    )
    requisitos = relationship(
        "RequisitoHtmlDescarga", back_populates="proceso", cascade="all, delete-orphan"
    )


class CronogramaHtmlDescarga(Base):
    """Eventos del proceso (20+ hitos: publicación, cierre, apertura, adjudicación, etc.)."""

    __tablename__ = "cronograma_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos_html_descarga.id"), nullable=False)

    evento = Column(String, default="")
    fecha = Column(String, default="")
    zona_horaria = Column(String, default="")

    proceso = relationship("ProcesoHtmlDescarga", back_populates="cronograma")
    historial = relationship(
        "CronogramaHistorialHtmlDescarga",
        back_populates="evento_cronograma",
        cascade="all, delete-orphan",
    )


class CronogramaHistorialHtmlDescarga(Base):
    """
    Registro de cambios de fecha en un evento del cronograma.
    Se crea automáticamente cuando, al reimportar, la fecha de un evento
    ya existente es distinta a la que había guardada. Pensado para
    alimentar alertas en el futuro dashboard de seguimiento.
    """

    __tablename__ = "cronograma_historial_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    cronograma_id = Column(Integer, ForeignKey("cronograma_html_descarga.id"), nullable=False)

    fecha_anterior = Column(String, default="")
    fecha_nueva = Column(String, default="")
    detectado_en = Column(String, default="")  # fecha/hora en que se detectó el cambio

    evento_cronograma = relationship("CronogramaHtmlDescarga", back_populates="historial")


class DocumentoHtmlDescarga(Base):
    """Documentos y pliegos del proceso. Se acumulan, nunca se sobrescriben."""

    __tablename__ = "documentos_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos_html_descarga.id"), nullable=False)

    nombre_documento = Column(String, default="")
    tipo = Column(String, default="")
    enlace = Column(String, default="")

    proceso = relationship("ProcesoHtmlDescarga", back_populates="documentos")


class ProponenteHtmlDescarga(Base):
    """Proveedores/proponentes que respondieron al proceso. Fijos una vez creados."""

    __tablename__ = "proponentes_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos_html_descarga.id"), nullable=False)

    nombre = Column(String, default="")
    ciudad = Column(String, default="")

    proceso = relationship("ProcesoHtmlDescarga", back_populates="proponentes")


class ObservacionHtmlDescarga(Base):
    """Observaciones y mensajes del proceso. Se acumulan en orden cronológico."""

    __tablename__ = "observaciones_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos_html_descarga.id"), nullable=False)

    tipo = Column(String, default="")
    referencia = Column(String, default="")  # código único del mensaje (ej. CO1.MSG.9788221)
    asunto = Column(String, default="")
    fecha = Column(String, default="")

    proceso = relationship("ProcesoHtmlDescarga", back_populates="observaciones")


class RequisitoHtmlDescarga(Base):
    """Checklist de requisitos/documentos exigidos en el pliego (uso futuro: formatos)."""

    __tablename__ = "requisitos_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos_html_descarga.id"), nullable=False)

    item = Column(String, default="")
    descripcion = Column(String, default="")
    requiere_documento = Column(Boolean, default=False)

    proceso = relationship("ProcesoHtmlDescarga", back_populates="requisitos")
