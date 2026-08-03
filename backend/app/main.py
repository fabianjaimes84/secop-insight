from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api.routes.secop_routes import router as secop_router
from app.api.routes.html_descarga_routes import router as html_descarga_router
from app.core.logger import logger
from app.db.base import engine, Base
from app.db import models as db_models  # noqa: F401 (registra las tablas en Base)

# Cargar variables del archivo .env
load_dotenv()

app = FastAPI(
    title="SECOP II | Insight API",
    description="Sistema para consulta de procesos SECOP II",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("SECOP Insight API iniciada correctamente.")


@app.get("/")
def inicio():
    logger.info("Consulta al endpoint raíz.")

    return {
        "mensaje": "Bienvenido a SECOP II | Insight API 🚀",
        "api_secop": os.getenv("SECOP_API_URL"),
    }


app.include_router(secop_router)
app.include_router(html_descarga_router)
