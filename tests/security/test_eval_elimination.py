"""
Comprehensive Security Tests for eval() Elimination

This module tests the SafeEvaluator to ensure it:
1. Blocks all code injection attempts
2. Prevents breakout attacks
3. Handles legitimate expressions correctly
4. Provides clear error messages
"""

import pytest
import math
from lukhas.security import (
    SafeEvaluator,
    safe_evaluate_expression,
    SecurityError,
    EvaluationError,
)


class TestCodeInjectionPrevention:
    """Test that the safe evaluator blocks code injection attempts."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_blocks_import_statements(self, evaluator):
        """Test that import statements are blocked."""
        malicious_inputs = [
            "__import__('os')",
            "__import__('os').system('ls')",
            "import os",
            "from os import system",
        ]

        for malicious in malicious_inputs:
            with pytest.raises((SecurityError, SyntaxError)):
                evaluator.evaluate(malicious, {})

    def test_blocks_exec_and_eval(self, evaluator):
        """Test that exec() and eval() calls are blocked."""
        malicious_inputs = [
            "exec('print(1)')",
            "eval('1+1')",
            "compile('1+1', '', 'eval')",
        ]

        for malicious in malicious_inputs:
            with pytest.raises(SecurityError):
                evaluator.evaluate(malicious, {})

    def test_blocks_class_attribute_breakout(self, evaluator):
        """Test that class attribute breakout attempts are blocked."""
        malicious_inputs = [
            "().__class__",
            "[].__class__.__bases__[0]",
            "().__class__.__bases__[0].__subclasses__()",
            "[].__class__.__base__.__subclasses__()",
            "().__class__.__bases__[0].__subclasses__()[104].__init__.__globals__['sys']",
        ]

        for malicious in malicious_inputs:
            with pytest.raises(SecurityError):
                evaluator.evaluate(malicious, {})

    def test_blocks_lambda_functions(self, evaluator):
        """Test that lambda functions are blocked."""
        malicious_inputs = [
            "lambda x: x + 1",
            "(lambda: __import__('os'))())",
        ]

        for malicious in malicious_inputs:
            with pytest.raises(SecurityError):
                evaluator.evaluate(malicious, {})

    def test_blocks_list_comprehensions(self, evaluator):
        """Test that comprehensions are blocked (could hide malicious code)."""
        malicious_inputs = [
            "[x for x in range(10)]",
            "{x: x for x in range(10)}",
            "{x for x in range(10)}",
        ]

        for malicious in malicious_inputs:
            with pytest.raises(SecurityError):
                evaluator.evaluate(malicious, {})

    def test_blocks_function_definitions(self, evaluator):
        """Test that function definitions are blocked."""
        malicious_inputs = [
            "def foo(): pass",
            "async def foo(): pass",
        ]

        for malicious in malicious_inputs:
            with pytest.raises((SecurityError, SyntaxError)):
                evaluator.evaluate(malicious, {})

    def test_blocks_class_definitions(self, evaluator):
        """Test that class definitions are blocked."""
        with pytest.raises((SecurityError, SyntaxError)):
            evaluator.evaluate("class Foo: pass", {})


class TestLegitimateExpressions:
    """Test that legitimate expressions work correctly."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_arithmetic_operations(self, evaluator):
        """Test basic arithmetic operations."""
        test_cases = [
            ("2 + 2", {}, 4),
            ("10 - 3", {}, 7),
            ("5 * 6", {}, 30),
            ("20 / 4", {}, 5.0),
            ("17 // 5", {}, 3),
            ("17 % 5", {}, 2),
            ("2 ** 3", {}, 8),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}: got {result}, expected {expected}"

    def test_comparison_operations(self, evaluator):
        """Test comparison operations."""
        test_cases = [
            ("5 > 3", {}, True),
            ("5 < 3", {}, False),
            ("5 >= 5", {}, True),
            ("5 <= 4", {}, False),
            ("5 == 5", {}, True),
            ("5 != 3", {}, True),
            ("5 is 5", {}, True),
            ("5 is not 3", {}, True),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_boolean_operations(self, evaluator):
        """Test boolean logic operations."""
        test_cases = [
            ("True and True", {}, True),
            ("True and False", {}, False),
            ("True or False", {}, True),
            ("False or False", {}, False),
            ("not True", {}, False),
            ("not False", {}, True),
            ("True and (False or True)", {}, True),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_variable_access(self, evaluator):
        """Test access to variables in context."""
        context = {"x": 10, "y": 20, "name": "Alice"}

        test_cases = [
            ("x + y", 30),
            ("x * 2", 20),
            ("y - x", 10),
            ("name == 'Alice'", True),
            ("x > 5 and y < 30", True),
        ]

        for expr, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_safe_builtin_functions(self, evaluator):
        """Test safe built-in functions."""
        test_cases = [
            ("abs(-5)", {}, 5),
            ("min(1, 2, 3)", {}, 1),
            ("max(1, 2, 3)", {}, 3),
            ("len([1, 2, 3])", {}, 3),
            ("int('42')", {}, 42),
            ("float('3.14')", {}, 3.14),
            ("str(123)", {}, "123"),
            ("bool(1)", {}, True),
            ("round(3.7)", {}, 4),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_math_functions(self, evaluator):
        """Test math functions."""
        test_cases = [
            ("sqrt(16)", {}, 4.0),
            ("ceil(3.2)", {}, 4),
            ("floor(3.8)", {}, 3),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_in_operator(self, evaluator):
        """Test 'in' and 'not in' operators."""
        context = {"items": [1, 2, 3], "text": "hello"}

        test_cases = [
            ("2 in items", True),
            ("5 in items", False),
            ("5 not in items", True),
            ("'ell' in text", True),
        ]

        for expr, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_literal_collections(self, evaluator):
        """Test literal collections."""
        test_cases = [
            ("[1, 2, 3]", {}, [1, 2, 3]),
            ("(1, 2, 3)", {}, (1, 2, 3)),
            ("{'a': 1, 'b': 2}", {}, {'a': 1, 'b': 2}),
            ("{1, 2, 3}", {}, {1, 2, 3}),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"

    def test_ternary_expression(self, evaluator):
        """Test ternary if-else expressions."""
        test_cases = [
            ("10 if True else 20", {}, 10),
            ("10 if False else 20", {}, 20),
            ("'yes' if 5 > 3 else 'no'", {}, 'yes'),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected, f"Failed for {expr}"


class TestAttributeAccess:
    """Test attribute access with proper security controls."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_blocks_attribute_access_by_default(self, evaluator):
        """Test that attribute access is blocked by default."""
        from dataclasses import dataclass

        @dataclass
        class Person:
            name: str
            age: int

        person = Person("Alice", 30)
        context = {"person": person}

        with pytest.raises(SecurityError):
            evaluator.evaluate("person.name", context)

    def test_allows_whitelisted_attributes(self, evaluator):
        """Test that whitelisted attributes can be accessed."""
        from dataclasses import dataclass

        @dataclass
        class Person:
            name: str
            age: int

        person = Person("Alice", 30)
        context = {"person": person}

        result = evaluator.evaluate(
            "person.name",
            context,
            allow_attribute_access=True,
            allowed_attributes={"name", "age"}
        )
        assert result == "Alice"

    def test_blocks_non_whitelisted_attributes(self, evaluator):
        """Test that non-whitelisted attributes are blocked."""
        from dataclasses import dataclass

        @dataclass
        class Person:
            name: str
            age: int

        person = Person("Alice", 30)
        context = {"person": person}

        with pytest.raises(SecurityError):
            evaluator.evaluate(
                "person.name",
                context,
                allow_attribute_access=True,
                allowed_attributes={"age"}  # name not in allowed list
            )

    def test_blocks_private_attributes(self, evaluator):
        """Test that private attributes are always blocked."""
        class MyClass:
            def __init__(self):
                self._private = "secret"
                self.__very_private = "very secret"

        obj = MyClass()
        context = {"obj": obj}

        with pytest.raises(SecurityError):
            evaluator.evaluate(
                "obj._private",
                context,
                allow_attribute_access=True,
                allowed_attributes={"_private"}
            )

    def test_blocks_dangerous_attributes(self, evaluator):
        """Test that dangerous attributes are blocked."""
        dangerous_attrs = [
            "__class__", "__bases__", "__subclasses__", "__globals__",
            "__builtins__", "__import__", "__code__", "__dict__"
        ]

        obj = object()
        context = {"obj": obj}

        for attr in dangerous_attrs:
            with pytest.raises(SecurityError):
                evaluator.evaluate(
                    f"obj.{attr}",
                    context,
                    allow_attribute_access=True,
                    allowed_attributes={attr}
                )


class TestConvenienceFunction:
    """Test the safe_evaluate_expression convenience function."""

    def test_basic_usage(self):
        """Test basic usage of convenience function."""
        result = safe_evaluate_expression("2 + 2", {})
        assert result == 4

    def test_with_context(self):
        """Test with variable context."""
        result = safe_evaluate_expression("x * 2", {"x": 10})
        assert result == 20

    def test_security_check(self):
        """Test that security checks still apply."""
        with pytest.raises(SecurityError):
            safe_evaluate_expression("__import__('os')", {})


class TestPolicyEngineExpressions:
    """Test expressions typical in policy engines."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_simple_condition_logic(self, evaluator):
        """Test simple condition logic like in policy engine."""
        # Simulating condition logic from policy_engine.py
        # where C0, C1, etc. are replaced with True/False
        test_cases = [
            ("True and True", {}, True),
            ("True or False", {}, True),
            ("True and False or True", {}, True),
            ("not False", {}, True),
        ]

        for expr, context, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert result == expected

    def test_complex_policy_conditions(self, evaluator):
        """Test complex policy conditions."""
        from dataclasses import dataclass

        @dataclass
        class Request:
            requester: str
            status: str
            denial_count: int

        request = Request("user1", "pending", 3)
        context = {
            "request": request,
            "requester_denial_count": 3,
        }

        # Test with attribute access enabled
        result = evaluator.evaluate(
            "requester_denial_count > 2",
            context,
            allow_attribute_access=True,
            allowed_attributes={"requester", "status", "denial_count"}
        )
        assert result == True


class TestSignalModulation:
    """Test expressions typical in signal modulation."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_modulation_expressions(self, evaluator):
        """Test modulation expressions like those in signals.py"""
        # Typical expressions: "0.7 - (level * 0.4)"
        context = {
            "level": 0.5,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "ceil": math.ceil,
            "floor": math.floor,
            "sqrt": math.sqrt,
        }

        test_cases = [
            ("0.7 - (level * 0.4)", 0.5),  # 0.7 - 0.2 = 0.5
            ("min(1.0, level * 2)", 1.0),  # min(1.0, 1.0) = 1.0
            ("max(0.0, level - 0.3)", 0.2),  # max(0.0, 0.2) = 0.2
        ]

        for expr, expected in test_cases:
            result = evaluator.evaluate(expr, context)
            assert abs(result - expected) < 0.0001, f"Failed for {expr}: got {result}, expected {expected}"


class TestErrorHandling:
    """Test error handling and messages."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_syntax_error_message(self, evaluator):
        """Test that syntax errors are reported clearly."""
        with pytest.raises(SyntaxError):
            evaluator.evaluate("2 +", {})

    def test_undefined_variable_error(self, evaluator):
        """Test error on undefined variable."""
        with pytest.raises(EvaluationError, match="Undefined variable"):
            evaluator.evaluate("undefined_var", {})

    def test_division_by_zero(self, evaluator):
        """Test division by zero handling."""
        with pytest.raises(EvaluationError):
            evaluator.evaluate("1 / 0", {})

    def test_type_error_in_operation(self, evaluator):
        """Test type errors in operations."""
        with pytest.raises(EvaluationError):
            evaluator.evaluate("'string' + 5", {})


class TestDepthLimiting:
    """Test that expression depth is limited to prevent DoS."""

    @pytest.fixture
    def evaluator(self):
        return SafeEvaluator()

    def test_deeply_nested_expression(self, evaluator):
        """Test that deeply nested expressions are rejected."""
        # Create a deeply nested expression
        expr = "1" + " + 1" * 100  # Should be fine
        result = evaluator.evaluate(expr, {})
        assert result == 101

    def test_extremely_deep_nesting(self, evaluator):
        """Test that extremely deep nesting is rejected."""
        # Create an extremely nested expression that would exceed limits
        expr = "(" * 60 + "1" + ")" * 60
        with pytest.raises(EvaluationError, match="too deeply nested"):
            evaluator.evaluate(expr, {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
