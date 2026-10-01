from abc import ABC, abstractmethod

from app.domain.entities.general.training_field import TrainingField


class TrainingFieldRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[TrainingField]: ...