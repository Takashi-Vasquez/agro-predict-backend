from fastapi import APIRouter

from app.presentation.api.v1.endpoints.auth.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
