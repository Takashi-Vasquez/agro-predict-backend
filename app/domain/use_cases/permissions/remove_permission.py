from app.domain.repositories import RoleMenuPermissionRepository


class RemovePermissionUseCase:
    def __init__(self, rmp_repo: RoleMenuPermissionRepository) -> None:
        self.rmp_repo = rmp_repo

    def execute(self, rmp_id: int) -> None:
        rmp = self.rmp_repo.get(rmp_id)
        if not rmp:
            raise ValueError("Permiso no encontrado")
        self.rmp_repo.delete(rmp)
