from app.domain.entities import RolePermissionDetail
from app.domain.repositories import RolePermissionRepository


class ListRolePermissionsUseCase:
    def __init__(self, role_permission_repo: RolePermissionRepository) -> None:
        self.role_permission_repo = role_permission_repo

    def execute(self, role_id: int) -> list[RolePermissionDetail]:
        return self.role_permission_repo.get_details_by_role_id(role_id)
