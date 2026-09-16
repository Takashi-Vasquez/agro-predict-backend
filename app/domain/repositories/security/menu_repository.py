from abc import ABC, abstractmethod

from app.domain.entities.security.menu import Menu


class MenuRepository(ABC):
    @abstractmethod
    def get(self, menu_id: int) -> Menu | None: ...

    @abstractmethod
    def get_all(self) -> list[Menu]: ...

    @abstractmethod
    def get_root_menus(self) -> list[Menu]: ...

    @abstractmethod
    def get_children(self, parent_id: int) -> list[Menu]: ...

    @abstractmethod
    def get_menus_with_permissions_for_role_ids(self, role_ids: list[int]) -> list[dict]: ...

    @abstractmethod
    def get_all_with_permissions(self) -> list[dict]: ...
