from app.domain.entities import User
from app.domain.repositories import UserRepository


class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, user_id: int, **kwargs) -> User:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        return self.user_repo.update(user, **kwargs)
