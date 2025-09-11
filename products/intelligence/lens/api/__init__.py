"""API Module for ΛLens.

This package exposes the FastAPI `app`, the `router` and pydantic schemas.
`api_new` has been consolidated into this package; this module exports the
canonical application objects for imports across the repository.
"""

import streamlit as st

from .endpoints import router
from .main import app
from .schemas import JobRequest, JobResponse, PhotonDocument

__all__ = ["JobRequest", "JobResponse", "PhotonDocument", "app", "router"]
