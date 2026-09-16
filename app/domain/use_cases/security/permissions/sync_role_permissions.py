from app.domain.entities import RoleMenuPermission
from app.domain.repositories import RoleMenuPermissionRepository, RoleRepository


class SyncRolePermissionsUseCase:
    def __init__(
        self,
        rmp_repo: RoleMenuPermissionRepository,
        role_repo: RoleRepository,
    ) -> None:
        self.rmp_repo = rmp_repo
        self.role_repo = role_repo

    def execute(self, role_id: int, assignments: list[tuple[int, int]]) -> list[RoleMenuPermission]:
        role = self.role_repo.get(role_id)
        if not role:
            raise ValueError("Rol no encontrado")
        return self.rmp_repo.bulk_sync(role_id, assignments)
