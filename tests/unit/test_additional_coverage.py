"""Additional unit coverage for observability and swarm fallbacks."""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


# Ensure repository root is importable when pytest uses nested configuration.
repo_root = str(Path(__file__).resolve().parents[2])
if repo_root not in sys.path:
    sys.path.append(repo_root)
os.environ.setdefault("PYTHONPATH", repo_root)

if "_bridgeutils" not in sys.modules:
    sys.modules["_bridgeutils"] = SimpleNamespace(
        bridge_from_candidates=lambda *candidates: (set(), {})
    )

# ΛTAG: coverage_extension_module_loader
def _load_module(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, Path(repo_root, relative_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    sys.modules.setdefault(module_name, module)
    package, _, attr = module_name.rpartition(".")
    if package:
        parent = sys.modules.get(package)
        if parent is None:
            parent = ModuleType(package)
            parent.__path__ = [str(Path(repo_root, package.replace(".", "/")))]
            sys.modules[package] = parent
        setattr(parent, attr, module)
    return module


# ΛTAG: coverage_extension_observability_filters
observability_filters = _load_module("observability.filters", "observability/filters.py")
redact_pii = observability_filters.redact_pii
# ΛTAG: coverage_extension_observability_log_redaction
observability_log_redaction = _load_module("observability.log_redaction", "observability/log_redaction.py")
RedactingFilter = observability_log_redaction.RedactingFilter
# ΛTAG: coverage_extension_observability_events
observability_events = _load_module("observability.events", "observability/events.py")
# ΛTAG: coverage_extension_observability_prom_registry
observability_prom_registry = _load_module(
    "observability.prometheus_registry", "observability/prometheus_registry.py"
)
prometheus_registry = observability_prom_registry
# ΛTAG: coverage_extension_core_swarm
core_swarm = _load_module("core.swarm", "core/swarm.py")
SwarmHub = core_swarm.SwarmHub


def _make_log_record(message: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=0, msg=message, args=(), exc_info=None
    )


def test_redacting_filter_scrubs_known_secret_patterns():
    """Ensure the log redaction filter removes token patterns without mutating clean text."""
    record = _make_log_record(
        "User sk-SECRET12345 requested Bearer TOKEN_ABC123 with APIKEY=Z12345678"
    )
    filter_ = RedactingFilter()

    assert filter_.filter(record) is True
    assert "sk-" not in record.msg
    assert "Bearer" not in record.msg
    assert "APIKEY" not in record.msg
    assert record.msg.count("[REDACTED]") == 3


def test_redact_pii_handles_email_and_openai_tokens():
    """Verify redact_pii replaces email addresses and secret tokens."""
    text = "Contact me at agent@lukhas.ai using token sk-abcdef123456"
    redacted = redact_pii(text)

    assert redacted.count("[redacted@email]") == 1
    assert "sk-" not in redacted
    assert "[redacted_token]" in redacted


def test_run_event_logging_writes_rotated_file(tmp_path):
    """Event logger should emit JSON lines with ISO timestamps to the daily file."""
    logger = observability_events.EventLogger(base_path=str(tmp_path))
    run_id = observability_events.generate_run_id()
    event = observability_events.RunEvent(event_type="run.started", run_id=run_id, timestamp=123.0)

    logger.log(event)
    log_files = list(tmp_path.iterdir())
    assert len(log_files) == 1
    contents = log_files[0].read_text().strip().splitlines()
    assert contents and "timestamp_iso" in contents[0]

    # Ensure helper utilities produce deterministic step IDs
    step_id = observability_events.generate_step_id(run_id, 3)
    assert step_id.endswith("_step_3")


@pytest.fixture
def restored_prometheus_registry(monkeypatch):
    """Provide a freshly imported prometheus_registry with stubbed Prometheus client."""
    stub_module = SimpleNamespace(
        CollectorRegistry=type("CollectorRegistry", (), {}),
        Counter=type("Counter", (), {"__call__": lambda *a, **k: None}),
        Gauge=type("Gauge", (), {"__call__": lambda *a, **k: None}),
        Histogram=type("Histogram", (), {"__call__": lambda *a, **k: None}),
        Summary=type("Summary", (), {"__call__": lambda *a, **k: None}),
    )
    monkeypatch.setitem(sys.modules, "prometheus_client", stub_module)
    module = importlib.reload(prometheus_registry)
    yield module
    importlib.reload(prometheus_registry)


def test_prometheus_registry_caches_duplicate_metrics(restored_prometheus_registry):
    """Duplicate metric declarations should return the cached instance."""
    registry = restored_prometheus_registry
    first = registry.counter("lukhas_test_metric", "doc", labelnames=("kind",))
    second = registry.counter("lukhas_test_metric", "doc", labelnames=("kind",))

    assert first is second
    labeled = first.labels("demo") if hasattr(first, "labels") else None
    if labeled is not None:
        assert labeled is first


def test_swarm_agent_receive_returns_placeholder_response(monkeypatch):
    """Fallback swarm implementation should accept messages and provide placeholder responses."""
    class StubSupervisor:
        def __init__(self, *args, **kwargs):
            self.children = {}

        def add_child(self, agent_id, agent):
            self.children[agent_id] = agent

        def handle_failure(self, agent_id, exc):  # pragma: no cover - not triggered
            return {"action": "restart", "agent": agent_id}

    monkeypatch.setattr(core_swarm, "Supervisor", StubSupervisor, raising=False)

    hub = SwarmHub()
    colony = hub.register_colony("colony-alpha", agent_count=0)
    agent = colony.create_agent("agent-1")

    agent.receive({"payload": "hello"})
    fallback = agent._handle_message({"payload": "direct"})
    assert fallback["status"] == "received"
    assert fallback["agent_id"] == "agent-1"

    assert "agent-1" in colony.supervisor.children
