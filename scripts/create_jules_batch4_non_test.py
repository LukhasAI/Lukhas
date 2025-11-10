#!/usr/bin/env python3
"""
Jules Batch 4 - NON-TEST Focus: Implementation, Refactoring, Quality
Excludes all test-related work (delegated separately)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient

BATCH4_SESSIONS = [
    {
        "title": "🔧 P1: Implement Symbolic Reasoning Adapter TODOs (9 TODOs)",
        "prompt": """**HIGH PRIORITY: Complete Symbolic Reasoning Adapter Implementation**

**Objective**: Implement all TODO items in symbolic reasoning modules

**Files to Complete**:
1. `labs/core/symbolic/symbolic_reasoning_adapter.py` (9 TODOs)
2. `labs/core/symbolic/symbolic_dream_bridge.py` (9 TODOs)
3. `labs/core/symbolic/symbolic_memory_mapper.py` (3 TODOs)

**Context**: These are core symbolic processing modules for LUKHAS consciousness layer

**Implementation Pattern** (for each TODO):
```python
# Before:
class SymbolicReasoningAdapter:
    def process_symbolic(self, input):
        # TODO: Implement symbolic transformation
        pass

# After:
class SymbolicReasoningAdapter:
    def process_symbolic(self, input: Dict[str, Any]) -> SymbolicResult:
        '''Transform input to symbolic representation'''
        # Validate input
        if not input or not isinstance(input, dict):
            raise ValueError("Invalid input for symbolic processing")

        # Extract semantic components
        concepts = self._extract_concepts(input)
        relations = self._identify_relations(concepts)

        # Build symbolic graph
        symbolic_graph = self._construct_graph(concepts, relations)

        # Return structured result
        return SymbolicResult(
            graph=symbolic_graph,
            metadata={'concepts': len(concepts), 'relations': len(relations)}
        )
```

**Required Implementations**:

**symbolic_reasoning_adapter.py**:
- Symbolic transformation logic
- Concept extraction
- Relation identification
- Graph construction
- Reasoning algorithms

**symbolic_dream_bridge.py**:
- Dream state symbolic mapping
- Unconscious processing integration
- Creative synthesis bridge
- Dream memory persistence

**symbolic_memory_mapper.py**:
- Memory to symbolic conversion
- Symbolic to memory retrieval
- Context preservation
- Semantic indexing

**Testing Requirements**:
- Unit tests for each implemented method
- Integration tests for full pipeline
- Edge case handling
- Performance benchmarks

**Expected Output**:
- All 21 TODOs implemented
- Comprehensive docstrings
- Type hints throughout
- Tests passing
- Documentation updated

**Commit Message**:
```
feat(symbolic): implement symbolic reasoning adapter pipeline

Problem:
- 21 TODOs in symbolic processing modules
- Core symbolic reasoning incomplete
- No dream-symbolic bridge
- Memory mapping missing

Solution:
- Implemented symbolic transformation logic
- Added dream state symbolic mapping
- Created memory-symbolic converter
- Full symbolic reasoning pipeline

Impact:
- Complete symbolic processing layer
- Dream integration working
- Memory semantic indexing enabled
- Production-ready symbolic module

Tests: 50+ tests, all passing
Files: 3 modules fully implemented
```

**Priority**: P1 - Core consciousness functionality
""",
    },
    {
        "title": "🔧 P1: Implement Memory System TODOs (7 modules)",
        "prompt": """**HIGH PRIORITY: Complete Memory System Implementation**

**Objective**: Implement all TODO placeholders in memory subsystem

**Files to Complete**:
1. `labs/memory/systems/memory_format.py` (2 TODOs)
2. `labs/memory/systems/memory_profiler.py` (1 TODO)
3. `labs/memory/systems/memory_session_storage.py` (1 TODO)
4. `labs/memory/systems/memory_media_file_storage.py` (2 TODOs)
5. `labs/memory/systems/memory_manager.py` (AIMPORT_TODO)
6. `labs/memory/episodic/episodic_memory.py` (1 TODO)
7. `labs/memory/folds/event_replayer.py` (1 TODO - marked ✅ but incomplete)

**Implementation Focus**:

