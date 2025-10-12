"""Unit tests for MemoryOrchestrator."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from lukhas.memory.indexer import Indexer
from lukhas.memory.memory_orchestrator import MemoryOrchestrator


@pytest.fixture
def mock_indexer():
    indexer = Mock(spec=Indexer)
    indexer.upsert.return_value = "doc-id-123"
    indexer.search_text.return_value = [("doc-id-123", 0.85), ("doc-id-456", 0.75)]
    return indexer

@pytest.fixture
def mock_guardian():
    guardian = AsyncMock()
    guardian.validate_action_async.return_value = None
    guardian.monitor_behavior_async.return_value = None
    return guardian

@pytest.fixture
def orchestrator(mock_indexer):
    return MemoryOrchestrator(mock_indexer)

@pytest.fixture
def orchestrator_with_guardian(mock_indexer, mock_guardian):
    return MemoryOrchestrator(mock_indexer, mock_guardian)

def test_orchestrator_initialization(mock_indexer):
    orch = MemoryOrchestrator(mock_indexer)
    assert orch.indexer == mock_indexer
    assert orch.guardian is None

def test_orchestrator_with_guardian_initialization(mock_indexer, mock_guardian):
    orch = MemoryOrchestrator(mock_indexer, mock_guardian)
    assert orch.indexer == mock_indexer
    assert orch.guardian == mock_guardian

@pytest.mark.asyncio
async def test_add_event_without_guardian(orchestrator, mock_indexer):
    text = "test memory event"
    meta = {"lane": "labs", "timestamp": 1234567890}

    with patch.object(orchestrator.tracer, 'trace_operation') as mock_trace:
        mock_span = Mock()
        mock_trace.return_value.__enter__ = Mock(return_value=mock_span)
        mock_trace.return_value.__exit__ = Mock(return_value=None)

        result = await orchestrator.add_event(text, meta)

        assert result == "doc-id-123"
        mock_indexer.upsert.assert_called_once_with(text, meta)
        mock_span.add_attributes.assert_called()

@pytest.mark.asyncio
async def test_add_event_with_guardian(orchestrator_with_guardian, mock_indexer, mock_guardian):
    text = "test memory event"
    meta = {"lane": "labs", "timestamp": 1234567890}

    with patch.object(orchestrator_with_guardian.tracer, 'trace_operation') as mock_trace:
        mock_span = Mock()
        mock_trace.return_value.__enter__ = Mock(return_value=mock_span)
        mock_trace.return_value.__exit__ = Mock(return_value=None)

        result = await orchestrator_with_guardian.add_event(text, meta)

        assert result == "doc-id-123"
        mock_guardian.validate_action_async.assert_called_once_with(
            "memory_add", {"text": text, "meta": meta}
        )
        mock_guardian.monitor_behavior_async.assert_called_once_with(
            "memory_added", {"id": "doc-id-123", "text_len": len(text)}
        )
        mock_indexer.upsert.assert_called_once_with(text, meta)

def test_query(orchestrator, mock_indexer):
    query_text = "search query"
    k = 5
    filters = {"lane": "labs"}

    with patch.object(orchestrator.tracer, 'trace_operation') as mock_trace:
        mock_span = Mock()
        mock_trace.return_value.__enter__ = Mock(return_value=mock_span)
        mock_trace.return_value.__exit__ = Mock(return_value=None)

        result = orchestrator.query(query_text, k=k, filters=filters)

        assert result == [("doc-id-123", 0.85), ("doc-id-456", 0.75)]
        mock_indexer.search_text.assert_called_once_with(query_text, k=k, filters=filters)
        mock_span.add_attributes.assert_called()

def test_legacy_orchestrate_memory(orchestrator):
    result = orchestrator.orchestrate_memory("test_op", {"data": "test"})

    assert result["status"] == "success"
    assert result["operation"] == "test_op"
    assert "completed" in result["result"]
