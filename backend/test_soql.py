import httpx
from pprint import pprint

BASE_URL = "https://www.datos.gov.co/resource/p6dx-8zbt.json"


def ejecutar(nombre: str, params: dict):
    print("\n" + "=" * 80)
    print(nombre)
    print("=" * 80)

    response = httpx.get(BASE_URL, params=params, timeout=60)

    print("\nURL:")
    print(response.url)

    print("\nStatus:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    datos = response.json()

    print(f"\nRegistros: {len(datos)}")

    if datos:
        print("\nPrimer registro:")
        pprint(datos[0])


# ← AQUÍ VA LA PRIMERA PRUEBA
def prueba_formato_fecha():

    ejecutar(
        "MISMA CONSULTA DEL BACKEND",
        {
            "$limit": 50,
            "$select": "referencia_del_proceso,fecha_de_publicacion_del,estado_del_procedimiento,modalidad_de_contratacion",
            "$order": "fecha_de_publicacion_del DESC",
            "estado_del_procedimiento": "Publicado",
            "modalidad_de_contratacion": "Concurso de méritos abierto",
            "$where": (
                "fecha_de_publicacion_del >= '2026-07-01T00:00:00' "
                "AND fecha_de_publicacion_del <= '2026-07-29T23:59:59'"
            ),
        },
    )


# ← Y AL FINAL DEL ARCHIVO
if __name__ == "__main__":
    prueba_formato_fecha()
