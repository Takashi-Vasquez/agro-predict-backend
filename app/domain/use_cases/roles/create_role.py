from app.domain.entities import Role
from app.domain.repositories import RoleRepository


class CreateRoleUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    def execute(self, name: str, description: str | None = None) -> Role:
        existing = self.role_repo.get_by_name(name)
        if existing:
            raise ValueError("Ya existe un rol con ese nombre")
        return self.role_repo.create(name=name, description=description)
