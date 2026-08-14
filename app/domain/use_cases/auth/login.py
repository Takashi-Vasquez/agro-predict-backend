from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.infrastructure.config.security import create_access_token, verify_password


class LoginUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, email: str, password: str) -> tuple[User, str]:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Email o contrasena incorrectos")
        if user.status != "ACTIVE":
            raise ValueError("Usuario inactivo")
        token = create_access_token(subject=user.id)
        return user, token
