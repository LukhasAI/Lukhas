# Core Adapters - Provider Pattern Infrastructure

**Purpose**: Runtime dependency injection to eliminate import-time dependencies from production → development lanes.

**Created**: 2025-11-02
**Part of**: Lane Isolation Initiative
**Status**: Production Ready ✅

---

## Architecture Overview

### The Problem: Lane Isolation

LUKHAS uses a 3-tier lane architecture:
```
candidate/  → Development lane (2,877 files) - Experimental research
core/       → Integration lane (253 files) - Testing/validation
lukhas/     → Production lane (692 files) - Battle-tested systems
```

**Critical Rule**: Production code (`lukhas/`, `core/`) MUST NOT import from development (`candidate/`, `labs/`) at **import time**.

### The Solution: Provider Pattern

The provider pattern uses **lazy loading** to defer imports until runtime:

```python
# ❌ BAD - Import-time dependency
from labs.consciousness import ConsciousnessService

class MyClass:
    def __init__(self):
        self.service = ConsciousnessService()  # Imported at module load

# ✅ GOOD - Runtime dependency via provider
from core.adapters import ProviderRegistry, make_resolver

class MyClass:
    def __init__(self):
        registry = ProviderRegistry(make_resolver())
        self.service = registry.get_consciousness_service()  # Imported when called
```

---

## Quick Start

### 1. Basic Usage

```python
from core.adapters import ProviderRegistry, make_resolver

# Create registry
config = make_resolver()
registry = ProviderRegistry(config)

# Get providers (lazy loaded on first access)
openai = registry.get_openai()
consciousness = registry.get_consciousness_service()
memory = registry.get_memory_service()
identity = registry.get_identity_service()
governance = registry.get_governance_service()
```

### 2. With Custom Configuration

```python
from core.adapters import ProviderRegistry, Config

# Create custom config
config = Config(
    environment="production",
    openai_model="gpt-4-turbo",
    openai_temperature=0.8,
)

registry = ProviderRegistry(config)
openai = registry.get_openai()
```

### 3. In Class Properties (Recommended)

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from labs.consciousness import ConsciousnessService
else:
    ConsciousnessService = None

class MyOrchestrator:
    def __init__(self):
        self._consciousness = None
        self._consciousness_loaded = False

    @property
    def consciousness(self) -> "ConsciousnessService":
        """Lazy-load consciousness service."""
        if self._consciousness is None and not self._consciousness_loaded:
            from core.adapters import ProviderRegistry, make_resolver
            registry = ProviderRegistry(make_resolver())
            self._consciousness = registry.get_consciousness_service()
            self._consciousness_loaded = True
        return self._consciousness
```

---

## Available Providers

### OpenAI Provider
```python
registry.get_openai() -> OpenAIModulatedService
```
**Module**: `labs.consciousness.reflection.openai_modulated_service`
**Use Cases**: GPT model access, OpenAI API calls, modulated AI requests
**Configuration**:
- `OPENAI_API_KEY` - API key
- `OPENAI_MODEL` - Model name (default: gpt-4)
- `OPENAI_TEMPERATURE` - Temperature (default: 0.7)

### Consciousness Service
```python
registry.get_consciousness_service() -> UnifiedConsciousnessService
```
**Modules Tried** (in order):
1. `candidate.consciousness.unified_consciousness_service`
2. `candidate.consciousness.consciousness_service`
3. `labs.consciousness.consciousness_service`

**Use Cases**: Consciousness processing, multi-engine coordination, reasoning systems
**Features**: Poetic/Complete/Codex/Alternative engines, dream integration, reflection

### Memory Service
```python
registry.get_memory_service() -> MemoryService
```
**Modules Tried** (in order):
1. `candidate.memory.memory_service`
2. `candidate.memory.unified_memory`
3. `labs.memory.memory_service`

**Use Cases**: Fold systems, emotional memory, temporal memory, memory persistence
**Features**: 1000-fold architecture, 99.7% cascade prevention, VAD encoding

### Identity Service
```python
registry.get_identity_service() -> LambdaIDService
```
**Modules Tried** (in order):
1. `candidate.identity.lambda_id`
2. `candidate.identity.identity_service`
3. `lukhas.identity.lambda_id`

**Use Cases**: Lambda ID management, namespace isolation, multi-modal auth
**Features**: WebAuthn/passkey support, crypto wallet auth, identity coherence

### Governance Service
```python
registry.get_governance_service() -> UnifiedConstitutionalAI
```
**Modules Tried** (in order):
1. `candidate.governance.unified_constitutional_ai`
2. `candidate.governance.governance_service`
3. `labs.governance.guardian_service`

**Use Cases**: Constitutional AI, Guardian systems, ethics validation, drift detection
**Features**: 33+ ethics components, real-time constitutional review, compliance

---

## Configuration

### Environment Variables

```bash
# Environment
LUKHAS_ENV=development|staging|production

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Testing
LUKHAS_MOCK_PROVIDERS=true|false
```

### Config Object

```python
from core.adapters import Config

config = Config(
    environment="production",
    openai_api_key="sk-...",
    openai_model="gpt-4-turbo",
    openai_temperature=0.8,
    mock_providers=False,
    extra={"custom_key": "custom_value"}
)

# Get/set values
api_key = config.get("openai_api_key")
config.set("custom_setting", "value")
```

---

## Testing

### Import Safety Testing

Every refactored module should have an import-safety test:

```python
# tests/integration/test_mymodule_importsafe.py

def test_mymodule_import_safety():
    """Verify module imports without labs dependencies."""
    try:
        from core.mypackage import mymodule
        assert mymodule is not None
    except ImportError as e:
        if "labs" in str(e) or "candidate" in str(e):
            raise AssertionError(f"Module has import-time dependency: {e}")
        raise