**1. Memory Format**:
```python
class MemoryFormat:
    '''Standardized memory serialization format'''

    def serialize(self, memory: Memory) -> bytes:
        '''Serialize memory to compact format'''
        # Implement efficient serialization
        # Use msgpack or protobuf for performance

    def deserialize(self, data: bytes) -> Memory:
        '''Deserialize memory from bytes'''
        # Implement safe deserialization
        # Validate schema
```

**2. Memory Profiler**:
```python
class MemoryProfiler:
    '''Profile memory system performance'''

    def profile_operation(self, operation: str) -> ProfileResult:
        '''Profile memory operation performance'''
        # Track: latency, throughput, memory usage
        # Return detailed metrics
```

**3. Session Storage**:
```python
class SessionStorage:
    '''Persistent session storage'''

    def save_session(self, session: Session) -> str:
        '''Save session to persistent storage'''
        # Implement atomic saves
        # Return session ID

    def load_session(self, session_id: str) -> Session:
        '''Load session from storage'''
        # Implement efficient loading
        # Handle missing sessions
```

**4. Media File Storage**:
```python
class MediaFileStorage:
    '''Storage for media files in memories'''

    def store_media(self, media: bytes, metadata: dict) -> str:
        '''Store media file with metadata'''
        # Deduplicate by content hash
        # Return media ID

    def retrieve_media(self, media_id: str) -> bytes:
        '''Retrieve media file'''
        # Efficient retrieval
        # Caching layer
```

**5. Episodic Memory**:
```python
class EpisodicMemory:
    '''Time-ordered episodic memory system'''

    def record_episode(self, event: Event) -> str:
        '''Record episodic event'''
        # Temporal ordering
        # Context preservation

    def recall_episode(self, query: dict) -> List[Event]:
        '''Recall episodes by query'''
        # Temporal search
        # Relevance ranking
```

**6. Event Replayer**:
```python
class EventReplayer:
    '''Replay events from memory'''

    def replay_sequence(self, start_time: datetime, end_time: datetime):
        '''Replay events in temporal order'''
        # Efficient streaming
        # State reconstruction
```

**Integration**:
- All modules work together cohesively
- Shared interfaces and types
- Consistent error handling
- Performance optimization

**Expected Output**:
- 7 memory modules fully implemented
- Integrated memory subsystem
- Performance targets met (<100ms retrieval)
- Documentation complete

**Commit Message**:
```
feat(memory): implement complete memory subsystem

Problem:
- 10+ TODOs across memory modules
- No standardized memory format
- Missing profiling capabilities
- Session storage incomplete
- Media storage placeholder
- Episodic memory partial

Solution:
- Implemented memory serialization format
- Added performance profiling
- Complete session storage
- Media file storage with dedup
- Full episodic memory system
- Event replay functionality

Impact:
- Production-ready memory system
- <100ms retrieval performance
- Efficient storage usage
- Complete memory lifecycle

Tests: 60+ tests, benchmarks pass
Modules: 7 fully implemented
```

**Priority**: P1 - Core memory infrastructure
""",
    },
    {
        "title": "🔧 P1: Implement Task Manager TODOs",
        "prompt": """**HIGH PRIORITY: Complete Task Manager Implementation**

**Objective**: Implement all TODOs in task management system

**File**: `labs/core/task_manager.py` (5 TODOs total)

**Implementation**:

