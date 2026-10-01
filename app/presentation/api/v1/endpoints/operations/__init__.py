from fastapi import APIRouter

from app.presentation.api.v1.endpoints.operations.crops import router as crops_router
from app.presentation.api.v1.endpoints.operations.varieties import router as varieties_router

router = APIRouter()
router.include_router(crops_router)
router.include_router(varieties_router)
