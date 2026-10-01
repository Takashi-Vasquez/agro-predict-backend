from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.domain.entities.general.campaign import Campaign
from app.domain.repositories.general.campaign_repository import CampaignRepository
from app.infrastructure.orm.general.campaign import Campaign as CampaignModel
from app.infrastructure.orm.operations.crop import Crop as CropModel


class CampaignRepositoryImpl(CampaignRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, campaign_id: int) -> Campaign | None:
        stmt = select(CampaignModel).where(
            CampaignModel.id == campaign_id,
            CampaignModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list_all(
        self, *, offset: int = 0, limit: int = 100, crop_id: int | None = None
    ) -> list[Campaign]:
        stmt = (
            select(CampaignModel)
            .where(
                CampaignModel.status != "DELETED",
            )
            .order_by(CampaignModel.id.desc())
        )
        if crop_id is not None:
            stmt = stmt.where(CampaignModel.crop_id == crop_id)
        stmt = stmt.offset(offset).limit(limit)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(
        self,
        user_id: int,
        code: str,
        name: str,
        start_date,
        end_date,
        crop_id: int,
        status: str = "PLANIFICADA",
    ) -> Campaign:
        orm = CampaignModel(
            user_id=user_id,
            code=code,
            name=name,
            start_date=start_date,
            end_date=end_date,
            crop_id=crop_id,
            status=status,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, campaign: Campaign, **kwargs) -> Campaign:
        orm = self.db.get(CampaignModel, campaign.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, campaign: Campaign) -> None:
        orm = self.db.get(CampaignModel, campaign.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.utcnow()
        self.db.commit()

    def check_code_exists(self, code: str, exclude_id: int | None = None) -> bool:
        conditions = [
            CampaignModel.code == code,
            CampaignModel.status != "DELETED",
        ]
        if exclude_id is not None:
            conditions.append(CampaignModel.id != exclude_id)
        stmt = select(CampaignModel.id).where(and_(*conditions)).limit(1)
        return self.db.scalar(stmt) is not None

    def check_date_overlap(
        self, code: str, start_date, end_date, crop_id, exclude_id: int | None = None
    ) -> bool:
        conditions = [
            CampaignModel.code == code,
            CampaignModel.status != "DELETED",
            CampaignModel.start_date <= end_date,
            CampaignModel.end_date >= start_date,
        ]
        if exclude_id is not None:
            conditions.append(CampaignModel.id != exclude_id)
        stmt = select(CampaignModel.id).where(and_(*conditions)).limit(1)
        return self.db.scalar(stmt) is not None

    @staticmethod
    def _to_entity(orm: CampaignModel) -> Campaign:
        return Campaign(
            id=orm.id,
            user_id=orm.user_id,
            code=orm.code,
            name=orm.name,
            start_date=orm.start_date,
            end_date=orm.end_date,
            crop_id=orm.crop_id,
            crop_name=orm.crop.name if orm.crop else "",
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
