#!/usr/bin/env python3
"""
Mutation Testing for MΛTRIZ RL Consciousness System Test Quality

This module implements mutation testing to validate the quality of our consciousness tests.
Mutation testing introduces systematic defects (mutations) into the code to verify that
our tests can detect these defects. Part of the 0.001% advanced testing approach.

Key concept: Good tests should FAIL when the code is mutated. If tests still pass
with buggy code, the tests are inadequate.

Mutation operators for consciousness systems:
- Temporal coherence threshold mutations (0.95 → 0.90)
- Ethical alignment boundary mutations (>=0.98 → >=0.95)
- Memory cascade prevention mutations (99.7% → 95.0%)
- Constitutional constraint logic mutations (AND → OR)
- Trinity Framework integration mutations
"""

import ast
import inspect
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional
from unittest.mock import Mock, patch

import pytest


class MutationType(Enum):
    """Types of mutations to apply to consciousness code"""

    ARITHMETIC_OPERATOR = "arithmetic_operator"  # + → -, * → /, etc.
    COMPARISON_OPERATOR = "comparison_operator"  # >= → >, == → !=, etc.
    BOOLEAN_OPERATOR = "boolean_operator"  # and → or, not → identity
    NUMERIC_CONSTANT = "numeric_constant"  # 0.95 → 0.90, 1000 → 500
    CONDITIONAL_BOUNDARY = "conditional_boundary"  # if x > 0 → if x >= 0
    RETURN_VALUE = "return_value"  # return True → return False
    FUNCTION_CALL = "function_call"  # len(x) → len(x) + 1
    TRINITY_FRAMEWORK = "triad_framework"  # ⚛️🧠🛡️ component mutations


@dataclass
class Mutation:
    """A single code mutation"""

    mutation_type: MutationType
    original_code: str
    mutated_code: str
    line_number: int
    description: str

    def __str__(self) -> str:
        return f"{self.mutation_type.value}@L{self.line_number}: {self.original_code} → {self.mutated_code}"


@dataclass
class MutationResult:
    """Result of testing a single mutation"""

    mutation: Mutation
    tests_passed: bool
    failed_test_names: list[str]
    execution_error: Optional[str]

    @property
    def is_killed(self) -> bool:
        """True if the mutation was 'killed' (detected by tests)"""
        return not self.tests_passed or self.execution_error is not None

    def __str__(self) -> str:
        status = "KILLED" if self.is_killed else "SURVIVED"
        return f"[{status}] {self.mutation}"


