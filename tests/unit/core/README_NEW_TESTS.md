# Quick Start: New Test Suites

This directory contains new comprehensive test suites for previously untested core modules.

## 🎯 What's New

**2 New Test Files**:
- `test_agent_tracer.py` - 35+ tests for `core/agent_tracer.py`
- `test_minimal_actor.py` - 28+ tests for `core/minimal_actor.py`

**Total**: 63+ new test cases covering ~315 lines of production code

## 🚀 Running Tests

### Quick Run (All New Tests)
```bash
# From repository root
./run_new_tests.sh
```

### Individual Test Files
```bash
# Agent tracer tests
pytest tests/unit/core/test_agent_tracer.py -v

# Actor model tests
pytest tests/unit/core/test_minimal_actor.py -v
```

### With Coverage
```bash
# Agent tracer coverage
pytest tests/unit/core/test_agent_tracer.py \
    --cov=core.agent_tracer \
    --cov-report=term-missing

# Actor model coverage
pytest tests/unit/core/test_minimal_actor.py \
    --cov=core.minimal_actor \
    --cov-report=term-missing
```

### Run Specific Test Class
```bash
# Example: Test only TraceSpan functionality
pytest tests/unit/core/test_agent_tracer.py::TestTraceSpan -v

# Example: Test only Actor communication
pytest tests/unit/core/test_minimal_actor.py::TestActorCommunication -v
```

### Run Specific Test
```bash
# Example: Test span duration calculation
pytest tests/unit/core/test_agent_tracer.py::TestTraceSpan::test_trace_span_duration_before_finish -v

# Example: Test actor lifecycle
pytest tests/unit/core/test_minimal_actor.py::TestActorLifecycle::test_stop_actor -v
```

## 📁 Test Structure

```
tests/unit/core/
├── test_agent_tracer.py          # NEW: 35+ tests
│   ├── TestTraceSpan            # 8 tests - span lifecycle
│   ├── TestTraceCollector       # 6 tests - metrics collection
│   ├── TestAIAgentTracer        # 7 tests - context manager
│   ├── TestGlobalTracer         # 5 tests - multi-agent coordination
│   ├── TestGlobalTracerSingleton # 2 tests - singleton pattern
│   └── TestIntegration          # 2 tests - end-to-end workflows
│
└── test_minimal_actor.py         # NEW: 28+ tests
    ├── TestActorInitialization  # 3 tests - actor creation
    ├── TestMessageReceiving     # 4 tests - message handling
    ├── TestMessageHandling      # 3 tests - custom handlers
    ├── TestActorCommunication   # 5 tests - inter-actor messaging
    ├── TestActorLifecycle       # 3 tests - start/stop
    ├── TestActorPatterns        # 5 tests - design patterns
    └── TestEdgeCases            # 5 tests - boundary conditions
```

## 🧪 What's Tested

### Agent Tracer (`core/agent_tracer.py`)
✅ **TraceSpan**: Duration tracking, lifecycle, metadata  
✅ **TraceCollector**: Span collection, metrics aggregation  
✅ **AIAgentTracer**: Context manager, exception handling  
✅ **GlobalTracer**: Multi-agent coordination, global metrics  
✅ **Integration**: Complete swarm tracing workflows  

### Minimal Actor (`core/minimal_actor.py`)
✅ **Initialization**: Actor creation, state management  
✅ **Message Receiving**: Simple/complex messages, logging  
✅ **Message Handling**: Default/custom handlers, state  
✅ **Communication**: Actor-to-actor, bidirectional, chains  
✅ **Lifecycle**: Start, stop, inactive handling  
✅ **Patterns**: Request-response, broadcast, queuing, stateful computation  
✅ **Edge Cases**: None handling, empty IDs, special characters  

## 📊 Coverage Expectations

| Module | Before | After | Tests |
|--------|--------|-------|-------|
| `core/agent_tracer.py` | 0% | ~95% | 35+ |
| `core/minimal_actor.py` | 0% | ~98% | 28+ |

## 🔍 Test Examples

### Example 1: Testing Context Manager
```python
def test_trace_operation_basic(tracer, collector):
    """Test basic operation tracing with context manager"""
    with tracer.trace_agent_operation("test-agent", "basic_op") as span:
        assert span.agent_id == "test-agent"
        assert span.operation == "basic_op"
        time.sleep(0.01)

    # After exiting context, span should be finished and collected
    assert span.end_time is not None
    assert len(collector.spans) == 1
```

### Example 2: Testing Actor Communication
```python
def test_send_message_to_active_actor(sender, receiver):
    """Test sending message from one actor to another"""
    with patch.object(receiver, "receive") as mock_receive:
        message = {"type": "test", "data": "hello"}
        sender.send(receiver, message)
        mock_receive.assert_called_once_with(message)
```

### Example 3: Testing Patterns
```python
def test_broadcast_pattern():
    """Test broadcasting message to multiple actors"""
    coordinator = BroadcastCoordinator("coordinator")
    subscribers = [Actor(f"subscriber-{i}") for i in range(3)]

    for sub in subscribers:
        coordinator.subscribe(sub)

    coordinator.broadcast("broadcast message")
    # All 3 subscribers receive the message
```

## 🛠️ Troubleshooting

### Test Failures
```bash
# Run with detailed output
pytest tests/unit/core/test_agent_tracer.py -vv

# Drop into debugger on failure
pytest tests/unit/core/test_agent_tracer.py --pdb

# Show local variables on failure
pytest tests/unit/core/test_agent_tracer.py -l
```

### Import Errors
```bash
# Verify Python path includes repo root
python -c "import sys; print('\n'.join(sys.path))"

# Test imports manually
python -c "from core.agent_tracer import TraceSpan; print('OK')"
```

### Environment Issues
If you see import errors, rebuild environment:
```bash
rm -rf .venv_test
python3 -m venv .venv_test
source .venv_test/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

## 📚 Additional Resources

- **Full Summary**: `TEST_COVERAGE_IMPROVEMENT_SUMMARY.md`
- **Source Files**: `core/agent_tracer.py`, `core/minimal_actor.py`
- **pytest Docs**: https://docs.pytest.org/
- **Coverage Docs**: https://pytest-cov.readthedocs.io/

## 💡 Tips

**Run tests during development**:
```bash
# Auto-run tests on file change
pytest-watch tests/unit/core/test_agent_tracer.py
```

**Generate HTML coverage report**:
```bash
pytest tests/unit/core/ --cov=core --cov-report=html
open htmlcov/index.html
```

**Run only failed tests**:
```bash
pytest --lf tests/unit/core/
```

**Run tests matching pattern**:
```bash
# All tests with "span" in name
pytest -k "span" tests/unit/core/test_agent_tracer.py

# All tests with "communication" in name
pytest -k "communication" tests/unit/core/test_minimal_actor.py
```

---

**Questions?** See `TEST_COVERAGE_IMPROVEMENT_SUMMARY.md` for full details.
