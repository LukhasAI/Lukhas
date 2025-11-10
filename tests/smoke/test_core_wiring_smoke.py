"""
Smoke Tests for LUKHAS Core Wiring
===================================

Lightweight smoke tests that run quickly in CI to validate:
- API endpoints are reachable
- Feature flags work correctly
- Basic request/response cycles succeed
- No critical errors on startup

Run with: pytest tests/smoke/test_core_wiring_smoke.py -v
"""
import os
import pytest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestDreamsAPISmoke:
    """Smoke tests for Dreams API"""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app with dreams router"""
        app = FastAPI()
        from lukhas_website.lukhas.api.dreams import router
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_health_endpoint_reachable(self, client):
        """Health check endpoint is reachable"""
        response = client.get("/api/v1/dreams/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "dreams"

    def test_simulate_disabled_by_default(self, client):
        """Simulate endpoint returns 503 when disabled"""
        response = client.post(
            "/api/v1/dreams/simulate",
            json={"seed": "test"}
        )
        assert response.status_code == 503

    def test_mesh_disabled_by_default(self, client):
        """Mesh endpoint returns 503 when disabled"""
        response = client.post(
            "/api/v1/dreams/mesh",
            json={"seeds": ["test1", "test2"]}
        )
        assert response.status_code == 503

    def test_simulate_with_enabled_flag(self, client):
        """Simulate endpoint works when enabled"""
        from lukhas_website.lukhas.api import dreams

        with patch.object(dreams, 'is_enabled', return_value=True):
            response = client.post(
                "/api/v1/dreams/simulate",
                json={"seed": "smoke_test", "context": {}}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestGlyphsAPISmoke:
    """Smoke tests for GLYPHs API"""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app with glyphs router"""
        app = FastAPI()
        from lukhas_website.lukhas.api.glyphs import router
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_health_endpoint_reachable(self, client):
        """Health check endpoint is reachable"""
        response = client.get("/api/v1/glyphs/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "glyphs"

    def test_encode_disabled_by_default(self, client):
        """Encode endpoint returns 503 when disabled"""
        response = client.post(
            "/api/v1/glyphs/encode",
            json={"concept": "test"}
        )
        assert response.status_code == 503

    def test_validate_always_available(self, client):
        """Validate endpoint works even when disabled"""
        response = client.post(
            "/api/v1/glyphs/validate",
            json={"glyph_data": {"concept": "test"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data

    def test_bind_validation_works(self, client):
        """Bind endpoint validates input even when disabled"""
        from lukhas_website.lukhas.api import glyphs

        with patch.object(glyphs, 'is_enabled', return_value=True):
            # Missing concept should fail validation
            response = client.post(
                "/api/v1/glyphs/bind",
                json={"glyph_data": {}, "memory_id": "mem_123"}
            )
            assert response.status_code == 400


class TestDriftAPISmoke:
    """Smoke tests for Drift Monitoring API"""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app with drift router"""
        app = FastAPI()
        from lukhas_website.lukhas.api.drift import router
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_health_endpoint_reachable(self, client):
        """Health check endpoint is reachable"""
        response = client.get("/api/v1/drift/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "drift"

    def test_update_disabled_by_default(self, client):
        """Update endpoint returns 503 when disabled"""
        response = client.post(
            "/api/v1/drift/update",
            json={
                "user_id": "user_123",
                "intent": [1.0, 0.0],
                "action": [0.9, 0.1]
            }
        )
        assert response.status_code == 503

    def test_config_always_available(self, client):
        """Config endpoint works even when disabled"""
        from lukhas_website.lukhas.api import drift

        with patch.object(drift, '_DRIFT_AVAILABLE', True):
            response = client.get("/api/v1/drift/config/experimental")
            assert response.status_code == 200
            data = response.json()
            assert "warn_threshold" in data

    def test_update_validates_vector_lengths(self, client):
        """Update endpoint validates vector length matching"""
        from lukhas_website.lukhas.api import drift

        with patch.object(drift, '_DRIFT_ENABLED', True):
            with patch.object(drift, '_DRIFT_AVAILABLE', True):
                # Mismatched vector lengths
                response = client.post(
                    "/api/v1/drift/update",
                    json={
                        "user_id": "user_123",
                        "intent": [1.0, 0.0, 0.5],
                        "action": [0.9, 0.1]
                    }
                )
                assert response.status_code == 400


class TestWrapperModulesSmoke:
    """Smoke tests for wrapper modules"""

    def test_consciousness_wrapper_imports(self):
        """Consciousness wrapper can be imported"""
        import lukhas.consciousness
        assert hasattr(lukhas.consciousness, 'is_enabled')

    def test_dream_wrapper_imports(self):
        """Dream wrapper can be imported"""
        import lukhas.dream
        assert hasattr(lukhas.dream, 'is_enabled')
        assert hasattr(lukhas.dream, 'simulate_dream')

    def test_glyphs_wrapper_imports(self):
        """Glyphs wrapper can be imported"""
        import lukhas.glyphs
        assert hasattr(lukhas.glyphs, 'is_enabled')
        assert hasattr(lukhas.glyphs, 'validate_glyph')

    def test_wrappers_disabled_by_default(self):
        """All wrappers are disabled by default"""
        import lukhas.consciousness
        import lukhas.dream
        import lukhas.glyphs

        # Clear any env vars
        with patch.dict(os.environ, {}, clear=False):
            for key in ['LUKHAS_CONSCIOUSNESS_ENABLED', 'LUKHAS_DREAMS_ENABLED',
                       'LUKHAS_GLYPHS_ENABLED']:
                if key in os.environ:
                    del os.environ[key]

            # Wrappers should report as disabled
            assert not lukhas.consciousness.is_enabled()
            assert not lukhas.dream.is_enabled()
            assert not lukhas.glyphs.is_enabled()


class TestFeatureFlagSmoke:
    """Smoke tests for feature flag behavior"""

    def test_dreams_flag_parsing(self):
        """Dreams flag parses correctly"""
        import lukhas.dream

        # Test various values
        test_cases = [
            ("1", True),
            ("0", False),
            ("true", False),  # Only "1" enables
            ("", False),
        ]

        for value, expected in test_cases:
            with patch.dict(os.environ, {'LUKHAS_DREAMS_ENABLED': value}):
                # Need to reload to pick up env change
                import importlib
                importlib.reload(lukhas.dream)

                result = lukhas.dream.DREAMS_ENABLED
                assert result == expected, f"Value '{value}' should result in {expected}"

    def test_parallel_dreams_requires_dreams_enabled(self):
        """Parallel dreams flag requires dreams enabled"""
        import lukhas.dream

        with patch.dict(os.environ, {
            'LUKHAS_DREAMS_ENABLED': '0',
            'LUKHAS_PARALLEL_DREAMS': '1'
        }):
            import importlib
            importlib.reload(lukhas.dream)

            # Parallel should not work if dreams disabled
            assert not lukhas.dream.is_parallel_enabled()


class TestStartupSmoke:
    """Smoke tests for application startup"""

    def test_serve_main_imports(self):
        """Main server module can be imported"""
        import serve.main
        assert hasattr(serve.main, 'app')

    def test_routers_safe_import(self):
        """Router safe import works correctly"""
        from serve.main import _safe_import_router

        # Test with non-existent module
        router = _safe_import_router('nonexistent.module', 'router')
        assert router is None

        # Test with valid module
        router = _safe_import_router('lukhas_website.lukhas.api.dreams', 'router')
        assert router is not None


class TestErrorHandlingSmoke:
    """Smoke tests for error handling"""

    def test_invalid_json_returns_422(self):
        """Invalid JSON returns 422 Unprocessable Entity"""
        app = FastAPI()
        from lukhas_website.lukhas.api.dreams import router
        app.include_router(router)
        client = TestClient(app)

        response = client.post(
            "/api/v1/dreams/simulate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_field_returns_422(self):
        """Missing required field returns 422"""
        app = FastAPI()
        from lukhas_website.lukhas.api.dreams import router
        app.include_router(router)
        client = TestClient(app)

        # Missing 'seed' field
        response = client.post(
            "/api/v1/dreams/simulate",
            json={"context": {}}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
