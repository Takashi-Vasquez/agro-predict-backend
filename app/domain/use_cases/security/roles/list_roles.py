from app.domain.entities import Role
from app.domain.repositories import RoleRepository


class ListRolesUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    def execute(self, offset: int = 0, limit: int = 100) -> list[Role]:
        return self.role_repo.list(offset=offset, limit=limit)
