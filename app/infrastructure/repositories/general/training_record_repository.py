from app.infrastructure.orm.general.model_version import ModelVersion as ModelVersionModel
from app.presentation.schemas.general.training_records.training_record import TrainingRecordModelVersion
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.general.training_record import TrainingRecord
from app.domain.repositories.general.training_record_repository import TrainingRecordRepository
from app.infrastructure.orm.general.training_record import TrainingRecord as TrainingRecordModel

ROUND_FIELDS = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph_soil", "rainfall", "target_yield"]


def _round_fields(data: dict) -> dict:
    return {k: round(v, 2) if k in ROUND_FIELDS and isinstance(v, (int, float)) else v for k, v in data.items()}


class TrainingRecordRepositoryImpl(TrainingRecordRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, record_id: int) -> TrainingRecord | None:
        stmt = select(TrainingRecordModel).where(
            TrainingRecordModel.id == record_id,
            TrainingRecordModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list_all(
        self, *, offset: int = 0, limit: int = 100, crop_id: int | None = None
    ) -> list[TrainingRecord]:
        stmt = (
            select(TrainingRecordModel)
            .where(
                TrainingRecordModel.status != "DELETED",
            )
            .order_by(TrainingRecordModel.id.desc())
        )
        if crop_id is not None:
            stmt = stmt.where(TrainingRecordModel.crop_id == crop_id)
        stmt = stmt.offset(offset).limit(limit)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, **kwargs) -> TrainingRecord:
        orm = TrainingRecordModel(**_round_fields(kwargs))
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, record: TrainingRecord) -> None:
        orm = self.db.get(TrainingRecordModel, record.id)
        if orm:
            orm.status = "DELETED"
            orm.deleted_at = func.now()
            self.db.commit()

    def get_model_version_stats(self) -> TrainingRecordModelVersion:
        stmt = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.status == "production",
            )
            .order_by(ModelVersionModel.trained_at.desc())
        )
        orm = self.db.scalar(stmt)

        return TrainingRecordModelVersion.model_validate(orm) if orm else None

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(TrainingRecordModel).where(
            TrainingRecordModel.status != "DELETED",
        )
        return self.db.scalar(stmt) or 0

    def count_by_crop(self) -> int:
        stmt = (
            select(
                TrainingRecordModel.crop_id,
                func.count().label("count"),
            )
            .where(
                TrainingRecordModel.status != "DELETED",
                TrainingRecordModel.crop_id != None,
            )
            .group_by(TrainingRecordModel.crop_id)
        )
        result = self.db.execute(stmt).all()
        print(len(result))
        return len(result)

    def count_by_campaign(self) -> int:
        stmt = (
            select(
                TrainingRecordModel.campaign,
                func.count().label("count"),
            )
            .where(
                TrainingRecordModel.status != "DELETED",
                TrainingRecordModel.campaign != None,
            )
            .group_by(TrainingRecordModel.campaign)
        )
        result = self.db.execute(stmt).all()
        return len(result)

    def validate_is_all_trained(self) -> bool:
        stmt = (
            select(TrainingRecordModel.id)
            .where(
                TrainingRecordModel.status != "DELETED",
                TrainingRecordModel.is_trained == False
            )
            .limit(1)
        )
        
        has_untrained = self.db.execute(stmt).scalar() is not None
        
        # Si encontramos un registro sin entrenar, devolvemos False. Si no hay ninguno, True.
        return not has_untrained

    
    def create_batch(self, records: list[dict]) -> list[TrainingRecord]:
        orms = [TrainingRecordModel(**{k: v for k, v in _round_fields(r).items() if k not in {'row', 'error','crop'}}) for r in records]
        self.db.add_all(orms)
        self.db.commit()
        for orm in orms:
            self.db.refresh(orm)
        return [self._to_entity(o) for o in orms]

    @staticmethod
    def _to_entity(orm: TrainingRecordModel) -> TrainingRecord:
        return TrainingRecord(
            id=orm.id,
            user_id=orm.user_id,
            crop_id=orm.crop_id,
            campaign=orm.campaign,
            location=orm.location,
            nitrogen=orm.nitrogen,
            phosphorus=orm.phosphorus,
            potassium=orm.potassium,
            temperature=orm.temperature,
            humidity=orm.humidity,
            ph_soil=orm.ph_soil,
            rainfall=orm.rainfall,
            irrigation_type=orm.irrigation_type,
            variety=orm.variety,
            soil_type=orm.soil_type,
            target_yield=orm.target_yield,
            source=orm.source,
            import_batch_id=orm.import_batch_id,
            is_trained=orm.is_trained,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
