═══════════════════════════════════════════════════════════════════════════════
║ 📖 API REFERENCE - FAULT TOLERANCE & RESILIENCE MODULES
║ Complete API Documentation for Supervision, Observability, Events & Circuits
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Documentation: API Reference
║ Path: lukhas/core/
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Author: Jules
╠═══════════════════════════════════════════════════════════════════════════════
║ TABLE OF CONTENTS
╠═══════════════════════════════════════════════════════════════════════════════
║ 1. Supervision Module (supervision.py)
║ 2. Observability & Steering Module (observability_steering.py)
║ 3. Event Replay & Snapshot Module (event_replay_snapshot.py)
║ 4. Circuit Breaker Module (circuit_breaker.py)
╚═══════════════════════════════════════════════════════════════════════════════

# API Reference - Fault Tolerance & Resilience Modules

## 1. Supervision Module (`supervision.py`)

### Enums

#### `SupervisionDirective`
Directives that a supervisor can return when handling failures.

```python
class SupervisionDirective(Enum):
    RESUME = "resume"      # Resume the actor, keeping its state
    RESTART = "restart"    # Restart the actor, clearing its state
    STOP = "stop"         # Stop the actor permanently
    ESCALATE = "escalate" # Escalate to the parent supervisor
```

#### `RestartPolicy`
When to restart child actors.

```python
class RestartPolicy(Enum):
    NEVER = "never"              # Never restart
    ALWAYS = "always"            # Always restart on failure
    ON_FAILURE = "on_failure"    # Restart only on failure
    ON_STOP = "on_stop"         # Restart even on normal stop
```

### Classes

#### `SupervisionStrategy`
Configuration for supervision behavior.

```python
@dataclass
class SupervisionStrategy:
    max_failures: int = 3
    within_time_window: float = 60.0  # seconds
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    restart_delay: float = 0.1  # seconds
    backoff_multiplier: float = 2.0
    max_restart_delay: float = 30.0

    def calculate_restart_delay(self, failure_count: int) -> float:
        """Calculate delay before restart using exponential backoff"""
```

**Methods:**
- `calculate_restart_delay(failure_count: int) -> float`: Returns delay in seconds

#### `SupervisorActor`
Enhanced actor with supervision capabilities.

```python
class SupervisorActor(Actor):
    def __init__(self,
                 actor_id: str,
                 supervision_strategy: Optional[SupervisionStrategy] = None,
                 supervision_decider: Optional[SupervisionDecider] = None)
```

**Methods:**
- `create_child(child_class: type, child_id: str, *args, **kwargs) -> ActorRef`
- `stop_all_children() -> None`
- `get_supervision_stats() -> Dict[str, Any]`

**Message Handlers:**
- `child_failed`: Handle child actor failure
- `child_terminated`: Handle normal child termination
- `supervise_child`: Take supervision of existing actor

#### `RootSupervisor`
Special root supervisor for the entire actor system.

```python
class RootSupervisor(SupervisorActor):
    def __init__(self)
```

**Additional Message Handlers:**
- `system_shutdown`: Graceful system shutdown
- `emergency_stop`: Emergency stop all actors

### Strategy Classes

#### `OneForOneStrategy`
Only the failed child is affected.

```python
supervisor = SupervisorActor(
    "my-supervisor",
    supervision_decider=OneForOneStrategy(strategy)
)
```

#### `AllForOneStrategy`
If one child fails, stop all children.

#### `RestForOneStrategy`
Stop the failed child and all children started after it.

```python
strategy = RestForOneStrategy(supervision_strategy)
strategy.register_child("child-1")  # Track start order
affected = strategy.get_affected_children("failed-child")
```

---

## 2. Observability & Steering Module (`observability_steering.py`)

### Enums

#### `ObservabilityLevel`
```python
class ObservabilityLevel(Enum):
    BASIC = "basic"              # Basic metrics only
    DETAILED = "detailed"        # Detailed metrics and traces
    FULL = "full"               # Complete system state capture
    INTERACTIVE = "interactive"  # Allow system steering
```

#### `SystemHealth`
```python
class SystemHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
```

### Data Classes

#### `ActorSnapshot`
Point-in-time snapshot of an actor's state.

