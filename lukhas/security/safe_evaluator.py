"""
Safe Expression Evaluator for LUKHAS

This module provides a secure AST-based expression evaluator that completely
eliminates the need for eval(). It supports:
- Boolean logic (and, or, not)
- Comparisons (<, <=, >, >=, ==, !=, in, not in, is, is not)
- Arithmetic operations (+, -, *, /, //, %, **)
- Attribute access on whitelisted objects
- Safe function calls (len, str, int, float, bool, etc.)
- String operations
- List/dict/tuple literals

Security principles:
1. NEVER uses eval(), exec(), or compile() for execution
2. Pure AST traversal and evaluation
3. Whitelist-based approach for all operations
4. No access to __builtins__ or dangerous functions
5. No ability to import modules or execute arbitrary code
"""

import ast
import math
import operator
import re
from typing import Any, Callable, Dict, Optional, Set, Union
from dataclasses import dataclass


class SecurityError(Exception):
    """Raised when an expression violates security policies."""
    pass


class EvaluationError(Exception):
    """Raised when expression evaluation fails."""
    pass


@dataclass
class EvaluationContext:
    """Context for expression evaluation."""
    variables: Dict[str, Any]
    allow_attribute_access: bool = False
    allowed_attributes: Optional[Set[str]] = None
    max_expression_depth: int = 50

    def __post_init__(self):
        if self.allowed_attributes is None:
            self.allowed_attributes = set()


