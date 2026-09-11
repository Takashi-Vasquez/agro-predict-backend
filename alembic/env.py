import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool, text

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.base import Base

# Añade el directorio raíz al sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Importa TODOS los modelos para que Base.metadata los conozca
import app.infrastructure.orm.core.crop  # noqa: F401
import app.infrastructure.orm.core.prediction  # noqa: F401
import app.infrastructure.orm.security.profile  # noqa: F401
import app.infrastructure.orm.security.role  # noqa: F401
import app.infrastructure.orm.security.user_role  # noqa: F401
import app.infrastructure.orm.security.menu  # noqa: F401
import app.infrastructure.orm.security.permission  # noqa: F401
import app.infrastructure.orm.security.menu_permission  # noqa: F401
import app.infrastructure.orm.security.role_menu_permission  # noqa: F401

# Configuración de logging desde alembic.ini
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de SQLAlchemy (target_metadata)
target_metadata = Base.metadata

# Obtener DATABASE_URL desde settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def include_names(name, type_, reflection_metadata):
    """Incluir solo los schemas que usamos (NO incluir 'auth' - es de Supabase)."""
    if type_ == "schema":
        return name in ("core", "security", "public")
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="public",
        include_name=include_names,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Crear schemas si no existen (NO crear 'auth' - es de Supabase)
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS security"))
        connection.commit()

        # Configurar search_path via execution_options (persiste para la sesión)
        connection = connection.execution_options(
            schema_search_path="auth, core, security, public"
        )

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="public",
            include_name=include_names,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
