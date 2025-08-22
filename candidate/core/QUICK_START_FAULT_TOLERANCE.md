═══════════════════════════════════════════════════════════════════════════════
║ 🚀 QUICK START GUIDE - FAULT TOLERANCE & RESILIENCE
║ Get Started with Self-Healing Actor Systems in 5 Minutes
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Documentation: Quick Start Guide
║ Path: lukhas/core/
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Author: Jules
╚═══════════════════════════════════════════════════════════════════════════════

# Quick Start: Fault Tolerance & Resilience

This guide will get you up and running with LUKHAS AI's fault tolerance architecture in 5 minutes.

## 📋 Prerequisites

```bash
# Ensure you have LUKHAS AI installed
pip install -e .

# Required imports
import asyncio
from lukhas.core.actor_system import get_global_actor_system
from lukhas.core.supervision import RootSupervisor, SupervisorActor, SupervisionStrategy
from lukhas.core.observability_steering import ObservabilityCollector, SteeringController
from lukhas.core.event_replay_snapshot import EventStore, SnapshotStore, ReplayController
from lukhas.core.circuit_breaker import CascadePreventionSystem
```

## 🏃 1. Basic Supervised Actor System (2 minutes)

```python
async def basic_supervision():
    # Get actor system
    system = await get_global_actor_system()
    
    # Create root supervisor
    root = await system.create_actor(RootSupervisor, "root-supervisor")
    
    # Create a supervised worker
    worker = await root.ask("create_child", {
        "child_class": YourWorkerActor,
        "child_id": "worker-001"
    })
    
    # Worker is now protected - will auto-restart on failure
    result = await worker.ask("do_work", {"task": "important"})
```

## 🔍 2. Add Observability (1 minute)

```python
async def observable_system():
    system = await get_global_actor_system()
    
    # Start observability
    collector = ObservabilityCollector()
    collector.start()
    
    # Create observable actor
    from lukhas.core.observability_steering import ObservableActor
    
    class MyObservableActor(ObservableActor):
        def __init__(self, actor_id: str):
            super().__init__(actor_id, collector)
            
        async def handle_work(self, message):
            # Automatically tracked!
            return {"status": "completed"}
    
    actor = await system.create_actor(MyObservableActor, "observable-001")
    
    # Check system health
    overview = collector.get_system_overview()
    print(f"System health: {overview['health']}")
```

## 🛡️ 3. Enable Circuit Breakers (1 minute)

```python
async def protected_system():
    system = await get_global_actor_system()
    collector = ObservabilityCollector()
    collector.start()
    
    # Create cascade prevention
    cascade_prevention = CascadePreventionSystem(system, collector)
    await cascade_prevention.start()
    
    # All calls are now protected
    actor_ref = await system.create_actor(YourActor, "protected-001")
    
    try:
        # Automatically protected with circuit breaker
        result = await cascade_prevention.protected_call(
            actor_ref,
            "risky_operation",
            {"data": "important"},
            timeout=30.0
        )
    except CircuitBreakerOpen:
        print("Circuit breaker is protecting the system!")
```

## 🕰️ 4. Add Time-Travel Debugging (1 minute)

```python
async def debuggable_system():
    system = await get_global_actor_system()
    
    # Setup event sourcing
    event_store = EventStore()
    snapshot_store = SnapshotStore()
    await event_store.start()
    
    # Create event-sourced actor
    from lukhas.core.event_replay_snapshot import EventSourcedActor
    
    class DebuggableActor(EventSourcedActor):
        def __init__(self, actor_id: str):
            super().__init__(actor_id, event_store, snapshot_store)
            self.state = "initial"
            
        async def handle_update(self, message):
            old_state = self.state
            self.state = message.payload["new_state"]
            
            # Automatically recorded!
            await self.record_state_change(
                "state_update", old_state, self.state
            )
    
    actor = await system.create_actor(DebuggableActor, "debuggable-001")
    
    # Create replay controller
    replay = ReplayController(system, event_store, snapshot_store)
    
    # Mark checkpoint
    checkpoint = await replay.create_debugging_checkpoint("Before changes")
```

## 🎯 5. Complete Example: Resilient Service