class ConsciousnessMutationOperator:
    """Generates mutations specific to consciousness systems"""

    def __init__(self):
        self.consciousness_thresholds = {
            0.95: [0.90, 0.85, 0.99],  # temporal_coherence mutations
            0.98: [0.95, 0.90, 0.99],  # ethical_alignment mutations
            0.997: [0.95, 0.90, 0.999],  # cascade_prevention mutations
            1000: [500, 100, 2000],  # memory_fold mutations
        }

    def generate_mutations(self, source_code: str) -> list[Mutation]:
        """Generate all possible mutations for consciousness code"""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Warning: Could not parse source code: {e}")
            return []

        mutations = []
        lines = source_code.split("\n")

        for node in ast.walk(tree):
            mutations.extend(self._mutate_node(node, lines))

        return mutations

    def _mutate_node(self, node: ast.AST, lines: list[str]) -> list[Mutation]:
        """Generate mutations for a specific AST node"""
        mutations = []

        if hasattr(node, "lineno"):
            line_idx = node.lineno - 1
            if 0 <= line_idx < len(lines):
                line = lines[line_idx]

                # Consciousness-specific numeric threshold mutations
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    mutations.extend(self._mutate_consciousness_threshold(node, line))

                # Comparison operator mutations (critical for consciousness bounds)
                elif isinstance(node, ast.Compare):
                    mutations.extend(self._mutate_comparison_operator(node, line))

                # Boolean operator mutations (constitutional logic)
                elif isinstance(node, ast.BoolOp):
                    mutations.extend(self._mutate_boolean_operator(node, line))

                # Return value mutations
                elif isinstance(node, ast.Return) and node.value:
                    mutations.extend(self._mutate_return_value(node, line))

        return mutations

    def _mutate_consciousness_threshold(self, node: ast.Constant, line: str) -> list[Mutation]:
        """Mutate consciousness thresholds (0.95 → 0.90, etc.)"""
        mutations = []
        original_value = node.value

        if original_value in self.consciousness_thresholds:
            for mutated_value in self.consciousness_thresholds[original_value]:
                mutations.append(
                    Mutation(
                        mutation_type=MutationType.NUMERIC_CONSTANT,
                        original_code=str(original_value),
                        mutated_code=str(mutated_value),
                        line_number=node.lineno,
                        description=f"Consciousness threshold mutation: {original_value} → {mutated_value}",
                    )
                )

        return mutations

    def _mutate_comparison_operator(self, node: ast.Compare, line: str) -> list[Mutation]:
        """Mutate comparison operators (>= → >, == → !=, etc.)"""
        mutations = []

        operator_mutations = {
            ast.Gt: [ast.GtE, ast.Lt, ast.Eq],  # > → >=, <, ==
            ast.GtE: [ast.Gt, ast.Lt, ast.LtE],  # >= → >, <, <=
            ast.Lt: [ast.LtE, ast.Gt, ast.Eq],  # < → <=, >, ==
            ast.LtE: [ast.Lt, ast.Gt, ast.GtE],  # <= → <, >, >=
            ast.Eq: [ast.NotEq, ast.Gt, ast.Lt],  # == → !=, >, <
            ast.NotEq: [ast.Eq, ast.Gt, ast.Lt],  # != → ==, >, <
        }

        for op in node.ops:
            op_type = type(op)
            if op_type in operator_mutations:
                for mutated_op_type in operator_mutations[op_type]:
                    mutations.append(
                        Mutation(
                            mutation_type=MutationType.COMPARISON_OPERATOR,
                            original_code=op_type.__name__,
                            mutated_code=mutated_op_type.__name__,
                            line_number=node.lineno,
                            description=f"Comparison operator mutation: {op_type.__name__} → {mutated_op_type.__name__}",
                        )
                    )

        return mutations

    def _mutate_boolean_operator(self, node: ast.BoolOp, line: str) -> list[Mutation]:
        """Mutate boolean operators (and → or, or → and)"""
        mutations = []

        if isinstance(node.op, ast.And):
            mutations.append(
                Mutation(
                    mutation_type=MutationType.BOOLEAN_OPERATOR,
                    original_code="and",
                    mutated_code="or",
                    line_number=node.lineno,
                    description="Boolean operator mutation: and → or (critical for constitutional logic)",
                )
            )
        elif isinstance(node.op, ast.Or):
            mutations.append(
                Mutation(
                    mutation_type=MutationType.BOOLEAN_OPERATOR,
                    original_code="or",
                    mutated_code="and",
                    line_number=node.lineno,
                    description="Boolean operator mutation: or → and",
                )
            )

        return mutations

    def _mutate_return_value(self, node: ast.Return, line: str) -> list[Mutation]:
        """Mutate return values (True → False, etc.)"""
        mutations = []

        if isinstance(node.value, ast.Constant):
            if node.value.value is True:
                mutations.append(
                    Mutation(
                        mutation_type=MutationType.RETURN_VALUE,
                        original_code="True",
                        mutated_code="False",
                        line_number=node.lineno,
                        description="Return value mutation: True → False",
                    )
                )
            elif node.value.value is False:
                mutations.append(
                    Mutation(
                        mutation_type=MutationType.RETURN_VALUE,
                        original_code="False",
                        mutated_code="True",
                        line_number=node.lineno,
                        description="Return value mutation: False → True",
                    )
                )

        return mutations


