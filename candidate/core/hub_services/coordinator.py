#!/usr/bin/env python3
"""
Hub Coordinator
Neutral coordination layer that breaks circular dependencies between modules.
Acts as a mediator for cross-module communication without creating tight coupling.
"""
import streamlit as st
from datetime import timezone

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__, timezone)


class ModuleType(Enum):
    """Types of modules that can be coordinated"""

    CORE = "core"
    MEMORY = "memory"
    CONSCIOUSNESS = "consciousness"
    LEARNING = "learning"
    IDENTITY = "identity"
    ORCHESTRATION = "orchestration"
    BIO = "bio"
    QUANTUM = "quantum"
    SYMBOLIC = "symbolic"
    DREAM = "dream"
    CREATIVITY = "creativity"
    ETHICS = "ethics"
    API = "api"


@dataclass
class CoordinationRequest:
    """Request for cross-module coordination"""

    source_module: ModuleType
    target_module: ModuleType
    operation: str
    data: dict[str, Any]
    priority: int = 5
    timeout: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class CoordinationResponse:
    """Response from coordination request"""

    request_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class HubCoordinator:
    """
    Central coordination hub that manages cross-module communication.
    This breaks circular dependencies by providing a neutral communication layer.
    """

    def __init__(self):
        # Module handlers registry
        self._handlers: dict[ModuleType, dict[str, Callable]] = {}

        # Request queue for async processing
        self._request_queue = asyncio.Queue()

        # Active requests tracking
        self._active_requests: dict[str, CoordinationRequest] = {}

        # Module availability
        self._module_status: dict[ModuleType, bool] = dict.fromkeys(ModuleType, False)

        # Start background processor
        self._processor_task = None
        self._running = False

    async def start(self):
        """Start the coordinator background processing"""
        if not self._running:
            self._running = True
            self._processor_task = asyncio.create_task(self._process_requests())
            logger.info("Hub Coordinator started")

    async def stop(self):
        """Stop the coordinator"""
        self._running = False
        if self._processor_task:
            await self._processor_task
        logger.info("Hub Coordinator stopped")

    def register_handler(self, module: ModuleType, operation: str, handler: Callable) -> None:
        """
        Register a handler for a specific module operation.

        This allows modules to register their capabilities without
        importing each other directly.
        """
        if module not in self._handlers:
            self._handlers[module] = {}

        self._handlers[module][operation] = handler
        self._module_status[module] = True

        logger.info(f"Registered handler: {module.value}.{operation}")

    async def coordinate(self, request: CoordinationRequest) -> CoordinationResponse:
        """
        Process a coordination request between modules.

        This is the main entry point for cross-module communication.
        """
        request_id = f"{request.source_module.value}_{request.target_module.value}_{datetime.now(timezone.utc).timestamp()}"

        try:
            # Check if target module is available
            if not self._module_status.get(request.target_module, False):
                return CoordinationResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Target module {request.target_module.value} not available",
                )

            # Check if operation is registered
            if request.target_module not in self._handlers:
                return CoordinationResponse(
                    request_id=request_id,
                    success=False,
                    error=f"No handlers registered for {request.target_module.value}",
                )

            if request.operation not in self._handlers[request.target_module]:
                return CoordinationResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Operation {request.operation} not registered for {request.target_module.value}",
                )

            # Get handler
            handler = self._handlers[request.target_module][request.operation]

            # Execute with timeout if specified
            start_time = datetime.now(timezone.utc)

            if request.timeout:
                result = await asyncio.wait_for(handler(request.data), timeout=request.timeout)
            else:
                result = await handler(request.data)

            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            return CoordinationResponse(
                request_id=request_id,
                success=True,
                result=result,
                processing_time=processing_time,
            )

        except asyncio.TimeoutError:
            return CoordinationResponse(
                request_id=request_id,
                success=False,
                error=f"Request timed out after {request.timeout} seconds",
            )
        except Exception as e:
            logger.error(f"Coordination error: {e}")
            return CoordinationResponse(request_id=request_id, success=False, error=str(e))

    async def coordinate_async(self, request: CoordinationRequest) -> str:
        """
        Submit a request for async processing.
        Returns immediately with a request ID.
        """
        request_id = f"{request.source_module.value}_{request.target_module.value}_{datetime.now(timezone.utc).timestamp()}"
        self._active_requests[request_id] = request
        await self._request_queue.put((request_id, request))
        return request_id

    async def get_result(self, request_id: str, timeout: float = 30.0) -> CoordinationResponse:
        """Get the result of an async request"""
        start_time = datetime.now(timezone.utc)

        while (datetime.now(timezone.utc) - start_time).total_seconds() < timeout:
            if request_id not in self._active_requests:
                # Request completed, find response
                # In a real implementation, we'd store responses
                return CoordinationResponse(
                    request_id=request_id,
                    success=True,
                    result={"status": "completed"},
                )
            await asyncio.sleep(0.1)

        return CoordinationResponse(request_id=request_id, success=False, error="Request timed out")

    async def _process_requests(self):
        """Background processor for async requests"""
        while self._running:
            try:
                # Get next request with timeout to allow checking _running
                request_id, request = await asyncio.wait_for(self._request_queue.get(), timeout=1.0)

                # Process the request
                await self.coordinate(request)

                # Store response and remove from active
                # In real implementation, store in a response cache
                self._active_requests.pop(request_id, None)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Request processor error: {e}")

    def get_module_status(self) -> dict[ModuleType, bool]:
        """Get current status of all modules"""
        return self._module_status.copy()

    def get_registered_operations(self, module: ModuleType) -> list[str]:
        """Get all registered operations for a module"""
        if module in self._handlers:
            return list(self._handlers[module].keys())
        return []


# Singleton instance
_hub_coordinator = None


def get_hub_coordinator() -> HubCoordinator:
    """Get the singleton hub coordinator instance."""
    global _hub_coordinator
    if _hub_coordinator is None:
        _hub_coordinator = HubCoordinator()
    return _hub_coordinator


# Convenience functions for module registration


def register_module_handler(module: ModuleType, operation: str, handler: Callable):
    """Register a handler with the hub coordinator"""
    coordinator = get_hub_coordinator()
    coordinator.register_handler(module, operation, handler)


async def coordinate_request(
    source: ModuleType,
    target: ModuleType,
    operation: str,
    data: dict[str, Any],
    **kwargs,
) -> CoordinationResponse:
    """Make a coordination request between modules"""
    coordinator = get_hub_coordinator()
    request = CoordinationRequest(
        source_module=source,
        target_module=target,
        operation=operation,
        data=data,
        **kwargs,
    )
    return await coordinator.coordinate(request)


__all__ = [
    "CoordinationRequest",
    "CoordinationResponse",
    "HubCoordinator",
    "ModuleType",
    "coordinate_request",
    "get_hub_coordinator",
    "register_module_handler",
]
