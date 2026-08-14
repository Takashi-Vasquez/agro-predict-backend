from app.domain.entities import User
from app.domain.repositories import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, email: str, hashed_password: str, is_admin: bool = False) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Ya existe un usuario con ese email")
        return self.user_repo.create(
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin,
        )
