from app.domain.entities import User
from app.domain.repositories import UserRepository


class ListUsersUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, offset: int = 0, limit: int = 100) -> list[User]:
        return self.user_repo.list(offset=offset, limit=limit)
