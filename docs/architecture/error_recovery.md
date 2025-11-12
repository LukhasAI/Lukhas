# Orchestrator Error Recovery Architecture

This document outlines the architecture of the error recovery mechanisms within the
LUKHAS orchestration layer. These components are designed to improve the resilience
and fault tolerance of the system when interacting with external services or
performing operations that may fail.

## Components

The error recovery module consists of three main components:

1.  **Retry Decorator**: A decorator for retrying failed operations with a configurable
    backoff strategy.
2.  **Circuit Breaker**: A context manager for preventing cascading failures when a
    service is unavailable.
3.  **Fallback Handler**: A decorator for providing a fallback mechanism when an
    operation fails.

### Retry Decorator

The `@retry` decorator can be applied to any asynchronous function to automatically
retry it if it fails. It supports configurable retries, backoff strategies, and
the types of exceptions to catch.

**Usage:**

```python
from lukhas.orchestration.error_recovery import retry

@retry(retries=3, backoff=0.5, exceptions=ValueError)
async def call_flaky_service():
    # ...
```

### Circuit Breaker

The `CircuitBreaker` is an asynchronous context manager that wraps calls to
external services. It monitors for failures and, if the number of failures
exceeds a threshold, it "opens" the circuit and prevents further calls to the
service for a configured amount of time.

**Usage:**

```python
from lukhas.orchestration.error_recovery import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

async def call_service_with_breaker():
    async with breaker:
        # ... call the service
```

### Fallback Handler

The `@fallback` decorator provides a way to gracefully handle failures by
executing a fallback function when the primary function fails.

**Usage:**

```python
from lukhas.orchestration.error_recovery import fallback

async def primary_operation():
    # ... risky operation

async def fallback_operation():
    # ... fallback logic

@fallback(fallback_handler=fallback_operation)
async def operation_with_fallback():
    await primary_operation()
```
