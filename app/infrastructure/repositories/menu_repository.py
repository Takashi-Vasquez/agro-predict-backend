from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Menu
from app.domain.repositories import MenuRepository
from app.infrastructure.orm.security.menu import Menu as MenuModel
from app.infrastructure.orm.security.role_menu_permission import RoleMenuPermission as RMPModel
from app.infrastructure.orm.security.permission import Permission as PermissionModel


class MenuRepositoryImpl(MenuRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, menu_id: int) -> Menu | None:
        stmt = select(MenuModel).where(
            MenuModel.id == menu_id,
            MenuModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_all(self) -> list[Menu]:
        stmt = select(MenuModel).where(MenuModel.status != "DELETED").order_by(MenuModel.order_index)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_root_menus(self) -> list[Menu]:
        stmt = select(MenuModel).where(
            MenuModel.parent_id.is_(None),
            MenuModel.status != "DELETED",
        ).order_by(MenuModel.order_index)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_children(self, parent_id: int) -> list[Menu]:
        stmt = select(MenuModel).where(
            MenuModel.parent_id == parent_id,
            MenuModel.status != "DELETED",
        ).order_by(MenuModel.order_index)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_menus_with_permissions_for_role_ids(self, role_ids: list[int]) -> list[dict]:
        if not role_ids:
            return []

        stmt = (
            select(
                RMPModel.menu_id,
                PermissionModel.code,
            )
            .join(PermissionModel, RMPModel.permission_id == PermissionModel.id)
            .where(
                RMPModel.role_id.in_(role_ids),
                RMPModel.status == "ACTIVE",
            )
        )
        rows = self.db.execute(stmt).all()

        menu_perms: dict[int, list[str]] = {}
        for menu_id, perm_code in rows:
            if menu_id not in menu_perms:
                menu_perms[menu_id] = []
            if perm_code not in menu_perms[menu_id]:
                menu_perms[menu_id].append(perm_code)

        return [{"menu_id": mid, "permissions": perms} for mid, perms in menu_perms.items()]

    def get_all_with_permissions(self) -> list[dict]:
        stmt = (
            select(
                RMPModel.menu_id,
                PermissionModel.code,
            )
            .join(PermissionModel, RMPModel.permission_id == PermissionModel.id)
            .where(RMPModel.status == "ACTIVE")
        )
        rows = self.db.execute(stmt).all()

        menu_perms: dict[int, list[str]] = {}
        for menu_id, perm_code in rows:
            if menu_id not in menu_perms:
                menu_perms[menu_id] = []
            if perm_code not in menu_perms[menu_id]:
                menu_perms[menu_id].append(perm_code)

        return [{"menu_id": mid, "permissions": perms} for mid, perms in menu_perms.items()]

    @staticmethod
    def _to_entity(orm: MenuModel) -> Menu:
        return Menu(
            id=orm.id,
            parent_id=orm.parent_id,
            name=orm.name,
            code=orm.code,
            icon=orm.icon,
            route=orm.route,
            order_index=orm.order_index,
            badge=orm.badge,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
