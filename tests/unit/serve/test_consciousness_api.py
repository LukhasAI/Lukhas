"""
Comprehensive unit tests for Consciousness API

Tests all endpoints, authorization, error handling, and integration points.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Import the router and components
from serve.consciousness_api import (
    router,
    require_admin,
    get_drift_detector,
    get_consciousness_engine,
    get_guardian,
    ConsciousnessStatus,
    AwarenessUpdate,
    DriftDetectionRequest,
    DriftDetectionResponse,
    MetricsResponse,
    _MockDriftDetector,
    _MockConsciousnessEngine,
    _MockGuardian,
)


# --- Fixtures ---
@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing."""
    return {
        "username": "admin_user",
        "role": "admin",
    }


@pytest.fixture
def mock_regular_user():
    """Mock regular user for testing."""
    return {
        "username": "regular_user",
        "role": "user",
    }


@pytest.fixture
def mock_guest_user():
    """Mock guest user for testing."""
    return {
        "username": "guest_user",
        "role": "guest",
    }


@pytest.fixture
def drift_detector():
    """Fixture for drift detector."""
    return _MockDriftDetector()


@pytest.fixture
def consciousness_engine():
    """Fixture for consciousness engine."""
    return _MockConsciousnessEngine()


@pytest.fixture
def guardian():
    """Fixture for guardian."""
    return _MockGuardian()


