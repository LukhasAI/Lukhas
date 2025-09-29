"""
Biometric Verification Colony

Distributed colony of specialized agents for parallel biometric analysis,
consensus-based verification, and self-healing sensor failure recovery.
"""
import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np

# Import colony infrastructure
from lukhas.core.colonies.base_colony import BaseColony, ConsensusResult
from lukhas.core.enhanced_swarm import AgentCapability, AgentState
from lukhas.core.enhanced_swarm import EnhancedSwarmAgent as SwarmAgent

# Import identity events
try:
    from governance.identity.core.events import (
        IdentityEventPublisher,
        IdentityEventType,
        VerificationResult,
    )
except ImportError:
    IdentityEventPublisher = None
    IdentityEventType = None
    VerificationResult = None

logger = logging.getLogger("LUKHAS_BIOMETRIC_COLONY")


class BiometricType(Enum):
    """Types of biometric data for verification."""

    FINGERPRINT = "fingerprint"
    FACIAL = "facial"
    IRIS = "iris"
    VOICE = "voice"
    GAIT = "gait"
    HEARTBEAT = "heartbeat"
    BRAINWAVE = "brainwave"
    TYPING_PATTERN = "typing_pattern"
    BEHAVIORAL = "behavioral"


class BiometricQuality(Enum):
    """Quality levels of biometric samples."""

    EXCELLENT = 0.9
    GOOD = 0.7
    FAIR = 0.5
    POOR = 0.3
    UNUSABLE = 0.1


@dataclass
class BiometricSample:
    """Represents a biometric sample for analysis."""

    sample_id: str
    biometric_type: BiometricType
    raw_data: bytes
    quality_score: float
    capture_timestamp: datetime
    device_id: str
    environmental_factors: dict[str, Any]
    preprocessing_applied: list[str]


@dataclass
class BiometricVerificationTask:
    """Task for biometric verification agents."""

    task_id: str
    lambda_id: str
    biometric_samples: list[BiometricSample]
    reference_template: Optional[bytes]
    verification_threshold: float
    tier_level: int
    required_confidence: float
    max_processing_time: float


