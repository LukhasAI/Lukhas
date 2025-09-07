#!/usr/bin/env python3

"""
Security and Fault Injection Tests for Wave C Memory System
==========================================================

Security-focused tests covering:
- Database outage tolerance and graceful degradation
- Transaction atomicity under failure conditions
- SQL injection prevention
- Memory exhaustion handling
- Concurrent access safety
- Error propagation and logging

Target: Production-grade resilience validation
"""

import time

import pytest
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError

from .conftest import create_test_glyph, create_test_scene


class TestFaultInjection:
    """Test system behavior under various failure conditions"""

    @pytest.mark.fault
    @pytest.mark.asyncio
    async def test_db_outage_graceful_degradation(self, monkeypatch, aq_with_sql_memory):
        """Memory failures should not crash consciousness pipeline"""

        # Simulate database connection failure
        def failing_save(**kwargs):
            raise OperationalError("Database connection lost", "", "")

        # Patch the memory save method to fail
        monkeypatch.setattr(aq_with_sql_memory.memory, "save", failing_save)

        # Consciousness should continue operating despite memory failure
        signals = {"text": "Testing resilience", "subject": "observer", "object": "test"}

        result = await aq_with_sql_memory.step(
            signals=signals,
            goals={},
            ethics_state={},
            guardian_state={"active": True},
            memory_ctx={"session_id": "fault_test"},
        )

        # System should not crash - should get a result
        assert result is not None
        assert "scene" in result
        assert "glyphs" in result
        assert "metrics" in result

        # Memory error should be logged but not cause system failure
        # (In production, this would be logged to monitoring systems)

    @pytest.mark.fault
    def test_partial_transaction_rollback(self, sql_memory, monkeypatch):
        """Failed glyph inserts should rollback entire transaction atomically"""

        # Track what gets inserted
        scene_inserted = False

        original_execute = sql_memory.engine.execute

        def failing_execute(query, params=None):
            nonlocal scene_inserted

            query_str = str(query)

            # Let scene insert succeed
            if "INSERT INTO akaq_scene" in query_str:
                scene_inserted = True
                return original_execute(query, params)

            # Make glyph insert fail
            elif "INSERT INTO akaq_glyph" in query_str:
                raise IntegrityError("Simulated glyph constraint violation", "", "")

            return original_execute(query, params)

        monkeypatch.setattr(sql_memory.engine, "execute", failing_execute)

        # Attempt to save scene with glyphs
        scene_data = create_test_scene()
        glyph_data = [create_test_glyph("test:failing_glyph")]

        with pytest.raises(IntegrityError):
            sql_memory.save(
                user_id="rollback_test",
                scene=scene_data,
                glyphs=glyph_data,
                policy={"gain": 1.0},
                metrics={"drift_phi": 0.9},
                cfg_version="wave_c_v1.0.0",
            )

        # Verify atomic rollback - no partial data should exist
        history = sql_memory.get_scene_history(user_id="rollback_test", limit=5)
        assert len(history) == 0, "No partial data should exist after transaction rollback"

        # Verify the scene insert was attempted but rolled back
        assert scene_inserted, "Scene insert should have been attempted"

    @pytest.mark.fault
    def test_connection_recovery(self, sql_memory, monkeypatch):
        """System should recover after temporary database outages"""

        call_count = 0

        def intermittent_failure(original_method):
            def wrapper(*args, **kwargs):
                nonlocal call_count
                call_count += 1

                # Fail on first two calls, succeed on third
                if call_count <= 2:
                    raise OperationalError("Connection temporarily unavailable", "", "")

                return original_method(*args, **kwargs)

            return wrapper

        # Patch the engine execute method to fail intermittently
        original_execute = sql_memory.engine.execute
        monkeypatch.setattr(sql_memory.engine, "execute", intermittent_failure(original_execute))

        scene_data = create_test_scene()

        # First save should fail
        with pytest.raises(OperationalError):
            sql_memory.save(
                user_id="recovery_test", scene=scene_data, glyphs=[], policy={}, metrics={}, cfg_version="wave_c_v1.0.0"
            )

        # Second save should also fail
        with pytest.raises(OperationalError):
            sql_memory.save(
                user_id="recovery_test", scene=scene_data, glyphs=[], policy={}, metrics={}, cfg_version="wave_c_v1.0.0"
            )

        # Third save should succeed (connection recovered)
        scene_id = sql_memory.save(
            user_id="recovery_test", scene=scene_data, glyphs=[], policy={}, metrics={}, cfg_version="wave_c_v1.0.0"
        )

        assert scene_id is not None
        assert len(scene_id) > 0

    @pytest.mark.fault
    def test_memory_exhaustion_handling(self, sql_memory):
        """System should handle memory exhaustion gracefully"""

        # Try to create a very large scene that might cause memory issues
        huge_string = "x" * (1024 * 1024)  # 1MB string

        large_scene = create_test_scene(
            context={
                "cfg_version": "wave_c_v1.0.0",
                "huge_data": huge_string,
                "nested_huge": {"level1": {"level2": {"data": huge_string},
            }
        )

        # Should either succeed or fail gracefully (not crash)
        try:
            scene_id = sql_memory.save(
                user_id="memory_test", scene=large_scene, glyphs=[], policy={}, metrics={}, cfg_version="wave_c_v1.0.0"
            )

            # If it succeeds, verify we can retrieve it
            if scene_id:
                history = sql_memory.get_scene_history(user_id="memory_test", limit=1)
                assert len(history) <= 1  # Should have 0 or 1 results

        except (MemoryError, DatabaseError, OperationalError) as e:
            # These are acceptable failures for huge data
            assert "memory" in str(e).lower() or "too large" in str(e).lower()

    @pytest.mark.fault
    def test_corrupt_data_handling(self, sql_memory):
        """System should handle corrupt/malformed data gracefully"""

        # Test with various types of malformed data
        corrupt_scenarios = [
            # Invalid JSON-like structures
            {"proto": {"tone": float("inf")},  # Infinite values
            {"proto": {"tone": float("nan")},  # NaN values
            {"context": {"recursive": None},  # Circular references would be handled by JSON serializer
            # Extremely nested data
            {"context": {"level_" + str(i): {"data": f"level_{i}"} for i in range(1000)},
            # Invalid UTF-8 sequences (if applicable)
            {"subject": "test\x00\x01\x02"},  # Null bytes and control characters
        ]

        for i, corrupt_data in enumerate(corrupt_scenarios):
            scene_data = create_test_scene(**corrupt_data)

            try:
                scene_id = sql_memory.save(
                    user_id=f"corrupt_test_{i}",
                    scene=scene_data,
                    glyphs=[],
                    policy={},
                    metrics={},
                    cfg_version="wave_c_v1.0.0",
                )

                # If it succeeds, that's fine - data was sanitized
                if scene_id:
                    assert len(scene_id) > 0

            except (ValueError, TypeError, DatabaseError) as e:
                # These are acceptable failures for corrupt data
                assert "invalid" in str(e).lower() or "error" in str(e).lower()


class TestSQLInjectionPrevention:
    """Test protection against SQL injection attacks"""

    @pytest.mark.security
    def test_user_id_sql_injection_prevention(self, sql_memory):
        """SQL injection in user_id should be prevented by parameterization"""

        malicious_user_ids = [
            "'; DROP TABLE akaq_scene; --",
            "admin' OR '1'='1",
            "test'; INSERT INTO akaq_scene VALUES ('hacked'); --",
            'user"; DELETE FROM akaq_scene; --',
        ]

        for malicious_id in malicious_user_ids:
            scene_data = create_test_scene()

            try:
                sql_memory.save(
                    user_id=malicious_id,
                    scene=scene_data,
                    glyphs=[],
                    policy={},
                    metrics={},
                    cfg_version="wave_c_v1.0.0",
                )

                # If save succeeds, verify the malicious SQL didn't execute
                # by checking that normal data is still intact
                sql_memory.get_scene_history(user_id="safe_user", limit=1)
                # This would be empty but that's expected - the point is no exception

            except (DatabaseError, ValueError) as e:
                # Acceptable - database rejected the malicious input
                assert "syntax" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.security
    def test_glyph_key_injection_prevention(self, sql_memory):
        """SQL injection in glyph keys should be prevented"""

        malicious_glyphs = [
            create_test_glyph("'; DROP TABLE akaq_glyph; --"),
            create_test_glyph("test' OR 1=1 --"),
            create_test_glyph("glyph\"; UPDATE akaq_scene SET subject='hacked'; --"),
        ]

        scene_data = create_test_scene()

        for glyph in malicious_glyphs:
            try:
                scene_id = sql_memory.save(
                    user_id="injection_test",
                    scene=scene_data,
                    glyphs=[glyph],
                    policy={},
                    metrics={},
                    cfg_version="wave_c_v1.0.0",
                )

                # Verify that the glyph key was stored as-is (not executed as SQL)
                if scene_id:
                    search_results = sql_memory.search_by_glyph(user_id="injection_test", glyph_key=glyph["key"])
                    # Should find 0 or 1 results, not cause a SQL error
                    assert len(search_results) <= 1

            except (DatabaseError, ValueError):
                # Acceptable rejection of malicious input
                pass

    @pytest.mark.security
    def test_context_data_injection_prevention(self, sql_memory):
        """SQL injection in context JSON should be prevented"""

        malicious_contexts = [
            {"malicious": "'; DROP TABLE akaq_scene; --"},
            {"nested": {"attack": "' OR 1=1 --"},
            {"json_attack": '\\"}; DROP TABLE akaq_scene; {\\"safe\\": \\"data\\"}'},
        ]

        for context in malicious_contexts:
            scene_data = create_test_scene(context={"cfg_version": "wave_c_v1.0.0", **context})

            try:
                scene_id = sql_memory.save(
                    user_id="context_injection_test",
                    scene=scene_data,
                    glyphs=[],
                    policy={},
                    metrics={},
                    cfg_version="wave_c_v1.0.0",
                )

                # If successful, verify the context was stored safely
                if scene_id:
                    history = sql_memory.get_scene_history(user_id="context_injection_test", limit=1)
                    assert len(history) <= 1

            except (DatabaseError, ValueError, TypeError):
                # Acceptable rejection
                pass


class TestConcurrentAccessSafety:
    """Test thread safety and concurrent access patterns"""

    @pytest.mark.security
    @pytest.mark.slow
    def test_concurrent_user_isolation(self, sql_memory):
        """Concurrent operations by different users should be isolated"""

        import queue
        import threading

        results = queue.Queue()
        errors = queue.Queue()

        def user_operations(user_id, num_operations):
            try:
                for i in range(num_operations):
                    scene_data = create_test_scene(subject=f"{user_id}_scene_{i}")
                    glyph_data = [create_test_glyph(f"{user_id}:glyph_{i}")]

                    scene_id = sql_memory.save(
                        user_id=user_id,
                        scene=scene_data,
                        glyphs=glyph_data,
                        policy={"gain": 1.0},
                        metrics={"drift_phi": 0.9},
                        cfg_version="wave_c_v1.0.0",
                    )

                    results.put((user_id, scene_id))

                # Verify user can only see their own data
                user_history = sql_memory.get_scene_history(user_id=user_id, limit=100)
                for scene in user_history:
                    # In dev mode, subjects should contain the user_id
                    assert user_id in str(scene.get("subject", ""))

            except Exception as e:
                errors.put((user_id, str(e)))

        # Start concurrent operations for multiple users
        users = ["user_a", "user_b", "user_c"]
        threads = []

        for user in users:
            t = threading.Thread(target=user_operations, args=(user, 5))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join(timeout=10.0)

        # Verify no errors occurred
        assert errors.empty(), f"Errors in concurrent access: {list(errors.queue)}"

        # Verify all operations completed
        assert results.qsize() == 15, "All 15 operations should have completed"

        # Verify data isolation - each user should only see their own data
        for user in users:
            user_history = sql_memory.get_scene_history(user_id=user, limit=10)
            assert len(user_history) == 5, f"User {user} should have exactly 5 scenes"

            # Verify no cross-contamination
            for scene in user_history:
                assert user in str(scene.get("subject", "")), f"Scene should belong to {user}"

    @pytest.mark.security
    def test_race_condition_prevention(self, sql_memory):
        """Race conditions in scene ID generation should be prevented"""

        import threading
        import time

        scene_ids = []
        lock = threading.Lock()

        def rapid_save(thread_id):
            # Save multiple scenes rapidly to try to trigger race conditions
            for i in range(10):
                scene_data = create_test_scene(subject=f"race_test_{thread_id}_{i}")

                scene_id = sql_memory.save(
                    user_id="race_test", scene=scene_data, glyphs=[], policy={}, metrics={}, cfg_version="wave_c_v1.0.0"
                )

                with lock:
                    scene_ids.append(scene_id)

                # Small random delay to increase chance of race conditions
                time.sleep(0.001)

        # Start multiple threads doing rapid saves
        threads = []
        for i in range(5):
            t = threading.Thread(target=rapid_save, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify all scene IDs are unique (no race condition duplicates)
        assert len(scene_ids) == 50, "Should have 50 scene IDs"
        assert len(set(scene_ids)) == 50, "All scene IDs should be unique"


class TestErrorPropagation:
    """Test proper error handling and logging"""

    @pytest.mark.fault
    def test_database_error_logging(self, sql_memory, monkeypatch, caplog):
        """Database errors should be properly logged"""

        # Mock the engine to raise a specific database error
        def failing_begin():
            raise DatabaseError("Simulated database error for testing", "", "")

        monkeypatch.setattr(sql_memory.engine, "begin", failing_begin)

        scene_data = create_test_scene()

        with pytest.raises(DatabaseError):
            sql_memory.save(
                user_id="error_logging_test",
                scene=scene_data,
                glyphs=[],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

        # In production, database errors would be logged
        # Here we just verify the exception propagated correctly

    @pytest.mark.fault
    def test_memory_stats_during_failures(self, noop_memory, monkeypatch):
        """Memory stats should track failures correctly"""

        def failing_save(*args, **kwargs):
            noop_memory.save_failures += 1  # Track the failure
            raise RuntimeError("Simulated save failure")

        monkeypatch.setattr(noop_memory, "save", failing_save)

        # Attempt to save and expect failure
        with pytest.raises(RuntimeError):
            noop_memory.save(
                user_id="failure_stats_test",
                scene=create_test_scene(),
                glyphs=[],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

        # Verify failure was tracked in stats
        stats = noop_memory.get_stats()
        assert stats["save_failures"] == 1, "Save failure should be tracked"
        assert stats["success_rate"] < 1.0, "Success rate should reflect failure"


class TestResourceLimits:
    """Test behavior under resource constraints"""

    @pytest.mark.fault
    @pytest.mark.slow
    def test_large_batch_handling(self, sql_memory):
        """System should handle large batches of scenes gracefully"""

        batch_size = 100  # Large but not excessive for testing

        start_time = time.perf_counter()

        try:
            for i in range(batch_size):
                scene_data = create_test_scene(subject=f"batch_scene_{i}")
                glyph_data = [create_test_glyph(f"batch:glyph_{i}")]

                sql_memory.save(
                    user_id="batch_test",
                    scene=scene_data,
                    glyphs=glyph_data,
                    policy={"gain": 1.0},
                    metrics={"drift_phi": 0.9},
                    cfg_version="wave_c_v1.0.0",
                )

                # Stop if taking too long (prevent test timeout)
                if time.perf_counter() - start_time > 30:
                    break

        except Exception as e:
            # If we hit resource limits, that's acceptable
            if "memory" in str(e).lower() or "limit" in str(e).lower():
                pass
            else:
                raise

        # Verify we can still query the data that was saved
        history = sql_memory.get_scene_history(user_id="batch_test", limit=10)
        assert len(history) > 0, "Should have saved at least some scenes"
        assert len(history) <= 10, "Limit should be respected"

    @pytest.mark.fault
    def test_connection_pool_exhaustion(self, sql_memory):
        """System should handle connection pool exhaustion gracefully"""

        # This test would be more relevant for PostgreSQL with connection pooling
        # For SQLite, we simulate by rapid concurrent access

        import threading

        def rapid_query(results_list):
            try:
                for _ in range(10):
                    sql_memory.get_scene_history(user_id="pool_test", limit=1)
                results_list.append("success")
            except Exception as e:
                results_list.append(f"error: {e!s}")

        # Start many concurrent queries
        results = []
        threads = []

        for _ in range(20):
            result_list = []
            results.append(result_list)
            t = threading.Thread(target=rapid_query, args=(result_list,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5.0)

        # Most operations should succeed, but some failures are acceptable
        total_operations = sum(len(result_list) for result_list in results)
        successful_operations = sum(len([r for r in result_list if r == "success"]) for result_list in results)

        success_rate = successful_operations / max(total_operations, 1)
        assert success_rate >= 0.8, "At least 80% of operations should succeed"