@pytest.fixture
def app():
    """Create test FastAPI app."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


# --- Test Authorization ---
class TestAuthorization:
    """Test admin authorization dependency."""

    def test_require_admin_with_admin_role(self, mock_admin_user):
        """Test that admin users pass authorization."""
        result = require_admin(current_user=mock_admin_user)
        assert result == mock_admin_user

    def test_require_admin_with_user_role(self, mock_regular_user):
        """Test that regular users are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=mock_regular_user)

        assert exc_info.value.status_code == 403
        assert "Admin role required" in exc_info.value.detail

    def test_require_admin_with_guest_role(self, mock_guest_user):
        """Test that guests are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=mock_guest_user)

        assert exc_info.value.status_code == 403

    def test_require_admin_with_no_role(self):
        """Test that users without role are rejected."""
        user_without_role = {"username": "no_role_user"}
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=user_without_role)

        assert exc_info.value.status_code == 403


# --- Test Pydantic Models ---
class TestPydanticModels:
    """Test Pydantic model validation."""

    def test_awareness_update_valid(self):
        """Test valid awareness update."""
        update = AwarenessUpdate(
            new_level=0.8,
            reason="Testing awareness",
            metadata={"test": "data"}
        )
        assert update.new_level == 0.8
        assert update.reason == "Testing awareness"

    def test_awareness_update_invalid_level_high(self):
        """Test awareness update with level > 1.0."""
        with pytest.raises(ValueError):
            AwarenessUpdate(
                new_level=1.5,
                reason="Invalid level",
            )

    def test_awareness_update_invalid_level_low(self):
        """Test awareness update with level < 0.0."""
        with pytest.raises(ValueError):
            AwarenessUpdate(
                new_level=-0.5,
                reason="Invalid level",
            )

    def test_awareness_update_boundary_values(self):
        """Test awareness update with boundary values."""
        # Test 0.0
        update1 = AwarenessUpdate(new_level=0.0, reason="Minimum")
        assert update1.new_level == 0.0

        # Test 1.0
        update2 = AwarenessUpdate(new_level=1.0, reason="Maximum")
        assert update2.new_level == 1.0

    def test_drift_detection_request_valid(self):
        """Test valid drift detection request."""
        request = DriftDetectionRequest(
            baseline_state={"metric1": 100, "metric2": 200},
            current_state={"metric1": 110, "metric2": 190},
        )
        assert request.baseline_state["metric1"] == 100
        assert request.current_state["metric2"] == 190

    def test_drift_detection_request_empty_states(self):
        """Test drift detection with empty states."""
        request = DriftDetectionRequest(
            baseline_state={},
            current_state={},
        )
        assert request.baseline_state == {}
        assert request.current_state == {}


# --- Test Mock Implementations ---
class TestMockImplementations:
    """Test fallback mock implementations."""

    def test_mock_drift_detector_summarize(self, drift_detector):
        """Test mock drift detector summarize."""
        summary = drift_detector.summarize_layers()
        assert "layers" in summary
        assert "timestamp" in summary
        assert "reasoning" in summary["layers"]
        assert "memory" in summary["layers"]

    def test_mock_drift_detector_query(self, drift_detector):
        """Test mock drift detector query."""
        results = drift_detector.query_archived_snapshots()
        assert isinstance(results, list)
        assert len(results) == 0

    def test_mock_drift_detector_record(self, drift_detector):
        """Test mock drift detector record (no-op)."""
        # Should not raise any exception
        drift_detector.record_snapshot(
            layer_id="test",
            driftScore=0.1,
            affect_delta=0.05,
        )

    def test_mock_consciousness_engine_status(self, consciousness_engine):
        """Test mock consciousness engine status."""
        status = consciousness_engine.get_status()
        assert status["active"] is True
        assert "threads" in status
        assert "subsystems" in status
        assert status["threads"] == 3

    def test_mock_consciousness_engine_metrics(self, consciousness_engine):
        """Test mock consciousness engine metrics."""
        metrics = consciousness_engine.get_metrics()
        assert "processing_time_ms" in metrics
        assert "memory_usage_mb" in metrics
        assert "active_threads" in metrics
        assert metrics["processing_time_ms"] == 150

    def test_mock_guardian_is_active(self, guardian):
        """Test mock guardian is_active."""
        assert guardian.is_active() is True

    def test_mock_guardian_check_policy(self, guardian):
        """Test mock guardian check_policy."""
        result = guardian.check_policy("test_action")
        assert result["allowed"] is True
        assert "reason" in result


# --- Test Endpoints ---
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/consciousness/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "components" in data

    def test_health_check_components(self, client):
        """Test health check includes component status."""
        response = client.get("/consciousness/health")
        data = response.json()
        components = data["components"]
        assert "drift_detector" in components
        assert "consciousness_engine" in components
        assert "guardian" in components
        assert isinstance(components["drift_detector"], bool)


class TestStatusEndpoint:
    """Test consciousness status endpoint."""

    @patch("serve.consciousness_api.get_drift_detector")
    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_get_status_endpoint(self, mock_engine, mock_drift, client):
        """Test GET /status endpoint."""
        # Setup mocks
        mock_engine.return_value = _MockConsciousnessEngine()
        mock_drift.return_value = _MockDriftDetector()

        response = client.get("/consciousness/status")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["active", "idle", "degraded"]
        assert 0.0 <= data["awareness_level"] <= 1.0
        assert data["active_threads"] >= 0
        assert "subsystems" in data
        assert "drift_score" in data
        assert "last_update" in data

    @patch("serve.consciousness_api.get_drift_detector")
    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_get_status_subsystems(self, mock_engine, mock_drift, client):
        """Test status endpoint returns subsystem information."""
        mock_engine.return_value = _MockConsciousnessEngine()
        mock_drift.return_value = _MockDriftDetector()

        response = client.get("/consciousness/status")
        data = response.json()

        subsystems = data["subsystems"]
        assert "reasoning" in subsystems
        assert "memory" in subsystems
        assert "learning" in subsystems

    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_status_error_handling(self, mock_engine, client):
        """Test status endpoint error handling."""
        mock_engine.side_effect = Exception("Engine failure")

        response = client.get("/consciousness/status")
        assert response.status_code == 500
        assert "Failed to get consciousness status" in response.json()["detail"]


class TestMetricsEndpoint:
    """Test metrics endpoint."""

    @patch("serve.consciousness_api.get_drift_detector")
    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_get_metrics_endpoint(self, mock_engine, mock_drift, client):
        """Test GET /metrics endpoint."""
        mock_engine.return_value = _MockConsciousnessEngine()
        mock_drift.return_value = _MockDriftDetector()

        response = client.get("/consciousness/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "processing_time_avg_ms" in data
        assert "memory_usage_mb" in data
        assert "active_threads" in data
        assert "drift_history" in data
        assert isinstance(data["drift_history"], list)

    @patch("serve.consciousness_api.get_drift_detector")
    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_metrics_drift_history(self, mock_engine, mock_drift, client):
        """Test metrics endpoint includes drift history."""
        mock_engine.return_value = _MockConsciousnessEngine()
        mock_drift.return_value = _MockDriftDetector()

        response = client.get("/consciousness/metrics")
        data = response.json()

        drift_history = data["drift_history"]
        assert len(drift_history) >= 0
        if len(drift_history) > 0:
            item = drift_history[0]
            assert "layer_id" in item
            assert "drift_score" in item
            assert "affect_delta" in item

    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_metrics_error_handling(self, mock_engine, client):
        """Test metrics endpoint error handling."""
        mock_engine.side_effect = Exception("Metrics failure")

        response = client.get("/consciousness/metrics")
        assert response.status_code == 500


class TestDriftDetectEndpoint:
    """Test drift detection endpoint."""

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_endpoint(self, mock_drift, client):
        """Test POST /drift/detect endpoint."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": 100, "metric2": 200},
            "current_state": {"metric1": 110, "metric2": 190},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "drift_score" in data
        assert "drift_details" in data
        assert "threshold_exceeded" in data
        assert "recommendation" in data
        assert isinstance(data["drift_score"], float)
        assert data["drift_score"] >= 0.0

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_no_drift(self, mock_drift, client):
        """Test drift detection with identical states."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": 100},
            "current_state": {"metric1": 100},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        data = response.json()

        # Drift should be 0 for identical states
        assert data["drift_score"] == 0.0
        assert data["threshold_exceeded"] is False

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_high_drift(self, mock_drift, client):
        """Test drift detection with high drift."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": 100},
            "current_state": {"metric1": 200},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        data = response.json()

        # High drift should be detected
        assert data["drift_score"] > 0.0
        assert "recommendation" in data

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_details(self, mock_drift, client):
        """Test drift detection includes detailed analysis."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": 100, "metric2": 50},
            "current_state": {"metric1": 120, "metric2": 45},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        data = response.json()

        details = data["drift_details"]
        assert "components" in details
        assert "num_components" in details
        assert "thresholds" in details

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_error_handling(self, mock_drift, client):
        """Test drift detection error handling."""
        mock_drift.side_effect = Exception("Drift detector failure")

        request_data = {
            "baseline_state": {"metric1": 100},
            "current_state": {"metric1": 110},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        assert response.status_code == 500


class TestAwarenessUpdateEndpoint:
    """Test awareness update endpoint (requires admin)."""

    @patch("serve.consciousness_api.require_admin")
    @patch("serve.consciousness_api.get_consciousness_engine")
    def test_update_awareness_success(self, mock_engine, mock_admin, client, mock_admin_user):
        """Test successful awareness update."""
        mock_admin.return_value = mock_admin_user
        mock_engine.return_value = _MockConsciousnessEngine()

        # Mock the dependency
        from serve.consciousness_api import update_awareness
        with patch("serve.consciousness_api.Depends"):
            request_data = {
                "new_level": 0.9,
                "reason": "System optimization",
                "metadata": {"source": "test"}
            }

            # Direct function call (bypassing auth for unit test)
            import asyncio
            result = asyncio.run(update_awareness(
                data=AwarenessUpdate(**request_data),
                user=mock_admin_user
            ))

            assert result["success"] is True
            assert result["new_level"] == 0.9
            assert result["reason"] == "System optimization"

    def test_update_awareness_invalid_level(self, client):
        """Test awareness update with invalid level."""
        request_data = {
            "new_level": 1.5,  # Invalid: > 1.0
            "reason": "Test",
        }

        response = client.post("/consciousness/awareness/update", json=request_data)
        # Will fail validation
        assert response.status_code == 422  # Validation error


class TestAwarenessHistoryEndpoint:
    """Test awareness history endpoint."""

    @patch("serve.consciousness_api.require_admin")
    def test_get_awareness_history(self, mock_admin, client, mock_admin_user):
        """Test GET /awareness/history endpoint."""
        mock_admin.return_value = mock_admin_user

        # Direct function call to test logic
        from serve.consciousness_api import get_awareness_history
        import asyncio

        result = asyncio.run(get_awareness_history(limit=5, user=mock_admin_user))

        assert "total_updates" in result
        assert "updates" in result
        assert "current_level" in result
        assert isinstance(result["updates"], list)


# --- Test Drift Detection Logic ---
class TestDriftCalculation:
    """Test drift calculation logic."""

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_calculation_identical_states(self, mock_drift, client):
        """Test drift calculation with identical states returns 0."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": 100, "metric2": 200, "metric3": 50},
            "current_state": {"metric1": 100, "metric2": 200, "metric3": 50},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        data = response.json()

        assert data["drift_score"] == 0.0

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_calculation_different_keys(self, mock_drift, client):
        """Test drift handles different keys between states."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": 100, "metric2": 200},
            "current_state": {"metric1": 110, "metric3": 50},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        data = response.json()

        # Should handle gracefully
        assert "drift_score" in data
        assert data["drift_score"] >= 0.0


# --- Test Router Configuration ---
class TestRouterConfiguration:
    """Test router configuration."""

    def test_router_exists(self):
        """Test that router is properly configured."""
        assert router is not None

    def test_router_prefix(self):
        """Test router has correct prefix."""
        assert router.prefix == "/consciousness"

    def test_router_tags(self):
        """Test router has correct tags."""
        assert "consciousness" in router.tags


# --- Test Edge Cases ---
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_empty_states(self, mock_drift, client):
        """Test drift detection with empty states."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {},
            "current_state": {},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["drift_score"] == 0.0

    @patch("serve.consciousness_api.get_drift_detector")
    def test_drift_detect_non_numeric_values(self, mock_drift, client):
        """Test drift detection handles non-numeric values."""
        mock_drift.return_value = _MockDriftDetector()

        request_data = {
            "baseline_state": {"metric1": "text", "metric2": 100},
            "current_state": {"metric1": "other", "metric2": 110},
        }

        response = client.post("/consciousness/drift/detect", json=request_data)
        assert response.status_code == 200
        # Should only calculate for numeric values


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
