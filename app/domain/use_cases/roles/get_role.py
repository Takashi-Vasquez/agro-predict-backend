from app.domain.entities import Role
from app.domain.repositories import RoleRepository


class GetRoleUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    def execute(self, role_id: int) -> Role | None:
        return self.role_repo.get(role_id)
