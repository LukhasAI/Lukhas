"""Entry point for Lukhas commercial API"""

from fastapi import FastAPI
import logging

from .routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Lukhas Commercial API")
app.include_router(router)
