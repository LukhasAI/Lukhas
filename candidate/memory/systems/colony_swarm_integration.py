#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🐝 LUKHAS AI - COLONY/SWARM MEMORY INTEGRATION
║ Distributed consensus validation for multi-agent memories
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: colony_swarm_integration.py
║ Path: memory/systems/colony_swarm_integration.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Swarm Intelligence Team
╠══════════════════════════════════════════════════════════════════════════════════
║ ΛTAG: ΛMEMORY, ΛCOLONY, ΛSWARM, ΛCONSENSUS, ΛDISTRIBUTED
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from .integration_adapters import (
    MemorySafetyIntegration,
)
from .memory_safety_features import MemorySafetySystem


class ColonyRole(Enum):
    """Roles that colonies can play in memory validation"""

    VALIDATOR = "validator"
    WITNESS = "witness"
    ARBITER = "arbiter"
    SPECIALIST = "specialist"


@dataclass
class ColonyProfile:
    """Profile for a colony in the swarm"""

    colony_id: str
    role: ColonyRole
    specializations: list[str] = field(default_factory=list)
    trust_score: float = 1.0
    validation_count: int = 0
    consensus_weight: float = 1.0
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ColonyMemoryValidator:
    """
    Individual colony validator for memory consensus.

    Each colony can have its own validation logic based on its role.
    """

    def __init__(
        self,
        colony_id: str,
        role: ColonyRole,
        specializations: Optional[list[str]] = None,
    ):
        self.colony_id = colony_id
        self.role = role
        self.specializations = specializations or []
        self.validation_history: list[dict[str, Any]] = []

    async def validate_memory(
        self, memory_id: str, memory_data: dict[str, Any]
    ) -> tuple[bool, float, Optional[str]]:
        """
        Validate memory based on colony's role and specialization.

        Returns: (is_valid, confidence, reason)
        """
        validation_result = {
            "memory_id": memory_id,
            "timestamp": datetime.now(timezone.utc),
            "colony_id": self.colony_id,
        }

        try:
            # Role-based validation
            if self.role == ColonyRole.VALIDATOR:
                result = await self._validate_general(memory_data)
            elif self.role == ColonyRole.WITNESS:
                result = await self._validate_as_witness(memory_data)
            elif self.role == ColonyRole.ARBITER:
                result = await self._validate_as_arbiter(memory_data)
            elif self.role == ColonyRole.SPECIALIST:
                result = await self._validate_specialized(memory_data)
            else:
                result = (True, 0.5, "Unknown role")

            validation_result["result"] = result
            self.validation_history.append(validation_result)

            return result

        except Exception as e:
            logger.error("Colony validation failed", colony_id=self.colony_id, error=str(e))
            return False, 0.0, f"Validation error: {e!s}"

    async def _validate_general(
        self, memory_data: dict[str, Any]
    ) -> tuple[bool, float, Optional[str]]:
        """General validation logic"""
        # Check basic structure
        required_fields = ["content", "timestamp"]
        for field in required_fields:
            if field not in memory_data:
                return False, 0.0, f"Missing required field: {field}"

        # Check timestamp validity
        if "timestamp" in memory_data:
            timestamp = memory_data["timestamp"]
            if isinstance(timestamp, datetime):
                # Future check
                if timestamp > datetime.now(timezone.utc):
                    return False, 0.0, "Future timestamp"

        # Content analysis
        content = str(memory_data.get("content", ""))
        if len(content) < 3:
            return False, 0.2, "Content too short"

        # Calculate confidence based on data completeness
        total_fields = len(memory_data)
        confidence = min(1.0, total_fields / 10)  # More fields = higher confidence

        return True, confidence, None

    async def _validate_as_witness(
        self, memory_data: dict[str, Any]
    ) -> tuple[bool, float, Optional[str]]:
        """Witness validation - confirms observations"""
        # Witnesses validate experiential memories
        if memory_data.get("type") in ["observation", "experience", "sensory"]:
            # Check for sensory details
            sensory_fields = ["visual", "audio", "emotion", "context"]
            sensory_count = sum(1 for field in sensory_fields if field in memory_data)

            if sensory_count >= 2:
                return True, 0.8 + (sensory_count * 0.05), None
            else:
                return True, 0.5, "Limited sensory data"

        # Not a witness-type memory
        return True, 0.3, "Not witness domain"

    async def _validate_as_arbiter(
        self, memory_data: dict[str, Any]
    ) -> tuple[bool, float, Optional[str]]:
        """Arbiter validation - resolves conflicts"""
        # Arbiters look for logical consistency
        content = str(memory_data.get("content", "")).lower()

        # Check for contradictory terms
        contradictions = [
            ("always", "never"),
            ("all", "none"),
            ("true", "false"),
            ("yes", "no"),
        ]

        for term1, term2 in contradictions:
            if term1 in content and term2 in content:
                return False, 0.1, f"Contains contradiction: {term1} vs {term2}"

        # Check emotional consistency
        emotion = memory_data.get("emotion")
        if emotion:
            emotion_words = {
                "joy": ["happy", "excited", "wonderful"],
                "sadness": ["sad", "depressed", "terrible"],
                "anger": ["angry", "furious", "rage"],
            }

            if emotion in emotion_words:
                expected_words = emotion_words[emotion]
                matches = sum(1 for word in expected_words if word in content)

                if matches == 0 and len(content) > 20:
                    return True, 0.4, "Emotion-content mismatch"

        return True, 0.9, None

    async def _validate_specialized(
        self, memory_data: dict[str, Any]
    ) -> tuple[bool, float, Optional[str]]:
        """Specialized validation based on colony expertise"""
        memory_type = memory_data.get("type", "")
        memory_tags = memory_data.get("tags", [])

        # Check if memory matches specialization
        relevance_score = 0.0
        for spec in self.specializations:
            if spec in memory_type or spec in str(memory_tags):
                relevance_score = 1.0
                break
            # Partial match
            if any(spec in tag for tag in memory_tags):
                relevance_score = max(relevance_score, 0.7)

        if relevance_score == 0:
            # Not in specialty - defer to others
            return True, 0.1, "Outside specialization"

        # Specialized validation logic would go here
        # For now, trust specialist judgment
        confidence = 0.7 + (relevance_score * 0.3)

        return True, confidence, None


