"""
Comprehensive test suite for serve.routes_traces module.

Tests all 3 endpoints (health, recent, get by ID) and 3 helper functions
(validate_trace_id, require_api_key, get_trace_storage_provider) with comprehensive coverage.

Following Test Surgeon canonical guidelines:
- Tests only (no production code changes)
- Deterministic (mocked time, dependencies, storage)
- Network-free (all external systems mocked)
- Comprehensive coverage (75%+ target)
"""
from typing import Any, Optional
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def mock_trace_data():
    """Create mock trace data."""
    return {
        "trace_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": 1730000000.0,
        "level": 3,
        "tags": ["api", "matrix"],
        "duration_ms": 125.5,
        "status": "completed",
        "metadata": {"user_id": "user_123"},
    }


@pytest.fixture
def mock_trace_storage():
    """
    Create mock TraceStorageProvider with pre-configured responses.
    """
    storage = mock.AsyncMock()

    # Mock health_check method
    storage.health_check.return_value = {
        "status": "healthy",
        "total_traces": 1000,
        "storage_type": "memory",
    }

    # Mock get_recent_traces method
    storage.get_recent_traces.return_value = [
        {
            "trace_id": f"trace_{i}",
            "timestamp": 1730000000.0 + i,
            "level": i % 8,
            "tags": ["test"],
            "duration_ms": 100.0,
            "status": "completed",
        }
        for i in range(10)
    ]

    # Mock get_trace_by_id method
    storage.get_trace_by_id.return_value = {
        "trace_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": 1730000000.0,
        "level": 3,
        "tags": ["api"],
        "duration_ms": 125.5,
        "status": "completed",
    }

    return storage


@pytest.fixture
def routes_traces_module(mock_trace_storage):
    """
    Import serve.routes_traces with mocked dependencies.
    """
    # Mock trace models
    mock_execution_trace = mock.MagicMock()
    mock_execution_trace.__fields__ = {
        "trace_id": None,
        "timestamp": None,
        "level": None,
        "tags": None,
        "duration_ms": None,
        "status": None,
    }

    mock_trace_response = mock.MagicMock()
    mock_trace_response.__fields__ = {
        "trace_id": None,
        "timestamp": None,
        "level": None,
    }

    with mock.patch.dict("sys.modules", {
        "serve.models": mock.MagicMock(),
        "serve.models.trace_models": mock.MagicMock(
            ExecutionTraceResponse=mock_execution_trace,
            TraceResponse=mock_trace_response,
            TraceErrorResponse=mock.MagicMock(),
            TraceNotFoundResponse=mock.MagicMock(),
            TraceValidationErrorResponse=mock.MagicMock(),
        ),
        "serve.storage": mock.MagicMock(),
        "serve.storage.trace_provider": mock.MagicMock(
            TraceStorageProvider=mock.MagicMock,
            get_default_trace_provider=lambda: mock_trace_storage,
        ),
        "config": mock.MagicMock(),
        "config.env": mock.MagicMock(),
    }):
        import importlib

        import serve.routes_traces as traces_module
        importlib.reload(traces_module)
        yield traces_module


@pytest.fixture
def test_app(routes_traces_module):
    """Create FastAPI test client with routes_traces module."""
    app = FastAPI()
    app.include_router(routes_traces_module.r)
    return TestClient(app)


# ==============================================================================
# Helper Function Tests: validate_trace_id
# ==============================================================================

def test_validate_trace_id_valid_uuid(routes_traces_module):
    """Test validate_trace_id accepts valid UUID."""
    valid_uuid = "550e8400-e29b-41d4-a716-446655440000"

    # Should not raise exception
    routes_traces_module.validate_trace_id(valid_uuid)


def test_validate_trace_id_invalid_format(routes_traces_module):
    """Test validate_trace_id rejects invalid UUID format."""
    invalid_uuid = "not-a-uuid"

    with pytest.raises(Exception):  # HTTPException
        routes_traces_module.validate_trace_id(invalid_uuid)


def test_validate_trace_id_empty_string(routes_traces_module):
    """Test validate_trace_id rejects empty string."""
    with pytest.raises(Exception):  # HTTPException
        routes_traces_module.validate_trace_id("")


def test_validate_trace_id_numeric_string(routes_traces_module):
    """Test validate_trace_id rejects numeric string."""
    with pytest.raises(Exception):  # HTTPException
        routes_traces_module.validate_trace_id("12345")


def test_validate_trace_id_uppercase_uuid(routes_traces_module):
    """Test validate_trace_id accepts uppercase UUID."""
    uppercase_uuid = "550E8400-E29B-41D4-A716-446655440000"

    # Should not raise exception
    routes_traces_module.validate_trace_id(uppercase_uuid)


