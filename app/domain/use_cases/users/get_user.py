from app.domain.entities import User
from app.domain.repositories import UserRepository


class GetUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, user_id: int) -> User | None:
        return self.user_repo.get(user_id)
