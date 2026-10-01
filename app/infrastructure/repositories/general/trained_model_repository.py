from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.domain.entities.general.trained_model import TrainedModel
from app.domain.repositories.general.trained_model_repository import TrainedModelRepository
from app.infrastructure.orm.general.trained_model import TrainedModel as TrainedModelModel


class TrainedModelRepositoryImpl(TrainedModelRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, model_id: int) -> TrainedModel | None:
        stmt = select(TrainedModelModel).where(
            TrainedModelModel.id == model_id,
            TrainedModelModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list_all(self) -> list[TrainedModel]:
        stmt = (
            select(TrainedModelModel)
            .where(
                TrainedModelModel.status != "DELETED",
            )
            .order_by(TrainedModelModel.r2_score.desc())
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_selected(self) -> TrainedModel | None:
        stmt = select(TrainedModelModel).where(
            TrainedModelModel.is_selected == True,
            TrainedModelModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def create(self, **kwargs) -> TrainedModel:
        orm = TrainedModelModel(**kwargs)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, model_id: int, **kwargs) -> TrainedModel | None:
        orm = self.db.get(TrainedModelModel, model_id)
        if not orm or orm.status == "DELETED":
            return None
        for k, v in kwargs.items():
            setattr(orm, k, v)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def set_selected(self, model_id: int) -> None:
        self.db.execute(
            update(TrainedModelModel)
            .where(
                TrainedModelModel.status != "DELETED",
            )
            .values(is_selected=False)
        )
        orm = self.db.get(TrainedModelModel, model_id)
        if orm:
            orm.is_selected = True
            self.db.commit()

    def archive_others(self) -> None:
        self.db.execute(
            update(TrainedModelModel)
            .where(
                TrainedModelModel.is_selected == True,
                TrainedModelModel.status != "DELETED",
            )
            .values(is_selected=False)
        )
        self.db.commit()

    @staticmethod
    def _to_entity(orm: TrainedModelModel) -> TrainedModel:
        return TrainedModel(
            id=orm.id,
            user_id=orm.user_id,
            name=orm.name,
            algorithm=orm.algorithm,
            version=orm.version,
            r2_score=orm.r2_score,
            rmse=orm.rmse,
            mae=orm.mae,
            feature_importance=orm.feature_importance,
            hyperparameters=orm.hyperparameters,
            training_samples=orm.training_samples,
            feature_names=orm.feature_names,
            artifact_path=orm.artifact_path,
            is_selected=orm.is_selected,
            notes=orm.notes,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