# ==============================================================================
# Helper Function Tests: require_api_key
# ==============================================================================

def test_require_api_key_valid_key(routes_traces_module):
    """Test require_api_key accepts valid API key."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": "test-key-123"}):
        result = routes_traces_module.require_api_key(x_api_key="test-key-123")

    assert result == "test-key-123"


def test_require_api_key_no_key_required(routes_traces_module):
    """Test require_api_key when no API key is configured."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        result = routes_traces_module.require_api_key(x_api_key=None)

    assert result == "no-key-required"


def test_require_api_key_invalid_key(routes_traces_module):
    """Test require_api_key rejects invalid API key."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": "correct-key"}):
        with pytest.raises(Exception):  # HTTPException
            routes_traces_module.require_api_key(x_api_key="wrong-key")


def test_require_api_key_missing_header(routes_traces_module):
    """Test require_api_key rejects missing API key when required."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": "required-key"}):
        with pytest.raises(Exception):  # HTTPException
            routes_traces_module.require_api_key(x_api_key=None)


def test_require_api_key_uses_config_env(routes_traces_module):
    """Test require_api_key tries config.env before os.environ."""
    mock_env_get = mock.MagicMock(return_value="config-key")

    with mock.patch("serve.routes_traces.env_get", mock_env_get):
        result = routes_traces_module.require_api_key(x_api_key="config-key")

    assert result == "config-key"
    mock_env_get.assert_called_once_with("LUKHAS_API_KEY", "")


# ==============================================================================
# Helper Function Tests: get_trace_storage_provider
# ==============================================================================

def test_get_trace_storage_provider(routes_traces_module, mock_trace_storage):
    """Test get_trace_storage_provider returns storage instance."""
    provider = routes_traces_module.get_trace_storage_provider()

    assert provider == mock_trace_storage


# ==============================================================================
# Endpoint Tests: GET /v1/matriz/trace/health
# ==============================================================================

