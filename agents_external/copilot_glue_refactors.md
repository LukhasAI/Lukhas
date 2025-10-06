---
status: wip
type: documentation
---
# Copilot — Glue Code, Typing & Edge Case Testing

## Primary Task
Implement comprehensive glue code refactoring with typing hardening and edge case validation:
- Type safety enforcement with mypy strict mode compliance
- Integration glue code optimization and error handling
- Edge case testing with boundary condition validation
- Refactoring legacy code patterns with modern Python best practices

**Output**: artifacts/{component}_glue_refactors_validation.json

## Specific Instructions

### Type Safety Enforcement
```python
from typing import (
    TypeVar, Generic, Protocol, Union, Optional, Dict, List, Any,
    Callable, Awaitable, AsyncIterator, Iterator, Tuple, cast,
    TYPE_CHECKING, Final, Literal, overload
)
from typing_extensions import ParamSpec, Concatenate
import abc
from dataclasses import dataclass, field
from enum import Enum, auto

# Type variable definitions
T = TypeVar('T')
P = ParamSpec('P')
ResponseT = TypeVar('ResponseT')

class StrictTypingValidator:
    """Validates and enforces strict typing across LUKHAS codebase."""

    def __init__(self):
        self.type_violations: List[Dict[str, Any]] = []

    def validate_function_signatures(self, module_path: str) -> Dict[str, Any]:
        """Validate all function signatures have proper type annotations."""
        import ast
        import inspect

        violations = []

        try:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check return type annotation
                    if node.returns is None and node.name != '__init__':
                        violations.append({
                            'type': 'missing_return_type',
                            'function': node.name,
                            'line': node.lineno
                        })

                    # Check parameter type annotations
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != 'self':
                            violations.append({
                                'type': 'missing_param_type',
                                'function': node.name,
                                'parameter': arg.arg,
                                'line': node.lineno
                            })

        except Exception as e:
            violations.append({
                'type': 'validation_error',
                'error': str(e),
                'module': module_path
            })

        return {
            'module_path': module_path,
            'violations': violations,
            'clean': len(violations) == 0
        }

    def generate_type_stubs(self, class_definition: str) -> str:
        """Generate proper type stubs for legacy classes."""
        # This would analyze existing class and generate proper .pyi files
        # For now, return template
        return '''
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Union
from typing_extensions import Literal

T = TypeVar('T')

class LegacyClass(Protocol):
    def process(self, data: Dict[str, Any]) -> Optional[T]: ...
    def validate(self, input_data: Union[str, Dict[str, Any]]) -> bool: ...
'''

# Protocol definitions for better type safety
class MATRIZComponent(Protocol):
    """Protocol defining the interface for MATRIZ components."""

    async def tick(self, context: 'MATRIZContext') -> 'TickResult':
        """Execute component tick operation."""
        ...

    async def reflect(self, tick_result: 'TickResult') -> 'ReflectionResult':
        """Execute component reflection operation."""
        ...

    async def decide(self, reflection: 'ReflectionResult') -> 'DecisionResult':
        """Execute component decision operation."""
        ...

@dataclass(frozen=True)
class MATRIZContext:
    """Immutable context for MATRIZ operations."""
    request_id: str
    timestamp: float
    component_id: str
    lane: Literal['candidate', 'integration', 'production']
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TickResult:
    """Result of a MATRIZ tick operation."""
    success: bool
    duration_ms: float
    data: Dict[str, Any]
    errors: List[str] = field(default_factory=list)

# Generic error handling with proper typing
class MATRIZError(Exception):
    """Base exception for MATRIZ operations."""

    def __init__(self, message: str, context: Optional[MATRIZContext] = None,
                 error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.context = context
        self.error_code = error_code

class ComponentError(MATRIZError):
    """Error in component operation."""
    pass

class ValidationError(MATRIZError):
    """Error in data validation."""
    pass
```

