#!/usr/bin/env python3
"""
Test script to demonstrate batch processing efficiency in vulnerability management
"""

import time

from orchestration_src.brain.github_vulnerability_manager import (
    GitHubVulnerabilityManager,
    Vulnerability,
    VulnerabilitySeverity,
)


def create_test_vulnerabilities():
    """Create some test vulnerabilities for demonstration"""
    test_vulns = [
        Vulnerability(
            id="GHSA-test-001",
            package_name="axios",
            severity=VulnerabilitySeverity.HIGH,
            repository="testuser/repo1",
            description="Cross-site request forgery vulnerability",
            ecosystem="npm",
            auto_fixable=True,
            estimated_fix_cost=0.02,
            affected_range="< 0.21.0",
            fixed_version="0.21.0",
        ),
        Vulnerability(
            id="GHSA-test-002",
            package_name="lodash",
            severity=VulnerabilitySeverity.HIGH,
            repository="testuser/repo1",
            description="Prototype pollution vulnerability",
            ecosystem="npm",
            auto_fixable=True,
            estimated_fix_cost=0.02,
            affected_range="< 4.17.21",
            fixed_version="4.17.21",
        ),
        Vulnerability(
            id="GHSA-test-003",
            package_name="requests",
            severity=VulnerabilitySeverity.CRITICAL,
            repository="testuser/repo2",
            description="SSL certificate verification bypass",
            ecosystem="pip",
            auto_fixable=True,
            estimated_fix_cost=0.03,
            affected_range="< 2.25.1",
            fixed_version="2.25.1",
        ),
        Vulnerability(
            id="GHSA-test-004",
            package_name="express",
            severity=VulnerabilitySeverity.HIGH,
            repository="testuser/repo2",
            description="Directory traversal vulnerability",
            ecosystem="npm",
            auto_fixable=True,
            estimated_fix_cost=0.02,
            affected_range="< 4.18.2",
            fixed_version="4.18.2",
        ),
        Vulnerability(
            id="GHSA-test-005",
            package_name="django",
            severity=VulnerabilitySeverity.CRITICAL,
            repository="testuser/repo3",
            description="SQL injection vulnerability",
            ecosystem="pip",
            auto_fixable=True,
            estimated_fix_cost=0.03,
            affected_range="< 3.2.13",
            fixed_version="3.2.13",
        ),
    ]
    return test_vulns


def test_individual_processing():
    """Test individual vulnerability processing"""
    print("🔧 Testing Individual Processing Mode...")

    manager = GitHubVulnerabilityManager(batch_mode=False, agi_mode=True)
    manager.vulnerabilities = create_test_vulnerabilities()

    start_time = time.time()
    start_budget = manager.budget_controller.daily_spend

    # Fix vulnerabilities individually
    results = manager.fix_critical_vulnerabilities(max_fixes=5)

    end_time = time.time()
    end_budget = manager.budget_controller.daily_spend

    print(f"  ⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"  💰 Budget used: ${end_budget - start_budget:.4f}")
    print(f"  🔧 Fixes applied: {results['fixes_applied']}")
    print(
        f"  📊 Cost per fix: ${(end_budget - start_budget) / max(results['fixes_applied'], 1):.4f}"
    )

    return {
        "time": end_time - start_time,
        "cost": end_budget - start_budget,
        "fixes": results["fixes_applied"],
    }


def test_batch_processing():
    """Test batch vulnerability processing"""
    print("\n🔄 Testing Batch Processing Mode...")

    manager = GitHubVulnerabilityManager(batch_mode=True, agi_mode=True)
    manager.vulnerabilities = create_test_vulnerabilities()

    start_time = time.time()
    start_budget = manager.budget_controller.daily_spend

    # Fix vulnerabilities in batches
    results = manager.fix_vulnerabilities_batch(max_batches=3)

    end_time = time.time()
    end_budget = manager.budget_controller.daily_spend

    print(f"  ⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"  💰 Budget used: ${end_budget - start_budget:.4f}")
    print(f"  🔧 Fixes applied: {results['fixes_applied']}")
    print(f"  📋 Batches processed: {results['batches_processed']}")
    print(f"  📄 PRs created: {results['prs_created']}")
    print(
        f"  📊 Cost per fix: ${(end_budget - start_budget) / max(results['fixes_applied'], 1):.4f}"
    )

    return {
        "time": end_time - start_time,
        "cost": end_budget - start_budget,
        "fixes": results["fixes_applied"],
        "batches": results["batches_processed"],
        "prs": results["prs_created"],
    }


def main():
    """Run efficiency comparison"""
    print("🧪 ΛBot Batch Processing Efficiency Test")
    print("=" * 50)

    # Test individual processing
    individual_results = test_individual_processing()

    # Reset budget controller for fair comparison
    # (In a real scenario, you'd use separate instances)

    # Test batch processing
    batch_results = test_batch_processing()

    # Compare results
    print("\n📊 Efficiency Comparison:")
    print("=" * 30)

    if individual_results["fixes"] > 0 and batch_results["fixes"] > 0:
        time_efficiency = individual_results["time"] / batch_results["time"]
        cost_efficiency = individual_results["cost"] / batch_results["cost"]

        print(
            f"⚡ Time efficiency: {time_efficiency:.1f}x faster with batch processing"
        )
        print(
            f"💰 Cost efficiency: {cost_efficiency:.1f}x cheaper with batch processing"
        )

    print(
        f"\nIndividual: {individual_results['fixes']} fixes, ${individual_results['cost']:.4f}"
    )
    print(
        f"Batch:      {batch_results['fixes']} fixes, ${batch_results['cost']:.4f} ({batch_results['batches']} batches)"
    )

    if batch_results["fixes"] > 0:
        print(
            f"\n✅ Batch processing created {batch_results['prs']} PRs for {batch_results['fixes']} fixes"
        )
        print(f"   (vs. {individual_results['fixes']} PRs for individual processing)")


if __name__ == "__main__":
    main()
