"""
Configuración de la base de datos.

Usamos SQLite: es un solo archivo (secop.db) que vive dentro de la carpeta
backend/, no requiere instalar ni levantar un servidor de base de datos
aparte. Si más adelante el proyecto crece, cambiar a PostgreSQL solo
requiere modificar SQLALCHEMY_DATABASE_URL, sin tocar el resto del código.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # carpeta backend/
RUTA_DB = BASE_DIR / "secop.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{RUTA_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # necesario para SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def obtener_db():
    """
    Dependencia de FastAPI: entrega una sesión de base de datos por request
    y la cierra automáticamente al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
