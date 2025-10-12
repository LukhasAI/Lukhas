"""
SPDX-License-Identifier: Apache-2.0

FastAPI routers for OpenAI-compatible API.
"""
from lukhas.adapters.openai.routes.indexes import router as indexes_router

__all__ = ["indexes_router"]
