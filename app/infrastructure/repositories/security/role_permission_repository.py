from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import RolePermission, RolePermissionDetail
from app.domain.repositories import RolePermissionRepository
from app.infrastructure.repositories.base import apply_company_filter, get_company_id_or_none
from app.infrastructure.orm.security.role_permissions import RolePermission as RolePermissionModel
from app.infrastructure.orm.security.role_permission_details import RolePermissionDetail as RolePermissionDetailModel
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel


class RolePermissionRepositoryImpl(RolePermissionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, role_id: int) -> RolePermission | None:
        stmt = select(RolePermissionModel).where(
            RolePermissionModel.id == role_id,
            RolePermissionModel.status != "DELETED",
        )
        stmt = apply_company_filter(stmt, RolePermissionModel)
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_many(self, role_ids: list[int]) -> list[RolePermission]:
        if not role_ids:
            return []
        stmt = select(RolePermissionModel).where(
            RolePermissionModel.id.in_(role_ids),
            RolePermissionModel.status != "DELETED",
        )
        stmt = apply_company_filter(stmt, RolePermissionModel)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_roles_for_user(self, user_id: int) -> list[RolePermission]:
        stmt = (
            select(RolePermissionModel)
            .join(UserRoleModel, UserRoleModel.role_id == RolePermissionModel.id)
            .where(
                UserRoleModel.user_id == user_id,
                UserRoleModel.status == "ACTIVE",
                RolePermissionModel.status != "DELETED",
            )
            .order_by(RolePermissionModel.id)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_by_name(self, name: str) -> RolePermission | None:
        stmt = select(RolePermissionModel).where(
            RolePermissionModel.name == name,
            RolePermissionModel.status.in_(["ACTIVE", "INACTIVE"]),
        )
        stmt = apply_company_filter(stmt, RolePermissionModel)
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list(self, *, offset: int = 0, limit: int = 1000) -> list[RolePermission]:
        stmt = (
            select(RolePermissionModel)
            .where(RolePermissionModel.status != "DELETED")
            .order_by(RolePermissionModel.name)
            .offset(offset)
            .limit(limit)
        )
        stmt = apply_company_filter(stmt, RolePermissionModel)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, name: str, company_id: int | None, status: str = "ACTIVE") -> RolePermission:
        orm = RolePermissionModel(
            name=name,
            company_id=company_id if company_id is not None else get_company_id_or_none(),
            status=status,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, role: RolePermission, **kwargs) -> RolePermission:
        orm = self.db.get(RolePermissionModel, role.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, role: RolePermission) -> None:
        orm = self.db.get(RolePermissionModel, role.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.utcnow()
        details_stmt = select(RolePermissionDetailModel).where(
            RolePermissionDetailModel.role_permissions_id == role.id,
            RolePermissionDetailModel.status == "ACTIVE",
        )
        for d in self.db.scalars(details_stmt).all():
            d.status = "DELETED"
            d.deleted_at = datetime.utcnow()
        self.db.commit()

    def get_details_by_role_id(self, role_id: int) -> list[RolePermissionDetail]:
        stmt = select(RolePermissionDetailModel).where(
            RolePermissionDetailModel.role_permissions_id == role_id,
            RolePermissionDetailModel.status == "ACTIVE",
        )
        return [self._detail_to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_all_details_by_role_id(self, role_id: int) -> list[RolePermissionDetail]:
        stmt = select(RolePermissionDetailModel).where(
            RolePermissionDetailModel.role_permissions_id == role_id,
        )
        return [self._detail_to_entity(o) for o in self.db.scalars(stmt).all()]

    def sync_details(self, role_id: int, assignments: list[tuple[int, int]]) -> list[RolePermissionDetail]:
        existing = self.get_all_details_by_role_id(role_id)
        existing_map: dict[tuple[int, int], RolePermissionDetail] = {}
        for d in existing:
            key = (d.menu_id, d.permission_id)
            existing_map[key] = d

        new_keys = set(assignments)

        for key, detail_entity in existing_map.items():
            if key in new_keys and detail_entity.status != "ACTIVE":
                orm = self.db.get(RolePermissionDetailModel, detail_entity.id)
                orm.status = "ACTIVE"
                orm.deleted_at = None
            elif key not in new_keys and detail_entity.status == "ACTIVE":
                orm = self.db.get(RolePermissionDetailModel, detail_entity.id)
                orm.status = "DELETED"
                orm.deleted_at = datetime.utcnow()

        for menu_id, permission_id in new_keys:
            if (menu_id, permission_id) not in existing_map:
                orm = RolePermissionDetailModel(
                    role_permissions_id=role_id,
                    menu_id=menu_id,
                    permission_id=permission_id,
                )
                self.db.add(orm)

        self.db.commit()
        return self.get_details_by_role_id(role_id)

    @staticmethod
    def _to_entity(orm: RolePermissionModel) -> RolePermission:
        return RolePermission(
            id=orm.id,
            name=orm.name,
            company_id=orm.company_id,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def _detail_to_entity(orm: RolePermissionDetailModel) -> RolePermissionDetail:
        return RolePermissionDetail(
            id=orm.id,
            role_permissions_id=orm.role_permissions_id,
            menu_id=orm.menu_id,
            permission_id=orm.permission_id,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
