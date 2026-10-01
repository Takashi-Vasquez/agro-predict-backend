from fastapi import APIRouter

from app.presentation.api.deps import DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.core.catalog_repository import CatalogRepositoryImpl
from app.domain.exceptions import AppException

router = APIRouter(prefix="/core/catalogs", tags=["Core/Catalogs"])


@router.get("/{code}")
def get_catalog_by_code(code: str, db: DbDep):
    repo = CatalogRepositoryImpl(db)
    catalog = repo.get_by_code(code)
    if not catalog:
        raise AppException.not_found(f"Catálogo '{code}' no encontrado")

    details = repo.get_details_by_catalog_id(catalog.id)

    data = [
            {"id": d.id, "value": d.value, "label": d.label, "orderIndex": d.order_index}
            for d in details
        ]
    return ApiResponseFactory.ok(data, "Catálogo obtenido correctamente")
