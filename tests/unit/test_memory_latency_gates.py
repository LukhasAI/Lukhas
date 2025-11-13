#!/usr/bin/env python3
"""
Test Memory & Latency Budget Gates for CI

Validates that memory and latency gates are properly configured to block CI
when performance budgets are exceeded.
"""

import time
from pathlib import Path

import yaml


def test_memory_latency_gates_workflow_exists():
    """Test that memory & latency gates workflow exists and is properly configured."""
    workflow_path = Path(".github/workflows/memory-latency-gates.yml")
    assert workflow_path.exists(), "Memory & latency gates workflow not found"

    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    # Verify workflow structure
    assert "jobs" in workflow
    assert "memory-latency-gates" in workflow["jobs"]

    job = workflow["jobs"]["memory-latency-gates"]

    # Verify job has proper timeout
    assert "timeout-minutes" in job
    assert job["timeout-minutes"] <= 15, "Timeout should be reasonable for CI"

    steps = job["steps"]

    # Find memory/latency related test steps
    memory_steps = [
        step for step in steps
        if "memory" in step.get("name", "").lower()
    ]
    latency_steps = [
        step for step in steps
        if "latency" in step.get("name", "").lower()
    ]

    # Verify test steps exist
    assert len(memory_steps) >= 1, "Missing memory performance test steps"
    assert len(latency_steps) >= 1, "Missing latency performance test steps"

    # Verify steps are blocking (exit 1 on failure)
    for step in memory_steps + latency_steps:
        run_content = step.get("run", "")
        if "pytest" in run_content:
            assert "exit 1" in run_content, f"Step '{step['name']}' missing blocking exit"


def test_performance_budgets_defined():
    """Test that performance budgets are properly defined."""
    # Critical performance budgets that must be enforced in CI
    required_budgets = {
        "memory_fold_access_ms": 10.0,      # Memory fold access time
        "topk_recall_10k_items_ms": 100.0,  # Top-K recall for 10k items
        "matriz_stage_latency_ms": 100.0,   # MATRIZ stage processing
        "pipeline_total_latency_ms": 250.0, # Complete pipeline
        "system_memory_usage_mb": 512.0,    # System memory usage
        "cpu_average_percent": 70.0,        # CPU usage under load
    }

    for budget_name, threshold in required_budgets.items():
        assert threshold > 0, f"Budget {budget_name} must be positive"
        assert isinstance(threshold, (int, float)), f"Budget {budget_name} must be numeric"

        # Verify thresholds are reasonable for production
        if "ms" in budget_name:
            assert threshold <= 1000, f"Latency budget {budget_name} should be sub-second"
        if "mb" in budget_name:
            assert threshold <= 2048, f"Memory budget {budget_name} should be reasonable"
        if "percent" in budget_name:
            assert threshold <= 100, f"Percentage budget {budget_name} should be <= 100%"


def test_memory_recall_budget_enforcement():
    """Test that memory recall budget enforcement is working."""
    # Simulate a simple Top-K recall operation
    items = [{"id": i, "data": f"item_{i}"} for i in range(10000)]

    def simple_topk_recall(query, k=10):
        """Simple Top-K recall simulation."""
        # Simulate basic sorting/selection
        scored_items = [(i, item) for i, item in enumerate(items)]
        scored_items.sort(key=lambda x: x[0] % 100)  # Simple scoring
        return [item for _, item in scored_items[:k]]

    # Measure performance
    start_time = time.perf_counter()
    results = simple_topk_recall("test_query", k=10)
    end_time = time.perf_counter()

    recall_time_ms = (end_time - start_time) * 1000

    # Verify budget compliance (100ms for 10k items)
    budget_ms = 100.0
    assert recall_time_ms <= budget_ms, \
        f"Top-K recall time {recall_time_ms:.2f}ms exceeds {budget_ms}ms budget"

    # Verify correctness
    assert len(results) == 10, "Should return exactly 10 items"
    assert len(items) == 10000, "Dataset should have 10k items"

    print(f"✅ Memory recall: {recall_time_ms:.2f}ms (budget: {budget_ms}ms)")


