#!/usr/bin/env python3

"""
Test Fixtures for Wave C Memory System Testing
=============================================

Comprehensive fixture setup for testing the C4 memory system with:
- Multiple database backends (SQLite/PostgreSQL)
- Production and development modes
- Test data generation
- Performance benchmarking utilities
"""
import contextlib
import tempfile
import time
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from candidate.aka_qualia.core import AkaQualia
from candidate.aka_qualia.memory_noop import NoopMemory
from candidate.aka_qualia.memory_sql import SqlMemory
from candidate.aka_qualia.models import (
    AgencyFeel,
    PhenomenalGlyph,
    PhenomenalScene,
    ProtoQualia,
    RegulationPolicy,
    RiskProfile,
    SeverityLevel,
    TemporalFeel,
)

# === Database Fixtures ===


@pytest.fixture
def sqlite_engine():
    """In-memory SQLite engine for fast unit tests"""
    # Use file-based SQLite for threading tests, in-memory for others
    import os
    import tempfile

    # Create a temporary database file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor, but keep the file

    engine = create_engine(
        f"sqlite:///{db_path}", 
        echo=False,
        connect_args={
            "check_same_thread": False,  # Allow SQLite to be used across threads
        },
        poolclass=StaticPool,  # Use single connection pool
    )

    yield engine

    # Cleanup: close engine and remove temp file
    engine.dispose()
    with contextlib.suppress(Exception):
        os.unlink(db_path)


@pytest.fixture
def temp_sqlite_file():
    """Temporary SQLite file that gets cleaned up"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    yield db_path

    # Cleanup
    with contextlib.suppress(Exception):
        Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sql_memory(sqlite_engine):
    """Basic SqlMemory client for development mode testing"""
    memory = SqlMemory(
        engine=sqlite_engine,
        rotate_salt="test_salt_dev",
        is_prod=False,  # Development mode - no hashing
    )

    # Apply migration to set up tables
    memory._apply_migration()

    return memory


@pytest.fixture
def sql_memory_prod(sqlite_engine):
    """Production-mode SqlMemory with privacy hashing enabled"""
    memory = SqlMemory(
        engine=sqlite_engine,
        rotate_salt="prod_salt_secure_123",
        is_prod=True,  # Production mode - hash PII
    )

    memory._apply_migration()

    return memory


@pytest.fixture
def noop_memory():
    """NoopMemory client for testing without database"""
    return NoopMemory()


# === AkaQualia System Fixtures ===


@pytest.fixture
def aq_with_noop_memory():
    """AkaQualia system with NoopMemory backend"""
    config = {
        "memory_driver": "noop",
        "memory_config": {},
        "enable_memory_storage": True,
        "enable_drift_monitoring": False,  # Simplified for testing
        "vivox_collapse_validation": False,
        "vivox_me_integration": False,
        "enable_glyph_routing": False,  # Avoid router import issues in tests
    }

    return AkaQualia(config=config)


@pytest.fixture
def aq_with_sql_memory(sql_memory):
    """AkaQualia system with SQL memory backend"""
    config = {
        "memory_driver": "sql",
        "memory_config": {
            "engine": sql_memory.engine,
            "rotate_salt": "test_salt",
            "is_prod": False,
        },
        "enable_memory_storage": True,
        "enable_drift_monitoring": False,
        "vivox_collapse_validation": False,
        "vivox_me_integration": False,
        "enable_glyph_routing": False,
    }

    # Pass the pre-configured memory client
    return AkaQualia(memory=sql_memory, config=config)


# === Test Data Generation ===


@pytest.fixture
def base_proto_qualia():
    """Standard proto-qualia for testing"""
    return ProtoQualia(
        tone=0.2,
        arousal=0.6,
        clarity=0.8,
        embodiment=0.7,
        colorfield="blue",
        temporal_feel=TemporalFeel.FLOWING,
        agency_feel=AgencyFeel.EMPOWERED,
        narrative_gravity=0.4,
    )


@pytest.fixture
def low_risk_scene(base_proto_qualia):
    """Low-risk scene that shouldn't trigger enforcement"""
    return PhenomenalScene(
        proto=base_proto_qualia,
        subject="observer",
        object="peaceful_scene",
        context={
            "session_id": "test_session",
            "cfg_version": "wave_c_v1.0.0",
            "policy_sig": "test_policy_123",
        },
        risk=RiskProfile(score=0.05, severity=SeverityLevel.MINIMAL, reasons=[]),
        timestamp=time.time(),
    )


@pytest.fixture
def high_risk_scene(base_proto_qualia):
    """High-risk scene that should trigger TEQ enforcement"""
    risky_proto = ProtoQualia(
        tone=-0.8,
        arousal=0.95,
        clarity=0.2,
        embodiment=0.3,
        colorfield="red",
        temporal_feel=TemporalFeel.URGENT,
        agency_feel=AgencyFeel.POWERLESS,
        narrative_gravity=0.9,
    )

    return PhenomenalScene(
        proto=risky_proto,
        subject="observer",
        object="threatening_stimulus",
        context={
            "session_id": "test_session",
            "cfg_version": "wave_c_v1.0.0",
            "policy_sig": "enforcement_policy_456",
            "transform_chain": ["teq.enforce", "sublimate_arousal_to_clarity_0.3"],
        },
        risk=RiskProfile(
            score=0.85,
            severity=SeverityLevel.HIGH,
            reasons=["violence_detected", "emotional_dysregulation"],
        ),
        transform_chain=["teq.enforce", "sublimate_arousal_to_clarity_0.3"],
        timestamp=time.time(),
    )


