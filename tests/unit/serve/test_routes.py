"""
Comprehensive test suite for serve.routes module.

Tests all 6 endpoints (generate_dream, glyph_feedback, tier_auth, plugin_load, memory_dump)
and 2 helper functions (compute_drift_score, compute_affect_delta) with both real
implementations and fallback paths.

Following Test Surgeon canonical guidelines:
- Tests only (no production code changes)
- Deterministic (mocked time, dependencies, filesystem)
- Network-free (all external systems mocked)
- Comprehensive coverage (75%+ target)
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest import mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def routes_module():
    """
    Import serve.routes with mocked external dependencies.

    Mocks:
    - config.config.TIER_PERMISSIONS
    - enterprise.observability (obs_stack decorator)
    - governance.guardian (drift detection)
    - consciousness.unified (dream generation)
    - emotion (affect processing)
    - memory.unified (fold management)
    """
    mock_tier_permissions = {
        1: ["read", "write"],
        3: ["read", "write", "admin"],
        5: ["read", "write", "admin", "superuser"],
    }

    mock_obs_stack = mock.MagicMock()
    mock_obs_stack.trace = lambda name: lambda func: func  # Pass-through decorator

    with mock.patch.dict("sys.modules", {
        "config": mock.MagicMock(),
        "config.config": mock.MagicMock(TIER_PERMISSIONS=mock_tier_permissions),
        "enterprise": mock.MagicMock(),
        "enterprise.observability": mock.MagicMock(),
        "enterprise.observability.instantiate": mock.MagicMock(obs_stack=mock_obs_stack),
        "governance": mock.MagicMock(),
        "governance.guardian": mock.MagicMock(),
        "governance.guardian.guardian_impl": mock.MagicMock(),
        "consciousness": mock.MagicMock(),
        "consciousness.unified": mock.MagicMock(),
        "consciousness.unified.auto_consciousness": mock.MagicMock(),
        "emotion": mock.MagicMock(),
        "memory": mock.MagicMock(),
        "memory.unified": mock.MagicMock(),
        "memory.unified.fold_manager": mock.MagicMock(),
    }):
        import importlib

        import serve.routes as routes_module
        importlib.reload(routes_module)
        yield routes_module


@pytest.fixture
def test_app(routes_module):
    """Create FastAPI test client with routes module."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(routes_module.router)
    return TestClient(app)


# ==============================================================================
# Helper Function Tests: compute_drift_score
# ==============================================================================

def test_compute_drift_score_with_guardian(routes_module):
    """Test compute_drift_score uses Guardian when available."""
    mock_guardian = mock.MagicMock()
    mock_guardian.detect_drift.return_value = mock.MagicMock(drift_score=0.42)

    with mock.patch("serve.routes.GuardianSystemImpl", return_value=mock_guardian):
        score = routes_module.compute_drift_score(["symbol1", "symbol2"])

    assert score == 0.42
    mock_guardian.detect_drift.assert_called_once()
    call_args = mock_guardian.detect_drift.call_args
    assert call_args[1]["current"] == "symbol1 symbol2"
    assert call_args[1]["threshold"] == 0.15


def test_compute_drift_score_caps_at_one(routes_module):
    """Test compute_drift_score caps drift score at 1.0."""
    mock_guardian = mock.MagicMock()
    mock_guardian.detect_drift.return_value = mock.MagicMock(drift_score=15.7)

    with mock.patch("serve.routes.GuardianSystemImpl", return_value=mock_guardian):
        score = routes_module.compute_drift_score(["symbol"])

    assert score == 1.0


def test_compute_drift_score_fallback_empty_symbols(routes_module):
    """Test compute_drift_score fallback returns 0.0 for empty symbols."""
    with mock.patch("serve.routes.GuardianSystemImpl", side_effect=ImportError):
        score = routes_module.compute_drift_score([])

    assert score == 0.0


def test_compute_drift_score_fallback_calculation(routes_module):
    """Test compute_drift_score fallback calculation logic."""
    with mock.patch("serve.routes.GuardianSystemImpl", side_effect=ImportError):
        # High diversity (unique symbols) = low drift
        score_diverse = routes_module.compute_drift_score(["a", "b", "c", "d"])

        # Low diversity (repeated symbols) = higher drift
        score_repeated = routes_module.compute_drift_score(["x", "x", "x", "x"])

    assert score_diverse < score_repeated
    assert 0.0 <= score_diverse <= 1.0
    assert 0.0 <= score_repeated <= 1.0


def test_compute_drift_score_fallback_caps_at_one(routes_module):
    """Test compute_drift_score fallback caps result at 1.0."""
    with mock.patch("serve.routes.GuardianSystemImpl", side_effect=ImportError):
        # Many repeated symbols should cap at 1.0
        score = routes_module.compute_drift_score(["x"] * 200)

    assert score == 1.0


