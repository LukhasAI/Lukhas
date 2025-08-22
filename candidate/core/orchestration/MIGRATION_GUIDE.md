# LUKHAS AI Orchestrator Migration Guide

**Version**: 1.0.0  
**Date**: 2025-07-26  
**Authors**: LUKHAS AI Architecture Team | AGI Agent

## Table of Contents

1. [Overview](#overview)
2. [Migration Patterns](#migration-patterns)
3. [Step-by-Step Migration Process](#step-by-step-migration-process)
4. [Code Examples](#code-examples)
5. [Testing Strategy](#testing-strategy)
6. [Common Pitfalls](#common-pitfalls)
7. [Rollback Plan](#rollback-plan)

## Overview

This guide provides comprehensive instructions for migrating existing orchestrators to the new LUKHAS orchestrator hierarchy. The new pattern provides standardized lifecycle management, health monitoring, and inter-module communication.

### New Orchestrator Hierarchy

```
BaseOrchestrator (Abstract)
├── ModuleOrchestrator      # Single module management
├── SystemOrchestrator      # Cross-module coordination
├── MasterOrchestrator      # Top-level system control
└── EndocrineOrchestrator   # Bio-aware orchestration
```

## Migration Patterns

### Pattern 1: Simple Module Orchestrator

For orchestrators that manage components within a single module (like MemoryOrchestrator):

```python
# OLD PATTERN
class MyOrchestrator:
    def __init__(self, config=None):
        self.config = config or {}
        self.is_initialized = False
        
    async def initialize(self):
        # Custom initialization
        pass

# NEW PATTERN
from lukhas.orchestration.module_orchestrator import ModuleOrchestrator, ModuleOrchestratorConfig

class MyOrchestrator(ModuleOrchestrator):
    def __init__(self, config=None):
        if config is None:
            config = ModuleOrchestratorConfig(
                name="MyOrchestrator",
                description="Description here",
                module_name="my_module"
            )
        super().__init__(config)
```

### Pattern 2: Complex System Orchestrator

For orchestrators that coordinate multiple modules (like BrainOrchestrator, EthicsOrchestrator):

```python
# OLD PATTERN
class ComplexOrchestrator:
    def __init__(self):
        self.subsystem1 = None
        self.subsystem2 = None
        self.metrics = {}

# NEW PATTERN  
from lukhas.orchestration.system_orchestrator import SystemOrchestrator, SystemOrchestratorConfig

class ComplexOrchestrator(SystemOrchestrator):
    def _register_modules(self):
        self.register_module("subsystem1", "Subsystem 1 Description")
        self.register_module("subsystem2", "Subsystem 2 Description")
```

### Pattern 3: Preserving Custom Functionality

Always preserve original methods while adapting to new structure:

```python
class MigratedOrchestrator(SystemOrchestrator):
    def __init__(self, config=None):
        super().__init__(config)
        # Preserve original state
        self.custom_state = {}
        self.original_metrics = {}
    
    # Required new methods
    async def _initialize_modules(self) -> bool:
        # Initialize using new pattern
        # But call original initialization logic
        return await self._original_init_logic()
    
    # Preserve original methods
    async def orchestrate_processing(self, data):
        # Original processing logic preserved
        pass
```

## Step-by-Step Migration Process

### Step 1: Analyze the Existing Orchestrator

1. Identify the orchestrator's scope:
   - Single module → Use `ModuleOrchestrator`
   - Multiple modules → Use `SystemOrchestrator`
   - System-wide control → Use `MasterOrchestrator`

2. Document key features to preserve:
   - Custom processing methods
   - State management
   - Metrics collection
   - Plugin systems
   - Integration pathways

### Step 2: Create Configuration Class

Extend the appropriate configuration class:

```python
@dataclass
class MyOrchestratorConfig(SystemOrchestratorConfig):
    # Add custom configuration fields
    my_custom_field: str = "default"
    enable_feature_x: bool = True
```

### Step 3: Implement Required Methods

#### For ModuleOrchestrator:

```python
async def _create_component(self, component_name: str) -> Optional[Any]:
    """Create component instances"""
    
async def _custom_initialize(self) -> None:
    """Custom initialization logic"""
```

#### For SystemOrchestrator:

```python
def _register_modules(self) -> None:
    """Register all managed modules"""
    
async def _initialize_modules(self) -> bool:
    """Initialize all modules"""
    
async def _check_module_health(self, name: str) -> bool:
    """Module-specific health checks"""
```

### Step 4: Preserve Original Methods

Keep all original public methods and adapt internal calls:

```python
# Original method preserved
async def orchestrate_processing(self, input_data):
    # Check state using new pattern
    if self.state.value not in ["RUNNING", "STARTED"]:
        await self.start()
    
    # Original processing logic
    result = await self._original_processing(input_data)
    
    # Update new metrics
    self.metrics.operations_completed += 1
    
    return result
```

### Step 5: Update Health Monitoring

Adapt health checks to new pattern:

```python
async def _check_module_health(self, name: str) -> bool:
    # Use original health check logic
    if name == "my_module":
        return await self._original_health_check()
    
    # Fallback to base implementation
    return await super()._check_module_health(name)
```

## Code Examples

### Example 1: Minimal Module Orchestrator

```python
from lukhas.orchestration.module_orchestrator import ModuleOrchestrator, ModuleOrchestratorConfig

class SimpleOrchestrator(ModuleOrchestrator):
    async def _create_component(self, component_name: str):
        # Create your component
        return MyComponent(component_name)
    
    async def process_request(self, request):
        # Original processing preserved
        operation = {
            'type': 'process',
            'component': 'my_component',
            'data': request
        }
        return await self.process(operation)
```

### Example 2: System Orchestrator with Multiple Subsystems

```python
from lukhas.orchestration.system_orchestrator import SystemOrchestrator

class MultiSystemOrchestrator(SystemOrchestrator):
    def _register_modules(self):
        self.register_module("ai_engine", "Core AI Processing")
        self.register_module("memory_system", "Memory Management")
        self.register_module("ethics_guardian", "Ethics Oversight")
    
    async def _initialize_modules(self):
        # Initialize each subsystem
        self.ai_engine = AIEngine()
        await self.ai_engine.initialize()
        self.module_instances["ai_engine"] = self.ai_engine
        
        # Continue for other modules...
        return True
```

### Example 3: Preserving Plugin Systems

```python
class PluginAwareOrchestrator(SystemOrchestrator):
    def __init__(self, config=None):
        super().__init__(config)
        # Preserve plugin system
        self.plugins = {}
        self.auto_plugin_register()
    
    def auto_plugin_register(self, plugin_dir="plugins"):
        # Original plugin logic preserved
        for plugin in discover_plugins(plugin_dir):
            self.plugins[plugin.name] = plugin
```

## Testing Strategy

### 1. Unit Tests

Test each migrated component in isolation:

```python
async def test_initialization():
    orchestrator = MigratedOrchestrator()
    assert await orchestrator.initialize()
    assert orchestrator.state == OrchestratorState.INITIALIZED

async def test_original_functionality():
    orchestrator = MigratedOrchestrator()
    await orchestrator.initialize()
    await orchestrator.start()
    
    # Test original method still works
    result = await orchestrator.original_method(test_data)
    assert result['status'] == 'success'
```

### 2. Integration Tests

Test interaction with other system components:

```python
async def test_module_communication():
    orchestrator = MigratedSystemOrchestrator()
    await orchestrator.initialize()
    await orchestrator.start()
    
    # Test inter-module communication
    result = await orchestrator.route_cross_module_request(
        from_module="module_a",
        to_module="module_b",
        data=test_payload
    )
    assert result['delivered']
```

### 3. Regression Tests

Ensure no functionality is lost:

```python
class RegressionTestSuite:
    def __init__(self, old_orchestrator, new_orchestrator):
        self.old = old_orchestrator
        self.new = new_orchestrator
    
    async def run_comparison_tests(self):
        test_cases = load_test_cases()
        
        for test in test_cases:
            old_result = await self.old.process(test.input)
            new_result = await self.new.process(test.input)
            
            assert_equivalent_results(old_result, new_result)
```

## Common Pitfalls

### 1. State Management Conflicts

**Problem**: Original state variables conflict with base class state.

**Solution**: Prefix original state variables or integrate with base state:
```python
# Instead of self.state = "running"
self.processing_state = "running"  # Original state
# Use self.state for base class state
```

### 2. Initialization Order Issues

**Problem**: Components initialized in wrong order.

**Solution**: Use configuration to specify order:
```python
config = ModuleOrchestratorConfig(
    component_startup_order=["component_a", "component_b", "component_c"],
    component_shutdown_order=["component_c", "component_b", "component_a"]
)
```

### 3. Missing Health Checks

**Problem**: Components don't implement health checks.

**Solution**: Provide default health check implementation:
```python
async def _check_component_health(self, name: str) -> ComponentStatus:
    if hasattr(self.component_instances[name], 'health_check'):
        return await self.component_instances[name].health_check()
    # Default: assume healthy if exists
    return ComponentStatus.HEALTHY if name in self.component_instances else ComponentStatus.UNKNOWN
```

### 4. Metrics Integration

**Problem**: Original metrics not integrated with base metrics.

**Solution**: Merge metrics appropriately:
```python
def get_comprehensive_metrics(self):
    return {
        **self.metrics.__dict__,  # Base metrics
        **self.original_metrics    # Original metrics
    }
```

## Rollback Plan

### 1. Parallel Running

Run both orchestrators in parallel during transition:

```python
class TransitionOrchestrator:
    def __init__(self):
        self.old_orchestrator = OldOrchestrator()
        self.new_orchestrator = NewOrchestrator()
        self.use_new = False  # Feature flag
    
    async def process(self, data):
        if self.use_new:
            return await self.new_orchestrator.process(data)
        return await self.old_orchestrator.process(data)
```

### 2. Feature Flags

Use configuration to control rollout:

```python
if config.get('use_new_orchestrator', False):
    orchestrator = MigratedOrchestrator()
else:
    orchestrator = LegacyOrchestrator()
```

### 3. Data Migration

Ensure state can be transferred:

```python
async def migrate_state(old_orch, new_orch):
    # Transfer runtime state
    state_data = await old_orch.export_state()
    await new_orch.import_state(state_data)
    
    # Verify state transfer
    assert await new_orch.verify_state()
```

## Best Practices

1. **Incremental Migration**: Migrate one orchestrator at a time
2. **Preserve APIs**: Keep public method signatures unchanged
3. **Document Changes**: Add migration notes in docstrings
4. **Test Thoroughly**: Run full regression test suite
5. **Monitor Metrics**: Compare performance before/after
6. **Keep Backups**: Maintain original code during transition
7. **Communication**: Notify teams about migration status

## Support

For migration assistance:
- Review examples in `/lukhas/orchestration/migrated/`
- Check test suites in `/tests/orchestration/`
- Consult architecture team for complex migrations

---

**Remember**: The goal is to modernize the infrastructure while preserving all existing functionality. When in doubt, preserve the original behavior.