# Agent Documentation Updates: Caching & Logging Standards

**Date**: 2025-01-10  
**Status**: Production  
**Affects**: All 27 LUKHAS agents  
**Version**: 1.0.0

---

## Overview

This document centralizes new caching and logging standards that all LUKHAS agents must follow. These standards were introduced with:

- **API Caching Performance Guide** (`docs/performance/API_CACHING_GUIDE.md`)
- **Logging Standards Guide** (`docs/development/LOGGING_STANDARDS.md`)

All agents should reference these patterns for consistent, auditable, and performant operations.

---

## Table of Contents

- [Caching Standards for Agents](#caching-standards-for-agents)
- [Logging Standards for Agents](#logging-standards-for-agents)
- [Testing Requirements](#testing-requirements)
- [Agent-Specific Notes](#agent-specific-notes)
- [Migration Examples](#migration-examples)

---

## Caching Standards for Agents

### When Agents Should Use Caching

✅ **DO cache**:
- LLM completions (expensive, often deterministic)
- API responses from external services
- Computed aggregations and analysis results
- Static configuration lookups
- Frequently accessed metadata

❌ **DON'T cache**:
- Real-time user actions
- Streaming responses
- Sensitive user data (without encryption)
- Rapidly changing metrics

### Standard Caching Pattern

```python
from labs.core.common import get_logger
from caching.cache_system import cache_operation

logger = get_logger(__name__)

# Decorator pattern (recommended)
@cache_operation(cache_key="agent_analysis", ttl_seconds=1800)
async def perform_analysis(data_id: str):
    """Analysis cached for 30 minutes"""
    logger.info("Performing analysis", extra={"data_id": data_id})
    result = await expensive_llm_call(data_id)
    return result

# Context manager pattern (for more control)
from caching.cache_system import get_cache_manager

async def perform_analysis_with_control(data_id: str):
    cache = get_cache_manager()
    
    async with cache.cached_operation(
        cache_key=f"analysis:{data_id}",
        operation=lambda: expensive_llm_call(data_id),
        ttl_seconds=1800
    ) as result:
        logger.info("Analysis complete", extra={
            "data_id": data_id,
            "cached": result is not None
        })
        return result
```

### Cache Invalidation

Agents must invalidate caches when underlying data changes:

```python
from caching.cache_system import get_cache_manager

async def on_data_updated(data_id: str):
    """Invalidate caches when data changes"""
    cache = get_cache_manager()
    
    # Invalidate specific key
    await cache.delete(f"analysis:{data_id}")
    
    # Or invalidate by pattern
    await cache.invalidate_pattern(f"analysis:{data_id}:*")
    
    logger.info("Cache invalidated", extra={"data_id": data_id})
```

### Agent-Specific Cache TTLs

| Agent Type | Recommended TTL | Reason |
|------------|----------------|--------|
| **Consciousness Systems** | 10-30 min | Balance freshness with compute cost |
| **API Bridge** | 5-15 min | External APIs change moderately |
| **Memory Systems** | 1-5 min | Memory queries are frequent but dynamic |
| **Testing/DevOps** | 30-60 min | Build/test results are stable |
| **Identity/Auth** | 5-10 min | Security-sensitive, shorter TTL |
| **Orchestration** | 15-30 min | Workflow state changes moderately |

### Cache Monitoring

Agents should emit metrics for cache performance:

```python
from observability import counter, histogram

cache_hits = counter("agent_cache_hits_total", "Cache hits", labelnames=("agent", "operation"))
cache_latency = histogram("agent_cache_latency_seconds", "Cache operation latency")

async def cached_operation(agent_name: str, operation_name: str):
    start = time.time()
    
    # ... cache operation ...
    
    if value_from_cache:
        cache_hits.labels(agent=agent_name, operation=operation_name).inc()
    
    cache_latency.observe(time.time() - start)
```

---

## Logging Standards for Agents

### Standard Logger Setup

**✅ CORRECT** (use this in all agents):

```python
from labs.core.common import get_logger

logger = get_logger(__name__)

def agent_function():
    logger.info("Agent processing started", extra={"agent": "my-agent"})
    # ... agent logic ...
```

**❌ INCORRECT** (don't do this):

```python
import logging

logger = logging.getLogger(__name__)  # Wrong - use get_logger()

# Also wrong - multiple loggers in one file
logger1 = logging.getLogger("agent1")
logger2 = logging.getLogger("agent2")
```

### Structured Logging for Agents

Always use `extra` dictionary for agent context:

```python
logger.info("Task completed", extra={
    "agent": "context-orchestrator",
    "task_id": task_id,
    "duration_ms": duration,
    "status": "success",
    "items_processed": len(results)
})
```

### Log Levels for Agents

| Level | When to Use | Example |
|-------|-------------|---------|
| **DEBUG** | Detailed workflow steps | `logger.debug("Entering orchestration phase", extra={"phase": "planning"})` |
| **INFO** | Major agent actions | `logger.info("Agent task completed", extra={"task_id": task_id})` |
| **WARNING** | Degraded performance, retries | `logger.warning("Cache miss rate high", extra={"miss_rate": 0.75})` |
| **ERROR** | Task failures (recoverable) | `logger.error("LLM call failed", exc_info=True, extra={"retries": 3})` |
| **CRITICAL** | Agent failures (unrecoverable) | `logger.critical("Agent initialization failed", exc_info=True)` |

### Standard Extra Fields for Agents

Use these field names consistently:

```python
{
    "agent": "agent-name",           # Always include agent name
    "task_id": "task_123",           # Unique task identifier
    "user_id": "user_456",           # User context (if applicable)
    "duration_ms": 123.45,           # Operation duration
    "status": "success|failure",     # Operation outcome
    "error_type": "ValidationError", # Error classification
    "retry_count": 3,                # Retry attempts
    "items_processed": 42,           # Items/records processed
    "cache_hit": True                # Cache performance
}
```

### Error Logging with Context

```python
try:
    result = await agent_operation(data)
except ValidationError as e:
    logger.error("Validation failed", exc_info=True, extra={
        "agent": "validator",
        "error_type": "ValidationError",
        "field": e.field,
        "value": e.value  # Don't log if sensitive!
    })
    raise
except Exception as e:
    logger.critical("Unexpected agent failure", exc_info=True, extra={
        "agent": "my-agent",
        "error_type": type(e).__name__
    })
    raise
```

### PII Sanitization

Agents must **never** log sensitive data:

```python
# ❌ WRONG
logger.info(f"User password: {password}")
logger.info(f"API key: {api_key}")

# ✅ CORRECT
logger.info("User authenticated", extra={"user_id": user_id})
logger.info("API call made", extra={"api_key_prefix": api_key[:8] + "..."})
```

---

## Testing Requirements

### Caching Tests

All agents with caching should include these tests:

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_caching():
    """Test agent uses caching correctly"""
    
    # Mock expensive operation
    with patch("agent.expensive_operation") as mock_op:
        mock_op.return_value = {"result": "data"}
        
        # First call (cache miss)
        result1 = await agent_function("test_id")
        assert mock_op.call_count == 1
        
        # Second call (cache hit - should not call operation again)
        result2 = await agent_function("test_id")
        assert mock_op.call_count == 1  # Still 1!
        assert result1 == result2

@pytest.mark.asyncio
async def test_agent_cache_invalidation():
    """Test agent invalidates cache appropriately"""
    
    result1 = await agent_function("test_id")
    
    # Trigger cache invalidation
    await agent_on_data_updated("test_id")
    
    # Next call should hit operation again
    with patch("agent.expensive_operation") as mock_op:
        mock_op.return_value = {"result": "new_data"}
        result2 = await agent_function("test_id")
        assert mock_op.call_count == 1
```

### Logging Tests

```python
import pytest
from unittest.mock import patch
import logging

def test_agent_logging_structure(caplog):
    """Test agent logs use correct structure"""
    
    with caplog.at_level(logging.INFO):
        agent_function("test_data")
    
    # Check log was created
    assert len(caplog.records) > 0
    
    # Check structured data in extra
    log_record = caplog.records[0]
    assert hasattr(log_record, "agent")
    assert hasattr(log_record, "task_id")

def test_agent_no_pii_in_logs(caplog):
    """Test agent doesn't log PII"""
    
    with caplog.at_level(logging.INFO):
        agent_function_with_user_data("user@email.com", "password123")
    
    # Check logs don't contain PII
    all_logs = " ".join(record.message for record in caplog.records)
    assert "password" not in all_logs.lower()
    assert "user@email.com" not in all_logs
```

---

## Agent-Specific Notes

### Context Orchestrator Specialist

**Caching Strategy**:
- Cache workflow templates (TTL: 30 min)
- Cache message routing rules (TTL: 15 min)
- Invalidate on pipeline changes

**Logging Focus**:
- Log all pipeline transitions
- Include workflow_id in all logs
- Track context handoff performance (<250ms target)

### API Bridge Specialist

**Caching Strategy**:
- Cache OpenAPI specs (TTL: 1 hour)
- Cache API responses (TTL: 5-15 min based on endpoint)
- Implement cache-aside pattern for external APIs

**Logging Focus**:
- Log all external API calls with latency
- Include api_name, endpoint, status_code
- Log rate limit warnings

### Memory Consciousness Specialist

**Caching Strategy**:
- Cache memory embeddings (TTL: 5 min)
- Cache frequently accessed memories (LRU, 1000 items)
- Invalidate on memory updates

**Logging Focus**:
- Log memory operations with memory_id
- Track embedding computation time
- Log drift detection events

### Testing DevOps Specialist

**Caching Strategy**:
- Cache test results (TTL: 30 min)
- Cache build artifacts (TTL: 1 hour)
- Don't cache failing tests

**Logging Focus**:
- Log all test runs with test_suite, duration
- Include pass/fail counts
- Log flaky test detection

### Consciousness Systems Architect

**Caching Strategy**:
- Cache system topologies (TTL: 15 min)
- Cache architecture decisions (TTL: 1 hour)
- Invalidate on system changes

**Logging Focus**:
- Log system state changes
- Include component health in logs
- Track system coherence metrics

### Guardian Compliance Officer

**Caching Strategy**:
- Cache policy rules (TTL: 30 min)
- Cache compliance checks (TTL: 10 min)
- Invalidate on policy updates

**Logging Focus**:
- Log all policy violations with severity
- Include user_id, action, policy_id
- Never log sensitive content being checked

---

## Migration Examples

### Before (Old Pattern)

```python
import logging

logger = logging.getLogger(__name__)

async def agent_process(data):
    logger.info(f"Processing {data}")
    
    # No caching
    result = await expensive_computation(data)
    
    return result
```

### After (New Pattern)

```python
from labs.core.common import get_logger
from caching.cache_system import cache_operation

logger = get_logger(__name__)

@cache_operation(cache_key="agent_process", ttl_seconds=1800)
async def agent_process(data):
    logger.info("Processing data", extra={
        "agent": "my-agent",
        "data_id": data.id
    })
    
    result = await expensive_computation(data)
    
    logger.info("Processing complete", extra={
        "agent": "my-agent",
        "data_id": data.id,
        "items_processed": len(result)
    })
    
    return result
```

---

## Verification Checklist

For each agent update, verify:

- [ ] Uses `get_logger(__name__)` from `labs.core.common`
- [ ] Only ONE logger defined per agent file
- [ ] Uses `@cache_operation` or context manager for caching
- [ ] Includes appropriate cache TTL for agent type
- [ ] Implements cache invalidation where needed
- [ ] Uses structured logging with `extra` dict
- [ ] Includes standard extra fields (agent, task_id, etc.)
- [ ] No PII in logs
- [ ] Includes caching tests
- [ ] Includes logging tests
- [ ] Emits Prometheus metrics for cache performance

---

## Quick Reference

### Imports

```python
# Logging
from labs.core.common import get_logger

# Caching
from caching.cache_system import cache_operation, get_cache_manager

# Metrics
from observability import counter, histogram, gauge
```

### Patterns

```python
# Logger setup
logger = get_logger(__name__)

# Cached function
@cache_operation(cache_key="operation", ttl_seconds=1800)
async def my_operation():
    logger.info("Operation started", extra={"agent": "my-agent"})
    # ... logic ...

# Cache invalidation
cache = get_cache_manager()
await cache.invalidate_pattern("operation:*")

# Structured logging
logger.info("Event", extra={
    "agent": "agent-name",
    "task_id": "task_123",
    "status": "success"
})
```

---

## Resources

**Documentation**:
- [API Caching Performance Guide](../performance/API_CACHING_GUIDE.md)
- [Logging Standards Guide](../development/LOGGING_STANDARDS.md)
- [Prometheus Monitoring Guide](../operations/PROMETHEUS_MONITORING_GUIDE.md)

**Implementation**:
- [Caching System](../../caching/cache_system.py)
- [Logger Implementation](../../labs/core/common/logger.py)
- [Observability System](../../observability/)

**Examples**:
- [Agent Tests](../../tests/test_slsa_provenance.py) - Logging example
- [Cache Tests](../../tests/) - Caching examples

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Applies To**: All 27 LUKHAS agents

🤖 Generated with Claude Code
