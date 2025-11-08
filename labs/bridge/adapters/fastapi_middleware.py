from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from labs.bridge.adapters.api_framework import JWTAdapter, TokenValidationResult


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_adapter: JWTAdapter, unprotected_paths: set = None):
        super().__init__(app)
        self.jwt_adapter = jwt_adapter
        self.unprotected_paths = unprotected_paths or set()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.unprotected_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
            )

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Authorization header format"},
            )

        token = parts[1]
        validation_result: TokenValidationResult = self.jwt_adapter.verify_token(token)

        if not validation_result.valid:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": validation_result.error, "error_code": validation_result.error_code},
            )

        request.scope["auth"] = validation_result.claims
        response = await call_next(request)
        return response
