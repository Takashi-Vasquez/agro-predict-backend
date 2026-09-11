from fastapi import APIRouter, Query

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.config.settings import get_settings
from app.infrastructure.ml.model import CropPredictor
from app.infrastructure.repositories.prediction_repository import PredictionRepositoryImpl
from app.presentation.schemas.predictions.prediction import PredictionInput, PredictionRead
from app.domain.exceptions import AppException
from app.domain.use_cases.predictions.predict import PredictUseCase
from app.domain.use_cases.predictions.list_predictions import ListPredictionsUseCase

router = APIRouter(prefix="/operations/predictions", tags=["predictions"])

_predictor: CropPredictor | None = None


def get_predictor() -> CropPredictor:
    global _predictor
    if _predictor is None:
        settings = get_settings()
        _predictor = CropPredictor(settings.ML_MODEL_PATH, settings.ML_FEATURES)
    return _predictor


@router.post("")
def predict(payload: PredictionInput, user: CurrentUser, db: DbDep):
    try:
        use_case = PredictUseCase(PredictionRepositoryImpl(db), get_predictor())
        record = use_case.execute(
            user_id=user.id,
            data=payload.model_dump(),
            crop_id=payload.crop_id,
        )
    except FileNotFoundError:
        raise AppException.bad_request(
            "Modelo no disponible. Entrena el modelo primero (ver README)."
        )
    except ValueError as exc:
        raise AppException.bad_request(str(exc))
    data = PredictionRead.model_validate(record).model_dump()
    return ApiResponseFactory.created(data, "Predicción generada correctamente")


@router.get("")
def list_predictions(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    rows = ListPredictionsUseCase(PredictionRepositoryImpl(db)).execute(user.id, offset, limit)
    data = [PredictionRead.model_validate(r).model_dump() for r in rows]
    return ApiResponseFactory.ok(data, "Predicciones obtenidas correctamente")
