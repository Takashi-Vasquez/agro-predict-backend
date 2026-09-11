from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities import (
    Crop,
    Menu,
    MenuPermission,
    Permission,
    Prediction,
    Profile,
    Role,
    RoleMenuPermission,
    User,
    UserRole,
)


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


class CropRepository(ABC):
    @abstractmethod
    def get(self, crop_id: int) -> Crop | None: ...

    @abstractmethod
    def get_owned(self, owner_id: int, crop_id: int) -> Crop | None: ...

    @abstractmethod
    def list_for_owner(self, owner_id: int, *, offset: int = 0, limit: int = 100) -> list[Crop]: ...

    @abstractmethod
    def create(
        self,
        owner_id: int,
        name: str,
        variety: str,
        category: str,
        cycle: int,
        temperature: str,
        water: str,
        color: str,
    ) -> Crop: ...

    @abstractmethod
    def update(self, crop: Crop, **kwargs) -> Crop: ...

    @abstractmethod
    def delete(self, crop: Crop) -> None: ...


class PredictionRepository(ABC):
    @abstractmethod
    def get(self, prediction_id: int) -> Prediction | None: ...

    @abstractmethod
    def list_for_user(self, user_id: int, *, offset: int = 0, limit: int = 100) -> list[Prediction]: ...

    @abstractmethod
    def create(self, **kwargs) -> Prediction: ...


class ProfileRepository(ABC):
    @abstractmethod
    def get(self, profile_id: int) -> Profile | None: ...

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Profile | None: ...

    @abstractmethod
    def create(self, user_id: int, first_name: str, last_name: str, phone: str | None, age: int | None) -> Profile: ...

    @abstractmethod
    def update(self, profile: Profile, **kwargs) -> Profile: ...


class RoleRepository(ABC):
    @abstractmethod
    def get(self, role_id: int) -> Role | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Role | None: ...

    @abstractmethod
    def list(self, *, offset: int = 0, limit: int = 100) -> list[Role]: ...

    @abstractmethod
    def create(self, name: str, description: str | None) -> Role: ...

    @abstractmethod
    def update(self, role: Role, **kwargs) -> Role: ...

    @abstractmethod
    def delete(self, role: Role) -> None: ...


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


class PermissionRepository(ABC):
    @abstractmethod
    def get(self, permission_id: int) -> Permission | None: ...

    @abstractmethod
    def get_by_code(self, code: str) -> Permission | None: ...

    @abstractmethod
    def get_all(self) -> list[Permission]: ...


class MenuPermissionRepository(ABC):
    @abstractmethod
    def get_by_menu_id(self, menu_id: int) -> list[MenuPermission]: ...

    @abstractmethod
    def get_permissions_by_menu_id(self, menu_id: int) -> list[Permission]: ...


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


class UserRoleRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> list[UserRole]: ...

    @abstractmethod
    def assign(self, user_id: int, role_id: int) -> UserRole: ...

    @abstractmethod
    def remove_by_user_id(self, user_id: int) -> None: ...
