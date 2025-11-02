"""Unit tests for core bridge implementations."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    for parent in start.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Repository root not found")


ROOT_PATH = _find_repo_root(Path(__file__).resolve())


def _load_module(module_name: str, relative_path: str):
    module_path = ROOT_PATH / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_bridge(module_file: str):
    return _load_module(f"candidate.core.bridges.{module_file}", f"candidate/core/bridges/{module_file}.py")


core_consciousness_bridge = _load_bridge("core_consciousness_bridge")
identity_core_bridge = _load_bridge("identity_core_bridge")
core_safety_bridge = _load_bridge("core_safety_bridge")
consciousness_qi_bridge = _load_module(
    "labs.core.bridges.consciousness_qi_bridge",
    "candidate/core/bridges/consciousness_qi_bridge.py",
)

CoreConsciousnessBridge = core_consciousness_bridge.CoreConsciousnessBridge
IdentityCoreBridge = identity_core_bridge.IdentityCoreBridge
CoreSafetyBridge = core_safety_bridge.CoreSafetyBridge
ConsciousnessQIBridge = consciousness_qi_bridge.ConsciousnessQIBridge


class _StubSystem:
    def __init__(self, name: str, state: dict[str, object]):
        self.name = name
        self.state = state
        self.events: list[tuple[str, dict[str, object]]] = []
        self.patches: list[dict[str, object]] = []

    async def process_event(self, event_type: str, payload: dict[str, object]):
        self.events.append((event_type, payload))
        return {"status": "ok", "event_type": event_type, "source": self.name}

    def get_state(self):
        return self.state

    async def apply_state_patch(self, payload: dict[str, object]):
        self.patches.append(payload)


@pytest.mark.asyncio
async def test_core_consciousness_bridge_sync_and_routing():
    core_state = {"consciousness": {"coherence": 0.3}}
    consciousness_state = {"consciousness": {"coherence": 0.8}}
    core_stub = _StubSystem("core", core_state)
    consciousness_stub = _StubSystem("consciousness", consciousness_state)

    bridge = CoreConsciousnessBridge(core_stub, consciousness_stub)

    sync_result = await bridge.sync_state()
    assert sync_result["differences"]
    assert core_stub.patches
    assert consciousness_stub.patches

    await bridge.handle_event(
        {
            "source": "core",
            "event_type": "core_state_update",
            "payload": {"event_type": "core_state_update", "data": {"metric": 1}},
        }
    )
    assert any(event for event, _ in consciousness_stub.events if "consciousness_state_sync" in event)

    await bridge.handle_event(
        {
            "source": "consciousness",
            "event_type": "consciousness_state_update",
            "payload": {"event_type": "consciousness_state_update", "data": {"metric": 2}},
        }
    )
    assert any(event for event, _ in core_stub.events if "core_state_sync" in event)


def test_identity_core_bridge_compare_states():
    bridge = IdentityCoreBridge()
    state_identity = {
        "identity": {"coherence": 0.4, "traits": ["caring", "curious"]},
        "guardian": {"status": "ok"},
    }
    state_core = {
        "identity": {"coherence": 0.7, "traits": ["caring", "resolute"]},
        "guardian": {"status": "elevated"},
    }

    differences = bridge.compare_states(state_identity, state_core)
    assert differences
    assert any(diff["trinity_axis"] == "⚛️" for diff in differences)
    assert any(diff["trinity_axis"] == "🛡️" for diff in differences)


def test_core_safety_bridge_compare_states():
    bridge = CoreSafetyBridge()
    state_core = {
        "guardian": {"risk_level": 0.2, "alerts": ["none"]},
        "consciousness": {"coherence": 0.5},
    }
    state_safety = {
        "guardian": {"risk_level": 0.6, "alerts": ["threshold"]},
        "consciousness": {"coherence": 0.5},
    }

    differences = bridge.compare_states(state_core, state_safety)
    assert differences
    assert any(diff["trinity_axis"] == "🛡️" for diff in differences)
    assert any(diff["driftScore"] > 0 for diff in differences)


def test_consciousness_qi_bridge_timestamp_format():
    bridge = ConsciousnessQIBridge()
    timestamp = bridge._get_timestamp()
    assert timestamp.endswith("Z")
