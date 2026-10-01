# Agro Predict API

Backend para tesis: **modelo predictivo de cultivos** con Clean Architecture, FastAPI, PostgreSQL, autenticacion JWT y sistema RBAC (Role-Based Access Control).

## Stack

- **Python 3.13**
- **FastAPI** + Uvicorn
- **SQLAlchemy 2.0** + **Supabase PostgreSQL** (via psycopg2)
- **Alembic** (migraciones)
- **JWT** con `python-jose` + `passlib[bcrypt]`
- **scikit-learn** (RandomForest) + `joblib` para el modelo entrenado
- **Docker** / Docker Compose

## Requisitos previos

### Docker Desktop

Instalar desde https://www.docker.com/products/docker-desktop

### Make (Windows)

```powershell
winget install GnuWin32.Make
```

Despues de instalar, **agregar al PATH del usuario** (ver paso detallado en "Levantar el proyecto").

### Cliente PostgreSQL - psql (para export/import de BD)

```powershell
winget install PostgreSQL.PostgreSQL.16 --silent --accept-package-agreements --accept-source-agreements
```

Solo se necesita el cliente `psql`, no el servidor completo.

### pgAdmin 4 (opcional - interfaz visual para BD)

```powershell
winget install PostgreSQL.pgAdmin --silent --accept-package-agreements --accept-source-agreements
```

## Estructura del proyecto (Clean Architecture)

```
agro-predict-backend/
├── app/
│   ├── domain/                          # NUCLEO (sin dependencias externas)
│   │   ├── entities/                    #   Entidades de negocio (dataclasses)
│   │   ├── repositories/                #   Interfaces ABC (contratos)
│   │   └── use_cases/                   #   Logica de negocio
│   │       ├── auth/                    #     Login
│   │       ├── users/                   #     CRUD usuarios
│   │       ├── roles/                   #     CRUD roles
│   │       ├── crops/                   #     CRUD cultivos
│   │       ├── predictions/             #     Prediccion + historial
│   │       └── permissions/             #     Asignacion de permisos
│   │
│   ├── infrastructure/                  # IMPLEMENTACION EXTERNA
│   │   ├── config/                      #   Settings + JWT + passwords
│   │   ├── database/                    #   Base ORM + session + schemas
│   │   ├── orm/                         #   Modelos SQLAlchemy (core, security)
│   │   ├── repositories/                #   Implementaciones concretas
│   │   └── ml/                          #   Modelo ML + entrenamiento
│   │
│   ├── presentation/                    # API (FastAPI)
│   │   ├── api/                         #   Endpoints + dependencias
│   │   │   ├── deps.py                  #     HTTPBearer, get_current_user
│   │   │   └── v1/endpoints/            #     auth, users, roles, profile, crops, predictions
│   │   └── schemas/                     #   DTOs Pydantic (entrada/salida)
│   │
│   ├── scripts/                         # Scripts CLI (seed, create_admin)
│   └── main.py                          # Creacion de la app FastAPI
├── alembic/                             # Migraciones de base de datos
│   ├── env.py                           #   Configuracion de conexion + schemas
│   ├── script.py.mako                   #   Template para nuevas migraciones
│   └── versions/                        #   Archivos de migracion generados
├── data/                                # Dataset + generador de datos
├── alembic.ini                          # Configuracion de Alembic
├── docker-compose.yml                   # Config base (sin overrides)
├── docker-compose.dev.yml               # Overrides para desarrollo
├── docker-compose.prod.yml              # Overrides para produccion
├── .env.dev                             # Variables de desarrollo (no commitear)
├── .env.prod                            # Variables de produccion (no commitear)
├── Dockerfile
├── Makefile
└── requirements.txt
```

### Flujo de datos (Clean Architecture)

```
HTTP Request → Presentation (schemas) → Use Cases (domain) → Repository Interface → Repository Impl (infrastructure) → DB
```

## Esquemas de base de datos