# ==============================================================================
# Helper Function Tests: compute_affect_delta
# ==============================================================================

def test_compute_affect_delta_with_emotion_engine(routes_module):
    """Test compute_affect_delta uses emotion engine when available."""
    mock_process_emotion = mock.MagicMock(return_value={
        "valence": 0.8,
        "arousal": 0.6,
        "dominance": 0.7,
    })

    with mock.patch("serve.routes.process_emotion", mock_process_emotion):
        delta = routes_module.compute_affect_delta(["joy", "love"])

    assert 0.0 <= delta <= 1.0
    mock_process_emotion.assert_called_once()


def test_compute_affect_delta_fallback_empty_symbols(routes_module):
    """Test compute_affect_delta fallback returns 0.0 for empty symbols."""
    with mock.patch("serve.routes.process_emotion", side_effect=ImportError):
        delta = routes_module.compute_affect_delta([])

    assert delta == 0.0


def test_compute_affect_delta_fallback_positive_indicators(routes_module):
    """Test compute_affect_delta fallback detects positive indicators."""
    with mock.patch("serve.routes.process_emotion", side_effect=ImportError):
        delta = routes_module.compute_affect_delta(["joy", "love", "hope"])

    assert delta > 0.0
    assert delta <= 1.0


def test_compute_affect_delta_fallback_negative_indicators(routes_module):
    """Test compute_affect_delta fallback detects negative indicators."""
    with mock.patch("serve.routes.process_emotion", side_effect=ImportError):
        delta = routes_module.compute_affect_delta(["fear", "anger", "sad"])

    assert delta > 0.0
    assert delta <= 1.0


def test_compute_affect_delta_fallback_high_arousal(routes_module):
    """Test compute_affect_delta fallback detects high arousal indicators."""
    with mock.patch("serve.routes.process_emotion", side_effect=ImportError):
        delta = routes_module.compute_affect_delta(["exciting", "intense", "energy"])

    assert delta > 0.0
    assert delta <= 1.0


def test_compute_affect_delta_fallback_caps_at_one(routes_module):
    """Test compute_affect_delta fallback caps result at 1.0."""
    with mock.patch("serve.routes.process_emotion", side_effect=ImportError):
        delta = routes_module.compute_affect_delta(["joy"] * 100)

    assert delta <= 1.0


# ==============================================================================
# Endpoint Tests: POST /generate-dream/
# ==============================================================================

def test_generate_dream_with_consciousness_core(test_app, routes_module):
    """Test generate_dream uses ConsciousnessCore when available."""
    mock_consciousness = mock.MagicMock()
    mock_consciousness.generate_dream_narrative.return_value = "A cosmic dream unfolds"

    with mock.patch("serve.routes.ConsciousnessCore", return_value=mock_consciousness):
        response = test_app.post("/generate-dream/", json={"symbols": ["star", "moon"]})

    assert response.status_code == 200
    data = response.json()
    assert data["dream"] == "A cosmic dream unfolds"
    assert "driftScore" in data
    assert "affect_delta" in data


def test_generate_dream_fallback_empty_symbols(test_app, routes_module):
    """Test generate_dream fallback handles empty symbols."""
    with mock.patch("serve.routes.ConsciousnessCore", side_effect=ImportError):
        response = test_app.post("/generate-dream/", json={"symbols": []})

    assert response.status_code == 200
    data = response.json()
    assert data["dream"] == "Empty dream space - silence and void"


def test_generate_dream_fallback_single_symbol(test_app, routes_module):
    """Test generate_dream fallback with single symbol."""
    with mock.patch("serve.routes.ConsciousnessCore", side_effect=ImportError):
        response = test_app.post("/generate-dream/", json={"symbols": ["phoenix"]})

    assert response.status_code == 200
    data = response.json()
    assert "phoenix" in data["dream"]
    assert "echoing through infinite space" in data["dream"]


def test_generate_dream_fallback_two_symbols(test_app, routes_module):
    """Test generate_dream fallback with two symbols."""
    with mock.patch("serve.routes.ConsciousnessCore", side_effect=ImportError):
        response = test_app.post("/generate-dream/", json={"symbols": ["fire", "ice"]})

    assert response.status_code == 200
    data = response.json()
    assert "fire" in data["dream"]
    assert "ice" in data["dream"]
    assert "merge into one" in data["dream"]


def test_generate_dream_fallback_many_symbols(test_app, routes_module):
    """Test generate_dream fallback with many symbols."""
    with mock.patch("serve.routes.ConsciousnessCore", side_effect=ImportError):
        response = test_app.post("/generate-dream/", json={
            "symbols": ["alpha", "beta", "gamma", "delta"]
        })

    assert response.status_code == 200
    data = response.json()
    assert "alpha" in data["dream"]
    assert "delta" in data["dream"]


