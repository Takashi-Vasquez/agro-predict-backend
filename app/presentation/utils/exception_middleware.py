import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware

from app.domain.exceptions import AppException
from app.presentation.schemas.common import ApiResponse


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppException as exc:
            return JSONResponse(
                status_code=exc.statusCode,
                content=ApiResponse(
                    statusCode=exc.statusCode,
                    message=str(exc),
                    data=None,
                ).model_dump(mode="json"),
            )
        except IntegrityError:
            return JSONResponse(
                status_code=409,
                content=ApiResponse(
                    statusCode=409,
                    message="El recurso ya existe",
                    data=None,
                ).model_dump(mode="json"),
            )
        except Exception as exc:
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content=ApiResponse(
                    statusCode=500,
                    message="Error interno del servidor",
                    data=None,
                ).model_dump(mode="json"),
            )
