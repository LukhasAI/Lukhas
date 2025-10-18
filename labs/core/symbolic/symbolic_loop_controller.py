#!/usr/bin/env python3
"""
Symbolic Loop Controller
Central control node for managing all symbolic loops in the system.
Routes symbolic terms (fold, drift, collapse) and ensures coherent processing.
"""
import streamlit as st
from datetime import timezone

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SymbolicTerm(Enum):
    """Core symbolic terms used throughout the system"""

    FOLD = "fold"  # Memory integration/compression
    DRIFT = "drift"  # Semantic evolution over time
    COLLAPSE = "collapse"  # State resolution/consolidation
    LINEAGE = "lineage"  # Causal chain tracking
    ENTANGLE = "entangle"  # Quantum-like correlation
    GROUND = "ground"  # Symbol-to-experience binding
    SYNTHESIZE = "synthesize"  # Creative generation
    INTEGRATE = "integrate"  # Holistic combination


class LoopType(Enum):
    """Types of symbolic loops in the system"""

    META_LEARNING = "meta_learning"  # Learning → Dream → Creativity → Memory
    SYMBOLIC_GROUNDING = "symbolic_grounding"  # Symbolic → Bio → Quantum → Consciousness
    SAFETY_MONITORING = "safety_monitoring"  # Identity → Ethics → Consciousness → Safety
    DREAM_SYNTHESIS = "dream_synthesis"  # Memory → Dream → Consciousness → Memory


@dataclass
class SymbolicOperation:
    """Represents a symbolic operation to be processed"""

    term: SymbolicTerm
    loop_type: LoopType
    agent_id: str
    data: dict[str, Any]
    priority: int = 5
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class SymbolicResult:
    """Result of a symbolic operation"""

    operation_id: str
    term: SymbolicTerm
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: dict[str, Any] = None


class SymbolicLoopController:
    """
    Master controller for all symbolic loops in the system.

    This controller:
    1. Routes symbolic operations to appropriate loops
    2. Manages dependencies between loops
    3. Ensures coherent symbolic processing
    4. Monitors loop health and performance
    """

    def __init__(self):
        # Loop handlers
        self._loop_handlers: dict[LoopType, Any] = {}

        # Operation queue
        self._operation_queue = asyncio.Queue()

        # Active operations
        self._active_operations: dict[str, SymbolicOperation] = {}

        # Loop status
        self._loop_status: dict[LoopType, dict[str, Any]] = {}

        # Symbolic vocabulary state
        self._symbolic_state: dict[str, Any] = {}

        # Background processor
        self._processor_task = None
        self._running = False

    async def initialize(self):
        """Initialize the controller and connect to loops"""
        # Get loop instances from service registry
        try:
            # Meta-learning loop
            from consciousness.loop_meta_learning import get_meta_learning_loop

            self._loop_handlers[LoopType.META_LEARNING] = get_meta_learning_loop()

            # Symbolic grounding loop
            from symbolic.loop_engine import get_symbolic_loop_engine

            self._loop_handlers[LoopType.SYMBOLIC_GROUNDING] = get_symbolic_loop_engine()

            # Initialize loop status
            for loop_type in LoopType:
                self._loop_status[loop_type] = {
                    "available": loop_type in self._loop_handlers,
                    "operations_processed": 0,
                    "last_operation": None,
                    "average_processing_time": 0.0,
                }

            # Start processor
            await self.start()

            logger.info("Symbolic Loop Controller initialized")

        except Exception as e:
            logger.error(f"Failed to initialize controller: {e}")
            raise

    async def start(self):
        """Start the controller processor"""
        if not self._running:
            self._running = True
            self._processor_task = asyncio.create_task(self._process_operations())
            logger.info("Symbolic processor started")

    async def stop(self):
        """Stop the controller"""
        self._running = False
        if self._processor_task:
            await self._processor_task
        logger.info("Symbolic processor stopped")

    async def process_symbolic_term(
        self,
        term: SymbolicTerm,
        agent_id: str,
        data: dict[str, Any],
        loop_type: Optional[LoopType] = None,
    ) -> SymbolicResult:
        """
        Process a symbolic term through the appropriate loop.

        If loop_type is not specified, the controller will determine
        the best loop based on the term and context.
        """
        # Determine loop type if not specified
        if loop_type is None:
            loop_type = self._determine_loop_type(term, data)

        # Create operation
        operation = SymbolicOperation(term=term, loop_type=loop_type, agent_id=agent_id, data=data)

        # Process based on term type
        return await self._route_operation(operation)

    def _determine_loop_type(self, term: SymbolicTerm, data: dict[str, Any]) -> LoopType:
        """Determine appropriate loop type for a symbolic term"""
        # Map terms to their primary loops
        term_loop_map = {
            SymbolicTerm.FOLD: LoopType.META_LEARNING,
            SymbolicTerm.DRIFT: LoopType.META_LEARNING,
            SymbolicTerm.COLLAPSE: LoopType.SYMBOLIC_GROUNDING,
            SymbolicTerm.LINEAGE: LoopType.META_LEARNING,
            SymbolicTerm.ENTANGLE: LoopType.SYMBOLIC_GROUNDING,
            SymbolicTerm.GROUND: LoopType.SYMBOLIC_GROUNDING,
            SymbolicTerm.SYNTHESIZE: LoopType.DREAM_SYNTHESIS,
            SymbolicTerm.INTEGRATE: LoopType.META_LEARNING,
        }

        # Check data for hints
        if "dream" in data or "synthesis" in data:
            return LoopType.DREAM_SYNTHESIS
        elif "safety" in data or "ethics" in data:
            return LoopType.SAFETY_MONITORING

        # Use default mapping
        return term_loop_map.get(term, LoopType.META_LEARNING)

    async def _route_operation(self, operation: SymbolicOperation) -> SymbolicResult:
        """Route operation to appropriate loop handler"""
        operation_id = f"{operation.term.value}_{operation.agent_id}_{datetime.now(timezone.utc).timestamp()}"

        try:
            # Check if loop is available
            if not self._loop_status[operation.loop_type]["available"]:
                return SymbolicResult(
                    operation_id=operation_id,
                    term=operation.term,
                    success=False,
                    error=f"Loop {operation.loop_type.value} not available",
                )

            # Get handler
            handler = self._loop_handlers.get(operation.loop_type)
            if not handler:
                return SymbolicResult(
                    operation_id=operation_id,
                    term=operation.term,
                    success=False,
                    error=f"No handler for loop {operation.loop_type.value}",
                )

            # Track operation
            self._active_operations[operation_id] = operation
            start_time = datetime.now(timezone.utc)

            # Route based on term
            result = await self._execute_term_operation(handler, operation)

            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Update statistics
            self._update_loop_statistics(operation.loop_type, processing_time)

            return SymbolicResult(
                operation_id=operation_id,
                term=operation.term,
                success=True,
                result=result,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"Operation failed: {e}")
            return SymbolicResult(
                operation_id=operation_id,
                term=operation.term,
                success=False,
                error=str(e),
            )
        finally:
            self._active_operations.pop(operation_id, None)

    async def _execute_term_operation(self, handler: Any, operation: SymbolicOperation) -> Any:
        """Execute specific term operation on handler"""
        term = operation.term
        data = operation.data
        agent_id = operation.agent_id

        # Route based on term type
        if term == SymbolicTerm.FOLD:
            # Memory folding operation
            if hasattr(handler, "execute_cycle"):
                return await handler.execute_cycle(agent_id, data)
            else:
                return {"error": "Handler doesn't support folding"}

        elif term == SymbolicTerm.GROUND:
            # Symbol grounding operation
            if hasattr(handler, "ground_symbol"):
                symbol = data.get("symbol", "")
                return await handler.ground_symbol(symbol, data.get("context"))
            else:
                return {"error": "Handler doesn't support grounding"}

        elif term == SymbolicTerm.SYNTHESIZE:
            # Synthesis operation
            if hasattr(handler, "synthesize"):
                return await handler.synthesize(agent_id, data)
            else:
                return {"error": "Handler doesn't support synthesis"}

        # Add more term handlers as needed
        else:
            return {"error": f"Unhandled term: {term.value}"}

    def _update_loop_statistics(self, loop_type: LoopType, processing_time: float):
        """Update loop performance statistics"""
        stats = self._loop_status[loop_type]

        # Update count
        stats["operations_processed"] += 1

        # Update average processing time
        n = stats["operations_processed"]
        avg = stats["average_processing_time"]
        stats["average_processing_time"] = (avg * (n - 1) + processing_time) / n

        # Update last operation time
        stats["last_operation"] = datetime.now(timezone.utc).isoformat()

    async def _process_operations(self):
        """Background processor for queued operations"""
        while self._running:
            try:
                # Get next operation with timeout
                operation = await asyncio.wait_for(self._operation_queue.get(), timeout=1.0)

                # Process the operation
                await self._route_operation(operation)

                # Could store result or notify listeners here

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Operation processor error: {e}")

    async def get_loop_status(self) -> dict[LoopType, dict[str, Any]]:
        """Get status of all loops"""
        return self._loop_status.copy()

    async def get_symbolic_state(self) -> dict[str, Any]:
        """Get current state of symbolic processing"""
        return {
            "active_operations": len(self._active_operations),
            "loop_status": await self.get_loop_status(),
            "symbolic_vocabulary": self._get_active_vocabulary(),
        }

    def _get_active_vocabulary(self) -> dict[str, int]:
        """Get currently active symbolic vocabulary with usage counts"""
        vocab = {}

        # Count term usage from active operations
        for op in self._active_operations.values():
            term = op.term.value
            vocab[term] = vocab.get(term, 0) + 1

        return vocab

    async def coordinate_multi_loop_operation(
        self,
        operations: list[tuple[SymbolicTerm, LoopType, dict[str, Any]]],
        agent_id: str,
    ) -> list[SymbolicResult]:
        """
        Coordinate operations across multiple loops.

        This enables complex symbolic processing that spans multiple loops.
        """
        results = []

        # Process operations in sequence (could be parallelized if independent)
        for term, loop_type, data in operations:
            result = await self.process_symbolic_term(term, agent_id, data, loop_type)
            results.append(result)

            # Pass result to next operation if successful
            if result.success and len(operations) > len(results):
                # Enrich next operation's data with previous result
                next_idx = len(results)
                if next_idx < len(operations):
                    operations[next_idx][2]["previous_result"] = result.result

        return results


