from http import HTTPStatus


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        statusCode: int = HTTPStatus.BAD_REQUEST,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.statusCode = statusCode

    @staticmethod
    def bad_request(message: str = "Solicitud inválida") -> "AppException":
        return AppException(message, "BAD_REQUEST", HTTPStatus.BAD_REQUEST)

    @staticmethod
    def unauthorized(message: str = "No autenticado") -> "AppException":
        return AppException(message, "UNAUTHORIZED", HTTPStatus.UNAUTHORIZED)

    @staticmethod
    def forbidden(message: str = "Acceso denegado") -> "AppException":
        return AppException(message, "FORBIDDEN", HTTPStatus.FORBIDDEN)

    @staticmethod
    def not_found(message: str = "Recurso no encontrado") -> "AppException":
        return AppException(message, "NOT_FOUND", HTTPStatus.NOT_FOUND)

    @staticmethod
    def conflict(message: str = "Conflicto con recurso existente") -> "AppException":
        return AppException(message, "CONFLICT", HTTPStatus.CONFLICT)

    @staticmethod
    def internal(message: str = "Error interno del servidor") -> "AppException":
        return AppException(message, "INTERNAL_ERROR", HTTPStatus.INTERNAL_SERVER_ERROR)
