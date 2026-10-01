from fastapi import APIRouter, Query
from sqlalchemy import select

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.core.select_options import SelectOption
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.orm.operations.crop import Crop as CropModel
from app.infrastructure.orm.operations.variety import Variety as VarietyModel
from app.infrastructure.orm.general.campaign import Campaign as CampaignModel

router = APIRouter(prefix="/core/select-options", tags=["Core/Select Options"])


@router.get("/crops")
def get_crop_options(user: CurrentUser, db: DbDep):
    stmt = (
        select(CropModel)
        .where(CropModel.status != "DELETED")
        .order_by(CropModel.name)
    )
    crops = db.scalars(stmt).all()
    options = [SelectOption(value=int(c.id), label=f"{c.name} - {c.variety.name}") for c in crops]
    return ApiResponseFactory.ok(options, "Opciones de cultivos obtenidas")


@router.get("/varieties")
def get_variety_options(user: CurrentUser, db: DbDep):
    stmt = (
        select(VarietyModel)
        .where(VarietyModel.status != "DELETED")
        .order_by(VarietyModel.name)
    )
    varieties = db.scalars(stmt).all()
    options = [SelectOption(value=v.id, label=v.name) for v in varieties]
    return ApiResponseFactory.ok(options, "Opciones de variedades obtenidas")


@router.get("/campaigns")
def get_campaign_options(
    user: CurrentUser,
    db: DbDep,
    cropId: int | None = Query(None, description="Filtrar por cultivo"),
):
    stmt = (
        select(CampaignModel)
        .where(CampaignModel.status != "DELETED")
        .order_by(CampaignModel.name)
    )

    if cropId is not None:
        stmt = stmt.where(CampaignModel.crop_id == cropId)

    campaigns = db.scalars(stmt).all()
    options = [SelectOption(value=c.id, label=f"{c.name} [{c.code}]", code=c.code) for c in campaigns]
    return ApiResponseFactory.ok(options, "Opciones de campañas obtenidas")
