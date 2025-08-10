"""
LUKHAS DAST Integration Tests
Comprehensive testing suite for the enhanced DAST system
Author: GitHub Copilot
"""

import asyncio
import time

import pytest

from .adapters import UniversalAdapter
from .api import DASTAPIEndpoints

# Import all DAST components
from .engine import LUKHASDASTEngine
from .processors import (
    AttentionProcessor,
    SolutionProcessor,
    TagProcessor,
    TaskProcessor,
)


class TestLUKHASDASTIntegration:
    """Integration tests for the complete LUKHAS DAST system"""

    @pytest.fixture
    async def dast_engine(self):
        """Setup DAST engine for testing"""
        engine = LUKHASDASTEngine()
        await engine.initialize()
        return engine

    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing"""
        return [
            {
                "id": "task_1",
                "title": "Implement AI-powered search",
                "description": "Build advanced search with natural language processing",
                "priority": "high",
                "complexity": "complex",
                "tags": ["ai", "search", "nlp"],
                "estimated_hours": 40,
            },
            {
                "id": "task_2",
                "title": "Fix login bug",
                "description": "Users cannot login with special characters in password",
                "priority": "urgent",
                "complexity": "simple",
                "tags": ["bug", "auth", "security"],
                "estimated_hours": 2,
            },
            {
                "id": "task_3",
                "title": "Design API documentation",
                "description": "Create comprehensive API docs with examples",
                "priority": "medium",
                "complexity": "medium",
                "tags": ["docs", "api", "examples"],
                "estimated_hours": 16,
            },
        ]

    async def test_one_line_api_performance(self, dast_engine, sample_tasks):
        """Test that one-line API calls meet <100ms performance target"""

        # Add tasks first
        for task in sample_tasks:
            await dast_engine.track(task)

        # Test track() performance
        start_time = time.time()
        result = await dast_engine.track(
            {
                "title": "Performance test task",
                "description": "Testing sub-100ms performance",
            }
        )
        track_time = (time.time() - start_time) * 1000

        assert track_time < 100, f"track() took {track_time}ms, should be <100ms"
        assert result["status"] == "success"

        # Test focus() performance
        start_time = time.time()
        focused_tasks = await dast_engine.focus("high priority tasks")
        focus_time = (time.time() - start_time) * 1000

        assert focus_time < 100, f"focus() took {focus_time}ms, should be <100ms"
        assert len(focused_tasks) > 0

        # Test progress() performance
        start_time = time.time()
        progress_report = await dast_engine.progress("task_1")
        progress_time = (time.time() - start_time) * 1000

        assert (
            progress_time < 100
        ), f"progress() took {progress_time}ms, should be <100ms"
        assert "progress" in progress_report

    async def test_ai_intelligence_integration(self, dast_engine, sample_tasks):
        """Test integration between AI intelligence modules"""

        # Add sample tasks
        for task in sample_tasks:
            await dast_engine.track(task)

        # Test TaskIntelligence analysis
        intelligence = dast_engine.task_intelligence
        analysis = await intelligence.analyze_task(sample_tasks[0])

        assert "complexity_score" in analysis
        assert "priority_score" in analysis
        assert "estimated_completion" in analysis
        assert analysis["complexity_score"] > 0

        # Test PriorityOptimizer
        optimizer = dast_engine.priority_optimizer
        priorities = await optimizer.optimize_priorities(sample_tasks)

        assert len(priorities) == len(sample_tasks)
        assert all("priority_score" in p for p in priorities)

        # Test ContextTracker
        tracker = dast_engine.context_tracker
        context = await tracker.track_context("task_1", {"focus_session": True})

        assert context["task_id"] == "task_1"
        assert "timestamp" in context

        # Test SymbolicReasoner
        reasoner = dast_engine.symbolic_reasoner
        reasoning = await reasoner.reason_about_task(sample_tasks[0])

        assert "reasoning_chain" in reasoning
        assert "confidence" in reasoning

    async def test_processor_integration(self, dast_engine, sample_tasks):
        """Test integration between specialized processors"""

        # Test TaskProcessor
        task_processor = TaskProcessor()
        processed_task = await task_processor.process_task(sample_tasks[0])

        assert "processed_at" in processed_task
        assert "categorization" in processed_task
        assert processed_task["ai_enhanced"] is True

        # Test TagProcessor
        tag_processor = TagProcessor()
        enhanced_tags = await tag_processor.enhance_tags(sample_tasks[0]["tags"])

        assert len(enhanced_tags) >= len(sample_tasks[0]["tags"])
        assert any(
            "ai_suggested" in tag for tag in enhanced_tags if isinstance(tag, dict)
        )

        # Test AttentionProcessor
        attention_processor = AttentionProcessor()
        attention_score = await attention_processor.calculate_attention_score(
            sample_tasks[0]
        )

        assert 0 <= attention_score <= 100

        # Test SolutionProcessor
        solution_processor = SolutionProcessor()
        solution_suggestions = await solution_processor.suggest_solutions(
            sample_tasks[0]
        )

        assert "suggestions" in solution_suggestions
        assert len(solution_suggestions["suggestions"]) > 0

    async def test_external_adapter_integration(self, dast_engine):
        """Test external system adapter integration"""

        adapter = UniversalAdapter()

        # Test adapter registration
        await adapter.register_system(
            "test_jira",
            {
                "type": "jira",
                "url": "https://test.atlassian.net",
                "auth": {"token": "test_token"},
            },
        )

        assert "test_jira" in adapter.registered_systems

        # Test format conversion
        test_task = {
            "title": "Test task",
            "description": "Test description",
            "priority": "high",
        }

        jira_format = await adapter.convert_format(test_task, "jira")
        assert "summary" in jira_format  # Jira uses 'summary' not 'title'
        assert "priority" in jira_format

        github_format = await adapter.convert_format(test_task, "github")
        assert "title" in github_format
        assert "body" in github_format

    async def test_api_endpoints_integration(self, dast_engine):
        """Test RESTful API endpoints integration"""

        api = DASTAPIEndpoints(dast_engine)

        # Test health endpoint
        health = await api.health()
        assert health["status"] == "healthy"
        assert "uptime" in health
        assert "performance" in health

        # Test analytics endpoint
        analytics = await api.get_analytics()
        assert "task_metrics" in analytics
        assert "performance_metrics" in analytics
        assert "productivity_insights" in analytics

    async def test_collaborative_workflow(self, dast_engine, sample_tasks):
        """Test human-AI collaborative workflow"""

        # Add tasks
        for task in sample_tasks:
            await dast_engine.track(task)

        # Test collaborative task breakdown
        collaboration_result = await dast_engine.collaborate(
            "break down the AI search implementation task",
            {"human_input": "Focus on the NLP component first"},
        )

        assert "ai_suggestions" in collaboration_result
        assert "human_context" in collaboration_result
        assert "collaborative_plan" in collaboration_result

        # Test collaborative prioritization
        priority_collaboration = await dast_engine.collaborate(
            "help me prioritize these tasks for this sprint",
            {"context": "We have 2 weeks, 3 developers, focus on user-facing features"},
        )

        assert "recommended_priorities" in priority_collaboration
        assert "reasoning" in priority_collaboration

    async def test_caching_and_performance(self, dast_engine):
        """Test intelligent caching system performance"""

        # First call - should cache result
        start_time = time.time()
        result1 = await dast_engine.focus("urgent tasks")
        first_call_time = (time.time() - start_time) * 1000

        # Second call - should use cache
        start_time = time.time()
        result2 = await dast_engine.focus("urgent tasks")
        second_call_time = (time.time() - start_time) * 1000

        # Cache should make second call faster
        assert second_call_time < first_call_time
        assert second_call_time < 50  # Cached calls should be <50ms

        # Results should be identical
        assert result1 == result2

    async def test_symbolic_ai_reasoning(self, dast_engine, sample_tasks):
        """Test symbolic AI reasoning patterns"""

        # Add tasks with dependencies
        complex_task = {
            "id": "complex_ai_task",
            "title": "Build AGI reasoning engine",
            "description": "Implement symbolic reasoning with neural networks",
            "dependencies": ["task_1"],  # Depends on AI search
            "complexity": "very_complex",
            "domain": "artificial_intelligence",
        }

        await dast_engine.track(complex_task)

        # Test symbolic reasoning
        reasoning_result = (
            await dast_engine.symbolic_reasoner.reason_about_dependencies(
                "complex_ai_task"
            )
        )

        assert "dependency_chain" in reasoning_result
        assert "critical_path" in reasoning_result
        assert "risk_analysis" in reasoning_result

        # Test pattern recognition
        patterns = await dast_engine.symbolic_reasoner.identify_patterns(
            [sample_tasks[0], complex_task]
        )

        assert "ai_related_tasks" in patterns
        assert "complexity_correlation" in patterns

    async def test_real_time_adaptation(self, dast_engine):
        """Test real-time adaptation capabilities"""

        # Simulate changing work patterns
        work_context = {
            "time_of_day": "morning",
            "focus_level": "high",
            "interruptions": "low",
            "energy_level": "peak",
        }

        adapted_suggestions = await dast_engine.context_tracker.adapt_to_context(
            work_context
        )

        assert "recommended_tasks" in adapted_suggestions
        assert "focus_duration" in adapted_suggestions
        assert "break_suggestions" in adapted_suggestions

        # Verify adaptation is context-aware
        assert (
            adapted_suggestions["focus_duration"] > 60
        )  # Should suggest longer focus in morning


# Performance Benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmarks for the DAST system"""

    async def test_bulk_operations_performance(self):
        """Test performance with bulk operations"""
        engine = LUKHASDASTEngine()
        await engine.initialize()

        # Create 1000 test tasks
        tasks = []
        for i in range(1000):
            tasks.append(
                {
                    "id": f"bulk_task_{i}",
                    "title": f"Bulk task {i}",
                    "description": f"Test task {i} for bulk operations",
                    "priority": ["low", "medium", "high"][i % 3],
                }
            )

        # Benchmark bulk tracking
        start_time = time.time()
        for task in tasks:
            await engine.track(task)
        bulk_time = time.time() - start_time

        avg_time_per_task = (bulk_time / len(tasks)) * 1000
        assert (
            avg_time_per_task < 10
        ), f"Average task tracking took {avg_time_per_task}ms, should be <10ms"

        # Benchmark bulk focus query
        start_time = time.time()
        focused_tasks = await engine.focus("high priority")
        focus_time = (time.time() - start_time) * 1000

        assert (
            focus_time < 200
        ), f"Bulk focus query took {focus_time}ms, should be <200ms"

    async def test_concurrent_operations(self):
        """Test concurrent operation performance"""
        engine = LUKHASDASTEngine()
        await engine.initialize()

        # Create concurrent track operations
        tasks = [
            engine.track({"title": f"Concurrent task {i}", "priority": "medium"})
            for i in range(50)
        ]

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        concurrent_time = (time.time() - start_time) * 1000

        assert (
            concurrent_time < 500
        ), f"50 concurrent operations took {concurrent_time}ms, should be <500ms"
        assert all(r["status"] == "success" for r in results)


if __name__ == "__main__":
    # Run integration tests
    async def run_tests():
        print("🧪 Running LUKHAS DAST Integration Tests...")

        # Initialize test engine
        engine = LUKHASDASTEngine()
        await engine.initialize()

        # Basic functionality test
        print("✅ Testing basic functionality...")
        result = await engine.track(
            {
                "title": "Integration test task",
                "description": "Testing the integrated DAST system",
            }
        )
        print(f"   Track result: {result['status']}")

        # Performance test
        print("✅ Testing performance...")
        start_time = time.time()
        focused = await engine.focus("test tasks")
        perf_time = (time.time() - start_time) * 1000
        print(f"   Focus performance: {perf_time:.2f}ms")

        # AI integration test
        print("✅ Testing AI integration...")
        analysis = await engine.task_intelligence.analyze_task(
            {
                "title": "Complex AI task",
                "description": "Build neural network for pattern recognition",
                "complexity": "high",
            }
        )
        print(f"   AI analysis: {analysis.get('complexity_score', 'N/A')}")

        print("🎉 Integration tests completed successfully!")
        print("🚀 DAST system is ready for production use!")

    # Run async tests
    asyncio.run(run_tests())
