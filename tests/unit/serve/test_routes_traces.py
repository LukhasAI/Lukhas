"""
Comprehensive unit tests for serve/routes_traces.py

Tests trace API endpoints including:
- Health check
- Recent traces with filtering
- Get trace by ID
- API key authentication
- Validation and error handling
"""

import uuid
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from serve.routes_traces import (
    get_recent_traces,
    get_trace,
    get_trace_storage_provider,
    require_api_key,
    trace_health,
    validate_trace_id,
)


class MockTraceStorageProvider:
    """Mock storage provider for testing."""

    def __init__(self):
        self.traces = {}
        self.recent_traces = []
        self.health_status = {"status": "healthy"}

    async def get_trace_by_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Mock get trace by ID."""
        return self.traces.get(trace_id)

    async def get_recent_traces(
        self,
        limit: int = 10,
        level: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mock get recent traces with filtering."""
        traces = self.recent_traces.copy()

        # Apply filters
        if level is not None:
            traces = [t for t in traces if t.get("level") == level]
        if tag is not None:
            traces = [t for t in traces if tag in t.get("tags", [])]

        return traces[:limit]

    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return self.health_status


@pytest.fixture
def mock_storage():
    """Fixture providing a mock storage provider."""
    return MockTraceStorageProvider()


@pytest.fixture
def sample_trace():
    """Fixture providing a sample trace."""
    return {
        "trace_id": str(uuid.uuid4()),
        "timestamp": "2025-01-10T12:00:00Z",
        "unix_time": 1704888000.0,
        "level": 3,
        "level_name": "INFO",
        "message": "Test trace message",
        "source_component": "test_component",
        "tags": ["test", "sample"],
        "metadata": {"test_key": "test_value"},
        "emotional": {"valence": 0.5},
        "ethical_score": 0.9,
    }


@pytest.fixture
def sample_execution_trace():
    """Fixture providing a sample execution trace with full context."""
    return {
        "trace_id": str(uuid.uuid4()),
        "timestamp": "2025-01-10T12:00:00Z",
        "unix_time": 1704888000.0,
        "level": 3,
        "level_name": "INFO",
        "message": "Test execution trace",
        "source_component": "test_component",
        "tags": ["execution", "test"],
        "metadata": {"test_key": "test_value"},
        "emotional": {"valence": 0.5},
        "ethical_score": 0.9,
        "execution_context": {"env": "test"},
        "performance_metrics": {"duration_ms": 123.45},
        "related_traces": ["trace-1", "trace-2"],
    }


class TestValidateTraceId:
    """Test trace ID validation."""

    def test_valid_uuid_passes(self):
        """Test that valid UUID format passes validation."""
        valid_id = str(uuid.uuid4())
        validate_trace_id(valid_id)  # Should not raise

    def test_invalid_uuid_raises_http_exception(self):
        """Test that invalid UUID format raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_trace_id("not-a-uuid")

        assert exc_info.value.status_code == 400
        assert "validation_error" in str(exc_info.value.detail)

    def test_empty_string_raises_http_exception(self):
        """Test that empty string raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_trace_id("")

        assert exc_info.value.status_code == 400

    def test_error_detail_contains_invalid_value(self):
        """Test that error detail includes the invalid value."""
        invalid_id = "invalid-123"
        with pytest.raises(HTTPException) as exc_info:
            validate_trace_id(invalid_id)

        detail = exc_info.value.detail
        assert detail["value"] == invalid_id
        assert detail["field"] == "trace_id"


