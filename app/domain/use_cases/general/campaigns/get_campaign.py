from app.domain.entities.general.campaign import Campaign
from app.domain.repositories.general.campaign_repository import CampaignRepository


class GetCampaignUseCase:
    def __init__(self, campaign_repo: CampaignRepository) -> None:
        self.campaign_repo = campaign_repo

    def execute(self, campaign_id: int) -> Campaign | None:
        return self.campaign_repo.get(campaign_id)
