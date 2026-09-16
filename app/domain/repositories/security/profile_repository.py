from abc import ABC, abstractmethod

from app.domain.entities.security.profile import Profile


class ProfileRepository(ABC):
    @abstractmethod
    def get(self, profile_id: int) -> Profile | None: ...

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Profile | None: ...

    @abstractmethod
    def create(self, user_id: int, first_name: str, last_name: str, phone: str | None, age: int | None) -> Profile: ...

    @abstractmethod
    def update(self, profile: Profile, **kwargs) -> Profile: ...
