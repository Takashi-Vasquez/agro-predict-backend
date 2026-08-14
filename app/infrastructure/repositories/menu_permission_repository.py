from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import MenuPermission, Permission
from app.domain.repositories import MenuPermissionRepository
from app.infrastructure.orm.security.menu_permission import MenuPermission as MenuPermissionModel
from app.infrastructure.orm.security.permission import Permission as PermissionModel


class MenuPermissionRepositoryImpl(MenuPermissionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_menu_id(self, menu_id: int) -> list[MenuPermission]:
        stmt = select(MenuPermissionModel).where(
            MenuPermissionModel.menu_id == menu_id,
            MenuPermissionModel.status != "DELETED",
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_permissions_by_menu_id(self, menu_id: int) -> list[Permission]:
        stmt = (
            select(PermissionModel)
            .join(MenuPermissionModel, MenuPermissionModel.permission_id == PermissionModel.id)
            .where(
                MenuPermissionModel.menu_id == menu_id,
                MenuPermissionModel.status != "DELETED",
                PermissionModel.status != "DELETED",
            )
        )
        return [Permission(id=o.id, code=o.code, name=o.name) for o in self.db.scalars(stmt).all()]

    @staticmethod
    def _to_entity(orm: MenuPermissionModel) -> MenuPermission:
        return MenuPermission(
            id=orm.id,
            menu_id=orm.menu_id,
            permission_id=orm.permission_id,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
