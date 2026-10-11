from fastapi import APIRouter

from app.presentation.api.v1.endpoints.security.users import router as users_router
from app.presentation.api.v1.endpoints.security.access_profile import router as access_profile_router

router = APIRouter()
router.include_router(users_router)
router.include_router(access_profile_router)
