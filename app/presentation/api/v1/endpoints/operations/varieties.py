from fastapi import APIRouter

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.operations.varieties.variety import VarietyRead
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.operations.variety_repository import VarietyRepositoryImpl

router = APIRouter(prefix="/operations/varieties", tags=["Operations/Varieties"])


@router.get("")
def list_varieties(user: CurrentUser, db: DbDep):
    repo = VarietyRepositoryImpl(db)
    varieties = repo.list_all()
    data = [VarietyRead.model_validate(v).model_dump() for v in varieties]
    return ApiResponseFactory.ok(data, "Variedades obtenidas correctamente")
