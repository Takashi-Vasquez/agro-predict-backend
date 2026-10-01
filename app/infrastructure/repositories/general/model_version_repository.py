from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.general.model_version import ModelVersion
from app.domain.repositories.general.model_version_repository import ModelVersionRepository
from app.infrastructure.orm.general.model_version import ModelVersion as ModelVersionModel


class ModelVersionRepositoryImpl(ModelVersionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, version_id: int) -> ModelVersion | None:
        stmt = select(ModelVersionModel).where(
            ModelVersionModel.id == version_id,
            ModelVersionModel.status != "archived",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list_versions(
        self, model_name: str, offset: int = 0, limit: int = 100
    ) -> list[ModelVersion]:
        stmt = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.model_name == model_name,
                ModelVersionModel.status != "archived",
            )
            .order_by(ModelVersionModel.trained_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_production(self, model_name: str) -> ModelVersion | None:
        stmt = select(ModelVersionModel).where(
            ModelVersionModel.model_name == model_name,
            ModelVersionModel.status == "production",
            ModelVersionModel.status != "archived",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_latest_candidate(self, model_name: str) -> ModelVersion | None:
        stmt = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.model_name == model_name,
                ModelVersionModel.status == "candidate",
                ModelVersionModel.status != "archived",
            )
            .order_by(ModelVersionModel.trained_at.desc())
            .limit(1)
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    @staticmethod
    def _to_entity(orm: ModelVersionModel) -> ModelVersion:
        from app.domain.entities.general.model_version import ModelVersion as ModelVersionEntity

        return ModelVersionEntity(
            id=orm.id,
            model_name=orm.model_name,
            version=orm.version,
            status=orm.status,
            trained_at=orm.trained_at,
            git_commit=orm.git_commit,
            data_version=orm.data_version,
            data_from=orm.data_from,
            data_to=orm.data_to,
            features=orm.features,
            candidates_evaluated=orm.candidates_evaluated,
            metrics=orm.metrics,
            baseline_compared=orm.baseline_compared,
            base_version_id=orm.base_version_id,
            artifact_path=orm.artifact_path,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )