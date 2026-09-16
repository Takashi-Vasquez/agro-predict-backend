from app.domain.repositories import UserRepository


class DeleteUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, user_id: int) -> None:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        self.user_repo.delete(user)
