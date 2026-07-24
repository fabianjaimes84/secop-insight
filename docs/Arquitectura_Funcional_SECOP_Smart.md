# SECOP Insight

> Plataforma para consultar, analizar y realizar seguimiento a los procesos de contratación pública publicados en SECOP II.

---

## Descripción

SECOP Insight es una plataforma web desarrollada para facilitar la consulta y análisis de los procesos de contratación pública publicados en SECOP II.

El proyecto implementa una arquitectura desacoplada basada en Angular 20 y FastAPI, permitiendo realizar búsquedas avanzadas, consumir la API pública de Datos Abiertos de SECOP II y presentar la información de manera clara, escalable y mantenible.

Actualmente el proyecto se encuentra en desarrollo y está diseñado para crecer con nuevas funcionalidades como reportes, dashboards, gestión documental e Inteligencia Artificial.

---

# Características

- Consulta de procesos de contratación.
- Búsqueda por palabra clave.
- Filtros por estado.
- Filtros por modalidad de contratación.
- Filtros por fechas.
- Arquitectura multicapa.
- Backend desarrollado con FastAPI.
- Frontend desarrollado con Angular 20.
- Integración con la API pública de SECOP II.

---

# Tecnologías

## Frontend

- Angular 20
- TypeScript
- Tailwind CSS
- FlyonUI
- RxJS

## Backend

- Python
- FastAPI
- Pydantic
- HTTPX

---

# Arquitectura

```text
                   Usuario
                      │
                      ▼
              Search Filters
                      │
                      ▼
                Search Page
                      │
                      ▼
              Process Search
                      │
                POST /busqueda
                      │
                      ▼
                FastAPI API
                      │
                      ▼
                  Services
                      │
                      ▼
               Repositories
                      │
                      ▼
        API Datos Abiertos SECOP II
```

---

# Arquitectura del Proyecto

```text
secop-insight/

├── backend/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   └── core/
│
├── frontend/
│   ├── core/
│   ├── features/
│   ├── shared/
│   └── layout/
│
└── docs/
```

---

# Funcionalidades Implementadas

| Funcionalidad | Estado |
|---------------|--------|
| Consulta de procesos | ✅ |
| Búsqueda avanzada | ✅ |
| Filtro por estado | ✅ |
| Filtro por modalidad | ✅ |
| Filtro por fechas | ✅ |
| Catálogos dinámicos | ✅ |
| Integración Angular - FastAPI | ✅ |
| Visualización de resultados | ✅ |

---

# Roadmap

## Versión 1.0

- Backend FastAPI
- Integración con SECOP II
- API REST
- Angular 20
- Consulta de procesos
- Filtros avanzados

## Próximas versiones

- Paginación
- Ordenamiento
- Exportación a Excel
- Exportación a Word
- Exportación a PDF
- Dashboard de indicadores
- Gestión documental
- Inteligencia Artificial
- Alertas automáticas
- Seguimiento de procesos

---

# Instalación

## Backend

```bash
cd backend

python -m venv venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend

npm install

ng serve
```

---

# Documentación

La documentación técnica del proyecto se encuentra en la carpeta **docs/**.

Incluye:

- Arquitectura del sistema
- Arquitectura del Frontend
- Arquitectura del Backend
- Diagramas Mermaid
- Flujo de consulta
- Roadmap
- Principios de diseño

---

# Estado del Proyecto

🚧 En desarrollo.

Actualmente el proyecto continúa evolucionando con nuevas funcionalidades enfocadas en el análisis de contratación pública y automatización de procesos.

---

# Autor

**Fabián Jaimes**

Ingeniero de Sistemas

Proyecto desarrollado con fines académicos y de fortalecimiento profesional.