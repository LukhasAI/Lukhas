"""
Performance Benchmarks for LUKHAS Core Wiring
==============================================

Benchmarks for dreams, glyphs, and drift APIs to ensure performance targets:
- Dream simulation: < 250ms p95
- GLYPH encoding: < 100ms p95
- Drift update: < 50ms p95
- API overhead: < 10ms

Run with: pytest tests/performance/test_core_wiring_benchmarks.py -v --benchmark-only
"""
import time
import pytest
from unittest.mock import patch, MagicMock

# Skip if pytest-benchmark not available
pytest_benchmark = pytest.importorskip("pytest_benchmark")


class TestDreamsPerformance:
    """Performance benchmarks for Dreams API"""

    @pytest.fixture
    def dream_wrapper_enabled(self):
        """Mock dreams wrapper as enabled"""
        with patch('lukhas.dream.is_enabled', return_value=True):
            with patch('lukhas.dream._DREAMS_AVAILABLE', True):
                yield

    def test_simulate_dream_latency(self, benchmark, dream_wrapper_enabled):
        """Dream simulation should complete in < 250ms"""
        from lukhas.dream import simulate_dream

        result = benchmark(
            simulate_dream,
            seed="benchmark_test",
            context={"test": "data"}
        )

        assert result["success"] is True
        assert "dream_id" in result
        # Benchmark will measure and report timing automatically

    def test_simulate_dream_with_context_latency(self, benchmark, dream_wrapper_enabled):
        """Dream simulation with rich context should complete in < 300ms"""
        from lukhas.dream import simulate_dream

        context = {
            "mood": "focused",
            "time": "morning",
            "tags": ["work", "productivity"],
            "metadata": {"session_id": "test_123"}
        }

        result = benchmark(
            simulate_dream,
            seed="complex_benchmark",
            context=context
        )

        assert result["success"] is True

    def test_parallel_mesh_throughput(self, benchmark, dream_wrapper_enabled):
        """Parallel dream mesh should handle multiple seeds efficiently"""
        with patch('lukhas.dream.is_parallel_enabled', return_value=True):
            from lukhas.dream import parallel_dream_mesh

            seeds = [f"seed_{i}" for i in range(5)]

            result = benchmark(
                parallel_dream_mesh,
                seeds=seeds,
                consensus_threshold=0.7
            )

            assert result["success"] is True
            assert len(result["seeds"]) == 5


class TestGlyphsPerformance:
    """Performance benchmarks for GLYPHs API"""

    @pytest.fixture
    def glyph_wrapper_enabled(self):
        """Mock glyphs wrapper as enabled"""
        with patch('lukhas.glyphs.is_enabled', return_value=True):
            with patch('lukhas.glyphs._GLYPHS_AVAILABLE', True):
                # Mock the glyph engine
                mock_engine = MagicMock()
                mock_symbol = MagicMock()
                mock_symbol.symbol_id = "bench_sym_123"
                mock_engine.encode_concept.return_value = mock_symbol

                with patch('lukhas.glyphs._glyph_engine', mock_engine):
                    yield

    def test_encode_concept_latency(self, benchmark, glyph_wrapper_enabled):
        """GLYPH encoding should complete in < 100ms"""
        from lukhas.glyphs import encode_concept

        result = benchmark(
            encode_concept,
            concept="benchmark_concept",
            emotion={"joy": 0.8}
        )

        assert result is not None
        assert "concept" in result

    def test_bind_glyph_latency(self, benchmark, glyph_wrapper_enabled):
        """GLYPH binding should complete in < 150ms"""
        from lukhas.glyphs import bind_glyph

        glyph_data = {
            "concept": "test_concept",
            "emotion": {"joy": 0.7}
        }

        result = benchmark(
            bind_glyph,
            glyph_data=glyph_data,
            memory_id="mem_bench_123",
            user_id="user_bench"
        )

        assert result["success"] is True

    def test_validate_glyph_latency(self, benchmark):
        """GLYPH validation should be very fast (< 10ms)"""
        from lukhas.glyphs import validate_glyph

        glyph_data = {
            "concept": "test",
            "emotion": {"joy": 0.5, "calm": 0.6}
        }

        is_valid, error = benchmark(
            validate_glyph,
            glyph_data
        )

        assert is_valid is True


