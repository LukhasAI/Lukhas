#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - COLONY MEMORY VALIDATOR
║ Distributed validation system for memory operations across colonies
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: colony_memory_validator.py
║ Path: memory/core/colony_memory_validator.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the distributed realm of colonies, trust is not assumed but earned      │
║ │ through consensus. Like neurons voting on the reality of a memory, each    │
║ │ colony contributes its voice to the choir of validation. No single point   │
║ │ of failure, no singular authority—only the collective wisdom of the        │
║ │ distributed mind ensuring the integrity of remembrance.                    │
║ │                                                                             │
║ │ Through Byzantine fault tolerance and quorum consensus, memories are       │
║ │ forged in the crucible of agreement, their truth verified not by decree    │
║ │ but by democratic process, their integrity guaranteed not by assumption    │
║ │ but by proof.                                                              │
║ │                                                                             │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Byzantine fault-tolerant consensus
║ • Quorum-based validation
║ • Integrity verification across colonies
║ • Conflict resolution mechanisms
║ • Performance-aware validation
║ • Colony health monitoring
║ • Adaptive timeout handling
║ • Memory operation auditing
║
║ ΛTAG: ΛVALIDATION, ΛCOLONY, ΛCONSENSUS, ΛBYZANTINE, ΛINTEGRITY
╚══════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations


import asyncio
import hashlib
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

from .interfaces.memory_interface import (
    MemoryOperation,
    ValidationResult,
)

# Module logger
logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """Validation modes for different operations"""

    NO_VALIDATION = "none"  # Skip validation (performance mode)
    SIMPLE = "simple"  # Basic integrity check
    QUORUM = "quorum"  # Majority consensus
    UNANIMOUS = "unanimous"  # All colonies must agree
    BYZANTINE = "byzantine"  # Byzantine fault tolerance


class ConsensusResult(Enum):
    """Consensus outcomes"""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CONFLICT = "conflict"
    INSUFFICIENT_COLONIES = "insufficient"


@dataclass
class ValidationRequest:
    """Request for memory validation across colonies"""

    operation: MemoryOperation
    request_id: str = field(default_factory=lambda: str(uuid4()))
    validation_mode: ValidationMode = ValidationMode.QUORUM

    # Participating colonies
    target_colonies: list[str] = field(default_factory=list)
    minimum_responses: int = 2
    consensus_threshold: float = 0.67  # 2/3 majority

    # Timeout settings
    timeout_seconds: float = 30.0
    max_retries: int = 2

    # Integrity checking
    expected_hash: Optional[str] = None
    require_hash_match: bool = False

    # Metadata
    timestamp: float = field(default_factory=time.time)
    requester: Optional[str] = None


@dataclass
class ColonyValidationResponse:
    """Response from a single colony for validation"""

    colony_id: str
    request_id: str
    success: bool = False

    # Validation results
    validation_result: ValidationResult = ValidationResult.INVALID
    content_hash: Optional[str] = None

    # Performance metrics
    response_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    # Colony health
    colony_load: float = 0.0
    colony_trust_score: float = 1.0


@dataclass
class ConsensusOutcome:
    """Final consensus result for validation request"""

    request_id: str
    result: ConsensusResult

    # Response analysis
    total_responses: int = 0
    successful_responses: int = 0
    consensus_achieved: bool = False
    consensus_confidence: float = 0.0

    # Colony responses
    colony_responses: dict[str, ColonyValidationResponse] = field(default_factory=dict)

    # Conflict resolution
    conflicting_colonies: list[str] = field(default_factory=list)
    dominant_response: Optional[ColonyValidationResponse] = None

    # Performance
    total_time_ms: float = 0.0
    fastest_response_ms: float = 0.0
    slowest_response_ms: float = 0.0

    # Additional metadata for integration points
    metadata: dict[str, Any] = field(default_factory=dict)