### Integration Glue Code Optimization
```python
class IntegrationGlue:
    """Optimized glue code for LUKHAS component integration."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.component_registry: Dict[str, MATRIZComponent] = {}
        self.error_handlers: List[Callable[[Exception], None]] = []

    async def register_component(self, component_id: str,
                               component: MATRIZComponent) -> None:
        """Register a MATRIZ component with type safety."""
        if not isinstance(component, MATRIZComponent):
            raise TypeError(f"Component {component_id} does not implement MATRIZComponent protocol")

        self.component_registry[component_id] = component

    async def execute_matriz_cycle(self, context: MATRIZContext) -> Dict[str, Any]:
        """Execute complete MATRIZ cycle with error handling."""
        results = {
            'context': context,
            'component_results': {},
            'cycle_success': True,
            'total_duration_ms': 0.0
        }

        cycle_start = time.time()

        try:
            for component_id, component in self.component_registry.items():
                component_start = time.time()

                try:
                    # Execute tick-reflect-decide cycle
                    tick_result = await component.tick(context)
                    reflection_result = await component.reflect(tick_result)
                    decision_result = await component.decide(reflection_result)

                    component_duration = (time.time() - component_start) * 1000

                    results['component_results'][component_id] = {
                        'tick': tick_result,
                        'reflection': reflection_result,
                        'decision': decision_result,
                        'duration_ms': component_duration,
                        'success': True
                    }

                except Exception as e:
                    # Handle component-level errors
                    component_error = ComponentError(
                        f"Component {component_id} failed: {str(e)}",
                        context=context,
                        error_code=f"COMPONENT_{component_id.upper()}_FAILED"
                    )

                    results['component_results'][component_id] = {
                        'error': str(component_error),
                        'success': False
                    }

                    results['cycle_success'] = False

                    # Execute error handlers
                    for handler in self.error_handlers:
                        try:
                            handler(component_error)
                        except Exception:
                            pass  # Don't let error handlers break the cycle

        finally:
            results['total_duration_ms'] = (time.time() - cycle_start) * 1000

        return results

    def add_error_handler(self, handler: Callable[[Exception], None]) -> None:
        """Add an error handler for component failures."""
        self.error_handlers.append(handler)

# Legacy code adapter with proper typing
class LegacyAdapter:
    """Adapter for legacy code with modern typing."""

    @overload
    def convert_legacy_response(self, response: str) -> Dict[str, str]: ...

    @overload
    def convert_legacy_response(self, response: Dict[str, Any]) -> Dict[str, Any]: ...

    @overload
    def convert_legacy_response(self, response: List[Any]) -> List[Dict[str, Any]]: ...

    def convert_legacy_response(self, response: Union[str, Dict[str, Any], List[Any]]) -> Union[Dict[str, str], Dict[str, Any], List[Dict[str, Any]]]:
        """Convert legacy response format to modern typed format."""
        if isinstance(response, str):
            return {'message': response, 'type': 'string'}
        elif isinstance(response, dict):
            # Ensure all keys are strings and add type information
            typed_response: Dict[str, Any] = {}
            for key, value in response.items():
                typed_response[str(key)] = value
            typed_response['_legacy_conversion'] = True
            return typed_response
        elif isinstance(response, list):
            return [
                self.convert_legacy_response(item) if not isinstance(item, dict)
                else {**item, '_legacy_conversion': True}
                for item in response
            ]
        else:
            raise ValidationError(f"Unsupported legacy response type: {type(response)}")
```

