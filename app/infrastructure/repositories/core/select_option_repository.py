from app.domain.entities.security.role_permissions import RolePermission
from app.infrastructure.orm.security.role_permissions import RolePermission as RolePermissionModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.core.company import Company
from app.domain.entities.general.campaign import Campaign
from app.domain.entities.operations.crop import Crop
from app.domain.entities.operations.variety import Variety
from app.domain.repositories.core.select_option_repository import SelectOptionRepository
from app.infrastructure.orm.general.campaign import Campaign as CampaignModel
from app.infrastructure.orm.operations.crop import Crop as CropModel
from app.infrastructure.orm.operations.variety import Variety as VarietyModel
from app.infrastructure.repositories.base import apply_company_filter
from app.infrastructure.repositories.core.company_repository import CompanyRepositoryImpl


class SelectOptionRepositoryImpl(SelectOptionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_rol_options(self) -> list[RolePermission]:
        stmt = (
            select(RolePermissionModel)
            .where(RolePermissionModel.status == "ACTIVE")
            .order_by(RolePermissionModel.name)
        )
        stmt = apply_company_filter(stmt, RolePermissionModel)
        return [self._rol_to_entity(o) for o in self.db.scalars(stmt).all()]

    def list_crop_options(self) -> list[Crop]:
        stmt = (
            select(CropModel)
            .where(CropModel.status != "DELETED")
            .order_by(CropModel.name)
        )
        stmt = apply_company_filter(stmt, CropModel)
        return [self._crop_to_entity(o) for o in self.db.scalars(stmt).all()]

    def list_variety_options(self) -> list[Variety]:
        stmt = (
            select(VarietyModel)
            .where(VarietyModel.status != "DELETED")
            .order_by(VarietyModel.name)
        )
        stmt = apply_company_filter(stmt, VarietyModel)
        return [self._variety_to_entity(o) for o in self.db.scalars(stmt).all()]

    def list_campaign_options(self, crop_id: int | None = None) -> list[Campaign]:
        stmt = (
            select(CampaignModel)
            .where(CampaignModel.status != "DELETED")
            .order_by(CampaignModel.name)
        )
        if crop_id is not None:
            stmt = stmt.where(CampaignModel.crop_id == crop_id)
        stmt = apply_company_filter(stmt, CampaignModel)
        return [self._campaign_to_entity(o) for o in self.db.scalars(stmt).all()]

    def list_company_options(self, show_all: bool, user_id: int) -> list[Company]:
        company_repo = CompanyRepositoryImpl(self.db)
        if show_all:
            return company_repo.list_all()
        return [company for company, _is_default in company_repo.list_for_user(user_id)]

    @staticmethod
    def _rol_to_entity(orm: RolePermissionModel) -> RolePermission:
        return RolePermission(
            id=orm.id,
            name=orm.name,
            company_id=orm.company_id,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
    
    @staticmethod
    def _crop_to_entity(orm: CropModel) -> Crop:
        return Crop(
            id=orm.id,
            owner_id=orm.owner_id,
            name=orm.name,
            variety_id=orm.variety_id,
            variety=orm.variety.name if orm.variety else "",
            category=orm.category,
            cycle=orm.cycle,
            temperature=orm.temperature,
            water=orm.water,
            color=orm.color,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def _variety_to_entity(orm: VarietyModel) -> Variety:
        return Variety(
            id=orm.id,
            name=orm.name,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def _campaign_to_entity(orm: CampaignModel) -> Campaign:
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