class SwarmConsensusManager:
    """
    Manages distributed consensus across multiple colonies.

    Implements Byzantine fault tolerance for memory validation.
    """

    def __init__(
        self,
        safety_integration: MemorySafetyIntegration,
        min_colonies: int = 3,
        consensus_threshold: float = 0.66,
    ):
        self.integration = safety_integration
        self.memory = safety_integration.memory
        self.min_colonies = min_colonies
        self.consensus_threshold = consensus_threshold

        self.colonies: dict[str, ColonyProfile] = {}
        self.colony_validators: dict[str, ColonyMemoryValidator] = {}

        # Consensus metrics
        self.consensus_history: list[dict[str, Any]] = []
        self.colony_performance: dict[str, dict[str, float]] = {}

    def register_colony(
        self,
        colony_id: str,
        role: ColonyRole,
        specializations: Optional[list[str]] = None,
    ):
        """Register a new colony in the swarm"""
        # Create profile
        self.colonies[colony_id] = ColonyProfile(
            colony_id=colony_id, role=role, specializations=specializations or []
        )

        # Create validator
        validator = ColonyMemoryValidator(colony_id, role, specializations)
        self.colony_validators[colony_id] = validator

        # Register with consensus adapter
        self.integration.consensus.register_colony_validator(colony_id, validator.validate_memory)

        logger.info(
            "Colony registered",
            colony_id=colony_id,
            role=role.value,
            specializations=specializations,
        )

    async def distributed_memory_storage(
        self, memory_data: dict[str, Any], tags: list[str], proposing_colony: str
    ) -> Optional[str]:
        """
        Store memory with distributed consensus validation.

        Memory is only stored if consensus is reached.
        """
        # Select validating colonies
        validating_colonies = self._select_validators(proposing_colony, tags)

        if len(validating_colonies) < self.min_colonies:
            logger.warning(
                "Insufficient colonies for consensus",
                required=self.min_colonies,
                available=len(validating_colonies),
            )
            return None

        # Collect votes
        votes: dict[str, tuple[bool, float, Optional[str]]] = {}

        for colony_id in validating_colonies:
            if colony_id in self.colony_validators:
                validator = self.colony_validators[colony_id]
                vote = await validator.validate_memory(
                    f"proposed_{proposing_colony}_{datetime.now().timestamp()}",
                    memory_data,
                )
                votes[colony_id] = vote

        # Calculate consensus
        consensus_reached, confidence = self._calculate_consensus(votes)

        # Record consensus event
        consensus_event = {
            "timestamp": datetime.now(timezone.utc),
            "proposing_colony": proposing_colony,
            "validators": validating_colonies,
            "votes": votes,
            "consensus_reached": consensus_reached,
            "confidence": confidence,
        }
        self.consensus_history.append(consensus_event)

        if consensus_reached:
            # Store with consensus metadata
            memory_data["_consensus"] = {
                "validators": list(votes.keys()),
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc),
            }

            # Store memory
            memory_id = await self.memory.fold_in_with_embedding(
                data=memory_data,
                tags=tags + [f"colony:{proposing_colony}", "consensus_validated"],
                text_content=memory_data.get("content", ""),
            )

            # Update colony performance
            self._update_colony_performance(votes, success=True)

            logger.info(
                "Memory stored with consensus",
                memory_id=memory_id,
                confidence=confidence,
                validators=len(votes),
            )

            return memory_id
        else:
            # Update colony performance
            self._update_colony_performance(votes, success=False)

            logger.warning("Consensus not reached", confidence=confidence, votes=votes)

            return None

    def _select_validators(self, proposing_colony: str, tags: list[str]) -> list[str]:
        """Select colonies to validate based on tags and roles"""
        validators = []

        # Always include arbiters
        for colony_id, profile in self.colonies.items():
            if colony_id != proposing_colony and profile.role == ColonyRole.ARBITER:
                validators.append(colony_id)

        # Add specialists if tags match
        for colony_id, profile in self.colonies.items():
            if colony_id != proposing_colony and colony_id not in validators:
                if profile.role == ColonyRole.SPECIALIST:
                    # Check if any specialization matches tags
                    if any(spec in tags for spec in profile.specializations):
                        validators.append(colony_id)

        # Add validators to reach minimum
        for colony_id, profile in self.colonies.items():
            if colony_id != proposing_colony and colony_id not in validators:
                if profile.role == ColonyRole.VALIDATOR:
                    validators.append(colony_id)
                    if len(validators) >= self.min_colonies * 2:
                        break

        # Add witnesses if still need more
        if len(validators) < self.min_colonies:
            for colony_id, profile in self.colonies.items():
                if colony_id != proposing_colony and colony_id not in validators:
                    if profile.role == ColonyRole.WITNESS:
                        validators.append(colony_id)
                        if len(validators) >= self.min_colonies:
                            break

        return validators

    def _calculate_consensus(
        self, votes: dict[str, tuple[bool, float, Optional[str]]]
    ) -> tuple[bool, float]:
        """Calculate weighted consensus from votes"""
        if not votes:
            return False, 0.0

        # Weight votes by colony trust and confidence
        weighted_sum = 0.0
        total_weight = 0.0

        for colony_id, (is_valid, confidence, _) in votes.items():
            if colony_id in self.colonies:
                colony = self.colonies[colony_id]
                weight = colony.trust_score * colony.consensus_weight

                if is_valid:
                    weighted_sum += weight * confidence

                total_weight += weight

        if total_weight == 0:
            return False, 0.0

        consensus_score = weighted_sum / total_weight
        consensus_reached = consensus_score >= self.consensus_threshold

        return consensus_reached, consensus_score

    def _update_colony_performance(
        self, votes: dict[str, tuple[bool, float, Optional[str]]], success: bool
    ):
        """Update colony performance metrics"""
        # Determine majority vote
        positive_votes = sum(1 for v, _, _ in votes.values() if v)
        positive_votes > len(votes) / 2

        for colony_id, (vote, confidence, _) in votes.items():
            if colony_id not in self.colony_performance:
                self.colony_performance[colony_id] = {
                    "correct_votes": 0,
                    "total_votes": 0,
                    "avg_confidence": 0.0,
                }

            perf = self.colony_performance[colony_id]
            perf["total_votes"] += 1

            # Colony was correct if it voted with consensus
            if (vote and success) or (not vote and not success):
                perf["correct_votes"] += 1

            # Update average confidence
            perf["avg_confidence"] = (
                perf["avg_confidence"] * (perf["total_votes"] - 1) + confidence
            ) / perf["total_votes"]

            # Update colony trust score
            if colony_id in self.colonies:
                accuracy = perf["correct_votes"] / perf["total_votes"]
                self.colonies[colony_id].trust_score = accuracy

    async def query_with_consensus(
        self, query: str, requesting_colony: str, min_confirmations: int = 2
    ) -> list[tuple[Any, float]]:
        """
        Query memories with multi-colony confirmation.

        Returns only memories confirmed by multiple colonies.
        """
        # Get candidate memories
        candidates = await self.memory.fold_out_semantic(query, top_k=20)

        confirmed_memories = []

        for memory, base_score in candidates:
            # Get confirmations from other colonies
            confirmations = 0
            total_confidence = 0.0

            validators = self._select_validators(
                requesting_colony, list(self.memory.get_item_tags(memory.item_id))
            )[: min_confirmations + 1]

            for colony_id in validators:
                if colony_id in self.colony_validators:
                    validator = self.colony_validators[colony_id]
                    is_valid, confidence, _ = await validator.validate_memory(
                        memory.item_id, memory.data
                    )

                    if is_valid:
                        confirmations += 1
                        total_confidence += confidence

            if confirmations >= min_confirmations:
                # Calculate final score
                avg_confidence = total_confidence / confirmations
                final_score = base_score * avg_confidence
                confirmed_memories.append((memory, final_score))

        # Sort by final score
        confirmed_memories.sort(key=lambda x: x[1], reverse=True)

        return confirmed_memories

    def get_swarm_status(self) -> dict[str, Any]:
        """Get current swarm consensus status"""
        active_colonies = [
            c
            for c in self.colonies.values()
            if (datetime.now(timezone.utc) - c.last_active).total_seconds() < 3600
        ]

        role_distribution = {}
        for colony in self.colonies.values():
            role = colony.role.value
            role_distribution[role] = role_distribution.get(role, 0) + 1

        # Calculate swarm health
        total_validations = sum(p["total_votes"] for p in self.colony_performance.values())

        avg_accuracy = 0.0
        if self.colony_performance:
            accuracies = [
                p["correct_votes"] / p["total_votes"]
                for p in self.colony_performance.values()
                if p["total_votes"] > 0
            ]
            avg_accuracy = np.mean(accuracies) if accuracies else 0.0

        recent_consensus = []
        if len(self.consensus_history) > 10:
            recent = self.consensus_history[-10:]
            recent_consensus = [event["consensus_reached"] for event in recent]

        return {
            "total_colonies": len(self.colonies),
            "active_colonies": len(active_colonies),
            "role_distribution": role_distribution,
            "total_validations": total_validations,
            "average_accuracy": avg_accuracy,
            "consensus_threshold": self.consensus_threshold,
            "recent_consensus_rate": (
                sum(recent_consensus) / len(recent_consensus) if recent_consensus else 0.0
            ),
            "top_performers": sorted(
                [
                    {
                        "colony_id": cid,
                        "accuracy": p["correct_votes"] / p["total_votes"],
                        "validations": p["total_votes"],
                    }
                    for cid, p in self.colony_performance.items()
                    if p["total_votes"] > 0
                ],
                key=lambda x: x["accuracy"],
                reverse=True,
            )[:5],
        }