### Edge Case Testing Framework
```python
class EdgeCaseValidator:
    """Comprehensive edge case testing for LUKHAS components."""

    def __init__(self):
        self.edge_cases: List[Dict[str, Any]] = []

    def test_boundary_conditions(self, function: Callable[..., Any],
                                test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test function with boundary conditions and edge cases."""
        results = {
            'function_name': function.__name__,
            'total_cases': len(test_cases),
            'passed_cases': 0,
            'failed_cases': 0,
            'edge_case_results': []
        }

        for i, test_case in enumerate(test_cases):
            case_result = {
                'case_index': i,
                'input_data': test_case.get('input', {}),
                'expected': test_case.get('expected'),
                'passed': False,
                'error': None,
                'actual_result': None
            }

            try:
                # Execute function with edge case input
                if 'args' in test_case:
                    actual_result = function(*test_case['args'])
                elif 'kwargs' in test_case:
                    actual_result = function(**test_case['kwargs'])
                else:
                    actual_result = function(test_case.get('input'))

                case_result['actual_result'] = actual_result

                # Validate result
                if 'expected' in test_case:
                    if actual_result == test_case['expected']:
                        case_result['passed'] = True
                        results['passed_cases'] += 1
                    else:
                        results['failed_cases'] += 1
                        case_result['error'] = f"Expected {test_case['expected']}, got {actual_result}"
                elif 'validator' in test_case:
                    validator = test_case['validator']
                    if validator(actual_result):
                        case_result['passed'] = True
                        results['passed_cases'] += 1
                    else:
                        results['failed_cases'] += 1
                        case_result['error'] = "Custom validator failed"

            except Exception as e:
                case_result['error'] = str(e)
                case_result['exception_type'] = type(e).__name__
                results['failed_cases'] += 1

                # Check if exception was expected
                if 'expected_exception' in test_case:
                    expected_exception = test_case['expected_exception']
                    if isinstance(e, expected_exception):
                        case_result['passed'] = True
                        results['passed_cases'] += 1
                        results['failed_cases'] -= 1

            results['edge_case_results'].append(case_result)

        results['success_rate'] = results['passed_cases'] / results['total_cases'] if results['total_cases'] > 0 else 0
        return results

    def generate_matriz_edge_cases(self) -> List[Dict[str, Any]]:
        """Generate comprehensive edge cases for MATRIZ operations."""
        edge_cases = [
            # Empty/None inputs
            {
                'description': 'Empty context',
                'input': None,
                'expected_exception': ValidationError
            },
            {
                'description': 'Invalid component ID',
                'kwargs': {'component_id': '', 'context': MATRIZContext('test', time.time(), '', 'candidate')},
                'expected_exception': ValidationError
            },

            # Boundary values
            {
                'description': 'Maximum string length',
                'input': 'x' * 10000,
                'validator': lambda x: isinstance(x, (str, dict))
            },
            {
                'description': 'Negative timestamp',
                'kwargs': {'timestamp': -1},
                'expected_exception': ValueError
            },

            # Type mismatches
            {
                'description': 'String instead of dict',
                'input': 'not_a_dict',
                'expected_exception': TypeError
            },

            # Unicode and special characters
            {
                'description': 'Unicode handling',
                'input': {'text': '🚀✨🧠💫'},
                'validator': lambda x: 'text' in x if isinstance(x, dict) else False
            },

            # Large data structures
            {
                'description': 'Large nested dict',
                'input': {'level1': {'level2': {'level3': list(range(1000))}}},
                'validator': lambda x: isinstance(x, dict) and 'level1' in x
            },

            # Concurrent access patterns
            {
                'description': 'Concurrent modification',
                'input': {'shared_state': {'counter': 0}},
                'validator': lambda x: isinstance(x, dict)
            }
        ]

        return edge_cases

# Refactored legacy patterns
class ModernMATRIZProcessor:
    """Refactored MATRIZ processor with modern patterns."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._components: Dict[str, MATRIZComponent] = {}
        self._metrics_collector: Optional[Callable[[str, float], None]] = None

    async def process_request(self,
                            request_data: Dict[str, Any],
                            *,  # Force keyword-only arguments
                            component_id: str,
                            lane: Literal['candidate', 'integration', 'production'],
                            timeout_ms: int = 30000) -> Dict[str, Any]:
        """Process MATRIZ request with modern error handling and type safety."""

        # Input validation
        if not request_data:
            raise ValidationError("Request data cannot be empty")

        if not component_id:
            raise ValidationError("Component ID is required")

        if component_id not in self._components:
            raise ComponentError(f"Component {component_id} not registered")

        # Create typed context
        context = MATRIZContext(
            request_id=request_data.get('request_id', str(uuid.uuid4())),
            timestamp=time.time(),
            component_id=component_id,
            lane=lane,
            metadata=request_data.get('metadata', {})
        )

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute_component_cycle(context),
                timeout=timeout_ms / 1000.0
            )

            # Collect metrics
            if self._metrics_collector:
                self._metrics_collector(
                    f'matriz.{component_id}.success',
                    result['duration_ms']
                )

            return result

        except asyncio.TimeoutError:
            raise ComponentError(f"Component {component_id} timed out after {timeout_ms}ms")
        except Exception as e:
            # Collect error metrics
            if self._metrics_collector:
                self._metrics_collector(f'matriz.{component_id}.error', 1)

            raise ComponentError(f"Component {component_id} failed: {str(e)}") from e

    async def _execute_component_cycle(self, context: MATRIZContext) -> Dict[str, Any]:
        """Execute the component cycle with proper error handling."""
        component = self._components[context.component_id]

        start_time = time.time()

        # Execute tick-reflect-decide cycle
        tick_result = await component.tick(context)
        reflection_result = await component.reflect(tick_result)
        decision_result = await component.decide(reflection_result)

        duration_ms = (time.time() - start_time) * 1000

        return {
            'context': context,
            'tick_result': tick_result,
            'reflection_result': reflection_result,
            'decision_result': decision_result,
            'duration_ms': duration_ms,
            'success': True
        }
```

