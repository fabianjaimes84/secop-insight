import httpx
import json
import unicodedata
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.logger import logger
from app.models.busqueda import BusquedaProceso
from app.core.security import sanitize_string, validate_field, get_allowed_fields


class SecopRepository:
    """
    Repositorio encargado de consultar la API de SECOP II de forma asíncrona.
    Incluye autenticación con Token Socrata si está configurado.
    """

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

    def _get_headers(self) -> Dict[str, str]:
        """
        Genera los headers necesarios, incluyendo el Token de Socrata si existe.
        Manejo seguro por si la configuración falla.
        """
        headers = {}
        try:
            token = getattr(settings, "SOCRATA_APP_TOKEN", None)
            if token:
                headers["X-App-Token"] = token
        except Exception as e:
            logger.warning(f"No se pudo leer el token de configuración: {e}")

        if not headers:
            logger.debug("Usando petición sin token (límite anónimo).")

        return headers

    async def obtener_procesos_async(
        self,
        limit: int = 5,
        buscar: Optional[str] = None,
        estado: Optional[str] = None,
    ):
        params = {
            "$limit": limit,
            "$select": ",".join(self.CAMPOS_PROCESO),
            "$order": "fecha_de_recepcion_de ASC",
        }

        if buscar:
            params["$q"] = sanitize_string(buscar)

        if estado:
            params["estado_resumen"] = sanitize_string(estado)

        logger.info("Consultando procesos en SECOP II (Async).")
        headers = self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.SECOP_API_URL,
                params=params,
                timeout=settings.TIMEOUT,
                headers=headers,
            )
            response.raise_for_status()
            datos = response.json()

        logger.info(f"Consulta completada. {len(datos)} procesos obtenidos.")
        return datos

    async def obtener_catalogo_async(self, campo: str):
        # Validar campo contra lista blanca
        allowed_fields = get_allowed_fields(settings.SECOP_API_URL)
        if not validate_field(campo, settings.SECOP_API_URL):
            logger.warning(f"Intento de acceso a campo no permitido: {campo}")
            return []

        params = {
            "$select": campo,
            "$group": campo,
            "$order": campo,
        }

        logger.info(f"Consultando catálogo '{campo}'.")
        headers = self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.SECOP_API_URL,
                params=params,
                timeout=settings.TIMEOUT,
                headers=headers,
            )
            response.raise_for_status()
            datos = response.json()

        logger.info(f"Catálogo '{campo}' obtenido. {len(datos)} registros.")
        return datos

    # Campos sobre los que se hace la búsqueda por texto libre.
    # Se usa una condición explícita en lugar de '$q' porque este último
    # solo consulta los campos que Socrata tiene indexados, y dejaba fuera
    # coincidencias en descripción, proveedor, categoría, etc.
    CAMPOS_BUSQUEDA_TEXTO = [
        "entidad",
        "referencia_del_proceso",
        "nombre_del_procedimiento",
        "descripci_n_del_procedimiento",
        "id_del_proceso",
        "nit_entidad",
        "departamento_entidad",
        "ciudad_entidad",
        "modalidad_de_contratacion",
        "tipo_de_contrato",
        "estado_resumen",
        "nombre_del_proveedor",
        "codigo_principal_de_categoria",
    ]

    # Caracteres que pueden aparecer acentuados en los datos de SECOP II y
    # que, por tanto, no son fiables para comparar directamente.
    VOCALES_VARIABLES = "aeiouáéíóúüuñn"

    def _condicion_busqueda_texto(self, texto: str) -> str:
        """
        Construye la condición de búsqueda insensible a tildes.

        Estrategia: se compara el término carácter por carácter usando
        LIKE con comodín '_' en el lugar de cada vocal acentuable. El
        comodín '_' coincide con cualquier carácter individual, así que
        'interventor_a' encuentra tanto 'interventoria' como
        'interventoría', sin importar la tilde.
        """
        patron = "".join(
            "_" if caracter in self.VOCALES_VARIABLES else caracter
            for caracter in texto.lower()
        )

        return "(" + " OR ".join(
            f"lower({campo}) like '%{patron}%'"
            for campo in self.CAMPOS_BUSQUEDA_TEXTO
        ) + ")"

    async def _construir_parametros_async(self, filtros: BusquedaProceso):
        params = {
            "$limit": filtros.limit,
            "$select": ",".join(self.CAMPOS_PROCESO),
            "$order": "fecha_de_publicacion_del DESC",
        }

        condiciones = []

        if filtros.buscar:
            texto = sanitize_string(filtros.buscar).lower()
            condiciones.append(self._condicion_busqueda_texto(texto))

        if filtros.estado:
            # Las opciones del select vienen del catálogo de
            # 'estado_del_procedimiento' (abierto, aprobado, borrado,
            # cancelado, en aprobación), así que el filtro debe aplicarse
            # sobre ese mismo campo para que los valores coincidan.
            params["estado_del_procedimiento"] = sanitize_string(filtros.estado)

        if filtros.tipo_proceso:
            params["modalidad_de_contratacion"] = sanitize_string(filtros.tipo_proceso)

        if filtros.tipo_contrato:
            params["tipo_de_contrato"] = sanitize_string(filtros.tipo_contrato)

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

    async def buscar_procesos_async(self, filtros: BusquedaProceso):
        params = await self._construir_parametros_async(filtros)
        logger.info("Iniciando búsqueda avanzada (Async).")
        headers = self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.SECOP_API_URL,
                params=params,
                timeout=settings.TIMEOUT,
                headers=headers,
            )
            response.raise_for_status()
            datos = response.json()

        # La consulta usa comodines en las vocales para ignorar tildes, lo
        # que puede traer coincidencias de más (ej. 'vias' -> 'v__s' también
        # casaría con 'veas'). Aquí se descartan esos falsos positivos
        # comparando el texto ya normalizado, sin tildes.
        if filtros.buscar:
            datos = self._filtrar_coincidencias_reales(datos, filtros.buscar)

        # Eliminar duplicados exactos
        datos_unicos = []
        vistos = set()
        for proceso in datos:
            firma = json.dumps(proceso, sort_keys=True, ensure_ascii=False)
            if firma not in vistos:
                vistos.add(firma)
                datos_unicos.append(proceso)

        logger.info(f"Búsqueda finalizada. {len(datos_unicos)} procesos únicos.")
        return datos_unicos

    @staticmethod
    def _sin_tildes(texto: str) -> str:
        """Pasa a minúsculas y quita tildes, para comparar de forma justa."""
        normalizado = unicodedata.normalize("NFD", str(texto or ""))
        return "".join(
            c for c in normalizado if unicodedata.category(c) != "Mn"
        ).lower()

    def _filtrar_coincidencias_reales(
        self, datos: List[Dict[str, Any]], termino: str
    ) -> List[Dict[str, Any]]:
        """Deja solo los procesos donde el término aparece de verdad."""
        buscado = self._sin_tildes(termino)

        resultado = []
        for proceso in datos:
            texto_proceso = " ".join(
                self._sin_tildes(proceso.get(campo, ""))
                for campo in self.CAMPOS_BUSQUEDA_TEXTO
            )
            if buscado in texto_proceso:
                resultado.append(proceso)

        return resultado