```python
async def complete_resilient_service():
    """A complete example combining all features"""
    
    # 1. Initialize all components
    system = await get_global_actor_system()
    event_store = EventStore()
    snapshot_store = SnapshotStore()
    collector = ObservabilityCollector()
    
    await event_store.start()
    collector.start()
    
    cascade_prevention = CascadePreventionSystem(system, collector)
    await cascade_prevention.start()
    
    # 2. Create root supervisor
    root = await system.create_actor(RootSupervisor, "root-supervisor")
    
    # 3. Define resilient actor
    from lukhas.core.observability_steering import ObservableActor
    from lukhas.core.event_replay_snapshot import EventSourcedActor
    
    class ResilientService(ObservableActor, EventSourcedActor):
        def __init__(self, actor_id: str):
            ObservableActor.__init__(self, actor_id, collector)
            EventSourcedActor.__init__(self, actor_id, event_store, snapshot_store)
            self.register_handler("process", self._handle_process)
            self.processed_count = 0
            
        async def _handle_process(self, message):
            # Record state change
            await self.record_state_change(
                "processing",
                self.processed_count,
                self.processed_count + 1
            )
            
            # Simulate work
            await asyncio.sleep(0.1)
            self.processed_count += 1
            
            return {"count": self.processed_count}
        
        def get_custom_metrics(self):
            return {"processed": self.processed_count}
    
    # 4. Create supervised service
    service = await root.ask("create_child", {
        "child_class": ResilientService,
        "child_id": "resilient-service-001"
    })
    
    # 5. Use with protection
    for i in range(10):
        try:
            result = await cascade_prevention.protected_call(
                service,
                "process",
                {"item": f"task-{i}"},
                timeout=5.0
            )
            print(f"Processed: {result}")
        except Exception as e:
            print(f"Failed: {e}")
    
    # 6. Check system status
    status = cascade_prevention.get_system_status()
    print(f"\nSystem Status:")
    print(f"  Health Score: {status['health_score']:.2%}")
    print(f"  Emergency Mode: {status['emergency_mode']}")
    print(f"  Quarantined Actors: {len(status['quarantined_actors'])}")
    
    # 7. Interactive debugging
    steering = SteeringController(system)
    dashboard = ObservabilityDashboard(collector, steering)
    
    graph = await dashboard.get_actor_graph()
    print(f"\nActor Network: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    
    # 8. Create checkpoint for debugging
    replay = ReplayController(system, event_store, snapshot_store)
    checkpoint = await replay.create_debugging_checkpoint("End of demo")
    print(f"\nCheckpoint created: {checkpoint}")
    
    # Cleanup
    await cascade_prevention.stop()
    await event_store.stop()
    collector.stop()

# Run the complete example
if __name__ == "__main__":
    asyncio.run(complete_resilient_service())
```

## 💡 Best Practices

### 1. **Always Start Services in Order**
```python
# Correct order
await event_store.start()
collector.start()
await cascade_prevention.start()
```

### 2. **Use Supervision for Critical Actors**
```python
# Don't create actors directly for critical services
# ❌ actor = await system.create_actor(CriticalActor, "critical-001")

# ✅ Create under supervision
actor = await supervisor.ask("create_child", {
    "child_class": CriticalActor,
    "child_id": "critical-001"
})
```

### 3. **Protected Calls for External Operations**
```python
# Always use cascade prevention for risky operations
result = await cascade_prevention.protected_call(
    actor_ref,
    "external_api_call",
    payload,
    timeout=30.0
)
```

### 4. **Record Important State Changes**
```python
# In EventSourcedActor
await self.record_state_change(
    "operation_type",
    old_value,
    new_value,
    metadata={"reason": "user_request"}
)
```

### 5. **Monitor System Health**
```python
# Regular health checks
status = cascade_prevention.get_system_status()
if status['health_score'] < 0.5:
    logger.warning("System health degraded!")
```

## 🚨 Common Pitfalls

1. **Forgetting to Start Services**
   ```python
   # Will fail silently!
   collector = ObservabilityCollector()
   # ❌ Forgot: collector.start()
   ```

2. **Creating Actors Outside Supervision**
   ```python
   # Unprotected actor
   actor = await system.create_actor(MyActor, "unprotected")
   ```

3. **Not Handling Circuit Breaker Exceptions**
   ```python
   try:
       result = await protected_call(...)
   except CircuitBreakerOpen:
       # Use fallback
       result = await fallback_operation()
   ```

## 🔗 Next Steps

1. Read the [Fault Tolerance Architecture](./FAULT_TOLERANCE_ARCHITECTURE.md) for deep understanding
2. Check the [API Reference](./API_REFERENCE.md) for all available options
3. See [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) for module overview
4. Explore example code in each module's demo functions

## 🆘 Getting Help

- Check module docstrings: `help(SupervisorActor)`
- Run demos: `python -m lukhas.core.supervision`
- Enable debug logging: `logging.getLogger('lukhas.core').setLevel(logging.DEBUG)`

═══════════════════════════════════════════════════════════════════════════════
║ Happy building self-healing systems! 🚀
╚═══════════════════════════════════════════════════════════════════════════════