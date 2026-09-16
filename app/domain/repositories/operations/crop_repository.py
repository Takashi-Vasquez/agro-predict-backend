from abc import ABC, abstractmethod

from app.domain.entities.operations.crop import Crop


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