La base de datos usa **2 esquemas PostgreSQL**:

### `security`

- **users**: id, email, hashed_password, is_admin, status, created_at, updated_at, deleted_at
- **profiles**: id, user_id (FK->users, unique), first_name, last_name, phone, age, status, timestamps
- **roles**: id, name (unique), description, status, timestamps
- **user_roles**: id, user_id (FK->users), role_id (FK->roles), UNIQUE(user_id, role_id), status, timestamps
- **menus**: id, parent_id (FK->menus), name, icon, route, order_index, status, timestamps
- **permissions**: id, code (unique), name, status, timestamps
- **menu_permissions**: id, menu_id (FK->menus), permission_id (FK->permissions), UNIQUE(menu_id, permission_id), status, timestamps
- **role_menu_permissions**: id, role_id (FK->roles), menu_id (FK->menus), permission_id (FK->permissions), UNIQUE(role_id, menu_id, permission_id), status, timestamps

### `core`

- **crops**: id, owner_id (FK->users), name, location, area_hectares, notes, status, timestamps
- **predictions**: id, user_id (FK->users), crop_id (FK->crops), predicted_crop, probability, features ML, status, timestamps

## RBAC (Role-Based Access Control)

### Como funciona

1. **Admin** (`is_admin=True`): acceso total a todo, no necesita role_menu_permissions
2. **Otros usuarios**: obtienen permisos a traves de roles asignados

### Jerarquia de menus

```
Dashboard
├── READ

Cultivos
├── Gestionar Cultivos (CREATE, READ, UPDATE, DELETE)
├── Reporte Cultivos (READ, EXPORT)

Predicciones
├── Gestionar Predicciones (CREATE, READ, UPDATE, DELETE)
├── Reporte Predicciones (READ, EXPORT)

Administracion
├── Usuarios (CREATE, READ, UPDATE, DELETE)
├── Roles (CREATE, READ, UPDATE, DELETE)
├── Permisos (READ)
```

### Seed data (estructura)

Ejecutar una vez para crear menus y permisos:

```bash
make seed
```

El script es idempotente: puede ejecutarse multiples veces sin duplicar datos.

## Migraciones (Alembic)

El proyecto usa **Alembic** para gestionar cambios en la base de datos. Cada vez que modificas un modelo ORM, Alembic genera una migracion automatica.

### Comandos

```bash
# Crear nueva migracion (detecta cambios en los modelos ORM)
make migrate-new msg="descripcion del cambio"

# Aplicar migraciones pendientes (equivalente a dotnet ef database update)
make migrate

# Revertir la ultima migracion (equivalente a dotnet ef migrations remove)
make migrate-down

# Ver historial de migraciones
make migrate-history

# Ver migracion actual aplicada en la BD
make migrate-current
```

### Flujo de trabajo

```bash
# 1. Modificar un modelo ORM (ej: agregar columna phone a users)
#    Archivo: app/infrastructure/orm/security/user.py

# 2. Generar migracion (detecta el cambio automaticamente)
make migrate-new msg="add phone to users"

# 3. Aplicar la migracion
make migrate

# Si algo sale mal, revertir:
make migrate-down
```

### Ejemplo: agregar una columna

```python
# 1. Editar el modelo ORM
# app/infrastructure/orm/security/user.py
class User(BitacoraMixin, Base):
    # ... columnas existentes ...
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # NUEVA

# 2. Generar migracion
# make migrate-new msg="add phone to users"
# Crea: alembic/versions/xxxx_add_phone_to_users.py

# 3. Aplicar
# make migrate
# Ejecuta el upgrade() de la migracion en la BD
```

### Equivalencia con .NET

| .NET (Entity Framework)       | Python (Alembic)           |
| ----------------------------- | -------------------------- |
| `dotnet ef migrations add X`  | `make migrate-new msg="X"` |
| `dotnet ef database update`   | `make migrate`             |
| `dotnet ef migrations remove` | `make migrate-down`        |
| `__EFMigrationsHistory`       | `alembic_version`          |

