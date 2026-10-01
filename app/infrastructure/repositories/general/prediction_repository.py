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

    def list_all(self, *, offset: int = 0, limit: int = 100) -> list[Prediction]:
        stmt = (
            select(PredictionModel)
            .where(PredictionModel.status != "DELETED")
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
            nitrogen=orm.nitrogen,
            phosphorus=orm.phosphorus,
            potassium=orm.potassium,
            temperature=orm.temperature,
            humidity=orm.humidity,
            ph_soil=orm.ph_soil,
            rainfall=orm.rainfall,
            predicted_yield=orm.predicted_yield,
            target_yield=orm.target_yield,
            gap=orm.gap,
            model_id=orm.model_id,
            model_algorithm=orm.model_algorithm,
            error_message=orm.error_message,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
