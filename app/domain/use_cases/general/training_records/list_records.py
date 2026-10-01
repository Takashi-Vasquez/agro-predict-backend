from app.domain.entities.general.training_record import TrainingRecord
from app.domain.repositories.general.training_record_repository import TrainingRecordRepository


class ListTrainingRecordsUseCase:
    def __init__(self, record_repo: TrainingRecordRepository) -> None:
        self.record_repo = record_repo

    def execute(
        self, *, offset: int = 0, limit: int = 100, crop_id: int | None = None
    ) -> list[TrainingRecord]:
        return self.record_repo.list_all(offset=offset, limit=limit, crop_id=crop_id)