class TestRequireApiKey:
    """Test API key authentication."""

    def test_no_api_key_configured_allows_any_key(self):
        """Test that when no API key is configured, any key is accepted."""
        with patch("serve.routes_traces.env_get", return_value=""):
            result = require_api_key("any-key")
            assert result == "any-key"

    def test_no_api_key_configured_allows_no_key(self):
        """Test that when no API key is configured, no key is accepted."""
        with patch("serve.routes_traces.env_get", return_value=""):
            result = require_api_key(None)
            assert result == "no-key-required"

    def test_valid_api_key_passes(self):
        """Test that valid API key passes authentication."""
        with patch("serve.routes_traces.env_get", return_value="secret-key"):
            result = require_api_key("secret-key")
            assert result == "secret-key"

    def test_invalid_api_key_raises_http_exception(self):
        """Test that invalid API key raises HTTPException."""
        with patch("serve.routes_traces.env_get", return_value="secret-key"):
            with pytest.raises(HTTPException) as exc_info:
                require_api_key("wrong-key")

            assert exc_info.value.status_code == 401
            assert "unauthorized" in str(exc_info.value.detail)

    def test_missing_api_key_when_required_raises_http_exception(self):
        """Test that missing API key raises HTTPException when one is required."""
        with patch("serve.routes_traces.env_get", return_value="secret-key"):
            with pytest.raises(HTTPException) as exc_info:
                require_api_key(None)

            assert exc_info.value.status_code == 401

    def test_import_error_fallback_to_os_getenv(self):
        """Test fallback to os.getenv when config.env import fails."""
        with patch("serve.routes_traces.env_get", side_effect=ImportError):
            with patch("os.getenv", return_value="secret-key"):
                result = require_api_key("secret-key")
                assert result == "secret-key"


class TestTraceHealth:
    """Test trace health check endpoint."""

    @pytest.mark.asyncio
    async def test_healthy_status_returns_200(self, mock_storage):
        """Test that healthy storage returns 200 status."""
        mock_storage.health_status = {"status": "healthy"}
        response = await trace_health(storage=mock_storage)

        assert response.status_code == 200
        assert response.body.decode() == '{"status":"healthy"}'

    @pytest.mark.asyncio
    async def test_unhealthy_status_returns_503(self, mock_storage):
        """Test that unhealthy storage returns 503 status."""
        mock_storage.health_status = {"status": "unhealthy"}
        response = await trace_health(storage=mock_storage)

        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_exception_returns_503_with_error(self, mock_storage):
        """Test that exceptions return 503 with error details."""
        mock_storage.health_check = AsyncMock(side_effect=Exception("Test error"))
        response = await trace_health(storage=mock_storage)

        assert response.status_code == 503
        body = response.body.decode()
        assert "unhealthy" in body
        assert "Test error" in body

    @pytest.mark.asyncio
    async def test_uses_default_storage_when_none_provided(self):
        """Test that default storage is used when none provided."""
        with patch("serve.routes_traces.get_trace_storage_provider") as mock_get:
            mock_provider = MockTraceStorageProvider()
            mock_get.return_value = mock_provider
            response = await trace_health(storage=None)

            assert response.status_code == 200


