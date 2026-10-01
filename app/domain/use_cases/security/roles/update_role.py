from app.domain.entities import Role
from app.domain.repositories import RoleRepository


class UpdateRoleUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    def execute(self, role_id: int, **kwargs) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise ValueError("Rol no encontrado")
        existing = self.role_repo.get_by_name(kwargs["name"])

        if existing and existing.id != role_id:
            raise ValueError("Ya existe un rol con ese nombre")
        return self.role_repo.update(role, **kwargs)
