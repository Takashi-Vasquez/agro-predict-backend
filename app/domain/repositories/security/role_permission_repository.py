from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.security.role_permission_details import RolePermissionDetail
from app.domain.entities.security.role_permissions import RolePermission


class RolePermissionRepository(ABC):
    @abstractmethod
    def get(self, role_id: int) -> RolePermission | None: ...

    @abstractmethod
    def get_many(self, role_ids: list[int]) -> list[RolePermission]: ...

    @abstractmethod
    def get_roles_for_user(self, user_id: int) -> list[RolePermission]: ...

    @abstractmethod
    def get_by_name(self, name: str) -> RolePermission | None: ...

    @abstractmethod
    def list(self, *, offset: int = 0, limit: int = 1000) -> list[RolePermission]: ...

    @abstractmethod
    def create(self, name: str, company_id: int | None, status: str = "ACTIVE") -> RolePermission: ...

    @abstractmethod
    def update(self, role: RolePermission, **kwargs) -> RolePermission: ...

    @abstractmethod
    def delete(self, role: RolePermission) -> None: ...

    @abstractmethod
    def get_details_by_role_id(self, role_id: int) -> list[RolePermissionDetail]: ...

    @abstractmethod
    def get_all_details_by_role_id(self, role_id: int) -> list[RolePermissionDetail]: ...

    @abstractmethod
    def sync_details(self, role_id: int, assignments: list[tuple[int, int]]) -> list[RolePermissionDetail]: ...
