from fastapi import APIRouter

from app.presentation.api.v1.endpoints.auth import router as auth_router
from app.presentation.api.v1.endpoints.security import router as security_router
from app.presentation.api.v1.endpoints.general import router as general_router
from app.presentation.api.v1.endpoints.operations import router as operations_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(security_router)
router.include_router(general_router)
router.include_router(operations_router)
