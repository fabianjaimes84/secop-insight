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

    # Datos corporativos (de la empresa, no personales)
    direccion = Column(String, default="")
    ciudad = Column(String, default="")
    correo = Column(String, default="")
    telefono_fijo = Column(String, default="")
    telefono_celular = Column(String, default="")

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
    Socio o accionista de una empresa.
    Incluye su participación y rol en la empresa.
    """

    __tablename__ = "accionistas_empresa"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    # Datos básicos del accionista
    nombre = Column(String, default="")
    cedula = Column(String, default="")

    # Participación en la empresa
    orden = Column(Integer, default=1)
    porcentaje = Column(String, default="")
    es_representante_legal = Column(Boolean, default=False)

    empresa = relationship("Empresa", back_populates="accionistas")
    participaciones_como_representante_principal = relationship(
        "ProponentePerfil",
        foreign_keys="ProponentePerfil.repre_principal_accionista_id",
        back_populates="repre_principal",
    )
    participaciones_como_representante_suplente = relationship(
        "ProponentePerfil",
        foreign_keys="ProponentePerfil.repre_suplente_accionista_id",
        back_populates="repre_suplente",
    )


class ProponentePerfil(Base):
    """
    Un proponente para una oferta: puede ser una sola empresa (persona
    natural o jurídica) o la unión de varias en consorcio o unión temporal.
    """

    __tablename__ = "proponentes_perfil"

    id = Column(Integer, primary_key=True, index=True)

    # 'natural', 'juridica', 'consorcio' o 'union_temporal'
    tipo = Column(String, default="natural")
    # Nombre único de la oferta: "UNION TEMPORAL VIALTEK 16"
    nombre = Column(String, unique=True, index=True)

    # Proceso al que se presenta. Un proceso tiene un solo proponente.
    codigo_proceso = Column(String, default="", index=True)

    # Información de lotes
    presenta_por_lotes = Column(Boolean, default=False)
    lotes_seleccionados = Column(String, default="")  # Ej: "Lote 1 y 2" o "Lote 1, 2 y 3"

    # Empresa que firma los formatos (representante_empresa_id)
    representante_empresa_id = Column(
        Integer, ForeignKey("empresas.id"), nullable=True
    )

    # Accionistas que firman el Pacto de Transparencia y formatos
    # Son socios de una de las empresas integrantes
    repre_principal_accionista_id = Column(
        Integer, ForeignKey("accionistas_empresa.id"), nullable=True
    )
    repre_suplente_accionista_id = Column(
        Integer, ForeignKey("accionistas_empresa.id"), nullable=True
    )

    # INFORMACIÓN ESPECIAL DE LA OFERTA

    # Personal clave evaluable
    pers_clave_eval = Column(String, default="")

    # Experiencia que debe demostrar
    experiencia_requerida = Column(String, default="")

    # Póliza (del proponente para esta oferta)
    poliza_numero = Column(String, default="")
    poliza_vigencia = Column(String, default="")
    poliza_valor = Column(Float, nullable=True)

    # Datos de la entidad contratante para esta oferta
    entidad_telefono = Column(String, default="")
    entidad_correo = Column(String, default="")
    entidad_horario = Column(String, default="")
    entidad_url_web = Column(String, default="")
    entidad_url_politica_datos = Column(String, default="")

    # Fechas clave de esta oferta
    fecha_cierre = Column(String, default="")
    fecha_carta_gerencia = Column(String, default="")

    representante_empresa = relationship("Empresa", foreign_keys=[representante_empresa_id])
    repre_principal = relationship(
        "AccionistaEmpresa",
        foreign_keys=[repre_principal_accionista_id],
        back_populates="participaciones_como_representante_principal",
    )
    repre_suplente = relationship(
        "AccionistaEmpresa",
        foreign_keys=[repre_suplente_accionista_id],
        back_populates="participaciones_como_representante_suplente",
    )

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
    tipo_grupo_empresarial = Column(String, default="")  # matriz, subsidiaria, filial, subordinada, otro
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
