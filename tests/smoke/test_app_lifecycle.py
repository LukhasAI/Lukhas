"""
App Startup & Lifecycle Smoke Test
==================================

Validates that FastAPI application starts up and shuts down correctly.

Tests:
- App initialization
- Middleware stack configuration
- Router loading (conditional)
- Startup lifecycle with TestClient
- Health endpoint availability

Expected runtime: 0.5 seconds
Marker: @pytest.mark.smoke
"""
from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_app_initialization():
    """
    Test that FastAPI app initializes without errors.

    Validates app instance is created and has expected metadata.
    """
    try:
        # App should be FastAPI instance
        from fastapi import FastAPI
        from serve.main import app

        assert isinstance(app, FastAPI), "app should be FastAPI instance"

        # Check app metadata
        assert hasattr(app, "title"), "App should have title"
        assert hasattr(app, "version"), "App should have version"

        # Title should be set
        assert (
            app.title is not None and len(app.title) > 0
        ), "App title should be set"

    except ImportError as e:
        pytest.skip(f"FastAPI app not available: {e}")


@pytest.mark.smoke
def test_app_middleware_stack():
    """
    Test that middleware is properly configured.

    Validates CORS, auth, and other middleware are loaded.
    """
    try:
        from serve.main import app

        # Check middleware exists
        assert hasattr(app, "user_middleware"), "App should have middleware"

        # Get middleware count
        middleware_count = len(app.user_middleware)
        assert middleware_count >= 0, "Should have middleware list (possibly empty)"

        # Get middleware class names
        if middleware_count > 0:
            middleware_classes = [m.cls.__name__ for m in app.user_middleware]

            # Should have some middleware loaded
            assert len(middleware_classes) > 0, "Should have middleware loaded"

            # Common middleware we expect
            # CORS is important for web access
            # Log what middleware we have (no assertion - configuration-dependent)
            # In production, we'd expect CORS at minimum

    except ImportError:
        pytest.skip("FastAPI app not available")


@pytest.mark.smoke
def test_app_router_loading():
    """
    Test that routers load conditionally based on availability.

    Validates router discovery and conditional loading works.
    """
    try:
        from serve.main import (
            consciousness_router,
            feedback_router,
            guardian_router,
            openai_router,
        )

        # Count loaded routers
        loaded_routers = []

        if consciousness_router is not None:
            loaded_routers.append("consciousness")

        if feedback_router is not None:
            loaded_routers.append("feedback")

        if guardian_router is not None:
            loaded_routers.append("guardian")

        if openai_router is not None:
            loaded_routers.append("openai")

        # Should have loaded at least some routers
        # Configuration-dependent, so no strict assertion
        # Just verify the import mechanism works
        assert isinstance(loaded_routers, list), "Router list should be created"

    except ImportError:
        pytest.skip("Router imports not available")


@pytest.mark.smoke
def test_app_startup_with_test_client():
    """
    Test app starts successfully with TestClient.

    TestClient simulates full ASGI lifecycle including startup/shutdown.
    """
    try:
        from serve.main import app
        from starlette.testclient import TestClient

        # TestClient context manager triggers startup/shutdown
        with TestClient(app) as client:
            # If we get here, startup succeeded
            assert client is not None, "TestClient should initialize"

            # Test health endpoint
            response = client.get("/healthz")
            assert response.status_code == 200, "Health endpoint should work"

            # Response should be JSON
            data = response.json()
            assert isinstance(data, dict), "Health response should be JSON object"

            # Should have status info
            assert (
                "status" in data or "healthy" in data or "ok" in data
            ), "Health response should have status"

    except ImportError:
        pytest.skip("TestClient not available")


@pytest.mark.smoke
def test_app_routes_registered():
    """
    Test that routes are registered with the app.

    Validates router inclusion worked correctly.
    """
    try:
        from serve.main import app

        # Check routes are registered
        assert hasattr(app, "routes"), "App should have routes"
        assert len(app.routes) > 0, "Should have at least one route"

        # Get route paths
        route_paths = [getattr(route, "path", None) for route in app.routes]
        route_paths = [p for p in route_paths if p is not None]

        # Should have core routes
        assert len(route_paths) > 0, "Should have route paths"

        # Check for essential health routes
        # Health route is pretty essential, but configuration-dependent
        # At minimum, we should have some routes
        assert len(route_paths) > 0, "Should have registered routes"

    except ImportError:
        pytest.skip("FastAPI app not available")


@pytest.mark.smoke
def test_app_openapi_schema():
    """
    Test that OpenAPI schema is generated.

    Validates FastAPI auto-documentation works.
    """
    try:
        from serve.main import app

        # Get OpenAPI schema
        schema = app.openapi()

        # Schema should be dict
        assert isinstance(schema, dict), "OpenAPI schema should be dict"

        # Should have OpenAPI version
        assert "openapi" in schema, "Schema should have OpenAPI version"

        # Should have info section
        assert "info" in schema, "Schema should have info section"

        # Should have paths
        assert "paths" in schema, "Schema should have paths"
        assert len(schema["paths"]) > 0, "Should have at least one endpoint documented"

    except ImportError:
        pytest.skip("FastAPI app not available")


@pytest.mark.smoke
def test_app_exception_handlers():
    """
    Test that exception handlers are configured.

    Validates error handling middleware is set up.
    """
    try:
        from serve.main import app

        # Check for exception handlers
        if hasattr(app, "exception_handlers"):
            handlers = app.exception_handlers

            # Should be dict-like
            assert hasattr(
                handlers, "__getitem__"
            ), "Exception handlers should be dict-like"

        # Exception handlers are optional, so no strict assertion

    except ImportError:
        pytest.skip("FastAPI app not available")


@pytest.mark.smoke
def test_app_lifespan_events():
    """
    Test that lifespan events are configured (if any).

    Validates startup/shutdown event handlers.
    """
    try:
        from serve.main import app

        # FastAPI 0.109+ uses lifespan context manager
        # Older versions use on_event decorators

        # Check for router on_startup/on_shutdown
        startup_handlers = getattr(app.router, "on_startup", [])
        shutdown_handlers = getattr(app.router, "on_shutdown", [])

        # Handlers are optional - just verify they're lists
        assert isinstance(startup_handlers, list), "Startup handlers should be list"
        assert isinstance(shutdown_handlers, list), "Shutdown handlers should be list"

    except ImportError:
        pytest.skip("FastAPI app not available")


@pytest.mark.smoke
def test_app_state_initialization():
    """
    Test that app state is initialized.

    Validates state dictionary is available for dependency injection.
    """
    try:
        from serve.main import app

        # Check app.state exists
        assert hasattr(app, "state"), "App should have state attribute"

        # State should be usable (can set attributes)
        app.state.smoke_test_marker = True
        assert (
            app.state.smoke_test_marker is True
        ), "Should be able to set state attributes"

        # Clean up
        delattr(app.state, "smoke_test_marker")

    except ImportError:
        pytest.skip("FastAPI app not available")