```python
class TaskManager:
    '''Manage LUKHAS cognitive tasks'''

    def __init__(self):
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def submit_task(self, task: Task) -> str:
        '''Submit task for execution'''
        # TODO: Implement task submission
        task_id = self._generate_task_id()
        self.active_tasks[task_id] = task

        # Enqueue for processing
        await self.task_queue.put((task_id, task))

        # Start task worker if not running
        if not hasattr(self, '_worker_task'):
            self._worker_task = asyncio.create_task(self._process_tasks())

        return task_id

    async def get_task_status(self, task_id: str) -> TaskStatus:
        '''Get task execution status'''
        # TODO: Implement status tracking
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return TaskStatus(
                id=task_id,
                state=task.state,
                progress=task.progress,
                result=task.result if task.state == 'completed' else None
            )

        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return TaskStatus(id=task_id, state='completed', result=task.result)

        raise TaskNotFoundError(f"Task {task_id} not found")

    async def cancel_task(self, task_id: str) -> bool:
        '''Cancel running task'''
        # TODO: Implement task cancellation
        if task_id not in self.active_tasks:
            return False

        task = self.active_tasks[task_id]
        if hasattr(task, 'cancel'):
            task.cancel()

        # Move to completed
        self.completed_tasks.append(task)
        del self.active_tasks[task_id]

        return True

    async def _process_tasks(self):
        '''Worker to process task queue'''
        # TODO: Implement task processing loop
        while True:
            try:
                task_id, task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # Execute task
                try:
                    result = await self._execute_task(task)
                    task.result = result
                    task.state = 'completed'
                except Exception as e:
                    task.error = str(e)
                    task.state = 'failed'

                # Move to completed
                self.completed_tasks.append(task)
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]

            except asyncio.TimeoutError:
                # Check if we should exit
                if not self.active_tasks and self.task_queue.empty():
                    break

    async def _execute_task(self, task: Task) -> Any:
        '''Execute a single task'''
        # TODO: Implement task execution
        # Support different task types
        if task.type == 'cognitive':
            return await self._execute_cognitive(task)
        elif task.type == 'memory':
            return await self._execute_memory(task)
        elif task.type == 'symbolic':
            return await self._execute_symbolic(task)
        else:
            raise ValueError(f"Unknown task type: {task.type}")
```

**Features to Implement**:
- Task submission and queuing
- Status tracking and monitoring
- Task cancellation
- Priority handling
- Resource management
- Error handling and retry
- Task dependencies
- Progress reporting

**Performance Targets**:
- Submit latency: <10ms
- Status check: <1ms
- Support 100+ concurrent tasks
- Graceful degradation under load

**Expected Output**:
- Complete task manager implementation
- All 5 TODOs resolved
- Async/await throughout
- Comprehensive error handling
- Documentation

**Commit Message**:
```
feat(core): implement complete task management system

Problem:
- 5 TODOs in task manager
- No task submission
- Missing status tracking
- No cancellation support
- Task execution incomplete

Solution:
- Implemented async task submission
- Added status tracking system
- Task cancellation support
- Priority queue processing
- Resource-aware execution

Impact:
- Complete task management
- 100+ concurrent tasks supported
- <10ms submission latency
- Production-ready orchestration

Tests: 40+ tests, load tested
```

**Priority**: P1 - Core orchestration
""",
    },
    {
        "title": "📦 P1: Clean Up Import Issues (F401, AIMPORT_TODO)",
        "prompt": """**HIGH PRIORITY: Systematic Import Cleanup**

**Objective**: Fix all import-related issues across codebase

**Issues to Fix**:
1. F401 unused imports (hundreds remaining)
2. AIMPORT_TODO placeholders (need proper imports)
3. Circular import issues
4. Missing __all__ declarations

**Approach**:

**1. Remove Unused Imports (F401)**:
```bash
# Auto-remove safe unused imports
ruff check --fix --select F401 --exclude tests/ .

# Manual review for re-exports
# Add __all__ where needed
```

**2. Fix AIMPORT_TODO**:
```python
# Before:
# AIMPORT_TODO

# After:
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from lukhas.core.base import BaseComponent
from lukhas.memory.interfaces import MemoryInterface
```

**3. Resolve Circular Imports**:
```python
# Strategy 1: Use TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_a import ClassA  # Only imported for type hints

# Strategy 2: Lazy imports
def function_needing_import():
    from module_a import ClassA  # Import at runtime
    return ClassA()

# Strategy 3: Restructure
# Move common types to separate module
```

**4. Add __all__ Declarations**:
```python
# In __init__.py
from .module_a import ClassA
from .module_b import ClassB

__all__ = ['ClassA', 'ClassB']  # Explicit public API
```

**Files to Fix** (priority order):
1. `labs/memory/systems/memory_manager.py` (AIMPORT_TODO)
2. `labs/memory/systems/memory_legacy/replayer.py` (AIMPORT_TODO)
3. All files with F401 violations (auto-fix where safe)
4. All `__init__.py` files (add __all__)

