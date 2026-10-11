"""drop users.company_id, backfill user_company from it

Revision ID: a3f5b2c8d9e1
Revises: fc6798867a4d
Create Date: 2026-10-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f5b2c8d9e1'
down_revision: Union[str, None] = 'fc6798867a4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill: one user_company row per user with company_id and no row yet,
    # so no user loses access when the column is dropped.
    op.execute("""
        INSERT INTO security.user_company (user_id, company_id, is_default, is_active, status, created_at, updated_at)
        SELECT u.id, u.company_id, TRUE, TRUE, 'ACTIVE', NOW(), NOW()
        FROM security.users u
        WHERE u.company_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM security.user_company uc
              WHERE uc.user_id = u.id AND uc.company_id = u.company_id
          )
    """)

    # Drops ix_security_users_company_id and fk_users_company automatically (PostgreSQL)
    op.drop_column('users', 'company_id', schema='security')


def downgrade() -> None:
    op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True), schema='security')
    op.create_index('ix_security_users_company_id', 'users', ['company_id'], unique=False, schema='security')
    op.create_foreign_key('fk_users_company', 'users', 'company', ['company_id'], ['id'], source_schema='security', referent_schema='core')
    op.execute("""
        UPDATE security.users u
        SET company_id = uc.company_id
        FROM security.user_company uc
        WHERE uc.user_id = u.id AND uc.is_default = TRUE
    """)
