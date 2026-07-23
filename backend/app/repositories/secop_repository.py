import httpx
from app.core.config import settings
from app.models.busqueda import BusquedaProceso


class SecopRepository:
    def obtener_procesos(
        self,
        limit: int = 5,
        buscar: str | None = None,
        estado: str | None = None,
    ):

        url = settings.SECOP_API_URL

        params = {"$limit": limit}

        if buscar:
            params["$q"] = buscar

        if estado:
            params["estado_resumen"] = estado

        respuesta = httpx.get(url, params=params, timeout=settings.TIMEOUT)

        respuesta.raise_for_status()

        return respuesta.json()

    def obtener_catalogo(self, campo: str):
        params = {
            "$select": campo,
            "$group": campo,
            "$order": campo,
        }

        response = httpx.get(
            settings.SECOP_API_URL,
            params=params,
            timeout=settings.TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    def _construir_parametros(self, filtros: BusquedaProceso):
        params = {"$limit": filtros.limit}

        if filtros.buscar:
            params["$q"] = filtros.buscar

        if filtros.estado:
            params["estado_resumen"] = filtros.estado

        if filtros.tipo_proceso:
            params["modalidad_de_contratacion"] = filtros.tipo_proceso

        if filtros.fecha_publicacion_desde:
            params["$where"] = (
                f"fecha_de_ultima_publicaci >= '{filtros.fecha_publicacion_desde}'"
            )

        if filtros.fecha_publicacion_hasta:
            if "$where" in params:
                params["$where"] += (
                    f" AND fecha_de_ultima_publicaci <= '{filtros.fecha_publicacion_hasta}'"
                )
            else:
                params["$where"] = (
                    f"fecha_de_ultima_publicaci <= '{filtros.fecha_publicacion_hasta}'"
                )

        if filtros.fecha_presentacion_desde:
            if "$where" in params:
                params["$where"] += (
                    f" AND fecha_de_recepcion_de >= '{filtros.fecha_presentacion_desde}'"
                )
            else:
                params["$where"] = (
                    f"fecha_de_recepcion_de >= '{filtros.fecha_presentacion_desde}'"
                )

        if filtros.fecha_presentacion_hasta:
            if "$where" in params:
                params["$where"] += (
                    f" AND fecha_de_recepcion_de <= '{filtros.fecha_presentacion_hasta}'"
                )
            else:
                params["$where"] = (
                    f"fecha_de_recepcion_de <= '{filtros.fecha_presentacion_hasta}'"
                )

        return params

    def buscar_procesos(self, filtros: BusquedaProceso):
        params = self._construir_parametros(filtros)

        print(params)

        response = httpx.get(
            settings.SECOP_API_URL,
            params=params,
            timeout=settings.TIMEOUT,
        )

        print(response.status_code)
        print(response.text[:500])

        response.raise_for_status()
        return response.json()
