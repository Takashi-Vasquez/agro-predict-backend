from abc import ABC, abstractmethod

from app.domain.entities.core.company import Company
from app.domain.entities.general.campaign import Campaign
from app.domain.entities.operations.crop import Crop
from app.domain.entities.operations.variety import Variety


class SelectOptionRepository(ABC):
    @abstractmethod
    def list_rol_options(self) -> list[Crop]: ...

    @abstractmethod
    def list_crop_options(self) -> list[Crop]: ...

    @abstractmethod
    def list_variety_options(self) -> list[Variety]: ...

    @abstractmethod
    def list_campaign_options(self, crop_id: int | None = None) -> list[Campaign]: ...

    @abstractmethod
    def list_company_options(self, show_all: bool, user_id: int) -> list[Company]: ...
