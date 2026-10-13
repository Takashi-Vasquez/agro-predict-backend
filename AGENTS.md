# AGENTS.md - Agro Predict Backend

## Instrucciones Globales

- **Responder siempre en español** — Todas las respuestas deben ser en español.

## Inicio Rápido

```bash
# Construir y ejecutar (requiere Docker, sin montajes de volumen — reconstruir en cada cambio)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build api

# API disponible en http://localhost:8150/docs
# Python no está en el host — ejecutar todos los comandos Python dentro del contenedor:
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api <comando>
```

## Comandos Esenciales

```bash
# Ejecutar seed (crea usuario admin + cultivos + training_fields + permisos)
docker exec agro-predict-api-dev python -m app.scripts.seed_data

# Generar y aplicar migración Alembic
docker exec agro-predict-api-dev alembic revision --autogenerate -m "descripcion"
docker exec agro-predict-api-dev alembic upgrade head

# Entrenar clasificador legacy (predicción de tipo de cultivo)
docker exec agro-predict-api-dev python -m app.infrastructure.ml.train

# Entrenar modelos de regresión (predicción de rendimiento) vía API
curl -X POST http://localhost:8150/api/v1/general/trained-models/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"algorithms":null}'   # null = todos (random_forest, linear_regression, xgboost)
```

## Arquitectura

**Clean Architecture** con tres capas:
- `app/domain/` — Entidades (dataclasses), ABCs de Repository, Use cases, Excepciones
- `app/infrastructure/` — Modelos ORM, Implementaciones de Repository, Config, Sesión DB, ML, Scheduler
- `app/presentation/` — Endpoints FastAPI, Schemas Pydantic (DTOs), DI, Middleware

**Flujo de solicitud:** Endpoint → Use Case → Repository → ORM → PostgreSQL

## Base de Datos

- **Supabase PostgreSQL** (remoto), 4 schemas: `security`, `core`, `operations`, `monitoring`
- Schema `auth` es gestionado por Supabase — nunca crear ni modificar
- Todas las tablas usan `BitacoraMixin`: `status` (ACTIVE/INACTIVE/DELETED), `created_at`, `updated_at`, `deleted_at`
- Soft delete en todas partes: las consultas deben filtrar `status != 'DELETED'`
- `search_path` establecido en cada conexión: `security, core, operations, monitoring, public`

## Registro de Modelos ORM

Para agregar un nuevo modelo ORM:
1. Crearlo en `app/infrastructure/orm/<schema>/`
2. Importarlo en `app/infrastructure/orm/base.py` y agregarlo a `__all__`
3. Importarlo en `alembic/env.py` para autogenerate
4. Crear migración Alembic: `alembic revision --autogenerate -m "descripcion"`

## Auth y Convenciones API

- Auth: `HTTPBearer` + JWT vía `python-jose` + `passlib[bcrypt]`
- Dependencias: `CurrentUser = Annotated[User, Depends(get_current_user)]`, `DbDep = Annotated[Session, Depends(get_db)]`
- **Todos los endpoints** retornan wrapper `ApiResponse`: `{"statusCode": int, "message": str, "data": T}`
- Usar `ApiResponseFactory.ok()`, `.created()`, `.bad_request()`, `.not_found()`, etc.
- Errores personalizados: `AppException.bad_request("msg")`, `.not_found()`, `.forbidden()`, etc.
- Schemas de cuerpo de solicitud usan `BaseModel`, schemas de respuesta extienden `BaseReadSchema` (alias camelCase)
- Tags definidos en `app/presentation/api/tags.py` — agregar nuevos tags ahí

## Problemas de Docker

- **Sin montajes de volumen** — los cambios de código requieren reconstrucción completa: `docker compose ... up -d --build api`
- La construcción ejecuta `python -m data.generate_dataset` y `python -m app.infrastructure.ml.train` — asegurarse de que pasen
- Los artefactos del modelo ML viven en `app/infrastructure/ml/artifacts/` — se pierden en la reconstrucción a menos que se reentrene
- Puerto dev: `8150` (externo) → `8000` (interno)

## Módulo ML

- **Clasificador legacy** (tipo de cultivo): `app/infrastructure/ml/train.py` + `model.py` — RandomForest, 7 features
- **Entrenador de regresión** (rendimiento): `app/infrastructure/ml/regression_trainer.py` — RF + LinearRegression + XGBoost
- **Predictor de rendimiento**: `app/infrastructure/ml/yield_predictor.py` — carga modelo entrenado + scaler + imputer
- **Entrenamiento asíncrono**: `app/infrastructure/ml/training_jobs.py` — ThreadPoolExecutor, polling de jobs
- Campos de entrenamiento definidos en seed (`TRAINING_FIELDS_DATA`), no vía API CRUD
- 10 columnas fijas: nitrogen, phosphorus, potassium, temperature, humidity, ph_soil, rainfall, irrigation_type, variety, soil_type
- Imputación: mediana para numéricos, hash a float para strings (irrigation_type, variety, soil_type)
- Mínimo 50 registros para entrenar

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `app/main.py` | Fábrica de app, lifespan (scheduler, creación de schemas) |
| `app/infrastructure/config/settings.py` | Todas las configuraciones vía variables de entorno |
| `app/infrastructure/database/session.py` | Singleton de engine, factory de sesiones, search_path |
| `app/infrastructure/database/base.py` | `Base`, `Schemas`, `BitacoraMixin` |
| `app/presentation/api/deps.py` | Dependencias `CurrentUser`, `DbDep` |
| `app/presentation/utils/api_response_factory.py` | Respuestas API estandarizadas |
| `app/presentation/utils/exception_middleware.py` | Manejo global de errores |
| `app/scripts/seed_data.py` | Seed: usuario admin, cultivos, training_fields, permisos, menús |
| `alembic/env.py` | Config de Alembic, imports de schemas, search_path |

## Usuario Admin

- Email: `admin@tesis.com`
- Contraseña: `admin@agro6020.`
- `is_admin=True` (evita RBAC)