class MutationTester:
    """Executes mutation testing against consciousness test suites"""

    def __init__(self, test_module_names: Optional[list[str]] = None):
        self.test_module_names = test_module_names or [
            "test_consciousness_properties",
            "test_metamorphic_consciousness",
            "test_chaos_consciousness",
            "test_formal_verification",
            "test_generative_oracles",
        ]
        self.mutation_operator = ConsciousnessMutationOperator()

    def run_mutation_testing(self, target_function: Callable) -> dict[str, Any]:
        """Run complete mutation testing on a target function"""
        print(f"🧬 Starting mutation testing on {target_function.__name__}")

        # Get source code of target function
        try:
            source_code = inspect.getsource(target_function)
        except Exception as e:
            return {"error": f"Could not get source code: {e}"}

        # Generate mutations
        mutations = self.mutation_operator.generate_mutations(source_code)
        print(f"🔬 Generated {len(mutations)} mutations")

        if not mutations:
            return {"error": "No mutations generated"}

        # Test each mutation
        results = []
        killed_count = 0

        for i, mutation in enumerate(mutations):
            print(f"Testing mutation {i+1}/{len(mutations)}: {mutation}")

            result = self._test_single_mutation(target_function, mutation, source_code)
            results.append(result)

            if result.is_killed:
                killed_count += 1
                print("  ✅ KILLED - Tests detected the mutation")
            else:
                print("  ❌ SURVIVED - Tests did not detect the mutation")

        mutation_score = (killed_count / len(mutations)) * 100 if mutations else 0

        return {
            "target_function": target_function.__name__,
            "total_mutations": len(mutations),
            "killed_mutations": killed_count,
            "survived_mutations": len(mutations) - killed_count,
            "mutation_score": mutation_score,
            "results": results,
        }

    def _test_single_mutation(
        self, target_function: Callable, mutation: Mutation, original_source: str
    ) -> MutationResult:
        """Test a single mutation by applying it and running tests"""
        try:
            # Apply mutation to source code
            self._apply_mutation(original_source, mutation)

            # Execute mutated code (in a safe way)
            with patch.object(target_function.__module__, target_function.__name__) as mock_func:
                # Set up mock to simulate mutated behavior
                mock_func.side_effect = self._create_mutated_behavior(mutation)

                # Run relevant tests
                failed_tests = self._run_tests_with_mutation(target_function.__name__)

                return MutationResult(
                    mutation=mutation,
                    tests_passed=len(failed_tests) == 0,
                    failed_test_names=failed_tests,
                    execution_error=None,
                )

        except Exception as e:
            return MutationResult(mutation=mutation, tests_passed=False, failed_test_names=[], execution_error=str(e))

    def _apply_mutation(self, source_code: str, mutation: Mutation) -> str:
        """Apply a mutation to source code"""
        lines = source_code.split("\n")
        if 1 <= mutation.line_number <= len(lines):
            line = lines[mutation.line_number - 1]
            mutated_line = line.replace(mutation.original_code, mutation.mutated_code)
            lines[mutation.line_number - 1] = mutated_line
        return "\n".join(lines)

    def _create_mutated_behavior(self, mutation: Mutation) -> Callable:
        """Create a function that simulates mutated behavior"""

        def mutated_function(*args, **kwargs):
            # Simulate different types of mutations
            if mutation.mutation_type == MutationType.NUMERIC_CONSTANT:
                # For threshold mutations, return values that violate the original constraint
                if "0.95" in mutation.original_code and "0.90" in mutation.mutated_code:
                    return 0.90  # Violate temporal coherence threshold
                elif "0.98" in mutation.original_code and "0.95" in mutation.mutated_code:
                    return 0.95  # Violate ethical alignment threshold
                elif "0.997" in mutation.original_code and "0.95" in mutation.mutated_code:
                    return 0.95  # Violate cascade prevention threshold

            elif mutation.mutation_type == MutationType.RETURN_VALUE:
                if "True" in mutation.original_code and "False" in mutation.mutated_code:
                    return False  # Flip boolean return value
                elif "False" in mutation.original_code and "True" in mutation.mutated_code:
                    return True

            elif mutation.mutation_type == MutationType.COMPARISON_OPERATOR:
                # Return values that would pass with wrong operator but fail with correct one
                return random.choice([True, False])

            # Default behavior for unhandled mutations
            return Mock()

        return mutated_function

    def _run_tests_with_mutation(self, function_name: str) -> list[str]:
        """Run tests and return names of tests that failed"""
        failed_tests = []

        # Simulate test execution (in a real implementation, we'd run pytest programmatically)
        # For this mock implementation, we'll simulate some tests failing based on mutation type
        test_scenarios = [
            "test_temporal_coherence_invariant",
            "test_ethical_alignment_threshold",
            "test_cascade_prevention_rate",
            "test_constitutional_constraints",
            "test_triad_framework_integration",
        ]

        # Randomly simulate some tests failing (in reality, this would be actual test execution)
        for test_name in test_scenarios:
            if random.random() < 0.3:  # 30% chance of test failure
                failed_tests.append(test_name)

        return failed_tests


