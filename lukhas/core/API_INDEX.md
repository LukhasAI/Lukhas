# 🔌 LUKHAS Core API Index

**Generated:** July 27, 2025  
**Purpose:** Unified API reference for all core modules to prevent method name drift

## 📋 Table of Contents

1. [Actor System APIs](#actor-system-apis)
2. [Event Sourcing APIs](#event-sourcing-apis)
3. [Communication APIs](#communication-apis)
4. [Distributed Tracing APIs](#distributed-tracing-apis)
5. [State Management APIs](#state-management-apis)
6. [Colony System APIs](#colony-system-apis)

---

## Actor System APIs

### ActorRef Methods
```python
# Message passing
async def tell(message_type: str, payload: Dict, correlation_id: Optional[str] = None) -> bool
async def ask(message_type: str, payload: Dict, timeout: float = 5.0) -> Any

# Note: NO send_message() method - use tell() instead
```

### Actor Base Class Methods
```python
# Lifecycle
async def start(actor_system: ActorSystem) -> None
async def stop() -> None
async def pre_start() -> None
async def pre_stop() -> None
async def post_stop() -> None

# Message handling
def register_handler(message_type: str, handler: Callable) -> None
def become(new_handlers: Dict[str, Callable]) -> None
async def send_message(message: ActorMessage) -> bool  # Internal use only

# Child management
async def create_child(child_class: type, child_id: str, *args, **kwargs) -> ActorRef
```

### ActorSystem Methods
```python
# Actor management
async def create_actor(actor_class: type, actor_id: str, *args, **kwargs) -> ActorRef
async def stop_actor(actor_id: str) -> None
async def restart_actor(actor_id: str, reason: Exception) -> None

# References
def get_actor_ref(actor_id: str) -> Optional[ActorRef]
def get_actor(actor_id: str) -> Optional[Actor]  # Internal use

# Message delivery
async def deliver_message(message: ActorMessage) -> bool

# System control
async def start() -> None
async def stop() -> None
def get_system_stats() -> Dict[str, Any]
```

---

## Event Sourcing APIs

### EventStore Methods
```python
# Event management
def append(event: Event) -> None
def get_events(aggregate_id: str, start_version: int = 0, end_version: Optional[int] = None) -> List[Event]
def get_events_by_type(event_type: str, limit: int = 100) -> List[Event]

# Temporal queries
def get_events_in_time_range(start_time: float, end_time: float, aggregate_id: Optional[str] = None) -> List[Event]

# Aggregate support
def load_aggregate(aggregate_id: str, aggregate_class: type) -> Any
def save_aggregate(aggregate: Any) -> None
```

### Event Class
```python
@dataclass
class Event:
    event_id: str
    event_type: str
    aggregate_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: float
    version: int
    correlation_id: Optional[str] = None
```

---

## Communication APIs

### EfficientCommunicationFabric Methods
```python
# Message sending
async def send_message(recipient: str, message: Any, priority: MessagePriority = MessagePriority.NORMAL) -> bool
async def broadcast(message: Any, topic: str = "general") -> int

# P2P operations
async def send_p2p(peer_id: str, data: bytes) -> bool
async def send_large_data(recipient: str, data: bytes, chunk_size: int = 1024*1024) -> bool  # TODO: Implement

# Event bus
def subscribe(topic: str, handler: Callable) -> None
def unsubscribe(topic: str, handler: Callable) -> None

# Statistics
def get_statistics() -> Dict[str, Any]
# Note: Should include 'total_messages' in stats
```

### Message Priority Enum
```python
class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3
```

---

## Distributed Tracing APIs

### Tracer Methods
```python
# Span management
def start_span(operation_name: str, parent_span: Optional[Span] = None) -> Span
def finish_span(span: Span) -> None

# Context propagation
def inject(span_context: SpanContext, carrier: Dict) -> None
def extract(carrier: Dict) -> Optional[SpanContext]

# Correlation
def set_correlation_id(correlation_id: str) -> None
def get_correlation_id() -> Optional[str]
```

### Span Methods
```python
# Tagging
def set_tag(key: str, value: Any) -> Span
def log(event: str, payload: Optional[Dict] = None) -> Span

# Lifecycle
def finish() -> None
```

---

## State Management APIs

### TieredStateManager Methods
```python
# State operations
async def get_state(aggregate_id: str, state_type: StateType, consistency: ConsistencyLevel = ConsistencyLevel.EVENTUAL) -> Dict[str, Any]
async def update_state(aggregate_id: str, updates: Dict[str, Any], state_type: StateType) -> bool

# Snapshots
async def create_snapshot(aggregate_id: str) -> StateSnapshot
async def load_from_snapshot(aggregate_id: str) -> Dict[str, Any]

# Actor synchronization
async def sync_actor_state(actor: Any, sync_direction: str = "bidirectional") -> None

# Replication
def subscribe_to_replicated_state(aggregate_id: str, callback: Callable) -> None
def unsubscribe_from_replicated_state(aggregate_id: str, callback: Callable) -> None
```

---

## Colony System APIs

### BaseColony Methods
```python
# Lifecycle
async def start() -> None
async def stop() -> None

# Task execution
async def execute_task(task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]

# Worker management
async def scale_workers(num_workers: int) -> None

# Status
def get_status() -> Dict[str, Any]
```

### DistributedAISystem Methods
```python
# Colony management
async def create_colony(colony_id: str, colony_class: type, **kwargs) -> BaseColony
async def remove_colony(colony_id: str) -> None

# Task distribution
async def execute_distributed_task(task_data: Dict[str, Any]) -> Dict[str, Any]

# System control
async def start() -> None
async def stop() -> None
async def get_system_statistics() -> Dict[str, Any]
```

---

## 🔧 Common Patterns

### Error Handling
```python
# All async methods should handle these exceptions:
- asyncio.TimeoutError: For time-bounded operations
- RuntimeError: For system state errors
- ValueError: For invalid parameters
```

### Resource Management
```python
# All components should implement:
async def __aenter__()  # Context manager entry
async def __aexit__()   # Context manager exit
```

### Metrics Collection
```python
# All major components should provide:
def get_stats() -> Dict[str, Any]  # Component-specific metrics
def get_metrics() -> Dict[str, float]  # Numeric metrics only
```

---

## ⚠️ Breaking Changes from Tests

### Actor System
- ❌ `actor_ref.send_message()` → ✅ `actor_ref.tell()`
- ❌ `actor.handle_message()` → ✅ Register handlers with `actor.register_handler()`

### Communication Fabric
- ❌ Missing `total_messages` in stats → ✅ Add to statistics dict
- ❌ Missing `send_large_data()` → ✅ Implement chunked P2P transfer

### Integrated System
- ❌ `DistributedAIAgent.process_task()` → ✅ Use `execute_task()` on colonies

---

## 📝 Migration Guide

### For Test Writers
```python
# Old test pattern
response = await actor_ref.send_message("task", data)

# New test pattern
response = await actor_ref.tell("task", data)
# or for request-response:
response = await actor_ref.ask("task", data)
```

### For System Users
```python
# Old pattern
agent = DistributedAIAgent()
result = await agent.process_task(task_data)

# New pattern
system = DistributedAISystem()
colony = await system.create_colony("worker", WorkerColony)
result = await system.execute_distributed_task(task_data)
```

---

*This index should be updated whenever APIs change to maintain consistency across the codebase.*