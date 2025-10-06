---
status: wip
type: documentation
---
# LUKHAS Capability Tests

Capability tests validate system-level behavior under realistic conditions and stress scenarios. These tests ensure the system meets performance and reliability targets in production-like environments.

## Test Categories

### Tier 1 Capabilities (Critical)

**Router Coverage**
- Every `ConsciousnessSignalType` has ≥1 routing rule and ≥1 target node
- No new signal types can be added without corresponding routing rules
- Fallback routing catches any missed signal types

**Zero-Unrouted Guarantee**
- Unrouted signal counter delta must remain 0 per consciousness cycle
- System startup/shutdown generates zero unrouted signals
- Full demonstration scenarios produce zero unrouted signals

**Performance SLOs**
- Consciousness processing: 30 FPS equivalent with p95 < 35ms under default load
- Router latency: p95 routing time < 10ms for single signals
- Network coherence: maintains ≥0.7 coherence under normal operation

**Backpressure Handling**
- Burst emissions (100+ signals) do not deadlock the system
- Cascade prevention activates appropriately under high load
- System remains responsive after burst scenarios

### Test Execution

**Local Development**
```bash
# Run all capability tests
pytest tests/capabilities/ -m capability -v

# Run specific capability
pytest tests/capabilities/test_router_no_unrouted.py -v

# Run with short stress duration
LUKHAS_STRESS_DURATION=1.0 pytest tests/capabilities/ -m capability
```

**CI/CD Pipeline**
```bash
# Strict mode enabled
LUKHAS_STRICT_EMIT=1 pytest tests/capabilities/ -m capability -q

# With Prometheus metrics validation
pytest tests/capabilities/ -m capability --prometheus-check
```

## Capability Markers

Tests use pytest markers to categorize capability requirements:

- `@pytest.mark.capability` - Core system capability test
- `@pytest.mark.performance` - Performance-focused test
- `@pytest.mark.stress` - High-load stress test
- `@pytest.mark.integration` - Multi-component integration test

## Success Criteria

### Router Capabilities
- ✅ All signal types have routing coverage
- ✅ Zero unrouted signals during normal operation
- ✅ Idempotent node registration
- ✅ Cascade prevention under burst load

### Processing Capabilities
- ✅ Bio-symbolic processor handles all signal types
- ✅ Memory systems maintain coherence under load
- ✅ Constellation Framework (8 Stars) validation passes

### Network Capabilities
- ✅ Network coherence remains ≥0.7
- ✅ Node health monitoring functions correctly
- ✅ Signal propagation latency within SLO targets

## Monitoring Integration

Capability tests integrate with the metrics system to validate:

**Prometheus Counters**
- `lukhas_router_no_rule_total` - Must remain 0 during tests
- `lukhas_router_cascade_preventions_total` - Expected under burst load
- `lukhas_network_coherence_score` - Must maintain ≥0.7

**Performance Metrics**
- `lukhas_router_signal_processing_seconds` - p95 < 0.035s
- Network latency and throughput within operational targets

## Failure Scenarios

**Hard Failures (Test Fails)**
- Any unrouted signals during normal operation
- Router boot sanity check failures
- Network coherence drops below 0.4
- Deadlocks or timeouts during burst scenarios

**Soft Failures (Warnings)**
- Performance degradation beyond SLO targets
- Cascade prevention activation frequency
- Memory or resource utilization spikes

## Adding New Capabilities

When adding new capability tests:

1. **Mark appropriately** with `@pytest.mark.capability`
2. **Document success criteria** in test docstrings
3. **Use metrics validation** where applicable
4. **Include cleanup** in try/finally blocks
5. **Set reasonable timeouts** to prevent hanging CI

Example template:
```python
@pytest.mark.capability
async def test_new_capability():
    """Test description and success criteria"""
    system = create_matriz_consciousness_system("test_id")

    try:
        await system.start_system()
        # Test logic here
        assert success_condition, "Descriptive failure message"
    finally:
        await system.stop_system()
```

## CI Integration

Capability tests run in CI with:
- `LUKHAS_STRICT_EMIT=1` for strict validation
- Reduced stress test duration for faster feedback
- Prometheus counter delta validation
- Performance regression detection

Alerts trigger on capability test failures to prevent production regressions.