**Safety Checks**:
- Run tests after each batch of changes
- Verify no broken imports
- Check that public APIs still work
- Validate type hints still resolve

**Expected Output**:
- All F401 violations resolved
- All AIMPORT_TODO replaced
- __all__ in all public modules
- Clean import structure
- No circular imports

**Commit Message**:
```
refactor(imports): comprehensive import cleanup

Problem:
- 300+ F401 unused import violations
- AIMPORT_TODO placeholders in critical files
- No __all__ declarations
- Some circular import issues

Solution:
- Auto-removed safe unused imports
- Replaced all AIMPORT_TODO with proper imports
- Added __all__ to public modules
- Resolved circular imports with TYPE_CHECKING
- Restructured problematic dependencies

Impact:
- Clean, maintainable imports
- Faster import times
- Clear public API boundaries
- No circular dependency issues

Safety: All tests pass, no API changes
Files: 100+ files cleaned
```

**Priority**: P1 - Code hygiene and maintainability
""",
    },
    {
        "title": "🚀 P1: Implement OpenAI Routes TODOs",
        "prompt": """**HIGH PRIORITY: Complete OpenAI API Compatibility Layer**

**Objective**: Implement all TODOs in OpenAI routes for full API compatibility

**File**: `serve/openai_routes.py`

**Implementation Requirements**:

**1. Chat Completions Endpoint**:
```python
@app.post('/v1/chat/completions')
async def chat_completions(request: ChatCompletionRequest):
    '''OpenAI-compatible chat completions'''
    # TODO: Implement full request handling

    # Validate request
    if not request.messages:
        raise HTTPException(400, "messages required")

    # Route to LUKHAS MATRIZ
    matriz_response = await matriz_engine.process_conversation(
        messages=request.messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        stream=request.stream
    )

    # Format as OpenAI response
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": matriz_response.content
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": matriz_response.tokens_in,
            "completion_tokens": matriz_response.tokens_out,
            "total_tokens": matriz_response.tokens_total
        }
    )
```

**2. Streaming Support**:
```python
async def stream_chat_completion(request: ChatCompletionRequest):
    '''Stream chat completion chunks'''
    # TODO: Implement streaming

    async for chunk in matriz_engine.process_stream(request.messages):
        yield f"data: {json.dumps({
            'id': f'chatcmpl-{request_id}',
            'object': 'chat.completion.chunk',
            'created': int(time.time()),
            'model': request.model,
            'choices': [{
                'index': 0,
                'delta': {'content': chunk.text},
                'finish_reason': None
            }]
        })}\\n\\n"

    # Send final chunk
    yield f"data: {json.dumps({
        'choices': [{'finish_reason': 'stop'}]
    })}\\n\\n"
    yield "data: [DONE]\\n\\n"
```

**3. Models Endpoint**:
```python
@app.get('/v1/models')
async def list_models():
    '''List available models'''
    # TODO: Return LUKHAS models in OpenAI format

    return {
        "object": "list",
        "data": [
            {
                "id": "lukhas-matriz-v1",
                "object": "model",
                "created": 1677610602,
                "owned_by": "lukhas-ai",
                "permission": [],
                "root": "lukhas-matriz-v1",
                "parent": None
            },
            {
                "id": "lukhas-consciousness-v1",
                "object": "model",
                "owned_by": "lukhas-ai"
            }
        ]
    }
```

**4. Embeddings Endpoint**:
```python
@app.post('/v1/embeddings')
async def create_embeddings(request: EmbeddingRequest):
    '''Generate embeddings'''
    # TODO: Implement embedding generation

    # Get embeddings from LUKHAS memory system
    embeddings = await memory_system.generate_embeddings(
        texts=request.input if isinstance(request.input, list) else [request.input],
        model=request.model
    )

    return EmbeddingResponse(
        object="list",
        data=[{
            "object": "embedding",
            "embedding": emb.vector,
            "index": i
        } for i, emb in enumerate(embeddings)],
        model=request.model,
        usage={
            "prompt_tokens": sum(len(t.split()) for t in request.input),
            "total_tokens": sum(len(t.split()) for t in request.input)
        }
    )
```