### Performance Requirements
- Type validation: <10ms per module
- Glue code execution: <50ms per component integration
- Edge case testing: <200ms per test suite
- Legacy code adaptation: <25ms per conversion

### Testing Framework
```python
@pytest.mark.refactoring
@pytest.mark.lane("integration")
def test_strict_typing_validation():
    validator = StrictTypingValidator()

    # Test with a properly typed module
    result = validator.validate_function_signatures('lukhas/core/typed_module.py')
    assert result['clean'] is True
    assert len(result['violations']) == 0

@pytest.mark.refactoring
@pytest.mark.lane("integration")
def test_edge_case_validation():
    validator = EdgeCaseValidator()

    def sample_function(x: int) -> int:
        if x < 0:
            raise ValueError("Negative values not allowed")
        return x * 2

    edge_cases = [
        {'input': 0, 'expected': 0},
        {'input': sys.maxsize, 'expected': sys.maxsize * 2},
        {'input': -1, 'expected_exception': ValueError}
    ]

    result = validator.test_boundary_conditions(sample_function, edge_cases)
    assert result['success_rate'] == 1.0

@pytest.mark.refactoring
@pytest.mark.lane("integration")
async def test_integration_glue():
    glue = IntegrationGlue({'test': True})

    # Mock component
    class MockComponent:
        async def tick(self, context):
            return TickResult(True, 10.0, {'processed': True})

        async def reflect(self, tick_result):
            return {'reflection': 'completed'}

        async def decide(self, reflection_result):
            return {'decision': 'proceed'}

    await glue.register_component('test_component', MockComponent())

    context = MATRIZContext('test', time.time(), 'test_component', 'candidate')
    result = await glue.execute_matriz_cycle(context)

    assert result['cycle_success'] is True
    assert 'test_component' in result['component_results']
```

### Evidence Generation
Create validation artifact with structure:
```json
{
  "component": "glue_refactors_validation",
  "validation_timestamp": "ISO8601",
  "type_safety": {
    "mypy_strict_compliance": true,
    "function_signatures_typed": true,
    "protocol_compliance": true,
    "type_stubs_generated": true,
    "performance_ms": 8
  },
  "glue_code": {
    "integration_optimized": true,
    "error_handling_improved": true,
    "legacy_adapters_created": true,
    "performance_ms": 42
  },
  "edge_case_testing": {
    "boundary_conditions_tested": true,
    "unicode_handling_validated": true,
    "concurrent_access_tested": true,
    "success_rate": 1.0,
    "performance_ms": 185
  },
  "refactoring": {
    "legacy_patterns_modernized": true,
    "type_safety_improved": true,
    "error_handling_enhanced": true,
    "performance_ms": 20
  }
}
```