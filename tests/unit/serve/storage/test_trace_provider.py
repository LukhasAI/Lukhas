"""
Comprehensive test suite for serve/storage/trace_provider.py

Tests trace storage provider interface and implementations:
- Abstract TraceStorageProvider interface
- FileTraceStorageProvider implementation
- TraceMemoryLogger integration
- Health check functionality
- Factory functions
- Default provider singleton
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.fixture
def mock_trace_logger():
    """Mock TraceMemoryLogger."""
    mock_logger = MagicMock()

    # Mock trace retrieval
    mock_trace = {
        "trace_id": "trace_123",
        "timestamp": 1730000000.0,
        "level": 1,
        "message": "Test trace",
        "tags": ["test"],
    }
    mock_logger.get_trace_by_id.return_value = mock_trace

    # Mock recent traces
    mock_recent = [
        {"trace_id": f"trace_{i}", "message": f"Message {i}", "level": 1}
        for i in range(5)
    ]
    mock_logger.get_recent_traces.return_value = mock_recent
    mock_logger.recent_traces = mock_recent

    return mock_logger


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary storage directory."""
    storage_dir = tmp_path / "test_traces"
    storage_dir.mkdir()
    return str(storage_dir)


class TestTraceStorageProvider:
    """Test abstract TraceStorageProvider interface."""

    def test_abstract_interface(self):
        """Test TraceStorageProvider is abstract."""
        from serve.storage.trace_provider import TraceStorageProvider

        # Should not be able to instantiate abstract class
        with pytest.raises(TypeError):
            TraceStorageProvider()

    def test_interface_methods(self):
        """Test interface defines required methods."""
        from serve.storage.trace_provider import TraceStorageProvider

        # Check abstract methods exist
        assert hasattr(TraceStorageProvider, "get_trace_by_id")
        assert hasattr(TraceStorageProvider, "get_recent_traces")
        assert hasattr(TraceStorageProvider, "health_check")


