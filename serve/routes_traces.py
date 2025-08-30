"""
Enhanced trace endpoint with TraceMemoryLogger integration.
Provides structured API for retrieving trace data with proper error handling and authentication.
"""

import logging
import uuid
from typing import Optional, Union

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from .models.trace_models import (
    ExecutionTraceResponse,
    TraceErrorResponse,
    TraceNotFoundResponse,
    TraceResponse,
    TraceValidationErrorResponse,
)
from .storage.trace_provider import TraceStorageProvider, get_default_trace_provider

logger = logging.getLogger(__name__)
r = APIRouter()


def get_trace_storage_provider() -> TraceStorageProvider:
    """Dependency injection for trace storage provider."""
    return get_default_trace_provider()


def validate_trace_id(trace_id: str) -> None:
    """
    Validate that trace_id is a valid UUID format.

    Args:
        trace_id: The trace ID to validate

    Raises:
        HTTPException: If trace_id is not a valid UUID
    """
    try:
        # Attempt to parse as UUID to validate format
        uuid.UUID(trace_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": f"Invalid trace ID format: {trace_id}",
                "field": "trace_id",
                "value": trace_id,
            },
        )


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> str:
    """
    Simple API key authentication for trace endpoints.
    Uses the same pattern as main.py but returns the key for logging.
    """
    try:
        from config.env import get as env_get

        expected_key = env_get("LUKHAS_API_KEY", "")
    except ImportError:
        import os

        expected_key = os.getenv("LUKHAS_API_KEY", "")

    if expected_key and x_api_key != expected_key:
        logger.warning(f"Unauthorized trace access attempt from API key: {x_api_key}")
        raise HTTPException(
            status_code=401,
            detail={"error": "unauthorized", "message": "Invalid or missing API key"},
        )
    return x_api_key or "no-key-required"


# Health check for trace subsystem
@r.get(
    "/v1/matriz/trace/health",
    summary="Trace system health check",
    description="Check if the trace storage provider is functioning properly",
)
async def trace_health(storage: TraceStorageProvider = Depends(get_trace_storage_provider)):
    """Health check endpoint for the trace subsystem."""
    try:
        health_data = await storage.health_check()
        status_code = 200 if health_data.get("status") == "healthy" else 503
        return JSONResponse(status_code=status_code, content=health_data)
    except Exception as e:
        logger.error(f"Trace health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


# Recent traces endpoint
@r.get(
    "/v1/matriz/trace/recent",
    response_model=list[ExecutionTraceResponse],
    summary="Get recent traces",
    description="Retrieve recent traces with optional filtering by level or tag",
)
async def get_recent_traces(
    limit: int = 10,
    level: Optional[int] = None,
    tag: Optional[str] = None,
    api_key: str = Depends(require_api_key),
    storage: TraceStorageProvider = Depends(get_trace_storage_provider),
) -> list[ExecutionTraceResponse]:
    """
    Retrieve recent traces with optional filtering.

    Args:
        limit: Maximum number of traces to return (default: 10, max: 100)
        level: Filter by trace level (0-7)
        tag: Filter by specific tag
        api_key: API key for authentication (from header)
        storage: Trace storage provider instance (injected)

    Returns:
        List of recent trace entries
    """
    try:
        # Limit the maximum number of traces to prevent resource issues
        limit = min(limit, 100)

        # Validate level if provided
        if level is not None and not (0 <= level <= 7):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Level must be between 0 and 7",
                    "field": "level",
                    "value": level,
                },
            )

        logger.info(f"Recent traces request: limit={limit}, level={level}, tag={tag}")

        # Get recent traces from storage
        traces_data = await storage.get_recent_traces(limit=limit, level=level, tag=tag)

        # Convert to response models
        responses = []
        for trace_data in traces_data:
            try:
                response = ExecutionTraceResponse(**trace_data)
                responses.append(response)
            except Exception as e:
                logger.warning(
                    f"Skipping malformed trace {trace_data.get('trace_id', 'unknown')}: {e}"
                )
                continue

        logger.info(f"Returning {len(responses)} recent traces")
        return responses

    except HTTPException:
        # Re-raise HTTP exceptions (validation, auth errors)
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error retrieving recent traces: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An internal error occurred while retrieving recent traces",
                "error_type": type(e).__name__,
            },
        )


@r.get(
    "/v1/matriz/trace/{trace_id}",
    response_model=ExecutionTraceResponse,
    responses={
        200: {
            "description": "Trace found and returned successfully",
            "model": ExecutionTraceResponse,
        },
        400: {"description": "Invalid trace ID format", "model": TraceValidationErrorResponse},
        401: {"description": "Unauthorized - invalid API key", "model": TraceErrorResponse},
        404: {"description": "Trace not found", "model": TraceNotFoundResponse},
        500: {"description": "Internal server error", "model": TraceErrorResponse},
    },
    summary="Get trace by ID",
    description="Retrieve a specific trace by its unique identifier. Requires valid API key if configured.",
)
async def get_trace(
    trace_id: str,
    api_key: str = Depends(require_api_key),
    storage: TraceStorageProvider = Depends(get_trace_storage_provider),
) -> Union[ExecutionTraceResponse, JSONResponse]:
    """
    Retrieve a trace by its unique identifier.

    This endpoint integrates with the TraceStorageProvider to provide structured access
    to trace data with proper error handling and authentication.

    Args:
        trace_id: UUID of the trace to retrieve
        api_key: API key for authentication (from header)
        storage: Trace storage provider instance (injected)

    Returns:
        ExecutionTraceResponse: The trace data if found

    Raises:
        HTTPException: For various error conditions (400, 401, 404, 500)
    """
    # Validate trace ID format
    validate_trace_id(trace_id)

    try:
        # Log the API request
        logger.info(f"Trace lookup request for ID: {trace_id}")

        # Attempt to retrieve the trace using storage provider
        trace_data = await storage.get_trace_by_id(trace_id)

        if trace_data is None:
            # Trace not found
            logger.info(f"Trace not found: {trace_id}")
            error_response = TraceNotFoundResponse(
                message=f"No trace found with ID: {trace_id}", trace_id=trace_id
            )
            return JSONResponse(status_code=404, content=error_response.model_dump())

        # Convert to enhanced response model
        # Use ExecutionTraceResponse for better compatibility with enhanced fields
        try:
            response = ExecutionTraceResponse(**trace_data)
        except Exception:
            # Fallback to basic TraceResponse if extra fields cause issues
            basic_fields = {k: v for k, v in trace_data.items() if k in TraceResponse.__fields__}
            response = ExecutionTraceResponse(**basic_fields)

        logger.info(f"Trace retrieved successfully: {trace_id}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions (validation, auth errors)
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error retrieving trace {trace_id}: {e!s}", exc_info=True)

        error_response = TraceErrorResponse(
            error="internal_error",
            message="An internal error occurred while retrieving the trace",
            details={"trace_id": trace_id, "error_type": type(e).__name__},
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())


# include_router(r) in main app
