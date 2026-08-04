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

    # Fecha/hora (ISO) de la última vez que se importó el HTML de este proceso.
    ultima_actualizacion = Column(String, default="")

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


class Contador(Base):
    """
    Catálogo de contadores/revisores fiscales, reutilizables entre empresas.
    Una misma persona puede ser el contador de varias empresas distintas.
    """

    __tablename__ = "contadores"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, default="")
    cedula = Column(String, default="")
    mat_profe = Column(String, default="")
    # 'contador' o 'revisor_fiscal'
    rol = Column(String, default="contador")

    empresas = relationship("Empresa", back_populates="contador")


class Empresa(Base):
    """
    Catálogo de empresas y personas naturales con las que se concursa.
    Se registran una sola vez y se reutilizan en cada oferta.
    """

    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)

    nom_o_raz_social = Column(String, unique=True, index=True)
    nit = Column(String, default="")
    es_persona_juridica = Column(Boolean, default=False)

    # Representante legal. En una persona natural, se representa a sí misma.
    repre_nombre = Column(String, default="")
    repre_cedula = Column(String, default="")
    repre_mat_profe = Column(String, default="")

    # Datos de contacto, que se usan cuando esta empresa es la líder.
    contac_direccion = Column(String, default="")
    contac_ciudad = Column(String, default="")
    contac_email = Column(String, default="")
    contac_tele = Column(String, default="")
    contac_telefax = Column(String, default="")

    # Contador o revisor fiscal, elegido del catálogo (opcional).
    contador_id = Column(Integer, ForeignKey("contadores.id"), nullable=True)

    accionistas = relationship(
        "AccionistaEmpresa",
        back_populates="empresa",
        cascade="all, delete-orphan",
        order_by="AccionistaEmpresa.orden",
    )

    contador = relationship("Contador", back_populates="empresas")

    participaciones = relationship(
        "IntegranteProponente", back_populates="empresa"
    )


class AccionistaEmpresa(Base):
    """
    Socio o accionista de una empresa, con su porcentaje de participación.
    Se usa en los formatos de factores de desempate.
    """

    __tablename__ = "accionistas_empresa"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    orden = Column(Integer, default=1)
    nombre = Column(String, default="")
    cedula = Column(String, default="")
    porcentaje = Column(String, default="")

    empresa = relationship("Empresa", back_populates="accionistas")


class ProponentePerfil(Base):
    """
    Un proponente para una oferta: puede ser una sola empresa (persona
    natural o jurídica) o la unión de varias en consorcio o unión temporal.
    """

    __tablename__ = "proponentes_perfil"

    id = Column(Integer, primary_key=True, index=True)

    # 'natural', 'consorcio' o 'union_temporal'
    tipo = Column(String, default="natural")
    # Nombre único de la oferta: "UNION TEMPORAL VIALTEK 16"
    nombre = Column(String, unique=True, index=True)

    # Proceso al que se presenta. Un proceso tiene un solo proponente.
    codigo_proceso = Column(String, default="", index=True)

    # Quién firma los formatos. Siempre es el representante legal de una
    # de las empresas que conforman el proponente.
    representante_empresa_id = Column(
        Integer, ForeignKey("empresas.id"), nullable=True
    )

    # Datos de la entidad contratante para el Formato 11 (no siempre
    # vienen completos en lo que trae SECOP).
    entidad_telefono = Column(String, default="")
    entidad_pagina = Column(String, default="")
    entidad_horario = Column(String, default="")
    entidad_correo = Column(String, default="")

    # Fechas clave de esta oferta. El cierre se trae del cronograma del
    # proceso; la carta de gerencia se calcula un día antes del cierre.
    fecha_cierre = Column(String, default="")
    fecha_carta_gerencia = Column(String, default="")

    # Personal clave evaluable (texto libre, se repite entre ofertas)
    pers_clave_eval = Column(String, default="")

    representante_empresa = relationship("Empresa", foreign_keys=[representante_empresa_id])

    integrantes = relationship(
        "IntegranteProponente",
        back_populates="perfil",
        cascade="all, delete-orphan",
        order_by="IntegranteProponente.orden",
    )


class IntegranteProponente(Base):
    """
    La participación de una empresa dentro de un proponente concreto.
    Solo guarda lo que cambia entre ofertas: el porcentaje y si lidera.
    Los demás datos vienen de la empresa referenciada.
    """

    __tablename__ = "integrantes_proponente"

    id = Column(Integer, primary_key=True, index=True)
    perfil_id = Column(Integer, ForeignKey("proponentes_perfil.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    orden = Column(Integer, default=1)
    compromiso = Column(String, default="")  # porcentaje de participación
    es_lider = Column(Boolean, default=False)

    # Estas marcas dependen de la empresa Y de la oferta concreta, así
    # que se preguntan aquí (por integrante), no en el catálogo de empresas.
    pertenece_grupo = Column(Boolean, default=False)
    cotiza_bolsa = Column(Boolean, default=False)

    # Criterios que este integrante acredita PARA ESTA oferta.
    acredita_mujeres = Column(Boolean, default=False)       # Formato 13
    acredita_discapacidad = Column(Boolean, default=False)  # Formato 6
    acredita_mipyme = Column(Boolean, default=False)

    perfil = relationship("ProponentePerfil", back_populates="integrantes")
    empresa = relationship(
        "Empresa", back_populates="participaciones", foreign_keys=[empresa_id]
    )


class RequisitoHtmlDescarga(Base):
    """Checklist de requisitos/documentos exigidos en el pliego (uso futuro: formatos)."""

    __tablename__ = "requisitos_html_descarga"

    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos_html_descarga.id"), nullable=False)

    item = Column(String, default="")
    descripcion = Column(String, default="")
    requiere_documento = Column(Boolean, default=False)

    proceso = relationship("ProcesoHtmlDescarga", back_populates="requisitos")
