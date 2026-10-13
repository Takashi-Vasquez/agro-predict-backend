# Agro Predict API

Backend de tesis: **modelo predictivo de cultivos** (tipo de cultivo y rendimiento) con Clean Architecture, FastAPI, PostgreSQL, autenticación JWT y RBAC.

## Stack

- **Python 3.13**, **FastAPI** + Uvicorn, **Pydantic 2**
- **SQLAlchemy 2.0** + **Supabase PostgreSQL** (psycopg2), **Alembic**
- **JWT**: `python-jose` + `passlib[bcrypt]`
- **ML**: `scikit-learn`, `xgboost`, `pandas`, `joblib`
- **Docker** / Docker Compose

## Levantar el proyecto

### Make (Windows, solo una vez)

```powershell
winget install GnuWin32.Make
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\Program Files (x86)\GnuWin32\bin", "User")
```

Cerrar y reabrir la terminal. Verificar con `make --version`.

### Comandos

```bash
make dev-build     # Construir y levantar (primera vez o tras cambios de código)
make dev           # Levantar SIN rebuild — solo sirve si no cambió código
make down          # Detener
make logs          # Ver logs

make seed          # Menús + permisos (idempotente)
make admin         # Crear usuario administrador
make train         # Entrenar clasificador legacy (tipo de cultivo)
make generate-data # Generar dataset

make migrate-new msg="descripcion"  # Generar migración
make migrate                        # Aplicar pendientes
make migrate-down                   # Revertir última
make migrate-history / migrate-current

make shell         # Terminal dentro del contenedor
```

> **Importante:** el compose **no tiene volume mounts**. Cualquier cambio de código
> requiere `make dev-build`. `make dev` solo reutiliza la imagen existente.

### URLs

- API: `http://localhost:8150` (interno `8000`)
- Swagger: `http://localhost:8150/docs`

### Sin Make

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Estructura

```
agro-predict-backend/
├── app/
│   ├── domain/           # Entidades, repositorios ABC, use cases
│   ├── infrastructure/   # ORM, repositorios concretos, config, ML
│   ├── presentation/     # Endpoints + schemas Pydantic
│   ├── scripts/          # seed_data, create_admin, seed_catalogs
│   └── main.py
├── alembic/              # Migraciones
├── data/                 # Generador de dataset
├── docker-compose.yml    # Base (+ .dev.yml / .prod.yml)
└── requirements.txt
```

**Flujo:** `Endpoint → Use Case → Repository (ABC) → Repository Impl → ORM → PostgreSQL`

## Autenticación y RBAC

- `POST /api/v1/auth/login` → JWT (Bearer). **No hay endpoint de registro**: los usuarios los crea un admin con `POST /api/v1/security/users`.
- Admin (`is_admin=True`): acceso total.
- Otros usuarios: permisos vía roles → `role_permissions` + `role_permission_details`.
- Multi-empresa: header opcional `X-Company-Id`.

## Rutas

Prefijos globales por módulo (documentación completa en `/docs`):

| Módulo | Prefijo |
|--------|---------|
| Auth | `/api/v1/auth` |
| Usuarios | `/api/v1/security/users` |
| Menús y permisos | `/api/v1/security/access-profile` |
| Cultivos / variedades / predicciones | `/api/v1/operations/crops` · `/varieties` · `/predictions` |
| Campañas / modelos / registros | `/api/v1/general/campaigns` · `/trained-models` · `/training-records` |
| Catálogos / empresas / opciones | `/api/v1/core/catalogs` · `/companies` · `/select-options` |
| Clima | `/api/v1/weather` |

Todos los endpoints responden el wrapper `{"statusCode", "message", "data"}`.

## Base de datos

**Supabase PostgreSQL** (remoto), 4 esquemas:

