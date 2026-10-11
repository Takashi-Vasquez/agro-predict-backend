from abc import ABC, abstractmethod

from app.domain.entities.security.menu_permission import MenuPermission
from app.domain.entities.security.permission import Permission


class MenuPermissionRepository(ABC):
    @abstractmethod
    def get_by_menu_id(self, menu_id: int) -> list[MenuPermission]: ...

    @abstractmethod
    def get_permissions_by_menu_id(self, menu_id: int) -> list[Permission]: ...

    @abstractmethod
    def get_permissions_by_menu_ids(self, menu_ids: list[int]) -> dict[int, list[Permission]]: ...