**5. Error Handling**:
```python
class OpenAIErrorHandler:
    '''OpenAI-compatible error responses'''

    @staticmethod
    def format_error(error: Exception) -> dict:
        '''Format error in OpenAI format'''
        if isinstance(error, RateLimitError):
            return {
                "error": {
                    "message": "Rate limit exceeded",
                    "type": "rate_limit_error",
                    "code": "rate_limit_exceeded"
                }
            }
        # ... other error types
```

**Testing**:
- Test with official OpenAI Python client
- Verify streaming works
- Test all endpoints
- Load testing

**Expected Output**:
- Full OpenAI API compatibility
- All endpoints implemented
- Streaming working
- Error handling complete
- Tests passing

**Commit Message**:
```
feat(api): complete OpenAI API compatibility layer

Problem:
- Multiple TODOs in openai_routes.py
- Chat completions incomplete
- No streaming support
- Missing embeddings endpoint
- Error handling basic

Solution:
- Implemented full chat completions
- Added streaming support
- Complete embeddings endpoint
- Models listing
- OpenAI-compatible error handling

Impact:
- Drop-in replacement for OpenAI API
- Official OpenAI client compatible
- Streaming working perfectly
- Production-ready API layer

Tests: OpenAI client compatibility verified
```

**Priority**: P1 - Critical for adoption
""",
    },
    {
        "title": "🔧 P2: Implement Consciousness API TODOs",
        "prompt": """**MEDIUM PRIORITY: Complete Integrated Consciousness API**

**Objective**: Implement all TODOs in consciousness API layer

**File**: `serve/api/integrated_consciousness_api.py`

**Implementation**:

**1. Consciousness State Endpoint**:
```python
@app.get('/consciousness/state')
async def get_consciousness_state():
    '''Get current consciousness state'''
    # TODO: Implement state retrieval

    state = await consciousness_engine.get_current_state()

    return {
        'state': state.name,
        'awareness_level': state.awareness,
        'active_thoughts': len(state.thoughts),
        'emotional_state': state.emotion,
        'memory_context': state.context_size,
        'timestamp': state.timestamp.isoformat()
    }
```

**2. Thought Processing**:
```python
@app.post('/consciousness/think')
async def process_thought(request: ThoughtRequest):
    '''Process thought through consciousness layer'''
    # TODO: Implement thought processing

    result = await consciousness_engine.process_thought(
        content=request.content,
        context=request.context,
        emotions=request.emotions
    )

    return {
        'thought_id': result.id,
        'processed_content': result.content,
        'associations': result.associations,
        'emotional_response': result.emotions,
        'memory_references': result.memories
    }
```

**3. Dream State**:
```python
@app.post('/consciousness/dream')
async def enter_dream_state(request: DreamRequest):
    '''Enter dream/creative state'''
    # TODO: Implement dream state transition

    dream_session = await consciousness_engine.enter_dream_state(
        seed_thoughts=request.seeds,
        duration=request.duration,
        creativity=request.creativity_level
    )

    return {
        'session_id': dream_session.id,
        'state': 'dreaming',
        'estimated_duration': request.duration,
        'creative_outputs': []
    }

@app.get('/consciousness/dream/{session_id}')
async def get_dream_outputs(session_id: str):
    '''Get dream session outputs'''
    # TODO: Retrieve dream outputs

    outputs = await consciousness_engine.get_dream_outputs(session_id)

    return {
        'session_id': session_id,
        'outputs': outputs,
        'insights': [o.insight for o in outputs],
        'state': 'completed' if outputs.complete else 'in_progress'
    }
```

**4. Memory Integration**:
```python
@app.post('/consciousness/remember')
async def store_consciousness_memory(request: MemoryRequest):
    '''Store experience in consciousness memory'''
    # TODO: Implement memory storage

    memory_id = await consciousness_engine.store_memory(
        experience=request.experience,
        context=request.context,
        emotional_weight=request.importance
    )

    return {'memory_id': memory_id}

@app.post('/consciousness/recall')
async def recall_memory(request: RecallRequest):
    '''Recall relevant memories'''
    # TODO: Implement memory recall

    memories = await consciousness_engine.recall(
        query=request.query,
        limit=request.limit,
        emotional_filter=request.emotions
    )

    return {'memories': [m.to_dict() for m in memories]}
```

