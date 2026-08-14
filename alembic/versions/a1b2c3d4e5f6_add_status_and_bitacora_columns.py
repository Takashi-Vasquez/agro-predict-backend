"""add status and bitacora columns

Revision ID: a1b2c3d4e5f6
Revises: fbb02c990ae3
Create Date: 2026-08-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fbb02c990ae3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear enum type en schema public
    op.execute("CREATE TYPE record_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED')")

    # --- auth.users ---
    op.execute("ALTER TABLE auth.users ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE auth.users ADD COLUMN deleted_at TIMESTAMPTZ NULL")
    op.execute("ALTER TABLE auth.users RENAME COLUMN created_at TO _created_at_old")
    op.execute("ALTER TABLE auth.users ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("UPDATE auth.users SET created_at = _created_at_old")
    op.execute("ALTER TABLE auth.users DROP COLUMN _created_at_old")
    op.execute("ALTER TABLE auth.users RENAME COLUMN updated_at TO _updated_at_old")
    op.execute("ALTER TABLE auth.users ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("UPDATE auth.users SET updated_at = _updated_at_old")
    op.execute("ALTER TABLE auth.users DROP COLUMN _updated_at_old")
    op.execute("ALTER TABLE auth.users DROP COLUMN is_active")

    # --- core.crops ---
    op.execute("ALTER TABLE core.crops ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE core.crops ADD COLUMN deleted_at TIMESTAMPTZ NULL")

    # --- core.predictions ---
    op.execute("ALTER TABLE core.predictions ADD COLUMN deleted_at TIMESTAMPTZ NULL")
    op.execute("ALTER TABLE core.predictions DROP COLUMN status")

    # --- security.profiles ---
    op.execute("ALTER TABLE security.profiles ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.profiles ADD COLUMN deleted_at TIMESTAMPTZ NULL")

    # --- security.roles ---
    op.execute("ALTER TABLE security.roles ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.roles ADD COLUMN deleted_at TIMESTAMPTZ NULL")

    # --- security.menus ---
    op.execute("ALTER TABLE security.menus ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.menus ADD COLUMN deleted_at TIMESTAMPTZ NULL")
    op.execute("ALTER TABLE security.menus DROP COLUMN is_active")

    # --- security.permissions ---
    op.execute("ALTER TABLE security.permissions ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.permissions ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.permissions ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.permissions ADD COLUMN deleted_at TIMESTAMPTZ NULL")

    # --- security.menu_permissions ---
    op.execute("ALTER TABLE security.menu_permissions ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.menu_permissions ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.menu_permissions ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.menu_permissions ADD COLUMN deleted_at TIMESTAMPTZ NULL")

    # --- security.role_menu_permissions ---
    op.execute("ALTER TABLE security.role_menu_permissions ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.role_menu_permissions ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.role_menu_permissions ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.role_menu_permissions ADD COLUMN deleted_at TIMESTAMPTZ NULL")

    # --- security.user_roles ---
    op.execute("ALTER TABLE security.user_roles ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'")
    op.execute("ALTER TABLE security.user_roles ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.user_roles ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TABLE security.user_roles ADD COLUMN deleted_at TIMESTAMPTZ NULL")


def downgrade() -> None:
    # Restaurar columnas eliminadas
    op.execute("ALTER TABLE auth.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
    op.execute("ALTER TABLE security.menus ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
    op.execute("ALTER TABLE core.predictions ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ok'")

    # Eliminar columnas agregadas
    for schema, table in [
        ("auth", "users"),
        ("core", "crops"),
        ("core", "predictions"),
        ("security", "profiles"),
        ("security", "roles"),
        ("security", "menus"),
        ("security", "permissions"),
        ("security", "menu_permissions"),
        ("security", "role_menu_permissions"),
        ("security", "user_roles"),
    ]:
        op.execute(f"ALTER TABLE {schema}.{table} DROP COLUMN IF EXISTS status")
        op.execute(f"ALTER TABLE {schema}.{table} DROP COLUMN IF EXISTS deleted_at")
        if schema == "security" and table in ("permissions", "menu_permissions", "role_menu_permissions", "user_roles"):
            op.execute(f"ALTER TABLE {schema}.{table} DROP COLUMN IF EXISTS created_at")
            op.execute(f"ALTER TABLE {schema}.{table} DROP COLUMN IF EXISTS updated_at")

    op.execute("DROP TYPE IF EXISTS record_status")
