"""create_varieties_and_update_crops

Revision ID: i1j2k3l4m5n6
Revises: h3i4j5k6l7m8
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'i1j2k3l4m5n6'
down_revision: Union[str, None] = 'h3i4j5k6l7m8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear tabla operations.varieties
    op.create_table(
        'varieties',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('status', sa.String(50), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        schema='operations',
    )

    # 2. Insertar variedades existentes
    op.execute("""
        INSERT INTO operations.varieties (name, status) VALUES
        ('Hass', 'ACTIVE'),
        ('Biloxi', 'ACTIVE'),
        ('Fuerte', 'ACTIVE'),
        ('Zutano', 'ACTIVE'),
        ('Hass 816', 'ACTIVE'),
        ('Lula', 'ACTIVE'),
        ('Eda Derezo', 'ACTIVE')
    """)

    # 3. Agregar columna variety_id (nullable temporalmente)
    op.add_column('crops', sa.Column('variety_id', sa.Integer(), nullable=True), schema='operations')

    # 4. Migrar datos existentes: variety string → variety_id
    op.execute("""
        UPDATE operations.crops SET variety_id = (
            SELECT v.id FROM operations.varieties v WHERE v.name = operations.crops.variety
        )
    """)

    # 5. Hacer variety_id NOT NULL
    op.alter_column('crops', 'variety_id', nullable=False, schema='operations')

    # 6. Agregar FK
    op.create_foreign_key(
        'fk_crops_variety_id',
        'crops', 'varieties',
        ['variety_id'], ['id'],
        source_schema='operations',
        referent_schema='operations',
    )

    # 7. Eliminar columna variety (string viejo)
    op.drop_column('crops', 'variety', schema='operations')


def downgrade() -> None:
    # 1. Restaurar columna variety como string
    op.add_column('crops', sa.Column('variety', sa.String(100), nullable=True), schema='operations')

    # 2. Copiar datos de variety_id de vuelta a variety
    op.execute("""
        UPDATE operations.crops SET variety = (
            SELECT v.name FROM operations.varieties v WHERE v.id = operations.crops.variety_id
        )
    """)

    # 3. Hacer variety NOT NULL
    op.alter_column('crops', 'variety', nullable=False, schema='operations')

    # 4. Eliminar FK y columna variety_id
    op.drop_constraint('fk_crops_variety_id', 'crops', schema='operations')
    op.drop_column('crops', 'variety_id', schema='operations')

    # 5. Eliminar tabla varieties
    op.drop_table('varieties', schema='operations')
