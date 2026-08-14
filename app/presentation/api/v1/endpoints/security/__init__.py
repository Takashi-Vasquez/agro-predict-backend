from fastapi import APIRouter

from app.presentation.api.v1.endpoints.security.users import router as users_router
from app.presentation.api.v1.endpoints.security.roles import router as roles_router
from app.presentation.api.v1.endpoints.security.profile import router as profile_router

router = APIRouter()
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(profile_router)
