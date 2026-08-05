# 🚀 SECOP Insight

SECOP Insight es una plataforma desarrollada para facilitar la consulta, análisis y seguimiento de procesos de contratación pública publicados en **SECOP II**, utilizando la API de Datos Abiertos de Colombia.

El proyecto integra un **backend desarrollado en FastAPI** y un **frontend desarrollado en Angular 20**, proporcionando una interfaz moderna para consultar procesos de contratación, aplicar filtros avanzados y servir como base para futuras funcionalidades como análisis documental mediante Inteligencia Artificial, generación de reportes y seguimiento de oportunidades contractuales.

---

# 📌 Características

## Funcionalidades implementadas

### Backend

- Consulta de procesos de contratación en SECOP II.
- Búsqueda avanzada mediante múltiples filtros.
- Catálogos dinámicos para listas desplegables.
- API REST documentada automáticamente con Swagger.
- Arquitectura por capas.
- Repository Pattern.
- Transformación de datos mediante modelos Pydantic.
- Base de datos SQLite con SQLAlchemy ORM.
- Gestión de empresas y catálogo de contadores.
- Gestión de proponentes (personas naturales, jurídicas, consorcios y uniones temporales).
- Validación de procesos disponibles para presentación de ofertas.
- Cálculo automático de fechas de cierre desde cronograma de procesos.

### Frontend

- Angular 20 con componentes Standalone.
- Arquitectura basada en Features.
- Formulario de búsqueda avanzada.
- Tabla de resultados con filtros.
- Consumo de la API mediante HttpClient.
- Modelos tipados mediante interfaces TypeScript.
- Configuración mediante Environments.
- Endpoints y rutas centralizados.
- Diseño modular y escalable.
- **Módulo de Documentos**:
  - Registro y gestión de empresas (personas naturales y jurídicas).
  - Asignación de accionistas y contadores a empresas.
  - Creación de proponentes con empresas integrantes.
  - **Formulario Uno**: Preguntas progresivas sobre características de empresas:
    - ¿Está en grupo empresarial? (con tipo de relación condicional).
    - ¿Cotiza en bolsa?
    - ¿Es empresa de mujeres?
    - ¿Está constituida por personas con discapacidad?
  - Cálculo automático de porcentajes de participación.
  - Validación de duplicados en nombres de proponentes.
  - Formato de fechas en DD/MM/YYYY.
- **Módulo de Seguimiento**:
  - Listado de procesos con estado.
  - Protección de procesos con ofertas vinculadas.
  - Actualización de estado de procesos.

## Funcionalidades planeadas

- Exportación de formularios a PDF.
- Exportación de resultados a Excel.
- Descarga automática de documentos del proceso.
- Dashboard de indicadores mejorado.
- Análisis documental mediante Inteligencia Artificial.
- Sistema de autenticación y roles.
- Caché de consultas.
- Paginación avanzada.
- Generación de reportes consolidados.
- Notificaciones de cambios en procesos.
- Integración con e-firma.

---

# 🏗️ Arquitectura

El proyecto implementa una arquitectura por capas para garantizar una adecuada separación de responsabilidades y facilitar el mantenimiento del sistema.

```text
                     Usuario
                        │
                        ▼
                 Angular 20
                        │
                 HttpClient
                        │
                        ▼
                FastAPI (API)
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

## Backend

### API (Routes)

Expone los endpoints REST y recibe las solicitudes HTTP.

### Services

Contiene la lógica de negocio y transforma la información obtenida desde el repositorio.

### Repositories

Gestiona la comunicación con la API pública de Datos Abiertos de SECOP II.

### Models

Define los modelos de datos utilizando Pydantic.

### Core

Centraliza la configuración del proyecto y las variables de entorno.

## Frontend

El frontend sigue una arquitectura basada en **Features**, separando responsabilidades y facilitando la escalabilidad.

```text
frontend/
└── src/
    └── app/
        ├── core/
        │   ├── constants/
        │   ├── models/
        │   └── services/
        │
        ├── features/
        │   └── process-search/
        │       ├── components/
        │       ├── pages/
        │       └── services/
        │
        ├── layout/
        └── shared/
```

---

# 🛠️ Tecnologías

## Backend

- Python 3.13
- FastAPI
- HTTPX
- Pydantic
- SQLAlchemy (ORM)
- SQLite (Base de datos)
- Pandas
- OpenPyXL
- Uvicorn

## Frontend

- Angular 20
- TypeScript
- RxJS
- Angular Router
- HttpClient
- Standalone Components

---

# 📁 Estructura del proyecto

```text
secop-insight/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── proceso_routes.py
│   │   │   │   ├── empresa_routes.py
│   │   │   │   ├── proponente_routes.py
│   │   │   │   └── documentos_routes.py
│   │   │   └── main.py
│   │   ├── core/
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── models.py
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── secop.db (SQLite)
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── core/
│   │       ├── features/
│   │       │   ├── dashboard/
│   │       │   ├── documentos/
│   │       │   ├── seguimiento/
│   │       │   └── search/
│   │       ├── layout/
│   │       └── shared/
│   └── package.json
│
├── docs/
│   └── Arquitectura_Funcional_SECOP_Insight.md
│
├── README.md
└── .gitignore
```

---

# ⚙️ Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/secop-insight.git
```

