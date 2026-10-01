from app.domain.entities.general.model_run import ModelRun
from app.domain.repositories.general.model_run_repository import ModelRunRepository


class ListModelRunsUseCase:
    def __init__(self, repo: ModelRunRepository) -> None:
        self.repo = repo

    def execute(self, offset: int = 0, limit: int = 100) -> list[ModelRun]:
        return self.repo.list_runs(offset, limit)