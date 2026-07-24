import httpx

from app.models.busqueda import BusquedaProceso
from app.models.proceso import Proceso
from app.repositories.secop_repository import SecopRepository


class SecopService:
    """
    Servicio encargado de la lógica de negocio relacionada con SECOP.
    """

    _catalogos_cache = None

    def __init__(self):
        self.repository = SecopRepository()

    # ==========================================================
    # Construcción del modelo Proceso
    # ==========================================================

    def _mapear_proceso(self, item: dict) -> Proceso:
        """Convierte un registro de SECOP al modelo Proceso."""

        return Proceso(
            # ==========================
            # Información de la Entidad
            # ==========================
            entidad=item.get("entidad", ""),
            nit_entidad=item.get("nit_entidad", ""),
            departamento_entidad=item.get("departamento_entidad", ""),
            ciudad_entidad=item.get("ciudad_entidad", ""),
            ordenentidad=item.get("ordenentidad", ""),
            codigo_entidad=item.get("codigo_entidad"),
            # ==========================
            # Información del Proceso
            # ==========================
            id_del_proceso=item.get("id_del_proceso", ""),
            referencia_del_proceso=item.get("referencia_del_proceso", ""),
            nombre_del_procedimiento=item.get("nombre_del_procedimiento", ""),
            descripci_n_del_procedimiento=item.get("descripci_n_del_procedimiento", ""),
            fase=item.get("fase", ""),
            estado_resumen=item.get("estado_resumen", ""),
            estado_del_procedimiento=item.get("estado_del_procedimiento", ""),
            id_estado_del_procedimiento=item.get("id_estado_del_procedimiento"),
            # ==========================
            # Contratación
            # ==========================
            modalidad_de_contratacion=item.get("modalidad_de_contratacion", ""),
            justificaci_n_modalidad_de=item.get("justificaci_n_modalidad_de", ""),
            tipo_de_contrato=item.get("tipo_de_contrato", ""),
            subtipo_de_contrato=item.get("subtipo_de_contrato", ""),
            duracion=item.get("duracion"),
            unidad_de_duracion=item.get("unidad_de_duracion", ""),
            # ==========================
            # Fechas
            # ==========================
            fecha_de_publicacion_del=item.get("fecha_de_publicacion_del", ""),
            fecha_de_ultima_publicaci=item.get("fecha_de_ultima_publicaci", ""),
            fecha_de_recepcion_de=item.get("fecha_de_recepcion_de", ""),
            fecha_de_apertura_de_respuesta=item.get(
                "fecha_de_apertura_de_respuesta", ""
            ),
            fecha_de_apertura_efectiva=item.get("fecha_de_apertura_efectiva", ""),
            fecha_adjudicacion=item.get("fecha_adjudicacion", ""),
            # ==========================
            # Información Económica
            # ==========================
            precio_base=item.get("precio_base"),
            adjudicado=item.get("adjudicado", ""),
            valor_total_adjudicacion=item.get("valor_total_adjudicacion"),
            # ==========================
            # Proveedor Adjudicado
            # ==========================
            codigoproveedor=item.get("codigoproveedor", ""),
            nombre_del_proveedor=item.get("nombre_del_proveedor", ""),
            nit_del_proveedor_adjudicado=item.get("nit_del_proveedor_adjudicado", ""),
            departamento_proveedor=item.get("departamento_proveedor", ""),
            ciudad_proveedor=item.get("ciudad_proveedor", ""),
            # ==========================
            # Estadísticas
            # ==========================
            proveedores_invitados=item.get("proveedores_invitados"),
            proveedores_con_invitacion=item.get("proveedores_con_invitacion"),
            proveedores_que_manifestaron=item.get("proveedores_que_manifestaron"),
            respuestas_al_procedimiento=item.get("respuestas_al_procedimiento"),
            respuestas_externas=item.get("respuestas_externas"),
            conteo_de_respuestas_a_ofertas=item.get("conteo_de_respuestas_a_ofertas"),
            proveedores_unicos_con=item.get("proveedores_unicos_con"),
            visualizaciones_del=item.get("visualizaciones_del"),
            numero_de_lotes=item.get("numero_de_lotes"),
            # ==========================
            # Clasificación
            # ==========================
            codigo_principal_de_categoria=item.get("codigo_principal_de_categoria", ""),
            categorias_adicionales=item.get("categorias_adicionales", ""),
            # ==========================
            # Enlace
            # ==========================
            urlproceso=item.get("urlproceso", {}).get("url", ""),
        )

    # ==========================================================
    # Consulta rápida
    # ==========================================================

    def obtener_procesos(
        self,
        limit: int = 5,
        buscar: str | None = None,
        estado: str | None = None,
    ):

        try:
            datos = self.repository.obtener_procesos(
                limit=limit,
                buscar=buscar,
                estado=estado,
            )

            return [self._mapear_proceso(item) for item in datos]

        except httpx.HTTPError as e:
            return {
                "error": "No fue posible consultar la API de SECOP.",
                "detalle": str(e),
            }

    # ==========================================================
    # Catálogos
    # ==========================================================

    def obtener_catalogo(self, campo: str):

        datos = self.repository.obtener_catalogo(campo)

        return sorted({item[campo] for item in datos if item.get(campo)})

    def obtener_catalogos(self):

        if self._catalogos_cache is not None:
            print("📦 Catálogos obtenidos desde memoria")
            return self._catalogos_cache

        print("🌐 Consultando catálogos en SECOP...")

        self._catalogos_cache = {
            "estados": self.obtener_catalogo("estado_resumen"),
            "tipos_proceso": self.obtener_catalogo("modalidad_de_contratacion"),
        }

        return self._catalogos_cache

    # ==========================================================
    # Búsqueda principal
    # ==========================================================

    def buscar_procesos(self, filtros: BusquedaProceso):

        datos = self.repository.buscar_procesos(filtros)

        return [self._mapear_proceso(item) for item in datos]
