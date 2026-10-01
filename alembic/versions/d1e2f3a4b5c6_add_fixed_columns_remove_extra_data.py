"""add irrigation_type, variety columns, remove extra_data

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
Create Date: 2026-09-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str, schema: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = :schema AND table_name = :table AND column_name = :column)"
    ), {"schema": schema, "table": table, "column": column})
    return result.scalar()


def upgrade() -> None:
    if not _column_exists("training_records", "irrigation_type", "core"):
        op.add_column("training_records", sa.Column("irrigation_type", sa.String(50), nullable=True), schema="core")

    if not _column_exists("training_records", "variety", "core"):
        op.add_column("training_records", sa.Column("variety", sa.String(100), nullable=True), schema="core")

    op.execute(sa.text(
        "UPDATE core.training_records "
        "SET irrigation_type = extra_data->>'irrigation_type', "
        "    variety = extra_data->>'variety' "
        "WHERE extra_data IS NOT NULL"
    ))

    if _column_exists("training_records", "extra_data", "core"):
        op.drop_column("training_records", "extra_data", schema="core")


def downgrade() -> None:
    if not _column_exists("training_records", "extra_data", "core"):
        op.add_column("training_records", sa.Column("extra_data", sa.JSON, nullable=True), schema="core")

    op.execute(sa.text(
        "UPDATE core.training_records "
        "SET extra_data = jsonb_build_object("
        "  'irrigation_type', irrigation_type,"
        "  'variety', variety"
        ") "
        "WHERE irrigation_type IS NOT NULL OR variety IS NOT NULL"
    ))

    if _column_exists("training_records", "variety", "core"):
        op.drop_column("training_records", "variety", schema="core")
    if _column_exists("training_records", "irrigation_type", "core"):
        op.drop_column("training_records", "irrigation_type", schema="core")
