# 🚀 LUKHAS  Module Interface Quick Reference

## Common Imports

```python
# Core
from core.common import GLYPHToken, get_logger
from core.interfaces import CoreInterface
from core.interfaces.dependency_injection import inject, get_service

# Memory
from core.interfaces.memory_interface import MemoryInterface, MemoryType
from memory.core.unified_memory_orchestrator import UnifiedMemoryOrchestrator

# Consciousness
from consciousness.unified.auto_consciousness import AutoConsciousness
from consciousness.reflection.self_reflection import ReflectionEngine

# Guardian
from governance.guardian_system import GuardianSystem, ValidationResult
```

## Basic Module Pattern

```python
from core.interfaces import CoreInterface
from core.common import GLYPHToken, get_logger
from core.interfaces.dependency_injection import register_service

logger = get_logger(__name__)

class MyModule(CoreInterface):
    """Example LUKHAS module"""

    def __init__(self):
        self.operational = False

    async def initialize(self):
        """Async initialization"""
        # Register with dependency injection
        register_service("my_module", self, singleton=True)
        self.operational = True
        logger.info("MyModule initialized")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data"""
        if not self.operational:
            raise ProcessingError("Module not initialized")

        # Process data
        result = {"processed": True, "data": data}
        return result

    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH communication"""
        # Process token
        response = GLYPHToken(
            symbol=token.symbol,
            source=self.__class__.__name__,
            target=token.source,
            payload={"response": "acknowledged"}
        )
        return response

    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            "operational": self.operational,
            "health_score": 1.0 if self.operational else 0.0,
            "last_update": datetime.now(timezone.utc),
            "metrics": {}
        }
```

## Dependency Injection

### Register Service

```python
# In module initialization
from core.interfaces.dependency_injection import register_service

async def initialize(self):
    register_service("my_service", self, singleton=True)
```

### Get Service

```python
# Direct access
from core.interfaces.dependency_injection import get_service

memory_service = get_service("memory_service")
result = await memory_service.store(data, MemoryType.EPISODIC)
```

### Inject Service

```python
# Decorator injection
from core.interfaces.dependency_injection import inject

@inject(service_name="memory_service")
async def process_with_memory(data, memory_service=None):
    memory_id = await memory_service.store(data, MemoryType.WORKING)
    return memory_id
```

## GLYPH Communication

### Send GLYPH Token

```python
from core.common import GLYPHToken, GLYPHSymbol

# Create token
token = GLYPHToken(
    symbol=GLYPHSymbol.QUERY,
    source="module_a",
    target="module_b",
    payload={"query": "status"}
)

# Send to target
target_module = get_service("module_b")
response = await target_module.handle_glyph(token)
```

### Common GLYPH Symbols

```python
GLYPHSymbol.SYNC      # Synchronization
GLYPHSymbol.QUERY     # Query request
GLYPHSymbol.TRUST     # Trust establishment
GLYPHSymbol.REFLECT   # Reflection trigger
GLYPHSymbol.DREAM     # Dream state
GLYPHSymbol.WAKE      # Wake state
GLYPHSymbol.LEARN     # Learning signal
GLYPHSymbol.ALERT     # Alert/warning
```

## Memory Operations

### Store Memory

```python
memory_service = get_service("memory_service")

# Store episodic memory
memory_id = await memory_service.store(
    content={"event": "user_interaction", "data": {...}},
    memory_type=MemoryType.EPISODIC,
    metadata={"importance": 0.8}
)
```

### Retrieve Memory

```python
# Retrieve by ID
memory_item = await memory_service.retrieve(memory_id)

# Search memories
results = await memory_service.search(
    query={"type": "user_interaction", "timestamp": {"$gt": yesterday}},
    memory_type=MemoryType.EPISODIC,
    limit=10
)
```

## Consciousness Operations

### Make Decision

```python
consciousness = get_service("consciousness_service")

decision = await consciousness.make_decision(
    scenario={
        "context": "user_request",
        "options": ["approve", "deny", "defer"],
        "constraints": ["ethical", "safe"]
    }
)

if decision.confidence > 0.8:
    execute_decision(decision.selected_option)
```

### Assess Awareness

```python
awareness_state = await consciousness.assess_awareness({
    "stimulus": incoming_data,
    "context": current_context
})

if awareness_state.overall_awareness < 0.5:
    await consciousness.increase_attention(targets=["critical_stimulus"])
```

## Guardian Validation

### Validate Action

```python
guardian = get_service("guardian_service")

validation = await guardian.validate_action(
    action={
        "type": "data_access",
        "target": "user_profile",
        "purpose": "personalization"
    },
    context={"user_consent": True}
)

if validation.approved:
    proceed_with_action(validation.constraints)
else:
    handle_rejection(validation.reasoning)
```

### Monitor Drift

```python
drift_result = await guardian.detect_drift({
    "recent_behaviors": behavior_log[-100:],
    "baseline": established_baseline
})

if drift_result.drift_score > 0.5:
    await apply_remediation(drift_result.remediation_actions)
```

## Error Handling

### Standard Pattern

```python
from core.common.exceptions import LukhasError, ValidationError

try:
    result = await risky_operation()
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return {"error": "validation", "message": str(e)}
except LukhasError as e:
    logger.error(f"Operation failed: {e}")
    return {"error": "operation", "message": str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return {"error": "unexpected", "message": "Internal error"}
```

## Performance Monitoring

### Add Metrics

```python
from time import time

class MyModule(CoreInterface):
    def __init__(self):
        self.metrics = {
            "operations_count": 0,
            "total_time_ms": 0,
            "errors_count": 0
        }

    async def process(self, data):
        start = time()
        try:
            result = await self._process_internal(data)
            self.metrics["operations_count"] += 1
            return result
        except Exception as e:
            self.metrics["errors_count"] += 1
            raise
        finally:
            self.metrics["total_time_ms"] += (time() - start) * 1000
```

## Testing Pattern

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_memory_service():
    service = Mock()
    service.store = AsyncMock(return_value="mem_123")
    service.retrieve = AsyncMock(return_value={"data": "test"})
    return service

@pytest.mark.asyncio
async def test_my_module(mock_memory_service, monkeypatch):
    # Inject mock service
    monkeypatch.setattr(
        "core.interfaces.dependency_injection.get_service",
        lambda name: mock_memory_service if name == "memory_service" else None
    )

    # Test module
    module = MyModule()
    await module.initialize()

    result = await module.process({"test": "data"})
    assert result["processed"] is True
```

## Common Gotchas

1. **Always use async/await** - All module operations should be async
2. **Register services early** - Register in `initialize()` method
3. **Handle service unavailability** - Services might not be registered
4. **Validate GLYPH tokens** - Always validate incoming tokens
5. **Check Guardian approval** - Never skip ethical validation
6. **Close memory folds** - Always close opened memory folds
7. **Monitor drift** - Regular drift checks prevent issues
8. **Log appropriately** - Use proper log levels

---

*Quick Reference v1.0.0*
