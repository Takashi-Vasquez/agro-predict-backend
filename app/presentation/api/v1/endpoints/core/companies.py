from fastapi import APIRouter

from app.domain.use_cases.core.companies.list_companies import ListCompaniesUseCase
from app.infrastructure.repositories.core.company_repository import CompanyRepositoryImpl
from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.core.company import CompanyRead
from app.presentation.utils.api_response_factory import ApiResponseFactory

router = APIRouter(prefix="/core/companies", tags=["Core/Companies"])


@router.get("")
def list_companies(
    user: CurrentUser,
    db: DbDep,
    showAll: bool = False,
):
    companies = ListCompaniesUseCase(CompanyRepositoryImpl(db)).execute(
        show_all=showAll, user_id=user.id
    )
    data = [CompanyRead.model_validate(c).model_dump(by_alias=True) for c in companies]
    return ApiResponseFactory.ok(data, "Empresas obtenidas correctamente")
