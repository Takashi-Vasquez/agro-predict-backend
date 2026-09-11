from fastapi import APIRouter

from app.presentation.api.v1.endpoints.core.operations.crops import router as crops_router
from app.presentation.api.v1.endpoints.core.operations.predictions import router as predictions_router

router = APIRouter()
router.include_router(crops_router)
router.include_router(predictions_router)
