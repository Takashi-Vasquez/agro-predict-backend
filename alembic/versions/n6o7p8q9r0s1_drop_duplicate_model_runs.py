"""drop_duplicate_model_runs_table

Revision ID: n6o7p8q9r0s1
Revises: j2k3l4m5n6o7
Create Date: 2026-09-30

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'n6o7p8q9r0s1'
down_revision: Union[str, None] = 'j2k3l4m5n6o7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS core.model_runs")


def downgrade() -> None:
    op.execute("""
        CREATE TABLE core.model_runs (
            id SERIAL PRIMARY KEY,
            model_version_id INTEGER,
            trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            git_commit VARCHAR(100),
            data_version VARCHAR(100),
            data_from DATE,
            data_to DATE,
            candidates_evaluated JSONB,
            winner VARCHAR(50),
            improvement_vs_baseline DOUBLE PRECISION,
            generated_version BOOLEAN NOT NULL DEFAULT FALSE,
            reason_no_version VARCHAR(100),
            duration_seconds INTEGER
        )
    """)

    op.execute("""
        ALTER TABLE core.model_runs
        ADD CONSTRAINT fk_model_runs_version
        FOREIGN KEY (model_version_id) REFERENCES core.model_version(id)
    """)

    op.execute("""
        CREATE INDEX ix_model_runs_trained_at ON core.model_runs (trained_at)
    """)