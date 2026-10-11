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
            .order_by(PermissionModel.id)
        )
        return [Permission(id=o.id, code=o.code, name=o.name) for o in self.db.scalars(stmt).all()]

    def get_permissions_by_menu_ids(self, menu_ids: list[int]) -> dict[int, list[Permission]]:
        if not menu_ids:
            return {}

        stmt = (
            select(MenuPermissionModel.menu_id, PermissionModel)
            .join(MenuPermissionModel, MenuPermissionModel.permission_id == PermissionModel.id)
            .where(
                MenuPermissionModel.menu_id.in_(menu_ids),
                MenuPermissionModel.status != "DELETED",
                PermissionModel.status != "DELETED",
            )
            .order_by(MenuPermissionModel.menu_id, PermissionModel.id)
        )

        result: dict[int, list[Permission]] = {}
        for menu_id, orm in self.db.execute(stmt).all():
            result.setdefault(menu_id, []).append(
                Permission(id=orm.id, code=orm.code, name=orm.name)
            )
        return result

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
