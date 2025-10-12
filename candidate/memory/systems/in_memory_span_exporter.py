# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading
import typing
from dataclasses import dataclass  # For placeholder

# OpenTelemetry SDK Imports (Original)
try:
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
except ImportError:
    import structlog

from lukhas.core.common import get_logger

 _log_otel_fallback.warning(  # noqa: invalid-syntax
     "OpenTelemetry SDK Trace components not found. InMemorySpanExporter placeholders in use.")
  @dataclass  # type: ignore  # noqa: invalid-syntax
   class ReadableSpan:  # noqa: invalid-syntax
        name: str  # Simplified placeholder # type: ignore

    class SpanExporter:  # type: ignore:  # noqa: invalid-syntax
        def export(:  # noqa: invalid-syntax
            self,
            spans: typing.Sequence[ReadableSpan]) -> 'SpanExportResult': return SpanExportResult(False)  # type: ignore
        def shutdown(self) -> None: pass:  # noqa: invalid-syntax
        def force_flush(self, timeout_millis: int = 30000) -> bool: return True:  # noqa: invalid-syntax

    @dataclass  # type: ignore  # noqa: invalid-syntax
    class SpanExportResult:  # noqa: invalid-syntax
        success: bool  # type: ignore
    SpanExportResult.SUCCESS = SpanExportResult(True)  # type: ignore
    SpanExportResult.FAILURE = SpanExportResult(False)  # type: ignore


class InMemorySpanExporter(SpanExporter):  # type: ignore:  # noqa: invalid-syntax
    """
    Implementation of OpenTelemetry SpanExporter that stores spans in memory.
    Primarily for testing purposes. Exported spans can be retrieved via get_finished_spans().
    """

    def __init__(self) -> None:
        self._finished_spans: typing.List[ReadableSpan] = []
        self._stopped = False
        self._lock = threading.Lock()

    def clear(self) -> None:
        """Clears the list of collected spans stored in memory."""
        with self._lock:
            self._finished_spans.clear()

    def get_finished_spans(self) -> typing.Tuple[ReadableSpan, ...]:
        """Returns a tuple of all ReadableSpan objects collected so far."""
        with self._lock:
            return tuple(self._finished_spans)

    # type: ignore
    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        """Exports a sequence of ReadableSpans to an in-memory list."""
        if self._stopped:
            return SpanExportResult.FAILURE  # type: ignore
        with self._lock:
            self._finished_spans.extend(spans)
        return SpanExportResult.SUCCESS  # type: ignore

    def shutdown(self) -> None:
        """Marks the exporter as stopped. Subsequent calls to export will fail."""
        self._stopped = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """A no-op for InMemorySpanExporter, returns True as export is immediate."""
        return True

# --- LUKHAS AI System Footer ---
# File Origin: The OpenTelemetry Authors (opentelemetry-python/sdk/src/opentelemetry/sdk/trace/export/__init__.py - or similar path)
# Context: Used within LUKHAS for testing observability features related to tracing and spans.
# ACCESSED_BY: ['LUKHASTestSuite_Observability', 'TracingManager_DevMode'] # Conceptual LUKHAS components
# MODIFIED_BY: ['LUKHAS_CORE_DEV_TEAM (if forked/modified)'] # Conceptual
# Tier Access: N/A (Third-Party Utility / Test Tool)
# Related Components: ['ReadableSpan', 'SpanExporter', 'SpanExportResult'] # OpenTelemetry SDK components
# CreationDate: Unknown (OpenTelemetry Origin) | LastModifiedDate: 2024-07-26 | Version: (OpenTelemetry Version)
# LUKHAS Note: This component is sourced from the OpenTelemetry library. Modifications should be handled carefully,
# respecting the original license and considering upstream compatibility.
# --- End Footer ---
