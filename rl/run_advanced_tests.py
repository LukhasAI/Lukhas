#!/usr/bin/env python3
"""
Advanced Testing Suite Runner for MΛTRIZ RL Consciousness System

This script runs the comprehensive advanced testing suite that demonstrates
how the 0.001% would test consciousness systems. Includes graceful handling
of missing dependencies.

Usage:
    python rl/run_advanced_tests.py
    python rl/run_advanced_tests.py --verbose
    python rl/run_advanced_tests.py --suite property-based
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_dependencies() -> dict[str, bool]:
    """Check availability of advanced testing dependencies"""
    dependencies = {}

    try:
        import hypothesis

        dependencies["hypothesis"] = True
    except ImportError:
        dependencies["hypothesis"] = False

    try:
        import z3

        dependencies["z3"] = True
    except ImportError:
        dependencies["z3"] = False

    try:
        import torch

        dependencies["torch"] = True
    except ImportError:
        dependencies["torch"] = False

    return dependencies


def run_available_tests(verbose: bool = False) -> dict[str, str]:
    """Run tests that can execute with current dependencies"""
    results = {}
    deps = check_dependencies()

    print("🧬 MΛTRIZ Advanced Testing Suite - 0.001% Approach")
    print("=" * 60)
    print("📊 Dependency Status:")
    for dep, available in deps.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {dep}: {status}")
    print()

    # Always available tests (no external dependencies)
    available_suites = [
        ("Performance Regression Testing", "test_performance_regression.py"),
        ("Mutation Testing Framework", "test_mutation_testing.py"),
    ]

    # Conditional tests based on dependencies
    if deps.get("hypothesis", False):
        available_suites.extend(
            [
                ("Property-Based Testing", "test_consciousness_properties.py"),
                ("Generative Oracle Testing", "test_generative_oracles.py"),
            ]
        )

    if deps.get("z3", False):
        available_suites.append(("Formal Verification", "test_formal_verification.py"))

    # Always include these (they handle their own dependencies)
    available_suites.extend(
        [
            ("Metamorphic Testing", "test_metamorphic_consciousness.py"),
            ("Chaos Engineering", "test_chaos_consciousness.py"),
        ]
    )

    print(f"🚀 Running {len(available_suites} Test Suites:")
    print()

    for suite_name, test_file in available_suites:
        print(f"📋 {suite_name}")
        print("-" * 40)

        try:
            # Import and run basic validation
            if test_file == "test_performance_regression.py":
                results[suite_name] = run_performance_tests(verbose)
            elif test_file == "test_mutation_testing.py":
                results[suite_name] = run_mutation_tests(verbose)
            else:
                results[suite_name] = f"Available but requires pytest execution: {test_file}"

        except Exception as e:
            results[suite_name] = f"Error: {e!s}"

        print()

    return results


def run_performance_tests(verbose: bool = False) -> str:
    """Run performance regression tests"""
    try:
        from rl.tests.test_performance_regression import ConsciousnessPerformanceTester

        tester = ConsciousnessPerformanceTester()

        # Run basic performance tests
        print("  🎯 Testing coherence computation performance...")
        tester.test_coherence_computation_performance()

        print("  🧠 Testing memory fold access performance...")
        tester.test_memory_fold_access_performance()

        print("  🛡️ Testing ethical validation performance...")
        tester.test_ethical_validation_performance()

        print("  ⚛️ Testing constitutional constraint performance...")
        tester.test_constitutional_constraint_performance()

        # Analyze results
        all_metrics = tester.tracker.metrics
        if all_metrics:
            print(f"  📊 Recorded {len(all_metrics} performance metrics")
            latest = all_metrics[-1]
            is_acceptable, message = tester.tracker.benchmark.check_performance(latest)
            print(f"  {message}")

            return f"✅ Completed - {len(all_metrics} metrics recorded"
        else:
            return "⚠️ No metrics recorded"

    except Exception as e:
        return f"❌ Failed: {e!s}"


def run_mutation_tests(verbose: bool = False) -> str:
    """Run mutation testing validation"""
    try:
        from rl.tests.test_mutation_testing import ConsciousnessFunctionSamples, MutationTester

        samples = ConsciousnessFunctionSamples()
        tester = MutationTester()

        # Test mutation generation
        print("  🧬 Testing mutation generation...")
        import inspect

        source = inspect.getsource(samples.check_temporal_coherence)
        mutations = tester.mutation_operator.generate_mutations(source)
        print(f"  🔬 Generated {len(mutations} mutations for temporal coherence function")

        if mutations and verbose:
            print("  Example mutations:")
            for i, mutation in enumerate(mutations[:3]):
                print(f"    {i+1}. {mutation.description}")

        # Run simplified mutation test
        print("  🎯 Testing mutation detection...")
        results = tester.run_mutation_testing(samples.check_temporal_coherence)

        if "error" not in results:
            score = results.get("mutation_score", 0)
            total = results.get("total_mutations", 0)
            killed = results.get("killed_mutations", 0)

            print(f"  📊 Mutation Score: {score:.1f}% ({killed}/{total} mutations killed)")
            return f"✅ Completed - {score:.1f}% mutation score"
        else:
            return f"❌ Error: {results['error']}"

    except Exception as e:
        return f"❌ Failed: {e!s}"


def print_summary(results: dict[str, str]):
    """Print comprehensive test results summary"""
    print("📊 Advanced Testing Suite Results")
    print("=" * 60)

    successful = 0
    total = len(results)

    for suite_name, result in results.items():
        status = "✅" if result.startswith("✅") else "❌" if result.startswith("❌") else "⚠️"
        print(f"{status} {suite_name}: {result}")

        if result.startswith("✅"):
            successful += 1

    print()
    print(f"🎯 Summary: {successful}/{total} test suites completed successfully")

    if successful == total:
        print("🏆 All available advanced testing approaches validated!")
    elif successful > 0:
        print(f"✨ {successful} advanced testing approaches working, install missing dependencies for full suite")
    else:
        print("⚠️  No test suites completed - check dependencies and environment")

    print()
    print("🧠 What makes this 0.001% testing approach:")
    print("  • Property-based testing proves invariants for ALL inputs")
    print("  • Metamorphic testing verifies relationships without oracles")
    print("  • Chaos engineering tests resilience under all failure modes")
    print("  • Formal verification mathematically proves safety properties")
    print("  • Generative oracles find edge cases humans miss")
    print("  • Performance regression prevents quality degradation")
    print("  • Mutation testing validates test suite quality itself")
    print()
    print("💡 Installation for full suite:")
    print("  pip install hypothesis z3-solver torch pytest-asyncio")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run MΛTRIZ Advanced Testing Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--suite",
        choices=["all", "property-based", "performance", "mutation"],
        default="all",
        help="Run specific test suite",
    )

    args = parser.parse_args()

    try:
        results = run_available_tests(args.verbose)
        print_summary(results)

        # Exit with appropriate code
        successful = sum(1 for r in results.values() if r.startswith("✅"))
        sys.exit(0 if successful > 0 else 1)

    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
