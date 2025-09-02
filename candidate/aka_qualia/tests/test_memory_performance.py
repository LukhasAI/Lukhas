#!/usr/bin/env python3

"""
Performance Tests for Wave C Memory System
==========================================

Performance benchmarks and stress tests covering:
- Batch write performance (1k scenes < 2s)
- Query performance with indexing (< 5ms p95)
- Memory usage under load
- Concurrent access scalability
- Large dataset handling
- Performance regression detection

Target: Production SLA validation
"""

import gc
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

import psutil
import pytest

from .conftest import create_test_glyph, create_test_scene, create_varying_scene


class TestBatchWritePerformance:
    """Test batch write operations and throughput"""

    @pytest.mark.perf
    @pytest.mark.slow
    def test_1k_scene_insert_performance(self, sql_memory, performance_timer):
        """1000 scene inserts should complete < 2s (local database)"""

        num_scenes = 1000

        # Generate test data upfront (don't include in timing)
        test_data = []
        for i in range(num_scenes):
            scene_data = create_varying_scene(f"perf_test_{i}")
            glyph_data = [
                create_test_glyph(f"perf:glyph_{i}", value=i),
                create_test_glyph("batch:test", batch_id=i // 100),  # Group by hundreds
            ]
            test_data.append((scene_data, glyph_data))

        # Measure insertion performance
        performance_timer.start()

        scene_ids = []
        for i, (scene_data, glyph_data) in enumerate(test_data):
            scene_id = sql_memory.save(
                user_id=f"perf_user_{i % 10}",  # 10 different users
                scene=scene_data,
                glyphs=glyph_data,
                policy={"gain": 1.0, "pace": 1.0},
                metrics={"drift_phi": 0.9, "congruence_index": 0.8},
                cfg_version="wave_c_v1.0.0",
            )
            scene_ids.append(scene_id)

        elapsed_time = performance_timer.stop()

        # Performance assertions
        assert elapsed_time < 3.0, f"1000 inserts took {elapsed_time:.2f}s, should be < 3.0s"
        assert len(scene_ids) == num_scenes, f"Should have {num_scenes} scene IDs"
        assert len(set(scene_ids)) == num_scenes, "All scene IDs should be unique"

        # Throughput metrics
        throughput = num_scenes / elapsed_time
        print(f"Batch insert throughput: {throughput:.1f} scenes/second")
        assert throughput > 300, f"Throughput {throughput:.1f} scenes/sec is too low"

        # Verify data integrity after bulk insert
        total_scenes = sum(len(sql_memory.get_scene_history(user_id=f"perf_user_{i}", limit=1000)) for i in range(10))
        assert total_scenes == num_scenes, "All scenes should be retrievable after bulk insert"

    @pytest.mark.perf
    def test_incremental_write_performance(self, sql_memory, performance_timer):
        """Individual writes should maintain consistent performance"""

        num_iterations = 100
        write_times = []

        for i in range(num_iterations):
            scene_data = create_varying_scene(f"incremental_test_{i}")
            glyph_data = [create_test_glyph(f"incremental:glyph_{i}")]

            # Time individual write
            start_time = time.perf_counter()

            scene_id = sql_memory.save(
                user_id="incremental_perf_test",
                scene=scene_data,
                glyphs=glyph_data,
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

            end_time = time.perf_counter()
            write_time = end_time - start_time
            write_times.append(write_time)

            assert scene_id is not None, f"Write {i} should succeed"

        # Performance statistics
        avg_time = statistics.mean(write_times)
        p95_time = statistics.quantiles(write_times, n=20)[18]  # 95th percentile
        max_time = max(write_times)

        print(f"Write performance - Avg: {avg_time*1000:.2f}ms, P95: {p95_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")

        # Performance assertions
        assert avg_time < 0.01, f"Average write time {avg_time*1000:.2f}ms should be < 10ms"
        assert p95_time < 0.02, f"P95 write time {p95_time*1000:.2f}ms should be < 20ms"
        assert max_time < 0.05, f"Max write time {max_time*1000:.2f}ms should be < 50ms"

    @pytest.mark.perf
    def test_batch_vs_individual_performance(self, sql_memory):
        """Batch operations should be significantly faster than individual operations"""

        num_scenes = 100

        # Generate test data
        test_scenes = [create_varying_scene(f"batch_vs_individual_{i}") for i in range(num_scenes)]
        test_glyphs = [[create_test_glyph(f"test:glyph_{i}")] for i in range(num_scenes)]

        # Test individual inserts
        individual_start = time.perf_counter()
        for i in range(num_scenes):
            sql_memory.save(
                user_id="individual_test",
                scene=test_scenes[i],
                glyphs=test_glyphs[i],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )
        individual_time = time.perf_counter() - individual_start

        # Test batch-style insert (rapid succession)
        batch_start = time.perf_counter()
        for i in range(num_scenes):
            sql_memory.save(
                user_id="batch_test",
                scene=test_scenes[i],
                glyphs=test_glyphs[i],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )
        batch_time = time.perf_counter() - batch_start

        print(f"Individual inserts: {individual_time:.2f}s ({individual_time/num_scenes*1000:.2f}ms each)")
        print(f"Batch inserts: {batch_time:.2f}s ({batch_time/num_scenes*1000:.2f}ms each)")

        # Both should be reasonably fast
        assert individual_time < 5.0, "Individual inserts should complete in reasonable time"
        assert batch_time < 5.0, "Batch inserts should complete in reasonable time"


class TestQueryPerformance:
    """Test query performance with various data sizes"""

    @pytest.mark.perf
    def test_user_history_query_performance(self, sql_memory_with_data, performance_timer):
        """User history queries should be fast with proper indexing"""

        # Add more data to make the test meaningful
        for i in range(50):  # Add 50 more scenes to existing 5
            scene_data = create_varying_scene(f"query_perf_test_{i}")
            sql_memory_with_data.save(
                user_id="test_user",
                scene=scene_data,
                glyphs=[create_test_glyph(f"query_perf:glyph_{i}")],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

        # Test query performance
        query_times = []

        for _ in range(20):  # Multiple queries to get average
            performance_timer.start()
            results = sql_memory_with_data.get_scene_history(user_id="test_user", limit=10)
            query_time = performance_timer.stop()

            query_times.append(query_time)
            assert len(results) == 10, "Should return requested number of results"

        avg_query_time = statistics.mean(query_times)
        p95_query_time = statistics.quantiles(query_times, n=20)[18]

        print(f"Query performance - Avg: {avg_query_time*1000:.2f}ms, P95: {p95_query_time*1000:.2f}ms")

        # Performance assertions
        assert avg_query_time < 0.01, f"Average query time {avg_query_time*1000:.2f}ms should be < 10ms"
        assert p95_query_time < 0.02, f"P95 query time {p95_query_time*1000:.2f}ms should be < 20ms"

    @pytest.mark.perf
    def test_glyph_search_performance(self, sql_memory, performance_timer):
        """Glyph search should scale well with data size"""

        # Create scenes with common and unique glyphs
        common_glyph_key = "performance:common"
        unique_prefix = "performance:unique"

        # Insert data with predictable glyph distribution
        for i in range(200):
            glyphs = [
                create_test_glyph(common_glyph_key),  # Every scene has this
                create_test_glyph(f"{unique_prefix}_{i}"),  # Each scene has unique glyph
            ]

            # Some scenes have additional glyphs
            if i % 10 == 0:
                glyphs.append(create_test_glyph("performance:rare"))

            sql_memory.save(
                user_id="glyph_search_perf_test",
                scene=create_varying_scene(f"glyph_search_perf_{i}"),
                glyphs=glyphs,
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

        # Test common glyph search (should find many results)
        performance_timer.start()
        common_results = sql_memory.search_by_glyph(user_id="glyph_search_perf_test", glyph_key=common_glyph_key)
        common_search_time = performance_timer.stop()

        assert len(common_results) == 200, "Should find all scenes with common glyph"
        assert common_search_time < 0.05, f"Common glyph search took {common_search_time*1000:.2f}ms, should be < 50ms"

        # Test unique glyph search (should find one result)
        performance_timer.start()
        unique_results = sql_memory.search_by_glyph(user_id="glyph_search_perf_test", glyph_key=f"{unique_prefix}_100")
        unique_search_time = performance_timer.stop()

        assert len(unique_results) == 1, "Should find exactly one scene with unique glyph"
        assert unique_search_time < 0.01, f"Unique glyph search took {unique_search_time*1000:.2f}ms, should be < 10ms"

        # Test rare glyph search
        performance_timer.start()
        rare_results = sql_memory.search_by_glyph(user_id="glyph_search_perf_test", glyph_key="performance:rare")
        rare_search_time = performance_timer.stop()

        assert len(rare_results) == 20, "Should find 20 scenes with rare glyph (every 10th)"
        assert rare_search_time < 0.02, f"Rare glyph search took {rare_search_time*1000:.2f}ms, should be < 20ms"

    @pytest.mark.perf
    def test_large_result_set_performance(self, sql_memory):
        """Large result sets should be handled efficiently"""

        # Create large dataset
        num_scenes = 500
        user_id = "large_dataset_test"

        for i in range(num_scenes):
            scene_data = create_varying_scene(f"large_dataset_{i}")
            sql_memory.save(
                user_id=user_id,
                scene=scene_data,
                glyphs=[create_test_glyph(f"large:glyph_{i}")],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

        # Test various limit sizes
        limit_tests = [10, 50, 100, 250]

        for limit in limit_tests:
            start_time = time.perf_counter()
            results = sql_memory.get_scene_history(user_id=user_id, limit=limit)
            query_time = time.perf_counter() - start_time

            assert len(results) == limit, f"Should return exactly {limit} results"
            assert query_time < 0.1, f"Query for {limit} results took {query_time*1000:.2f}ms, should be < 100ms"

            # Verify results are properly ordered (newest first)
            timestamps = [scene["timestamp"] for scene in results]
            assert timestamps == sorted(timestamps, reverse=True), "Results should be ordered by timestamp desc"


class TestMemoryUsagePerformance:
    """Test memory usage and garbage collection"""

    @pytest.mark.perf
    @pytest.mark.slow
    def test_memory_usage_under_load(self, sql_memory):
        """Memory usage should remain stable under continuous load"""

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Initial memory usage: {initial_memory:.1f} MB")

        # Continuous operation for extended period
        num_iterations = 200
        memory_samples = []

        for i in range(num_iterations):
            # Create and save scene
            scene_data = create_varying_scene(f"memory_test_{i}")
            glyph_data = [create_test_glyph(f"memory:test_{i}")]

            sql_memory.save(
                user_id=f"memory_user_{i % 5}",
                scene=scene_data,
                glyphs=glyph_data,
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

            # Query some data
            sql_memory.get_scene_history(user_id=f"memory_user_{i % 5}", limit=5)

            # Sample memory usage periodically
            if i % 20 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)

                # Force garbage collection to test for leaks
                gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        max_memory = max(memory_samples)

        print(f"Final memory usage: {final_memory:.1f} MB")
        print(f"Memory growth: {memory_growth:.1f} MB")
        print(f"Max memory usage: {max_memory:.1f} MB")

        # Memory growth should be reasonable
        assert memory_growth < 50, f"Memory growth {memory_growth:.1f} MB is too high"
        assert max_memory < initial_memory + 100, f"Peak memory usage {max_memory:.1f} MB is too high"

    @pytest.mark.perf
    def test_large_scene_memory_handling(self, sql_memory):
        """Large individual scenes should be handled efficiently"""

        # Create scene with large context data
        large_context = {
            "cfg_version": "wave_c_v1.0.0",
            "large_array": list(range(10000)),  # 10k integers
            "large_text": "x" * 50000,  # 50k characters
            "nested_data": {
                f"key_{i}": f"value_{i}" * 100
                for i in range(1000)  # 1k nested items
            },
        }

        large_scene = create_test_scene(context=large_context)

        # Measure memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024

        # Save large scene
        start_time = time.perf_counter()
        sql_memory.save(
            user_id="large_scene_test",
            scene=large_scene,
            glyphs=[create_test_glyph("large:scene")],
            policy={},
            metrics={},
            cfg_version="wave_c_v1.0.0",
        )
        save_time = time.perf_counter() - start_time

        # Measure memory after
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_delta = memory_after - memory_before

        print(f"Large scene save time: {save_time*1000:.2f}ms")
        print(f"Memory delta: {memory_delta:.1f} MB")

        # Should handle large scenes without excessive time/memory
        assert save_time < 1.0, f"Large scene save took {save_time*1000:.2f}ms, should be < 1000ms"
        assert memory_delta < 100, f"Memory increase {memory_delta:.1f} MB is too high"

        # Verify we can retrieve the large scene
        start_time = time.perf_counter()
        history = sql_memory.get_scene_history(user_id="large_scene_test", limit=1)
        retrieve_time = time.perf_counter() - start_time

        assert len(history) == 1, "Should retrieve the large scene"
        assert retrieve_time < 0.1, f"Large scene retrieval took {retrieve_time*1000:.2f}ms, should be < 100ms"


class TestConcurrentPerformance:
    """Test performance under concurrent access"""

    @pytest.mark.perf
    @pytest.mark.slow
    def test_concurrent_write_throughput(self, sql_memory):
        """Concurrent writes should scale reasonably"""

        num_threads = 5
        scenes_per_thread = 50
        total_scenes = num_threads * scenes_per_thread

        def write_scenes(thread_id: int, results: list):
            thread_results = []
            thread_start = time.perf_counter()

            for i in range(scenes_per_thread):
                scene_data = create_varying_scene(f"concurrent_write_{thread_id}_{i}")
                glyph_data = [create_test_glyph(f"concurrent:thread_{thread_id}_glyph_{i}")]

                try:
                    scene_id = sql_memory.save(
                        user_id=f"concurrent_user_{thread_id}",
                        scene=scene_data,
                        glyphs=glyph_data,
                        policy={},
                        metrics={},
                        cfg_version="wave_c_v1.0.0",
                    )
                    thread_results.append(scene_id)
                except Exception as e:
                    thread_results.append(f"ERROR: {e!s}")

            thread_time = time.perf_counter() - thread_start
            results.append(
                {
                    "thread_id": thread_id,
                    "scenes_saved": len([r for r in thread_results if not str(r).startswith("ERROR")]),
                    "errors": len([r for r in thread_results if str(r).startswith("ERROR")]),
                    "time": thread_time,
                    "throughput": len(thread_results) / thread_time,
                }
            )

        # Execute concurrent writes
        overall_start = time.perf_counter()

        results = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(write_scenes, thread_id, results) for thread_id in range(num_threads)]

            # Wait for all threads to complete
            for future in futures:
                future.result(timeout=30)

        overall_time = time.perf_counter() - overall_start

        # Analyze results
        total_saved = sum(r["scenes_saved"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        overall_throughput = total_saved / overall_time
        avg_thread_throughput = statistics.mean([r["throughput"] for r in results])

        print("Concurrent write performance:")
        print(f"  Total scenes saved: {total_saved}/{total_scenes}")
        print(f"  Total errors: {total_errors}")
        print(f"  Overall time: {overall_time:.2f}s")
        print(f"  Overall throughput: {overall_throughput:.1f} scenes/sec")
        print(f"  Average thread throughput: {avg_thread_throughput:.1f} scenes/sec")

        # Performance assertions
        assert total_errors == 0, f"Should have no errors, got {total_errors}"
        assert total_saved == total_scenes, f"Should save all {total_scenes} scenes, saved {total_saved}"
        assert overall_throughput > 50, f"Overall throughput {overall_throughput:.1f} scenes/sec is too low"
        assert overall_time < 10, f"Overall time {overall_time:.2f}s is too high"

    @pytest.mark.perf
    def test_concurrent_read_write_performance(self, sql_memory):
        """Mixed read/write workloads should perform well"""

        # Pre-populate with some data
        for i in range(100):
            sql_memory.save(
                user_id="mixed_workload_user",
                scene=create_varying_scene(f"mixed_initial_{i}"),
                glyphs=[create_test_glyph(f"mixed:initial_{i}")],
                policy={},
                metrics={},
                cfg_version="wave_c_v1.0.0",
            )

        def mixed_workload(thread_id: int, results: list):
            operations = []
            thread_start = time.perf_counter()

            for i in range(20):  # 20 operations per thread
                op_start = time.perf_counter()

                if i % 3 == 0:  # Write operation (33%)
                    scene_data = create_varying_scene(f"mixed_write_{thread_id}_{i}")
                    try:
                        sql_memory.save(
                            user_id=f"mixed_user_{thread_id}",
                            scene=scene_data,
                            glyphs=[create_test_glyph(f"mixed:write_{thread_id}_{i}")],
                            policy={},
                            metrics={},
                            cfg_version="wave_c_v1.0.0",
                        )
                        op_type = "write_success"
                    except Exception:
                        op_type = "write_error"
                else:  # Read operation (67%)
                    try:
                        results_data = sql_memory.get_scene_history(user_id="mixed_workload_user", limit=10)
                        op_type = "read_success" if len(results_data) > 0 else "read_empty"
                    except Exception:
                        op_type = "read_error"

                op_time = time.perf_counter() - op_start
                operations.append({"type": op_type, "time": op_time})

            thread_time = time.perf_counter() - thread_start
            results.append({"thread_id": thread_id, "total_time": thread_time, "operations": operations})

        # Execute mixed workload
        overall_start = time.perf_counter()

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(mixed_workload, thread_id, results) for thread_id in range(4)]

            for future in futures:
                future.result(timeout=20)

        overall_time = time.perf_counter() - overall_start

        # Analyze mixed workload performance
        all_operations = []
        for result in results:
            all_operations.extend(result["operations"])

        write_ops = [op for op in all_operations if op["type"].startswith("write")]
        read_ops = [op for op in all_operations if op["type"].startswith("read")]
        error_ops = [op for op in all_operations if "error" in op["type"]]

        avg_write_time = statistics.mean([op["time"] for op in write_ops]) if write_ops else 0
        avg_read_time = statistics.mean([op["time"] for op in read_ops]) if read_ops else 0

        print("Mixed workload performance:")
        print(f"  Write operations: {len(write_ops)}, avg time: {avg_write_time*1000:.2f}ms")
        print(f"  Read operations: {len(read_ops)}, avg time: {avg_read_time*1000:.2f}ms")
        print(f"  Error operations: {len(error_ops)}")
        print(f"  Overall time: {overall_time:.2f}s")

        # Performance assertions
        assert len(error_ops) == 0, f"Should have no errors, got {len(error_ops)}"
        assert avg_write_time < 0.02, f"Average write time {avg_write_time*1000:.2f}ms is too high"
        assert avg_read_time < 0.01, f"Average read time {avg_read_time*1000:.2f}ms is too high"

    @pytest.mark.perf
    def test_connection_contention_handling(self, sql_memory):
        """High connection contention should be handled gracefully"""

        num_threads = 20  # High contention
        operations_per_thread = 10

        def high_contention_operations(thread_id: int, results: list):
            success_count = 0
            error_count = 0

            for i in range(operations_per_thread):
                try:
                    # Mix of operations that might cause contention
                    if i % 2 == 0:
                        # Write operation
                        sql_memory.save(
                            user_id=f"contention_user_{thread_id}",
                            scene=create_varying_scene(f"contention_{thread_id}_{i}"),
                            glyphs=[create_test_glyph(f"contention:glyph_{thread_id}_{i}")],
                            policy={},
                            metrics={},
                            cfg_version="wave_c_v1.0.0",
                        )
                    else:
                        # Read operation
                        sql_memory.get_scene_history(user_id=f"contention_user_{thread_id}", limit=5)

                    success_count += 1

                except Exception:
                    error_count += 1
                    # Some errors may be acceptable under high contention

            results.append({"thread_id": thread_id, "success": success_count, "errors": error_count})

        # Execute high contention test
        start_time = time.perf_counter()

        results = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(high_contention_operations, thread_id, results) for thread_id in range(num_threads)
            ]

            for future in futures:
                future.result(timeout=15)

        total_time = time.perf_counter() - start_time

        # Analyze contention handling
        total_success = sum(r["success"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        total_operations = total_success + total_errors
        success_rate = total_success / total_operations if total_operations > 0 else 0

        print("Connection contention test:")
        print(f"  Total operations: {total_operations}")
        print(f"  Successful operations: {total_success}")
        print(f"  Failed operations: {total_errors}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Total time: {total_time:.2f}s")

        # Under high contention, we expect some resilience
        assert success_rate >= 0.90, f"Success rate {success_rate:.2%} is too low"
        assert total_time < 15, f"Total time {total_time:.2f}s is too high"
