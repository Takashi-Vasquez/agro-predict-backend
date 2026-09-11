from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.infrastructure.config.settings import get_settings
from app.infrastructure.orm.base import Base
from app.infrastructure.database.session import _get_engine
from app.presentation.api.v1.router import router
from app.presentation.utils.exception_middleware import ExceptionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    engine = _get_engine()
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS security"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print(f"\n  API disponible en http://localhost:8150/docs\n")
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="API de prediccion de cultivos para tesis. Clean Architecture.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ExceptionMiddleware)

    app.include_router(router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.APP_NAME}

    return app


app = create_app()