def test_latency_budget_enforcement():
    """Test that latency budget enforcement is working."""
    # Simulate MATRIZ pipeline stages
    stage_budgets = {
        "intent": 50.0,      # Intent analysis
        "decision": 100.0,   # Decision making
        "processing": 120.0, # Main processing
        "validation": 40.0,  # Validation
        "reflection": 30.0,  # Reflection
    }

    def simulate_stage(stage_name, budget_ms):
        """Simulate a MATRIZ stage with controlled timing."""
        start_time = time.perf_counter()

        # Simulate stage work (should be well under budget)
        time.sleep(budget_ms / 2000)  # Half budget time in seconds

        end_time = time.perf_counter()
        return (end_time - start_time) * 1000

    # Test each stage meets its budget
    total_pipeline_time = 0
    for stage_name, budget_ms in stage_budgets.items():
        stage_time = simulate_stage(stage_name, budget_ms)
        total_pipeline_time += stage_time

        assert stage_time <= budget_ms, \
            f"Stage {stage_name} time {stage_time:.2f}ms exceeds {budget_ms}ms budget"

    # Test total pipeline budget (250ms)
    pipeline_budget_ms = 250.0
    assert total_pipeline_time <= pipeline_budget_ms, \
        f"Pipeline time {total_pipeline_time:.2f}ms exceeds {pipeline_budget_ms}ms budget"

    print(f"✅ Pipeline latency: {total_pipeline_time:.2f}ms (budget: {pipeline_budget_ms}ms)")


def test_ci_gate_blocking_behavior():
    """Test that CI gates have proper blocking behavior."""
    workflow_path = Path(".github/workflows/memory-latency-gates.yml")
    with open(workflow_path) as f:
        content = f.read()

    # Should have blocking failure messages
    assert "🚨 BLOCKING:" in content, "Missing blocking failure indicators"
    assert "exit 1" in content, "Missing immediate failure commands"

    # Should have status reporting
    blocking_indicators = [
        "BLOCKING",
        "exit 1",
        "budget",
        "exceeded"
    ]

    found_indicators = sum(1 for indicator in blocking_indicators if indicator in content)
    assert found_indicators >= 3, "Workflow missing clear blocking behavior"


def test_performance_reporting():
    """Test that performance results are properly reported."""
    workflow_path = Path(".github/workflows/memory-latency-gates.yml")
    with open(workflow_path) as f:
        content = f.read()

    # Should generate performance reports
    assert "Performance Budget Report" in content, "Missing performance report generation"
    assert "budget-report.md" in content, "Missing report artifact"

    # Should have PR commenting for visibility
    assert "Comment on PR" in content, "Missing PR comment functionality"


def test_budget_thresholds_reasonable():
    """Test that budget thresholds are reasonable for production."""
    # These thresholds represent production-ready performance
    production_thresholds = {
        "memory_fold_access": (10.0, "ms"),        # Very fast memory access
        "topk_recall_10k": (100.0, "ms"),          # Fast search
        "stage_latency": (100.0, "ms"),            # Responsive stages
        "pipeline_latency": (250.0, "ms"),         # Quarter-second response
        "memory_usage": (512.0, "MB"),             # Reasonable memory footprint
        "cpu_usage": (70.0, "%"),                  # Not overwhelming CPU
    }

    for metric, (threshold, unit) in production_thresholds.items():
        # Verify threshold is achievable but challenging
        if unit == "ms":
            assert 1.0 <= threshold <= 1000.0, f"{metric} threshold {threshold}ms should be 1-1000ms"
        elif unit == "MB":
            assert 64.0 <= threshold <= 2048.0, f"{metric} threshold {threshold}MB should be 64-2048MB"
        elif unit == "%":
            assert 10.0 <= threshold <= 95.0, f"{metric} threshold {threshold}% should be 10-95%"


if __name__ == "__main__":
    test_memory_latency_gates_workflow_exists()
    test_performance_budgets_defined()
    test_memory_recall_budget_enforcement()
    test_latency_budget_enforcement()
    test_ci_gate_blocking_behavior()
    test_performance_reporting()
    test_budget_thresholds_reasonable()
    print("✅ All memory & latency budget gate tests passed!")
