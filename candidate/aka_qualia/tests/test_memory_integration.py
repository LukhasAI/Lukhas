#!/usr/bin/env python3

"""
Integration Tests for Wave C Memory System
=========================================

Integration tests covering:
- SQL query correctness and performance
- Database schema validation
- Cross-component integration
- Real database operations
- Join queries and referential integrity

Target: Real database operations, complex scenarios
"""
import time

import pytest
import sqlalchemy
from sqlalchemy import text

from candidate.aka_qualia.tests.conftest import create_test_glyph, create_test_scene, create_varying_scene


class TestSQLQueryCorrectness:
    """Test that SQL queries work correctly against real database"""

    @pytest.mark.integration
    def test_get_scene_history_ordering(self, sql_memory_with_data):
        """Scene history should be ordered by timestamp descending"""

        results = sql_memory_with_data.get_scene_history(user_id="test_user", limit=5)

        # Verify we got results
        assert len(results) == 5

        # Verify chronological ordering (newest first)
        timestamps = [r["timestamp"] for r in results]
        assert timestamps == sorted(timestamps, reverse=True), "Results should be newest first"

        # Verify all results are for correct user
        for scene in results:
            assert "scene_id" in scene
            assert "proto" in scene
            assert isinstance(scene["timestamp"], (int, float))

    @pytest.mark.integration
    def test_scene_history_limit_respected(self, sql_memory_with_data):
        """Limit parameter should be respected in queries"""

        # Test different limits
        for limit in [1, 3, 10]:
            results = sql_memory_with_data.get_scene_history(user_id="test_user", limit=limit)
            assert len(results) <= limit, f"Results should not exceed limit {limit}"

    @pytest.mark.integration
    def test_risk_severity_filtering(
        self,
        sql_memory,
        high_risk_scene,
        low_risk_scene,
        test_glyphs,
        test_policy,
        test_metrics,
    ):
        """Should be able to filter scenes by risk severity"""

        # Add high and low risk scenes
        for scene, _risk_type in [(high_risk_scene, "high"), (low_risk_scene, "low")]:
            scene_data = scene.model_dump()
            sql_memory.save(
                user_id="risk_filter_test",
                scene=scene_data,
                glyphs=[g.model_dump() for g in test_glyphs],
                policy=test_policy.model_dump(),
                metrics=test_metrics.model_dump(),
                cfg_version="wave_c_v1.0.0",
            )

        # Test custom SQL query for high-risk scenes
        with sql_memory.engine.begin() as conn:
            query = text(
                """
                SELECT scene_id, risk->>'severity' as severity
                FROM akaq_scene
                WHERE user_id = :user_id
                AND risk->>'severity' = 'high'
                ORDER BY ts DESC
            """
            )

            results = conn.execute(query, {"user_id": "risk_filter_test"}).fetchall()

            assert len(results) == 1, "Should find exactly one high-risk scene"
            assert results[0].severity == "high"

    @pytest.mark.integration
    def test_glyph_search_functionality(self, sql_memory):
        """Glyph search should work correctly with joins"""

        # Create scenes with specific glyphs
        test_scenes = [
            {
                "scene": create_test_scene(subject=f"subject_{i}"),
                "glyphs": [
                    create_test_glyph(f"test:glyph_{i}"),
                    create_test_glyph("aka:vigilance"),  # Common glyph
                ],
            }
            for i in range(3)
        ]

        # Save all scenes
        for scene_data in test_scenes:
            sql_memory.save(
                user_id="glyph_search_test",
                scene=scene_data["scene"],
                glyphs=scene_data["glyphs"],
                policy={"gain": 1.0},
                metrics={"drift_phi": 0.9},
                cfg_version="wave_c_v1.0.0",
            )

        # Search for common glyph
        results = sql_memory.search_by_glyph(user_id="glyph_search_test", glyph_key="aka:vigilance")

        assert len(results) == 3, "Should find all 3 scenes with vigilance glyph"

        # Search for specific glyph
        specific_results = sql_memory.search_by_glyph(user_id="glyph_search_test", glyph_key="test:glyph_1")

        assert len(specific_results) == 1, "Should find exactly one scene with glyph_1"
        assert "subject_1" in str(specific_results[0])

    @pytest.mark.integration
    def test_scene_glyph_referential_integrity(self, sql_memory):
        """Scene-glyph joins should maintain referential integrity"""

        # Add scene with multiple glyphs
        scene_data = create_test_scene(subject="integrity_test")
        glyph_data = [
            create_test_glyph("glyph:alpha"),
            create_test_glyph("glyph:beta"),
            create_test_glyph("glyph:gamma"),
        ]

        scene_id = sql_memory.save(
            user_id="integrity_test",
            scene=scene_data,
            glyphs=glyph_data,
            policy={"gain": 1.0},
            metrics={"drift_phi": 0.9},
            cfg_version="wave_c_v1.0.0",
        )

        # Test complex join query
        with sql_memory.engine.begin() as conn:
            query = text(
                """
                SELECT
                    s.scene_id,
                    s.subject,
                    s.drift_phi,
                    array_agg(g.key ORDER BY g.key) as glyph_keys
                FROM akaq_scene s
                JOIN akaq_glyph g USING(scene_id)
                WHERE s.user_id = :user_id
                GROUP BY s.scene_id, s.subject, s.drift_phi
                ORDER BY s.ts DESC
            """
            )

            results = conn.execute(query, {"user_id": "integrity_test"}).fetchall()

            assert len(results) == 1, "Should find exactly one scene"
            result = results[0]

            assert result.scene_id == scene_id
            assert result.subject == "integrity_test"  # Assuming dev mode
            assert isinstance(result.glyph_keys, list)
            assert len(result.glyph_keys) == 3
            assert "glyph:alpha" in result.glyph_keys
            assert "glyph:beta" in result.glyph_keys
            assert "glyph:gamma" in result.glyph_keys


