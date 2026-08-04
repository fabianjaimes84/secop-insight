"""
Catálogo de los formatos que se generan para una oferta.

Cada formato declara:
  - alcance: si se genera uno solo por oferta ('proponente') o uno por
    cada integrante del consorcio/unión temporal ('integrante').
  - criterio: si solo aplica cuando el integrante cumple cierta condición
    (ej. el Formato 13 solo para quien acredita empresa de mujeres).
  - tipos: para qué tipos de proponente aplica.

Los nombres de archivo deben coincidir con las plantillas guardadas en
'backend/plantillas/'.
"""

from dataclasses import dataclass, field


@dataclass
class FormatoOferta:
    codigo: str
    nombre: str
    plantilla: str
    # 'proponente' -> uno por oferta | 'integrante' -> uno por miembro
    alcance: str = "proponente"
    # Campo booleano del integrante que debe ser True para generarlo
    criterio: str | None = None
    # Tipos de proponente a los que aplica
    tipos: list[str] = field(
        default_factory=lambda: ["natural", "consorcio", "union_temporal"]
    )


CATALOGO_FORMATOS: list[FormatoOferta] = [
    FormatoOferta(
        codigo="formato_1",
        nombre="Formato 1 - Carta de presentación de la oferta",
        plantilla="Formato 1 - Carta de presentación de la oferta.docx",
    ),
    FormatoOferta(
        codigo="formato_2",
        nombre="Formato 2 - Conformación de Proponente plural",
        plantilla="Formato 2 - Conformación de Proponente plural.docx",
        # Solo tiene sentido cuando hay varios integrantes
        tipos=["consorcio", "union_temporal"],
    ),
    FormatoOferta(
        codigo="formato_5",
        nombre="Formato 5 - Pagos de seguridad social y aportes legales",
        plantilla="Formato 5 - Pagos de seguridad social y aportes legales.docx",
        alcance="integrante",
    ),
    FormatoOferta(
        codigo="formato_6",
        nombre="Formato 6 - Vinculación de personas con discapacidad",
        plantilla="Formato 6 - Vinculacion de personas con discapacidad.docx",
        alcance="integrante",
        criterio="acredita_discapacidad",
    ),
    FormatoOferta(
        codigo="formato_7",
        nombre="Formato 7 - Puntaje de Industria Nacional",
        plantilla="Formato 7 - Puntaje de Industria Nacional.docx",
    ),
    FormatoOferta(
        codigo="formato_8",
        nombre="Formato 8 - Aceptación y cumplimiento personal clave",
        plantilla="Formato 8 - Aceptacion y cumplimiento personal clave.docx",
    ),
    FormatoOferta(
        codigo="formato_9",
        nombre="Formato 9 - Experiencia y formación académica personal clave",
        plantilla="Formato 9 - Experiencia y formación academica personal clave evaluable.docx",
    ),
    FormatoOferta(
        codigo="formato_10h",
        nombre="Formato 10 H - Factores de desempate",
        plantilla="Formato 10 H - Factores de desempate.docx",
        alcance="integrante",
    ),
    FormatoOferta(
        codigo="formato_10b",
        nombre="Formato 10 B - Factores de desempate",
        plantilla="Formato 10 B - Factores de desempate.docx",
        alcance="integrante",
    ),
    FormatoOferta(
        codigo="formato_11",
        nombre="Formato 11 - Autorización tratamiento de datos personales",
        plantilla="Formato 11 - Auto para el Tratamiento de Datos Personales.docx",
        alcance="integrante",
    ),
    FormatoOferta(
        codigo="formato_12",
        nombre="Formato 12 - Factor de Sostenibilidad",
        plantilla="Formato 12 - Factor de Sostenibilidad.docx",
    ),
    FormatoOferta(
        codigo="formato_13",
        nombre="Formato 13 - Emprendimiento y Empresa de Mujeres",
        plantilla="Formato 13 - Acreditacion Emprendimiento y Empresa de Mujeres.docx",
        alcance="integrante",
        criterio="acredita_mujeres",
    ),
    FormatoOferta(
        codigo="anexo_4",
        nombre="Anexo 4 - Pacto de Transparencia",
        plantilla="Anexo 4 - Pacto de Transparencia.docx",
    ),
    FormatoOferta(
        codigo="cert_anticorrupcion",
        nombre="Certificado Anticorrupción",
        plantilla="Certificado Anticorrupción.docx",
        alcance="integrante",
    ),
    FormatoOferta(
        codigo="cert_inhabilidades",
        nombre="Certificado de inhabilidades o incompatibilidades",
        plantilla="Certificado de inhabilidades o incompatibilidades.docx",
        alcance="integrante",
    ),
    FormatoOferta(
        codigo="cert_sgsst",
        nombre="Certificación del proponente en SG-SST",
        plantilla="Certificacion del proponente en SG-SST.docx",
    ),
    FormatoOferta(
        codigo="cert_laboral",
        nombre="Certificado Laboral - Gerente",
        plantilla="Certificado Laboral - Gerente.docx",
    ),
]


def formatos_aplicables(tipo_proponente: str) -> list[FormatoOferta]:
    """Formatos que aplican a un tipo de proponente."""
    return [f for f in CATALOGO_FORMATOS if tipo_proponente in f.tipos]


def buscar_formato(codigo: str) -> FormatoOferta | None:
    return next((f for f in CATALOGO_FORMATOS if f.codigo == codigo), None)
