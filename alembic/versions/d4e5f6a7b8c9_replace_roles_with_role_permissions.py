"""replace roles with role_permissions

Creates security.role_permissions (the role, holding name + company_id) and
security.role_permission_details (menu x permission grants), migrates data from
the old security.roles and security.role_menu_permissions tables preserving ids,
repoints user_roles.role_id FK to role_permissions, then drops the old tables.

Revision ID: d4e5f6a7b8c9
Revises: b7c9d1e3f5a2
Create Date: 2026-10-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'b7c9d1e3f5a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create role_permissions (the role)
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('core.company.id'), nullable=True, index=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        schema='security',
    )

    # 2. Create role_permission_details (menu x permission)
    op.create_table(
        'role_permission_details',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('role_permissions_id', sa.Integer(), sa.ForeignKey('security.role_permissions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('menu_id', sa.Integer(), sa.ForeignKey('security.menus.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('security.permissions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('role_permissions_id', 'menu_id', 'permission_id', name='uq_role_permission_detail'),
        schema='security',
    )

    # 3. Migrate roles -> role_permissions preserving ids (skip description)
    op.execute("""
        INSERT INTO security.role_permissions (id, name, company_id, status, created_at, updated_at, deleted_at)
        SELECT id, name, company_id, status, created_at, updated_at, deleted_at
        FROM security.roles
    """)

    # Keep the sequence in sync after explicit id inserts
    op.execute("""
        SELECT setval('security.role_permissions_id_seq', (SELECT COALESCE(MAX(id), 1) FROM security.role_permissions))
    """)

    # 4. Repoint user_roles.role_id FK from roles to role_permissions
    op.execute("ALTER TABLE security.user_roles DROP CONSTRAINT user_roles_role_id_fkey")
    op.execute("""
        ALTER TABLE security.user_roles
        ADD CONSTRAINT user_roles_role_id_fkey
        FOREIGN KEY (role_id) REFERENCES security.role_permissions(id) ON DELETE CASCADE
    """)

    # 5. Migrate role_menu_permissions -> role_permission_details (empty today, kept for safety)
    op.execute("""
        INSERT INTO security.role_permission_details (role_permissions_id, menu_id, permission_id, status, created_at, updated_at, deleted_at)
        SELECT role_id, menu_id, permission_id, status, created_at, updated_at, deleted_at
        FROM security.role_menu_permissions
    """)

    # 6. Drop old tables
    op.drop_table('role_menu_permissions', schema='security')
    op.drop_table('roles', schema='security')


def downgrade() -> None:
    # Recreate roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('core.company.id'), nullable=True, index=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        schema='security',
    )

    # Recreate role_menu_permissions
    op.create_table(
        'role_menu_permissions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('security.roles.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('menu_id', sa.Integer(), sa.ForeignKey('security.menus.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('security.permissions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('role_id', 'menu_id', 'permission_id', name='uq_role_menu_permission'),
        schema='security',
    )

    # Copy back preserving ids
    op.execute("""
        INSERT INTO security.roles (id, name, company_id, status, created_at, updated_at, deleted_at)
        SELECT id, name, company_id, status, created_at, updated_at, deleted_at
        FROM security.role_permissions
    """)
    op.execute("""
        SELECT setval('security.roles_id_seq', (SELECT COALESCE(MAX(id), 1) FROM security.roles))
    """)
    op.execute("""
        INSERT INTO security.role_menu_permissions (role_id, menu_id, permission_id, status, created_at, updated_at, deleted_at)
        SELECT role_permissions_id, menu_id, permission_id, status, created_at, updated_at, deleted_at
        FROM security.role_permission_details
    """)

    # Repoint user_roles FK back to roles
    op.execute("ALTER TABLE security.user_roles DROP CONSTRAINT user_roles_role_id_fkey")
    op.execute("""
        ALTER TABLE security.user_roles
        ADD CONSTRAINT user_roles_role_id_fkey
        FOREIGN KEY (role_id) REFERENCES security.roles(id) ON DELETE CASCADE
    """)

    # Drop new tables
    op.drop_table('role_permission_details', schema='security')
    op.drop_table('role_permissions', schema='security')