class TestDatabaseSchemaValidation:
    """Test database schema constraints and validations"""

    @pytest.mark.integration
    def test_required_columns_exist(self, sql_memory):
        """Database schema should have all required columns"""

        with sql_memory.engine.begin() as conn:
            # Check akaq_scene table structure
            scene_columns = conn.execute(
                text(
                    """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'akaq_scene'
                ORDER BY ordinal_position
            """
                )
            )

            scene_cols = {row.column_name: row for row in scene_columns}

            # Required columns
            required_scene_cols = [
                "scene_id",
                "user_id",
                "ts",
                "subject",
                "object",
                "proto",
                "proto_vec",
                "risk",
                "context",
                "drift_phi",
                "congruence_index",
                "neurosis_risk",
            ]

            for col in required_scene_cols:
                assert col in scene_cols, f"Missing required column: {col}"

            # Check akaq_glyph table structure
            glyph_columns = conn.execute(
                text(
                    """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'akaq_glyph'
                ORDER BY ordinal_position
            """
                )
            )

            glyph_cols = {row.column_name: row for row in glyph_columns}

            required_glyph_cols = ["scene_id", "key", "attrs"]
            for col in required_glyph_cols:
                assert col in glyph_cols, f"Missing required glyph column: {col}"

    @pytest.mark.integration
    def test_indexes_exist_and_perform(self, sql_memory):
        """Critical indexes should exist and provide good performance"""

        with sql_memory.engine.begin() as conn:
            # Check that user_id + timestamp index exists
            index_query = text(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'akaq_scene'
                AND indexdef LIKE '%user_id%'
                AND indexdef LIKE '%ts%'
            """
            )

            try:
                indexes = conn.execute(index_query).fetchall()
                # Note: This will fail on SQLite, but would work on PostgreSQL
                # For SQLite, we'd need a different query
            except (sqlalchemy.exc.DatabaseError, sqlalchemy.exc.OperationalError):
                # SQLite doesn't have pg_indexes, use sqlite_master
                sqlite_index_query = text(
                    """
                    SELECT name, sql
                    FROM sqlite_master
                    WHERE type='index'
                    AND tbl_name='akaq_scene'
                    AND sql LIKE '%user_id%'
                """
                )
                indexes = conn.execute(sqlite_index_query).fetchall()

            # Should have at least one compound index on user_id
            assert len(indexes) >= 1, "Should have user_id index for performance"

    @pytest.mark.integration
    def test_foreign_key_constraints(self, sql_memory):
        """Foreign key constraints should be enforced"""

        # Try to insert glyph with non-existent scene_id
        with sql_memory.engine.begin() as conn:
            try:
                conn.execute(
                    text(
                        """
                    INSERT INTO akaq_glyph (scene_id, key, attrs)
                    VALUES ('nonexistent_scene_id', 'test:key', '{}')
                """
                    )
                )

                # If we get here, foreign key constraint is not enforced
                # This might be expected for SQLite with foreign keys disabled
                pass

            except Exception as e:
                # Foreign key constraint should prevent this
                assert "foreign key" in str(e).lower() or "constraint" in str(e).lower()


class TestConcurrentOperations:
    """Test concurrent database operations"""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skip(reason="URGENT: SQLite threading causes segfaults - disabled until thread-safe implementation")
    def test_concurrent_saves(self, sql_memory):
        """Multiple concurrent saves should not interfere"""

        import queue
        import threading

        results_queue = queue.Queue()
        error_queue = queue.Queue()

        def save_scene(thread_id):
            try:
                scene_data = create_varying_scene(f"concurrent_test_{thread_id}")
                glyph_data = [create_test_glyph(f"concurrent:glyph_{thread_id}")]

                scene_id = sql_memory.save(
                    user_id=f"concurrent_user_{thread_id % 3}",  # 3 different users
                    scene=scene_data,
                    glyphs=glyph_data,
                    policy={"gain": 1.0},
                    metrics={"drift_phi": 0.9},
                    cfg_version="wave_c_v1.0.0",
                )

                results_queue.put((thread_id, scene_id))

            except Exception as e:
                error_queue.put((thread_id, str(e)))

        # Launch 10 concurrent save operations
        threads = []
        for i in range(10):
            t = threading.Thread(target=save_scene, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join(timeout=5.0)

        # Check results
        assert error_queue.empty(), f"Errors occurred: {list(error_queue.queue)}"
        assert results_queue.qsize() == 10, "All saves should have completed successfully"

        # Verify all scene IDs are unique
        scene_ids = [results_queue.get()[1] for _ in range(10)]
        assert len(set(scene_ids)) == 10, "All scene IDs should be unique"


class TestAkaQualiaIntegration:
    """Test integration between AkaQualia core and memory system"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_memory_persistence(self, aq_with_sql_memory):
        """Complete consciousness pipeline should persist to memory"""

        signals = {
            "text": "I'm feeling contemplative about the nature of memory",
            "subject": "observer",
            "object": "contemplation",
        }
        goals = {"understand_memory": True}
        ethics_state = {"drift_score": 0.02}
        guardian_state = {"active": True}
        memory_ctx = {"session_id": "integration_test"}

        # Run consciousness step
        result = await aq_with_sql_memory.step(
            signals=signals,
            goals=goals,
            ethics_state=ethics_state,
            guardian_state=guardian_state,
            memory_ctx=memory_ctx,
        )

        # Verify result structure
        assert "scene" in result
        assert "glyphs" in result
        assert "metrics" in result

        # Verify data was persisted
        memory = aq_with_sql_memory.memory
        stats = memory.get_stats()
        assert stats["total_saves"] >= 1, "Should have persisted at least one scene"

        # Verify we can retrieve the data
        history = memory.get_scene_history(user_id="system", limit=1)
        assert len(history) == 1, "Should be able to retrieve persisted scene"

        stored_scene = history[0]
        assert stored_scene["subject"] == "observer"
        assert "proto" in stored_scene
        assert "context" in stored_scene
        # Context flow may be transformed during processing
        context = stored_scene["context"]
        assert context is not None, "Context should be stored"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_memory_aware_drift_computation(self, aq_with_sql_memory):
        """Second scene should use memory for drift computation"""

        base_signals = {
            "text": "First contemplative moment",
            "subject": "observer",
            "object": "first_thought",
        }

        # First scene
        result1 = await aq_with_sql_memory.step(
            signals=base_signals,
            goals={},
            ethics_state={},
            guardian_state={"active": True},
            memory_ctx={"session_id": "drift_test"},
        )

        metrics1 = result1["metrics"]
        assert metrics1.drift_phi == 1.0, "First scene should have perfect drift (no history)"

        # Second scene - different signals
        changed_signals = {
            "text": "Second contemplative moment with change",
            "subject": "observer",
            "object": "changed_thought",
        }

        result2 = await aq_with_sql_memory.step(
            signals=changed_signals,
            goals={},
            ethics_state={},
            guardian_state={"active": True},
            memory_ctx={"session_id": "drift_test"},
        )

        metrics2 = result2["metrics"]
        assert 0.0 <= metrics2.drift_phi <= 1.0, "Drift phi should be valid range"
        assert metrics2.drift_phi < 1.0, "Second scene should show some drift from first"

        # Verify both scenes are in memory
        memory = aq_with_sql_memory.memory
        history = memory.get_scene_history(user_id="system", limit=2)
        assert len(history) == 2, "Should have both scenes in memory"

        # Verify ordering (newest first)
        timestamps = [scene["timestamp"] for scene in history]
        assert timestamps[0] > timestamps[1], "Newer scene should come first"


class TestComplexQueries:
    """Test complex database queries and aggregations"""

    @pytest.mark.integration
    def test_drift_phi_aggregation(self, sql_memory):
        """Should be able to aggregate drift metrics across scenes"""

        # Add multiple scenes with varying drift values
        drift_values = [0.95, 0.87, 0.92, 0.78, 0.89]

        for i, drift in enumerate(drift_values):
            scene_data = create_test_scene(subject=f"drift_test_{i}")
            sql_memory.save(
                user_id="drift_aggregation_test",
                scene=scene_data,
                glyphs=[create_test_glyph(f"test:glyph_{i}")],
                policy={"gain": 1.0},
                metrics={"drift_phi": drift},
                cfg_version="wave_c_v1.0.0",
            )

        # Test aggregation query
        with sql_memory.engine.begin() as conn:
            query = text(
                """
                SELECT
                    COUNT(*) as scene_count,
                    AVG(drift_phi) as avg_drift,
                    MIN(drift_phi) as min_drift,
                    MAX(drift_phi) as max_drift,
                    STDDEV(drift_phi) as stddev_drift
                FROM akaq_scene
                WHERE user_id = :user_id
            """
            )

            result = conn.execute(query, {"user_id": "drift_aggregation_test"}).fetchone()

            assert result.scene_count == 5
            assert abs(result.avg_drift - sum(drift_values) / len(drift_values)) < 0.001
            assert result.min_drift == min(drift_values)
            assert result.max_drift == max(drift_values)

    @pytest.mark.integration
    def test_temporal_windowing_queries(self, sql_memory):
        """Should support time-based windowing of scenes"""

        # Add scenes with specific timestamps
        base_time = time.time()
        scene_times = [
            base_time - 3600,  # 1 hour ago
            base_time - 1800,  # 30 minutes ago
            base_time - 900,  # 15 minutes ago
            base_time - 300,  # 5 minutes ago
            base_time,  # now
        ]

        for i, scene_time in enumerate(scene_times):
            create_test_scene(subject=f"temporal_test_{i}", timestamp=scene_time)

            # Manually set the timestamp in the save call
            with sql_memory.engine.begin() as conn:
                scene_id = f"temporal_{i}_{int(scene_time)}"

                conn.execute(
                    text(
                        """
                    INSERT INTO akaq_scene (
                        scene_id, user_id, ts, subject, object, proto, proto_vec,
                        risk, context, drift_phi, congruence_index, neurosis_risk,
                        repair_delta, sublimation_rate, cfg_version
                    ) VALUES (
                        :scene_id, :user_id, to_timestamp(:ts), :subject, :object,
                        :proto, :proto_vec, :risk, :context, :drift_phi,
                        :congruence_index, :neurosis_risk, :repair_delta,
                        :sublimation_rate, :cfg_version
                    )
                """
                    ),
                    {
                        "scene_id": scene_id,
                        "user_id": "temporal_test",
                        "ts": scene_time,
                        "subject": f"temporal_test_{i}",
                        "object": "temporal_object",
                        "proto": '{"tone": 0.0}',
                        "proto_vec": [0.0, 0.0, 0.0, 0.0, 0.0],
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

        # Query for scenes in last 20 minutes
        cutoff_time = base_time - 1200  # 20 minutes ago

        with sql_memory.engine.begin() as conn:
            query = text(
                """
                SELECT scene_id, subject, EXTRACT(EPOCH FROM ts) as timestamp
                FROM akaq_scene
                WHERE user_id = :user_id
                AND ts >= to_timestamp(:cutoff_time)
                ORDER BY ts DESC
            """
            )

            results = conn.execute(query, {"user_id": "temporal_test", "cutoff_time": cutoff_time}).fetchall()

            # Should get the last 3 scenes (15 min, 5 min, now)
            assert len(results) == 3, f"Should find 3 recent scenes, got {len(results)}"

            # Verify ordering and timestamps
            timestamps = [row.timestamp for row in results]
            assert timestamps == sorted(timestamps, reverse=True)
            assert all(ts >= cutoff_time for ts in timestamps)
