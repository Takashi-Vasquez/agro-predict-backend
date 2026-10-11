from abc import ABC, abstractmethod

from app.domain.entities.security.user import User


class AuthRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def get(self, user_id: int) -> User | None: ...