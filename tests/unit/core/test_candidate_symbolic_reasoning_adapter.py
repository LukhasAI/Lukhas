"""Unit tests validating candidate.core.symbolic.symbolic_reasoning_adapter cleanup flows."""

from lukhas.core.symbolic.symbolic_reasoning_adapter import (
    ReasoningContext,
    ReasoningMode,
    SymbolicReasoningAdapter,
)


def _build_context(context_id: str = "ctx-1", mode: ReasoningMode = ReasoningMode.SYMBOLIC) -> ReasoningContext:
    """Create a baseline reasoning context for testing."""

    return ReasoningContext(
        context_id=context_id,
        mode=mode,
        symbolic_input={"payload": 1},
        logical_output={"result": "ok"},
        adaptation_metadata={"source": "unit-test"},
    )


def test_close_reasoning_context_archives_and_updates_metrics() -> None:
    """Closing a context should archive data, clean caches, and update metrics."""

    adapter = SymbolicReasoningAdapter()
    context = _build_context()
    adapter.reasoning_contexts[context.context_id] = context
    adapter.adaptation_cache[context.context_id] = {"context_id": context.context_id, "value": 42}
    adapter.adaptation_cache["alias"] = {"context_id": context.context_id, "value": "alias"}

    result = adapter.close_reasoning_context(context.context_id)

    assert result is True
    assert context.context_id not in adapter.reasoning_contexts
    assert context.context_id not in adapter.adaptation_cache
    assert "alias" not in adapter.adaptation_cache

    assert adapter.metrics["closed_contexts"] == 1
    assert adapter.metrics["archived_contexts"] == len(adapter.archived_contexts) == 1
    assert adapter.metrics["cache_entries_removed"] == 2
    assert adapter.metrics["active_contexts"] == 0
    assert adapter.metrics["cleanup_failures"] == 0
    assert adapter.metrics["last_closed_mode"] == ReasoningMode.SYMBOLIC.value
    assert adapter.metrics["coherence_snapshot"] == adapter.coherence_threshold

    archive_record = adapter.archived_contexts[-1]
    assert archive_record["context_id"] == context.context_id
    assert archive_record["mode"] == ReasoningMode.SYMBOLIC.value
    assert archive_record["removed_cache_keys"] == [context.context_id, "alias"]
    assert archive_record["symbolic_input"] == {"payload": 1}
    assert archive_record["logical_output"] == {"result": "ok"}
    assert archive_record["metadata"] == {"source": "unit-test"}
    assert archive_record["coherence_snapshot"] == adapter.coherence_threshold

    # Ensure archived data is a snapshot, not a live reference.
    context.symbolic_input["payload"] = 99
    assert archive_record["symbolic_input"] == {"payload": 1}


def test_close_reasoning_context_missing_records_failure() -> None:
    """Closing a missing context should register a cleanup failure and return False."""

    adapter = SymbolicReasoningAdapter()

    result = adapter.close_reasoning_context("missing")

    assert result is False
    assert adapter.metrics["cleanup_failures"] == 1
    assert adapter.archived_contexts == []