class BiometricVerificationAgent(SwarmAgent):
    """
    Specialized agent for biometric verification tasks.
    Each agent focuses on specific biometric types or analysis methods.
    """

    def __init__(
        self,
        agent_id: str,
        colony: "BiometricVerificationColony",
        specialization: BiometricType,
    ):
        super().__init__(agent_id, colony, capabilities=[specialization.value])
        self.specialization = specialization
        self.verification_history: list[dict[str, Any]] = []
        self.success_rate = 0.8
        self.processing_speed = 1.0

        # Agent-specific capabilities
        self.capabilities[specialization.value] = AgentCapability(
            name=specialization.value, proficiency=0.8, experience=0, success_rate=0.8
        )

        # Performance tracking
        self.verifications_performed = 0
        self.false_positives = 0
        self.false_negatives = 0

        logger.info(f"Biometric agent {agent_id} initialized for {specialization.value}")

    async def process_biometric_sample(self, sample: BiometricSample, reference_template: bytes) -> dict[str, Any]:
        """Process a single biometric sample."""
        start_time = time.time()

        try:
            # Simulate biometric processing based on type
            if sample.biometric_type != self.specialization:
                return {
                    "success": False,
                    "error": f"Agent specializes in {self.specialization.value}, not {sample.biometric_type.value}",
                }

            # Quality check
            if sample.quality_score < BiometricQuality.POOR.value:
                return {
                    "success": False,
                    "error": "Sample quality too low",
                    "quality_score": sample.quality_score,
                }

            # Simulate feature extraction and matching
            extracted_features = await self._extract_features(sample)
            match_score = await self._match_features(extracted_features, reference_template)

            # Apply quality-adjusted scoring
            adjusted_score = match_score * (0.7 + 0.3 * sample.quality_score)

            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(adjusted_score, sample.quality_score)

            processing_time = time.time() - start_time

            result = {
                "success": True,
                "match_score": adjusted_score,
                "confidence": confidence,
                "processing_time": processing_time,
                "quality_factors": {
                    "sample_quality": sample.quality_score,
                    "environmental_impact": self._assess_environmental_impact(sample.environmental_factors),
                },
                "agent_id": self.agent_id,
                "specialization": self.specialization.value,
            }

            # Update agent performance
            self.verifications_performed += 1
            self.capabilities[self.specialization.value].experience += 1

            return result

        except Exception as e:
            logger.error(f"Biometric processing error in agent {self.agent_id}: {e}")
            return {"success": False, "error": str(e), "agent_id": self.agent_id}

    async def _extract_features(self, sample: BiometricSample) -> np.ndarray:
        """Extract features from biometric sample."""
        # Simulate feature extraction with processing delay
        processing_delay = 0.1 / self.processing_speed
        await asyncio.sleep(processing_delay)

        # Generate pseudo-features based on sample data
        feature_vector = np.frombuffer(hashlib.sha256(sample.raw_data).digest(), dtype=np.float32)

        # Apply specialization-specific processing
        if self.specialization == BiometricType.FACIAL:
            # Simulate facial landmark extraction
            feature_vector = feature_vector[:128]  # 128-dimensional face encoding
        elif self.specialization == BiometricType.FINGERPRINT:
            # Simulate minutiae extraction
            feature_vector = feature_vector[:64]  # Minutiae points
        elif self.specialization == BiometricType.VOICE:
            # Simulate voice spectral features
            feature_vector = feature_vector[:256]  # Voice features

        return feature_vector

    async def _match_features(self, features: np.ndarray, reference: bytes) -> float:
        """Match extracted features against reference template."""
        # Extract reference features
        ref_features = np.frombuffer(hashlib.sha256(reference).digest(), dtype=np.float32)[: len(features)]

        # Calculate similarity score using cosine similarity
        similarity = np.dot(features, ref_features) / (np.linalg.norm(features) * np.linalg.norm(ref_features))

        # Normalize to 0-1 range
        match_score = (similarity + 1) / 2

        # Add agent proficiency factor
        proficiency = self.capabilities[self.specialization.value].proficiency
        match_score = match_score * (0.8 + 0.2 * proficiency)

        return float(match_score)

    def _calculate_confidence(self, match_score: float, quality_score: float) -> float:
        """Calculate confidence in verification result."""
        # Base confidence on match score
        confidence = match_score

        # Adjust for quality
        quality_factor = 0.7 + 0.3 * quality_score
        confidence *= quality_factor

        # Adjust for agent experience
        experience = self.capabilities[self.specialization.value].experience
        experience_factor = min(1.0, 0.8 + experience / 100)
        confidence *= experience_factor

        return min(1.0, confidence)

    def _assess_environmental_impact(self, factors: dict[str, Any]) -> float:
        """Assess impact of environmental factors on biometric quality."""
        impact_score = 1.0

        # Check various environmental factors
        if factors.get("lighting", "good") == "poor":
            impact_score *= 0.8
        if factors.get("noise_level", "low") == "high":
            impact_score *= 0.85
        if factors.get("motion", "stable") == "unstable":
            impact_score *= 0.75

        return impact_score


