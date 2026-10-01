from sqlalchemy.orm import Session

from app.domain.entities.core.catalog import Catalog
from app.domain.entities.core.catalog_detail import CatalogDetail
from app.domain.repositories.core.catalog_repository import CatalogRepository
from app.infrastructure.orm.core.catalog import Catalog as CatalogModel
from app.infrastructure.orm.core.catalog_detail import CatalogDetail as CatalogDetailModel


class CatalogRepositoryImpl(CatalogRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_code(self, code: str) -> Catalog | None:
        orm = self.db.query(CatalogModel).filter(
            CatalogModel.code == code,
            CatalogModel.is_active == True,
            CatalogModel.status != "DELETED",
        ).first()
        return self._to_entity(orm) if orm else None

    def get_details_by_catalog_id(self, catalog_id: int) -> list[CatalogDetail]:
        orms = (
            self.db.query(CatalogDetailModel)
            .filter(
                CatalogDetailModel.catalog_id == catalog_id,
                CatalogDetailModel.is_active == True,
                CatalogDetailModel.status != "DELETED",
            )
            .order_by(CatalogDetailModel.order_index)
            .all()
        )
        return [self._detail_to_entity(o) for o in orms]

    @staticmethod
    def _to_entity(orm: CatalogModel) -> Catalog:
        return Catalog(
            id=orm.id,
            code=orm.code,
            label=orm.label,
            description=orm.description,
            is_active=orm.is_active,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def _detail_to_entity(orm: CatalogDetailModel) -> CatalogDetail:
        return CatalogDetail(
            id=orm.id,
            catalog_id=orm.catalog_id,
            value=orm.value,
            label=orm.label,
            order_index=orm.order_index,
            is_active=orm.is_active,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
