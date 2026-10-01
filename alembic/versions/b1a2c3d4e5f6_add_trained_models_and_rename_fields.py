"""add trained_models table and rename training field columns

Revision ID: b1a2c3d4e5f6
Revises: 951b5c802655
Create Date: 2026-09-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = 'b1a2c3d4e5f6'
down_revision: Union[str, None] = '951b5c802655'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str, schema: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = :schema AND table_name = :table AND column_name = :col)"
    ), {"schema": schema, "table": table, "col": column})
    return result.scalar()


def _table_exists(table: str, schema: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema = :schema AND table_name = :table)"
    ), {"schema": schema, "table": table})
    return result.scalar()


def upgrade() -> None:
    # --- trained_models table (idempotent) ---
    if not _table_exists("trained_models", "core"):
        op.create_table(
            "trained_models",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("security.users.id"), nullable=False, index=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("algorithm", sa.String(50), nullable=False),
            sa.Column("version", sa.String(50), nullable=False),
            sa.Column("r2_score", sa.Float, nullable=False),
            sa.Column("rmse", sa.Float, nullable=True),
            sa.Column("mae", sa.Float, nullable=True),
            sa.Column("feature_importance", JSONB, nullable=True),
            sa.Column("hyperparameters", JSONB, nullable=True),
            sa.Column("training_samples", sa.Integer, nullable=True),
            sa.Column("feature_names", JSONB, nullable=True),
            sa.Column("artifact_path", sa.String(500), nullable=True),
            sa.Column("is_selected", sa.Boolean, default=False, nullable=False),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("status", sa.String(20), default="ACTIVE", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            schema="core",
        )
        op.create_index("ix_core_trained_models_user_id", "trained_models", ["user_id"], schema="core")
        op.create_index("ix_core_trained_models_status", "trained_models", ["status"], schema="core")

    # --- rename columns in training_records (idempotent) ---
    rename_map = {
        "N": "nitrogen",
        "P": "phosphorus",
        "K": "potassium",
        "ph": "ph_soil",
    }
    for old_name, new_name in rename_map.items():
        if _column_exists("training_records", old_name, "core") and not _column_exists("training_records", new_name, "core"):
            op.alter_column("training_records", old_name, new_column_name=new_name, schema="core")

    # --- rename columns in predictions (idempotent) ---
    for old_name, new_name in rename_map.items():
        if _column_exists("predictions", old_name, "core") and not _column_exists("predictions", new_name, "core"):
            op.alter_column("predictions", old_name, new_column_name=new_name, schema="core")

    # --- handle already-renamed Spanish columns from previous run ---
    rename_spanish = {
        "nitrogeno": "nitrogen",
        "fosforo": "phosphorus",
        "potasio": "potassium",
        "ph_suelo": "ph_soil",
    }
    for old_name, new_name in rename_spanish.items():
        if _column_exists("training_records", old_name, "core") and not _column_exists("training_records", new_name, "core"):
            op.alter_column("training_records", old_name, new_column_name=new_name, schema="core")
        if _column_exists("predictions", old_name, "core") and not _column_exists("predictions", new_name, "core"):
            op.alter_column("predictions", old_name, new_column_name=new_name, schema="core")

    # --- handle already-renamed soil_ph from previous run ---
    for tbl in ("training_records", "predictions"):
        if _column_exists(tbl, "soil_ph", "core") and not _column_exists(tbl, "ph_soil", "core"):
            op.alter_column(tbl, "soil_ph", new_column_name="ph_soil", schema="core")


def downgrade() -> None:
    # rename back to original
    reverse_map = {
        "nitrogen": "N",
        "phosphorus": "P",
        "potassium": "K",
        "ph_soil": "ph",
    }
    for new_name, old_name in reverse_map.items():
        if _column_exists("training_records", new_name, "core"):
            op.alter_column("training_records", new_name, new_column_name=old_name, schema="core")
        if _column_exists("predictions", new_name, "core"):
            op.alter_column("predictions", new_name, new_column_name=old_name, schema="core")

    # drop trained_models
    if _table_exists("trained_models", "core"):
        op.drop_index("ix_core_trained_models_status", schema="core")
        op.drop_index("ix_core_trained_models_user_id", schema="core")
        op.drop_table("trained_models", schema="core")
