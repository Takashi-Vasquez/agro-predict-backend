from fastapi import APIRouter, Query

from app.domain.use_cases.core.select_options.list_select_options import ListSelectOptionsUseCase
from app.infrastructure.repositories.core.select_option_repository import SelectOptionRepositoryImpl
from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.core.select_options import SelectOption
from app.presentation.utils.api_response_factory import ApiResponseFactory

router = APIRouter(prefix="/core/select-options", tags=["Core/Select Options"])


@router.get("/crops")
def get_crop_options(user: CurrentUser, db: DbDep):
    crops = ListSelectOptionsUseCase(SelectOptionRepositoryImpl(db)).crops()
    options = [SelectOption(value=c.id, label=f"{c.name} - {c.variety}") for c in crops]
    return ApiResponseFactory.ok(options, "Opciones de cultivos obtenidas")


@router.get("/varieties")
def get_variety_options(user: CurrentUser, db: DbDep):
    varieties = ListSelectOptionsUseCase(SelectOptionRepositoryImpl(db)).varieties()
    options = [SelectOption(value=v.id, label=v.name) for v in varieties]
    return ApiResponseFactory.ok(options, "Opciones de variedades obtenidas")


@router.get("/campaigns")
def get_campaign_options(
    user: CurrentUser,
    db: DbDep,
    cropId: int | None = Query(None, description="Filtrar por cultivo"),
):
    campaigns = ListSelectOptionsUseCase(SelectOptionRepositoryImpl(db)).campaigns(crop_id=cropId)
    options = [SelectOption(value=c.id, label=f"{c.name} [{c.code}]", code=c.code) for c in campaigns]
    return ApiResponseFactory.ok(options, "Opciones de campañas obtenidas")


@router.get("/companies")
def get_company_options(user: CurrentUser, db: DbDep, showAll: bool = False):
    companies = ListSelectOptionsUseCase(SelectOptionRepositoryImpl(db)).companies(
        show_all=showAll, user_id=user.id
    )
    options = [SelectOption(value=c.id, label=c.name) for c in companies]
    return ApiResponseFactory.ok(options, "Opciones de empresas obtenidas")

@router.get("/roles")
def get_crop_options(user: CurrentUser, db: DbDep):
    roles = ListSelectOptionsUseCase(SelectOptionRepositoryImpl(db)).roles()
    options = [SelectOption(value=c.id, label=f"{c.name}") for c in roles]
    return ApiResponseFactory.ok(options, "Opciones de Roles obtenidas")