from fastapi import APIRouter

from app.presentation.api.v1.endpoints.core.catalogs import router as catalogs_router
from app.presentation.api.v1.endpoints.core.select_options import router as select_options_router

router = APIRouter()
router.include_router(catalogs_router)
router.include_router(select_options_router)
