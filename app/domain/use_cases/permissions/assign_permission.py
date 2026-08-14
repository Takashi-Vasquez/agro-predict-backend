from app.domain.entities import RoleMenuPermission
from app.domain.repositories import (
    MenuRepository,
    PermissionRepository,
    RoleMenuPermissionRepository,
    RoleRepository,
)


class AssignPermissionUseCase:
    def __init__(
        self,
        rmp_repo: RoleMenuPermissionRepository,
        role_repo: RoleRepository,
        menu_repo: MenuRepository,
        perm_repo: PermissionRepository,
    ) -> None:
        self.rmp_repo = rmp_repo
        self.role_repo = role_repo
        self.menu_repo = menu_repo
        self.perm_repo = perm_repo

    def execute(self, role_id: int, menu_id: int, permission_id: int) -> RoleMenuPermission:
        if not self.role_repo.get(role_id):
            raise ValueError("Rol no encontrado")
        if not self.menu_repo.get(menu_id):
            raise ValueError("Menu no encontrado")
        if not self.perm_repo.get(permission_id):
            raise ValueError("Permiso no encontrado")
        return self.rmp_repo.create(
            role_id=role_id,
            menu_id=menu_id,
            permission_id=permission_id,
        )