---

## Backend

Ingresar al directorio

```bash
cd backend
```

Crear el entorno virtual

```bash
python -m venv .venv
```

Activar el entorno virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Instalar dependencias

```bash
pip install -r requirements.txt
```

Configurar el archivo `.env`

```env
SECOP_API_URL=https://www.datos.gov.co/resource/p6dx-8zbt.json
TIMEOUT=30
```

Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El backend estará disponible en:

```
http://localhost:8000
```

---

## Frontend

Ingresar al directorio

```bash
cd frontend
```

Instalar dependencias

```bash
npm install
```

Ejecutar la aplicación

```bash
ng serve
```

La aplicación estará disponible en:

```
http://localhost:4200
```

---

# 🌍 Variables de entorno

La configuración del frontend se encuentra en:

```text
src/environments/
├── environment.ts
├── environment.development.ts
└── environment.production.ts
```

La URL del backend se administra mediante estos archivos, evitando direcciones hardcodeadas dentro del código fuente.

---

# 📋 Módulo de Documentos

El módulo de Documentos permite gestionar empresas, contadores y crear proponentes para presentar ofertas en procesos de SECOP II.

## Flujo de creación de un proponente

### Paso 1: Seleccionar proceso
- Elige un proceso de SECOP II disponible en estado "Presentar oferta".
- El sistema valida que hay procesos disponibles; si no, muestra una advertencia.

### Paso 2: Empresas y Formulario Uno
- Agrega las empresas que participarán en la oferta.
- Completa el **Formulario Uno** con preguntas progresivas:
  - **¿Está en grupo empresarial?** → Si selecciona "Sí", aparece "Tipo de relación"
  - **Tipo de relación:** Matriz, Subsidiaria, Filial, Subordinada, Otro (solo si está en grupo)
  - **¿Cotiza en bolsa?**
  - **¿Es empresa de mujeres?**
  - **¿Está constituida por personas con discapacidad?**
- El sistema calcula automáticamente los porcentajes si la suma no es 100%.

### Paso 3: Representantes
- Selecciona el representante principal (quien firma el Pacto de Transparencia).
- Asigna un representante suplente (opcional).

### Paso 4: Información especial
- Ingresa datos adicionales como póliza, experiencia requerida, etc.
- Datos de contacto de la entidad contratante.

### Paso 5: Revisión y guardado
- Verifica todos los datos.
- Guarda el proponente en la base de datos.
- Genera un checklist de documentos por enviar.

## Gestión de empresas

- **Registro único**: Una empresa se registra una sola vez y se reutiliza en múltiples ofertas.
- **Personas naturales y jurídicas**: Soporta ambos tipos.
- **Accionistas**: Asigna múltiples accionistas a una empresa con sus respectivos porcentajes.
- **Contadores**: Vincula un contador/revisor fiscal a cada empresa.

---

# 📡 API

## Obtener procesos

**GET** `/procesos`

Obtiene procesos de contratación utilizando filtros básicos.

### Parámetros

| Parámetro | Tipo |
|-----------|------|
| limit | integer |
| buscar | string |
| estado | string |

---

## Obtener catálogos

**GET** `/catalogos/{campo}`

Permite obtener los valores únicos de un campo para alimentar listas desplegables.

### Ejemplos

```
GET /catalogos/estado_resumen

GET /catalogos/modalidad_de_contratacion

GET /catalogos/departamento_entidad
```

---

## Búsqueda avanzada

**POST** `/busqueda`

Permite realizar búsquedas utilizando múltiples filtros simultáneamente.

### Body

| Campo | Tipo |
|--------|------|
| buscar | string |
| estado | string |
| tipo_proceso | string |
| fecha_publicacion_desde | date |
| fecha_publicacion_hasta | date |
| fecha_presentacion_desde | date |
| fecha_presentacion_hasta | date |
| limit | integer |

### Ejemplo

```json
{
  "buscar": "puente",
  "estado": "Presentación de oferta",
  "tipo_proceso": "Licitación pública",
  "fecha_publicacion_desde": "2026-01-01",
  "fecha_publicacion_hasta": "2026-01-31",
  "fecha_presentacion_desde": null,
  "fecha_presentacion_hasta": null,
  "limit": 20
}
```

---

## Gestión de empresas

**GET** `/empresas`

Obtiene el listado de empresas registradas.

**POST** `/empresas`

Crea una nueva empresa.

### Body

| Campo | Tipo | Requerido |
|--------|------|-----------|
| nom_o_raz_social | string | ✓ |
| nit | string | ✓ |
| es_persona_juridica | boolean | ✓ |
| direccion | string | |
| ciudad | string | |
| correo | string | |
| telefono_fijo | string | |
| telefono_celular | string | |
| contador_id | integer | |
| accionistas | array | |

---

