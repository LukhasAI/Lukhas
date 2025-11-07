"""
LUKHAS AI - Route Handlers
==========================

Route handling functionality for the unified API gateway.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RouteHandlers:
    """Route handlers for API gateway endpoints."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize route handlers with configuration."""
        self.config = config or {}
        self.handlers: dict[str, Callable] = {}
        self.middleware: list[Callable] = []
        # ΛTAG: uptime_tracking
        self._boot_timestamp = datetime.now(timezone.utc)
        self._boot_monotonic = time.monotonic()

        # Register default handlers
        self._register_default_handlers()

    def register_handler(self, path: str, handler: Callable) -> None:
        """Register a handler for a specific path."""
        self.handlers[path] = handler
        logger.info(f"Registered handler for path: {path}")

    def register_middleware(self, middleware: Callable) -> None:
        """Register middleware to be applied to all requests."""
        self.middleware.append(middleware)
        logger.info(f"Registered middleware: {middleware.__name__}")

    async def handle_request(self, path: str, request: dict[str, Any]) -> dict[str, Any]:
        """Handle incoming request by routing to appropriate handler."""
        try:
            # Apply middleware
            for middleware in self.middleware:
                request = await self._apply_middleware(middleware, request)

            # Find and execute handler
            handler = self._find_handler(path)
            if not handler:
                return {
                    "error": f"No handler found for path: {path}",
                    "status_code": 404,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Execute handler
            response = await handler(request)

            # Add metadata
            response["timestamp"] = datetime.now(timezone.utc).isoformat()
            response["path"] = path

            return response

        except Exception as e:
            logger.error(f"Error handling request for {path}: {e!s}")
            return {
                "error": f"Internal server error: {e!s}",
                "status_code": 500,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _find_handler(self, path: str) -> Optional[Callable]:
        """Find handler for given path."""
        # Direct match
        if path in self.handlers:
            return self.handlers[path]

        # Pattern matching (simple implementation)
        for registered_path, handler in self.handlers.items():
            if self._path_matches(path, registered_path):
                return handler

        return None

    def _path_matches(self, request_path: str, registered_path: str) -> bool:
        """Check if request path matches registered path pattern."""
        # Simple wildcard matching
        if registered_path.endswith("*"):
            prefix = registered_path[:-1]
            return request_path.startswith(prefix)

        return request_path == registered_path

    async def _apply_middleware(self, middleware: Callable, request: dict[str, Any]) -> dict[str, Any]:
        """Apply middleware to request."""
        try:
            if asyncio.iscoroutinefunction(middleware):
                return await middleware(request)
            else:
                return middleware(request)
        except Exception as e:
            logger.error(f"Error applying middleware {middleware.__name__}: {e!s}")
            return request  # Continue with original request

    def _register_default_handlers(self) -> None:
        """Register default handlers."""
        self.register_handler("/health", self._health_handler)
        self.register_handler("/status", self._status_handler)
        self.register_handler("/api/v1/*", self._api_handler)

    async def _health_handler(self, request: dict[str, Any]) -> dict[str, Any]:
        """Health check handler."""
        return {"status": "healthy", "service": "LUKHAS API Gateway", "version": "1.0.0", "status_code": 200}

    async def _status_handler(self, request: dict[str, Any]) -> dict[str, Any]:
        """Status handler."""
        return {
            "status": "operational",
            "registered_handlers": len(self.handlers),
            "middleware_count": len(self.middleware),
            "uptime": self._format_uptime(self._uptime_seconds()),
            "started_at": self._boot_timestamp.isoformat(),
            "status_code": 200,
        }

    async def _api_handler(self, request: dict[str, Any]) -> dict[str, Any]:
        """Default API handler."""
        path = request.get("path", "/api/v1/")

        return {
            "message": f"API endpoint: {path}",
            "method": request.get("method", "GET"),
            "user_id": request.get("user_id", "anonymous"),
            "status_code": 200,
            "data": "This is a placeholder API response",
        }

    def get_registered_paths(self) -> list[str]:
        """Get list of registered paths."""
        return list(self.handlers.keys())

    def remove_handler(self, path: str) -> bool:
        """Remove handler for specified path."""
        if path in self.handlers:
            del self.handlers[path]
            logger.info(f"Removed handler for path: {path}")
            return True
        return False

    def _uptime_seconds(self) -> float:
        """Compute uptime in seconds using a monotonic clock."""
        return max(0.0, time.monotonic() - self._boot_monotonic)

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Represent uptime as a human-friendly string."""
        # ΛTAG: uptime_tracking
        minutes, remaining_seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        segments: list[str] = []
        if days:
            segments.append(f"{days}d")
        if hours or segments:
            segments.append(f"{hours}h")
        if minutes or segments:
            segments.append(f"{minutes}m")
        segments.append(f"{remaining_seconds}s")
        return " ".join(segments)