```

### Provider Testing

```python
from core.adapters import ProviderRegistry, make_resolver

def test_provider_loading():
    """Test provider can be loaded."""
    registry = ProviderRegistry(make_resolver())

    # Should not raise if module is available
    provider = registry.get_consciousness_service()
    assert provider is not None

    # Should cache
    provider2 = registry.get_consciousness_service()
    assert provider is provider2
```

### Mocking in Tests

```python
import pytest
from core.adapters import ProviderRegistry, Config

def test_with_mock_provider():
    """Test with mocked provider."""
    config = Config(mock_providers=True)
    registry = ProviderRegistry(config)

    # Register mock
    mock_service = MockConsciousnessService()
    registry.register_provider("consciousness", mock_service)

    # Get returns mock
    service = registry.get_consciousness_service()
    assert service is mock_service
```

---

## Migration Guide

### Before (Import-time Dependency)

```python
from labs.consciousness import ConsciousnessService
from labs.openai import OpenAIModulatedService

class Orchestrator:
    def __init__(self):
        self.consciousness = ConsciousnessService()
        self.openai = OpenAIModulatedService()

    async def process(self, query: str):
        result = await self.consciousness.process(query)
        enhanced = await self.openai.enhance(result)
        return enhanced
```

### After (Runtime Dependency)

```python
from typing import TYPE_CHECKING, Optional
from core.adapters import ProviderRegistry, make_resolver

if TYPE_CHECKING:
    from labs.consciousness import ConsciousnessService
    from labs.openai import OpenAIModulatedService
else:
    ConsciousnessService = None
    OpenAIModulatedService = None

class Orchestrator:
    def __init__(self):
        self._consciousness: Optional["ConsciousnessService"] = None
        self._openai: Optional["OpenAIModulatedService"] = None
        self._loaded = {"consciousness": False, "openai": False}

    @property
    def consciousness(self) -> "ConsciousnessService":
        if self._consciousness is None and not self._loaded["consciousness"]:
            registry = ProviderRegistry(make_resolver())
            self._consciousness = registry.get_consciousness_service()
            self._loaded["consciousness"] = True
        return self._consciousness

    @property
    def openai(self) -> "OpenAIModulatedService":
        if self._openai is None and not self._loaded["openai"]:
            registry = ProviderRegistry(make_resolver())
            self._openai = registry.get_openai()
            self._loaded["openai"] = True
        return self._openai

    async def process(self, query: str):
        # Same logic, but services loaded lazily
        result = await self.consciousness.process(query)
        enhanced = await self.openai.enhance(result)
        return enhanced
```

---

## Benefits

### 1. Lane Isolation ✅
- Production code can be imported without candidate/labs
- Static analysis tools work without development dependencies
- Clear separation of concerns

### 2. Testing Flexibility ✅
- Easy to mock providers in tests
- Can test production code in isolation
- No need to have full candidate/ tree for unit tests

### 3. Performance ✅
- Lazy loading reduces startup time
- Only load what's needed
- Caching prevents duplicate imports

### 4. Maintainability ✅
- Clear dependency boundaries
- Easy to swap implementations
- Configuration-driven behavior

### 5. Type Safety ✅
- Full type hints with `TYPE_CHECKING`
- IDEs provide autocomplete
- Static type checkers work correctly

---

## Troubleshooting

### Provider Not Found

```python
ImportError: Could not find consciousness service in any of: [...]
```

**Solutions**:
1. Check that candidate/consciousness exists
2. Verify module structure matches expected paths
3. Check for typos in class names
4. Review logs for detailed error messages

### Import Errors at Module Load

```python
ImportError: cannot import name 'ConsciousnessService' from 'labs.consciousness'
```

**Cause**: Direct import instead of lazy loading

**Solution**: Use provider pattern or `TYPE_CHECKING` guard

### Cached Provider Issues

```python
# Clear cache in tests
registry.clear()

# Or create new registry
registry = ProviderRegistry(make_resolver())
```

---

## Examples

See:
- `core/orchestration/gpt_colony_orchestrator.py` - Full implementation
- `tests/integration/test_gpt_colony_orchestrator_importsafe.py` - Import safety tests
- `core/governance.py` - Lazy loading with `__getattr__`
- `core/collective/__init__.py` - Dynamic module loading

---

## API Reference

### ProviderRegistry

```python
class ProviderRegistry:
    def __init__(self, config: Config)

    def get_openai() -> OpenAIModulatedService
    def get_consciousness_service() -> Any
    def get_memory_service() -> Any
    def get_identity_service() -> Any
    def get_governance_service() -> Any

    def get_provider(name: str) -> Optional[Any]
    def register_provider(name: str, instance: Any) -> None
    def is_initialized(name: str) -> bool
    def clear() -> None
```

### Config

```python
@dataclass
class Config:
    environment: str
    openai_api_key: Optional[str]
    openai_model: str
    openai_temperature: float
    mock_providers: bool
    extra: dict[str, Any]

    def get(key: str, default: Any = None) -> Any
    def set(key: str, value: Any) -> None
```

### make_resolver

```python
def make_resolver() -> Config:
    """Factory function to create Config from environment."""
```

---

## Related Documentation

- [Lane Isolation Architecture](../../docs/architecture/LANE_ISOLATION.md)
- [Testing Guide](../../docs/testing/IMPORT_SAFETY.md)
- [Migration Guide](../../docs/migration/PROVIDER_PATTERN.md)
- [Constellation Framework](../../lukhas_context.md)

---

**Maintained by**: LUKHAS Core Team
**Last Updated**: 2025-11-02
**Questions?**: See issues or contact dev team