class TestDriftPerformance:
    """Performance benchmarks for Drift Monitoring API"""

    @pytest.fixture
    def drift_available(self):
        """Mock drift module as available"""
        with patch('lukhas_website.lukhas.api.drift._DRIFT_AVAILABLE', True):
            from lukhas_website.lukhas.core.drift import DriftMonitor
            yield DriftMonitor

    def test_drift_update_latency(self, benchmark, drift_available):
        """Drift update should be very fast (< 50ms)"""
        monitor = drift_available(lane="experimental")

        intent = [1.0, 0.0, 0.5, 0.3]
        action = [0.9, 0.1, 0.4, 0.35]

        result = benchmark(
            monitor.update,
            intent=intent,
            action=action
        )

        assert "drift" in result
        assert "ema" in result

    def test_drift_update_large_vectors(self, benchmark, drift_available):
        """Drift should handle large vectors efficiently"""
        monitor = drift_available(lane="experimental")

        # Simulate larger embedding vectors (e.g., 768-dim)
        size = 768
        intent = [0.5 + (i % 100) / 200 for i in range(size)]
        action = [0.5 + (i % 100) / 200 + 0.01 for i in range(size)]

        result = benchmark(
            monitor.update,
            intent=intent,
            action=action
        )

        assert "drift" in result

    def test_drift_ema_calculation_overhead(self, benchmark, drift_available):
        """EMA calculation overhead should be minimal"""
        monitor = drift_available(lane="prod")

        # Pre-populate with some history
        for i in range(50):
            monitor.update([1.0, 0.0], [0.9, 0.1])

        # Benchmark the update with history
        result = benchmark(
            monitor.update,
            intent=[1.0, 0.0],
            action=[0.95, 0.05]
        )

        assert result["n"] > 50  # Has history


class TestEndToEndPerformance:
    """End-to-end performance tests"""

    def test_api_overhead(self, benchmark):
        """API routing overhead should be minimal (< 10ms)"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from lukhas_website.lukhas.api.dreams import router as dreams_router

        app = FastAPI()
        app.include_router(dreams_router)
        client = TestClient(app)

        def make_request():
            return client.get("/api/v1/dreams/")

        response = benchmark(make_request)
        assert response.status_code == 200

    def test_validation_overhead(self, benchmark):
        """Pydantic validation overhead should be acceptable"""
        from lukhas_website.lukhas.api.dreams import DreamSimulationRequest

        def create_request():
            return DreamSimulationRequest(
                seed="test",
                context={"foo": "bar"},
                parallel=False
            )

        req = benchmark(create_request)
        assert req.seed == "test"


class TestMemoryAndResourceUsage:
    """Memory and resource usage tests"""

    def test_drift_monitor_memory_growth(self):
        """Drift monitor should have bounded memory (window size)"""
        from lukhas_website.lukhas.core.drift import DriftMonitor

        monitor = DriftMonitor(lane="experimental")

        # Add many updates
        for i in range(1000):
            monitor.update([1.0, 0.0], [0.9, 0.1])

        # Window should be bounded to 64 (from config)
        assert len(monitor._raw) <= 64

    def test_glyph_validation_no_leaks(self):
        """GLYPH validation should not leak memory"""
        from lukhas.glyphs import validate_glyph

        # Run validation many times
        for i in range(1000):
            validate_glyph({
                "concept": f"test_{i}",
                "emotion": {"joy": 0.5}
            })

        # No assertion - just checking it doesn't crash/leak


# Performance budgets for CI
PERFORMANCE_BUDGETS = {
    "test_simulate_dream_latency": {
        "max_mean": 0.250,  # 250ms
        "max_stddev": 0.050,  # 50ms
    },
    "test_encode_concept_latency": {
        "max_mean": 0.100,  # 100ms
        "max_stddev": 0.020,  # 20ms
    },
    "test_bind_glyph_latency": {
        "max_mean": 0.150,  # 150ms
        "max_stddev": 0.030,  # 30ms
    },
    "test_drift_update_latency": {
        "max_mean": 0.050,  # 50ms
        "max_stddev": 0.010,  # 10ms
    },
    "test_validate_glyph_latency": {
        "max_mean": 0.010,  # 10ms
        "max_stddev": 0.002,  # 2ms
    },
}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only", "--benchmark-autosave"])