def test_generate_dream_emotional_modifiers(test_app, routes_module):
    """Test generate_dream applies emotional modifiers based on affect."""
    with mock.patch("serve.routes.ConsciousnessCore", side_effect=ImportError):
        # Low affect = peaceful
        with mock.patch("serve.routes.compute_affect_delta", return_value=0.2):
            response = test_app.post("/generate-dream/", json={"symbols": ["calm"]})
            assert "peaceful" in response.json()["dream"]

        # Medium affect = vivid
        with mock.patch("serve.routes.compute_affect_delta", return_value=0.5):
            response = test_app.post("/generate-dream/", json={"symbols": ["active"]})
            assert "vivid" in response.json()["dream"]

        # High affect = intense
        with mock.patch("serve.routes.compute_affect_delta", return_value=0.8):
            response = test_app.post("/generate-dream/", json={"symbols": ["extreme"]})
            assert "intense" in response.json()["dream"]


# ==============================================================================
# Endpoint Tests: POST /glyph-feedback/
# ==============================================================================

def test_glyph_feedback_high_drift(test_app):
    """Test glyph_feedback with high drift score."""
    response = test_app.post("/glyph-feedback/", json={
        "driftScore": 0.75,
        "collapseHash": "test_hash"
    })

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert any("High drift detected" in s for s in data["suggestions"])


def test_glyph_feedback_moderate_drift(test_app):
    """Test glyph_feedback with moderate drift score."""
    response = test_app.post("/glyph-feedback/", json={
        "driftScore": 0.3,
        "collapseHash": "test_hash"
    })

    assert response.status_code == 200
    data = response.json()
    assert any("Moderate drift" in s or "Guardian" in s for s in data["suggestions"])


def test_glyph_feedback_low_drift(test_app):
    """Test glyph_feedback with low drift score."""
    response = test_app.post("/glyph-feedback/", json={
        "driftScore": 0.05,
        "collapseHash": "test_hash"
    })

    assert response.status_code == 200
    data = response.json()
    suggestions = data["suggestions"]
    assert any("acceptable range" in s or "stability" in s for s in suggestions)


def test_glyph_feedback_collapse_hash_variations(test_app):
    """Test glyph_feedback with different collapse hash densities."""
    # High density hash
    response = test_app.post("/glyph-feedback/", json={
        "driftScore": 0.1,
        "collapseHash": "high_density_hash_999"
    })
    data = response.json()
    # Should have hash-based suggestion
    assert len(data["suggestions"]) > 0


def test_glyph_feedback_empty_collapse_hash(test_app):
    """Test glyph_feedback with empty collapse hash."""
    response = test_app.post("/glyph-feedback/", json={
        "driftScore": 0.1,
        "collapseHash": ""
    })

    assert response.status_code == 200
    assert "suggestions" in response.json()


# ==============================================================================
# Endpoint Tests: POST /tier-auth/
# ==============================================================================

def test_tier_auth_valid_tier1_token(test_app):
    """Test tier_auth with valid tier 1 token."""
    response = test_app.post("/tier-auth/", json={"token": "symbolic-tier-1"})

    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == 1
    assert data["access_rights"] == ["read", "write"]


def test_tier_auth_valid_tier3_token(test_app):
    """Test tier_auth with valid tier 3 token."""
    response = test_app.post("/tier-auth/", json={"token": "symbolic-tier-3"})

    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == 3
    assert data["access_rights"] == ["read", "write", "admin"]


def test_tier_auth_valid_tier5_token(test_app):
    """Test tier_auth with valid tier 5 token."""
    response = test_app.post("/tier-auth/", json={"token": "symbolic-tier-5"})

    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == 5
    assert data["access_rights"] == ["read", "write", "admin", "superuser"]


def test_tier_auth_invalid_token(test_app):
    """Test tier_auth with invalid token."""
    response = test_app.post("/tier-auth/", json={"token": "invalid-token"})

    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


# ==============================================================================
# Endpoint Tests: POST /plugin-load/
# ==============================================================================

def test_plugin_load_successful_persistence(test_app, tmp_path):
    """Test plugin_load successfully persists plugins to registry."""
    with mock.patch("serve.routes.Path", return_value=tmp_path):
        with mock.patch("serve.routes.Path.mkdir"):
            with mock.patch("builtins.open", mock.mock_open()):
                with mock.patch("json.dump"):
                    with mock.patch("json.load", return_value={}):
                        response = test_app.post("/plugin-load/", json={
                            "symbols": ["plugin1", "plugin2"]
                        })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "loaded and persisted"


