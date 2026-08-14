from fastapi import APIRouter, HTTPException, Query, status

from app.presentation.api.deps import CurrentUser, DbDep
from app.infrastructure.config.settings import get_settings
from app.infrastructure.ml.model import CropPredictor
from app.infrastructure.repositories.prediction_repository import PredictionRepositoryImpl
from app.presentation.schemas.predictions.prediction import PredictionInput, PredictionRead
from app.domain.use_cases.predictions.predict import PredictUseCase
from app.domain.use_cases.predictions.list_predictions import ListPredictionsUseCase

router = APIRouter(prefix="/predictions", tags=["predictions"])

_predictor: CropPredictor | None = None


def get_predictor() -> CropPredictor:
    global _predictor
    if _predictor is None:
        settings = get_settings()
        _predictor = CropPredictor(settings.ML_MODEL_PATH, settings.ML_FEATURES)
    return _predictor


@router.post("", response_model=PredictionRead, status_code=status.HTTP_201_CREATED)
def predict(payload: PredictionInput, user: CurrentUser, db: DbDep) -> PredictionRead:
    try:
        use_case = PredictUseCase(PredictionRepositoryImpl(db), get_predictor())
        record = use_case.execute(
            user_id=user.id,
            data=payload.model_dump(),
            crop_id=payload.crop_id,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo no disponible. Entrena el modelo primero (ver README).",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    return PredictionRead.model_validate(record)


@router.get("", response_model=list[PredictionRead])
def list_predictions(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[PredictionRead]:
    rows = ListPredictionsUseCase(PredictionRepositoryImpl(db)).execute(user.id, offset, limit)
    return [PredictionRead.model_validate(r) for r in rows]
