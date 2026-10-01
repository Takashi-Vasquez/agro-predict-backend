from app.domain.entities.general.campaign import Campaign
from app.domain.repositories.general.campaign_repository import CampaignRepository


class ListCampaignsUseCase:
    def __init__(self, campaign_repo: CampaignRepository) -> None:
        self.campaign_repo = campaign_repo

    def execute(
        self, offset: int = 0, limit: int = 100, crop_id: int | None = None
    ) -> list[Campaign]:
        return self.campaign_repo.list_all(offset=offset, limit=limit, crop_id=crop_id)