# Example usage
async def demonstrate_colony_swarm():
    """Demonstrate colony/swarm consensus validation"""
    from .hybrid_memory_fold import create_hybrid_memory_fold

    # Create systems
    memory = create_hybrid_memory_fold()
    safety = MemorySafetySystem()
    integration = MemorySafetyIntegration(safety, memory)

    # Create swarm manager
    swarm = SwarmConsensusManager(integration, min_colonies=3)

    # Register colonies with different roles
    swarm.register_colony("colony_alpha", ColonyRole.VALIDATOR)
    swarm.register_colony("colony_beta", ColonyRole.WITNESS)
    swarm.register_colony("colony_gamma", ColonyRole.ARBITER)
    swarm.register_colony("colony_delta", ColonyRole.SPECIALIST, ["technical", "science"])
    swarm.register_colony("colony_epsilon", ColonyRole.SPECIALIST, ["creative", "emotional"])

    print("🐝 COLONY/SWARM CONSENSUS DEMONSTRATION")
    print("=" * 60)

    # Test 1: Store memory with consensus
    print("\n1. Storing memory with distributed consensus:")

    test_memory = {
        "content": "The distributed swarm successfully validated this memory",
        "type": "technical",
        "importance": 0.8,
        "timestamp": datetime.now(timezone.utc),
    }

    memory_id = await swarm.distributed_memory_storage(
        memory_data=test_memory,
        tags=["technical", "consensus", "test"],
        proposing_colony="colony_alpha",
    )

    if memory_id:
        print(f"✅ Memory stored with consensus: {memory_id}")
    else:
        print("❌ Consensus not reached")

    # Test 2: Try to store conflicting memory
    print("\n2. Attempting to store conflicting memory:")

    conflicting_memory = {
        "content": "This memory contains always and never contradictions",
        "type": "invalid",
        "timestamp": datetime.now(timezone.utc),
    }

    memory_id = await swarm.distributed_memory_storage(
        memory_data=conflicting_memory,
        tags=["test", "conflict"],
        proposing_colony="colony_beta",
    )

    if memory_id:
        print(f"✅ Memory stored: {memory_id}")
    else:
        print("❌ Consensus rejected the memory")

    # Test 3: Query with multi-colony confirmation
    print("\n3. Querying with multi-colony confirmation:")

    # Add a few more test memories
    for i in range(3):
        await swarm.distributed_memory_storage(
            memory_data={
                "content": f"Technical documentation entry {i}",
                "type": "technical",
                "index": i,
                "timestamp": datetime.now(timezone.utc),
            },
            tags=["technical", "documentation"],
            proposing_colony="colony_delta",
        )

    # Query with confirmation
    results = await swarm.query_with_consensus(
        query="technical documentation",
        requesting_colony="colony_alpha",
        min_confirmations=2,
    )

    print(f"Found {len(results)} confirmed memories:")
    for mem, score in results[:3]:
        print(f"  • {mem.data.get('content', '')[:50]}... (score: {score:.3f})")

    # Get swarm status
    print("\n4. Swarm Status Report:")
    status = swarm.get_swarm_status()
    print(f"  Active colonies: {status['active_colonies']}/{status['total_colonies']}")
    print(f"  Role distribution: {status['role_distribution']}")
    print(f"  Average accuracy: {status['average_accuracy']:.2%}")
    print(f"  Recent consensus rate: {status['recent_consensus_rate']:.2%}")

    if status["top_performers"]:
        print("\n  Top performing colonies:")
        for perf in status["top_performers"][:3]:
            print(
                f"    • {perf['colony_id']}: {perf['accuracy']:.2%} accuracy ({perf['validations']} validations)"
            )

    print("\n✅ Colony/Swarm demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_colony_swarm())
