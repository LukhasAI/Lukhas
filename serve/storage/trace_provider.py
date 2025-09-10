"""
Storage provider interface for LUKHAS AI trace data.

This module defines the abstract interface for trace storage providers and implements
a file-based provider that integrates with the TraceMemoryLogger system.
"""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

# Import TraceMemoryLogger from candidate lane with fallback
try:
    from candidate.core.orchestration.brain.trace_memory_logger import TraceMemoryLogger
except ImportError:
    TraceMemoryLogger = None

logger = logging.getLogger(__name__)


class TraceStorageProvider(ABC):
    """
    Abstract base class for trace storage providers.

    This interface allows the trace API to work with different storage backends
    while maintaining a consistent API surface.
    """

    @abstractmethod
    async def get_trace_by_id(self, trace_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a trace by its unique identifier.

        Args:
            trace_id: UUID of the trace to retrieve

        Returns:
            Trace data if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_recent_traces(
        self,
        limit: int = 10,
        level: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent traces with optional filtering.

        Args:
            limit: Maximum number of traces to return
            level: Filter by trace level
            tag: Filter by specific tag

        Returns:
            List of trace entries
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the storage provider.

        Returns:
            Health check status and metrics
        """
        pass


class FileTraceStorageProvider(TraceStorageProvider):
    """
    File-based trace storage provider using TraceMemoryLogger.

    This implementation integrates with the existing TraceMemoryLogger system
    to provide structured access to trace data stored in JSONL files.
    """

    def __init__(self, storage_location: Optional[str] = None):
        """
        Initialize the file-based trace storage provider.

        Args:
            storage_location: Base directory for trace storage.
                             Defaults to 'var/traces/' if not specified.
        """
        # Set default storage location
        if storage_location is None:
            storage_location = "var/traces/"

        self.storage_location = storage_location
        self._trace_logger: Optional[TraceMemoryLogger] = None

        # Ensure storage directory exists
        Path(self.storage_location).mkdir(parents=True, exist_ok=True)

        logger.info(f"FileTraceStorageProvider initialized with location: {self.storage_location}")

    def _get_trace_logger(self) -> TraceMemoryLogger:
        """
        Get or initialize the TraceMemoryLogger instance.

        Returns:
            Configured TraceMemoryLogger instance

        Raises:
            ImportError: If TraceMemoryLogger is not available
        """
        if self._trace_logger is None:
            if TraceMemoryLogger is None:
                raise ImportError(
                    "TraceMemoryLogger not available - missing candidate.core.orchestration.brain.trace_memory_logger"
                )

            # Configure TraceMemoryLogger to use our storage location
            config = {
                "log_dir": self.storage_location,
                "recent_traces_limit": 200,  # Increase cache for API usage
            }

            self._trace_logger = TraceMemoryLogger(config=config)
            logger.info("TraceMemoryLogger instance created for FileTraceStorageProvider")

        return self._trace_logger

    async def get_trace_by_id(self, trace_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a trace by its unique identifier.

        Args:
            trace_id: UUID of the trace to retrieve

        Returns:
            Trace data if found, None otherwise
        """
        try:
            trace_logger = self._get_trace_logger()
            return trace_logger.get_trace_by_id(trace_id)
        except Exception as e:
            logger.error(f"Error retrieving trace {trace_id}: {e}")
            raise

    async def get_recent_traces(
        self,
        limit: int = 10,
        level: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent traces with optional filtering.

        Args:
            limit: Maximum number of traces to return
            level: Filter by trace level
            tag: Filter by specific tag

        Returns:
            List of trace entries
        """
        try:
            trace_logger = self._get_trace_logger()
            return trace_logger.get_recent_traces(limit=limit, level=level, tag=tag)
        except Exception as e:
            logger.error(f"Error retrieving recent traces: {e}")
            raise

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the storage provider.

        Returns:
            Health check status and metrics
        """
        try:
            trace_logger = self._get_trace_logger()

            # Check if storage directory is accessible
            storage_accessible = os.path.isdir(self.storage_location) and os.access(self.storage_location, os.W_OK)

            # Check if all_traces.jsonl exists and is readable
            all_traces_file = os.path.join(self.storage_location, "all_traces.jsonl")
            traces_file_exists = os.path.exists(all_traces_file)

            # Get metrics
            recent_count = len(trace_logger.recent_traces)

            return {
                "status": "healthy" if storage_accessible else "unhealthy",
                "storage_location": self.storage_location,
                "storage_accessible": storage_accessible,
                "traces_file_exists": traces_file_exists,
                "recent_traces_count": recent_count,
                "trace_logger_initialized": True,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "storage_location": self.storage_location,
                "trace_logger_initialized": False,
            }


# Factory function to create storage provider based on configuration
def create_trace_storage_provider(
    provider_type: str = "file",
    storage_location: Optional[str] = None,
    **_kwargs,
) -> TraceStorageProvider:
    """
    Factory function to create trace storage providers.

    Args:
        provider_type: Type of storage provider ("file" is currently the only option)
        storage_location: Storage location (provider-specific)
        **kwargs: Additional provider-specific configuration

    Returns:
        Configured trace storage provider instance

    Raises:
        ValueError: If provider_type is not supported
    """
    if provider_type == "file":
        return FileTraceStorageProvider(storage_location=storage_location)
    else:
        raise ValueError(f"Unsupported storage provider type: {provider_type}")


# Default provider instance for convenience
_default_provider: Optional[TraceStorageProvider] = None


def get_default_trace_provider() -> TraceStorageProvider:
    """
    Get the default trace storage provider instance.

    This creates a singleton instance for use across the application.

    Returns:
        Default trace storage provider instance
    """
    global _default_provider
    if _default_provider is None:
        # Use environment variable or default location
        storage_location = os.getenv("LUKHAS_TRACE_STORAGE", "var/traces/")
        _default_provider = create_trace_storage_provider(provider_type="file", storage_location=storage_location)
    return _default_provider


def reset_default_trace_provider():
    """
    Reset the default trace storage provider singleton.

    This is primarily intended for testing to ensure clean state
    between test runs.
    """
    global _default_provider
    _default_provider = None
