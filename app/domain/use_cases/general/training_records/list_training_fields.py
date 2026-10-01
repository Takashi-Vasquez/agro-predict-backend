from app.domain.entities.general.training_field import TrainingField
from app.domain.repositories.general.training_field_repository import TrainingFieldRepository


class ListTrainingFieldsUseCase:
    def __init__(self, repo: TrainingFieldRepository) -> None:
        self.repo = repo

    def execute(self) -> list[TrainingField]:
        return self.repo.list_all()