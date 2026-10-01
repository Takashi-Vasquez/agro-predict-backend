"""add soil_type to training_records

Revision ID: f1a2b3c4d5e6
Revises: e2f3a4b5c6d7
Create Date: 2026-09-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "e2f3a4b5c6d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "training_records",
        sa.Column("soil_type", sa.String(50), nullable=True),
        schema="core",
    )


def downgrade() -> None:
    op.drop_column("training_records", "soil_type", schema="core")
