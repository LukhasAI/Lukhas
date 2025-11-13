
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from labs.core.security.auth import get_auth_system
from starlette.middleware.base import BaseHTTPMiddleware


class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Enforce authentication on all /v1/* endpoints.
    Returns 401 with OpenAI-compatible error envelope on auth failure.
    """

    def __init__(self, app):
        super().__init__(app)
        self.auth_system = get_auth_system()

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith('/v1/'):
            return await call_next(request)

        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return self._auth_error('Missing Authorization header')
        if not auth_header.startswith('Bearer '):
            return self._auth_error('Authorization header must use Bearer scheme')

        token = auth_header[7:].strip()
        if not token:
            return self._auth_error('Bearer token is empty')

        payload = self.auth_system.verify_jwt(token)
        if payload is None:
            return self._auth_error('Invalid authentication credentials')

        # Attach user info to request state
        request.state.user_id = payload.get("user_id")
        request.state.user_tier = payload.get("tier", 0)
        request.state.user_permissions = payload.get("permissions", [])
        request.state.user = payload  # Full claims for advanced use cases

        if not request.state.user_id:
            return self._auth_error("Token is missing the 'user_id' claim.")

        return await call_next(request)

    def _auth_error(self, message: str) -> Response:
        """Return OpenAI-compatible 401 error envelope."""
        error_detail = {'type': 'invalid_api_key', 'message': message, 'code': 'invalid_api_key'}
        error_response = {'error': error_detail}
        return JSONResponse(status_code=401, content=error_response)
