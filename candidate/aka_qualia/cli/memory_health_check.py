#!/usr/bin/env python3
"""
Wave C C4 Memory System Health Check Tool

Comprehensive health monitoring for the Aka Qualia memory system.
Validates database connectivity, schema integrity, and performance metrics.
"""
import streamlit as st

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_noop import NoopMemory
from memory_sql import SqlMemory
from sqlalchemy import create_engine, text


def test_database_connectivity(engine):
    """Test basic database connectivity."""
    print("🔌 Testing database connectivity...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            assert result.scalar() == 1
        print("  ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False


def check_schema_integrity(engine):
    """Check database schema integrity."""
    print("🗄️  Checking schema integrity...")

    try:
        with engine.connect() as conn:
            # Check required tables exist
            required_tables = ["akaq_scene", "akaq_glyph", "akaq_memory_ops"]

            for table in required_tables:
                result = conn.execute(
                    text(
                        f"""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = '{table}'
                """
                    )
                )
                if result.scalar() == 0:
                    # Try SQLite syntax
                    result = conn.execute(
                        text(
                            f"""
                        SELECT COUNT(*) FROM sqlite_master
                        WHERE type='table' AND name='{table}'
                    """
                        )
                    )

                if result.scalar() == 0:
                    print(f"  ❌ Missing table: {table}")
                    return False

            print("  ✅ All required tables present")

            # Check foreign key constraints
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM akaq_glyph g
                LEFT JOIN akaq_scene s ON g.scene_id = s.scene_id
                WHERE s.scene_id IS NULL
            """
                )
            )
            orphaned = result.scalar()

            if orphaned > 0:
                print(f"  ⚠️  Warning: {orphaned} orphaned glyphs found")
            else:
                print("  ✅ Foreign key integrity verified")

            return True

    except Exception as e:
        print(f"  ❌ Schema integrity check failed: {e}")
        return False


def test_memory_operations(memory_client):
    """Test basic memory operations."""
    print("🧠 Testing memory operations...")

    try:
        # Test scene save
        test_scene = {
            "subject": "health_check",
            "object": "test_scene",
            "setting": "automated_test",
            "affect": {"vigilance": 0.5, "valence": 0.0, "arousal": 0.0},
        }

        test_glyphs = [
            {"key": "vigilance", "value": 0.5, "is_cache": False},
            {"key": "test_marker", "value": 1.0, "is_cache": True},
        ]

        test_policy = {"tempo": "moderate", "operations": ["test"]}
        test_metrics = {"drift_phi": 0.0, "congruence_index": 1.0}

        # Save scene - handle different memory client interfaces
        if hasattr(memory_client, "save"):
            if isinstance(memory_client, NoopMemory):
                # NoopMemory has different parameter names
                scene_id = memory_client.save(
                    user_id="health_check_user",
                    scene=test_scene,
                    glyphs=test_glyphs,
                    policy=test_policy,
                    metrics=test_metrics,
                    cfg_version="health_check_1.0",
                )
            else:
                # SqlMemory interface
                scene_id = memory_client.save(
                    user_id="health_check_user",
                    scene=test_scene,
                    glyphs=test_glyphs,
                    regulation_policy=test_policy,
                    akaq_metrics=test_metrics,
                )
        else:
            raise AttributeError("Memory client missing save method")

        print(f"  ✅ Scene save successful: {scene_id}")

        # Test scene retrieval - handle different interfaces
        if isinstance(memory_client, NoopMemory):
            # NoopMemory uses history method
            history = memory_client.history(user_id="health_check_user", limit=1)
        else:
            # SqlMemory uses get_scene_history
            history = memory_client.get_scene_history(user_id="health_check_user", limit=1)

        if isinstance(memory_client, NoopMemory):
            # NoopMemory returns empty history by design
            if len(history) == 0:
                print("  ✅ Scene retrieval successful (NoopMemory returns empty as expected)")
            else:
                print("  ❌ NoopMemory should return empty history")
                return False
        else:
            # SqlMemory should return actual data
            if len(history) > 0 and history[0]["subject"] == "health_check":
                print("  ✅ Scene retrieval successful")
            else:
                print("  ❌ Scene retrieval failed")
                return False

        # Cleanup test data
        if hasattr(memory_client, "delete_user"):
            deleted = memory_client.delete_user(user_id="health_check_user")
            print(f"  🗑️  Cleanup: Removed {deleted} test records")

        return True

    except Exception as e:
        print(f"  ❌ Memory operations test failed: {e}")
        return False


def measure_performance(memory_client):
    """Measure basic performance metrics."""
    print("⚡ Measuring performance...")

    try:
        # Measure save performance
        test_scene = {
            "subject": "perf_test",
            "object": "benchmark",
            "setting": "performance_test",
            "affect": {"vigilance": 0.5, "valence": 0.0, "arousal": 0.0},
        }

        test_glyphs = [{"key": "perf_marker", "value": 1.0, "is_cache": False}]
        test_policy = {"tempo": "fast", "operations": ["benchmark"]}
        test_metrics = {"drift_phi": 0.0, "congruence_index": 1.0}

        # Measure save time
        start_time = time.time()
        if isinstance(memory_client, NoopMemory):
            memory_client.save(
                user_id="perf_test_user",
                scene=test_scene,
                glyphs=test_glyphs,
                policy=test_policy,
                metrics=test_metrics,
                cfg_version="perf_test_1.0",
            )
        else:
            memory_client.save(
                user_id="perf_test_user",
                scene=test_scene,
                glyphs=test_glyphs,
                regulation_policy=test_policy,
                akaq_metrics=test_metrics,
            )
        save_time = (time.time() - start_time) * 1000  # milliseconds

        # Measure retrieval time
        start_time = time.time()
        if isinstance(memory_client, NoopMemory):
            memory_client.history(user_id="perf_test_user", limit=1)
        else:
            memory_client.get_scene_history(user_id="perf_test_user", limit=1)
        retrieval_time = (time.time() - start_time) * 1000  # milliseconds

        print(f"  📊 Save latency: {save_time:.1f}ms")
        print(f"  📊 Retrieval latency: {retrieval_time:.1f}ms")

        # Performance thresholds
        save_ok = save_time < 100  # 100ms threshold
        retrieval_ok = retrieval_time < 50  # 50ms threshold

        if save_ok and retrieval_ok:
            print("  ✅ Performance within acceptable limits")
            perf_status = True
        else:
            print("  ⚠️  Performance may need attention")
            perf_status = False

        # Cleanup
        if hasattr(memory_client, "delete_user"):
            memory_client.delete_user(user_id="perf_test_user")

        return perf_status

    except Exception as e:
        print(f"  ❌ Performance measurement failed: {e}")
        return False


def get_system_statistics(engine):
    """Get system usage statistics."""
    print("📈 Gathering system statistics...")

    try:
        with engine.connect() as conn:
            # Count total records
            scene_count = conn.execute(text("SELECT COUNT(*) FROM akaq_scene")).scalar()
            glyph_count = conn.execute(text("SELECT COUNT(*) FROM akaq_glyph")).scalar()
            ops_count = conn.execute(text("SELECT COUNT(*) FROM akaq_memory_ops")).scalar()

            # Get recent activity
            recent_ops = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM akaq_memory_ops
                WHERE timestamp > datetime('now', '-24 hours')
            """
                )
            ).scalar()

            print(f"  📊 Total scenes: {scene_count:,}")
            print(f"  📊 Total glyphs: {glyph_count:,}")
            print(f"  📊 Total operations: {ops_count:,}")
            print(f"  📊 Operations (24h): {recent_ops:,}")

            return True

    except Exception as e:
        print(f"  ❌ Statistics gathering failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Wave C C4 Memory System Health Check Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic health check
  python memory_health_check.py --db-url sqlite:///akaq_memory.db

  # Full health check with performance testing
  python memory_health_check.py --db-url sqlite:///akaq_memory.db --full

  # NoopMemory health check
  python memory_health_check.py --memory-type noop
        """,
    )

    parser.add_argument("--db-url", help="Database connection URL (required for SqlMemory)")
    parser.add_argument(
        "--memory-type",
        choices=["sql", "noop"],
        default="sql",
        help="Memory client type to test (default: sql)",
    )
    parser.add_argument("--salt", default="health_check_salt", help="Salt for user ID hashing")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full health check including performance tests",
    )
    parser.add_argument(
        "--prod-mode",
        action="store_true",
        help="Test in production mode (user ID hashing)",
    )

    args = parser.parse_args()

    if args.memory_type == "sql" and not args.db_url:
        print("❌ --db-url is required for SQL memory type")
        return 1

    print("🏥 Wave C C4 Memory System Health Check")
    print(f"🧠 Memory type: {args.memory_type.upper(}")
    if args.db_url:
        print(f"📡 Database: {args.db_url}")
    print(f"🎯 Mode: {'FULL' if args.full else 'BASIC'}")
    print(f"⏰ Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'}")
    print()

    health_checks = []

    try:
        if args.memory_type == "sql":
            # SQL Memory health check
            engine = create_engine(args.db_url)

            # Test connectivity
            connectivity_ok = test_database_connectivity(engine)
            health_checks.append(("Database Connectivity", connectivity_ok))

            if connectivity_ok:
                # Test schema
                schema_ok = check_schema_integrity(engine)
                health_checks.append(("Schema Integrity", schema_ok))

                # Create memory client
                memory = SqlMemory(engine=engine, rotate_salt=args.salt, is_prod=args.prod_mode)

                # Test memory operations
                operations_ok = test_memory_operations(memory)
                health_checks.append(("Memory Operations", operations_ok))

                if args.full:
                    # Performance testing
                    performance_ok = measure_performance(memory)
                    health_checks.append(("Performance", performance_ok))

                    # System statistics
                    stats_ok = get_system_statistics(engine)
                    health_checks.append(("Statistics", stats_ok))

        else:
            # NoopMemory health check
            print("🧠 Testing NoopMemory client...")
            memory = NoopMemory()

            # Test basic operations
            operations_ok = test_memory_operations(memory)
            health_checks.append(("NoopMemory Operations", operations_ok))

            if args.full:
                performance_ok = measure_performance(memory)
                health_checks.append(("NoopMemory Performance", performance_ok))

        # Summary
        print()
        print("📋 Health Check Summary:")
        all_ok = True

        for check_name, status in health_checks:
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check_name}: {'PASS' if status else 'FAIL'}")
            if not status:
                all_ok = False

        print()
        if all_ok:
            print("🎉 Overall Status: HEALTHY")
            print("💚 All health checks passed")
        else:
            print("⚠️  Overall Status: ISSUES DETECTED")
            print("🔧 Some health checks failed - investigation recommended")

        print(f"⏰ Completed: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'}")

        return 0 if all_ok else 1

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
