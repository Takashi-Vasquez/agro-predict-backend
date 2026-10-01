from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Crop
from app.domain.repositories import CropRepository
from app.infrastructure.orm.operations.crop import Crop as CropModel


class CropRepositoryImpl(CropRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, crop_id: int) -> Crop | None:
        stmt = select(CropModel).where(CropModel.id == crop_id, CropModel.status != "DELETED")
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list_all(self, *, offset: int = 0, limit: int = 100) -> list[Crop]:
        stmt = (
            select(CropModel)
            .where(CropModel.status != "DELETED")
            .order_by(CropModel.id)
            .offset(offset).limit(limit)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, owner_id, name, variety_id, category, cycle, temperature, water, color) -> Crop:
        orm = CropModel(owner_id=owner_id, name=name, variety_id=variety_id, category=category,
                        cycle=cycle, temperature=temperature, water=water, color=color)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, crop: Crop, **kwargs) -> Crop:
        orm = self.db.get(CropModel, crop.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, crop: Crop) -> None:
        orm = self.db.get(CropModel, crop.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.utcnow()
        self.db.commit()

    @staticmethod
    def _to_entity(orm: CropModel) -> Crop:
        return Crop(
            id=orm.id, owner_id=orm.owner_id, name=orm.name,
            variety_id=orm.variety_id,
            variety=orm.variety.name if orm.variety else "",
            category=orm.category, cycle=orm.cycle, temperature=orm.temperature,
            water=orm.water, color=orm.color, status=orm.status,
            created_at=orm.created_at, updated_at=orm.updated_at, deleted_at=orm.deleted_at,
        )