**5. Self-Awareness Endpoint**:
```python
@app.get('/consciousness/self-awareness')
async def get_self_awareness():
    '''Get self-awareness metrics'''
    # TODO: Implement self-awareness analysis

    awareness = await consciousness_engine.analyze_self_awareness()

    return {
        'awareness_score': awareness.score,
        'introspection_depth': awareness.depth,
        'metacognitive_insights': awareness.insights,
        'timestamp': datetime.utcnow().isoformat()
    }
```

**Expected Output**:
- Complete consciousness API
- All TODOs implemented
- Full integration with consciousness engine
- Comprehensive documentation
- API examples

**Commit Message**:
```
feat(consciousness): complete integrated consciousness API

Problem:
- Multiple TODOs in consciousness API
- No consciousness state endpoint
- Thought processing incomplete
- Dream state placeholder
- Memory integration missing
- No self-awareness endpoint

Solution:
- Implemented consciousness state retrieval
- Complete thought processing pipeline
- Dream state session management
- Memory storage and recall
- Self-awareness analysis endpoint

Impact:
- Production-ready consciousness API
- Full consciousness system accessible
- Dream state experiments enabled
- Memory-consciousness integration
- Self-awareness monitoring

Tests: 30+ API tests passing
```

**Priority**: P2 - Advanced features
""",
    },
    {
        "title": "⚡ P2: Implement Performance Optimizations",
        "prompt": """**MEDIUM PRIORITY: System-Wide Performance Optimizations**

**Objective**: Implement performance improvements across critical paths

**Areas to Optimize**:

**1. Caching Layer**:
```python
from functools import lru_cache
import asyncio

class CacheManager:
    '''Intelligent caching for LUKHAS'''

    def __init__(self):
        self._cache = {}
        self._ttl = {}

    async def get_or_compute(self, key: str, compute_fn, ttl: int = 300):
        '''Get from cache or compute'''
        # Check cache
        if key in self._cache:
            if time.time() < self._ttl.get(key, 0):
                return self._cache[key]

        # Compute
        result = await compute_fn() if asyncio.iscoroutinefunction(compute_fn) else compute_fn()

        # Store with TTL
        self._cache[key] = result
        self._ttl[key] = time.time() + ttl

        return result
```

**2. Database Query Optimization**:
```python
class OptimizedQuery:
    '''Optimized database queries'''

    @staticmethod
    async def batch_fetch(ids: List[str]) -> Dict[str, Any]:
        '''Batch fetch instead of N+1 queries'''
        # Single query for all IDs
        results = await db.execute(
            "SELECT * FROM table WHERE id = ANY($1)",
            ids
        )
        return {r['id']: r for r in results}

    @staticmethod
    async def prefetch_relations(objects: List[Any], relation: str):
        '''Prefetch related objects'''
        # Eager load instead of lazy
        relation_ids = [getattr(o, f'{relation}_id') for o in objects]
        relations = await batch_fetch(relation_ids)

        for obj in objects:
            setattr(obj, relation, relations[getattr(obj, f'{relation}_id')])
```

**3. Async Optimization**:
```python
async def parallel_processing(items: List[Any]):
    '''Process items in parallel'''
    # Before: Sequential (slow)
    # results = [await process(item) for item in items]

    # After: Parallel (fast)
    tasks = [process(item) for item in items]
    results = await asyncio.gather(*tasks)

    return results
```

**4. Memory Optimization**:
```python
import sys
from typing import Generator

def stream_large_dataset(file_path: str) -> Generator:
    '''Stream instead of loading all at once'''
    # Before: data = load_all(file_path)  # 10GB in memory!

    # After: Stream line by line
    with open(file_path, 'r') as f:
        for line in f:
            yield process_line(line)
            # Memory stays constant
```

**5. Connection Pooling**:
```python
from aiohttp import ClientSession

class ConnectionPool:
    '''Reuse connections instead of creating new ones'''

    def __init__(self, max_connections: int = 100):
        self.session = None
        self.max_connections = max_connections

    async def __aenter__(self):
        self.session = ClientSession(
            connector=TCPConnector(limit=self.max_connections)
        )
        return self.session

    async def __aexit__(self, *args):
        await self.session.close()
```

