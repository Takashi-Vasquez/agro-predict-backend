from abc import ABC, abstractmethod

from app.domain.entities.security.user import User


class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def list(self, *, offset: int = 0, limit: int = 100) -> list[User]: ...

    @abstractmethod
    def create(self, email: str, hashed_password: str, is_admin: bool) -> User: ...

    @abstractmethod
    def update(self, user: User, **kwargs) -> User: ...

    @abstractmethod
    def delete(self, user: User) -> None: ...