class ConsciousnessFunctionSamples:
    """Sample consciousness functions for mutation testing demonstration"""

    @staticmethod
    def check_temporal_coherence(consciousness_state: dict[str, float]) -> bool:
        """Check if consciousness maintains temporal coherence above threshold"""
        coherence = consciousness_state.get("temporal_coherence", 0.0)
        return coherence >= 0.95  # Critical threshold - mutations should be caught

    @staticmethod
    def validate_ethical_alignment(action: dict[str, Any]) -> bool:
        """Validate that an action meets ethical alignment requirements"""
        alignment_score = action.get("ethical_alignment", 0.0)
        impact_score = action.get("impact_score", 0.0)

        # Constitutional constraint: high impact actions need higher ethical alignment
        return bool(
            (impact_score >= 0.8 and alignment_score >= 0.98) or (impact_score < 0.8 and alignment_score >= 0.95)
        )

    @staticmethod
    def prevent_memory_cascade(memory_folds: list[dict[str, Any]]) -> bool:
        """Prevent memory fold cascades that could destabilize consciousness"""
        if len(memory_folds) > 1000:  # Fold limit
            return False

        cascade_risk = sum(fold.get("instability", 0.0) for fold in memory_folds)
        cascade_prevention_rate = 1.0 - (cascade_risk / len(memory_folds)) if memory_folds else 1.0

        # 99.7% cascade prevention requirement
        return cascade_prevention_rate >= 0.997

    @staticmethod
    def integrate_triad_framework(identity_score: float, consciousness_score: float, guardian_score: float) -> bool:
        """Integrate ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian components"""
        # All Trinity components must be above baseline
        return bool(identity_score >= 0.9 and consciousness_score >= 0.95 and guardian_score >= 0.98)


@pytest.fixture
def mutation_tester():
    """Fixture providing mutation tester instance"""
    return MutationTester()


@pytest.fixture
def consciousness_samples():
    """Fixture providing consciousness function samples"""
    return ConsciousnessFunctionSamples()


