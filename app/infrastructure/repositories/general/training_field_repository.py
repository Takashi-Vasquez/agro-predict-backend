from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.general.training_field import TrainingField
from app.domain.repositories.general.training_field_repository import TrainingFieldRepository
from app.infrastructure.repositories.base import apply_company_filter
from app.infrastructure.orm.general.training_field import TrainingField as TrainingFieldModel


class TrainingFieldRepositoryImpl(TrainingFieldRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[TrainingField]:
        stmt = (
            select(TrainingFieldModel)
            .where(TrainingFieldModel.status != "DELETED")
            .order_by(TrainingFieldModel.order_index)
        )
        stmt = apply_company_filter(stmt, TrainingFieldModel)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    @staticmethod
    def _to_entity(orm: TrainingFieldModel) -> TrainingField:
        return TrainingField(
            id=orm.id,
            field_key=orm.field_key,
            label=orm.label,
            field_type=orm.field_type,
            category=orm.category,
            unit=orm.unit,
            min_value=orm.min_value,
            max_value=orm.max_value,
            options=orm.options,
            is_required=orm.is_required,
            order_index=orm.order_index,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )