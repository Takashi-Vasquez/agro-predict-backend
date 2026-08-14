from fastapi import APIRouter, HTTPException, Query, status

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.common import Message
from app.presentation.schemas.crops.crop import CropCreate, CropRead, CropUpdate
from app.infrastructure.repositories.crop_repository import CropRepositoryImpl
from app.domain.use_cases.crops.create_crop import CreateCropUseCase
from app.domain.use_cases.crops.list_crops import ListCropsUseCase
from app.domain.use_cases.crops.update_crop import UpdateCropUseCase
from app.domain.use_cases.crops.delete_crop import DeleteCropUseCase

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("", response_model=list[CropRead])
def list_crops(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[CropRead]:
    crop_repo = CropRepositoryImpl(db)
    crops = ListCropsUseCase(crop_repo).execute(user.id, offset, limit)
    return [CropRead.model_validate(c) for c in crops]


@router.post("", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def create_crop(payload: CropCreate, user: CurrentUser, db: DbDep) -> CropRead:
    crop = CreateCropUseCase(CropRepositoryImpl(db)).execute(
        owner_id=user.id,
        name=payload.name,
        location=payload.location,
        area_hectares=payload.area_hectares,
        notes=payload.notes,
    )
    return CropRead.model_validate(crop)


@router.get("/{crop_id}", response_model=CropRead)
def get_crop(crop_id: int, user: CurrentUser, db: DbDep) -> CropRead:
    crop = CropRepositoryImpl(db).get_owned(user.id, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo no encontrado")
    return CropRead.model_validate(crop)


@router.patch("/{crop_id}", response_model=CropRead)
def update_crop(crop_id: int, payload: CropUpdate, user: CurrentUser, db: DbDep) -> CropRead:
    crop = UpdateCropUseCase(CropRepositoryImpl(db)).execute(
        user.id, crop_id, **payload.model_dump(exclude_unset=True)
    )
    return CropRead.model_validate(crop)


@router.delete("/{crop_id}", response_model=Message)
def delete_crop(crop_id: int, user: CurrentUser, db: DbDep) -> Message:
    DeleteCropUseCase(CropRepositoryImpl(db)).execute(user.id, crop_id)
    return Message(detail="Cultivo eliminado")
