from app.domain.entities.general.training_record import TrainingRecord
from app.domain.repositories.general.training_record_repository import TrainingRecordRepository


class CreateTrainingRecordUseCase:
    def __init__(self, record_repo: TrainingRecordRepository) -> None:
        self.record_repo = record_repo

    def execute(self, user_id: int, data: dict) -> TrainingRecord:
        return self.record_repo.create(user_id=user_id, **data)
