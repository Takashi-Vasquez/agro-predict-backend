from abc import ABC, abstractmethod

from app.domain.entities.security.user_role import UserRole


class UserRoleRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> list[UserRole]: ...

    @abstractmethod
    def assign(self, user_id: int, role_id: int) -> UserRole: ...

    @abstractmethod
    def remove_by_user_id(self, user_id: int) -> None: ...