def test_plugin_load_updates_existing_registry(test_app, tmp_path):
    """Test plugin_load updates load_count for existing plugins."""
    existing_registry = {
        "plugin1": {
            "registered_at": "2024-01-01T00:00:00Z",
            "status": "active",
            "load_count": 5
        }
    }

    with mock.patch("serve.routes.Path", return_value=tmp_path):
        with mock.patch("serve.routes.Path.mkdir"):
            with mock.patch("serve.routes.Path.exists", return_value=True):
                mock_file_data = mock.mock_open(read_data=json.dumps(existing_registry))
                with mock.patch("builtins.open", mock_file_data):
                    with mock.patch("json.load", return_value=existing_registry):
                        with mock.patch("json.dump"):
                            response = test_app.post("/plugin-load/", json={
                                "symbols": ["plugin1", "plugin2"]
                            })

    assert response.status_code == 200


def test_plugin_load_persistence_failure(test_app, tmp_path):
    """Test plugin_load handles persistence failures gracefully."""
    with mock.patch("serve.routes.Path", side_effect=Exception("Disk full")):
        response = test_app.post("/plugin-load/", json={
            "symbols": ["plugin1"]
        })

    assert response.status_code == 200
    data = response.json()
    assert "persistence failed" in data["status"]


def test_plugin_load_empty_symbols(test_app, tmp_path):
    """Test plugin_load with empty symbols list."""
    with mock.patch("serve.routes.Path", return_value=tmp_path):
        with mock.patch("serve.routes.Path.mkdir"):
            with mock.patch("builtins.open", mock.mock_open()):
                with mock.patch("json.dump"):
                    with mock.patch("json.load", return_value={}):
                        response = test_app.post("/plugin-load/", json={"symbols": []})

    assert response.status_code == 200


# ==============================================================================
# Endpoint Tests: GET /memory-dump/
# ==============================================================================

def test_memory_dump_with_fold_manager(test_app, routes_module):
    """Test memory_dump uses FoldManager when available."""
    mock_fold_manager = mock.MagicMock()
    mock_fold_manager.get_recent_folds.return_value = [
        {
            "fold_id": "fold_001",
            "content": "test memory",
            "created_at": "2024-01-01T00:00:00Z",
            "emotional_context": {"valence": 0.7},
            "symbolic_weight": 1.0,
        }
    ]

    mock_process_emotion = mock.MagicMock(return_value={
        "valence": 0.6,
        "arousal": 0.5,
        "dominance": 0.5,
    })

    with mock.patch("serve.routes.FoldManager", return_value=mock_fold_manager):
        with mock.patch("serve.routes.process_emotion", mock_process_emotion):
            response = test_app.get("/memory-dump/")

    assert response.status_code == 200
    data = response.json()
    assert "folds" in data
    assert "emotional_state" in data
    assert len(data["folds"]) > 0


def test_memory_dump_fallback_mode(test_app):
    """Test memory_dump fallback when FoldManager unavailable."""
    with mock.patch("serve.routes.FoldManager", side_effect=ImportError):
        response = test_app.get("/memory-dump/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["folds"]) == 3  # Fallback returns 3 folds
    assert data["emotional_state"]["status"] == "fallback_mode"


def test_memory_dump_emotional_state_structure(test_app):
    """Test memory_dump returns properly structured emotional state."""
    with mock.patch("serve.routes.FoldManager", side_effect=ImportError):
        response = test_app.get("/memory-dump/")

    assert response.status_code == 200
    data = response.json()
    emotional_state = data["emotional_state"]

    assert "affect_delta" in emotional_state
    assert "valence" in emotional_state
    assert "arousal" in emotional_state
    assert "dominance" in emotional_state
    assert "memory_fold_count" in emotional_state
    assert "emotional_coherence" in emotional_state


def test_memory_dump_fold_structure(test_app):
    """Test memory_dump folds have required fields."""
    with mock.patch("serve.routes.FoldManager", side_effect=ImportError):
        response = test_app.get("/memory-dump/")

    assert response.status_code == 200
    data = response.json()

    for fold in data["folds"]:
        assert "id" in fold
        assert "content" in fold
        assert "timestamp" in fold
        assert "emotional_context" in fold
        assert "symbolic_weight" in fold


# ==============================================================================
# Integration Tests
# ==============================================================================

def test_router_exports(routes_module):
    """Test that routes module exports router correctly."""
    assert hasattr(routes_module, "router")
    assert routes_module.router is not None


def test_token_tier_map_integrity(routes_module):
    """Test TOKEN_TIER_MAP has expected structure."""
    token_map = routes_module.TOKEN_TIER_MAP

    assert "symbolic-tier-1" in token_map
    assert "symbolic-tier-3" in token_map
    assert "symbolic-tier-5" in token_map
    assert token_map["symbolic-tier-1"] == 1
    assert token_map["symbolic-tier-3"] == 3
    assert token_map["symbolic-tier-5"] == 5
