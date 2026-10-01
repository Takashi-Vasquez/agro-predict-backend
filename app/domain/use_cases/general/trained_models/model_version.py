from app.domain.entities.general.model_version import ModelVersion
from app.domain.repositories.general.model_version_repository import ModelVersionRepository


class GetModelVersionUseCase:
    def __init__(self, repo: ModelVersionRepository) -> None:
        self.repo = repo

    def execute(self, version_id: int) -> ModelVersion | None:
        return self.repo.get(version_id)


class ListModelVersionsUseCase:
    def __init__(self, repo: ModelVersionRepository) -> None:
        self.repo = repo

    def execute(
        self, model_name: str = "yield-prediction", offset: int = 0, limit: int = 100
    ) -> list[ModelVersion]:
        return self.repo.list_versions(model_name, offset, limit)


class GetProductionModelUseCase:
    def __init__(self, repo: ModelVersionRepository) -> None:
        self.repo = repo

    def execute(self, model_name: str = "yield-prediction") -> ModelVersion | None:
        return self.repo.get_production(model_name)