class BiometricVerificationColony(BaseColony):
    """
    Colony for distributed biometric verification with consensus mechanisms.
    """

    def __init__(self, colony_id: str = "biometric_verification"):
        super().__init__(
            colony_id=colony_id,
            capabilities=["biometric_verification", "consensus_voting", "self_healing"],
        )

        self.verification_agents: dict[str, BiometricVerificationAgent] = {}
        self.event_publisher: Optional[IdentityEventPublisher] = None

        # Colony configuration
        self.min_agents_per_type = 3
        self.consensus_threshold = 0.67
        self.verification_timeout = 10.0  # seconds

        # Performance metrics
        self.total_verifications = 0
        self.successful_verifications = 0
        self.consensus_failures = 0
        self.healing_events = 0

        # Self-healing configuration
        self.agent_health_threshold = 0.6
        self.max_consecutive_failures = 3

        logger.info(f"Biometric Verification Colony {colony_id} initialized")

    async def initialize(self):
        """Initialize the colony with specialized agents."""
        await super().initialize()

        # Get event publisher
        from governance.identity.core.events import get_identity_event_publisher

        self.event_publisher = await get_identity_event_publisher()

        # Create specialized agents for each biometric type
        agent_count = 0
        for biometric_type in BiometricType:
            for i in range(self.min_agents_per_type):
                agent_id = f"{self.colony_id}_agent_{biometric_type.value}_{i}"
                agent = BiometricVerificationAgent(agent_id, self, biometric_type)

                self.verification_agents[agent_id] = agent
                self.agents[agent_id] = agent
                agent_count += 1

        logger.info(f"Colony initialized with {agent_count} specialized agents")

        # Publish colony initialization event
        await self.event_publisher.publish_colony_event(
            IdentityEventType.COLONY_VERIFICATION_START,
            lambda_id="system",
            tier_level=0,
            colony_id=self.colony_id,
            consensus_data={"agent_count": agent_count},
        )

    async def verify_biometric_identity(
        self,
        lambda_id: str,
        biometric_samples: list[BiometricSample],
        reference_template: bytes,
        tier_level: int,
        session_id: Optional[str] = None,
    ) -> VerificationResult:
        """
        Perform distributed biometric verification with consensus.
        """
        verification_start = time.time()
        task_id = f"bio_verify_{lambda_id}_{int(verification_start)}"

        # Create verification task
        task = BiometricVerificationTask(
            task_id=task_id,
            lambda_id=lambda_id,
            biometric_samples=biometric_samples,
            reference_template=reference_template,
            verification_threshold=self._get_verification_threshold(tier_level),
            tier_level=tier_level,
            required_confidence=self._get_required_confidence(tier_level),
            max_processing_time=self.verification_timeout,
        )

        # Publish verification start event
        correlation_id = await self.event_publisher.publish_verification_event(
            IdentityEventType.VERIFICATION_START,
            lambda_id=lambda_id,
            tier_level=tier_level,
            colony_id=self.colony_id,
            correlation_id=task_id,
        )

        try:
            # Group samples by biometric type
            samples_by_type = self._group_samples_by_type(biometric_samples)

            # Process each biometric type in parallel
            verification_tasks = []
            for biometric_type, samples in samples_by_type.items():
                task_coro = self._verify_biometric_type(task, biometric_type, samples, reference_template)
                verification_tasks.append(task_coro)

            # Wait for all verifications with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*verification_tasks, return_exceptions=True),
                timeout=self.verification_timeout,
            )

            # Aggregate results and build consensus
            consensus_result = await self._build_verification_consensus(results, task, tier_level)

            # Create verification result
            verification_result = VerificationResult(
                verified=consensus_result.consensus_reached and consensus_result.decision,
                confidence_score=consensus_result.confidence,
                verification_method="distributed_biometric_consensus",
                colony_consensus={
                    "votes": consensus_result.votes,
                    "participation_rate": consensus_result.participation_rate,
                    "consensus_strength": consensus_result.confidence,
                },
                failure_reasons=(consensus_result.dissent_reasons if not consensus_result.decision else []),
                verification_duration_ms=(time.time() - verification_start) * 1000,
                agents_involved=len([r for r in results if isinstance(r, dict)]),
            )

            # Update metrics
            self.total_verifications += 1
            if verification_result.verified:
                self.successful_verifications += 1

            # Publish completion event
            await self.event_publisher.publish_verification_event(
                IdentityEventType.VERIFICATION_COMPLETE,
                lambda_id=lambda_id,
                tier_level=tier_level,
                verification_result=verification_result,
                colony_id=self.colony_id,
                correlation_id=correlation_id,
            )

            return verification_result

        except asyncio.TimeoutError:
            logger.error(f"Biometric verification timeout for {lambda_id}")

            # Create timeout result
            verification_result = VerificationResult(
                verified=False,
                confidence_score=0.0,
                verification_method="distributed_biometric_consensus",
                failure_reasons=["Verification timeout"],
                verification_duration_ms=(time.time() - verification_start) * 1000,
                agents_involved=0,
            )

            # Publish failure event
            await self.event_publisher.publish_verification_event(
                IdentityEventType.VERIFICATION_FAILED,
                lambda_id=lambda_id,
                tier_level=tier_level,
                verification_result=verification_result,
                colony_id=self.colony_id,
                correlation_id=correlation_id,
            )

            # Trigger healing for timeout
            await self._trigger_timeout_healing(task_id)

            return verification_result

        except Exception as e:
            logger.error(f"Biometric verification error: {e}")

            # Create error result
            verification_result = VerificationResult(
                verified=False,
                confidence_score=0.0,
                verification_method="distributed_biometric_consensus",
                failure_reasons=[f"Verification error: {e!s}"],
                verification_duration_ms=(time.time() - verification_start) * 1000,
                agents_involved=0,
            )

            return verification_result

    async def _verify_biometric_type(
        self,
        task: BiometricVerificationTask,
        biometric_type: BiometricType,
        samples: list[BiometricSample],
        reference_template: bytes,
    ) -> dict[str, Any]:
        """Verify samples of a specific biometric type using specialized agents."""

        # Get agents specialized in this biometric type
        specialized_agents = [
            agent
            for agent in self.verification_agents.values()
            if agent.specialization == biometric_type and agent.state != AgentState.FAILED
        ]

        if not specialized_agents:
            logger.warning(f"No healthy agents available for {biometric_type.value}")
            return {
                "biometric_type": biometric_type.value,
                "success": False,
                "error": "No specialized agents available",
            }

        # Distribute samples across agents
        agent_results = []
        for i, sample in enumerate(samples):
            agent = specialized_agents[i % len(specialized_agents)]
            result = await agent.process_biometric_sample(sample, reference_template)
            agent_results.append(result)

        # Aggregate results for this biometric type
        successful_results = [r for r in agent_results if r.get("success", False)]

        if not successful_results:
            return {
                "biometric_type": biometric_type.value,
                "success": False,
                "error": "All agents failed to process samples",
            }

        # Calculate aggregate scores
        avg_match_score = np.mean([r["match_score"] for r in successful_results])
        avg_confidence = np.mean([r["confidence"] for r in successful_results])

        return {
            "biometric_type": biometric_type.value,
            "success": True,
            "match_score": avg_match_score,
            "confidence": avg_confidence,
            "samples_processed": len(successful_results),
            "agent_results": successful_results,
        }

    async def _build_verification_consensus(
        self,
        results: list[dict[str, Any]],
        task: BiometricVerificationTask,
        tier_level: int,
    ) -> ConsensusResult:
        """Build consensus from multiple biometric verification results."""

        # Filter successful results
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success", False)]

        if not successful_results:
            return ConsensusResult(
                consensus_reached=False,
                decision=False,
                confidence=0.0,
                votes={},
                participation_rate=0.0,
                dissent_reasons=["No successful verifications"],
            )

        # Calculate weighted votes based on biometric type and confidence
        votes = {}
        total_weight = 0.0

        for result in successful_results:
            biometric_type = result["biometric_type"]
            confidence = result["confidence"]
            match_score = result["match_score"]

            # Determine if this result votes for verification
            vote = match_score >= task.verification_threshold

            # Weight based on tier level and biometric type
            weight = self._calculate_vote_weight(biometric_type, confidence, tier_level)

            votes[f"{biometric_type}_{result.get('samples_processed', 1)}"] = {
                "vote": vote,
                "weight": weight,
                "confidence": confidence,
            }

            total_weight += weight

        # Calculate consensus
        positive_weight = sum(v["weight"] for v in votes.values() if v["vote"])
        consensus_ratio = positive_weight / total_weight if total_weight > 0 else 0

        # Adjust consensus threshold based on tier
        required_consensus = self._get_consensus_threshold(tier_level)
        consensus_reached = consensus_ratio >= required_consensus

        # Calculate overall confidence
        confidence_scores = [v["confidence"] * v["weight"] for v in votes.values()]
        overall_confidence = sum(confidence_scores) / total_weight if total_weight > 0 else 0

        # Identify dissent reasons
        dissent_reasons = []
        for biometric_type, vote_data in votes.items():
            if not vote_data["vote"]:
                dissent_reasons.append(f"{biometric_type} match below threshold")

        return ConsensusResult(
            consensus_reached=consensus_reached,
            decision=consensus_reached and consensus_ratio >= required_consensus,
            confidence=overall_confidence,
            votes={k: v["vote"] for k, v in votes.items()},
            participation_rate=len(successful_results) / len(results) if results else 0,
            dissent_reasons=dissent_reasons,
        )

    def _group_samples_by_type(self, samples: list[BiometricSample]) -> dict[BiometricType, list[BiometricSample]]:
        """Group biometric samples by type."""
        grouped = {}
        for sample in samples:
            if sample.biometric_type not in grouped:
                grouped[sample.biometric_type] = []
            grouped[sample.biometric_type].append(sample)
        return grouped

    def _get_verification_threshold(self, tier_level: int) -> float:
        """Get verification threshold based on tier level."""
        thresholds = {
            0: 0.6,  # Guest
            1: 0.65,  # Basic
            2: 0.7,  # Standard
            3: 0.75,  # Professional
            4: 0.8,  # Premium
            5: 0.85,  # Transcendent
        }
        return thresholds.get(tier_level, 0.7)

    def _get_required_confidence(self, tier_level: int) -> float:
        """Get required confidence based on tier level."""
        confidence_levels = {
            0: 0.5,  # Guest
            1: 0.6,  # Basic
            2: 0.65,  # Standard
            3: 0.7,  # Professional
            4: 0.75,  # Premium
            5: 0.8,  # Transcendent
        }
        return confidence_levels.get(tier_level, 0.65)

    def _get_consensus_threshold(self, tier_level: int) -> float:
        """Get consensus threshold based on tier level."""
        if tier_level <= 2:
            return 0.51  # Simple majority
        elif tier_level <= 4:
            return 0.67  # Two-thirds majority
        else:
            return 0.8  # 80% consensus for Tier 5

    def _calculate_vote_weight(self, biometric_type: str, confidence: float, tier_level: int) -> float:
        """Calculate vote weight based on biometric type and tier."""
        # Base weights for different biometric types
        type_weights = {
            BiometricType.FINGERPRINT.value: 1.0,
            BiometricType.FACIAL.value: 0.9,
            BiometricType.IRIS.value: 1.2,
            BiometricType.VOICE.value: 0.8,
            BiometricType.HEARTBEAT.value: 0.9,
            BiometricType.BRAINWAVE.value: 1.1,
            BiometricType.BEHAVIORAL.value: 0.7,
        }

        base_weight = type_weights.get(biometric_type, 0.8)

        # Adjust weight based on tier level
        if tier_level >= 4:
            # Higher tiers emphasize advanced biometrics
            if biometric_type in [
                BiometricType.BRAINWAVE.value,
                BiometricType.IRIS.value,
            ]:
                base_weight *= 1.2

        # Apply confidence modifier
        return base_weight * (0.5 + 0.5 * confidence)

    async def _trigger_timeout_healing(self, task_id: str):
        """Trigger healing process for timeout events."""
        self.healing_events += 1

        # Identify slow or failed agents
        slow_agents = []
        for agent_id, agent in self.verification_agents.items():
            if agent.state == AgentState.WORKING:
                slow_agents.append(agent_id)
                # Mark agent as potentially problematic
                agent.state = AgentState.FATIGUED

        # Publish healing event
        if self.event_publisher:
            await self.event_publisher.publish_colony_event(
                IdentityEventType.COLONY_HEALING_TRIGGERED,
                lambda_id="system",
                tier_level=0,
                colony_id=self.colony_id,
                consensus_data={
                    "healing_reason": "verification_timeout",
                    "affected_agents": slow_agents,
                    "task_id": task_id,
                },
            )

        # Initiate agent recovery
        for agent_id in slow_agents:
            await self._recover_agent(agent_id)

    async def _recover_agent(self, agent_id: str):
        """Recover a problematic agent."""
        agent = self.verification_agents.get(agent_id)
        if not agent:
            return

        logger.info(f"Recovering agent {agent_id}")

        # Reset agent state
        agent.state = AgentState.IDLE
        agent.verification_history.clear()

        # Reduce performance temporarily
        agent.processing_speed *= 0.9
        agent.capabilities[agent.specialization.value].proficiency *= 0.95

        # Schedule performance recovery
        asyncio.create_task(self._gradual_performance_recovery(agent_id))

    async def _gradual_performance_recovery(self, agent_id: str):
        """Gradually recover agent performance over time."""
        agent = self.verification_agents.get(agent_id)
        if not agent:
            return

        # Recovery over 5 minutes
        recovery_steps = 10
        recovery_interval = 30  # seconds

        for _ in range(recovery_steps):
            await asyncio.sleep(recovery_interval)

            if agent.state == AgentState.FAILED:
                break

            # Gradually restore performance
            agent.processing_speed = min(1.0, agent.processing_speed * 1.05)
            agent.capabilities[agent.specialization.value].proficiency = min(
                1.0, agent.capabilities[agent.specialization.value].proficiency * 1.02
            )

        logger.info(f"Agent {agent_id} performance recovery complete")

    def get_colony_health_status(self) -> dict[str, Any]:
        """Get comprehensive colony health status."""
        healthy_agents = sum(
            1
            for agent in self.verification_agents.values()
            if agent.state not in [AgentState.FAILED, AgentState.FATIGUED]
        )

        total_agents = len(self.verification_agents)
        health_ratio = healthy_agents / total_agents if total_agents > 0 else 0

        return {
            "colony_id": self.colony_id,
            "health_score": health_ratio,
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "agent_distribution": self._get_agent_distribution(),
            "performance_metrics": {
                "total_verifications": self.total_verifications,
                "successful_verifications": self.successful_verifications,
                "success_rate": self.successful_verifications / max(1, self.total_verifications),
                "consensus_failures": self.consensus_failures,
                "healing_events": self.healing_events,
            },
        }

    def _get_agent_distribution(self) -> dict[str, int]:
        """Get distribution of agents by biometric type."""
        distribution = {}
        for agent in self.verification_agents.values():
            bio_type = agent.specialization.value
            distribution[bio_type] = distribution.get(bio_type, 0) + 1
        return distribution
