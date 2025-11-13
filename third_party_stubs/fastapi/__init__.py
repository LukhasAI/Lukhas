from __future__ import annotations

from typing import Any, Callable


class HTTPException(Exception):
    """Lightweight HTTP exception matching FastAPI's API."""

    def __init__(self, status_code: int, detail: Any = None) -> None:
        super().__init__(f"HTTP {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class Response:
    """Simple response container mimicking FastAPI's Response."""

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        media_type: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.media_type = media_type
        self.headers = headers or {}


class _Status:
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_404_NOT_FOUND = 404
    HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


status = _Status()


def Query(default: Any = None, **_: Any) -> Any:
    """Return default query value (validation not enforced)."""

    return default


class APIRouter:
    """Minimal APIRouter stub storing registered routes."""

    def __init__(self, prefix: str = "", tags: list[str] | None = None) -> None:
        self.prefix = prefix
        self.tags = tags or []
        self.routes: list[tuple[str, str, Callable[..., Any]]] = []

    def get(self, path: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.routes.append(("GET", path, func))
            return func

        return decorator


__all__ = ["APIRouter", "HTTPException", "Query", "Response", "status"]