# Singleton instance
_symbolic_controller = None


def get_symbolic_controller() -> SymbolicLoopController:
    """Get the singleton symbolic loop controller"""
    global _symbolic_controller
    if _symbolic_controller is None:
        _symbolic_controller = SymbolicLoopController()
    return _symbolic_controller


# Convenience functions


async def fold_memory(agent_id: str, memory_data: dict[str, Any]) -> SymbolicResult:
    """Convenience function for memory folding"""
    controller = get_symbolic_controller()
    return await controller.process_symbolic_term(SymbolicTerm.FOLD, agent_id, memory_data)


async def ground_symbol(symbol: str, context: Optional[dict[str, Any]] = None) -> SymbolicResult:
    """Convenience function for symbol grounding"""
    controller = get_symbolic_controller()
    return await controller.process_symbolic_term(
        SymbolicTerm.GROUND,
        "system",  # System-level grounding
        {"symbol": symbol, "context": context or {},
    )


async def track_drift(agent_id: str, state: dict[str, Any]) -> SymbolicResult:
    """Convenience function for drift tracking"""
    controller = get_symbolic_controller()
    return await controller.process_symbolic_term(SymbolicTerm.DRIFT, agent_id, state)


__all__ = [
    "LoopType",
    "SymbolicLoopController",
    "SymbolicOperation",
    "SymbolicResult",
    "SymbolicTerm",
    "fold_memory",
    "get_symbolic_controller",
    "ground_symbol",
    "track_drift",
]
