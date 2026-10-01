from app.domain.entities.general.training_record import TrainingRecord
from app.domain.repositories.general.training_record_repository import TrainingRecordRepository


class DeleteTrainingRecordUseCase:
    def __init__(self, record_repo: TrainingRecordRepository) -> None:
        self.record_repo = record_repo

    def execute(self, record_id: int) -> None:
        record = self.record_repo.get(record_id)
        if record is None:
            raise ValueError("Registro no encontrado")
        self.record_repo.delete(record)
