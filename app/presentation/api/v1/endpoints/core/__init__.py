from fastapi import APIRouter

from app.presentation.api.v1.endpoints.core.operations import router as operations_router

router = APIRouter()
router.include_router(operations_router)
