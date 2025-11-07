#!/usr/bin/env python3
"""
Test Suite: Chaos Engineering Toolkit

Tests the functionality of the chaos engineering tools, including
failure injection, network partitioning, and resource exhaustion.

# ΛTAG: chaos_engineering, resilience_testing, failure_injection
"""

import asyncio
from unittest.mock import MagicMock

import pytest
from resilience.chaos import (
    ChaosMonkey,
    FailureInjector,
    NetworkPartitioner,
    ResourceExhaustor,
)

# --- Test FailureInjector ---

@pytest.mark.asyncio
async def test_failure_injector_injects_failure():
    """Test that the failure injector injects failures at the specified rate."""
    injector = FailureInjector(failure_rate=1.0)  # Always fail

    @injector.inject
    async def target_function():
        return "success"

    with pytest.raises(Exception, match="Chaos monkey intervened"):
        await target_function()

@pytest.mark.asyncio
async def test_failure_injector_allows_success():
    """Test that the failure injector allows successful calls."""
    injector = FailureInjector(failure_rate=0.0)  # Never fail

    @injector.inject
    async def target_function():
        return "success"

    assert await target_function() == "success"

# --- Test NetworkPartitioner ---

@pytest.mark.asyncio
async def test_network_partitioner_blocks_calls():
    """Test that the network partitioner can block calls."""
    partitioner = NetworkPartitioner(block_rate=1.0)  # Always block

    @partitioner.inject
    async def target_function():
        return "success"

    with pytest.raises(ConnectionAbortedError, match="Network partition simulated"):
        await target_function()

@pytest.mark.asyncio
async def test_network_partitioner_delays_calls():
    """Test that the network partitioner can delay calls."""
    partitioner = NetworkPartitioner(block_rate=0.0, delay_ms=100)  # Never block, always delay

    @partitioner.inject
    async def target_function():
        return "success"

    start_time = asyncio.get_event_loop().time()
    await target_function()
    end_time = asyncio.get_event_loop().time()

    assert (end_time - start_time) >= 0.1

# --- Test ResourceExhaustor ---

def test_resource_exhaustor_context_manager():
    """Test the resource exhaustor context manager."""
    exhaustor = ResourceExhaustor()

    with exhaustor.exhaust_resources():
        # In a real test, we would assert that resources are actually stressed.
        # For now, we just ensure the context manager runs without error.
        pass

# --- Test ChaosMonkey ---

@pytest.mark.asyncio
async def test_chaos_monkey_attacks():
    """Test that the chaos monkey randomly injects failures."""
    injector = FailureInjector(failure_rate=1.0)
    monkey = ChaosMonkey(failure_injectors=[injector])

    @monkey.attack
    async def target_function():
        return "success"

    with pytest.raises(Exception, match="Chaos monkey intervened"):
        await target_function()

@pytest.mark.asyncio
async def test_chaos_monkey_can_be_disabled():
    """Test that the chaos monkey can be disabled."""
    injector = FailureInjector(failure_rate=1.0)
    monkey = ChaosMonkey(failure_injectors=[injector], enabled=False)

    @monkey.attack
    async def target_function():
        return "success"

    assert await target_function() == "success"

# --- Recovery Verification ---

class MockService:
    def __init__(self):
        self.healthy = True

    async def perform_operation(self):
        if not self.healthy:
            raise ConnectionError("Service is down")
        return "operation successful"

    def is_healthy(self):
        return self.healthy

    def recover(self):
        self.healthy = True

@pytest.mark.asyncio
async def test_recovery_verification():
    """Test that the system can recover after a failure."""
    service = MockService()
    injector = FailureInjector(failure_rate=1.0, exception_type=ConnectionError)

    @injector.inject
    async def operation_with_chaos():
        return await service.perform_operation()

    # Initial state: service is healthy
    assert service.is_healthy()

    # Inject a failure
    with pytest.raises(ConnectionError):
        await operation_with_chaos()

    # Simulate recovery
    service.recover()

    # Verify that the service is healthy and operations succeed
    assert service.is_healthy()
    assert await service.perform_operation() == "operation successful"
