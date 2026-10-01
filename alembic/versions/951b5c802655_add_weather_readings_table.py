"""add weather_readings and drop old weather

Revision ID: 951b5c802655
Revises: e883636f72b9
Create Date: 2026-09-18 03:15:58.166501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '951b5c802655'
down_revision: Union[str, None] = 'e883636f72b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'weather_readings',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('crop_id', sa.Integer, sa.ForeignKey('operations.crops.id'), nullable=True),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('weather_code', sa.Integer, nullable=False),
        sa.Column('temperature', sa.Float, nullable=False),
        sa.Column('temperature_max', sa.Float, nullable=False),
        sa.Column('temperature_min', sa.Float, nullable=False),
        sa.Column('apparent_temperature', sa.Float, nullable=False),
        sa.Column('humidity', sa.Integer, nullable=False),
        sa.Column('precipitation', sa.Float, nullable=False),
        sa.Column('precipitation_probability', sa.Integer, nullable=False),
        sa.Column('wind_speed', sa.Float, nullable=False),
        sa.Column('wind_direction_degrees', sa.Float, nullable=False),
        sa.Column('pressure', sa.Float, nullable=False),
        sa.Column('uv_index', sa.Float, nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), server_default=sa.text("'ACTIVE'::character varying"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        schema='monitoring',
    )

    op.execute("DROP TABLE IF EXISTS monitoring.weather")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS monitoring.weather_readings")

    op.create_table(
        'weather',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('crop_id', sa.Integer, sa.ForeignKey('operations.crops.id'), nullable=True),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('temperature', sa.Float, nullable=False),
        sa.Column('humidity', sa.Float, nullable=False),
        sa.Column('wind_speed', sa.Float, nullable=False),
        sa.Column('wind_direction', sa.String(50), nullable=True),
        sa.Column('precipitation', sa.Float, nullable=False),
        sa.Column('pressure', sa.Float, nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), server_default=sa.text("'ACTIVE'::character varying"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        schema='monitoring',
    )
    op.create_index('ix_monitoring_weather_id', 'weather', ['id'], schema='monitoring')
