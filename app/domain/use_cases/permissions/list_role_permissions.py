from app.domain.entities import RoleMenuPermission
from app.domain.repositories import RoleMenuPermissionRepository


class ListRolePermissionsUseCase:
    def __init__(self, rmp_repo: RoleMenuPermissionRepository) -> None:
        self.rmp_repo = rmp_repo

    def execute(self, role_id: int) -> list[RoleMenuPermission]:
        return self.rmp_repo.get_by_role_id(role_id)
