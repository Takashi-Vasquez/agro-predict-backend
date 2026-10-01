from fastapi import APIRouter

from app.presentation.api.v1.endpoints.general.predictions import router as predictions_router
from app.presentation.api.v1.endpoints.general.training_records import router as training_records_router
from app.presentation.api.v1.endpoints.general.trained_models import router as trained_models_router
from app.presentation.api.v1.endpoints.general.campaigns import router as campaigns_router

router = APIRouter()
router.include_router(predictions_router)
router.include_router(training_records_router)
router.include_router(trained_models_router)
router.include_router(campaigns_router)