| Esquema | Tablas |
|---------|--------|
| `security` | users, profiles, roles, user_roles, user_company, menus, permissions, menu_permissions, role_permissions, role_permission_details |
| `core` | company, catalogs, catalog_details, predictions, trained_models, training_fields, training_records, model_version, model_run, campaigns |
| `operations` | crops, varieties |
| `monitoring` | weather_readings |

- Schema `auth` lo gestiona Supabase: **no crear ni modificar**.
- Todas las tablas usan `BitacoraMixin`: `status` (ACTIVE/INACTIVE/DELETED), `created_at`, `updated_at`, `deleted_at` — **soft delete**, filtrar siempre `status != 'DELETED'`.
- Las columnas de fecha son `DateTime(timezone=True)` → usar `datetime.now(timezone.utc)`.

### Credenciales

Las credenciales viven en `.env.dev` / `.env.prod` (**no commiteados**). Obtenerlas con:

```bash
grep DATABASE_URL .env.dev
```

## Migraciones

```bash
make migrate-new msg="add phone to users"   # detecta cambios en modelos ORM
make migrate                                  # aplica
make migrate-down                             # revierte
```

Para registrar un modelo ORM: crearlo en `app/infrastructure/orm/<schema>/`, importarlo en `orm/base.py` (`__all__`) y en `alembic/env.py`, luego `migrate-new`.

## Modelo ML

Dos familias de modelo:

| Modelo | Qué predice | Algoritmo(s) |
|--------|-------------|--------------|
| **Clasificador** (`train.py`) | tipo de cultivo | RandomForest |
| **Regresor** (`regression_trainer.py`) | rendimiento (t/ha) | `random_forest`, `linear_regression`, `xgboost` |

### Entrenar el regresor

```bash
curl -X POST http://localhost:8150/api/v1/general/trained-models/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"algorithms": null, "bump_level": "patch"}'
```

- `algorithms: null` entrena los 3; o lista explícita `["xgboost"]`.
- Los 3 compiten por **menor RMSE**; el ganador se evalúa contra el baseline de producción.
- **Mínimo 50 registros** en `core.training_records` (hoy hay 4 → aún no se puede entrenar).
- Asíncrono: `POST .../train-async` → `GET .../jobs/{job_id}`.

### Predicción

`POST /api/v1/operations/predictions/yield` acepta `modelId` opcional para elegir con qué modelo predecir; si se omite usa el modelo seleccionado con `PATCH .../trained-models/{id}/select`. La respuesta incluye `modelRmse`.

### Artefactos

Se guardan en `app/infrastructure/ml/artifacts/modelos/{version}/`. **Se pierden en cada rebuild** (no hay volume mounts): si faltan, `/predictions/yield` devuelve `400`.

## Versionado SemVer

| Nivel | Cuándo | Ejemplo |
|-------|--------|---------|
| **PATCH** | Reentrenamiento, misma arquitectura y features. Por defecto. | Registros nuevos |
| **MINOR** | Cambian features o hiperparámetros; esquema de entrada compatible | Nueva feature `ndvi` |
| **MAJOR** | Cambia algoritmo, target o esquema de entrada | Cambiar de RF a XGBoost |

Endpoints bajo `/api/v1/general/trained-models`:

| Ruta | Uso |
|------|-----|
| `POST /train` · `/train-async` | Entrenar (`bump_level`: patch/minor/major) |
| `GET /versions` · `/versions/{id}` | Versiones registradas |
| `GET /runs` | Historial de entrenamientos |
| `POST /promote` · `/rollback` | Promover / retroceder |
| `GET /production` | Versión actual en producción |

Configuración: `app/infrastructure/config/model_config.yaml` (`promotion_metric: rmse`, `promotion_tolerance: 0.01`, `min_train_records: 50`).

## Ambientes

| Variable | Dev | Prod |
|----------|-----|------|
| `DEBUG` | `true` | `false` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | `360` |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | URL del frontend |
| Puerto | `8150:8000` | `8150:8000` |

Ambos apuntan a **Supabase** (no hay PostgreSQL local). Variables en `.env.dev` / `.env.prod`.
