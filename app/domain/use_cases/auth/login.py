from app.domain.entities import User
from app.domain.repositories import AuthRepository
from app.infrastructure.config.security import verify_password
from app.infrastructure.config.security import create_access_token


class LoginUseCase:
    def __init__(self, auth_repo: AuthRepository) -> None:
        self.auth_repo = auth_repo

    def execute(self, email: str, password: str) -> tuple[User, str]:
        user = self.auth_repo.get_by_email(email)
        if not user or user.status != "ACTIVE":
            raise ValueError("Email o contrasena incorrectos")
        if not self.auth_repo.verify_password(password, user.hashed_password):
            raise ValueError("Email o contrasena incorrectos")
        token = self.auth_repo.create_access_token(subject=user.id)
        return user, token
