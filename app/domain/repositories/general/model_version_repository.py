from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.general.model_version import ModelVersion


class ModelVersionRepository(ABC):
    @abstractmethod
    def get(self, version_id: int) -> Optional[ModelVersion]: ...

    @abstractmethod
    def list_versions(
        self, model_name: str, offset: int = 0, limit: int = 100
    ) -> list[ModelVersion]: ...

    @abstractmethod
    def get_production(self, model_name: str) -> Optional[ModelVersion]: ...

    @abstractmethod
    def get_latest_candidate(self, model_name: str) -> Optional[ModelVersion]: ...