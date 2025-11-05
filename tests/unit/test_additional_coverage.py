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

import os
import sys
from pathlib import Path
from types import SimpleNamespace

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


# Ensure repository root is importable when pytest uses nested configuration.
repo_root = str(Path(__file__).resolve().parents[2])
if repo_root not in sys.path:
    sys.path.append(repo_root)
os.environ.setdefault("PYTHONPATH", repo_root)

if "_bridgeutils" not in sys.modules:
    sys.modules["_bridgeutils"] = SimpleNamespace(
        bridge_from_candidates=lambda *candidates: (set(), {})
    )

if "psutil" not in sys.modules:
    sys.modules["psutil"] = SimpleNamespace(
        cpu_percent=lambda interval=1: 0.0,
        virtual_memory=lambda: SimpleNamespace(percent=0.0, used=0.0),
    )

if "yaml" not in sys.modules:
    sys.modules["yaml"] = SimpleNamespace(safe_load=lambda *_, **__: {})

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
# ΛTAG: coverage_extension_ai_orchestration_support
mcp_support_module = _load_module(
    "ai_orchestration.mcp_operational_support",
    "ai_orchestration/mcp_operational_support.py",
)
LUKHASMCPOperationalSupport = mcp_support_module.LUKHASMCPOperationalSupport
# ΛTAG: coverage_extension_author_reference_guard
author_reference_guard = _load_module(
    "enforcement.tone.author_reference_guard",
    "enforcement/tone/author_reference_guard.py",
)
# ΛTAG: coverage_extension_guardian_emit
guardian_emit_module = _load_module("guardian.emit", "guardian/emit.py")
# ΛTAG: coverage_extension_agent_tracer
agent_tracer_module = _load_module("core.agent_tracer", "core/agent_tracer.py")


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


def test_mcp_operational_support_monitor_uses_stubbed_system_metrics(monkeypatch):
    """Ensure operational monitor records stubbed psutil values for alert scenarios."""

    support = LUKHASMCPOperationalSupport()
    server_context = mcp_support_module.MCPServerContext()
    server_context.active_connections = 3
    server_context.requests_per_minute = 120
    server_context.error_rate = 0.25

    stub_memory = SimpleNamespace(percent=96.0, used=512 * 1024 * 1024)
    stub_psutil = SimpleNamespace(
        cpu_percent=lambda interval=1: 92.5,
        virtual_memory=lambda: stub_memory,
    )
    monkeypatch.setattr(mcp_support_module, "psutil", stub_psutil, raising=False)

    timeline = SimpleNamespace(values=[1000.0, 1001.0])

    def _fake_time():
        if timeline.values:
            return timeline.values.pop(0)
        return 1001.0

    monkeypatch.setattr(mcp_support_module.time, "time", _fake_time)

    metrics = support.monitor_mcp_operations(server_context)

    assert metrics.metrics["cpu_usage_percent"] == 92.5
    assert metrics.metrics["memory_usage_percent"] == 96.0
    assert metrics.metrics["active_connections"] == 3
    assert metrics.metrics["error_rate"] == 0.25


def test_author_reference_guard_validate_file_detects_blocked_terms(tmp_path):
    """Detect blocked author references while respecting stance neutralization."""

    cfg = {
        "exceptions": {"paths": ["allowed/"]},
        "blocked_terms": ["Hemingway", "Woolf"],
        "allow_stance_terms": ["neutral stance"],
    }

    candidate_file = tmp_path / "note.md"
    candidate_file.write_text(
        "This neutral stance example still quotes Hemingway as inspiration.",
        encoding="utf-8",
    )

    violations = author_reference_guard.validate_file(candidate_file, cfg)

    assert violations == [f"{candidate_file}: blocked reference -> Hemingway"]


def test_guardian_emit_requires_consent_for_sensitive_tags():
    """Guardian decision helper must enforce consent for sensitive operations."""

    with pytest.raises(ValueError):
        guardian_emit_module.emit_guardian_decision(
            db=None,
            plan_id="plan-1",
            lambda_id="agent-7",
            action="block",
            rule_name="financial-check",
            tags=["financial"],
            confidences={},
            band="critical",
        )


def test_agent_tracer_collects_span_metrics(monkeypatch):
    """Trace collector should aggregate span metrics from the agent context manager."""

    class _Timeline:
        def __init__(self):
            self.values = [100.0, 104.0]

        def time(self):
            if self.values:
                return self.values.pop(0)
            return 104.0

    timeline = _Timeline()
    monkeypatch.setattr(agent_tracer_module, "time", SimpleNamespace(time=timeline.time))

    collector = agent_tracer_module.TraceCollector()
    tracer = agent_tracer_module.AIAgentTracer("agent-core", collector)

    with tracer.trace_agent_operation("agent-core", "process_message", driftScore=0.1):
        pass

    metrics = collector.get_metrics()
    assert metrics["total_operations"] == 1
    assert metrics["operations_by_type"]["process_message"]["count"] == 1

    agent_metrics = tracer.get_metrics()
    assert agent_metrics["total_operations"] == 1
    assert agent_metrics["total_duration"] == pytest.approx(metrics["total_duration"])


def test_otel_compat_falls_back_to_noop_when_opentelemetry_unavailable(monkeypatch):
    """Reload OTEL compat shim with a stub to ensure fallback no-op object is used."""

    otel_stub = ModuleType("opentelemetry")

    def _missing_attr(_):
        raise AttributeError("missing")

    otel_stub.__getattr__ = _missing_attr  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "opentelemetry", otel_stub)

    compat_module = _load_module(
        "observability.otel_compat_fallback", "observability/otel_compat.py"
    )

    noop = compat_module.trace
    assert noop is compat_module.metrics
    assert noop.__class__.__name__ == "_NoOp"
    assert noop() is noop
