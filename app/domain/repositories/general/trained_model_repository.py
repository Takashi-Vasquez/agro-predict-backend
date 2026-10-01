from abc import ABC, abstractmethod

from app.domain.entities.general.trained_model import TrainedModel


class TrainedModelRepository(ABC):
    @abstractmethod
    def get(self, model_id: int) -> TrainedModel | None: ...

    @abstractmethod
    def list_all(self) -> list[TrainedModel]: ...

    @abstractmethod
    def get_selected(self) -> TrainedModel | None: ...

    @abstractmethod
    def create(self, **kwargs) -> TrainedModel: ...

    @abstractmethod
    def update(self, model_id: int, **kwargs) -> TrainedModel | None: ...

    @abstractmethod
    def set_selected(self, model_id: int) -> None: ...

    @abstractmethod
    def archive_others(self) -> None: ...