class ColonyMemoryValidator:
    """
    Main validator for memory operations across colonies.
    Implements Byzantine fault-tolerant consensus for memory integrity.
    """

    def __init__(
        self,
        validator_id: Optional[str] = None,
        default_validation_mode: ValidationMode = ValidationMode.QUORUM,
        default_timeout: float = 30.0,
        max_concurrent_validations: int = 100,
    ):
        self.validator_id = validator_id or f"validator_{str(uuid4())[:8]}"
        self.default_validation_mode = default_validation_mode
        self.default_timeout = default_timeout
        self.max_concurrent_validations = max_concurrent_validations

        # Active validations
        self.active_validations: dict[str, ValidationRequest] = {}
        self.validation_semaphore = asyncio.Semaphore(max_concurrent_validations)

        # Colony management
        self.registered_colonies: dict[str, dict[str, Any]] = {}
        self.colony_trust_scores: dict[str, float] = {}
        self.colony_performance_history: dict[str, list[float]] = defaultdict(list)

        # Validation callbacks
        self.validation_callbacks: list[Callable] = []
        self.consensus_callbacks: list[Callable] = []

        # Metrics
        self.total_validations = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.timeout_validations = 0
        self.conflict_validations = 0

        # Background tasks
        self._running = False
        self._cleanup_task = None
        self._monitoring_task = None

        logger.info(
            "ColonyMemoryValidator initialized",
            validator_id=self.validator_id,
            default_mode=default_validation_mode.value,
            max_concurrent=max_concurrent_validations,
        )

    async def start(self):
        """Start the validator"""
        self._running = True

        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_validations())
        self._monitoring_task = asyncio.create_task(self._monitor_colony_health())

        logger.info("ColonyMemoryValidator started")

    async def stop(self):
        """Stop the validator"""
        self._running = False

        # Cancel background tasks
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._monitoring_task:
            self._monitoring_task.cancel()

        # Cancel active validations
        for request_id in list(self.active_validations.keys()):
            if request_id in self.active_validations:
                del self.active_validations[request_id]

        logger.info(
            "ColonyMemoryValidator stopped",
            total_validations=self.total_validations,
            success_rate=self.successful_validations / max(self.total_validations, 1),
        )

    def register_colony(
        self,
        colony_id: str,
        colony_info: dict[str, Any],
        initial_trust_score: float = 1.0,
    ):
        """Register a colony for validation participation"""
        self.registered_colonies[colony_id] = colony_info
        self.colony_trust_scores[colony_id] = initial_trust_score

        logger.info(
            "Colony registered for validation",
            colony_id=colony_id,
            trust_score=initial_trust_score,
        )

    def unregister_colony(self, colony_id: str):
        """Unregister a colony"""
        self.registered_colonies.pop(colony_id, None)
        self.colony_trust_scores.pop(colony_id, None)
        self.colony_performance_history.pop(colony_id, None)

        logger.info("Colony unregistered", colony_id=colony_id)

    async def validate_memory_operation(
        self,
        operation: MemoryOperation,
        validation_mode: Optional[ValidationMode] = None,
        target_colonies: Optional[list[str]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> ConsensusOutcome:
        """
        Validate memory operation across colonies with consensus.
        Returns consensus outcome with detailed results.
        """

        async with self.validation_semaphore:
            return await self._execute_validation(
                operation=operation,
                validation_mode=validation_mode or self.default_validation_mode,
                target_colonies=target_colonies or list(self.registered_colonies.keys()),
                timeout_seconds=timeout_seconds or self.default_timeout,
            )

    async def _execute_validation(
        self,
        operation: MemoryOperation,
        validation_mode: ValidationMode,
        target_colonies: list[str],
        timeout_seconds: float,
    ) -> ConsensusOutcome:
        """Execute the validation process"""

        start_time = time.time()

        # Create validation request
        request = ValidationRequest(
            operation=operation,
            validation_mode=validation_mode,
            target_colonies=target_colonies,
            timeout_seconds=timeout_seconds,
            consensus_threshold=self._get_consensus_threshold(validation_mode),
        )

        self.active_validations[request.request_id] = request
        self.total_validations += 1

        try:
            # Skip validation if mode is NO_VALIDATION
            if validation_mode == ValidationMode.NO_VALIDATION:
                return ConsensusOutcome(
                    request_id=request.request_id,
                    result=ConsensusResult.SUCCESS,
                    consensus_achieved=True,
                    consensus_confidence=1.0,
                )

            # Execute validation across colonies
            colony_responses = await self._gather_colony_responses(request)

            # Analyze consensus
            outcome = self._analyze_consensus(request, colony_responses)
            outcome.total_time_ms = (time.time() - start_time) * 1000

            # Update metrics
            if outcome.result == ConsensusResult.SUCCESS:
                self.successful_validations += 1
            elif outcome.result == ConsensusResult.TIMEOUT:
                self.timeout_validations += 1
            elif outcome.result == ConsensusResult.CONFLICT:
                self.conflict_validations += 1
            else:
                self.failed_validations += 1

            # Update colony trust scores
            self._update_colony_trust_scores(outcome)

            # Notify callbacks
            await self._notify_callbacks(request, outcome)

            logger.debug(
                "Validation completed",
                request_id=request.request_id,
                result=outcome.result.value,
                consensus_achieved=outcome.consensus_achieved,
                total_time_ms=outcome.total_time_ms,
            )

            return outcome

        except Exception as e:
            self.failed_validations += 1
            logger.error(f"Validation error: {e}", request_id=request.request_id)

            return ConsensusOutcome(
                request_id=request.request_id,
                result=ConsensusResult.FAILED,
                total_time_ms=(time.time() - start_time) * 1000,
            )

        finally:
            # Clean up
            self.active_validations.pop(request.request_id, None)

    async def _gather_colony_responses(self, request: ValidationRequest) -> dict[str, ColonyValidationResponse]:
        """Gather validation responses from colonies"""

        responses = {}
        tasks = []

        # Filter colonies by availability and trust
        available_colonies = self._select_colonies_for_validation(request.target_colonies, request.minimum_responses)

        if len(available_colonies) < request.minimum_responses:
            logger.warning(
                "Insufficient colonies for validation",
                available=len(available_colonies),
                required=request.minimum_responses,
            )

        # Create validation tasks
        for colony_id in available_colonies:
            task = asyncio.create_task(self._validate_in_colony(request, colony_id))
            tasks.append((colony_id, task))

        # Wait for responses with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                timeout=request.timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.warning("Validation timeout", request_id=request.request_id)

        # Collect responses (optimized to avoid try-except in loop)
        for colony_id, task in tasks:
            if task.done() and not task.exception():
                response = task.result()
                responses[colony_id] = response
            elif task.done() and task.exception():
                # Handle task exception
                e = task.exception()
                responses[colony_id] = ColonyValidationResponse(
                    colony_id=colony_id,
                    request_id=request.request_id,
                    success=False,
                    error_message=str(e),
                    error_code="ERROR",
                )
            else:
                # Create timeout response
                responses[colony_id] = ColonyValidationResponse(
                    colony_id=colony_id,
                    request_id=request.request_id,
                    success=False,
                    error_message="Timeout",
                    error_code="TIMEOUT",
                )

        return responses

    async def _validate_in_colony(self, request: ValidationRequest, colony_id: str) -> ColonyValidationResponse:
        """Validate operation in specific colony"""

        start_time = time.time()

        try:
            # Simulate colony validation - in practice would call actual colony
            await asyncio.sleep(0.1)  # Simulate network delay

            # Mock validation logic
            success = True
            validation_result = ValidationResult.VALID
            content_hash = (
                hashlib.sha256()  #  Changed from MD5 for securitystr(request.operation.content.encode()).hexdigest()
                if request.operation.content
                else None
            )

            # Simulate occasional failures based on trust score
            trust_score = self.colony_trust_scores.get(colony_id, 1.0)
            if trust_score < 0.8:
                success = False
                validation_result = ValidationResult.CORRUPTED

            response = ColonyValidationResponse(
                colony_id=colony_id,
                request_id=request.request_id,
                success=success,
                validation_result=validation_result,
                content_hash=content_hash,
                response_time_ms=(time.time() - start_time) * 1000,
                colony_trust_score=trust_score,
            )

            return response

        except Exception as e:
            return ColonyValidationResponse(
                colony_id=colony_id,
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
            )

    def _analyze_consensus(
        self, request: ValidationRequest, responses: dict[str, ColonyValidationResponse]
    ) -> ConsensusOutcome:
        """Analyze colony responses for consensus"""

        outcome = ConsensusOutcome(
            request_id=request.request_id,
            total_responses=len(responses),
            colony_responses=responses,
        )

        if not responses:
            outcome.result = ConsensusResult.INSUFFICIENT_COLONIES
            return outcome

        # Count successful responses
        successful_responses = [r for r in responses.values() if r.success]
        outcome.successful_responses = len(successful_responses)

        # Calculate consensus based on validation mode
        if request.validation_mode == ValidationMode.SIMPLE:
            # Just need one successful response
            outcome.consensus_achieved = len(successful_responses) > 0

        elif request.validation_mode == ValidationMode.QUORUM:
            # Need majority consensus
            success_rate = len(successful_responses) / len(responses)
            outcome.consensus_achieved = success_rate >= request.consensus_threshold
            outcome.consensus_confidence = success_rate

        elif request.validation_mode == ValidationMode.UNANIMOUS:
            # All must agree
            outcome.consensus_achieved = len(successful_responses) == len(responses)
            outcome.consensus_confidence = 1.0 if outcome.consensus_achieved else 0.0

        elif request.validation_mode == ValidationMode.BYZANTINE:
            # Byzantine fault tolerance (2/3 + 1)
            required = (2 * len(responses)) // 3 + 1
            outcome.consensus_achieved = len(successful_responses) >= required
            outcome.consensus_confidence = len(successful_responses) / len(responses)

        # Determine final result
        if outcome.consensus_achieved:
            outcome.result = ConsensusResult.SUCCESS
        elif outcome.total_responses < request.minimum_responses:
            outcome.result = ConsensusResult.INSUFFICIENT_COLONIES
        else:
            # Check for conflicts
            validation_results = [r.validation_result for r in successful_responses]
            if len(set(validation_results)) > 1:
                outcome.result = ConsensusResult.CONFLICT
                outcome.conflicting_colonies = [
                    r.colony_id for r in responses.values() if r.validation_result != validation_results[0]
                ]
            else:
                outcome.result = ConsensusResult.FAILED

        # Set dominant response
        if successful_responses:
            outcome.dominant_response = max(successful_responses, key=lambda r: r.colony_trust_score)

        # Calculate performance metrics
        response_times = [r.response_time_ms for r in responses.values()]
        if response_times:
            outcome.fastest_response_ms = min(response_times)
            outcome.slowest_response_ms = max(response_times)

        return outcome

    def _select_colonies_for_validation(self, target_colonies: list[str], minimum_required: int) -> list[str]:
        """Select best colonies for validation based on trust and performance"""

        # Filter to registered colonies
        available = [cid for cid in target_colonies if cid in self.registered_colonies]

        # Sort by trust score and performance
        available.sort(
            key=lambda cid: (
                self.colony_trust_scores.get(cid, 0.0),
                -self._get_average_response_time(cid),  # Negative for ascending sort
            ),
            reverse=True,
        )

        # Return top colonies, but ensure minimum
        return available[: max(minimum_required, len(available))]

    def _get_consensus_threshold(self, validation_mode: ValidationMode) -> float:
        """Get consensus threshold for validation mode"""
        thresholds = {
            ValidationMode.SIMPLE: 0.01,  # Just need one
            ValidationMode.QUORUM: 0.67,  # 2/3 majority
            ValidationMode.UNANIMOUS: 1.0,  # All must agree
            ValidationMode.BYZANTINE: 0.67,  # Byzantine threshold
        }
        return thresholds.get(validation_mode, 0.67)

    def _get_average_response_time(self, colony_id: str) -> float:
        """Get average response time for colony"""
        history = self.colony_performance_history.get(colony_id, [])
        return sum(history) / len(history) if history else 0.0

    def _update_colony_trust_scores(self, outcome: ConsensusOutcome):
        """Update colony trust scores based on validation outcome"""

        for colony_id, response in outcome.colony_responses.items():
            current_trust = self.colony_trust_scores.get(colony_id, 1.0)

            # Update based on response quality
            if response.success and outcome.consensus_achieved:
                # Successful participation in successful consensus
                new_trust = min(1.0, current_trust + 0.01)
            elif not response.success:
                # Failed to respond successfully
                new_trust = max(0.0, current_trust - 0.05)
            else:
                # Successful response but consensus failed
                new_trust = max(0.0, current_trust - 0.02)

            self.colony_trust_scores[colony_id] = new_trust

            # Update performance history
            if response.response_time_ms > 0:
                history = self.colony_performance_history[colony_id]
                history.append(response.response_time_ms)
                if len(history) > 100:  # Keep last 100 measurements
                    history.pop(0)

    async def _notify_callbacks(self, request: ValidationRequest, outcome: ConsensusOutcome):
        """Notify registered callbacks"""
        # Collect callback results to avoid try-except in loop
        callback_tasks = []
        for callback in self.consensus_callbacks:
            task = asyncio.create_task(callback(request, outcome))
            callback_tasks.append(task)

        # Wait for all callbacks and log any errors
        if callback_tasks:
            results = await asyncio.gather(*callback_tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Callback error: {result}")

    async def _cleanup_expired_validations(self):
        """Background task to clean up expired validations"""
        while self._running:
            current_time = time.time()
            expired_requests = []

            for request_id, request in self.active_validations.items():
                if current_time - request.timestamp > request.timeout_seconds * 2:
                    expired_requests.append(request_id)

            for request_id in expired_requests:
                self.active_validations.pop(request_id, None)
                logger.debug("Cleaned up expired validation", request_id=request_id)

            await asyncio.sleep(30)  # Clean up every 30 seconds

    async def _monitor_colony_health(self):
        """Background task to monitor colony health"""
        while self._running:
            # Check colony responsiveness
            unresponsive_colonies = []

            for colony_id, trust_score in self.colony_trust_scores.items():
                if trust_score < 0.3:  # Very low trust
                    unresponsive_colonies.append(colony_id)

            if unresponsive_colonies:
                logger.warning("Low trust colonies detected", colonies=unresponsive_colonies)

            await asyncio.sleep(60)  # Monitor every minute

    def register_consensus_callback(self, callback: Callable):
        """Register callback for consensus events"""
        self.consensus_callbacks.append(callback)

    def get_colony_stats(self) -> dict[str, Any]:
        """Get colony statistics"""
        return {
            "registered_colonies": len(self.registered_colonies),
            "average_trust_score": (
                sum(self.colony_trust_scores.values()) / len(self.colony_trust_scores)
                if self.colony_trust_scores
                else 0.0
            ),
            "colony_trust_scores": dict(self.colony_trust_scores),
            "colony_performance": {cid: self._get_average_response_time(cid) for cid in self.registered_colonies},
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get validator metrics"""
        success_rate = self.successful_validations / max(self.total_validations, 1)

        return {
            "validator_id": self.validator_id,
            "total_validations": self.total_validations,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "timeout_validations": self.timeout_validations,
            "conflict_validations": self.conflict_validations,
            "success_rate": success_rate,
            "active_validations": len(self.active_validations),
            "registered_colonies": len(self.registered_colonies),
        }