@pytest.fixture
def test_glyphs():
    """Standard set of test glyphs"""
    return [
        PhenomenalGlyph(key="aka:vigilance", attrs={"tone": 0.2, "arousal": 0.6, "risk_score": 0.1}),
        PhenomenalGlyph(key="temporal_flowing", attrs={"narrative_gravity": 0.4, "clarity": 0.8}),
        PhenomenalGlyph(key="agency_empowered", attrs={"embodiment": 0.7}),
    ]


@pytest.fixture
def test_policy():
    """Standard regulation policy for testing"""
    return RegulationPolicy(gain=1.0, pace=1.0, actions=["maintain"], color_contrast=None)


@pytest.fixture
def test_metrics():
    """Standard metrics for testing"""
    from candidate.aka_qualia.models import Metrics

    return Metrics(
        drift_phi=0.95,
        congruence_index=0.88,
        sublimation_rate=0.0,
        neurosis_risk=0.12,
        qualia_novelty=0.73,
        repair_delta=0.05,
        timestamp=time.time(),
        episode_id=f"test_episode_{int(time.time())}",
    )


# === Data Population Fixtures ===


@pytest.fixture
def sql_memory_with_data(sql_memory, low_risk_scene, test_glyphs, test_policy, test_metrics):
    """SQL memory pre-populated with test data"""

    # Add 5 scenes for testing
    for i in range(5):
        scene_data = low_risk_scene.model_dump()
        scene_data["subject"] = f"user_{i}"
        scene_data["timestamp"] = time.time() + i  # Increasing timestamps

        glyphs_data = [g.model_dump() for g in test_glyphs]
        policy_data = test_policy.model_dump()
        metrics_data = test_metrics.model_dump()

        sql_memory.save(
            user_id="test_user",
            scene=scene_data,
            glyphs=glyphs_data,
            policy=policy_data,
            metrics=metrics_data,
            cfg_version="wave_c_v1.0.0",
        )

    return sql_memory


@pytest.fixture
def sql_memory_with_100k_rows(sql_memory):
    """SQL memory with 100k rows for performance testing"""
    # This would be too slow for regular tests, so we'll mock it
    # or use pytest markers to skip unless specifically requested
    pytest.skip("100k row fixture only for explicit performance tests")


# === Performance & Monitoring Fixtures ===


@pytest.fixture
def performance_timer():
    """Utility for timing operations"""

    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.perf_counter()

        def stop(self):
            self.end_time = time.perf_counter()
            return self.elapsed()

        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return PerformanceTimer()


@pytest.fixture
def metrics_collector_mock():
    """Mock metrics collector for testing observability"""
    mock = Mock()
    mock.record_aka_qualia_scene = Mock()
    mock.record_aka_qualia_regulation = Mock()
    mock.record_aka_qualia_processing_time = Mock()
    return mock


# === Utility Functions ===


def create_test_scene(**overrides) -> dict[str, Any]:
    """Create test scene data with optional overrides"""
    default = {
        "proto": {
            "tone": 0.0,
            "arousal": 0.5,
            "clarity": 0.7,
            "embodiment": 0.6,
            "colorfield": "blue",
            "temporal_feel": "flowing",
            "agency_feel": "empowered",
            "narrative_gravity": 0.3,
        },
        "subject": "observer",
        "object": "test_stimulus",
        "context": {
            "cfg_version": "wave_c_v1.0.0",
            "policy_sig": "test_policy_sig",
            "session_id": "test_session",
        },
        "risk": {"score": 0.1, "severity": "minimal", "reasons": []},
        "timestamp": time.time(),
    }

    # Apply overrides recursively
    def update_nested(d, overrides):
        for k, v in overrides.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                update_nested(d[k], v)
            else:
                d[k] = v

    update_nested(default, overrides)
    return default


def create_test_glyph(key: str = "test:glyph", **attrs) -> dict[str, Any]:
    """Create test glyph data"""
    return {"key": key, "attrs": {"tone": 0.0, "risk_score": 0.1, **attrs}}


def create_varying_scene(scene_id: str) -> dict[str, Any]:
    """Create scene with varying data for performance tests"""
    import hashlib

    # Use scene_id to create deterministic but varied data
    hash_int = int(hashlib.md5(scene_id.encode()).hexdigest()[:8], 16)

    return create_test_scene(
        proto={
            "tone": (hash_int % 200 - 100) / 100.0,  # -1.0 to 1.0
            "arousal": (hash_int % 100) / 100.0,  # 0.0 to 1.0
            "clarity": ((hash_int >> 8) % 100) / 100.0,
        },
        subject=f"subject_{scene_id}",
        object=f"object_{hash_int % 10}",
        context={
            "cfg_version": "wave_c_v1.0.0",
            "policy_sig": f"policy_{hash_int % 5}",
            "scene_id": scene_id,
        },
    )
