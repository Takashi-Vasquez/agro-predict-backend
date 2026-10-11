"""add company_id FK to 7 tables

Revision ID: fc6798867a4d
Revises: c5a2ce4d1fe9
Create Date: 2026-10-07 22:57:38.864513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc6798867a4d'
down_revision: Union[str, None] = 'c5a2ce4d1fe9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('campaigns', sa.Column('company_id', sa.Integer(), nullable=True), schema='core')
    op.create_index('ix_core_campaigns_company_id', 'campaigns', ['company_id'], unique=False, schema='core')
    op.create_foreign_key('fk_campaigns_company', 'campaigns', 'company', ['company_id'], ['id'], source_schema='core', referent_schema='core')

    op.add_column('model_version', sa.Column('company_id', sa.Integer(), nullable=True), schema='core')
    op.create_index('ix_core_model_version_company_id', 'model_version', ['company_id'], unique=False, schema='core')
    op.create_foreign_key('fk_model_version_company', 'model_version', 'company', ['company_id'], ['id'], source_schema='core', referent_schema='core')

    op.add_column('training_fields', sa.Column('company_id', sa.Integer(), nullable=True), schema='core')
    op.create_index('ix_core_training_fields_company_id', 'training_fields', ['company_id'], unique=False, schema='core')
    op.create_foreign_key('fk_training_fields_company', 'training_fields', 'company', ['company_id'], ['id'], source_schema='core', referent_schema='core')

    op.add_column('training_records', sa.Column('company_id', sa.Integer(), nullable=True), schema='core')
    op.create_index('ix_core_training_records_company_id', 'training_records', ['company_id'], unique=False, schema='core')
    op.create_foreign_key('fk_training_records_company', 'training_records', 'company', ['company_id'], ['id'], source_schema='core', referent_schema='core')

    op.add_column('crops', sa.Column('company_id', sa.Integer(), nullable=True), schema='operations')
    op.create_index('ix_operations_crops_company_id', 'crops', ['company_id'], unique=False, schema='operations')
    op.create_foreign_key('fk_crops_company', 'crops', 'company', ['company_id'], ['id'], source_schema='operations', referent_schema='core')

    op.add_column('roles', sa.Column('company_id', sa.Integer(), nullable=True), schema='security')
    op.create_index('ix_security_roles_company_id', 'roles', ['company_id'], unique=False, schema='security')
    op.create_foreign_key('fk_roles_company', 'roles', 'company', ['company_id'], ['id'], source_schema='security', referent_schema='core')

    op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True), schema='security')
    op.create_index('ix_security_users_company_id', 'users', ['company_id'], unique=False, schema='security')
    op.create_foreign_key('fk_users_company', 'users', 'company', ['company_id'], ['id'], source_schema='security', referent_schema='core')

    # Backfill: existing rows get the default company HASSPERU
    op.execute("""
        UPDATE security.users SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)
    op.execute("""
        UPDATE security.roles SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)
    op.execute("""
        UPDATE operations.crops SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)
    op.execute("""
        UPDATE core.campaigns SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)
    op.execute("""
        UPDATE core.training_records SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)
    op.execute("""
        UPDATE core.training_fields SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)
    op.execute("""
        UPDATE core.model_version SET company_id = (SELECT id FROM core.company WHERE code = 'HASSPERU')
        WHERE company_id IS NULL
    """)


def downgrade() -> None:
    op.drop_constraint('fk_users_company', 'users', schema='security', type_='foreignkey')
    op.drop_index('ix_security_users_company_id', table_name='users', schema='security')
    op.drop_column('users', 'company_id', schema='security')

    op.drop_constraint('fk_roles_company', 'roles', schema='security', type_='foreignkey')
    op.drop_index('ix_security_roles_company_id', table_name='roles', schema='security')
    op.drop_column('roles', 'company_id', schema='security')

    op.drop_constraint('fk_crops_company', 'crops', schema='operations', type_='foreignkey')
    op.drop_index('ix_operations_crops_company_id', table_name='crops', schema='operations')
    op.drop_column('crops', 'company_id', schema='operations')

    op.drop_constraint('fk_training_records_company', 'training_records', schema='core', type_='foreignkey')
    op.drop_index('ix_core_training_records_company_id', table_name='training_records', schema='core')
    op.drop_column('training_records', 'company_id', schema='core')

    op.drop_constraint('fk_training_fields_company', 'training_fields', schema='core', type_='foreignkey')
    op.drop_index('ix_core_training_fields_company_id', table_name='training_fields', schema='core')
    op.drop_column('training_fields', 'company_id', schema='core')

    op.drop_constraint('fk_model_version_company', 'model_version', schema='core', type_='foreignkey')
    op.drop_index('ix_core_model_version_company_id', table_name='model_version', schema='core')
    op.drop_column('model_version', 'company_id', schema='core')

    op.drop_constraint('fk_campaigns_company', 'campaigns', schema='core', type_='foreignkey')
    op.drop_index('ix_core_campaigns_company_id', table_name='campaigns', schema='core')
    op.drop_column('campaigns', 'company_id', schema='core')
