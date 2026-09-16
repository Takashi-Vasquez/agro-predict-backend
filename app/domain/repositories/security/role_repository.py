from abc import ABC, abstractmethod

from app.domain.entities.security.role import Role


class RoleRepository(ABC):
    @abstractmethod
    def get(self, role_id: int) -> Role | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Role | None: ...

    @abstractmethod
    def list(self, *, offset: int = 0, limit: int = 100) -> list[Role]: ...

    @abstractmethod
    def create(self, name: str, description: str | None, status: str = "ACTIVE") -> Role: ...

    @abstractmethod
    def update(self, role: Role, **kwargs) -> Role: ...

    @abstractmethod
    def delete(self, role: Role) -> None: ...
