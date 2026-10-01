from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.operations.variety import Variety
from app.domain.repositories.operations.variety_repository import VarietyRepository
from app.infrastructure.orm.operations.variety import Variety as VarietyModel


class VarietyRepositoryImpl(VarietyRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Variety]:
        stmt = (
            select(VarietyModel)
            .where(VarietyModel.status != "DELETED")
            .order_by(VarietyModel.name)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def get_by_name(self, name: str) -> Variety | None:
        stmt = select(VarietyModel).where(
            VarietyModel.name == name,
            VarietyModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    @staticmethod
    def _to_entity(orm: VarietyModel) -> Variety:
        return Variety(
            id=orm.id,
            name=orm.name,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
