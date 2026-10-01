from fastapi import APIRouter, Query

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.general.campaigns.campaign import CampaignCreate, CampaignRead, CampaignUpdate
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.general.campaign_repository import CampaignRepositoryImpl
from app.domain.exceptions import AppException
from app.domain.use_cases.general.campaigns.create_campaign import CreateCampaignUseCase
from app.domain.use_cases.general.campaigns.list_campaigns import ListCampaignsUseCase
from app.domain.use_cases.general.campaigns.get_campaign import GetCampaignUseCase
from app.domain.use_cases.general.campaigns.update_campaign import UpdateCampaignUseCase
from app.domain.use_cases.general.campaigns.delete_campaign import DeleteCampaignUseCase

router = APIRouter(prefix="/general/campaigns", tags=["General/Campaigns"])


@router.get("")
def list_campaigns(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    crop_id: int | None = Query(None, description="Filtrar por cultivo"),
):
    campaign_repo = CampaignRepositoryImpl(db)
    campaigns = ListCampaignsUseCase(campaign_repo).execute(
        offset=offset, limit=limit, crop_id=crop_id
    )
    data = [CampaignRead.model_validate(c).model_dump() for c in campaigns]
    return ApiResponseFactory.ok(data, "Campañas obtenidas correctamente")


@router.post("")
def create_campaign(payload: CampaignCreate, user: CurrentUser, db: DbDep):
    campaign_repo = CampaignRepositoryImpl(db)
    try:
        campaign = CreateCampaignUseCase(campaign_repo).execute(
            user_id=user.id,
            code=payload.code,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            crop_id=payload.crop_id,
            status=payload.status,
        )
    except ValueError as exc:
        raise AppException.bad_request(str(exc))
    result = CampaignRead.model_validate(campaign).model_dump()
    return ApiResponseFactory.created(result, "Campaña creada correctamente")


@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, user: CurrentUser, db: DbDep):
    campaign = GetCampaignUseCase(CampaignRepositoryImpl(db)).execute(campaign_id)
    if not campaign:
        raise AppException.not_found("Campaña no encontrada")
    data = CampaignRead.model_validate(campaign).model_dump()
    return ApiResponseFactory.ok(data, "Campaña obtenida correctamente")


@router.patch("/{campaign_id}")
def update_campaign(campaign_id: int, payload: CampaignUpdate, user: CurrentUser, db: DbDep):
    campaign_repo = CampaignRepositoryImpl(db)
    try:
        campaign = UpdateCampaignUseCase(campaign_repo).execute(
            campaign_id, **payload.model_dump(exclude_unset=True)
        )
    except ValueError as exc:
        raise AppException.bad_request(str(exc))
    result = CampaignRead.model_validate(campaign).model_dump()
    return ApiResponseFactory.ok(result, "Campaña actualizada correctamente")


@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, user: CurrentUser, db: DbDep):
    try:
        DeleteCampaignUseCase(CampaignRepositoryImpl(db)).execute(campaign_id)
    except ValueError as exc:
        raise AppException.not_found(str(exc))
    return ApiResponseFactory.no_content("Campaña eliminada correctamente")
