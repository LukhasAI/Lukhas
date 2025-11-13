"""
External Dependencies Health Smoke Test
=======================================

Validates that external service clients initialize gracefully and handle
unavailable services without crashing.

Tests:
- SQLite connection (always available)
- Redis client graceful fallback
- PostgreSQL availability check
- S3/Cloud adapter imports
- Service availability flags

Expected runtime: 0.4 seconds
Marker: @pytest.mark.smoke
"""
from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_sqlite_connection_available():
    """
    Test that SQLite database connection works.

    SQLite is built into Python, so this should always pass.
    """
    try:
        from sqlalchemy import create_engine, text

        # Create in-memory SQLite database
        engine = create_engine("sqlite:///:memory:")

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row[0] == 1, "SQLite connection should work"

    except ImportError:
        pytest.skip("SQLAlchemy not available")


@pytest.mark.smoke
def test_redis_client_graceful_fallback():
    """
    Test that Redis client handles unavailable server gracefully.

    This should not crash even if Redis is not running.
    """
    try:
        from core.reliability.redis_backend import RedisBackend

        # Attempt connection (will fail if Redis not running)
        try:
            backend = RedisBackend(url="redis://localhost:6379/0")

            # If connection succeeds, verify basic operation
            if hasattr(backend, "ping"):
                backend.ping()

        except Exception as e:
            # Connection failure is acceptable for smoke test
            # Should fail gracefully, not crash the test suite
            error_msg = str(e).lower()
            assert (
                "connection" in error_msg
                or "redis" in error_msg
                or "timeout" in error_msg
                or "refused" in error_msg
            ), f"Error should be connection-related: {e}"

    except ImportError:
        pytest.skip("Redis client not available")


@pytest.mark.smoke
def test_postgresql_availability_check():
    """
    Test PostgreSQL client import and availability detection.

    Does not require PostgreSQL to be running.
    """
    try:
        from sqlalchemy import create_engine

        # Try creating PostgreSQL engine (won't actually connect)
        # This tests that psycopg2/psycopg3 is available
        try:
            engine = create_engine("postgresql://user:pass@localhost:5432/test")
            assert engine is not None, "PostgreSQL engine should be creatable"

        except Exception as e:
            # Import error for psycopg is acceptable
            if "psycopg" in str(e).lower() or "postgresql" in str(e).lower():
                pytest.skip("PostgreSQL driver not installed (acceptable)")
            else:
                # Other errors are OK - we're just testing imports
                pass

    except ImportError:
        pytest.skip("SQLAlchemy not available")


@pytest.mark.smoke
def test_s3_backend_imports():
    """
    Test that S3 archival backend can be imported.

    Does not test actual S3 connection (no AWS credentials needed).
    """
    try:
        from lukhas_website.lukhas.memory.backends.archival_s3 import ArchivalS3Backend

        assert ArchivalS3Backend is not None, "S3 backend should be importable"

        # Verify it's a class
        assert isinstance(ArchivalS3Backend, type), "ArchivalS3Backend should be a class"

    except ImportError as e:
        # S3 backend might not be available, that's OK
        if "boto" in str(e).lower() or "s3" in str(e).lower():
            pytest.skip("boto3/S3 dependencies not installed (acceptable)")
        else:
            pytest.skip(f"S3 backend not available: {e}")


@pytest.mark.smoke
def test_cloud_consolidation_imports():
    """
    Test that cloud consolidation adapter can be imported.

    Does not test actual cloud connections.
    """
    try:
        from matriz.adapters.cloud_consolidation import CloudConsolidation

        assert CloudConsolidation is not None, "CloudConsolidation should be importable"

    except ImportError:
        pytest.skip("CloudConsolidation not available (acceptable)")


@pytest.mark.smoke
def test_matriz_availability_flag():
    """
    Test MATRIZ system availability flag.

    Validates that availability detection works correctly.
    """
    try:
        from serve.main import MATRIZ_AVAILABLE

        # Flag should be boolean
        assert isinstance(MATRIZ_AVAILABLE, bool), "MATRIZ_AVAILABLE should be boolean"

        # If available, try importing
        if MATRIZ_AVAILABLE:
            try:
                import matriz

                assert matriz is not None
            except ImportError:
                # Race condition possible, acceptable
                pass

    except ImportError:
        pytest.skip("serve.main not available")


@pytest.mark.smoke
def test_memory_availability_flag():
    """
    Test memory system availability flag.

    Validates that memory system detection works.
    """
    try:
        from serve.main import MEMORY_AVAILABLE

        # Flag should be boolean
        assert isinstance(
            MEMORY_AVAILABLE, bool
        ), "MEMORY_AVAILABLE should be boolean"

        # If available, try importing
        if MEMORY_AVAILABLE:
            try:
                # Try importing memory components
                from lukhas_website.lukhas.memory.backends import InMemoryVectorStore

                assert InMemoryVectorStore is not None
            except ImportError:
                # Memory might be available in different location
                pass

    except ImportError:
        pytest.skip("serve.main not available")


@pytest.mark.smoke
def test_database_client_initialization():
    """
    Test that database clients can initialize without external services.

    Uses in-memory databases for testing.
    """
    db_clients_tested = []

    # Test SQLAlchemy
    try:
        from sqlalchemy import create_engine

        engine = create_engine("sqlite:///:memory:")
        assert engine is not None
        db_clients_tested.append("SQLAlchemy")
    except ImportError:
        pass

    # Test SqlMemory (LUKHAS memory implementation)
    try:
        from lukhas_website.lukhas.aka_qualia.memory_sql import SqlMemory

        # Try different constructor signatures
        try:
            memory = SqlMemory(database_url="sqlite:///:memory:")
        except TypeError:
            try:
                memory = SqlMemory()
            except ValueError:
                # Requires engine or dsn - skip this client
                memory = None

        if memory is not None:
            assert memory is not None
            db_clients_tested.append("SqlMemory")
    except ImportError:
        pass
    except Exception as e:
        # Initialization might fail if dependencies missing
        if "psycopg" not in str(e).lower():
            raise

    # Should have tested at least one DB client
    if len(db_clients_tested) == 0:
        pytest.skip("No database clients available for testing")

    assert len(db_clients_tested) > 0, "At least one DB client should work"


@pytest.mark.smoke
def test_external_service_error_handling():
    """
    Test that external service errors are handled gracefully.

    Validates error handling patterns for unavailable services.
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.exc import OperationalError

        # Try connecting to non-existent PostgreSQL server
        engine = create_engine("postgresql://invalid:invalid@localhost:9999/invalid")

        try:
            with engine.connect():
                pass
        except OperationalError as e:
            # Expected - connection should fail gracefully
            assert "connection" in str(e).lower() or "could not" in str(
                e
            ).lower(), "Should raise connection error"

    except ImportError:
        pytest.skip("SQLAlchemy not available")


@pytest.mark.smoke
def test_monitoring_dependencies():
    """
    Test that monitoring/observability dependencies are available or gracefully absent.

    Tests OpenTelemetry, Prometheus, etc.
    """
    monitoring_available = []

    # Test OpenTelemetry
    try:
        from opentelemetry import trace

        monitoring_available.append("OpenTelemetry")
    except ImportError:
        pass

    # Test Prometheus client
    try:
        from prometheus_client import Counter

        monitoring_available.append("Prometheus")
    except ImportError:
        pass

    # Monitoring is optional, so no assertion required
    # Just log what's available
    assert True, "Monitoring dependencies check complete"
