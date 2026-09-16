from abc import ABC, abstractmethod

from app.domain.entities.security.permission import Permission


class PermissionRepository(ABC):
    @abstractmethod
    def get(self, permission_id: int) -> Permission | None: ...

    @abstractmethod
    def get_by_code(self, code: str) -> Permission | None: ...

    @abstractmethod
    def get_all(self) -> list[Permission]: ...