```python
@dataclass
class ActorSnapshot:
    actor_id: str
    timestamp: float
    state: str
    mailbox_size: int
    message_rate: float
    error_rate: float
    memory_usage: int
    custom_metrics: Dict[str, Any]
    relationships: List[str]
```

#### `MessageFlow`
Represents message flow between actors.

```python
@dataclass
class MessageFlow:
    source: str
    destination: str
    message_type: str
    timestamp: float
    correlation_id: str
    latency: Optional[float] = None
    payload_size: int = 0
```

#### `EmergentPattern`
Detected emergent behavior pattern.

```python
@dataclass
class EmergentPattern:
    pattern_id: str
    pattern_type: str
    involved_actors: List[str]
    confidence: float
    description: str
    first_detected: float
    last_observed: float
    occurrence_count: int
```

### Classes

#### `ObservabilityCollector`
Collects and aggregates observability data.

```python
class ObservabilityCollector:
    def __init__(self,
                 retention_period: float = 3600.0,
                 aggregation_interval: float = 5.0)
```

**Methods:**
- `start() -> None`
- `stop() -> None`
- `record_actor_snapshot(snapshot: ActorSnapshot) -> None`
- `record_message_flow(flow: MessageFlow) -> None`
- `record_system_event(event_type: str, event_data: Dict[str, Any]) -> None`
- `register_pattern_detector(detector: Callable) -> None`
- `get_system_overview() -> Dict[str, Any]`

#### `SteeringController`
Allows interactive steering of the actor system.

```python
class SteeringController:
    def __init__(self, actor_system: ActorSystem)
```

**Methods:**
- `pause_actor(actor_id: str) -> bool`
- `resume_actor(actor_id: str) -> bool`
- `inject_message(source: str, destination: str, message_type: str, payload: Dict[str, Any]) -> bool`
- `modify_actor_state(actor_id: str, state_updates: Dict[str, Any]) -> bool`
- `apply_steering_policy(policy_name: str, *args, **kwargs) -> Any`
- `register_steering_policy(name: str, policy: Callable) -> None`

#### `ObservableActor`
Enhanced actor with built-in observability.

```python
class ObservableActor(Actor):
    def __init__(self, actor_id: str, collector: Optional[ObservabilityCollector] = None)

    def get_custom_metrics(self) -> Dict[str, Any]:
        """Override to provide custom metrics"""
        return {}
```

#### `ObservabilityDashboard`
Interactive dashboard for system observation.

```python
class ObservabilityDashboard:
    def __init__(self,
                 collector: ObservabilityCollector,
                 steering: SteeringController)
```

**Methods:**
- `get_actor_graph() -> Dict[str, Any]`
- `get_time_series_data(actor_id: str, metric: str, duration: float = 300.0) -> List[Tuple[float, float]]`
- `get_pattern_summary() -> Dict[str, Any]`
- `register_visualization(name: str, viz_func: Callable) -> None`

---

## 3. Event Replay & Snapshot Module (`event_replay_snapshot.py`)

### Enums

#### `EventType`
```python
class EventType(Enum):
    ACTOR_CREATED = "actor_created"
    ACTOR_DESTROYED = "actor_destroyed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_PROCESSED = "message_processed"
    STATE_CHANGED = "state_changed"
    SNAPSHOT_TAKEN = "snapshot_taken"
    FAILURE_OCCURRED = "failure_occurred"
```

### Data Classes

#### `Event`
Immutable event record.

```python
@dataclass
class Event:
    event_id: str
    event_type: EventType
    actor_id: str
    timestamp: float
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    def to_json(self) -> str

    @classmethod
    def from_json(cls, json_str: str) -> 'Event'
```

#### `ActorStateSnapshot`
Snapshot of an actor's complete state.

```python
@dataclass
class ActorStateSnapshot:
    actor_id: str
    actor_class: str
    timestamp: float
    event_id: str
    state_data: bytes
    state_hash: str
    metadata: Dict[str, Any]

    @classmethod
    def create_from_actor(cls, actor: Actor, event_id: str) -> 'ActorStateSnapshot'

    def restore_to_actor(self, actor: Actor) -> None
```

### Classes

#### `EventStore`
Persistent storage for events with replay capabilities.

