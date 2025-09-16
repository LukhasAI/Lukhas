import json

import pytest

from candidate.bridge.trace_logger import (
    BridgeTraceLogger,
    TraceCategory,
    TraceLevel,
)


@pytest.fixture()
def bridge_logger(tmp_path):
    log_file = tmp_path / "trace.log"
    return BridgeTraceLogger(log_file=str(log_file))


def test_trace_summary_contains_aggregated_data(bridge_logger):
    bridge_logger.log_bridge_event(
        TraceCategory.HANDSHAKE,
        TraceLevel.INFO,
        "core.gateway",
        "handshake established",
        {"latency_ms": 12},
    )
    bridge_logger.log_bridge_event(
        TraceCategory.HANDSHAKE,
        TraceLevel.WARNING,
        "core.gateway",
        "handshake retry",
        {"attempt": 2},
    )
    bridge_logger.log_bridge_event(
        TraceCategory.MEMORY_MAP,
        TraceLevel.INFO,
        "memory.mapper",
        "mapping created",
    )

    summary = bridge_logger.get_trace_summary()

    assert summary["total_events"] == 3
    assert summary["by_category"]["handshake"] == 2
    assert summary["by_level"]["info"] >= 2
    assert summary["top_components"][0]["component"] == "core.gateway"
    assert summary["patterns"]
    assert "level_distribution" in summary["patterns"][0]
    assert "Total events" in summary["report"]
    assert summary["recent_events"]


def test_trace_logger_export_formats(bridge_logger):
    bridge_logger.log_bridge_event(
        TraceCategory.BRIDGE_OP,
        TraceLevel.INFO,
        "bridge.monitor",
        "heartbeat",
    )

    json_payload = bridge_logger.export_trace_data("json")
    data = json.loads(json_payload)
    assert len(data["events"]) == 1

    csv_payload = bridge_logger.export_trace_data("csv")
    assert "event_id" in csv_payload
    assert "metadata" in csv_payload

    markdown_payload = bridge_logger.export_trace_data("markdown")
    assert markdown_payload.startswith("| event_id |")

    with pytest.raises(ValueError):
        bridge_logger.export_trace_data("xml")
