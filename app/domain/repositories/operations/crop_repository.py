from abc import ABC, abstractmethod

from app.domain.entities.operations.crop import Crop


class CropRepository(ABC):
    @abstractmethod
    def get(self, crop_id: int) -> Crop | None: ...

    @abstractmethod
    def list_all(self, *, offset: int = 0, limit: int = 100) -> list[Crop]: ...

    @abstractmethod
    def create(
        self,
        owner_id: int,
        name: str,
        variety_id: int,
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
