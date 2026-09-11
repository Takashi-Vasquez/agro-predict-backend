from typing import Any

from fastapi.responses import JSONResponse

from app.presentation.schemas.common import ApiResponse


class ApiResponseFactory:
    @staticmethod
    def ok(data: Any = None, message: str = "OK") -> JSONResponse:
        return JSONResponse(
            status_code=200,
            content=ApiResponse(statusCode=200, message=message, data=data).model_dump(
                mode="json"
            ),
        )

    @staticmethod
    def created(data: Any = None, message: str = "Creado correctamente") -> JSONResponse:
        return JSONResponse(
            status_code=201,
            content=ApiResponse(statusCode=201, message=message, data=data).model_dump(
                mode="json"
            ),
        )

    @staticmethod
    def no_content(message: str = "Eliminado correctamente") -> JSONResponse:
        return JSONResponse(status_code=204, content=None)

    @staticmethod
    def bad_request(message: str = "Solicitud inválida") -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=ApiResponse(
                statusCode=400, message=message, data=None
            ).model_dump(mode="json"),
        )

    @staticmethod
    def unauthorized(message: str = "No autenticado") -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content=ApiResponse(
                statusCode=401, message=message, data=None
            ).model_dump(mode="json"),
        )

    @staticmethod
    def forbidden(message: str = "Acceso denegado") -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content=ApiResponse(
                statusCode=403, message=message, data=None
            ).model_dump(mode="json"),
        )

    @staticmethod
    def not_found(message: str = "Recurso no encontrado") -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=ApiResponse(
                statusCode=404, message=message, data=None
            ).model_dump(mode="json"),
        )

    @staticmethod
    def conflict(message: str = "Conflicto con recurso existente") -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=ApiResponse(
                statusCode=409, message=message, data=None
            ).model_dump(mode="json"),
        )
