from app.domain.entities.core.company import Company
from app.domain.entities.general.campaign import Campaign
from app.domain.entities.operations.crop import Crop
from app.domain.entities.operations.variety import Variety
from app.domain.repositories.core.select_option_repository import SelectOptionRepository


class ListSelectOptionsUseCase:
    def __init__(self, select_option_repo: SelectOptionRepository) -> None:
        self.select_option_repo = select_option_repo

    def roles(self) -> list[Crop]:
        return self.select_option_repo.list_rol_options()
    
    def crops(self) -> list[Crop]:
        return self.select_option_repo.list_crop_options()

    def varieties(self) -> list[Variety]:
        return self.select_option_repo.list_variety_options()

    def campaigns(self, crop_id: int | None = None) -> list[Campaign]:
        return self.select_option_repo.list_campaign_options(crop_id)

    def companies(self, show_all: bool, user_id: int) -> list[Company]:
        return self.select_option_repo.list_company_options(show_all, user_id)
    
    
