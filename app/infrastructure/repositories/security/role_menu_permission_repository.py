from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import RoleMenuPermission
from app.domain.repositories import RoleMenuPermissionRepository
from app.infrastructure.orm.security.role_menu_permission import RoleMenuPermission as RoleMenuPermissionModel


class RoleMenuPermissionRepositoryImpl(RoleMenuPermissionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, rmp_id: int) -> RoleMenuPermission | None:
        orm = self.db.get(RoleMenuPermissionModel, rmp_id)
        return self._to_entity(orm) if orm else None

    def get_by_role_id(self, role_id: int) -> list[RoleMenuPermission]:
        stmt = select(RoleMenuPermissionModel).where(
            RoleMenuPermissionModel.role_id == role_id,
            RoleMenuPermissionModel.status == "ACTIVE",
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_all_by_role_id(self, role_id: int) -> list[RoleMenuPermission]:
        stmt = select(RoleMenuPermissionModel).where(
            RoleMenuPermissionModel.role_id == role_id,
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, role_id: int, menu_id: int, permission_id: int) -> RoleMenuPermission:
        orm = RoleMenuPermissionModel(role_id=role_id, menu_id=menu_id, permission_id=permission_id)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, rmp: RoleMenuPermission) -> None:
        orm = self.db.get(RoleMenuPermissionModel, rmp.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.utcnow()
        self.db.commit()

    def soft_delete(self, rmp_id: int) -> None:
        orm = self.db.get(RoleMenuPermissionModel, rmp_id)
        if orm:
            orm.status = "DELETED"
            orm.deleted_at = datetime.utcnow()
            self.db.commit()

    def bulk_sync(self, role_id: int, assignments: list[tuple[int, int]]) -> list[RoleMenuPermission]:
        existing = self.get_all_by_role_id(role_id)
        existing_map: dict[tuple[int, int], RoleMenuPermissionModel] = {}
        for rmp in existing:
            key = (rmp.menu_id, rmp.permission_id)
            existing_map[key] = rmp

        new_keys = set(assignments)

        for key, rmp_entity in existing_map.items():
            if key in new_keys and rmp_entity.status != "ACTIVE":
                orm = self.db.get(RoleMenuPermissionModel, rmp_entity.id)
                orm.status = "ACTIVE"
                orm.deleted_at = None
            elif key not in new_keys and rmp_entity.status == "ACTIVE":
                orm = self.db.get(RoleMenuPermissionModel, rmp_entity.id)
                orm.status = "DELETED"
                orm.deleted_at = datetime.utcnow()

        for menu_id, permission_id in new_keys:
            if (menu_id, permission_id) not in existing_map:
                orm = RoleMenuPermissionModel(
                    role_id=role_id,
                    menu_id=menu_id,
                    permission_id=permission_id,
                )
                self.db.add(orm)

        self.db.commit()

        return self.get_by_role_id(role_id)

    @staticmethod
    def _to_entity(orm: RoleMenuPermissionModel) -> RoleMenuPermission:
        return RoleMenuPermission(
            id=orm.id,
            role_id=orm.role_id,
            menu_id=orm.menu_id,
            permission_id=orm.permission_id,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
