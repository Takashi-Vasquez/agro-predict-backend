from abc import ABC, abstractmethod

from app.domain.entities.general.prediction import Prediction


class PredictionRepository(ABC):
    @abstractmethod
    def get(self, prediction_id: int) -> Prediction | None: ...

    @abstractmethod
    def list_all(self, *, offset: int = 0, limit: int = 100) -> list[Prediction]: ...

    @abstractmethod
    def create(self, **kwargs) -> Prediction: ...
