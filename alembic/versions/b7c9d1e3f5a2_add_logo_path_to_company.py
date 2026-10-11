"""add logo_path to company

Revision ID: b7c9d1e3f5a2
Revises: a3f5b2c8d9e1
Create Date: 2026-10-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c9d1e3f5a2'
down_revision: Union[str, None] = 'a3f5b2c8d9e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'company',
        sa.Column('logo_path', sa.String(length=255), nullable=True),
        schema='core',
    )


def downgrade() -> None:
    op.drop_column('company', 'logo_path', schema='core')