@pytest.mark.asyncio
async def test_trace_health_healthy(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/health when system is healthy."""
    response = test_app.get("/v1/matriz/trace/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_traces"] == 1000
    assert data["storage_type"] == "memory"


@pytest.mark.asyncio
async def test_trace_health_unhealthy(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/health when system is unhealthy."""
    mock_trace_storage.health_check.return_value = {
        "status": "unhealthy",
        "error": "Storage disconnected",
    }

    response = test_app.get("/v1/matriz/trace/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_trace_health_exception(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/health handles exceptions."""
    mock_trace_storage.health_check.side_effect = Exception("Connection timeout")

    response = test_app.get("/v1/matriz/trace/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert "Connection timeout" in data["error"]


# ==============================================================================
# Endpoint Tests: GET /v1/matriz/trace/recent
# ==============================================================================

@pytest.mark.asyncio
async def test_get_recent_traces_success(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/recent returns recent traces."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    mock_trace_storage.get_recent_traces.assert_called_once()


@pytest.mark.asyncio
async def test_get_recent_traces_with_level_filter(
    test_app, mock_trace_storage
):
    """Test GET /v1/matriz/trace/recent with level filter."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent?limit=10&level=3")

    assert response.status_code == 200
    mock_trace_storage.get_recent_traces.assert_called_once_with(
        limit=10, level=3, tag=None
    )


@pytest.mark.asyncio
async def test_get_recent_traces_with_tag_filter(
    test_app, mock_trace_storage
):
    """Test GET /v1/matriz/trace/recent with tag filter."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent?limit=10&tag=api")

    assert response.status_code == 200
    mock_trace_storage.get_recent_traces.assert_called_once_with(
        limit=10, level=None, tag="api"
    )


@pytest.mark.asyncio
async def test_get_recent_traces_limit_cap(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/recent caps limit at 100."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent?limit=500")

    assert response.status_code == 200
    # Should cap at 100
    mock_trace_storage.get_recent_traces.assert_called_once_with(
        limit=100, level=None, tag=None
    )


@pytest.mark.asyncio
async def test_get_recent_traces_invalid_level_low(test_app):
    """Test GET /v1/matriz/trace/recent rejects level below 0."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent?level=-1")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "validation_error" in str(data["detail"])


@pytest.mark.asyncio
async def test_get_recent_traces_invalid_level_high(test_app):
    """Test GET /v1/matriz/trace/recent rejects level above 7."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent?level=8")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_recent_traces_malformed_trace_tolerance(
    test_app, mock_trace_storage
):
    """Test GET /v1/matriz/trace/recent tolerates malformed traces."""
    # Mix valid and malformed traces
    mock_trace_storage.get_recent_traces.return_value = [
        {"trace_id": "valid_1", "timestamp": 1730000000.0, "level": 1},
        {"trace_id": "malformed", "invalid_field": "breaks validation"},
        {"trace_id": "valid_2", "timestamp": 1730000001.0, "level": 2},
    ]

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent")

    assert response.status_code == 200
    # Should skip malformed trace and return 2 valid ones
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_recent_traces_storage_error(
    test_app, mock_trace_storage
):
    """Test GET /v1/matriz/trace/recent handles storage errors."""
    mock_trace_storage.get_recent_traces.side_effect = Exception(
        "Storage unavailable"
    )

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get("/v1/matriz/trace/recent")

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_recent_traces_requires_auth(test_app):
    """Test GET /v1/matriz/trace/recent requires authentication."""
    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": "required-key"}):
        response = test_app.get("/v1/matriz/trace/recent")

    assert response.status_code == 401


# ==============================================================================
# Endpoint Tests: GET /v1/matriz/trace/{trace_id}
# ==============================================================================

@pytest.mark.asyncio
async def test_get_trace_success(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/{trace_id} returns trace."""
    trace_id = "550e8400-e29b-41d4-a716-446655440000"

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get(f"/v1/matriz/trace/{trace_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["trace_id"] == trace_id
    mock_trace_storage.get_trace_by_id.assert_called_once_with(trace_id)


@pytest.mark.asyncio
async def test_get_trace_not_found(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/{trace_id} when trace not found."""
    trace_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_trace_storage.get_trace_by_id.return_value = None

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get(f"/v1/matriz/trace/{trace_id}")

    assert response.status_code == 404
    data = response.json()
    assert trace_id in data["message"]


@pytest.mark.asyncio
async def test_get_trace_invalid_uuid_format(test_app):
    """Test GET /v1/matriz/trace/{trace_id} with invalid UUID."""
    invalid_id = "not-a-uuid"

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get(f"/v1/matriz/trace/{invalid_id}")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid trace ID format" in str(data["detail"])


@pytest.mark.asyncio
async def test_get_trace_fallback_to_basic_response(
    test_app, mock_trace_storage
):
    """Test GET /v1/matriz/trace/{trace_id} falls back on parse errors."""
    trace_id = "550e8400-e29b-41d4-a716-446655440000"

    # Return data that fails ExecutionTraceResponse validation
    mock_trace_storage.get_trace_by_id.return_value = {
        "trace_id": trace_id,
        "timestamp": 1730000000.0,
        "level": 3,
        "extra_field_that_breaks_validation": "value",
    }

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get(f"/v1/matriz/trace/{trace_id}")

    # Should succeed with fallback
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_trace_storage_error(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/{trace_id} handles storage errors."""
    trace_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_trace_storage.get_trace_by_id.side_effect = Exception(
        "Database connection failed"
    )

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get(f"/v1/matriz/trace/{trace_id}")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"] == "internal_error"


@pytest.mark.asyncio
async def test_get_trace_requires_auth(test_app):
    """Test GET /v1/matriz/trace/{trace_id} requires authentication."""
    trace_id = "550e8400-e29b-41d4-a716-446655440000"

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": "required-key"}):
        response = test_app.get(f"/v1/matriz/trace/{trace_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_trace_uppercase_uuid(test_app, mock_trace_storage):
    """Test GET /v1/matriz/trace/{trace_id} accepts uppercase UUID."""
    trace_id = "550E8400-E29B-41D4-A716-446655440000"

    with mock.patch.dict("os.environ", {"LUKHAS_API_KEY": ""}):
        response = test_app.get(f"/v1/matriz/trace/{trace_id}")

    assert response.status_code == 200


# ==============================================================================
# Integration Tests
# ==============================================================================

def test_router_exports(routes_traces_module):
    """Test that routes_traces module exports router correctly."""
    assert hasattr(routes_traces_module, "r")
    assert routes_traces_module.r is not None


def test_router_has_endpoints(routes_traces_module):
    """Test that router has expected endpoints."""
    routes = [route.path for route in routes_traces_module.r.routes]

    assert "/v1/matriz/trace/health" in routes
    assert "/v1/matriz/trace/recent" in routes
    assert "/v1/matriz/trace/{trace_id}" in routes


def test_all_endpoints_documented(routes_traces_module):
    """Test that all endpoints have summary and description."""
    for route in routes_traces_module.r.routes:
        if hasattr(route, "summary"):
            assert route.summary is not None
            assert route.description is not None
