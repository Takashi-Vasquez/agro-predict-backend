from abc import ABC, abstractmethod

from app.domain.entities.core.catalog import Catalog
from app.domain.entities.core.catalog_detail import CatalogDetail


class CatalogRepository(ABC):
    @abstractmethod
    def get_by_code(self, code: str) -> Catalog | None: ...

    @abstractmethod
    def get_details_by_catalog_id(self, catalog_id: int) -> list[CatalogDetail]: ...
