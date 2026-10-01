from app.domain.entities.general.training_record import TrainingRecord
from app.domain.repositories.general.training_record_repository import TrainingRecordRepository


class GetTrainingRecordUseCase:
    def __init__(self, record_repo: TrainingRecordRepository) -> None:
        self.record_repo = record_repo

    def execute(self, record_id: int) -> TrainingRecord | None:
        return self.record_repo.get(record_id)
