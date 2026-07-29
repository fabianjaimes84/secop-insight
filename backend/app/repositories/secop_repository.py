import json
import httpx

from app.core.config import settings
from app.core.logger import logger
from app.models.busqueda import BusquedaProceso


class SecopRepository:
    """
    Repositorio encargado de consultar la API de SECOP II.

    Centraliza la construcción de los parámetros enviados
    a la API, permitiendo mantener la lógica de búsqueda
    en un único lugar.
    """

    # ==========================================
    # Campos utilizados por la aplicación
    # ==========================================

    CAMPOS_PROCESO = [
        "entidad",
        "nit_entidad",
        "departamento_entidad",
        "ciudad_entidad",
        "ordenentidad",
        "codigo_entidad",
        "id_del_proceso",
        "referencia_del_proceso",
        "nombre_del_procedimiento",
        "descripci_n_del_procedimiento",
        "fase",
        "estado_resumen",
        "estado_del_procedimiento",
        "id_estado_del_procedimiento",
        "modalidad_de_contratacion",
        "justificaci_n_modalidad_de",
        "tipo_de_contrato",
        "subtipo_de_contrato",
        "duracion",
        "unidad_de_duracion",
        "fecha_de_publicacion_del",
        "fecha_de_ultima_publicaci",
        "fecha_de_recepcion_de",
        "fecha_de_apertura_de_respuesta",
        "fecha_de_apertura_efectiva",
        "fecha_adjudicacion",
        "precio_base",
        "adjudicado",
        "valor_total_adjudicacion",
        "codigoproveedor",
        "nombre_del_proveedor",
        "nit_del_proveedor_adjudicado",
        "departamento_proveedor",
        "ciudad_proveedor",
        "proveedores_invitados",
        "proveedores_con_invitacion",
        "proveedores_que_manifestaron",
        "respuestas_al_procedimiento",
        "respuestas_externas",
        "conteo_de_respuestas_a_ofertas",
        "proveedores_unicos_con",
        "visualizaciones_del",
        "numero_de_lotes",
        "codigo_principal_de_categoria",
        "categorias_adicionales",
        "urlproceso",
    ]

    # ==========================================
    # Consulta básica de procesos
    # ==========================================

    def obtener_procesos(
        self,
        limit: int = 5,
        buscar: str | None = None,
        estado: str | None = None,
    ):

        params = {
            "$limit": limit,
            "$select": ",".join(self.CAMPOS_PROCESO),
            "$order": "fecha_de_recepcion_de ASC",
        }

        if buscar:
            params["$q"] = buscar

        if estado:
            params["estado_resumen"] = estado

        logger.info("Consultando procesos en SECOP II.")

        response = httpx.get(
            settings.SECOP_API_URL,
            params=params,
            timeout=settings.TIMEOUT,
        )

        response.raise_for_status()

        datos = response.json()

        logger.info(
            f"Consulta completada correctamente. {len(datos)} procesos obtenidos."
        )

        return datos

    # ==========================================
    # Obtener valores únicos para los filtros
    # ==========================================

    def obtener_catalogo(self, campo: str):

        params = {
            "$select": campo,
            "$group": campo,
            "$order": campo,
        }

        logger.info(f"Consultando catálogo '{campo}'.")

        response = httpx.get(
            settings.SECOP_API_URL,
            params=params,
            timeout=settings.TIMEOUT,
        )

        response.raise_for_status()

        datos = response.json()

        logger.info(
            f"Catálogo '{campo}' obtenido correctamente. {len(datos)} registros."
        )

        return datos

    # ==========================================
    # Construir parámetros de búsqueda
    # ==========================================

    def _construir_parametros(self, filtros: BusquedaProceso):

        params = {
            "$limit": filtros.limit,
            "$select": ",".join(self.CAMPOS_PROCESO),
            "$order": "fecha_de_publicacion_del DESC",
        }

        if filtros.buscar:
            params["$q"] = filtros.buscar

        if filtros.estado:
            params["estado_del_procedimiento"] = filtros.estado

        if filtros.tipo_proceso:
            params["modalidad_de_contratacion"] = filtros.tipo_proceso

        condiciones = []

        # ==========================================
        # Filtro por fecha de publicación (solo fecha)
        # ==========================================

        if filtros.fecha_publicacion_desde:
            condiciones.append(
                f"fecha_de_publicacion_del >= '{filtros.fecha_publicacion_desde}T00:00:00'"
            )

        if filtros.fecha_publicacion_hasta:
            condiciones.append(
                f"fecha_de_publicacion_del <= '{filtros.fecha_publicacion_hasta}T23:59:59'"
            )
        if condiciones:
            params["$where"] = " AND ".join(condiciones)

        return params

    # ==========================================
    # Consulta principal utilizada por la aplicación
    # ==========================================

    def buscar_procesos(self, filtros: BusquedaProceso):

        params = self._construir_parametros(filtros)

        logger.info("Iniciando búsqueda avanzada de procesos.")

        response = httpx.get(
            settings.SECOP_API_URL,
            params=params,
            timeout=settings.TIMEOUT,
        )

        response.raise_for_status()

        datos = response.json()

        logger.info(
            f"Búsqueda finalizada correctamente. {len(datos)} procesos encontrados."
        )

        # ==========================================
        # Eliminar registros 100 % idénticos
        # ==========================================

        datos_unicos = []
        vistos = set()

        for proceso in datos:
            firma = json.dumps(proceso, sort_keys=True, ensure_ascii=False)

            if firma not in vistos:
                vistos.add(firma)
                datos_unicos.append(proceso)

        logger.info(
            f"Se recibieron {len(datos)} registros, "
            f"se eliminaron {len(datos) - len(datos_unicos)} duplicados exactos y "
            f"se devolverán {len(datos_unicos)} registros."
        )

        return datos_unicos