## Ambientes (dev / prod)

### Configuracion por ambiente

| Variable                      | Dev                         | Prod                  |
| ----------------------------- | --------------------------- | --------------------- |
| `DEBUG`                       | `true`                      | `false`               |
| `SECRET_KEY`                  | clave generica              | clave real segura     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480`                       | `360`                 |
| `CORS_ORIGINS`                | `["http://localhost:5173"]` | URL del frontend real |
| Puerto API                    | `8150:8000`                 | `8150:8000`           |

**Nota:** Ambos ambientes se conectan a **Supabase** (no hay PostgreSQL local).

## Levantar el proyecto

### Instalar Make (Windows)

Make no viene instalado por defecto en Windows. Instalar con winget:

```powershell
winget install GnuWin32.Make
```

Despues de instalar, **agregar al PATH del usuario**:

```powershell
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "C:\Program Files (x86)\GnuWin32\bin"
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$newPath", "User")
```

**Importante:** Cerrar y abrir completamente la terminal (o VS Code) para que el PATH se actualice. Verificar con:

```powershell
make --version
```

### Usando Make (recomendado)

```bash
# Dev
make dev              # Levantar sin rebuild (cambios en codigo)
make dev-build        # Levantar entorno(Cuando se hacen cambios en Dockerfile o requirements.txt)

# Prod
make prod             # Levantar sin rebuild (cambios en codigo)
make prod-build       # Levantar en entorno de produccion (con rebuild)

# Scripts Python
make seed             # Ejecutar seed_data.py (menus + permisos)
make admin            # Crear usuario administrador
make train            # Entrenar modelo ML
make generate-data    # Generar dataset

# Migraciones (Alembic)
make migrate-new msg="descripcion"   # Generar nueva migracion
make migrate                          # Aplicar migraciones pendientes
make migrate-down                     # Revertir ultima migracion
make migrate-history                  # Ver historial de migraciones
make migrate-current                  # Ver migracion actual en la BD

# Utilidades
make shell            # Abrir terminal interactiva dentro del contenedor
make logs             # Ver logs de todos los servicios
make down             # Detener contenedores
make dev-reset        # Detener y eliminar volumenes(borrar TODO incluyendo la BD)
```

### Desarrollo (sin Make)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

- API: `http://localhost:8150`
- Docs Swagger: `http://localhost:8150/docs`
- Base de datos: **Supabase** (remoto)
- Variables: lee `.env`

### Produccion (sin Make)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

- API: `http://localhost:8150`
- Docs Swagger: deshabilitar o proteger con auth
- Base de datos: **Supabase** (remoto)
- Variables: lee `.env`
- Contenedores con `restart: always`

### Solo local (sin Docker)

```bash
# 1. Entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

# 2. Verificar que .env contiene DATABASE_URL de Supabase

# 3. Dataset y modelo
python -m data.generate_dataset
python -m app.infrastructure.ml.train

# 4. Aplicar migraciones (crea las tablas en Supabase)
alembic upgrade head

# 5. Levantar
uvicorn app.main:app --reload

# 6. Seed + admin (una sola vez)
python -m app.scripts.seed_data
python -m app.scripts.create_admin
```

## Configurar .env.prod

**Importante:** antes de usar en produccion, cambiar estas variables:

```bash
# Generar una clave segura para SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Generar una contrasena segura para PostgreSQL
python -c "import secrets; print(secrets.token_urlsafe(32))"

```

Cambiar en `.env`:

- `SECRET_KEY`: usar la clave generada
- `DATABASE_URL`: verificar que apunta a Supabase con `?sslmode=require`
- `CORS_ORIGINS`: URL real del frontend

## Uso rapido (curl)