class TestGetRecentTraces:
    """Test get recent traces endpoint."""

    @pytest.mark.asyncio
    async def test_get_recent_traces_default_limit(self, mock_storage, sample_trace):
        """Test getting recent traces with default limit."""
        mock_storage.recent_traces = [sample_trace]

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=50,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert len(traces) == 1
        assert traces[0].trace_id == sample_trace["trace_id"]

    @pytest.mark.asyncio
    async def test_limit_capped_at_100(self, mock_storage):
        """Test that limit is capped at maximum of 100."""
        # Create 150 traces
        mock_storage.recent_traces = [
            {
                "trace_id": str(uuid.uuid4()),
                "timestamp": "2025-01-10T12:00:00Z",
                "unix_time": 1704888000.0,
                "level": 3,
                "level_name": "INFO",
                "message": f"Trace {i}",
                "source_component": "test",
                "tags": [],
            }
            for i in range(150)
        ]

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=150,
                _api_key="test-key",
                storage=mock_storage,
            )

        # Should return max 100
        assert len(traces) <= 100

    @pytest.mark.asyncio
    async def test_filter_by_level(self, mock_storage):
        """Test filtering traces by level."""
        mock_storage.recent_traces = [
            {
                "trace_id": str(uuid.uuid4()),
                "timestamp": "2025-01-10T12:00:00Z",
                "unix_time": 1704888000.0,
                "level": 3,
                "level_name": "INFO",
                "message": "Info message",
                "source_component": "test",
                "tags": [],
            },
            {
                "trace_id": str(uuid.uuid4()),
                "timestamp": "2025-01-10T12:00:01Z",
                "unix_time": 1704888001.0,
                "level": 5,
                "level_name": "ERROR",
                "message": "Error message",
                "source_component": "test",
                "tags": [],
            },
        ]

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=50,
                level=3,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert len(traces) == 1
        assert traces[0].level == 3

    @pytest.mark.asyncio
    async def test_filter_by_tag(self, mock_storage):
        """Test filtering traces by tag."""
        mock_storage.recent_traces = [
            {
                "trace_id": str(uuid.uuid4()),
                "timestamp": "2025-01-10T12:00:00Z",
                "unix_time": 1704888000.0,
                "level": 3,
                "level_name": "INFO",
                "message": "Tagged message",
                "source_component": "test",
                "tags": ["important"],
            },
            {
                "trace_id": str(uuid.uuid4()),
                "timestamp": "2025-01-10T12:00:01Z",
                "unix_time": 1704888001.0,
                "level": 3,
                "level_name": "INFO",
                "message": "Untagged message",
                "source_component": "test",
                "tags": [],
            },
        ]

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=50,
                tag="important",
                _api_key="test-key",
                storage=mock_storage,
            )

        assert len(traces) == 1
        assert "important" in traces[0].tags

    @pytest.mark.asyncio
    async def test_invalid_level_raises_http_exception(self, mock_storage):
        """Test that invalid level raises HTTPException."""
        with patch("serve.routes_traces.env_get", return_value=""):
            with pytest.raises(HTTPException) as exc_info:
                await get_recent_traces(
                    limit=50,
                    level=10,  # Invalid: must be 0-7
                    _api_key="test-key",
                    storage=mock_storage,
                )

            assert exc_info.value.status_code == 400
            assert "validation_error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_negative_level_raises_http_exception(self, mock_storage):
        """Test that negative level raises HTTPException."""
        with patch("serve.routes_traces.env_get", return_value=""):
            with pytest.raises(HTTPException) as exc_info:
                await get_recent_traces(
                    limit=50,
                    level=-1,
                    _api_key="test-key",
                    storage=mock_storage,
                )

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_malformed_trace_skipped(self, mock_storage):
        """Test that malformed traces are skipped gracefully."""
        mock_storage.recent_traces = [
            {"trace_id": "invalid"},  # Missing required fields
            {
                "trace_id": str(uuid.uuid4()),
                "timestamp": "2025-01-10T12:00:00Z",
                "unix_time": 1704888000.0,
                "level": 3,
                "level_name": "INFO",
                "message": "Valid message",
                "source_component": "test",
                "tags": [],
            },
        ]

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=50,
                _api_key="test-key",
                storage=mock_storage,
            )

        # Should only return the valid trace
        assert len(traces) == 1

    @pytest.mark.asyncio
    async def test_storage_exception_raises_http_exception(self, mock_storage):
        """Test that storage exceptions are converted to HTTPException."""
        mock_storage.get_recent_traces = AsyncMock(
            side_effect=Exception("Storage error")
        )

        with patch("serve.routes_traces.env_get", return_value=""):
            with pytest.raises(HTTPException) as exc_info:
                await get_recent_traces(
                    limit=50,
                    _api_key="test-key",
                    storage=mock_storage,
                )

            assert exc_info.value.status_code == 500
            assert "internal_error" in str(exc_info.value.detail)