**Performance Targets**:
- API response: <100ms p95
- Memory usage: <500MB for typical workload
- Database queries: <10ms average
- Cache hit rate: >80%

**Benchmarking**:
```python
# Before/after benchmarks
import timeit

# Measure improvements
old_time = timeit.timeit(old_function, number=1000)
new_time = timeit.timeit(new_function, number=1000)

print(f"Improvement: {(old_time - new_time) / old_time * 100:.1f}%")
```

**Expected Output**:
- 30-50% performance improvement
- Reduced memory footprint
- Better resource utilization
- Comprehensive benchmarks

**Commit Message**:
```
perf: system-wide performance optimizations

Problem:
- Slow API responses (>200ms p95)
- High memory usage
- N+1 query problems
- No caching layer
- Sequential processing

Solution:
- Implemented intelligent caching
- Optimized database queries (batching)
- Parallel async processing
- Memory-efficient streaming
- Connection pooling

Impact:
- 40% faster API responses
- 50% reduced memory usage
- 80%+ cache hit rate
- <100ms p95 latency achieved

Benchmarks: All targets met
```

**Priority**: P2 - Performance improvement
""",
    },
    {
        "title": "🔒 P2: Implement Guardian Ethics DSL Enforcement",
        "prompt": """**MEDIUM PRIORITY: Activate Guardian Ethics DSL Enforcement**

**Objective**: Enable and enforce the Guardian ethics DSL system

**Background**: From AUDIT_07_NOV_25.md:
- Ethics DSL enforcement is OFF by default
- Need to activate for production readiness

**Implementation**:

**1. Enable DSL Enforcement**:
```python
# governance/guardian/config.py

class GuardianConfig:
    '''Guardian configuration'''

    # Change from:
    ENFORCE_ETHICS_DSL = False  # ❌ Currently disabled

    # To:
    ENFORCE_ETHICS_DSL = True   # ✅ Enable enforcement

    # Or environment-based:
    ENFORCE_ETHICS_DSL = os.getenv('GUARDIAN_ENFORCE_DSL', 'true').lower() == 'true'
```

**2. Implement DSL Parser**:
```python
class EthicsDSLParser:
    '''Parse and validate ethics DSL rules'''

    def parse_rule(self, rule_text: str) -> EthicsRule:
        '''Parse DSL rule into executable form'''
        # Example DSL:
        # WHEN action == "data_access" AND sensitivity == "high"
        # REQUIRE approval FROM admin AND audit_log == true

        tokens = self.tokenize(rule_text)
        ast = self.build_ast(tokens)
        return EthicsRule.from_ast(ast)

    def validate_rule(self, rule: EthicsRule) -> bool:
        '''Validate rule is well-formed'''
        # Check syntax
        # Verify all references exist
        # Ensure no conflicts
        return True
```

**3. Enforcement Engine**:
```python
class EthicsEnforcer:
    '''Enforce ethics rules at runtime'''

    async def check_action(self, action: Action) -> EnforcementResult:
        '''Check if action complies with ethics rules'''

        # Get applicable rules
        rules = self.get_rules_for_action(action)

        # Evaluate each rule
        violations = []
        for rule in rules:
            if not await rule.evaluate(action):
                violations.append(rule)

        if violations:
            return EnforcementResult(
                allowed=False,
                violations=violations,
                action='DENY'
            )

        return EnforcementResult(
            allowed=True,
            action='ALLOW'
        )
```

**4. Integration Points**:
```python
# Integrate into API layer
@app.post('/api/sensitive-action')
async def sensitive_action(request: Request):
    '''Protected endpoint with ethics check'''

    # Check ethics rules FIRST
    enforcement = await guardian.check_action(
        Action(
            type='sensitive-action',
            user=request.user,
            resource=request.resource
        )
    )

    if not enforcement.allowed:
        raise HTTPException(
            403,
            detail=f"Ethics violation: {enforcement.violations}"
        )

    # Proceed with action
    return await perform_action(request)
```

