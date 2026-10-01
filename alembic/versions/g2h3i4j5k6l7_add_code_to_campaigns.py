"""add code to campaigns

Revision ID: g2h3i4j5k6l7
Revises: f1a2b3c4d5e6
Create Date: 2026-09-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "g2h3i4j5k6l7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "campaigns",
        sa.Column("code", sa.String(50), nullable=True),
        schema="core",
    )
    op.execute("UPDATE core.campaigns SET code = 'CAMP-' || id WHERE code IS NULL")
    op.alter_column("campaigns", "code", nullable=False, schema="core")
    op.create_unique_constraint(
        "uq_campaign_code",
        "campaigns",
        ["code"],
        schema="core",
    )


def downgrade() -> None:
    op.drop_constraint("uq_campaign_code", "campaigns", schema="core")
    op.drop_column("campaigns", "code", schema="core")
