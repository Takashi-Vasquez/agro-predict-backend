from app.domain.entities import Role
from app.domain.repositories import RoleRepository


class UpdateRoleUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    def execute(self, role_id: int, **kwargs) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise ValueError("Rol no encontrado")
        return self.role_repo.update(role, **kwargs)