**5. Canary Deployment**:
```python
class CanaryEnforcement:
    '''Gradual rollout of enforcement'''

    def __init__(self, canary_percentage: float = 0.1):
        self.canary_percentage = canary_percentage

    async def should_enforce(self, user_id: str) -> bool:
        '''Decide if this user gets enforcement'''
        # Hash-based consistent assignment
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        return (user_hash % 100) < (self.canary_percentage * 100)
```

**Rollout Plan**:
1. Enable at 10% traffic (canary)
2. Monitor for false positives
3. Adjust rules as needed
4. Increase to 50%
5. Full rollout at 100%

**Monitoring**:
```python
# Track enforcement metrics
enforcement_checks = Counter('guardian_enforcement_checks_total')
enforcement_denials = Counter('guardian_enforcement_denials_total')
enforcement_latency = Histogram('guardian_enforcement_latency_ms')
```

**Expected Output**:
- Ethics DSL enforcement active
- Canary deployment working
- Monitoring in place
- Documentation updated

**Commit Message**:
```
feat(guardian): activate ethics DSL enforcement

Problem:
- Ethics DSL enforcement disabled by default
- No runtime ethics checking
- Production readiness gap
- Compliance risk

Solution:
- Enabled ethics DSL enforcement
- Implemented DSL parser and validator
- Created enforcement engine
- Added canary deployment (10% → 100%)
- Integrated into API layer
- Comprehensive monitoring

Impact:
- Active ethics enforcement
- Compliance requirement met
- Gradual, safe rollout
- Production-ready Guardian system

Security-Impact: High - Activates constitutional AI
Deployment: Canary (10% initial)
```

**Priority**: P2 - Compliance and safety
""",
    },
]


async def create_batch4():
    """Create Batch 4: Non-test implementation tasks"""

    print("\n" + "="*80)
    print("🚀 JULES BATCH 4: NON-TEST IMPLEMENTATION & OPTIMIZATION")
    print("="*80)
    print(f"\nCreating {len(BATCH4_SESSIONS)} sessions:")
    print("  🔧 Implementation: 5 sessions")
    print("  ⚡ Performance: 1 session")
    print("  📦 Code Quality: 1 session")
    print("  🔒 Governance: 1 session")
    print(f"\n  TOTAL: {len(BATCH4_SESSIONS)} sessions")
    print("\n⚠️  NOTE: May hit rate limit - will retry if needed")
    print("="*80 + "\n")

    created = []
    failed = []

    async with JulesClient() as jules:
        for i, session_config in enumerate(BATCH4_SESSIONS, 1):
            try:
                print(f"\n[{i}/{len(BATCH4_SESSIONS)}] Creating: {session_config['title']}")

                session = await jules.create_session(
                    prompt=session_config['prompt'],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session['name'].split('/')[-1]
                created.append({
                    'title': session_config['title'],
                    'session_id': session_id
                })

                print(f"✅ Created: {session_id}")
                print(f"   URL: https://jules.google.com/session/{session_id}")

            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print("⏸️  Rate limit hit - stopping here")
                    failed.append(session_config)
                    break
                else:
                    print(f"❌ Failed: {e}")
                    failed.append(session_config)
                    continue

            await asyncio.sleep(1)

    # Summary
    print("\n" + "="*80)
    print("📊 BATCH 4 SUMMARY")
    print("="*80)
    print(f"\n✅ Created: {len(created)}/{len(BATCH4_SESSIONS)} sessions")

    if created:
        print("\n📋 Successfully Created:")
        for s in created:
            print(f"\n• {s['title']}")
            print(f"  ID: {s['session_id']}")
            print(f"  URL: https://jules.google.com/session/{s['session_id']}")

    if failed:
        print(f"\n⏸️  Not Created (rate limit or error): {len(failed)} sessions")
        print("\nRetry later with:")
        print("  python3 scripts/create_jules_batch4_non_test.py")

    print("\n" + "="*80)
    print(f"🎯 Total Sessions Today: {26 + len(created)}/100")
    print("="*80 + "\n")

    return created, failed


if __name__ == "__main__":
    try:
        asyncio.run(create_batch4())
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
