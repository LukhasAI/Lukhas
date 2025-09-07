from dataclasses import dataclass
from typing import Any, Optional

import streamlit as st


@dataclass
class APIError(Exception):
    """Base API error class."""

    code: str
message: str
details: Optional[dict[str, Any]] = None
status_code: int = 400


class ValidationError(APIError):
    """Request validation error."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(
code="VALIDATION_ERROR",
message=message,
details={"field": field} if field else None,
status_code=422,
)


class ProcessingError(APIError):
    """Processing error."""

    def __init__(self, message: str, drift_score: Optional[float] = None) -> None:
        super().__init__(
code="PROCESSING_ERROR",
message=message,
details={"drift_score": drift_score} if drift_score else None,
status_code=500,
)
