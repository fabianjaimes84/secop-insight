from pydantic import BaseModel


class Proceso(BaseModel):
    # ==========================
    # Información de la Entidad
    # ==========================

    entidad: str = ""
    nit_entidad: str = ""
    departamento_entidad: str = ""
    ciudad_entidad: str = ""
    ordenentidad: str = ""
    codigo_entidad: int | None = None

    # ==========================
    # Información del Proceso
    # ==========================

    id_del_proceso: str = ""
    referencia_del_proceso: str = ""
    nombre_del_procedimiento: str = ""
    descripci_n_del_procedimiento: str = ""
    fase: str = ""

    estado_resumen: str = ""
    estado_del_procedimiento: str = ""
    id_estado_del_procedimiento: int | None = None

    # ==========================
    # Contratación
    # ==========================

    modalidad_de_contratacion: str = ""
    justificaci_n_modalidad_de: str = ""

    tipo_de_contrato: str = ""
    subtipo_de_contrato: str = ""

    duracion: float | None = None
    unidad_de_duracion: str = ""

    # ==========================
    # Fechas
    # ==========================

    fecha_de_publicacion_del: str = ""
    fecha_de_ultima_publicaci: str = ""

    fecha_de_recepcion_de: str = ""
    fecha_de_apertura_de_respuesta: str = ""
    fecha_de_apertura_efectiva: str = ""

    fecha_adjudicacion: str = ""

    # ==========================
    # Información Económica
    # ==========================

    precio_base: float | None = None

    adjudicado: str = ""
    valor_total_adjudicacion: float | None = None

    # ==========================
    # Proveedor Adjudicado
    # ==========================

    codigoproveedor: str = ""
    nombre_del_proveedor: str = ""
    nit_del_proveedor_adjudicado: str = ""

    departamento_proveedor: str = ""
    ciudad_proveedor: str = ""

    # ==========================
    # Estadísticas
    # ==========================

    proveedores_invitados: int | None = None
    proveedores_con_invitacion: int | None = None
    proveedores_que_manifestaron: int | None = None

    respuestas_al_procedimiento: int | None = None
    respuestas_externas: int | None = None

    conteo_de_respuestas_a_ofertas: int | None = None
    proveedores_unicos_con: int | None = None

    visualizaciones_del: int | None = None
    numero_de_lotes: int | None = None

    # ==========================
    # Clasificación
    # ==========================

    codigo_principal_de_categoria: str = ""
    categorias_adicionales: str = ""

    # ==========================
    # Enlace
    # ==========================

    urlproceso: str = ""
