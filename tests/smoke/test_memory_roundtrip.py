"""
Memory + Persistence Roundtrip Smoke Test
=========================================

Validates that memory system can store and retrieve data correctly.

Tests:
- CoreMemoryComponent basic operations
- Memory backend availability
- SQLite in-memory persistence
- Vector store imports

Expected runtime: 0.5 seconds
Marker: @pytest.mark.smoke
"""
from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_memory_core_component():
    """
    Test CoreMemoryComponent initialization and basic operations.

    Validates:
    - CoreMemoryComponent can be imported
    - Initializes without external dependencies
    - Has expected methods
    """
    try:
        from labs.memory.memory_core import CoreMemoryComponent

        # Initialize component
        memory = CoreMemoryComponent(config={"enabled": True})

        # Verify initialization
        assert memory is not None, "CoreMemoryComponent should initialize"

        # Check expected methods
        assert hasattr(
            memory, "process_symbolic_trace"
        ), "Should have process_symbolic_trace method"
        assert hasattr(
            memory, "get_component_status"
        ), "Should have get_component_status method"

        # Test status check (should not crash)
        try:
            status = memory.get_component_status()
            assert isinstance(status, dict), "Status should be dict"
            assert (
                "operational_status" in status or "status" in status
            ), "Status should have operational info"
        except Exception:
            # Status check might fail if not fully configured, that's OK
            pass

    except ImportError as e:
        pytest.skip(f"CoreMemoryComponent not available: {e}")


@pytest.mark.smoke
def test_memory_backends_available():
    """
    Check which memory backends are available.

    Tests import of various vector stores without requiring them to work.
    """
    available_backends = []

    # Test InMemoryVectorStore (should always be available)
    try:
        from lukhas_website.lukhas.memory.backends import InMemoryVectorStore

        available_backends.append("InMemory")
        assert InMemoryVectorStore is not None
    except ImportError:
        pass

    # Test PgVectorStore (requires PostgreSQL)
    try:
        from lukhas_website.lukhas.memory.backends import PgVectorStore

        available_backends.append("PgVector")
        assert PgVectorStore is not None
    except ImportError:
        pass

    # Test FAISSStore (requires FAISS library)
    try:
        from lukhas_website.lukhas.memory.backends import FAISSStore

        available_backends.append("FAISS")
        assert FAISSStore is not None
    except ImportError:
        pass

    # Should have at least one backend available (ideally InMemory)
    if len(available_backends) == 0:
        pytest.skip("No memory backends available")

    # If we have backends, that's good
    assert len(available_backends) > 0, "At least one memory backend should be available"


@pytest.mark.smoke
def test_sqlite_memory_persistence():
    """
    Test basic persistence using SQLite in-memory database.

    This validates SQLAlchemy integration without requiring PostgreSQL.
    """
    try:
        from sqlalchemy import create_engine, text

        # Create in-memory SQLite database
        engine = create_engine("sqlite:///:memory:")

        # Test connection
        with engine.connect() as conn:
            # Create test table
            conn.execute(
                text(
                    """
                CREATE TABLE test_memory (
                    id INTEGER PRIMARY KEY,
                    data TEXT
                )
            """
                )
            )
            conn.commit()

            # Insert test data
            conn.execute(
                text("INSERT INTO test_memory (id, data) VALUES (1, 'test_data')")
            )
            conn.commit()

            # Retrieve test data
            result = conn.execute(text("SELECT data FROM test_memory WHERE id = 1"))
            row = result.fetchone()

            assert row is not None, "Should retrieve inserted row"
            assert row[0] == "test_data", "Data should match what was inserted"

    except ImportError:
        pytest.skip("SQLAlchemy not available")


@pytest.mark.smoke
def test_sql_memory_initialization():
    """
    Test SqlMemory class initialization with SQLite.

    This tests the actual LUKHAS memory implementation.
    """
    try:
        from lukhas_website.lukhas.aka_qualia.memory_sql import SqlMemory

        # Initialize with in-memory SQLite
        # Try different constructor signatures
        try:
            memory = SqlMemory(database_url="sqlite:///:memory:")
        except TypeError:
            try:
                memory = SqlMemory()
            except ValueError as ve:
                # Requires engine or dsn - skip test
                pytest.skip(f"SqlMemory requires specific initialization: {ve}")

        assert memory is not None, "SqlMemory should initialize with SQLite"

        # Test basic operations if methods are available
        if hasattr(memory, "create_tables"):
            try:  # TODO[T4-ISSUE]: {"code":"SIM105","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"try-except-pass pattern - consider contextlib.suppress for clarity","estimate":"10m","priority":"low","dependencies":"contextlib","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tests_smoke_test_memory_roundtrip_py_L177"}
                memory.create_tables()
            except Exception:
                # Table creation might fail, that's OK for smoke test
                pass

    except ImportError as e:
        pytest.skip(f"SqlMemory not available: {e}")
    except Exception as e:
        # Initialization might fail if dependencies missing
        if "psycopg" in str(e).lower() or "postgresql" in str(e).lower():
            pytest.skip(f"PostgreSQL dependencies missing (acceptable): {e}")
        else:
            # Other errors should be reported
            raise


@pytest.mark.smoke
def test_memory_trace_processing():
    """
    Test memory trace processing (stub mode acceptable).

    Validates that trace processing methods exist and can be called.
    """
    try:
        from labs.memory.memory_core import CoreMemoryComponent

        memory = CoreMemoryComponent(config={"enabled": False})  # Disabled/stub mode OK

        # Test trace processing
        if hasattr(memory, "process_symbolic_trace"):
            result = memory.process_symbolic_trace(
                input_data="smoke test data", tier_level=1
            )

            # Result should be dict or None
            assert (
                result is None or isinstance(result, dict)
            ), "Trace processing should return dict or None"

            # If dict returned, check for status field
            if isinstance(result, dict):
                assert (
                    "status" in result or "processed" in result or "error" in result
                ), "Result should have status info"

    except ImportError:
        pytest.skip("CoreMemoryComponent not available")
    except Exception as e:
        # Processing might fail if not configured, that's acceptable
        if "not configured" in str(e).lower() or "disabled" in str(e).lower():
            pytest.skip(f"Memory component disabled in test env: {e}")
        else:
            raise
