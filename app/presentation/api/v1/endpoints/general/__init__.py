from fastapi import APIRouter

from app.presentation.api.v1.endpoints.general.predictions import router as predictions_router

router = APIRouter()
router.include_router(predictions_router)
