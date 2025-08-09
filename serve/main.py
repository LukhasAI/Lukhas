"""Entry point for Lukhas commercial API"""

from fastapi import FastAPI
import logging

from .routes import router
from .openai_routes import router as openai_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Lukhas Commercial API")
app.include_router(router)
app.include_router(openai_router)
