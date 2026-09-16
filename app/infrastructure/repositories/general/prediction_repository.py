from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Prediction
from app.domain.repositories import PredictionRepository
from app.infrastructure.orm.general.prediction import Prediction as PredictionModel


class PredictionRepositoryImpl(PredictionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, prediction_id: int) -> Prediction | None:
        stmt = select(PredictionModel).where(
            PredictionModel.id == prediction_id,
            PredictionModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list_for_user(self, user_id: int, *, offset: int = 0, limit: int = 100) -> list[Prediction]:
        stmt = (
            select(PredictionModel)
            .where(PredictionModel.user_id == user_id, PredictionModel.status != "DELETED")
            .order_by(PredictionModel.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, **kwargs) -> Prediction:
        orm = PredictionModel(**kwargs)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    @staticmethod
    def _to_entity(orm: PredictionModel) -> Prediction:
        return Prediction(
            id=orm.id,
            user_id=orm.user_id,
            crop_id=orm.crop_id,
            predicted_crop=orm.predicted_crop,
            probability=orm.probability,
            N=orm.N,
            P=orm.P,
            K=orm.K,
            temperature=orm.temperature,
            humidity=orm.humidity,
            ph=orm.ph,
            rainfall=orm.rainfall,
            error_message=orm.error_message,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