class SafeEvaluator:
    """
    Safe expression evaluator using AST traversal.

    This evaluator provides a secure alternative to eval() by:
    1. Parsing expressions into AST
    2. Validating all nodes against security policies
    3. Evaluating nodes using a whitelist-based approach
    4. Never executing arbitrary code

    Example:
        >>> evaluator = SafeEvaluator()
        >>> result = evaluator.evaluate("2 + 2", {})
        >>> print(result)  # 4

        >>> context = {"age": 25, "name": "Alice"}
        >>> result = evaluator.evaluate("age > 18 and name == 'Alice'", context)
        >>> print(result)  # True
    """

    # Safe binary operators
    BINARY_OPERATORS: Dict[type, Callable] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Safe comparison operators
    COMPARISON_OPERATORS: Dict[type, Callable] = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: lambda x, y: x in y,
        ast.NotIn: lambda x, y: x not in y,
    }

    # Safe boolean operators
    BOOLEAN_OPERATORS: Dict[type, Callable] = {
        ast.And: lambda *args: all(args),
        ast.Or: lambda *args: any(args),
    }

    # Safe unary operators
    UNARY_OPERATORS: Dict[type, Callable] = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
    }

    # Safe built-in functions
    SAFE_FUNCTIONS: Dict[str, Callable] = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        # Math functions
        "ceil": math.ceil,
        "floor": math.floor,
        "sqrt": math.sqrt,
    }

    # Unsafe node types that should never be allowed
    UNSAFE_NODES: Set[type] = {
        ast.Import,
        ast.ImportFrom,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Lambda,
        ast.GeneratorExp,
        ast.ListComp,
        ast.DictComp,
        ast.SetComp,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
        ast.Global,
        ast.Nonlocal,
        ast.Delete,
        ast.AugAssign,
        ast.AnnAssign,
    }

    def __init__(self):
        self._depth = 0
        self._max_depth = 50

    def evaluate(
        self,
        expression: str,
        context: Union[Dict[str, Any], EvaluationContext],
        allow_attribute_access: bool = False,
        allowed_attributes: Optional[Set[str]] = None,
    ) -> Any:
        """
        Safely evaluate a Python expression.

        Args:
            expression: The expression string to evaluate
            context: Either a dict of variables or an EvaluationContext
            allow_attribute_access: Whether to allow attribute access (e.g., obj.field)
            allowed_attributes: Set of allowed attribute names (if attribute access is enabled)

        Returns:
            The evaluation result

        Raises:
            SecurityError: If the expression contains unsafe operations
            EvaluationError: If evaluation fails
            SyntaxError: If the expression cannot be parsed
        """
        # Normalize context
        if isinstance(context, dict):
            eval_context = EvaluationContext(
                variables=context,
                allow_attribute_access=allow_attribute_access,
                allowed_attributes=allowed_attributes or set(),
            )
        else:
            eval_context = context

        try:
            # Parse expression into AST
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise SyntaxError(f"Invalid expression syntax: {e}")

        # Validate AST for security
        self._validate_ast(tree, eval_context)

        # Reset depth counter
        self._depth = 0

        # Evaluate the expression
        try:
            return self._evaluate_node(tree.body, eval_context)
        except RecursionError:
            raise EvaluationError("Expression too deeply nested")
        except Exception as e:
            if isinstance(e, (SecurityError, EvaluationError)):
                raise
            raise EvaluationError(f"Evaluation failed: {e}")

    def _validate_ast(self, tree: ast.AST, context: EvaluationContext) -> None:
        """
        Validate that the AST contains only safe operations.

        Args:
            tree: AST to validate
            context: Evaluation context

        Raises:
            SecurityError: If unsafe operations are detected
        """
        for node in ast.walk(tree):
            node_type = type(node)

            # Check for explicitly unsafe nodes
            if node_type in self.UNSAFE_NODES:
                raise SecurityError(
                    f"Unsafe operation detected: {node_type.__name__}"
                )

            # Check for attribute access if not allowed
            if isinstance(node, ast.Attribute) and not context.allow_attribute_access:
                raise SecurityError(
                    "Attribute access is not allowed in this context"
                )

            # Check for function calls - only allow whitelisted functions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.SAFE_FUNCTIONS:
                        # Check if it's in the context
                        if func_name not in context.variables:
                            raise SecurityError(
                                f"Function '{func_name}' is not allowed"
                            )
                elif not isinstance(node.func, ast.Attribute):
                    raise SecurityError(
                        "Only simple function calls are allowed"
                    )

    def _evaluate_node(self, node: ast.AST, context: EvaluationContext) -> Any:
        """
        Evaluate an AST node.

        Args:
            node: AST node to evaluate
            context: Evaluation context

        Returns:
            The evaluation result

        Raises:
            SecurityError: If unsafe operations are encountered
            EvaluationError: If evaluation fails
        """
        # Check depth
        self._depth += 1
        if self._depth > context.max_expression_depth:
            raise EvaluationError("Expression too deeply nested")

        try:
            result = self._evaluate_node_impl(node, context)
            return result
        finally:
            self._depth -= 1

    def _evaluate_node_impl(self, node: ast.AST, context: EvaluationContext) -> Any:
        """Implementation of node evaluation."""
        node_type = type(node)

        # Literals
        if isinstance(node, ast.Constant):
            return node.value

        # For Python 3.8 compatibility
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.Bytes):
            return node.s
        if isinstance(node, ast.NameConstant):
            return node.value

        # Variables
        if isinstance(node, ast.Name):
            var_name = node.id
            if var_name in context.variables:
                return context.variables[var_name]
            # Check for special constants
            if var_name == "True":
                return True
            if var_name == "False":
                return False
            if var_name == "None":
                return None
            raise EvaluationError(f"Undefined variable: {var_name}")

        # Binary operations
        if isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left, context)
            right = self._evaluate_node(node.right, context)
            op = self.BINARY_OPERATORS.get(type(node.op))
            if op is None:
                raise SecurityError(f"Unsupported operator: {type(node.op).__name__}")
            return op(left, right)

        # Unary operations
        if isinstance(node, ast.UnaryOp):
            operand = self._evaluate_node(node.operand, context)
            op = self.UNARY_OPERATORS.get(type(node.op))
            if op is None:
                raise SecurityError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op(operand)

        # Comparisons
        if isinstance(node, ast.Compare):
            left = self._evaluate_node(node.left, context)

            for op, comparator in zip(node.ops, node.comparators):
                right = self._evaluate_node(comparator, context)
                op_func = self.COMPARISON_OPERATORS.get(type(op))
                if op_func is None:
                    raise SecurityError(f"Unsupported comparison: {type(op).__name__}")

                if not op_func(left, right):
                    return False
                left = right

            return True

        # Boolean operations
        if isinstance(node, ast.BoolOp):
            values = [self._evaluate_node(val, context) for val in node.values]
            op = self.BOOLEAN_OPERATORS.get(type(node.op))
            if op is None:
                raise SecurityError(f"Unsupported boolean operator: {type(node.op).__name__}")
            return op(*values)

        # Function calls
        if isinstance(node, ast.Call):
            return self._evaluate_call(node, context)

        # Attribute access
        if isinstance(node, ast.Attribute):
            return self._evaluate_attribute(node, context)

        # Subscripting
        if isinstance(node, ast.Subscript):
            value = self._evaluate_node(node.value, context)
            index = self._evaluate_node(node.slice, context)
            return value[index]

        # Collections
        if isinstance(node, ast.List):
            return [self._evaluate_node(elt, context) for elt in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._evaluate_node(elt, context) for elt in node.elts)

        if isinstance(node, ast.Dict):
            result = {}
            for key_node, value_node in zip(node.keys, node.values):
                key = self._evaluate_node(key_node, context)
                value = self._evaluate_node(value_node, context)
                result[key] = value
            return result

        if isinstance(node, ast.Set):
            return {self._evaluate_node(elt, context) for elt in node.elts}

        # If-expression (ternary)
        if isinstance(node, ast.IfExp):
            test = self._evaluate_node(node.test, context)
            if test:
                return self._evaluate_node(node.body, context)
            else:
                return self._evaluate_node(node.orelse, context)

        raise SecurityError(f"Unsupported AST node type: {node_type.__name__}")

    def _evaluate_call(self, node: ast.Call, context: EvaluationContext) -> Any:
        """Evaluate a function call."""
        # Get function
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            func = self.SAFE_FUNCTIONS.get(func_name)
            if func is None:
                # Check if it's in context
                if func_name in context.variables:
                    func = context.variables[func_name]
                    if not callable(func):
                        raise EvaluationError(f"'{func_name}' is not callable")
                else:
                    raise SecurityError(f"Function '{func_name}' is not allowed")
        elif isinstance(node.func, ast.Attribute):
            # Method call on an object
            obj = self._evaluate_node(node.func.value, context)
            attr_name = node.func.attr

            # Only allow specific safe methods
            if not context.allow_attribute_access:
                raise SecurityError("Method calls are not allowed in this context")

            if attr_name not in context.allowed_attributes:
                raise SecurityError(f"Method '{attr_name}' is not allowed")

            func = getattr(obj, attr_name)
        else:
            raise SecurityError("Complex function calls are not allowed")

        # Evaluate arguments
        args = [self._evaluate_node(arg, context) for arg in node.args]

        # Evaluate keyword arguments
        kwargs = {}
        for keyword in node.keywords:
            kwargs[keyword.arg] = self._evaluate_node(keyword.value, context)

        # Call function
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise EvaluationError(f"Function call failed: {e}")

    def _evaluate_attribute(self, node: ast.Attribute, context: EvaluationContext) -> Any:
        """Evaluate attribute access."""
        if not context.allow_attribute_access:
            raise SecurityError("Attribute access is not allowed in this context")

        obj = self._evaluate_node(node.value, context)
        attr_name = node.attr

        # Block access to private attributes and dangerous methods
        if attr_name.startswith("_"):
            raise SecurityError(f"Access to private attribute '{attr_name}' is not allowed")

        # Check if attribute is in allowed list
        if context.allowed_attributes and attr_name not in context.allowed_attributes:
            raise SecurityError(f"Access to attribute '{attr_name}' is not allowed")

        # Block access to dangerous attributes
        dangerous_attrs = {
            "__class__", "__bases__", "__subclasses__", "__globals__",
            "__builtins__", "__import__", "__code__", "__dict__",
        }
        if attr_name in dangerous_attrs:
            raise SecurityError(f"Access to '{attr_name}' is not allowed")

        try:
            return getattr(obj, attr_name)
        except AttributeError as e:
            raise EvaluationError(f"Attribute access failed: {e}")


# Convenience function for simple use cases
def safe_evaluate_expression(
    expression: str,
    context: Optional[Dict[str, Any]] = None,
    allow_attribute_access: bool = False,
    allowed_attributes: Optional[Set[str]] = None,
) -> Any:
    """
    Safely evaluate a Python expression.

    This is a convenience function that creates a SafeEvaluator and evaluates
    the expression.

    Args:
        expression: The expression string to evaluate
        context: Dictionary of variables available in the expression
        allow_attribute_access: Whether to allow attribute access
        allowed_attributes: Set of allowed attribute names

    Returns:
        The evaluation result

    Raises:
        SecurityError: If the expression contains unsafe operations
        EvaluationError: If evaluation fails
        SyntaxError: If the expression cannot be parsed

    Example:
        >>> result = safe_evaluate_expression("2 + 2")
        >>> print(result)  # 4

        >>> context = {"age": 25}
        >>> result = safe_evaluate_expression("age > 18", context)
        >>> print(result)  # True
    """
    evaluator = SafeEvaluator()
    return evaluator.evaluate(
        expression,
        context or {},
        allow_attribute_access=allow_attribute_access,
        allowed_attributes=allowed_attributes,
    )
