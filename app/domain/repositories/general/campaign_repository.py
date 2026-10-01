from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.general.campaign import Campaign


class CampaignRepository(ABC):
    @abstractmethod
    def get(self, campaign_id: int) -> Campaign | None: ...

    @abstractmethod
    def list_all(
        self, *, offset: int = 0, limit: int = 100, crop_id: int | None = None
    ) -> list[Campaign]: ...

    @abstractmethod
    def create(
        self,
        user_id: int,
        code: str,
        name: str,
        start_date: date,
        end_date: date,
        crop_id: int,
        status: str,
    ) -> Campaign: ...

    @abstractmethod
    def update(self, campaign: Campaign, **kwargs) -> Campaign: ...

    @abstractmethod
    def delete(self, campaign: Campaign) -> None: ...

    @abstractmethod
    def check_code_exists(self, code: str, exclude_id: int | None = None) -> bool: ...

    @abstractmethod
    def check_date_overlap(
        self, code: str, start_date: date, end_date: date, crop_id: int, exclude_id: int | None = None
    ) -> bool: ...
