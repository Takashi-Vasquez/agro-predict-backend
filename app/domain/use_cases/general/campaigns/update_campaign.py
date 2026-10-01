from datetime import date

from app.domain.entities.general.campaign import Campaign
from app.domain.repositories.general.campaign_repository import CampaignRepository

VALID_STATUSES = {"PLANNED", "ACTIVE", "PAUSED", "CLOSED"}


class UpdateCampaignUseCase:
    def __init__(self, campaign_repo: CampaignRepository) -> None:
        self.campaign_repo = campaign_repo

    def execute(self, campaign_id: int, **kwargs) -> Campaign:
        campaign = self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError("Campaña no encontrada")

        new_code = kwargs.get("code", campaign.code)
        new_start = kwargs.get("start_date", campaign.start_date)
        new_end = kwargs.get("end_date", campaign.end_date)
        new_crop_id = kwargs.get("crop_id", campaign.crop_id)

        if "code" in kwargs and new_code != campaign.code:
            if self.campaign_repo.check_code_exists(new_code, exclude_id=campaign_id):
                raise ValueError(f"Ya existe una campaña con el código '{new_code}'")

        if new_end <= new_start:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

        if "start_date" in kwargs or "end_date" in kwargs or "crop_id" in kwargs:
            if self.campaign_repo.check_date_overlap(
                new_code, new_start, new_end, new_crop_id, exclude_id=campaign_id
            ):
                raise ValueError("Ya existe una campaña que se cruza con las fechas indicadas")

        if "status" in kwargs and kwargs["status"] not in VALID_STATUSES:
            raise ValueError(f"Status inválido: {kwargs['status']}. Válidos: {', '.join(VALID_STATUSES)}")

        return self.campaign_repo.update(campaign, **kwargs)
