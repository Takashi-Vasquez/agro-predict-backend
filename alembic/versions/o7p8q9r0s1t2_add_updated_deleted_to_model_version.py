"""add_updated_deleted_to_model_version

Revision ID: o7p8q9r0s1t2
Revises: m5n6o7p8q9r0
Create Date: 2026-09-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'o7p8q9r0s1t2'
down_revision: Union[str, None] = 'l4m5n6o7p8q9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE core.model_version
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
    """)
    op.execute("""
        ALTER TABLE core.model_version
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE core.model_version DROP COLUMN IF EXISTS updated_at")
    op.execute("ALTER TABLE core.model_version DROP COLUMN IF EXISTS deleted_at")