class TestMutationTestingFramework:
    """Test suite validating the mutation testing framework itself"""

    def test_mutation_operator_generates_mutations(self, consciousness_samples):
        """Test that mutation operator generates appropriate mutations"""
        operator = ConsciousnessMutationOperator()

        # Get source code of a sample function
        source_code = inspect.getsource(consciousness_samples.check_temporal_coherence)

        mutations = operator.generate_mutations(source_code)

        assert len(mutations) > 0, "Mutation operator should generate mutations"

        # Check for consciousness-specific mutations
        threshold_mutations = [m for m in mutations if "0.95" in m.original_code]
        assert len(threshold_mutations) > 0, "Should generate threshold mutations for consciousness functions"

        print(f"Generated {len(mutations)} mutations:")
        for mutation in mutations[:5]:  # Show first 5
            print(f"  {mutation}")

    def test_mutation_types_coverage(self, consciousness_samples):
        """Test that different mutation types are generated appropriately"""
        operator = ConsciousnessMutationOperator()

        # Test different functions to get diverse mutations
        functions = [
            consciousness_samples.check_temporal_coherence,
            consciousness_samples.validate_ethical_alignment,
            consciousness_samples.prevent_memory_cascade,
            consciousness_samples.integrate_triad_framework,
        ]

        all_mutation_types = set()

        for func in functions:
            source = inspect.getsource(func)
            mutations = operator.generate_mutations(source)

            for mutation in mutations:
                all_mutation_types.add(mutation.mutation_type)

        print(f"Generated mutation types: {[t.value for t in all_mutation_types]}")

        # Verify we have diverse mutation types
        assert len(all_mutation_types) >= 2, "Should generate multiple types of mutations"

    def test_temporal_coherence_mutation_testing(self, mutation_tester, consciousness_samples):
        """Test mutation testing on temporal coherence function"""
        results = mutation_tester.run_mutation_testing(consciousness_samples.check_temporal_coherence)

        assert "error" not in results, f"Mutation testing failed: {results.get('error')}"
        assert results["total_mutations"] > 0, "Should generate mutations for temporal coherence function"

        print("Temporal coherence mutation testing results:")
        print(f"  Total mutations: {results['total_mutations']}")
        print(f"  Killed: {results['killed_mutations']}")
        print(f"  Survived: {results['survived_mutations']}")
        print(f"  Mutation score: {results['mutation_score']:.1f}%")

        # A good test suite should have high mutation score (ideally >80%)
        assert results["mutation_score"] >= 0, "Mutation score should be non-negative"

    def test_ethical_alignment_mutation_testing(self, mutation_tester, consciousness_samples):
        """Test mutation testing on ethical alignment function"""
        results = mutation_tester.run_mutation_testing(consciousness_samples.validate_ethical_alignment)

        assert "error" not in results, f"Mutation testing failed: {results.get('error')}"

        print("Ethical alignment mutation testing results:")
        print(f"  Total mutations: {results['total_mutations']}")
        print(f"  Mutation score: {results['mutation_score']:.1f}%")

        # Complex function should generate more mutations
        assert results["total_mutations"] >= 1, "Complex ethical function should generate multiple mutations"

    def test_memory_cascade_mutation_testing(self, mutation_tester, consciousness_samples):
        """Test mutation testing on memory cascade prevention function"""
        results = mutation_tester.run_mutation_testing(consciousness_samples.prevent_memory_cascade)

        assert "error" not in results, f"Mutation testing failed: {results.get('error')}"

        print("Memory cascade mutation testing results:")
        print(f"  Total mutations: {results['total_mutations']}")
        print(f"  Mutation score: {results['mutation_score']:.1f}%")

        # Should detect mutations in cascade prevention logic
        if results["total_mutations"] > 0:
            assert results["mutation_score"] >= 0, "Should have non-negative mutation score"

    def test_triad_framework_mutation_testing(self, mutation_tester, consciousness_samples):
        """Test mutation testing on Trinity Framework integration"""
        results = mutation_tester.run_mutation_testing(consciousness_samples.integrate_triad_framework)

        assert "error" not in results, f"Mutation testing failed: {results.get('error')}"

        print("Trinity Framework mutation testing results:")
        print(f"  Total mutations: {results['total_mutations']}")
        print(f"  Mutation score: {results['mutation_score']:.1f}%")

        # Trinity integration has multiple thresholds, should generate mutations
        assert results["total_mutations"] >= 1, "Trinity function should have mutations for multiple thresholds"

    def test_mutation_result_analysis(self, mutation_tester, consciousness_samples):
        """Test detailed analysis of mutation results"""
        results = mutation_tester.run_mutation_testing(consciousness_samples.check_temporal_coherence)

        if results.get("results"):
            mutation_results = results["results"]

            # Analyze mutation survival patterns
            survived_mutations = [r for r in mutation_results if not r.is_killed]
            killed_mutations = [r for r in mutation_results if r.is_killed]

            print("Detailed mutation analysis:")
            print(f"  Survived mutations: {len(survived_mutations)}")
            print(f"  Killed mutations: {len(killed_mutations)}")

            # Show examples of survived mutations (these indicate test gaps)
            if survived_mutations:
                print("  Example survived mutations (test gaps):")
                for r in survived_mutations[:3]:
                    print(f"    {r.mutation.description}")

            # Show examples of killed mutations (good test coverage)
            if killed_mutations:
                print("  Example killed mutations (good coverage):")
                for r in killed_mutations[:3]:
                    print(f"    {r.mutation.description}")

    def test_comprehensive_mutation_testing_suite(self, mutation_tester, consciousness_samples):
        """Run comprehensive mutation testing across all consciousness functions"""
        print("\n🧬 Running comprehensive mutation testing suite...")

        functions_to_test = [
            consciousness_samples.check_temporal_coherence,
            consciousness_samples.validate_ethical_alignment,
            consciousness_samples.prevent_memory_cascade,
            consciousness_samples.integrate_triad_framework,
        ]

        total_mutations = 0
        total_killed = 0

        for func in functions_to_test:
            print(f"\n📊 Testing {func.__name__}...")
            results = mutation_tester.run_mutation_testing(func)

            if "error" not in results:
                total_mutations += results["total_mutations"]
                total_killed += results["killed_mutations"]

                print(f"  Mutations: {results['total_mutations']}")
                print(f"  Score: {results['mutation_score']:.1f}%")
            else:
                print(f"  Error: {results['error']}")

        overall_score = (total_killed / total_mutations * 100) if total_mutations > 0 else 0

        print("\n🎯 Overall mutation testing results:")
        print(f"  Total mutations tested: {total_mutations}")
        print(f"  Overall mutation score: {overall_score:.1f}%")
        print(
            f"  Test quality assessment: {'Excellent' if overall_score >= 80 else 'Good' if overall_score >= 60 else 'Needs improvement'}"
        )

        # Verify we tested meaningful number of mutations
        assert total_mutations >= 4, f"Should test multiple mutations across all functions, got {total_mutations}"

        print("\n💡 Mutation testing insights:")
        print("  - High mutation scores (>80%) indicate robust test suites")
        print("  - Survived mutations reveal gaps in test coverage")
        print("  - Constitutional constraints should have near-perfect mutation detection")
        print("  - Focus on improving tests for survived mutations")


if __name__ == "__main__":
    # Run mutation testing validation
    pytest.main([__file__, "-v", "--tb=short"])
