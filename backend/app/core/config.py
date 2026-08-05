import os
from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path

# Obtener la ruta absoluta del archivo .env (está en la carpeta padre de app)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Configuración global de la aplicación.
    """

    # URL de la API de SECOP
    SECOP_API_URL: str = "https://www.datos.gov.co/resource/p6dx-8zbt.json"

    # Token de aplicación Socrata (Opcional)
    SOCRATA_APP_TOKEN: Optional[str] = None

    # Límite por defecto
    SECOP_DEFAULT_LIMIT: int = 5

    # Timeout
    TIMEOUT: int = 30

    # Entorno
    ENVIRONMENT: str = "dev"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

# Debug: Imprimir en consola al iniciar si se cargó el token (Solo para desarrollo)
if settings.SOCRATA_APP_TOKEN:
    print(
        f"[OK] Token Socrata cargado correctamente (longitud: {len(settings.SOCRATA_APP_TOKEN)})"
    )
else:
    print("⚠️ ADVERTENCIA: No se encontró SOCRATA_APP_TOKEN en el .env")
