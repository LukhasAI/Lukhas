"""
Compatibility entrypoint for the OpenAI-compatible API server.

Provides a `get_app()` factory callable so existing tooling like:

  uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000

continues to work after the API server was consolidated under `serve/main.py`.
"""

from __future__ import annotations

from typing import Any


def get_app() -> Any:
    """Return the FastAPI application defined in `serve.main`.

    This keeps the legacy `lukhas.adapters.openai.api:get_app` import path
    operational while using the consolidated server implementation.
    """
    # Import locally to avoid side effects at module import time
    from serve.main import app

    return app


__all__ = ["get_app"]
