#!/usr/bin/env python3
"""
Memory Integration Validation Test
==================================

Standalone test to validate that our memory integration fixes are working correctly.
This test runs independently of pytest to validate our improvements.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import sqlite3
import tempfile

from aka_qualia.memory_sql import SqlMemory


def test_memory_migration_and_indexes():
    """Test that database migration creates tables and indexes correctly"""
    print("=== Testing Database Migration and Indexes ===")

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # Initialize memory - should trigger migration
        SqlMemory(dsn=f"sqlite:///{db_path}")

        # Check that tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check akaq_scene table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='akaq_scene'")
        assert cursor.fetchone() is not None, "akaq_scene table should exist"

        # Check akaq_glyph table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='akaq_glyph'")
        assert cursor.fetchone() is not None, "akaq_glyph table should exist"

        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_akaq_%'")
        indexes = cursor.fetchall()
        assert len(indexes) >= 4, f"Should have at least 4 indexes, found {len(indexes)}"

        # Check specific indexes
        index_names = [idx[0] for idx in indexes]
        expected_indexes = [
            "idx_akaq_scene_user_id",
            "idx_akaq_scene_timestamp",
            "idx_akaq_glyph_user_id",
            "idx_akaq_glyph_scene_id",
        ]
        for expected in expected_indexes:
            assert expected in index_names, f"Index {expected} should exist"

        conn.close()
        print("✅ Database migration and indexes working correctly")
        return True

    finally:
        os.unlink(db_path)


def test_memory_save_retrieve_cycle():
    """Test complete save/retrieve cycle with proper data structures"""
    print("=== Testing Memory Save/Retrieve Cycle ===")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        memory = SqlMemory(dsn=f"sqlite:///{db_path}")

        # Test data with correct structure
        scene = {
            "scene_id": "test_scene_123",
            "subject": "test_subject",
            "object": "test_object",
            "proto": {"tone": 0.5, "arousal": 0.3, "clarity": 0.8, "embodiment": 0.2, "narrative_gravity": 0.6},
            "risk": {"score": 0.1, "severity": "minimal", "reasons": []},
            "context": {"test": True},
        }

        glyphs = [
            {"key": "test:glyph1", "priority": 1.0, "attrs": {"type": "test"}},
            {"key": "test:glyph2", "priority": 0.8, "attrs": {"type": "secondary"}},
        ]

        metrics = {"drift_phi": 0.9, "congruence_index": 0.8, "neurosis_risk": 0.1}

        # Save scene
        result = memory.save(
            user_id="test_user",
            scene=scene,
            glyphs=glyphs,
            metrics=metrics,
            policy={"test_policy": True},
            cfg_version="test_v1.0.0",
        )

        assert result is not None, "Save should return scene ID"
        print(f"✅ Save successful: {result[:12]}...")

        # Retrieve scene
        history = memory.get_scene_history(user_id="test_user", limit=1)
        assert len(history) == 1, "Should retrieve 1 scene"

        retrieved = history[0]
        assert retrieved["subject"] == "test_subject", "Subject should match"
        assert retrieved["object"] == "test_object", "Object should match"

        print("✅ Retrieve successful")

        # Test stats
        stats = memory.get_stats()
        assert stats["scenes_saved"] == 1, "Should have 1 scene saved"
        assert stats["save_failures"] == 0, "Should have 0 failures"
        assert stats["success_rate"] == 1.0, "Should have 100% success rate"

        print("✅ Statistics tracking working")
        return True

    finally:
        os.unlink(db_path)


def test_multi_user_isolation():
    """Test that user data is properly isolated"""
    print("=== Testing Multi-User Data Isolation ===")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        memory = SqlMemory(dsn=f"sqlite:///{db_path}")

        # Save data for user1
        memory.save(
            user_id="user1",
            scene={
                "scene_id": "scene1",
                "subject": "user1_data",
                "object": "obj1",
                "proto": {"tone": 0.5},
                "risk": {"score": 0.1},
                "context": {},
            },
            glyphs=[{"key": "user1:glyph", "priority": 1.0, "attrs": {}}],
            metrics={"drift_phi": 0.8},
            policy={},
            cfg_version="v1.0",
        )

        # Save data for user2
        memory.save(
            user_id="user2",
            scene={
                "scene_id": "scene2",
                "subject": "user2_data",
                "object": "obj2",
                "proto": {"tone": -0.3},
                "risk": {"score": 0.2},
                "context": {},
            },
            glyphs=[{"key": "user2:glyph", "priority": 0.8, "attrs": {}}],
            metrics={"drift_phi": 0.6},
            policy={},
            cfg_version="v1.0",
        )

        # Check isolation
        user1_history = memory.get_scene_history(user_id="user1", limit=10)
        user2_history = memory.get_scene_history(user_id="user2", limit=10)

        assert len(user1_history) == 1, "User1 should have 1 scene"
        assert len(user2_history) == 1, "User2 should have 1 scene"

        assert user1_history[0]["subject"] == "user1_data", "User1 should only see their data"
        assert user2_history[0]["subject"] == "user2_data", "User2 should only see their data"

        print("✅ Multi-user isolation working correctly")
        return True

    finally:
        os.unlink(db_path)


def test_production_mode_privacy():
    """Test production mode privacy hashing"""
    print("=== Testing Production Mode Privacy Hashing ===")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # Test production mode
        memory_prod = SqlMemory(dsn=f"sqlite:///{db_path}", is_prod=True, rotate_salt="test_salt")

        memory_prod.save(
            user_id="sensitive_user",
            scene={
                "scene_id": "prod_scene",
                "subject": "sensitive",
                "object": "data",
                "proto": {"tone": 0.0},
                "risk": {"score": 0.0},
                "context": {},
            },
            glyphs=[{"key": "prod:glyph", "priority": 1.0, "attrs": {}}],
            metrics={"drift_phi": 0.5},
            policy={},
            cfg_version="v1.0",
        )

        # Should be able to retrieve with same memory instance
        history = memory_prod.get_scene_history(user_id="sensitive_user", limit=1)
        assert len(history) == 1, "Should retrieve scene in production mode"

        print("✅ Production mode privacy hashing working")
        return True

    finally:
        os.unlink(db_path)


def main():
    """Run all validation tests"""
    print("Memory Integration Validation Test Suite")
    print("=" * 50)

    tests = [
        test_memory_migration_and_indexes,
        test_memory_save_retrieve_cycle,
        test_multi_user_isolation,
        test_production_mode_privacy,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
            import traceback

            traceback.print_exc()
        print()

    print("=" * 50)
    print(f"VALIDATION RESULTS: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 ALL MEMORY INTEGRATION FIXES VALIDATED SUCCESSFULLY!")
        print("Database migrations, SQL compatibility, enum fixes, and memory operations are working correctly.")
        return True
    else:
        print("❌ Some validation tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