```bash
# Registrar usuario
curl -X POST http://localhost:8150/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tesis.com","password":"secret123"}'

# Obtener token JWT
curl -X POST http://localhost:8150/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tesis.com","password":"secret123"}'

# CRUD de cultivos
curl http://localhost:8150/api/v1/crops \
  -H "Authorization: Bearer <token>"

# Prediccion
curl -X POST http://localhost:8150/api/v1/predictions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"N":90,"P":42,"K":43,"temperature":20.8,"humidity":82,"ph":6.5,"rainfall":202}'
```

## Endpoints

### Auth

| Metodo | Ruta                    | Auth | Descripcion                     |
| ------ | ----------------------- | ---- | ------------------------------- |
| POST   | `/api/v1/auth/register` | -    | Registrar usuario               |
| POST   | `/api/v1/auth/login`    | -    | Login (email + password) -> JWT |
| GET    | `/api/v1/users/me`      | JWT  | Perfil del usuario              |
| PATCH  | `/api/v1/users/me`      | JWT  | Actualizar perfil               |
| DELETE | `/api/v1/users/me`      | JWT  | Eliminar cuenta                 |

### Crops

| Metodo | Ruta                 | Auth | Descripcion        |
| ------ | -------------------- | ---- | ------------------ |
| GET    | `/api/v1/crops`      | JWT  | Listar cultivos    |
| POST   | `/api/v1/crops`      | JWT  | Crear cultivo      |
| GET    | `/api/v1/crops/{id}` | JWT  | Obtener cultivo    |
| PATCH  | `/api/v1/crops/{id}` | JWT  | Actualizar cultivo |
| DELETE | `/api/v1/crops/{id}` | JWT  | Eliminar cultivo   |

### Predictions

| Metodo | Ruta                  | Auth | Descripcion               |
| ------ | --------------------- | ---- | ------------------------- |
| POST   | `/api/v1/predictions` | JWT  | Predecir cultivo          |
| GET    | `/api/v1/predictions` | JWT  | Historial de predicciones |

### Admin (requiere is_admin=True)

| Metodo | Ruta                                            | Auth  | Descripcion                             |
| ------ | ----------------------------------------------- | ----- | --------------------------------------- |
| GET    | `/api/v1/admin/users`                           | Admin | Listar usuarios con perfiles            |
| POST   | `/api/v1/admin/users`                           | Admin | Crear usuario con perfil y roles        |
| GET    | `/api/v1/admin/users/{id}`                      | Admin | Obtener usuario                         |
| PATCH  | `/api/v1/admin/users/{id}`                      | Admin | Actualizar perfil                       |
| PATCH  | `/api/v1/admin/users/{id}/roles`                | Admin | Asignar roles                           |
| GET    | `/api/v1/admin/roles`                           | Admin | Listar roles                            |
| POST   | `/api/v1/admin/roles`                           | Admin | Crear rol                               |
| GET    | `/api/v1/admin/roles/{id}`                      | Admin | Obtener rol                             |
| PATCH  | `/api/v1/admin/roles/{id}`                      | Admin | Actualizar rol                          |
| DELETE | `/api/v1/admin/roles/{id}`                      | Admin | Eliminar rol                            |
| GET    | `/api/v1/admin/menus`                           | Admin | Arbol de menus con permisos disponibles |
| GET    | `/api/v1/admin/menus/{id}`                      | Admin | Menu especifico                         |
| GET    | `/api/v1/admin/permissions`                     | Admin | Listar permisos                         |
| POST   | `/api/v1/admin/role-menu-permissions`           | Admin | Asignar permiso a rol                   |
| GET    | `/api/v1/admin/role-menu-permissions/{role_id}` | Admin | Permisos de un rol                      |
| DELETE | `/api/v1/admin/role-menu-permissions/{rmp_id}`  | Admin | Remover permiso                         |

Documentacion interactiva: `http://localhost:8150/docs`

## Modelo ML

- **Entrada (7 features):** N, P, K (nutrientes del suelo), temperatura, humedad, pH, precipitacion.
- **Salida:** cultivo recomendado + probabilidad (RandomForest).
- Modelo entrenado en `app/infrastructure/ml/artifacts/crop_model.joblib`.