class TestFileTraceStorageProvider:
    """Test FileTraceStorageProvider implementation."""

    def test_initialization_default_location(self):
        """Test provider initialization with default location."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        provider = FileTraceStorageProvider()

        assert provider.storage_location == "var/traces/"
        assert provider._trace_logger is None

    def test_initialization_custom_location(self, temp_storage):
        """Test provider initialization with custom location."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        provider = FileTraceStorageProvider(storage_location=temp_storage)

        assert provider.storage_location == temp_storage

    def test_initialization_creates_directory(self, tmp_path):
        """Test provider creates storage directory."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        storage_path = str(tmp_path / "new_traces")
        assert not os.path.exists(storage_path)

        provider = FileTraceStorageProvider(storage_location=storage_path)

        assert os.path.exists(storage_path)
        assert os.path.isdir(storage_path)

    def test_get_trace_logger_lazy_initialization(self, temp_storage):
        """Test TraceMemoryLogger is lazily initialized."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger") as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            provider = FileTraceStorageProvider(storage_location=temp_storage)

            # Should not be initialized yet
            assert provider._trace_logger is None

            # Call method that uses logger
            logger = provider._get_trace_logger()

            # Should now be initialized
            assert logger == mock_logger
            mock_logger_class.assert_called_once()

    def test_get_trace_logger_singleton(self, temp_storage):
        """Test TraceMemoryLogger is singleton per provider."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger") as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            provider = FileTraceStorageProvider(storage_location=temp_storage)

            logger1 = provider._get_trace_logger()
            logger2 = provider._get_trace_logger()

            # Should be same instance
            assert logger1 == logger2
            # Should only be called once
            mock_logger_class.assert_called_once()

    def test_get_trace_logger_configuration(self, temp_storage):
        """Test TraceMemoryLogger is configured correctly."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger") as mock_logger_class:
            provider = FileTraceStorageProvider(storage_location=temp_storage)
            provider._get_trace_logger()

            # Check config passed to TraceMemoryLogger
            call_kwargs = mock_logger_class.call_args.kwargs
            assert "config" in call_kwargs

            config = call_kwargs["config"]
            assert config["log_dir"] == temp_storage
            assert config["recent_traces_limit"] == 200

    def test_get_trace_logger_import_error(self, temp_storage):
        """Test error when TraceMemoryLogger not available."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", None):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            with pytest.raises(ImportError) as exc_info:
                provider._get_trace_logger()

            assert "TraceMemoryLogger not available" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_trace_by_id_success(self, temp_storage, mock_trace_logger):
        """Test successful trace retrieval by ID."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            trace = await provider.get_trace_by_id("trace_123")

            assert trace is not None
            assert trace["trace_id"] == "trace_123"
            assert trace["message"] == "Test trace"

            mock_trace_logger.get_trace_by_id.assert_called_once_with("trace_123")

    @pytest.mark.asyncio
    async def test_get_trace_by_id_not_found(self, temp_storage, mock_trace_logger):
        """Test trace retrieval when not found."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        mock_trace_logger.get_trace_by_id.return_value = None

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            trace = await provider.get_trace_by_id("nonexistent")

            assert trace is None

    @pytest.mark.asyncio
    async def test_get_trace_by_id_error(self, temp_storage, mock_trace_logger):
        """Test error handling in trace retrieval."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        mock_trace_logger.get_trace_by_id.side_effect = Exception("Retrieval error")

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            with pytest.raises(Exception) as exc_info:
                await provider.get_trace_by_id("trace_123")

            assert "Retrieval error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_recent_traces_success(self, temp_storage, mock_trace_logger):
        """Test successful recent traces retrieval."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            traces = await provider.get_recent_traces(limit=10)

            assert len(traces) == 5
            assert all("trace_id" in t for t in traces)

            mock_trace_logger.get_recent_traces.assert_called_once_with(
                limit=10, level=None, tag=None
            )

    @pytest.mark.asyncio
    async def test_get_recent_traces_with_filters(self, temp_storage, mock_trace_logger):
        """Test recent traces retrieval with filters."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            traces = await provider.get_recent_traces(limit=5, level=2, tag="test_tag")

            mock_trace_logger.get_recent_traces.assert_called_once_with(
                limit=5, level=2, tag="test_tag"
            )

    @pytest.mark.asyncio
    async def test_get_recent_traces_error(self, temp_storage, mock_trace_logger):
        """Test error handling in recent traces retrieval."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        mock_trace_logger.get_recent_traces.side_effect = Exception("Query error")

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            with pytest.raises(Exception) as exc_info:
                await provider.get_recent_traces()

            assert "Query error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, temp_storage, mock_trace_logger):
        """Test health check when system is healthy."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        # Create traces file
        traces_file = os.path.join(temp_storage, "all_traces.jsonl")
        Path(traces_file).touch()

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            health = await provider.health_check()

            assert health["status"] == "healthy"
            assert health["storage_location"] == temp_storage
            assert health["storage_accessible"] is True
            assert health["traces_file_exists"] is True
            assert health["recent_traces_count"] == 5
            assert health["trace_logger_initialized"] is True

    @pytest.mark.asyncio
    async def test_health_check_missing_traces_file(self, temp_storage, mock_trace_logger):
        """Test health check when traces file doesn't exist."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            health = await provider.health_check()

            assert health["storage_accessible"] is True
            assert health["traces_file_exists"] is False

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, temp_storage, mock_trace_logger):
        """Test health check when system is unhealthy."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_trace_logger):
            with patch("os.path.isdir", return_value=False):
                provider = FileTraceStorageProvider(storage_location=temp_storage)

                health = await provider.health_check()

                assert health["status"] == "unhealthy"
                assert health["storage_accessible"] is False

    @pytest.mark.asyncio
    async def test_health_check_error(self, temp_storage):
        """Test health check error handling."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", side_effect=Exception("Init error")):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            health = await provider.health_check()

            assert health["status"] == "unhealthy"
            assert "error" in health
            assert "Init error" in health["error"]
            assert health["trace_logger_initialized"] is False


class TestCreateTraceStorageProvider:
    """Test create_trace_storage_provider factory function."""

    def test_create_file_provider_default(self):
        """Test creating file provider with defaults."""
        from serve.storage.trace_provider import create_trace_storage_provider

        provider = create_trace_storage_provider(provider_type="file")

        assert provider is not None
        assert provider.storage_location == "var/traces/"

    def test_create_file_provider_custom_location(self, temp_storage):
        """Test creating file provider with custom location."""
        from serve.storage.trace_provider import create_trace_storage_provider

        provider = create_trace_storage_provider(
            provider_type="file",
            storage_location=temp_storage,
        )

        assert provider.storage_location == temp_storage

    def test_create_unsupported_provider(self):
        """Test error on unsupported provider type."""
        from serve.storage.trace_provider import create_trace_storage_provider

        with pytest.raises(ValueError) as exc_info:
            create_trace_storage_provider(provider_type="unsupported")

        assert "Unsupported storage provider type" in str(exc_info.value)

    def test_create_provider_ignores_extra_kwargs(self):
        """Test factory ignores unexpected kwargs."""
        from serve.storage.trace_provider import create_trace_storage_provider

        # Should not raise error
        provider = create_trace_storage_provider(
            provider_type="file",
            unknown_param="value",
        )

        assert provider is not None


class TestDefaultTraceProvider:
    """Test default trace provider singleton."""

    def test_get_default_provider(self):
        """Test getting default provider."""
        from serve.storage.trace_provider import get_default_trace_provider

        with patch.dict("os.environ", {"LUKHAS_TRACE_STORAGE": "test_location"}):
            provider = get_default_trace_provider()

            assert provider is not None
            assert provider.storage_location == "test_location"

    def test_get_default_provider_env_default(self):
        """Test default provider uses env variable."""
        from serve.storage.trace_provider import (
            get_default_trace_provider,
            reset_default_trace_provider,
        )

        reset_default_trace_provider()

        with patch.dict("os.environ", {}, clear=True):
            with patch("os.getenv", return_value="var/traces/"):
                provider = get_default_trace_provider()

                assert provider.storage_location == "var/traces/"

    def test_get_default_provider_singleton(self):
        """Test default provider is singleton."""
        from serve.storage.trace_provider import (
            get_default_trace_provider,
            reset_default_trace_provider,
        )

        reset_default_trace_provider()

        provider1 = get_default_trace_provider()
        provider2 = get_default_trace_provider()

        assert provider1 is provider2

    def test_reset_default_provider(self):
        """Test resetting default provider."""
        from serve.storage.trace_provider import (
            get_default_trace_provider,
            reset_default_trace_provider,
        )

        provider1 = get_default_trace_provider()
        reset_default_trace_provider()
        provider2 = get_default_trace_provider()

        # Should be different instances after reset
        assert provider1 is not provider2


class TestProviderIntegration:
    """Test provider integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_storage):
        """Test complete workflow: create, retrieve, health check."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        mock_logger = MagicMock()
        mock_trace = {"trace_id": "test_123", "message": "Test"}
        mock_logger.get_trace_by_id.return_value = mock_trace
        mock_logger.get_recent_traces.return_value = [mock_trace]
        mock_logger.recent_traces = [mock_trace]

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            # Get trace by ID
            trace = await provider.get_trace_by_id("test_123")
            assert trace["trace_id"] == "test_123"

            # Get recent traces
            traces = await provider.get_recent_traces(limit=10)
            assert len(traces) == 1

            # Health check
            health = await provider.health_check()
            assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_concurrent_access(self, temp_storage):
        """Test concurrent access to provider."""
        import asyncio

        from serve.storage.trace_provider import FileTraceStorageProvider

        mock_logger = MagicMock()
        mock_logger.get_trace_by_id.return_value = {"trace_id": "test"}
        mock_logger.get_recent_traces.return_value = []
        mock_logger.recent_traces = []

        with patch("serve.storage.trace_provider.TraceMemoryLogger", return_value=mock_logger):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            # Simulate concurrent requests
            tasks = [
                provider.get_trace_by_id(f"trace_{i}")
                for i in range(10)
            ]

            results = await asyncio.gather(*tasks)

            assert len(results) == 10
            assert all(r["trace_id"] == "test" for r in results)

    def test_multiple_providers_different_locations(self, tmp_path):
        """Test multiple providers with different storage locations."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        location1 = str(tmp_path / "storage1")
        location2 = str(tmp_path / "storage2")

        provider1 = FileTraceStorageProvider(storage_location=location1)
        provider2 = FileTraceStorageProvider(storage_location=location2)

        assert provider1.storage_location == location1
        assert provider2.storage_location == location2
        assert os.path.exists(location1)
        assert os.path.exists(location2)


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_storage_directory_permission_error(self, tmp_path):
        """Test handling of permission errors."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("pathlib.Path.mkdir", side_effect=PermissionError):
            with pytest.raises(PermissionError):
                FileTraceStorageProvider(storage_location=str(tmp_path / "no_permission"))

    @pytest.mark.asyncio
    async def test_trace_logger_initialization_failure(self, temp_storage):
        """Test handling of logger initialization failure."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        with patch("serve.storage.trace_provider.TraceMemoryLogger", side_effect=RuntimeError("Init failed")):
            provider = FileTraceStorageProvider(storage_location=temp_storage)

            with pytest.raises(RuntimeError):
                await provider.get_trace_by_id("test")


class TestModuleExports:
    """Test module exports and API."""

    def test_module_exports(self):
        """Test module exports all required classes and functions."""
        from serve.storage import trace_provider

        # Check classes
        assert hasattr(trace_provider, "TraceStorageProvider")
        assert hasattr(trace_provider, "FileTraceStorageProvider")

        # Check functions
        assert hasattr(trace_provider, "create_trace_storage_provider")
        assert hasattr(trace_provider, "get_default_trace_provider")
        assert hasattr(trace_provider, "reset_default_trace_provider")

    def test_provider_inheritance(self):
        """Test FileTraceStorageProvider inherits from abstract base."""
        from serve.storage.trace_provider import (
            FileTraceStorageProvider,
            TraceStorageProvider,
        )

        assert issubclass(FileTraceStorageProvider, TraceStorageProvider)

    def test_abstract_methods_implemented(self):
        """Test all abstract methods are implemented."""
        from serve.storage.trace_provider import FileTraceStorageProvider

        provider_methods = dir(FileTraceStorageProvider)

        assert "get_trace_by_id" in provider_methods
        assert "get_recent_traces" in provider_methods
        assert "health_check" in provider_methods
