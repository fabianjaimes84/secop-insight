import httpx
from datetime import datetime, timedelta

from app.core.logger import logger
from app.models.busqueda import BusquedaProceso
from app.models.proceso import Proceso
from app.repositories.secop_repository import SecopRepository


class SecopService:
    """
    Servicio encargado de la lógica de negocio relacionada con SECOP.
    """

    # ==========================================
    # Configuración de caché
    # ==========================================

    _catalogos_cache = None
    _catalogos_cache_fecha = None

    CATALOGOS_CACHE_HORAS = 24

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
        logger.info("Iniciando consulta rápida de procesos.")

        try:
            datos = self.repository.obtener_procesos(
                limit=limit,
                buscar=buscar,
                estado=estado,
            )

            logger.info(f"Consulta completada. {len(datos)} procesos encontrados.")

            return [self._mapear_proceso(item) for item in datos]

        except httpx.HTTPError:
            logger.exception("Error al consultar la API de SECOP.")
            return {
                "error": "No fue posible consultar la API de SECOP.",
                "detalle": "Error de comunicación con SECOP.",
            }

    # ==========================================================
    # Catálogos
    # ==========================================================

    def obtener_catalogo(self, campo: str):
        logger.info(f"Consultando catálogo: {campo}")

        datos = self.repository.obtener_catalogo(campo)

        logger.info(f"Catálogo '{campo}' obtenido correctamente.")

        return sorted({item[campo] for item in datos if item.get(campo)})

    def obtener_catalogos(self):

        ahora = datetime.now()

        # ======================================================
        # Validar si la caché sigue vigente
        # ======================================================

        if (
            self._catalogos_cache is not None
            and self._catalogos_cache_fecha is not None
        ):
            horas = ahora - self._catalogos_cache_fecha

            if horas < timedelta(hours=self.CATALOGOS_CACHE_HORAS):
                restante = timedelta(hours=self.CATALOGOS_CACHE_HORAS) - horas

                logger.info(
                    f"Catálogos obtenidos desde memoria. "
                    f"Expiran en {restante.seconds // 3600} horas."
                )

                return self._catalogos_cache

            logger.info("La caché de catálogos expiró. Actualizando información...")

        # ======================================================
        # Consultar SECOP
        # ======================================================

        logger.info("Consultando catálogos en SECOP...")

        estados = self.obtener_catalogo("estado_del_procedimiento")
        logger.info(
            f"Catálogo de --> Estado del proceso <-- ha cargado ({len(estados)} registros)."
        )

        tipos = self.obtener_catalogo("modalidad_de_contratacion")
        logger.info(
            f"Catálogo de --> Tipo de proceso <-- ha cargado ({len(tipos)} registros)."
        )

        self._catalogos_cache = {
            "estados": estados,
            "tipos_proceso": tipos,
        }

        self._catalogos_cache_fecha = ahora

        logger.info(
            f"Catálogos almacenados en memoria durante "
            f"{self.CATALOGOS_CACHE_HORAS} horas."
        )

        return self._catalogos_cache

    # ==========================================================
    # Búsqueda principal
    # ==========================================================

    def buscar_procesos(self, filtros: BusquedaProceso):

        logger.info("Iniciando búsqueda de procesos.")

        datos = self.repository.buscar_procesos(filtros)

        logger.info(f"Búsqueda finalizada. {len(datos)} procesos encontrados.")

        return [self._mapear_proceso(item) for item in datos]
