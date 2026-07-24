import httpx

from app.repositories.secop_repository import SecopRepository
from app.models.proceso import Proceso
from app.models.busqueda import BusquedaProceso


class SecopService:
    _catalogos_cache = None

    def __init__(self):
        self.repository = SecopRepository()

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

            procesos = []

            for item in datos:
                proceso = Proceso(
                    entidad=item.get("entidad", ""),
                    nit_entidad=item.get("nit_entidad", ""),
                    departamento=item.get("departamento_entidad", ""),
                    ciudad=item.get("ciudad_entidad", ""),
                    numero_proceso=item.get("referencia_del_proceso", ""),
                    objeto=item.get("nombre_del_procedimiento", ""),
                    modalidad=item.get("modalidad_de_contratacion", ""),
                    estado=item.get("estado_resumen", ""),
                    fecha_publicacion=item.get("fecha_de_publicacion", ""),
                )

                procesos.append(proceso)

            return procesos

        except httpx.HTTPError as e:
            return {
                "error": "No fue posible consultar la API de SECOP.",
                "detalle": str(e),
            }

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

    def buscar_procesos(self, filtros: BusquedaProceso):
        datos = self.repository.buscar_procesos(filtros)

        procesos = []

        for item in datos:
            proceso = Proceso(
                entidad=item.get("entidad", ""),
                nit_entidad=item.get("nit_entidad", ""),
                departamento=item.get("departamento_entidad", ""),
                ciudad=item.get("ciudad_entidad", ""),
                numero_proceso=item.get("referencia_del_proceso", ""),
                objeto=item.get("nombre_del_procedimiento", ""),
                modalidad=item.get("modalidad_de_contratacion", ""),
                estado=item.get("estado_resumen", ""),
                fecha_publicacion=item.get("fecha_de_publicacion_del", ""),
            )

            procesos.append(proceso)

        return procesos
