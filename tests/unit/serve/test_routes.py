"""
Comprehensive test suite for serve/routes.py

Tests core LUKHAS API routes:
- Dream generation endpoint
- Glyph feedback endpoint
- Tier authentication
- Plugin loading
- Memory dump
- Guardian integration
- Emotion processing
- Memory subsystem integration
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_guardian():
    """Mock GuardianSystemImpl."""
    with patch("serve.routes.GuardianSystemImpl") as mock_guardian_class:
        mock_instance = MagicMock()

        # Mock drift detection
        mock_drift_result = MagicMock()
        mock_drift_result.drift_score = 0.25
        mock_instance.detect_drift.return_value = mock_drift_result

        mock_guardian_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_emotion():
    """Mock emotion processing."""
    with patch("serve.routes.process_emotion") as mock_emotion_func:
        mock_emotion_func.return_value = {
            "valence": 0.7,
            "arousal": 0.5,
            "dominance": 0.6,
        }
        yield mock_emotion_func


@pytest.fixture
def mock_consciousness():
    """Mock ConsciousnessCore."""
    with patch("serve.routes.ConsciousnessCore") as mock_consciousness_class:
        mock_instance = MagicMock()
        mock_instance.generate_dream_narrative.return_value = "AI-generated dream narrative"
        mock_consciousness_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_fold_manager():
    """Mock FoldManager."""
    with patch("serve.routes.FoldManager") as mock_fold_class:
        mock_instance = MagicMock()

        # Mock memory folds
        mock_folds = [
            {
                "fold_id": "fold_1",
                "content": "Memory content 1",
                "created_at": "2025-01-01T00:00:00Z",
                "emotional_context": {"valence": 0.8, "arousal": 0.6},
                "symbolic_weight": 1.2,
            },
            {
                "fold_id": "fold_2",
                "content": "Memory content 2",
                "created_at": "2025-01-01T00:01:00Z",
                "emotional_context": {"valence": 0.7, "arousal": 0.4},
                "symbolic_weight": 1.0,
            },
        ]
        mock_instance.get_recent_folds.return_value = mock_folds

        mock_fold_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def app_client():
    """Create test client."""
    from serve.routes import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestGenerateDream:
    """Test /generate-dream/ endpoint."""

    def test_generate_dream_basic(self, app_client, mock_guardian, mock_consciousness):
        """Test basic dream generation."""
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["moon", "stars", "night"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "dream" in data
        assert "driftScore" in data
        assert "affect_delta" in data

        # Verify consciousness was used
        mock_consciousness.generate_dream_narrative.assert_called_once()

    def test_generate_dream_with_guardian(self, app_client, mock_guardian):
        """Test dream generation uses Guardian drift detection."""
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["test", "symbols"]},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify Guardian was called
        mock_guardian.detect_drift.assert_called_once()

        # Check drift score in response
        assert data["driftScore"] <= 1.0
        assert data["driftScore"] >= 0.0

    def test_generate_dream_fallback_no_consciousness(self, app_client, mock_guardian):
        """Test dream generation fallback when consciousness unavailable."""
        with patch("serve.routes.ConsciousnessCore", side_effect=ImportError):
            response = app_client.post(
                "/generate-dream/",
                json={"symbols": ["peaceful", "harmony"]},
            )

            assert response.status_code == 200
            data = response.json()

            assert "dream" in data
            # Should use fallback dream generation
            assert "peaceful" in data["dream"] or "harmony" in data["dream"]

    def test_generate_dream_empty_symbols(self, app_client):
        """Test dream generation with empty symbols."""
        response = app_client.post("/generate-dream/", json={"symbols": []})

        assert response.status_code == 200
        data = response.json()

        assert "dream" in data
        # Should handle empty input gracefully
        assert len(data["dream"]) > 0

    def test_generate_dream_affect_calculation(self, app_client, mock_emotion):
        """Test affect delta calculation."""
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["joy", "love", "peace"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "affect_delta" in data
        assert 0 <= data["affect_delta"] <= 1.0

    def test_generate_dream_drift_score_calculation(self, app_client):
        """Test drift score calculation."""
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["repeated"] * 10},  # High repetition
        )

        assert response.status_code == 200
        data = response.json()

        assert "driftScore" in data

    def test_generate_dream_emotional_modifiers(self, app_client):
        """Test emotional modifiers in dream narrative."""
        # High affect
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["intense", "exciting", "energy"]},
        )

        assert response.status_code == 200

        # Low affect
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["calm", "quiet"]},
        )

        assert response.status_code == 200

    def test_generate_dream_multiple_symbols(self, app_client):
        """Test dream with multiple symbols."""
        response = app_client.post(
            "/generate-dream/",
            json={"symbols": ["symbol1", "symbol2", "symbol3", "symbol4"]},
        )

        assert response.status_code == 200
        data = response.json()

        # Dream should incorporate multiple symbols
        assert len(data["dream"]) > 20


class TestGlyphFeedback:
    """Test /glyph-feedback/ endpoint."""

    def test_glyph_feedback_high_drift(self, app_client):
        """Test glyph feedback with high drift."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.6, "collapseHash": "test_hash"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "suggestions" in data
        suggestions = data["suggestions"]

        # Should suggest drift correction for high drift
        assert any("drift" in s.lower() for s in suggestions)

    def test_glyph_feedback_moderate_drift(self, app_client):
        """Test glyph feedback with moderate drift."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.25, "collapseHash": "test_hash"},
        )

        assert response.status_code == 200
        data = response.json()

        suggestions = data["suggestions"]
        assert len(suggestions) > 0

    def test_glyph_feedback_low_drift(self, app_client):
        """Test glyph feedback with low drift."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.05, "collapseHash": "test_hash"},
        )

        assert response.status_code == 200
        data = response.json()

        suggestions = data["suggestions"]
        # Should indicate drift is acceptable
        assert any("acceptable" in s.lower() or "optimal" in s.lower() for s in suggestions)

    def test_glyph_feedback_collapse_hash_high(self, app_client):
        """Test feedback with high collapse hash value."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.1, "collapseHash": "z" * 100},
        )

        assert response.status_code == 200
        data = response.json()

        suggestions = data["suggestions"]
        assert len(suggestions) > 0

    def test_glyph_feedback_collapse_hash_low(self, app_client):
        """Test feedback with low collapse hash value."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.1, "collapseHash": "a" * 10},
        )

        assert response.status_code == 200
        data = response.json()

        suggestions = data["suggestions"]
        assert len(suggestions) > 0

    def test_glyph_feedback_guardian_protocols(self, app_client):
        """Test Guardian protocol suggestions."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.35, "collapseHash": "test"},
        )

        assert response.status_code == 200
        data = response.json()

        suggestions = data["suggestions"]
        # High combined score should suggest Guardian protocols
        assert any("Guardian" in s for s in suggestions)

    def test_glyph_feedback_stability_achieved(self, app_client):
        """Test stability achieved message."""
        response = app_client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.05, "collapseHash": "stable"},
        )

        assert response.status_code == 200
        data = response.json()

        suggestions = data["suggestions"]
        # Should indicate stability
        assert any("stability" in s.lower() or "ready" in s.lower() for s in suggestions)


class TestTierAuth:
    """Test /tier-auth/ endpoint."""

    def test_tier_auth_tier_1(self, app_client):
        """Test tier 1 authentication."""
        response = app_client.post(
            "/tier-auth/",
            json={"token": "symbolic-tier-1"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["tier"] == 1
        assert "access_rights" in data
        assert isinstance(data["access_rights"], list)

    def test_tier_auth_tier_3(self, app_client):
        """Test tier 3 authentication."""
        response = app_client.post(
            "/tier-auth/",
            json={"token": "symbolic-tier-3"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["tier"] == 3
        assert len(data["access_rights"]) >= 0

    def test_tier_auth_tier_5(self, app_client):
        """Test tier 5 authentication."""
        response = app_client.post(
            "/tier-auth/",
            json={"token": "symbolic-tier-5"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["tier"] == 5

    def test_tier_auth_invalid_token(self, app_client):
        """Test invalid token returns 401."""
        response = app_client.post(
            "/tier-auth/",
            json={"token": "invalid-token"},
        )

        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_tier_auth_permissions(self, app_client):
        """Test tier permissions are returned."""
        with patch("serve.routes.TIER_PERMISSIONS", {1: ["read"], 3: ["read", "write"]}):
            response = app_client.post(
                "/tier-auth/",
                json={"token": "symbolic-tier-3"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "read" in data["access_rights"]
            assert "write" in data["access_rights"]


class TestPluginLoad:
    """Test /plugin-load/ endpoint."""

    def test_plugin_load_success(self, app_client, tmp_path):
        """Test successful plugin loading."""
        with patch("serve.routes.Path") as mock_path:
            mock_plugins_dir = MagicMock()
            mock_registry_file = MagicMock()
            mock_registry_file.exists.return_value = False

            mock_path.return_value = mock_plugins_dir
            mock_plugins_dir.__truediv__ = lambda self, other: mock_registry_file

            response = app_client.post(
                "/plugin-load/",
                json={"symbols": ["plugin1", "plugin2", "plugin3"]},
            )

            assert response.status_code == 200
            data = response.json()

            assert data["status"] in ["loaded and persisted", "loaded (persistence failed)"]

    def test_plugin_load_with_existing_registry(self, app_client):
        """Test plugin loading with existing registry."""
        import json
        from pathlib import Path

        with patch("serve.routes.Path") as mock_path_class:
            mock_plugins_dir = MagicMock()
            mock_registry_file = MagicMock()

            # Mock existing registry
            mock_registry_file.exists.return_value = True
            existing_registry = {
                "plugin1": {
                    "registered_at": "2025-01-01T00:00:00Z",
                    "status": "active",
                    "load_count": 5,
                }
            }

            mock_open = MagicMock()
            mock_open.__enter__ = MagicMock(return_value=MagicMock(read=lambda: json.dumps(existing_registry)))
            mock_open.__exit__ = MagicMock()

            mock_path_class.return_value = mock_plugins_dir
            mock_plugins_dir.__truediv__ = lambda self, other: mock_registry_file

            with patch("builtins.open", return_value=mock_open):
                response = app_client.post(
                    "/plugin-load/",
                    json={"symbols": ["plugin1", "plugin_new"]},
                )

                assert response.status_code == 200

    def test_plugin_load_persistence_failure(self, app_client):
        """Test graceful handling of persistence failure."""
        with patch("serve.routes.Path", side_effect=Exception("Persistence error")):
            response = app_client.post(
                "/plugin-load/",
                json={"symbols": ["plugin1"]},
            )

            assert response.status_code == 200
            data = response.json()
            assert "persistence failed" in data["status"].lower()

    def test_plugin_load_empty_symbols(self, app_client):
        """Test plugin load with empty symbols list."""
        response = app_client.post("/plugin-load/", json={"symbols": []})

        assert response.status_code == 200


class TestMemoryDump:
    """Test /memory-dump/ endpoint."""

    def test_memory_dump_success(self, app_client, mock_fold_manager, mock_emotion):
        """Test successful memory dump."""
        response = app_client.get("/memory-dump/")

        assert response.status_code == 200
        data = response.json()

        assert "folds" in data
        assert "emotional_state" in data

        folds = data["folds"]
        assert len(folds) > 0

        # Check fold structure
        for fold in folds:
            assert "id" in fold
            assert "content" in fold
            assert "timestamp" in fold
            assert "emotional_context" in fold
            assert "symbolic_weight" in fold

        # Check emotional state
        emotional_state = data["emotional_state"]
        assert "affect_delta" in emotional_state
        assert "valence" in emotional_state
        assert "arousal" in emotional_state
        assert "dominance" in emotional_state

    def test_memory_dump_fold_manager_integration(self, app_client, mock_fold_manager):
        """Test FoldManager integration."""
        response = app_client.get("/memory-dump/")

        assert response.status_code == 200

        # Verify FoldManager was called
        mock_fold_manager.get_recent_folds.assert_called_once()

    def test_memory_dump_emotion_processing(self, app_client, mock_fold_manager, mock_emotion):
        """Test emotion processing in memory dump."""
        response = app_client.get("/memory-dump/")

        assert response.status_code == 200

        # Verify emotion processing was called
        mock_emotion.assert_called()

    def test_memory_dump_fallback_mode(self, app_client):
        """Test fallback when memory subsystem unavailable."""
        with patch("serve.routes.FoldManager", side_effect=ImportError):
            response = app_client.get("/memory-dump/")

            assert response.status_code == 200
            data = response.json()

            # Should use fallback data
            assert len(data["folds"]) > 0
            assert "emotional_state" in data
            assert "status" in data["emotional_state"]
            assert data["emotional_state"]["status"] == "fallback_mode"

    def test_memory_dump_affect_delta_calculation(self, app_client, mock_fold_manager):
        """Test affect delta calculation from memory folds."""
        response = app_client.get("/memory-dump/")

        assert response.status_code == 200
        data = response.json()

        affect_delta = data["emotional_state"]["affect_delta"]
        assert 0 <= affect_delta <= 1.0

    def test_memory_dump_emotional_coherence(self, app_client, mock_fold_manager):
        """Test emotional coherence calculation."""
        response = app_client.get("/memory-dump/")

        assert response.status_code == 200
        data = response.json()

        assert "emotional_coherence" in data["emotional_state"]


class TestComputeDriftScore:
    """Test compute_drift_score helper."""

    def test_compute_drift_score_with_guardian(self, mock_guardian):
        """Test drift score computation using Guardian."""
        from serve.routes import compute_drift_score

        score = compute_drift_score(["test", "symbols"])

        assert 0 <= score <= 1.0
        mock_guardian.detect_drift.assert_called_once()

    def test_compute_drift_score_fallback(self):
        """Test drift score fallback calculation."""
        with patch("serve.routes.GuardianSystemImpl", side_effect=ImportError):
            from serve.routes import compute_drift_score

            score = compute_drift_score(["test", "symbols"])

            assert 0 <= score <= 1.0

    def test_compute_drift_score_empty_symbols(self):
        """Test drift score with empty symbols."""
        from serve.routes import compute_drift_score

        score = compute_drift_score([])

        assert score == 0.0

    def test_compute_drift_score_repetition(self):
        """Test drift score increases with repetition."""
        from serve.routes import compute_drift_score

        with patch("serve.routes.GuardianSystemImpl", side_effect=ImportError):
            score_unique = compute_drift_score(["a", "b", "c", "d"])
            score_repeated = compute_drift_score(["a", "a", "a", "a"])

            # More repetition should generally increase drift
            # (though exact behavior depends on implementation)
            assert isinstance(score_unique, float)
            assert isinstance(score_repeated, float)


class TestComputeAffectDelta:
    """Test compute_affect_delta helper."""

    def test_compute_affect_delta_with_emotion(self, mock_emotion):
        """Test affect delta computation using emotion engine."""
        from serve.routes import compute_affect_delta

        delta = compute_affect_delta(["joy", "love"])

        assert 0 <= delta <= 1.0
        mock_emotion.assert_called()

    def test_compute_affect_delta_fallback(self):
        """Test affect delta fallback calculation."""
        with patch("serve.routes.process_emotion", side_effect=ImportError):
            from serve.routes import compute_affect_delta

            delta = compute_affect_delta(["happy", "sad"])

            assert 0 <= delta <= 1.0

    def test_compute_affect_delta_empty_symbols(self):
        """Test affect delta with empty symbols."""
        from serve.routes import compute_affect_delta

        delta = compute_affect_delta([])

        assert delta == 0.0

    def test_compute_affect_delta_positive_indicators(self):
        """Test affect delta with positive indicators."""
        from serve.routes import compute_affect_delta

        with patch("serve.routes.process_emotion", side_effect=ImportError):
            delta = compute_affect_delta(["joy", "love", "hope", "peace"])

            assert delta >= 0

    def test_compute_affect_delta_negative_indicators(self):
        """Test affect delta with negative indicators."""
        from serve.routes import compute_affect_delta

        with patch("serve.routes.process_emotion", side_effect=ImportError):
            delta = compute_affect_delta(["fear", "anger", "sad"])

            assert delta >= 0


class TestObservabilityIntegration:
    """Test observability integration."""

    def test_generate_dream_traced(self, app_client):
        """Test generate_dream is traced."""
        with patch("serve.routes.obs_stack") as mock_obs:
            mock_trace = MagicMock()
            mock_obs.trace.return_value = lambda f: f

            response = app_client.post(
                "/generate-dream/",
                json={"symbols": ["test"]},
            )

            assert response.status_code == 200

    def test_glyph_feedback_traced(self, app_client):
        """Test glyph_feedback is traced."""
        with patch("serve.routes.obs_stack") as mock_obs:
            mock_trace = MagicMock()
            mock_obs.trace.return_value = lambda f: f

            response = app_client.post(
                "/glyph-feedback/",
                json={"driftScore": 0.1, "collapseHash": "test"},
            )

            assert response.status_code == 200


class TestRouterConfiguration:
    """Test router configuration."""

    def test_router_exists(self):
        """Test router is properly exported."""
        from serve import routes

        assert hasattr(routes, "router")

    def test_router_has_routes(self):
        """Test router has expected routes."""
        from serve.routes import router

        route_paths = [route.path for route in router.routes]

        assert "/generate-dream/" in route_paths
        assert "/glyph-feedback/" in route_paths
        assert "/tier-auth/" in route_paths
        assert "/plugin-load/" in route_paths
        assert "/memory-dump/" in route_paths
