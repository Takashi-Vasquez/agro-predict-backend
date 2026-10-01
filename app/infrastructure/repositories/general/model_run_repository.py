from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.general.model_run import ModelRun
from app.domain.repositories.general.model_run_repository import ModelRunRepository
from app.infrastructure.orm.general.model_run import ModelRun as ModelRunModel


class ModelRunRepositoryImpl(ModelRunRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_runs(self, offset: int = 0, limit: int = 100) -> list[ModelRun]:
        stmt = (
            select(ModelRunModel)
            .where(ModelRunModel.status != "DELETED")
            .order_by(ModelRunModel.trained_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    @staticmethod
    def _to_entity(orm: ModelRunModel) -> ModelRun:
        from app.domain.entities.general.model_run import ModelRun as ModelRunEntity

        return ModelRunEntity(
            id=orm.id,
            model_version_id=orm.model_version_id,
            trained_at=orm.trained_at,
            git_commit=orm.git_commit,
            data_version=orm.data_version,
            data_from=orm.data_from,
            data_to=orm.data_to,
            candidates_evaluated=orm.candidates_evaluated,
            winner=orm.winner,
            improvement_vs_baseline=orm.improvement_vs_baseline,
            generated_version=orm.generated_version,
            reason_no_version=orm.reason_no_version,
            duration_seconds=orm.duration_seconds,
        )