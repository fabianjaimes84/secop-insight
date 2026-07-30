import os
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.core.logger import logger
from app.models.busqueda import BusquedaProceso
from app.models.proceso import Proceso
from app.repositories.secop_repository import SecopRepository
from app.core.cache import cache


class SecopServiceError(Exception):
    """Excepción personalizada para errores del servicio SECOP."""

    pass


class SecopService:
    """
    Servicio encargado de la lógica de negocio relacionada con SECOP.
    Implementa carga híbrida: Lectura inmediata de archivo local +
    actualización asíncrona en segundo plano.
    """

    def __init__(self):
        self.repository = SecopRepository()

    def _mapear_proceso(self, item: dict) -> Proceso:
        """Convierte un registro de SECOP al modelo Proceso con validación básica."""
        try:
            return Proceso(
                entidad=item.get("entidad", ""),
                nit_entidad=item.get("nit_entidad", ""),
                departamento_entidad=item.get("departamento_entidad", ""),
                ciudad_entidad=item.get("ciudad_entidad", ""),
                ordenentidad=item.get("ordenentidad", ""),
                codigo_entidad=item.get("codigo_entidad"),
                id_del_proceso=item.get("id_del_proceso", ""),
                referencia_del_proceso=item.get("referencia_del_proceso", ""),
                nombre_del_procedimiento=item.get("nombre_del_procedimiento", ""),
                descripci_n_del_procedimiento=item.get(
                    "descripci_n_del_procedimiento", ""
                ),
                fase=item.get("fase", ""),
                estado_resumen=item.get("estado_resumen", ""),
                estado_del_procedimiento=item.get("estado_del_procedimiento", ""),
                id_estado_del_procedimiento=item.get("id_estado_del_procedimiento"),
                modalidad_de_contratacion=item.get("modalidad_de_contratacion", ""),
                justificaci_n_modalidad_de=item.get("justificaci_n_modalidad_de", ""),
                tipo_de_contrato=item.get("tipo_de_contrato", ""),
                subtipo_de_contrato=item.get("subtipo_de_contrato", ""),
                duracion=item.get("duracion"),
                unidad_de_duracion=item.get("unidad_de_duracion", ""),
                fecha_de_publicacion_del=item.get("fecha_de_publicacion_del", ""),
                fecha_de_ultima_publicaci=item.get("fecha_de_ultima_publicaci", ""),
                fecha_de_recepcion_de=item.get("fecha_de_recepcion_de", ""),
                fecha_de_apertura_de_respuesta=item.get(
                    "fecha_de_apertura_de_respuesta", ""
                ),
                fecha_de_apertura_efectiva=item.get("fecha_de_apertura_efectiva", ""),
                fecha_adjudicacion=item.get("fecha_adjudicacion", ""),
                precio_base=item.get("precio_base"),
                adjudicado=item.get("adjudicado", ""),
                valor_total_adjudicacion=item.get("valor_total_adjudicacion"),
                codigoproveedor=item.get("codigoproveedor", ""),
                nombre_del_proveedor=item.get("nombre_del_proveedor", ""),
                nit_del_proveedor_adjudicado=item.get(
                    "nit_del_proveedor_adjudicado", ""
                ),
                departamento_proveedor=item.get("departamento_proveedor", ""),
                ciudad_proveedor=item.get("ciudad_proveedor", ""),
                proveedores_invitados=item.get("proveedores_invitados"),
                proveedores_con_invitacion=item.get("proveedores_con_invitacion"),
                proveedores_que_manifestaron=item.get("proveedores_que_manifestaron"),
                respuestas_al_procedimiento=item.get("respuestas_al_procedimiento"),
                respuestas_externas=item.get("respuestas_externas"),
                conteo_de_respuestas_a_ofertas=item.get(
                    "conteo_de_respuestas_a_ofertas"
                ),
                proveedores_unicos_con=item.get("proveedores_unicos_con"),
                visualizaciones_del=item.get("visualizaciones_del"),
                numero_de_lotes=item.get("numero_de_lotes"),
                codigo_principal_de_categoria=item.get(
                    "codigo_principal_de_categoria", ""
                ),
                categorias_adicionales=item.get("categorias_adicionales", ""),
                urlproceso=self._extraer_url(item.get("urlproceso")),
            )
        except Exception as e:
            logger.error(
                f"Error mapeando proceso {item.get('id_del_proceso', 'DESCONOCIDO')}: {str(e)}"
            )
            raise SecopServiceError(f"Error procesando dato del proceso: {str(e)}")

    def _extraer_url(self, valor):
        if not valor:
            return ""
        if isinstance(valor, dict):
            return valor.get("url", "")
        return str(valor)

    def _manejar_error_api(self, error: Exception, contexto: str) -> Dict[str, Any]:
        """Estandariza la respuesta de error."""
        logger.exception(f"Error en {contexto}: {str(error)}")

        if isinstance(error, httpx.TimeoutException):
            return {
                "error": "Tiempo de espera agotado",
                "detalle": "La API de SECOP tardó demasiado en responder. Intente nuevamente.",
                "codigo": "TIMEOUT",
            }
        elif isinstance(error, httpx.ConnectError):
            return {
                "error": "Error de conexión",
                "detalle": "No se pudo conectar con la API de SECOP. Verifique su conexión a internet.",
                "codigo": "CONNECTION_ERROR",
            }
        elif isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code
            if status == 404:
                detalle = "Recurso no encontrado en la API de SECOP."
            elif status >= 500:
                detalle = "Error interno en la API de SECOP. Intente más tarde."
            else:
                detalle = f"Error HTTP {status} desde la API de SECOP."

            return {
                "error": "Error en la respuesta de SECOP",
                "detalle": detalle,
                "codigo": f"HTTP_{status}",
            }
        else:
            return {
                "error": "Error inesperado",
                "detalle": "Ocurrió un error interno procesando la solicitud.",
                "codigo": "INTERNAL_ERROR",
            }

    async def obtener_procesos(
        self,
        limit: int = 5,
        buscar: Optional[str] = None,
        estado: Optional[str] = None,
    ):
        logger.info("Iniciando consulta rápida de procesos.")
        try:
            datos = await self.repository.obtener_procesos_async(
                limit=limit,
                buscar=buscar,
                estado=estado,
            )
            logger.info(f"Consulta completada. {len(datos)} procesos encontrados.")
            return [self._mapear_proceso(item) for item in datos]

        except Exception as e:
            return self._manejar_error_api(e, "obtener_procesos")

    async def obtener_catalogo(self, campo: str):
        """Obtiene valores únicos para un campo, usando caché asíncrono global."""
        cache_key = f"catalogo_{campo}"

        try:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Caché hit para catálogo '{campo}'.")
                return cached_data

            logger.info(f"Caché miss para '{campo}'. Consultando API...")
            datos_crudos = await self.repository.obtener_catalogo_async(campo)

            resultados = sorted(
                {item.get(campo) for item in datos_crudos if item.get(campo)}
            )

            await cache.set(cache_key, resultados, ttl_seconds=3600)
            return resultados

        except Exception as e:
            logger.error(f"Error obteniendo catálogo {campo}: {e}")
            return []

    async def obtener_catalogos(self):
        """
        Estrategia Híbrida:
        1. Retorna inmediatamente los datos del archivo JSON local (Velocidad < 10ms).
        2. Dispara una tarea en segundo plano para actualizar el archivo si hay cambios.
        """
        # Ruta del archivo: backend/app/data/catalogos.json
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ruta_archivo = os.path.join(base_dir, "data", "catalogos.json")

        # 1. Cargar datos locales inmediatamente
        datos_locales = {"estados": [], "tipos_proceso": []}
        try:
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos_locales = json.load(f)
                logger.info(f"Catálogos cargados desde archivo local ({ruta_archivo}).")
            else:
                logger.warning(
                    "Archivo de catálogos no encontrado. Se devolverán listas vacías inicialmente."
                )
        except Exception as e:
            logger.error(f"Error leyendo archivo local de catálogos: {e}")

        # 2. Programar actualización en segundo plano (No bloquea la respuesta)
        asyncio.create_task(self._actualizar_catalogos_async(ruta_archivo))

        return datos_locales

    async def _actualizar_catalogos_async(self, ruta_archivo: str):
        """
        Tarea interna: Consulta la API, compara y guarda el archivo si hay cambios.
        Se ejecuta en segundo plano sin bloquear al usuario.
        """
        try:
            logger.info("Iniciando actualización de catálogos en segundo plano...")

            # Consultar API real (usando el método que ya tiene caché interno si se desea)
            estados_nuevos = await self.obtener_catalogo("estado_del_procedimiento")
            tipos_nuevos = await self.obtener_catalogo("modalidad_de_contratacion")

            datos_nuevos = {"estados": estados_nuevos, "tipos_proceso": tipos_nuevos}

            # Comparar con lo que hay en el archivo para evitar escrituras innecesarias
            datos_viejos = {}
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos_viejos = json.load(f)

            if datos_nuevos != datos_viejos:
                # Asegurar que la carpeta existe
                os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    json.dump(datos_nuevos, f, indent=2, ensure_ascii=False)

                logger.info("✅ Catálogos actualizados en disco exitosamente.")
            else:
                logger.info(
                    "ℹ️ Catálogos sin cambios. No se requiere escritura en disco."
                )

        except Exception as e:
            logger.error(f"❌ Error en actualización de segundo plano: {e}")

    async def buscar_procesos(self, filtros: BusquedaProceso):
        logger.info("Iniciando búsqueda avanzada de procesos.")
        try:
            datos = await self.repository.buscar_procesos_async(filtros)
            logger.info(f"Búsqueda finalizada. {len(datos)} procesos encontrados.")
            return [self._mapear_proceso(item) for item in datos]

        except Exception as e:
            return self._manejar_error_api(e, "buscar_procesos")
