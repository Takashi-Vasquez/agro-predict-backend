from abc import ABC, abstractmethod

from app.domain.entities.general.training_record import TrainingRecord
from app.presentation.schemas.general.training_records.training_record import TrainingRecordModelVersion


class TrainingRecordRepository(ABC):
    @abstractmethod
    def get(self, record_id: int) -> TrainingRecord | None: ...

    @abstractmethod
    def list_all(
        self, *, offset: int = 0, limit: int = 100, crop_id: int | None = None
    ) -> list[TrainingRecord]: ...

    @abstractmethod
    def create(self, **kwargs) -> TrainingRecord: ...

    @abstractmethod
    def delete(self, record: TrainingRecord) -> None: ...

    @abstractmethod
    def get_model_version_stats(self) -> TrainingRecordModelVersion: ...

    @abstractmethod
    def count_all(self) -> int: ...

    @abstractmethod
    def count_by_crop(self) -> int: ...

    @abstractmethod
    def count_by_campaign(self) -> int: ...

    @abstractmethod
    def validate_is_all_trained(self) -> bool: ...

    @abstractmethod
    def create_batch(self, records: list[dict]) -> list[TrainingRecord]: ...