```python
class EventStore:
    def __init__(self,
                 storage_path: str = "./event_store",
                 max_memory_events: int = 10000,
                 compression: bool = True)
```

**Methods:**
- `start() -> None`
- `stop() -> None`
- `append_event(event: Event) -> None`
- `get_events_for_actor(actor_id: str, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[Event]`
- `get_events_by_correlation(correlation_id: str) -> List[Event]`
- `replay_events(events: List[Event], speed: float = 1.0, callback: Optional[Callable] = None) -> int`

#### `SnapshotStore`
Storage for actor state snapshots.

```python
class SnapshotStore:
    def __init__(self, storage_path: str = "./snapshots")
```

**Methods:**
- `save_snapshot(snapshot: ActorStateSnapshot) -> None`
- `load_snapshot(actor_id: str, timestamp: Optional[float] = None) -> Optional[ActorStateSnapshot]`
- `delete_old_snapshots(retention_days: int = 7) -> None`

#### `EventSourcedActor`
Actor that automatically records events and supports replay.

```python
class EventSourcedActor(Actor):
    def __init__(self,
                 actor_id: str,
                 event_store: Optional[EventStore] = None,
                 snapshot_store: Optional[SnapshotStore] = None)
```

**Methods:**
- `record_state_change(change_type: str, old_value: Any, new_value: Any, metadata: Optional[Dict[str, Any]] = None) -> None`
- `take_snapshot(event_id: Optional[str] = None) -> None`
- `restore_from_snapshot(timestamp: Optional[float] = None) -> bool`
- `replay_history(start_time: Optional[float] = None, end_time: Optional[float] = None, speed: float = 1.0) -> None`

#### `ReplayController`
Controller for system-wide replay operations.

```python
class ReplayController:
    def __init__(self,
                 actor_system: ActorSystem,
                 event_store: EventStore,
                 snapshot_store: SnapshotStore)
```

**Methods:**
- `replay_scenario(correlation_id: str, speed: float = 1.0, isolated: bool = True) -> Dict[str, Any]`
- `create_debugging_checkpoint(description: str) -> str`

---

## 4. Circuit Breaker Module (`circuit_breaker.py`)

### Enums

#### `CircuitState`
```python
class CircuitState(Enum):
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Blocking calls
    HALF_OPEN = "half_open"    # Testing recovery
    FORCED_OPEN = "forced_open" # Manually opened
```

#### `FailureType`
```python
class FailureType(Enum):
    TIMEOUT = "timeout"
    ERROR = "error"
    REJECTION = "rejection"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    ANOMALY_DETECTED = "anomaly_detected"
    CONSENSUS_FAILURE = "consensus_failure"
```

### Data Classes

#### `FailureRecord`
Record of a failure event.

```python
@dataclass
class FailureRecord:
    timestamp: float
    failure_type: FailureType
    actor_id: str
    error_message: str
    correlation_id: Optional[str] = None
    propagation_path: List[str] = field(default_factory=list)
    severity: float = 1.0  # 0-1 scale
```

#### `HealthCheck`
Health check configuration.

```python
@dataclass
class HealthCheck:
    check_function: Callable
    interval: float = 30.0
    timeout: float = 5.0
    failure_threshold: int = 3
    success_threshold: int = 2
```

### Classes

#### `AdvancedCircuitBreaker`
Advanced circuit breaker with multiple failure types.

```python
class AdvancedCircuitBreaker:
    def __init__(self,
                 name: str,
                 failure_threshold: int = 5,
                 success_threshold: int = 3,
                 timeout: float = 60.0,
                 half_open_max_calls: int = 3,
                 error_rate_threshold: float = 0.5,
                 slow_call_duration: float = 1.0,
                 slow_call_rate_threshold: float = 0.5,
                 minimum_number_of_calls: int = 10)
```

**Methods:**
- `call(func: Callable, *args, **kwargs) -> Any`
- `async_call(func: Callable, *args, **kwargs) -> Any`
- `force_open() -> None`
- `force_close() -> None`
- `add_health_check(health_check: HealthCheck) -> None`
- `run_health_checks() -> Dict[str, bool]`
- `get_metrics() -> Dict[str, Any]`

