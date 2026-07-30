from typing import Any, List, Set

# ==========================================================
# Listas Blancas de Campos Permitidos
# ==========================================================

ALLOWED_FIELDS_P6DX = {
    "entidad",
    "nit_entidad",
    "departamento_entidad",
    "ciudad_entidad",
    "ordenentidad",
    "codigo_pci",
    "id_del_proceso",
    "referencia_del_proceso",
    "ppi",
    "id_del_portafolio",
    "nombre_del_procedimiento",
    "descripci_n_del_procedimiento",
    "fase",
    "fecha_de_publicacion_del",
    "fecha_de_ultima_publicaci",
    "fecha_de_publicacion_fase_3",
    "precio_base",
    "modalidad_de_contratacion",
    "justificaci_n_modalidad_de",
    "duracion",
    "unidad_de_duracion",
    "ciudad_de_la_unidad_de",
    "nombre_de_la_unidad_de",
    "proveedores_invitados",
    "proveedores_con_invitacion",
    "visualizaciones_del",
    "proveedores_que_manifestaron",
    "respuestas_al_procedimiento",
    "respuestas_externas",
    "conteo_de_respuestas_a_ofertas",
    "proveedores_unicos_con",
    "numero_de_lotes",
    "estado_del_procedimiento",
    "id_estado_del_procedimiento",
    "adjudicado",
    "id_adjudicacion",
    "codigoproveedor",
    "departamento_proveedor",
    "ciudad_proveedor",
    "valor_total_adjudicacion",
    "nombre_del_adjudicador",
    "nombre_del_proveedor",
    "nit_del_proveedor_adjudicado",
    "codigo_principal_de_categoria",
    "estado_de_apertura_del_proceso",
    "tipo_de_contrato",
    "subtipo_de_contrato",
    "categorias_adicionales",
    "urlproceso",
    "codigo_entidad",
    "estado_resumen",
    "@rendered_url",
    "id",
    ":id",
    ":created_at",
    ":updated_at",
}

ALLOWED_FIELDS_BT96 = {
    "id",
    "codigo_proceso",
    "referencia_proceso",
    "nombre_entidad",
    "nit_entidad",
    "departamento_entidad",
    "ciudad_entidad",
    "codigo_entidad",
    "objeto_contratacion",
    "descripcion",
    "modalidad_seleccion",
    "estado_proceso",
    "fase_actual",
    "fecha_publicacion",
    "fecha_apertura",
    "fecha_cierre",
    "valor_estimado",
    "valor_adjudicado",
    "departamento_ubicacion",
    "ciudad_ubicacion",
    "cpv_principal",
    "nombre_proveedor",
    "nit_proveedor",
    "url_externo",
    ":id",
    ":created_at",
    ":updated_at",
}

MAX_STRING_LENGTH = 256

# ==========================================================
# Funciones de Utilidad
# ==========================================================


def get_allowed_fields(api_url: str) -> Set[str]:
    """
    Retorna la lista de campos permitidos según la URL de la API configurada.
    """
    if "bt96-ncis" in api_url:
        return ALLOWED_FIELDS_BT96
    else:
        # Por defecto usa la lista antigua (p6dx-8zbt)
        return ALLOWED_FIELDS_P6DX


def validate_field(field: str, api_url: str) -> bool:
    """
    Verifica si el campo está en la lista blanca correspondiente a la API.
    """
    allowed = get_allowed_fields(api_url)
    return field in allowed


def sanitize_string(value: Any) -> str:
    """
    Limpia un string para evitar inyección SOQL.
    1. Convierte a string.
    2. Limita la longitud.
    3. Escapa comillas simples (' -> '').
    """
    if value is None:
        return ""

    str_val = str(value).strip()

    # Truncar si es muy largo
    if len(str_val) > MAX_STRING_LENGTH:
        str_val = str_val[:MAX_STRING_LENGTH]

    # Escapar comillas simples (estándar SQL/SOQL)
    return str_val.replace("'", "''")
