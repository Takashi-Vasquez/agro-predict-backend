from app.domain.entities import RolePermissionDetail
from app.domain.repositories import RolePermissionRepository


class SyncRolePermissionsUseCase:
    def __init__(self, role_permission_repo: RolePermissionRepository) -> None:
        self.role_permission_repo = role_permission_repo

    def execute(self, role_id: int, assignments: list[tuple[int, int]]) -> list[RolePermissionDetail]:
        role = self.role_permission_repo.get(role_id)
        if not role:
            raise ValueError("Rol no encontrado")
        return self.role_permission_repo.sync_details(role_id, assignments)