Reentrenar con datos propios:

```bash
# Coloca tu dataset en data/crop_data.csv
# Columnas: N,P,K,temperature,humidity,ph,rainfall,label
python -m app.infrastructure.ml.train
```

## Versionamiento del Modelo (SemVer)

El proyecto implementa versionado semantico automatico para el modelo de prediccion de rendimiento (`prediccion-rendimiento`).

### Reglas de versionado

| Nivel | Cuando aplicar | Ejemplo |
|-------|----------------|---------|
| **PATCH** (1.0.2 → 1.0.3) | Reentrenamiento con datos nuevos, misma arquitectura, features e hiperparámetros. **Por defecto.** | Se agregan registros nuevos de entrenamiento |
| **MINOR** (1.0.3 → 1.1.0) | Cambian features o hiperparámetros de forma relevante; el esquema de entrada sigue compatible. Resetea PATCH a 0. | Se agrega feature `ndvi`, se cambia `n_estimators` |
| **MAJOR** (1.1.0 → 2.0.0) | Cambia el algoritmo, el target o el esquema de entrada. Resetea MINOR y PATCH a 0. | Se cambia de RandomForest a XGBoost, o se predice otra variable |

### Flujo de entrenamiento con versionado

```
POST /api/v1/general/trained-models/train?bump_level=patch|minor|major
    │
    ├─► Entrena RandomForest + LinearRegression con split temporal (últimos 6 meses test)
    │
    ├─► Evalúa ambos en test set → candidatos_evaluados JSON
    │
    ├─► Selecciona ganador (mejor RMSE con tolerancia 1%)
    │
    ├─► Compara ganador vs modelo en PRODUCCIÓN (baseline)
    │       │
    │       ├─► SI supera: bump_version(patch|minor|major)
    │       │       ├─► Guarda artefactos en modelos/{version}/
    │       │       ├─► INSERT modelo_version (estado='candidato')
    │       │       ├─► INSERT modelo_runs (genero_version=true)
    │       │       └─► Retorna versión candidata
    │       │
    │       └─► NO supera:
    │           ├─► INSERT modelo_runs (genero_version=false, motivo='no_supero_baseline')
    │           └─► Retorna run sin versión nueva
    │
    ▼
POST /api/v1/general/trained-models/promote {version_id}
    │
    ├─► Valida: ningún algoritmo empeora vs producción actual (>5% tolerancia)
    │
    ├─► TX: UPDATE estado='archivado' WHERE estado='produccion'
    │
    ├─► TX: UPDATE estado='produccion' WHERE id={version_id}
    │
    └─► Git tag opcional: model-v{version}
```

### Endpoints de versionado

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/v1/general/trained-models/train` | Entrenar con bump_level (patch/minor/major) |
| POST | `/api/v1/general/trained-models/train-async` | Entrenamiento asíncrono con bump_level |
| GET | `/api/v1/general/trained-models/versions` | Listar todas las versiones del modelo |
| GET | `/api/v1/general/trained-models/versions/{id}` | Obtener versión específica |
| GET | `/api/v1/general/trained-models/runs` | Listar runs de entrenamiento |
| POST | `/api/v1/general/trained-models/promote` | Promover candidato a producción |
| POST | `/api/v1/general/trained-models/rollback` | Rollback a versión anterior |
| GET | `/api/v1/general/trained-models/production` | Obtener modelo actual en producción |

### Ejemplo de uso

```bash
# Entrenar con bump PATCH (por defecto)
curl -X POST http://localhost:8150/api/v1/general/trained-models/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"algorithms":["random_forest","linear_regression"],"bump_level":"patch"}'

# Entrenar con bump MINOR
curl -X POST http://localhost:8150/api/v1/general/trained-models/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"algorithms":["random_forest","linear_regression"],"bump_level":"minor"}'

