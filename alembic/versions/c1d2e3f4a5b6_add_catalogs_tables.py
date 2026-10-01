"""add catalogs and catalog_details tables

Revision ID: c1d2e3f4a5b6
Revises: b1a2c3d4e5f6
Create Date: 2026-09-22 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b1a2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table: str, schema: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema = :schema AND table_name = :table)"
    ), {"schema": schema, "table": table})
    return result.scalar()


def upgrade() -> None:
    if not _table_exists("catalogs", "core"):
        op.create_table(
            "catalogs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("code", sa.String(100), unique=True, nullable=False, index=True),
            sa.Column("label", sa.String(150), nullable=False),
            sa.Column("description", sa.String(500), nullable=True),
            sa.Column("is_active", sa.Boolean, default=True, nullable=False),
            sa.Column("status", sa.String(20), default="ACTIVE", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            schema="core",
        )

    if not _table_exists("catalog_details", "core"):
        op.create_table(
            "catalog_details",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("catalog_id", sa.Integer, sa.ForeignKey("core.catalogs.id"), nullable=False, index=True),
            sa.Column("value", sa.String(100), nullable=False),
            sa.Column("label", sa.String(150), nullable=False),
            sa.Column("order_index", sa.Integer, default=0, nullable=False),
            sa.Column("is_active", sa.Boolean, default=True, nullable=False),
            sa.Column("status", sa.String(20), default="ACTIVE", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            schema="core",
        )


def downgrade() -> None:
    if _table_exists("catalog_details", "core"):
        op.drop_table("catalog_details", schema="core")
    if _table_exists("catalogs", "core"):
        op.drop_table("catalogs", schema="core")