## Gestión de proponentes

**GET** `/proponentes`

Obtiene el listado de proponentes creados.

**POST** `/proponentes`

Crea un nuevo proponente para una oferta.

**GET** `/proponentes/{id}`

Obtiene los detalles de un proponente específico.

**PUT** `/proponentes/{id}`

Actualiza un proponente existente.

---

## Fechas de procesos

**GET** `/documentos/fechas/{codigo_proceso}`

Obtiene las fechas clave del cronograma de un proceso (cierre de oferta, carta de gerencia, etc.).

### Respuesta

| Campo | Tipo | Descripción |
|--------|------|-------------|
| fecha_cierre | string | Fecha de cierre en formato DD/MM/YYYY HH:MM |
| zona_cierre | string | Zona horaria |
| fecha_carta_gerencia | string | Fecha de cierre de carta de gerencia |

---

# 🔄 Flujo de funcionamiento

1. El usuario realiza una búsqueda desde la interfaz web.
2. Angular envía la solicitud al backend mediante HttpClient.
3. FastAPI procesa la petición.
4. El servicio consulta la API de Datos Abiertos de SECOP II.
5. Los datos son transformados al modelo interno del proyecto.
6. El backend retorna la respuesta en formato JSON.
7. Angular muestra los resultados en la tabla de procesos.

---

# 📊 Estado del proyecto

## Backend

- ✅ Arquitectura por capas.
- ✅ Repository Pattern.
- ✅ Integración con SECOP II.
- ✅ Catálogos dinámicos.
- ✅ Consulta de procesos.
- ✅ Búsqueda avanzada.
- ✅ API REST documentada.
- ✅ Base de datos SQLite con SQLAlchemy.
- ✅ Gestión de empresas y proponentes.
- ✅ Validación de procesos.
- ✅ Cálculo automático de fechas.

## Frontend

- ✅ Migración a Angular 20.
- ✅ Arquitectura basada en Features.
- ✅ Componentes Standalone.
- ✅ Integración con FastAPI.
- ✅ Modelos tipados.
- ✅ Configuración mediante Environments.
- ✅ Módulo de Documentos (gestión de empresas y proponentes).
- ✅ Formulario Uno con flujo progresivo.
- ✅ Módulo de Seguimiento.
- 🚧 Exportación a PDF.
- 🚧 Mejoras en dashboard.
- 🚧 Análisis documental.

---

# 🗺️ Roadmap

## Backend

- ✅ Arquitectura base
- ✅ Repository Pattern
- ✅ Integración con SECOP II
- ✅ Consulta de procesos
- ✅ Catálogos dinámicos
- ✅ Búsqueda avanzada
- ✅ Filtros por estado
- ✅ Filtros por modalidad
- ✅ Filtros por fechas
- ✅ Base de datos SQLite
- ✅ Gestión de empresas
- ✅ Gestión de proponentes
- ✅ Validación de procesos
- ⏳ Paginación
- ⏳ Exportación a Excel
- ⏳ Descarga de documentos
- ⏳ Análisis documental mediante IA

## Frontend

- ✅ Angular 20
- ✅ Arquitectura por Features
- ✅ Layout principal
- ✅ Formulario de búsqueda
- ✅ Tabla de resultados
- ✅ Consumo de la API
- ✅ Dashboard básico
- ✅ Módulo de Documentos
- ✅ Gestión de empresas
- ✅ Asistente de proponentes
- ✅ Formulario Uno (preguntas progresivas)
- ✅ Módulo de Seguimiento
- ⏳ Dashboard mejorado
- ⏳ Paginación avanzada
- ⏳ Exportación a PDF
- ⏳ Exportación de resultados a Excel

## Inteligencia Artificial

- ⏳ Resumen automático de procesos.
- ⏳ Clasificación de documentos.
- ⏳ Comparación de pliegos.
- ⏳ Generación de observaciones técnicas.
- ⏳ Asistente para análisis contractual.

---

# 📚 Documentación

## Swagger

```
http://127.0.0.1:8000/docs
```

## ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 📦 Versiones

## Versión actual

**v1.0.1-beta**

## Historial

| Versión | Estado | Cambios principales |
|----------|--------|----------------------|
| v0.1.0 | ✅ Backend MVP | Arquitectura base, integración SECOP II |
| v1.0.0-alpha | ✅ Backend y Frontend integrados | Angular 20, búsqueda avanzada |
| v1.0.1-beta | 🚧 Gestión de proponentes | Módulo de Documentos, Formulario Uno, Seguimiento |

---

# 🤝 Contribuciones

Actualmente el proyecto se encuentra en desarrollo activo.

Las contribuciones serán bienvenidas una vez se publique la primera versión estable.

---

# 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT.

---

# 👨‍💻 Autor

**Fabián Jaimes**

Ingeniero de Sistemas.

Proyecto desarrollado con fines académicos y profesionales para facilitar la consulta, análisis y seguimiento de procesos de contratación pública publicados en SECOP II mediante la integración de Angular, FastAPI y la API de Datos Abiertos de Colombia.