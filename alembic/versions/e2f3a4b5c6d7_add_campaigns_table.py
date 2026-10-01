"""add campaigns table

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-09-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
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
    if not _table_exists("campaigns", "core"):
        op.create_table(
            "campaigns",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("security.users.id"), nullable=False, index=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("crop_id", sa.Integer, sa.ForeignKey("operations.crops.id"), nullable=False, index=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="PLANIFICADA"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            schema="core",
        )


def downgrade() -> None:
    if _table_exists("campaigns", "core"):
        op.drop_table("campaigns", schema="core")