# Promover versión candidata a producción
curl -X POST http://localhost:8150/api/v1/general/trained-models/promote \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"versionId": 5}'

# Rollback a versión anterior
curl -X POST http://localhost:8150/api/v1/general/trained-models/rollback \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"versionId": 3}'

# Ver modelo actual en producción
curl http://localhost:8150/api/v1/general/trained-models/production \
  -H "Authorization: Bearer <token>"
```

### Tablas en BD

| Tabla | Descripcion |
|-------|-------------|
| `core.modelo_version` | Versiones registradas del modelo (candidato/produccion/archivado) |
| `core.modelo_runs` | Historial de todos los entrenamientos (incluye los que no generaron versión) |
| `core.predictions` | Predicciones con FK `modelo_version_id` para trazabilidad |

### Configuración (`app/infrastructure/config/model_config.yaml`)

```yaml
model:
  name: "prediccion-rendimiento"
  algorithms:
    - "random_forest"
    - "linear_regression"
  promotion_metric: "rmse"
  promotion_tolerance: 0.01
  random_seed: 42

training:
  test_window_months: 6
  min_train_records: 50
  temporal_split_column: "created_at"

artifacts:
  base_path: "app/infrastructure/ml/artifacts/modelos"
  include_version_in_path: true
```

### Ejemplo de registro en BD (`modelo_version`)

```json
{
  "modelo": "prediccion-rendimiento",
  "version": "1.3.0",
  "estado": "candidato",
  "entrenado_en": "2026-09-15T10:30:00",
  "git_commit": "a1b2c3d",
  "data_version": "datos_v2026-09-15",
  "data_desde": "2018-01-01",
  "data_hasta": "2026-08-31",
  "features": ["temperatura", "precipitacion", "ndvi", "tipo_suelo"],
  "candidatos_evaluados": {
    "random_forest": {"rmse": 0.42, "mae": 0.31, "artefacto": "modelos/1.3.0/random_forest.joblib"},
    "linear_regression": {"rmse": 0.55, "mae": 0.44, "artefacto": "modelos/1.3.0/linear_regression.joblib"}
  },
  "metricas": {"rmse": 0.42, "mae": 0.31, "r2": 0.85},
  "baseline_compared": "1.2.1",
  "ruta_artefacto": "modelos/1.3.0/"
}
```

## Conexion a la base de datos

### Desde DBeaver / pgAdmin (desarrollo)

Conectar directamente a Supabase:

- Host: `aws-0-us-east-1.pooler.supabase.com`
- Puerto: `5432`
- Database: `postgres`
- User: `postgres.eqhzwaylqbusidlcpkvs`
- Password: `AgroPrdict-lvbo87Pz4l1qui4w`
- SSL: `require`

### Desde dentro de otro contenedor Docker

```bash
# La app se conecta via DATABASE_URL en .env
# No hay PostgreSQL local, todo va a Supabase
```

### Esquemas

```sql
-- Ver esquemas
SELECT schema_name FROM information_schema.schemata;

-- Ver tablas del esquema security
SELECT table_name FROM information_schema.tables WHERE table_schema = 'security';

-- Ver menus
SELECT * FROM security.menus ORDER BY order_index;

-- Ver permisos
SELECT * FROM security.permissions;

-- Ver menu_permissions (que permisos tiene cada menu)
SELECT m.name as menu, p.code as permission
FROM security.menu_permissions mp
JOIN security.menus m ON mp.menu_id = m.id
JOIN security.permissions p ON mp.permission_id = p.id
ORDER BY m.order_index, p.code;

-- Ver role_menu_permissions (que permisos tiene cada rol)
SELECT r.name as role, m.name as menu, p.code as permission
FROM security.role_menu_permissions rmp
JOIN security.roles r ON rmp.role_id = r.id
JOIN security.menus m ON rmp.menu_id = m.id
JOIN security.permissions p ON rmp.permission_id = p.id
ORDER BY r.name, m.order_index, p.code;
```
