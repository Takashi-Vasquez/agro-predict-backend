from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import set_empresa_id, clear_empresa_id


class EmpresaMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        empresa_id_header = request.headers.get("X-Company-Id")

        if empresa_id_header:
            try:
                from app.core.context import set_empresa_id
                set_empresa_id(int(empresa_id_header))
            except (ValueError, TypeError):
                pass

        try:
            await self.app(scope, receive, send)
        finally:
            from app.core.context import clear_empresa_id
            clear_empresa_id()