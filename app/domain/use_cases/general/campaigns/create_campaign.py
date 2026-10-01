from datetime import date

from app.domain.entities.general.campaign import Campaign
from app.domain.repositories.general.campaign_repository import CampaignRepository
from app.infrastructure.repositories.operations.crop_repository import CropRepositoryImpl


VALID_STATUSES = {"PLANNED", "ACTIVE", "PAUSED", "CLOSED"}


class CreateCampaignUseCase:
    def __init__(self, campaign_repo: CampaignRepository, crop_repo_factory=None) -> None:
        self.campaign_repo = campaign_repo
        self.crop_repo_factory = crop_repo_factory

    def execute(
        self,
        user_id: int,
        code: str,
        name: str,
        start_date: date,
        end_date: date,
        crop_id: int,
        status: str
    ) -> Campaign:
        if self.campaign_repo.check_code_exists(code):
            raise ValueError(f"Ya existe una campaña con el código '{code}'")

        if end_date <= start_date:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

        if self.campaign_repo.check_date_overlap(code, start_date, end_date, crop_id):
            raise ValueError("Ya existe una campaña que se cruza con las fechas indicadas")

        return self.campaign_repo.create(
            user_id=user_id,
            code=code,
            name=name,
            start_date=start_date,
            end_date=end_date,
            crop_id=crop_id,
            status=status
        )
