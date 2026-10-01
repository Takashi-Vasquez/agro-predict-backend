"""remove row_number and error_message from training_records

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-09-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "h3i4j5k6l7m8"
down_revision = "g2h3i4j5k6l7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("training_records", "row_number", schema="core")
    op.drop_column("training_records", "error_message", schema="core")


def downgrade() -> None:
    op.add_column(
        "training_records",
        sa.Column("row_number", sa.Integer, nullable=True),
        schema="core",
    )
    op.add_column(
        "training_records",
        sa.Column("error_message", sa.String(500), nullable=True),
        schema="core",
    )
