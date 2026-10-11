"""Recreate missing mergepoint 5c114c1eec89.

Revision ID: 5c114c1eec89
Revises: o7p8q9r0s1t2
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '5c114c1eec89'
down_revision: Union[str, None] = 'o7p8q9r0s1t2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
