from abc import ABC, abstractmethod

from app.domain.entities.security.role_menu_permission import RoleMenuPermission


class RoleMenuPermissionRepository(ABC):
    @abstractmethod
    def get(self, rmp_id: int) -> RoleMenuPermission | None: ...

    @abstractmethod
    def get_by_role_id(self, role_id: int) -> list[RoleMenuPermission]: ...

    @abstractmethod
    def get_all_by_role_id(self, role_id: int) -> list[RoleMenuPermission]: ...

    @abstractmethod
    def create(self, role_id: int, menu_id: int, permission_id: int) -> RoleMenuPermission: ...

    @abstractmethod
    def delete(self, rmp: RoleMenuPermission) -> None: ...

    @abstractmethod
    def soft_delete(self, rmp_id: int) -> None: ...

    @abstractmethod
    def bulk_sync(self, role_id: int, assignments: list[tuple[int, int]]) -> list[RoleMenuPermission]: ...