class TestGetTrace:
    """Test get trace by ID endpoint."""

    @pytest.mark.asyncio
    async def test_get_existing_trace(self, mock_storage, sample_trace):
        """Test retrieving an existing trace."""
        trace_id = sample_trace["trace_id"]
        mock_storage.traces[trace_id] = sample_trace

        with patch("serve.routes_traces.env_get", return_value=""):
            result = await get_trace(
                trace_id=trace_id,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert result.trace_id == trace_id
        assert result.message == sample_trace["message"]

    @pytest.mark.asyncio
    async def test_get_execution_trace(self, mock_storage, sample_execution_trace):
        """Test retrieving an execution trace with full context."""
        trace_id = sample_execution_trace["trace_id"]
        mock_storage.traces[trace_id] = sample_execution_trace

        with patch("serve.routes_traces.env_get", return_value=""):
            result = await get_trace(
                trace_id=trace_id,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert result.trace_id == trace_id
        assert result.execution_context == sample_execution_trace["execution_context"]
        assert result.performance_metrics == sample_execution_trace["performance_metrics"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_trace_returns_404(self, mock_storage):
        """Test that nonexistent trace returns 404 response."""
        trace_id = str(uuid.uuid4())

        with patch("serve.routes_traces.env_get", return_value=""):
            result = await get_trace(
                trace_id=trace_id,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert result.status_code == 404
        body = result.body.decode()
        assert "trace_not_found" in body
        assert trace_id in body

    @pytest.mark.asyncio
    async def test_invalid_trace_id_raises_http_exception(self, mock_storage):
        """Test that invalid trace ID format raises HTTPException."""
        with patch("serve.routes_traces.env_get", return_value=""):
            with pytest.raises(HTTPException) as exc_info:
                await get_trace(
                    trace_id="not-a-uuid",
                    _api_key="test-key",
                    storage=mock_storage,
                )

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_trace_with_extra_fields_uses_fallback(self, mock_storage):
        """Test that trace with incompatible extra fields falls back gracefully."""
        trace_id = str(uuid.uuid4())
        trace_data = {
            "trace_id": trace_id,
            "timestamp": "2025-01-10T12:00:00Z",
            "unix_time": 1704888000.0,
            "level": 3,
            "level_name": "INFO",
            "message": "Test message",
            "source_component": "test",
            "tags": [],
            "invalid_field": "should be ignored",
        }
        mock_storage.traces[trace_id] = trace_data

        # Mock ExecutionTraceResponse to raise exception
        with patch("serve.routes_traces.env_get", return_value=""):
            with patch("serve.routes_traces.ExecutionTraceResponse") as mock_response:
                mock_response.side_effect = [
                    Exception("Invalid field"),
                    MagicMock(trace_id=trace_id),
                ]
                mock_response.__fields__ = {}

                with patch("serve.routes_traces.TraceResponse") as mock_basic:
                    mock_basic.__fields__ = {
                        "trace_id": None,
                        "timestamp": None,
                        "unix_time": None,
                        "level": None,
                        "level_name": None,
                        "message": None,
                        "source_component": None,
                        "tags": None,
                    }

                    result = await get_trace(
                        trace_id=trace_id,
                        _api_key="test-key",
                        storage=mock_storage,
                    )

                    # Should successfully return using fallback
                    assert result is not None

    @pytest.mark.asyncio
    async def test_storage_exception_returns_500(self, mock_storage):
        """Test that storage exceptions return 500 error response."""
        trace_id = str(uuid.uuid4())
        mock_storage.get_trace_by_id = AsyncMock(
            side_effect=Exception("Storage error")
        )

        with patch("serve.routes_traces.env_get", return_value=""):
            result = await get_trace(
                trace_id=trace_id,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert result.status_code == 500
        body = result.body.decode()
        assert "internal_error" in body


class TestGetTraceStorageProvider:
    """Test trace storage provider dependency injection."""

    def test_returns_storage_provider(self):
        """Test that get_trace_storage_provider returns a provider instance."""
        with patch("serve.routes_traces.get_default_trace_provider") as mock_get:
            mock_provider = MockTraceStorageProvider()
            mock_get.return_value = mock_provider

            provider = get_trace_storage_provider()
            assert provider == mock_provider


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_traces_list(self, mock_storage):
        """Test handling of empty traces list."""
        mock_storage.recent_traces = []

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=50,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert traces == []

    @pytest.mark.asyncio
    async def test_zero_limit(self, mock_storage, sample_trace):
        """Test handling of zero limit."""
        mock_storage.recent_traces = [sample_trace]

        with patch("serve.routes_traces.env_get", return_value=""):
            traces = await get_recent_traces(
                limit=0,
                _api_key="test-key",
                storage=mock_storage,
            )

        assert traces == []

    @pytest.mark.asyncio
    async def test_level_boundary_values(self, mock_storage, sample_trace):
        """Test level boundary values 0 and 7."""
        for level in [0, 7]:
            sample_trace["level"] = level
            mock_storage.recent_traces = [sample_trace]

            with patch("serve.routes_traces.env_get", return_value=""):
                traces = await get_recent_traces(
                    limit=50,
                    level=level,
                    _api_key="test-key",
                    storage=mock_storage,
                )

            assert len(traces) >= 0  # Should not raise
