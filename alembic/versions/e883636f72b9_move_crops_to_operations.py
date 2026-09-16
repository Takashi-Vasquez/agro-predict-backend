"""move crops to operations schema

Revision ID: e883636f72b9
Revises: 5ca8d3ce812a
Create Date: 2026-09-16 17:05:12.880725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e883636f72b9'
down_revision: Union[str, None] = '5ca8d3ce812a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS operations")

    # Drop the empty operations.crops created by SQLAlchemy on startup
    op.execute("DROP TABLE IF EXISTS operations.crops")

    # Drop indexes on core.crops before moving
    op.execute("DROP INDEX IF EXISTS core.ix_core_crops_id")
    op.execute("DROP INDEX IF EXISTS core.ix_core_crops_owner_id")

    # Move table from core to operations
    op.execute("ALTER TABLE core.crops SET SCHEMA operations")

    # Recreate indexes with new schema name
    op.execute("CREATE INDEX ix_operations_crops_id ON operations.crops (id)")
    op.execute("CREATE INDEX ix_operations_crops_owner_id ON operations.crops (owner_id)")

    # Update FK in predictions to point to operations.crops
    op.drop_constraint("predictions_crop_id_fkey", "predictions", schema="core", type_="foreignkey")
    op.create_foreign_key(
        "predictions_crop_id_fkey",
        "predictions",
        "crops",
        ["crop_id"],
        ["id"],
        source_schema="core",
        referent_schema="operations",
    )


def downgrade() -> None:
    op.drop_constraint("predictions_crop_id_fkey", "predictions", schema="core", type_="foreignkey")
    op.create_foreign_key(
        "predictions_crop_id_fkey",
        "predictions",
        "crops",
        ["crop_id"],
        ["id"],
        source_schema="core",
        referent_schema="core",
    )

    op.execute("DROP INDEX IF EXISTS operations.ix_operations_crops_id")
    op.execute("DROP INDEX IF EXISTS operations.ix_operations_crops_owner_id")

    op.execute("ALTER TABLE operations.crops SET SCHEMA core")

    op.execute("CREATE INDEX ix_core_crops_id ON core.crops (id)")
    op.execute("CREATE INDEX ix_core_crops_owner_id ON core.crops (owner_id)")
