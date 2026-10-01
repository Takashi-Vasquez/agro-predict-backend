"""add_model_version_table

Revision ID: j2k3l4m5n6o7
Revises: i1j2k3l4m5n6
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'j2k3l4m5n6o7'
down_revision: Union[str, None] = 'i1j2k3l4m5n6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type if not exists
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'model_version_status') THEN
                CREATE TYPE core.model_version_status AS ENUM ('candidate', 'production', 'archived');
            END IF;
        END $$;
    """)

    # Create model_version table using raw SQL to avoid SQLAlchemy enum issues
    op.execute("""
        CREATE TABLE core.model_version (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(100) NOT NULL,
            version VARCHAR(50) NOT NULL,
            status core.model_version_status NOT NULL DEFAULT 'candidate',
            trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            git_commit VARCHAR(100),
            data_version VARCHAR(100),
            data_from DATE,
            data_to DATE,
            features JSONB,
            candidates_evaluated JSONB,
            metrics JSONB,
            baseline_compared VARCHAR(50),
            base_version_id INTEGER,
            artifact_path VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        )
    """)

    # Add foreign key
    op.execute("""
        ALTER TABLE core.model_version
        ADD CONSTRAINT fk_model_version_base
        FOREIGN KEY (base_version_id) REFERENCES core.model_version(id)
    """)

    # Add unique constraint
    op.execute("""
        ALTER TABLE core.model_version
        ADD CONSTRAINT uq_model_version_model_version UNIQUE (model_name, version)
    """)

    # Partial unique index: only one version in 'production' per model
    op.execute("""
        CREATE UNIQUE INDEX uq_model_version_production
        ON core.model_version (model_name)
        WHERE status = 'production'
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS core.uq_model_version_production")
    op.execute("DROP TABLE IF EXISTS core.model_version")
    op.execute("DROP TYPE IF EXISTS core.model_version_status")