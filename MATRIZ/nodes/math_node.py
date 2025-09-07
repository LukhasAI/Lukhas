#!/usr/bin/env python3
"""
MATRIZ Mathematical Computation Node

A production-ready cognitive node for mathematical expression evaluation that provides:
- Deterministic mathematical computation
- Comprehensive error handling
- Complete MATRIZ format node emission
- Confidence scoring based on complexity
- Full traceability and audit support

This node supports basic arithmetic operations: +, -, *, /, exponents (**), and parentheses.
All computations are performed deterministically - same input always produces same output.
"""
from typing import List
from typing import Dict
import streamlit as st

import ast
import math
import operator
import re
import time
from typing import Any, Optional, Union

from ..core.node_interface import (
    CognitiveNode,
    NodeState,
    NodeTrigger,
)


class MathNode(CognitiveNode):
    """
    Production-ready mathematical computation node for MATRIZ-AGI system.

    Features:
    - Deterministic evaluation of mathematical expressions
    - Support for +, -, *, /, **, parentheses
    - Confidence scoring based on expression complexity
    - Comprehensive error handling and validation
    - Complete MATRIZ format node emission
    - Full audit trail and traceability

    Security:
    - Uses AST parsing for safe expression evaluation
    - No arbitrary code execution
    - Input validation and sanitization
    """

    # Supported mathematical operations
    SUPPORTED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Mathematical constants
    MATH_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}

    def __init__(self, tenant: str = "default", precision: int = 10):
        """
        Initialize the mathematical computation node.

        Args:
            tenant: Tenant identifier for multi-tenancy
            precision: Decimal precision for calculations (default: 10)
        """
        super().__init__(
            node_name="matriz_math_node",
            capabilities=[
                "arithmetic_evaluation",
                "expression_parsing",
                "mathematical_computation",
                "deterministic_calculation",
                "confidence_assessment",
            ],
            tenant=tenant,
        )

        self.precision = precision
        self.complexity_weights = {
            "numbers": 0.1,
            "operators": 0.2,
            "parentheses": 0.3,
            "exponents": 0.4,
            "constants": 0.2,
        }

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process mathematical expressions deterministically.

        Args:
            input_data: Dict containing:
                - 'expression': Mathematical expression to evaluate
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing:
                - 'answer': The computation result or error message
                - 'confidence': Confidence score (0.0-1.0)
                - 'matriz_node': Complete MATRIZ format node
                - 'processing_time': Processing duration in seconds
        """
        start_time = time.time()

        # Extract and validate input
        expression = input_data.get("expression", "").strip()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        context = input_data.get("context", {})

        # Create initial trigger
        trigger = NodeTrigger(
            event_type="mathematical_computation_request",
            timestamp=int(time.time() * 1000),
            effect="expression_evaluation",
        )

        if not expression:
            return self._create_error_response(
                "No mathematical expression provided",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        # Validate and sanitize expression
        validation_result = self._validate_expression(expression)
        if not validation_result["valid"]:
            return self._create_error_response(
                f"Invalid expression: {validation_result['error']}",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        # Evaluate the expression
        try:
            result = self._evaluate_expression(expression)
            complexity_score = self._calculate_complexity(expression)
            confidence = self._calculate_confidence(expression, result, complexity_score)

            # Create success state
            state = NodeState(
                confidence=confidence,
                salience=min(0.9, 0.5 + complexity_score * 0.4),  # Higher complexity = higher salience
                valence=0.8,  # Positive - successful computation
                utility=0.9,  # High utility for mathematical results
                novelty=max(0.1, complexity_score),  # Novelty based on complexity
                arousal=min(0.7, 0.3 + complexity_score * 0.4),  # Arousal based on complexity
            )

            # Create affirmation reflection
            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause="Successfully evaluated mathematical expression",
                new_state={
                    "expression": expression,
                    "result": result,
                    "confidence": confidence,
                    "complexity_score": complexity_score,
                },
            )

            # Create MATRIZ node for successful computation
            matriz_node = self.create_matriz_node(
                node_type="COMPUTATION",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "expression": expression,
                    "result": result,
                    "result_type": type(result).__name__,
                    "complexity_score": complexity_score,
                    "evaluation_method": "ast_safe_eval",
                    "precision": self.precision,
                    "context": context,
                    "deterministic_hash": self.get_deterministic_hash(
                        {"expression": expression, "precision": self.precision}
                    ),
                },
            )

            answer = f"The result is {self._format_result(result)}"

        except Exception as e:
            return self._create_error_response(
                f"Evaluation error: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
                expression=expression,
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the mathematical computation output.

        Validates:
        1. Required fields presence and types
        2. MATRIZ node schema compliance
        3. Mathematical result validity
        4. Confidence-result consistency
        5. Processing metadata completeness

        Args:
            output: Output from process() method

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            required_fields = ["answer", "confidence", "matriz_node", "processing_time"]
            for field in required_fields:
                if field not in output:
                    return False

            # Validate field types
            if not isinstance(output["answer"], str):
                return False
            if not isinstance(output["confidence"], (int, float)):
                return False
            if not isinstance(output["processing_time"], (int, float)):
                return False

            # Validate confidence range
            confidence = output["confidence"]
            if not (0 <= confidence <= 1):
                return False

            # Validate MATRIZ node
            matriz_node = output["matriz_node"]
            if not self.validate_matriz_node(matriz_node):
                return False

            # Check node type is COMPUTATION
            if matriz_node.get("type") != "COMPUTATION":
                return False

            # Validate mathematical computation specific fields
            state = matriz_node.get("state", {})

            # Check for expression in state
            if "expression" not in state:
                return False

            # Validate result consistency
            result = state.get("result")
            if result is not None:
                # If we have a numeric result, confidence should be reasonable
                if isinstance(result, (int, float)) and confidence < 0.3:
                    return False

                # Result should be a valid number or error indicator
                if not isinstance(result, (int, float, str)):
                    return False

            # Check complexity score if present
            complexity_score = state.get("complexity_score")
            if complexity_score is not None:
                if not isinstance(complexity_score, (int, float)):
                    return False
                if not (0 <= complexity_score <= 1):
                    return False

            # Validate provenance
            provenance = matriz_node.get("provenance", {})
            return not (
                "producer" not in provenance or "mathematical_computation" not in provenance.get("capabilities", [])
            )

        except Exception:
            return False

    def _validate_expression(self, expression: str) -> dict[str, Any]:
        """
        Validate mathematical expression for safety and correctness.

        Args:
            expression: Mathematical expression to validate

        Returns:
            Dict with 'valid' boolean and 'error' message if invalid
        """
        try:
            # Check length limits
            if len(expression) > 1000:
                return {
                    "valid": False,
                    "error": "Expression too long (max 1000 characters)",
                }

            # Check for empty expression
            if not expression.strip():
                return {"valid": False, "error": "Empty expression"}

            # Replace constants with placeholder values for parsing
            test_expr = expression.lower()
            for const in self.MATH_CONSTANTS:
                test_expr = test_expr.replace(const, "1")

            # Check for allowed characters only
            allowed_pattern = r"^[0-9+\-*/().\s**eE]+$"
            if not re.match(allowed_pattern, test_expr):
                return {
                    "valid": False,
                    "error": "Expression contains invalid characters",
                }

            # Check for balanced parentheses
            if test_expr.count("(") != test_expr.count(")"):
                return {"valid": False, "error": "Unbalanced parentheses"}

            # Try to parse with AST
            try:
                parsed = ast.parse(test_expr, mode="eval")
                self._validate_ast_node(parsed.body)
            except (SyntaxError, ValueError) as e:
                return {"valid": False, "error": f"Syntax error: {e!s}"}

            return {"valid": True, "error": None}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e!s}"}

    def _validate_ast_node(self, node: ast.AST) -> None:
        """
        Recursively validate AST node for security.

        Args:
            node: AST node to validate

        Raises:
            ValueError: If node contains unsafe operations
        """
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError(f"Invalid constant type: {type(node.value)}")
        elif isinstance(node, ast.Name):
            if node.id not in self.MATH_CONSTANTS:
                raise ValueError(f"Unknown identifier: {node.id}")
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.SUPPORTED_OPERATORS:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            self._validate_ast_node(node.left)
            self._validate_ast_node(node.right)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.SUPPORTED_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
            self._validate_ast_node(node.operand)
        else:
            raise ValueError(f"Unsupported AST node type: {type(node)}")

    def _evaluate_expression(self, expression: str) -> Union[float, int]:
        """
        Safely evaluate mathematical expression using AST.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            Numerical result of the computation

        Raises:
            ValueError: If evaluation fails
            ZeroDivisionError: If division by zero occurs
        """
        try:
            # Replace constants
            expr_with_constants = expression.lower()
            for const_name, const_value in self.MATH_CONSTANTS.items():
                expr_with_constants = expr_with_constants.replace(const_name, str(const_value))

            # Parse and evaluate
            parsed = ast.parse(expr_with_constants, mode="eval")
            result = self._eval_ast_node(parsed.body)

            # Handle special float values
            if math.isnan(result):
                raise ValueError("Result is not a number (NaN)")
            if math.isinf(result):
                raise ValueError("Result is infinite")

            # Round to specified precision
            if isinstance(result, float):
                result = round(result, self.precision)

            # Convert to int if it's a whole number
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            return result

        except ZeroDivisionError:
            raise ZeroDivisionError("Division by zero")
        except Exception as e:
            raise ValueError(f"Evaluation failed: {e!s}")

    def _eval_ast_node(self, node: ast.AST) -> Union[float, int]:
        """
        Recursively evaluate AST node.

        Args:
            node: AST node to evaluate

        Returns:
            Numerical result
        """
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return self.MATH_CONSTANTS[node.id]
        elif isinstance(node, ast.BinOp):
            left = self._eval_ast_node(node.left)
            right = self._eval_ast_node(node.right)
            op_func = self.SUPPORTED_OPERATORS[type(node.op)]
            return op_func(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_ast_node(node.operand)
            op_func = self.SUPPORTED_OPERATORS[type(node.op)]
            return op_func(operand)
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")

    def _calculate_complexity(self, expression: str) -> float:
        """
        Calculate complexity score for mathematical expression.

        Args:
            expression: Mathematical expression

        Returns:
            Complexity score between 0.0 and 1.0
        """
        try:
            expr_lower = expression.lower()

            # Count different components
            numbers = len(re.findall(r"\d+(?:\.\d+)?", expression))
            operators = len(re.findall(r"[+\-*/]", expression))
            parentheses = expression.count("(") + expression.count(")")
            exponents = expression.count("**")
            constants = sum(1 for const in self.MATH_CONSTANTS if const in expr_lower)

            # Calculate weighted complexity
            complexity = (
                min(numbers * self.complexity_weights["numbers"], 0.3)
                + min(operators * self.complexity_weights["operators"], 0.4)
                + min(parentheses * self.complexity_weights["parentheses"], 0.3)
                + min(exponents * self.complexity_weights["exponents"], 0.4)
                + min(constants * self.complexity_weights["constants"], 0.2)
            )

            return min(complexity, 1.0)

        except Exception:
            return 0.5  # Default complexity if calculation fails

    def _calculate_confidence(self, expression: str, result: Union[float, int], complexity: float) -> float:
        """
        Calculate confidence score based on expression and result.

        Args:
            expression: Original mathematical expression
            result: Computed result
            complexity: Complexity score of expression

        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            base_confidence = 0.95  # High base confidence for mathematical operations

            # Reduce confidence based on complexity
            complexity_penalty = complexity * 0.15

            # Reduce confidence for very large or very small results
            if isinstance(result, (int, float)):
                if abs(result) > 1e10 or (abs(result) < 1e-10 and result != 0):
                    complexity_penalty += 0.1

            # Reduce confidence for expressions with many operations
            operation_count = len(re.findall(r"[+\-*/()]", expression))
            if operation_count > 10:
                complexity_penalty += 0.1

            final_confidence = max(0.1, base_confidence - complexity_penalty)
            return min(1.0, final_confidence)

        except Exception:
            return 0.5  # Default confidence if calculation fails

    def _format_result(self, result: Union[float, int]) -> str:
        """
        Format numerical result for display.

        Args:
            result: Numerical result to format

        Returns:
            Formatted string representation
        """
        if isinstance(result, int):
            return str(result)
        elif isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            else:
                # Format with appropriate precision
                formatted = f"{result:.{self.precision}f}".rstrip("0").rstrip(".")
                return formatted if formatted else "0"
        else:
            return str(result)

    def _create_error_response(
        self,
        error_message: str,
        input_data: dict[str, Any],
        trace_id: str,
        start_time: float,
        triggers: list[NodeTrigger],
        expression: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create standardized error response with MATRIZ node.

        Args:
            error_message: Error description
            input_data: Original input data
            trace_id: Execution trace ID
            start_time: Processing start time
            triggers: List of triggers that led to this error
            expression: Mathematical expression if available

        Returns:
            Standardized error response dict
        """
        confidence = 0.1

        state = NodeState(
            confidence=confidence,
            salience=0.3,
            valence=-0.6,  # Negative - failed to compute
            risk=0.8,  # High risk due to error
            utility=0.1,  # Low utility - no result provided
        )

        # Create regret reflection
        reflection = self.create_reflection(
            reflection_type="regret",
            cause=f"Mathematical computation failed: {error_message}",
            old_state={"expression": expression} if expression else None,
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="COMPUTATION",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "expression": expression,
                "error": error_message,
                "result": None,
                "evaluation_method": "failed",
                "context": input_data.get("context", {}),
            },
        )

        processing_time = time.time() - start_time

        return {
            "answer": f"Error: {error_message}",
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }


# Example usage and testing
if __name__ == "__main__":
    # Create the math node
    math_node = MathNode(precision=6)

    # Comprehensive test cases
    test_cases = [
        # Basic arithmetic
        {"expression": "2 + 2", "expected_type": "success"},
        {"expression": "15 * 3", "expected_type": "success"},
        {"expression": "100 / 4", "expected_type": "success"},
        {"expression": "10 - 3", "expected_type": "success"},
        # Parentheses and order of operations
        {"expression": "(10 + 5) * 2", "expected_type": "success"},
        {"expression": "2 * (3 + 4)", "expected_type": "success"},
        {"expression": "((2 + 3) * 4) / 5", "expected_type": "success"},
        # Exponents
        {"expression": "2 ** 3", "expected_type": "success"},
        {"expression": "10 ** 2", "expected_type": "success"},
        {"expression": "2 ** (3 + 1)", "expected_type": "success"},
        # Mathematical constants
        {"expression": "pi * 2", "expected_type": "success"},
        {"expression": "e ** 1", "expected_type": "success"},
        # Decimal numbers
        {"expression": "3.14 + 2.86", "expected_type": "success"},
        {"expression": "10.5 / 2.5", "expected_type": "success"},
        # Negative numbers
        {"expression": "-5 + 3", "expected_type": "success"},
        {"expression": "10 + (-3)", "expected_type": "success"},
        # Complex expressions
        {"expression": "((2 + 3) * 4 - 1) / (2 ** 2)", "expected_type": "success"},
        # Error cases
        {"expression": "1 / 0", "expected_type": "error"},
        {"expression": "", "expected_type": "error"},
        {"expression": "2 +", "expected_type": "error"},
        {"expression": "((2 + 3)", "expected_type": "error"},
        {"expression": "2 + unknown_var", "expected_type": "error"},
        {"expression": "import os", "expected_type": "error"},
    ]

    print("MATRIZ Mathematical Computation Node Test")
    print("=" * 50)

    success_count = 0
    total_tests = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        expression = test_case["expression"]
        expected_type = test_case["expected_type"]

        print(f"\nTest {i:2d}: {expression}")
        print("-" * 30)

        try:
            # Process the expression
            result = math_node.process({"expression": expression, "context": {"test_case": i})

            # Validate output
            is_valid = math_node.validate_output(result)

            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Processing time: {result['processing_time']:.6f}s")
            print(f"Output valid: {is_valid}")

            # Check if result matches expected type
            is_error = result["answer"].startswith("Error:")
            actual_type = "error" if is_error else "success"
            type_matches = actual_type == expected_type

            print(f"Expected: {expected_type}, Got: {actual_type}, Match: {type_matches}")

            # Show MATRIZ node details
            matriz_node = result["matriz_node"]
            print(f"MATRIZ Node ID: {matriz_node['id'][:8]}...")
            print(f"Node Type: {matriz_node['type']}")

            state = matriz_node["state"]
            print(f"State: conf={state['confidence']:.3f}, sal={state['salience']:.3f}")

            if "result" in state and state["result"] is not None:
                print(f"Result: {state['result']} ({state.get('result_type', 'unknown')})")

            if "complexity_score" in state:
                print(f"Complexity: {state['complexity_score']:.3f}")

            # Check reflections
            if matriz_node["reflections"]:
                reflection = matriz_node["reflections"][0]
                print(f"Reflection: {reflection['reflection_type']} - {reflection['cause'][:50]}...")

            if is_valid and type_matches:
                success_count += 1
                print("✓ PASS")
            else:
                print("✗ FAIL")

        except Exception as e:
            print(f"✗ EXCEPTION: {e!s}")

    print("\n" + "=" * 50)
    print(f"Test Results: {success_count}/{total_tests} passed ({success_count / total_tests  * 100:.1f}%)")
    print(f"Processing History: {len(math_node.get_trace()} MATRIZ nodes created")

    # Show deterministic behavior
    print("\nDeterministic Test:")
    test_expr = "2 + 3 * 4"
    hash1 = math_node.get_deterministic_hash({"expression": test_expr})
    hash2 = math_node.get_deterministic_hash({"expression": test_expr})
    print(f"Same input produces same hash: {hash1 == hash2}")
    print(f"Hash: {hash1[:16]}...")
