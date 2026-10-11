"""add company and user_company tables

Revision ID: c5a2ce4d1fe9
Revises: 5c114c1eec89
Create Date: 2026-10-07 22:31:43.430160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5a2ce4d1fe9'
down_revision: Union[str, None] = '5c114c1eec89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS core.company (
            id SERIAL PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            ruc VARCHAR(20) UNIQUE,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_core_company_id ON core.company (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_core_company_code ON core.company (code)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_core_company_ruc ON core.company (ruc)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS security.user_company (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES security.users(id) ON DELETE CASCADE,
            company_id INTEGER NOT NULL REFERENCES core.company(id) ON DELETE CASCADE,
            is_default BOOLEAN NOT NULL DEFAULT FALSE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ,
            CONSTRAINT uq_user_company UNIQUE (user_id, company_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_security_user_company_id ON security.user_company (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_security_user_company_user_id ON security.user_company (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_security_user_company_company_id ON security.user_company (company_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS security.user_company")
    op.execute("DROP TABLE IF EXISTS core.company")
