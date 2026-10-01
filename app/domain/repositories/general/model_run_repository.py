from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.general.model_run import ModelRun


class ModelRunRepository(ABC):
    @abstractmethod
    def list_runs(
        self, offset: int = 0, limit: int = 100
    ) -> list[ModelRun]: ...