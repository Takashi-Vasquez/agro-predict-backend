from app.domain.repositories import RoleRepository


class DeleteRoleUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    def execute(self, role_id: int) -> None:
        role = self.role_repo.get(role_id)
        if not role:
            raise ValueError("Rol no encontrado")
        self.role_repo.delete(role)
