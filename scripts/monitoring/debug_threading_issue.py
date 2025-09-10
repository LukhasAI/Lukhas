#!/usr/bin/env python3
"""
Debug script to isolate and fix the threading issue with SQLite database table creation.
"""

import os
import queue
import sys
import tempfile
import threading

# Add paths for imports
sys.path.insert(0, ".")
sys.path.insert(0, "candidate/aka_qualia")

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool


def create_test_database():
    """Create a test SQLite database similar to the fixture"""
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

    return engine, db_path


def apply_migration(engine):
    """Apply database migration to create required tables"""
    with engine.begin() as conn:
        # Create akaq_scene table
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS akaq_scene (
                scene_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                subject TEXT,
                object TEXT,
                proto TEXT,
                proto_vec TEXT,
                risk TEXT,
                context TEXT,
                transform_chain TEXT,
                collapse_hash TEXT,
                drift_phi REAL,
                congruence_index REAL,
                neurosis_risk REAL,
                repair_delta REAL,
                sublimation_rate REAL,
                affect_energy_before REAL,
                affect_energy_after REAL,
                affect_energy_diff REAL,
                cfg_version TEXT,
                timestamp REAL DEFAULT (julianday('now'))
            )
        """
            )
        )

        # Create akaq_glyph table
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS akaq_glyph (
                glyph_id TEXT PRIMARY KEY,
                scene_id TEXT,
                user_id TEXT NOT NULL,
                glyph_key TEXT,
                glyph_attrs TEXT,
                priority REAL,
                timestamp REAL DEFAULT (julianday('now')),
                FOREIGN KEY (scene_id) REFERENCES akaq_scene(scene_id)
            )
        """
            )
        )

    print("Database migration applied successfully")


def test_threading_issue():
    """Test concurrent database operations to reproduce the threading issue"""

    # Create database and apply migration
    engine, db_path = create_test_database()

    print(f"Created test database at: {db_path}")

    # Apply migration in main thread
    apply_migration(engine)

    # Verify tables exist in main thread
    with engine.begin() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables in main thread: {tables}")

    # Test concurrent operations
    results_queue = queue.Queue()
    error_queue = queue.Queue()

    def save_scene_thread(thread_id):
        """Simulate saving a scene in a separate thread"""
        try:
            # Create a new connection in this thread
            thread_engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False,
                connect_args={
                    "check_same_thread": False,
                },
                poolclass=StaticPool,
            )

            # Check if tables exist in this thread
            with thread_engine.begin() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                print(f"Thread {thread_id} - Tables available: {tables}")

                # Try to insert a test scene
                scene_id = f"test_scene_{thread_id}"
                conn.execute(
                    text(
                        """
                        INSERT INTO akaq_scene (
                            scene_id, user_id, subject, object, proto, proto_vec, risk, context,
                            drift_phi, congruence_index, neurosis_risk, repair_delta,
                            sublimation_rate, cfg_version
                        ) VALUES (
                            :scene_id, :user_id, :subject, :object, :proto, :proto_vec, :risk, :context,
                            :drift_phi, :congruence_index, :neurosis_risk, :repair_delta,
                            :sublimation_rate, :cfg_version
                        )
                        """
                    ),
                    {
                        "scene_id": scene_id,
                        "user_id": f"test_user_{thread_id}",
                        "subject": f"subject_{thread_id}",
                        "object": f"object_{thread_id}",
                        "proto": '{"tone": 0.0}',
                        "proto_vec": "[0.0, 0.0, 0.0, 0.0, 0.0]",
                        "risk": '{"score": 0.1}',
                        "context": '{"test": true}',
                        "drift_phi": 0.9,
                        "congruence_index": 0.8,
                        "neurosis_risk": 0.1,
                        "repair_delta": 0.05,
                        "sublimation_rate": 0.0,
                        "cfg_version": "wave_c_v1.0.0",
                    },
                )

                print(f"Thread {thread_id} - Successfully inserted scene {scene_id}")
                results_queue.put((thread_id, scene_id))

        except Exception as e:
            error_msg = f"Thread {thread_id} - Error: {e!s}"
            print(error_msg)
            error_queue.put((thread_id, str(e)))

    # Launch 5 concurrent threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=save_scene_thread, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all to complete
    for t in threads:
        t.join(timeout=5.0)

    # Check results
    print(f"\nResults: {results_queue.qsize()} successful, {error_queue.qsize()} errors")

    # Print errors if any
    if not error_queue.empty():
        print("Errors:")
        while not error_queue.empty():
            thread_id, error = error_queue.get()
            print(f"  Thread {thread_id}: {error}")

    # Print successful results
    if not results_queue.empty():
        print("Successful saves:")
        while not results_queue.empty():
            thread_id, scene_id = results_queue.get()
            print(f"  Thread {thread_id}: {scene_id}")

    # Cleanup
    engine.dispose()
    try:
        os.unlink(db_path)
        print(f"Cleaned up database file: {db_path}")
    except Exception:
        pass


if __name__ == "__main__":
    print("Testing SQLite threading issue...")
    test_threading_issue()
    print("Test complete.")
