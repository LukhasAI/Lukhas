"""Tests for the consciousness bridge token mapping utilities."""

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import sys
import types

import pytest


class _StructlogLogger:
    """Minimal structlog logger stub for tests."""

    def info(self, *args, **kwargs) -> None:  # pragma: no cover - simple stub
        pass

    def warning(self, *args, **kwargs) -> None:  # pragma: no cover - simple stub
        pass

    def debug(self, *args, **kwargs) -> None:  # pragma: no cover - simple stub
        pass


if "structlog" not in sys.modules:
    structlog_stub = types.ModuleType("structlog")
    structlog_stub.get_logger = lambda *_: _StructlogLogger()
    sys.modules["structlog"] = structlog_stub


def _load_bridge_token_map() -> type:
    """Dynamically load the BridgeTokenMap class without importing heavy dependencies."""

    module_path = Path(__file__).resolve().parents[1] / "core" / "symbolic_bridge" / "token_map.py"
    spec = importlib.util.spec_from_file_location(
        "labs.core.symbolic_bridge.token_map", module_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.BridgeTokenMap


BridgeTokenMap = _load_bridge_token_map()


@pytest.fixture()
def token_map() -> BridgeTokenMap:
    """Create a token map with deterministic configuration for tests."""

    return BridgeTokenMap(config={"temporal_tolerance_ms": 4000})


def test_add_mapping_records_emotional_vector_and_temporal_signature(token_map: BridgeTokenMap) -> None:
    """Adding a mapping captures emotional vectors and temporal metadata."""

    timestamp = datetime(2025, 1, 1, 12, 30, tzinfo=timezone.utc)
    emotional_vector = {"valence": 0.8, "arousal": 0.25, "dominance": 0.6, "temporal_decay": 0.9}

    token_map.add_mapping(
        "glyph_a",
        "glyph_b",
        "token_alpha",
        "token_beta",
        emotional_vector=emotional_vector,
        timestamp=timestamp,
        temporal_signature="circadian_90",
    )

    record = token_map.get_mapping_record("glyph_a", "glyph_b", "token_alpha")
    assert record is not None
    assert record.target_token == "token_beta"
    assert record.emotional_vector == emotional_vector
    assert record.last_synced_at == timestamp
    assert record.temporal_signature == "circadian_90"
    assert record.sync_history[-1]["drift_ms"] == pytest.approx(0.0)


def test_emotional_vector_normalization_defaults_missing_dimensions(token_map: BridgeTokenMap) -> None:
    """Emotional vectors are normalized and missing dimensions defaulted."""

    timestamp = datetime(2025, 5, 5, tzinfo=timezone.utc)
    token_map.add_mapping(
        "glyph_a",
        "glyph_c",
        "token_gamma",
        "token_delta",
        emotional_vector={"valence": 1.5, "arousal": -0.5},
        timestamp=timestamp,
    )

    emotional_vector = token_map.get_emotional_vector("glyph_a", "glyph_c", "token_gamma")
    assert emotional_vector == {
        "valence": 1.0,  # clamped
        "arousal": 0.0,  # clamped
        "dominance": 0.0,  # default
        "temporal_decay": 1.0,  # default
    }


def test_synchronize_temporal_state_tracks_drift_and_status(token_map: BridgeTokenMap) -> None:
    """Temporal synchronization tracks drift and tolerance compliance."""

    base_time = datetime(2026, 3, 1, tzinfo=timezone.utc)
    token_map.add_mapping(
        "mesh_a",
        "mesh_b",
        "seed_token",
        "propagated_seed",
        timestamp=base_time,
    )

    within_window = base_time + timedelta(seconds=2)
    assert token_map.synchronize_temporal_state(
        "mesh_a",
        "mesh_b",
        "seed_token",
        timestamp=within_window,
        temporal_signature="ultradian_sync",
    )

    record = token_map.get_mapping_record("mesh_a", "mesh_b", "seed_token")
    assert record is not None
    assert record.sync_drift_ms == pytest.approx(2000.0, rel=1e-4)
    assert record.is_temporally_synced is True
    assert record.temporal_signature == "ultradian_sync"

    beyond_window = within_window + timedelta(seconds=10)
    assert token_map.synchronize_temporal_state(
        "mesh_a",
        "mesh_b",
        "seed_token",
        timestamp=beyond_window,
        tolerance_ms=1000,
    ) is False
    record = token_map.get_mapping_record("mesh_a", "mesh_b", "seed_token")
    assert record is not None
    assert record.sync_drift_ms == pytest.approx(10000.0, rel=1e-4)
    assert record.is_temporally_synced is False


def test_temporal_status_returns_full_snapshot(token_map: BridgeTokenMap) -> None:
    """Temporal status exposes synchronization metadata."""

    base_time = datetime(2027, 7, 7, tzinfo=timezone.utc)
    token_map.add_mapping(
        "mesh_c",
        "mesh_d",
        "token_epsilon",
        "token_zeta",
        timestamp=base_time,
    )

    status = token_map.get_temporal_status("mesh_c", "mesh_d", "token_epsilon")
    assert status is not None
    assert status["last_synced_at"] == base_time
    assert status["sync_drift_ms"] == pytest.approx(0.0)
    assert isinstance(status["sync_history"], list)
    assert status["is_temporally_synced"] is True


def test_synchronize_unknown_mapping_returns_false(token_map: BridgeTokenMap) -> None:
    """Synchronizing a missing mapping fails without raising."""

    assert token_map.synchronize_temporal_state(
        "unknown",
        "mesh_x",
        "token",  # missing mapping
        timestamp=datetime.now(timezone.utc),
    ) is False