**Properties:**
- `state: CircuitState`
- `state_change_listeners: List[Callable]`

#### `AnomalyDetector`
Detects anomalous behavior in actors.

```python
class AnomalyDetector:
    def __init__(self,
                 window_size: int = 100,
                 z_score_threshold: float = 3.0,
                 isolation_forest_contamination: float = 0.1)
```

**Methods:**
- `record_metric(actor_id: str, metric_name: str, value: float) -> None`
- `detect_anomalies(actor_id: str) -> List[Tuple[str, float]]`
- `get_anomaly_score(actor_id: str) -> float`  # Returns 0-1

#### `ErrorPropagationTracker`
Tracks error propagation paths.

```python
class ErrorPropagationTracker:
    def __init__(self, max_propagation_depth: int = 5)
```

**Methods:**
- `record_failure(failure: FailureRecord) -> None`
- `is_actor_infected(actor_id: str) -> bool`
- `quarantine_actor(actor_id: str) -> None`
- `is_quarantined(actor_id: str) -> bool`
- `analyze_propagation_patterns() -> Dict[str, Any]`

#### `ConsensusValidator`
Validates consensus among actors.

```python
class ConsensusValidator:
    def __init__(self,
                 quorum_size: int = 3,
                 agreement_threshold: float = 0.7)
```

**Methods:**
- `validate_consensus(actor_refs: List[ActorRef], query: str, timeout: float = 5.0) -> Tuple[bool, Any]`

#### `CascadePreventionSystem`
Main system for preventing cascading failures.

```python
class CascadePreventionSystem:
    def __init__(self,
                 actor_system: ActorSystem,
                 observability: Optional[ObservabilityCollector] = None)
```

**Methods:**
- `start() -> None`
- `stop() -> None`
- `get_or_create_circuit_breaker(actor_id: str, **kwargs) -> AdvancedCircuitBreaker`
- `protected_call(actor_ref: ActorRef, message_type: str, payload: Dict[str, Any], timeout: float = 30.0) -> Any`
- `validate_with_consensus(actor_refs: List[ActorRef], query: str) -> Tuple[bool, Any]`
- `report_failure(failure: FailureRecord) -> None`
- `get_system_status() -> Dict[str, Any]`

**Properties:**
- `system_health_score: float`  # 0-1
- `emergency_mode: bool`

### Exceptions

```python
class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""

class ActorQuarantined(Exception):
    """Raised when trying to communicate with a quarantined actor"""

class AnomalyDetected(Exception):
    """Raised when anomalous behavior is detected"""
```

---

## Usage Examples

### Complete System Setup

```python
# Initialize all components
async def setup_resilient_system():
    # Core actor system
    system = await get_global_actor_system()

    # Event sourcing
    event_store = EventStore()
    snapshot_store = SnapshotStore()
    await event_store.start()

    # Observability
    collector = ObservabilityCollector()
    collector.start()

    # Cascade prevention
    cascade_prevention = CascadePreventionSystem(system, collector)
    await cascade_prevention.start()

    # Root supervisor
    root = await system.create_actor(RootSupervisor, "root-supervisor")

    # Steering and dashboard
    steering = SteeringController(system)
    dashboard = ObservabilityDashboard(collector, steering)

    # Replay controller
    replay = ReplayController(system, event_store, snapshot_store)

    return locals()
```

### Creating a Fully Protected Actor

```python
class ProtectedActor(ObservableActor, EventSourcedActor):
    def __init__(self, actor_id: str, components):
        ObservableActor.__init__(self, actor_id, components['collector'])
        EventSourcedActor.__init__(
            self, actor_id,
            components['event_store'],
            components['snapshot_store']
        )
        self.cascade_prevention = components['cascade_prevention']

    async def protected_operation(self, data):
        # Record state change
        await self.record_state_change("op_start", self.state, "processing")

        # Use circuit breaker
        cb = self.cascade_prevention.get_or_create_circuit_breaker(self.actor_id)
        result = await cb.async_call(self._do_work, data)

        # Record completion
        await self.record_state_change("op_complete", "processing", self.state)

        return result
```

═══════════════════════════════════════════════════════════════════════════════
║ End of API Reference
╚═══════════════════════════════════════════════════════════════════════════════
