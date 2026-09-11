from fastapi import APIRouter, Query

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.crops.crop import CropCreate, CropRead, CropUpdate
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.crop_repository import CropRepositoryImpl
from app.domain.exceptions import AppException
from app.domain.use_cases.crops.create_crop import CreateCropUseCase
from app.domain.use_cases.crops.list_crops import ListCropsUseCase
from app.domain.use_cases.crops.update_crop import UpdateCropUseCase
from app.domain.use_cases.crops.delete_crop import DeleteCropUseCase

router = APIRouter(prefix="/operations/crops", tags=["crops"])


@router.get("")
def list_crops(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    crop_repo = CropRepositoryImpl(db)
    crops = ListCropsUseCase(crop_repo).execute(user.id, offset, limit)
    data = [CropRead.model_validate(c).model_dump() for c in crops]
    return ApiResponseFactory.ok(data, "Cultivos obtenidos correctamente")


@router.post("")
def create_crop(payload: CropCreate, user: CurrentUser, db: DbDep):
    crop = CreateCropUseCase(CropRepositoryImpl(db)).execute(
        owner_id=user.id,
        name=payload.name,
        variety=payload.variety,
        category=payload.category,
        cycle=payload.cycle,
        temperature=payload.temperature,
        water=payload.water,
        color=payload.color,
    )
    data = CropRead.model_validate(crop).model_dump()
    return ApiResponseFactory.created(data, "Cultivo creado correctamente")


@router.get("/{crop_id}")
def get_crop(crop_id: int, user: CurrentUser, db: DbDep):
    crop = CropRepositoryImpl(db).get_owned(user.id, crop_id)
    if crop is None:
        raise AppException.not_found("Cultivo no encontrado")
    data = CropRead.model_validate(crop).model_dump()
    return ApiResponseFactory.ok(data, "Cultivo obtenido correctamente")


@router.patch("/{crop_id}")
def update_crop(crop_id: int, payload: CropUpdate, user: CurrentUser, db: DbDep):
    crop = UpdateCropUseCase(CropRepositoryImpl(db)).execute(
        user.id, crop_id, **payload.model_dump(exclude_unset=True)
    )
    data = CropRead.model_validate(crop).model_dump()
    return ApiResponseFactory.ok(data, "Cultivo actualizado correctamente")


@router.delete("/{crop_id}")
def delete_crop(crop_id: int, user: CurrentUser, db: DbDep):
    DeleteCropUseCase(CropRepositoryImpl(db)).execute(user.id, crop_id)
    return ApiResponseFactory.no_content("Cultivo eliminado correctamente")
