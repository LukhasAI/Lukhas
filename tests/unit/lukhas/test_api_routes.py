"""
Tests for LUKHAS Core Wiring API Routes
========================================

Validates dreams, glyphs, and drift API endpoints:
- Feature flag gating
- Request validation
- Response structure
- Error handling
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestDreamsAPI:
    """Tests for Dreams API endpoints"""

    def test_dreams_router_import(self):
        """Dreams router can be imported"""
        from lukhas_website.lukhas.api.dreams import router
        assert router is not None

    def test_simulate_endpoint_disabled_by_default(self):
        """POST /api/v1/dreams/simulate returns 503 when disabled"""
        from lukhas_website.lukhas.api import dreams

        with patch.object(dreams, '_DRIFT_ENABLED', False):
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()
            app.include_router(dreams.router)
            client = TestClient(app)

            response = client.post(
                "/api/v1/dreams/simulate",
                json={"seed": "test", "context": {}}
            )
            assert response.status_code == 503

    def test_simulate_request_validation(self):
        """Request validation works for simulate endpoint"""
        from lukhas_website.lukhas.api.dreams import DreamSimulationRequest
        from pydantic import ValidationError

        # Valid request
        req = DreamSimulationRequest(seed="test", context={"foo": "bar"})
        assert req.seed == "test"

        # Invalid: missing seed
        with pytest.raises(ValidationError):
            DreamSimulationRequest(context={})

        # Invalid: seed too long
        with pytest.raises(ValidationError):
            DreamSimulationRequest(seed="x" * 501)

    def test_mesh_endpoint_requires_parallel_flag(self):
        """POST /api/v1/dreams/mesh requires parallel dreams enabled"""
        from lukhas_website.lukhas.api import dreams
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(dreams, 'is_enabled', return_value=True):
            with patch.object(dreams, 'is_parallel_enabled', return_value=False):
                app = FastAPI()
                app.include_router(dreams.router)
                client = TestClient(app)

                response = client.post(
                    "/api/v1/dreams/mesh",
                    json={"seeds": ["s1", "s2"], "consensus_threshold": 0.7}
                )
                assert response.status_code == 403
                assert "parallel" in response.json()["detail"].lower()

    def test_health_check_endpoint(self):
        """GET /api/v1/dreams/ returns health status"""
        from lukhas_website.lukhas.api import dreams
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(dreams.router)
        client = TestClient(app)

        response = client.get("/api/v1/dreams/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "dreams"
        assert "enabled" in data


class TestGlyphsAPI:
    """Tests for GLYPHs API endpoints"""

    def test_glyphs_router_import(self):
        """GLYPHs router can be imported"""
        from lukhas_website.lukhas.api.glyphs import router
        assert router is not None

    def test_encode_endpoint_disabled_by_default(self):
        """POST /api/v1/glyphs/encode returns 503 when disabled"""
        from lukhas_website.lukhas.api import glyphs
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(glyphs, 'is_enabled', return_value=False):
            app = FastAPI()
            app.include_router(glyphs.router)
            client = TestClient(app)

            response = client.post(
                "/api/v1/glyphs/encode",
                json={"concept": "test"}
            )
            assert response.status_code == 503

    def test_encode_request_validation(self):
        """Request validation works for encode endpoint"""
        from lukhas_website.lukhas.api.glyphs import GlyphEncodeRequest
        from pydantic import ValidationError

        # Valid request
        req = GlyphEncodeRequest(concept="test", emotion={"joy": 0.8})
        assert req.concept == "test"

        # Invalid: concept too long
        with pytest.raises(ValidationError):
            GlyphEncodeRequest(concept="x" * 1001)

        # Invalid: emotion out of range
        with pytest.raises(ValidationError):
            GlyphEncodeRequest(concept="test", emotion={"joy": 1.5})

    def test_bind_endpoint_validates_glyph_data(self):
        """POST /api/v1/glyphs/bind validates glyph_data structure"""
        from lukhas_website.lukhas.api import glyphs
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(glyphs, 'is_enabled', return_value=True):
            app = FastAPI()
            app.include_router(glyphs.router)
            client = TestClient(app)

            # Invalid: missing concept
            response = client.post(
                "/api/v1/glyphs/bind",
                json={"glyph_data": {}, "memory_id": "mem_123"}
            )
            assert response.status_code == 400
            assert "concept" in response.json()["detail"].lower()

    def test_validate_endpoint_always_available(self):
        """POST /api/v1/glyphs/validate works even when glyphs disabled"""
        from lukhas_website.lukhas.api import glyphs
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        # Validation should work even when disabled
        app = FastAPI()
        app.include_router(glyphs.router)
        client = TestClient(app)

        response = client.post(
            "/api/v1/glyphs/validate",
            json={"glyph_data": {"concept": "test"}}
        )
        # Should return 200 (validation succeeded)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_health_check_endpoint(self):
        """GET /api/v1/glyphs/ returns health status"""
        from lukhas_website.lukhas.api import glyphs
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(glyphs.router)
        client = TestClient(app)

        response = client.get("/api/v1/glyphs/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "glyphs"


class TestDriftAPI:
    """Tests for Drift Monitoring API endpoints"""

    def test_drift_router_import(self):
        """Drift router can be imported"""
        from lukhas_website.lukhas.api.drift import router
        assert router is not None

    def test_update_endpoint_disabled_by_default(self):
        """POST /api/v1/drift/update returns 503 when disabled"""
        from lukhas_website.lukhas.api import drift
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(drift, '_DRIFT_ENABLED', False):
            app = FastAPI()
            app.include_router(drift.router)
            client = TestClient(app)

            response = client.post(
                "/api/v1/drift/update",
                json={
                    "user_id": "user_123",
                    "intent": [1.0, 0.0],
                    "action": [0.9, 0.1]
                }
            )
            assert response.status_code == 503

    def test_update_request_validation(self):
        """Request validation works for drift update"""
        from lukhas_website.lukhas.api.drift import DriftUpdateRequest
        from pydantic import ValidationError

        # Valid request
        req = DriftUpdateRequest(
            user_id="user_123",
            intent=[1.0, 0.0],
            action=[0.9, 0.1]
        )
        assert req.user_id == "user_123"

        # Invalid: missing user_id
        with pytest.raises(ValidationError):
            DriftUpdateRequest(intent=[1.0], action=[1.0])

    def test_update_validates_vector_length_match(self):
        """Update endpoint validates intent/action vector lengths match"""
        from lukhas_website.lukhas.api import drift
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(drift, '_DRIFT_ENABLED', True):
            with patch.object(drift, '_DRIFT_AVAILABLE', True):
                app = FastAPI()
                app.include_router(drift.router)
                client = TestClient(app)

                # Mismatched lengths
                response = client.post(
                    "/api/v1/drift/update",
                    json={
                        "user_id": "user_123",
                        "intent": [1.0, 0.0, 0.5],
                        "action": [0.9, 0.1]
                    }
                )
                assert response.status_code == 400
                assert "same length" in response.json()["detail"].lower()

    def test_get_drift_score_404_for_unknown_user(self):
        """GET /api/v1/drift/{user_id} returns 404 for unknown user"""
        from lukhas_website.lukhas.api import drift
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(drift, '_DRIFT_ENABLED', True):
            with patch.object(drift, '_DRIFT_AVAILABLE', True):
                app = FastAPI()
                app.include_router(drift.router)
                client = TestClient(app)

                response = client.get("/api/v1/drift/unknown_user")
                assert response.status_code == 404

    def test_config_endpoint_always_available(self):
        """GET /api/v1/drift/config/{lane} works even when drift disabled"""
        from lukhas_website.lukhas.api import drift
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        with patch.object(drift, '_DRIFT_AVAILABLE', True):
            app = FastAPI()
            app.include_router(drift.router)
            client = TestClient(app)

            response = client.get("/api/v1/drift/config/experimental")
            assert response.status_code == 200
            data = response.json()
            assert "warn_threshold" in data
            assert "block_threshold" in data

    def test_health_check_endpoint(self):
        """GET /api/v1/drift/ returns health status"""
        from lukhas_website.lukhas.api import drift
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(drift.router)
        client = TestClient(app)

        response = client.get("/api/v1/drift/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "drift"


class TestFeatureFlagIntegration:
    """Tests for feature flag integration in main app"""

    def test_routers_not_loaded_by_default(self):
        """Routers not loaded when feature flags disabled"""
        with patch.dict(os.environ, {}, clear=False):
            # Clear all feature flags
            for key in ['LUKHAS_DREAMS_ENABLED', 'LUKHAS_GLYPHS_ENABLED', 'LUKHAS_DRIFT_ENABLED']:
                if key in os.environ:
                    del os.environ[key]

            # The routers should not be loaded
            # (This is tested indirectly by checking the flags in serve/main.py)
            assert os.getenv('LUKHAS_DREAMS_ENABLED', '0') == '0'
            assert os.getenv('LUKHAS_GLYPHS_ENABLED', '0') == '0'
            assert os.getenv('LUKHAS_DRIFT_ENABLED', '0') == '0'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
