from app.domain.repositories.general.campaign_repository import CampaignRepository


class DeleteCampaignUseCase:
    def __init__(self, campaign_repo: CampaignRepository) -> None:
        self.campaign_repo = campaign_repo

    def execute(self, campaign_id: int) -> None:
        campaign = self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError("Campaña no encontrada")
        self.campaign_repo.delete(campaign)
