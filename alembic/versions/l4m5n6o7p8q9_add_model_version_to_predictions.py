"""add_model_version_to_predictions

Revision ID: l4m5n6o7p8q9
Revises: k3l4m5n6o7p8
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'l4m5n6o7p8q9'
down_revision: Union[str, None] = 'n6o7p8q9r0s1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE core.predictions
        ADD COLUMN IF NOT EXISTS model_version_id INTEGER
    """)

    op.execute("""
        ALTER TABLE core.predictions
        ADD CONSTRAINT fk_predictions_model_version
        FOREIGN KEY (model_version_id) REFERENCES core.model_version(id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_predictions_model_version_id
        ON core.predictions (model_version_id)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS core.ix_predictions_model_version_id")
    op.execute("ALTER TABLE core.predictions DROP CONSTRAINT IF EXISTS fk_predictions_model_version")
    op.execute("ALTER TABLE core.predictions DROP COLUMN IF EXISTS model_version_id")