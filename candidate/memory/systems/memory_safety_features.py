#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory_safety_features.py
║ Path: memory/systems/memory_safety_features.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🛡️ LUKHAS AI - MEMORY SAFETY FEATURES
║ ║ Hallucination prevention, drift detection, and verification systems
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: MEMORY SAFETY FEATURES
║ ║ Path: memory/systems/memory_safety_features.py
║ ║ Version: 1.0.0 | Created: 2025-07-29
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Description: A sentinel at the gates of memory, ensuring safety and integrity.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the labyrinthine corridors of silicon and code, where shadows of
║ ║ uncertainty flit like phantoms in the twilight of logic, we stand vigilant,
║ ║ guardians of the ephemeral realm where thought meets machine. This
║ ║ module, an ethereal bastion, weaves an intricate tapestry of
║ ║ memory safety features, a delicate yet formidable shield against
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛADVANCED, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import numpy as np


@dataclass
class DriftMetrics:
    """Metrics for tracking semantic drift"""

    tag: str
    current_centroid: Optional[np.ndarray] = None
    historical_centroids: list[np.ndarray] = field(default_factory=list)
    drift_scores: list[float] = field(default_factory=list)
    last_calibration: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_uses: int = 0
    recent_uses: deque = field(default_factory=lambda: deque(maxlen=100))

    def calculate_drift(self) -> float:
        """Calculate current drift score"""
        if not self.historical_centroids or self.current_centroid is None:
            return 0.0

        # Compare current to historical average
        historical_avg = np.mean(self.historical_centroids, axis=0)
        drift = np.linalg.norm(self.current_centroid - historical_avg)

        return float(drift)


@dataclass
class VerifoldEntry:
    """Verification entry for memory integrity"""

    memory_id: str
    collapse_hash: str
    creation_time: datetime
    last_verified: datetime
    verification_count: int = 0
    integrity_score: float = 1.0
    suspicious_modifications: list[str] = field(default_factory=list)


class MemorySafetySystem:
    """
    Comprehensive safety system for memory fold operations.

    Prevents:
    - Hallucinations through hash verification
    - Drift through continuous monitoring
    - Corruption through consensus validation
    """

    def __init__(
        self,
        max_drift_threshold: float = 0.5,
        quarantine_threshold: float = 0.8,
        consensus_threshold: int = 3,
    ):
        self.max_drift_threshold = max_drift_threshold
        self.quarantine_threshold = quarantine_threshold
        self.consensus_threshold = consensus_threshold

        # Safety tracking
        self.drift_metrics: dict[str, DriftMetrics] = {}
        self.verifold_registry: dict[str, VerifoldEntry] = {}
        self.quarantine: dict[str, dict[str, Any]] = {}

        # Hallucination prevention
        self.reality_anchors: dict[str, str] = {}  # Known true facts
        self.contradiction_log: list[dict[str, Any]] = []

        logger.info(
            "Memory safety system initialized",
            drift_threshold=max_drift_threshold,
            quarantine_threshold=quarantine_threshold,
        )

    def compute_collapse_hash(self, memory_data: dict[str, Any]) -> str:
        """
        Compute deterministic collapse hash for memory verification.

        This prevents hallucinations by ensuring each memory has
        a unique, verifiable fingerprint.
        """
        # Normalize data for consistent hashing
        normalized = self._normalize_memory_data(memory_data)

        # Multi-stage hashing for security
        stage1 = hashlib.sha256(str(normalized).encode()).hexdigest()
        stage2 = hashlib.sha3_256(stage1.encode()).hexdigest()

        # Final collapse hash (first 32 chars)
        collapse_hash = stage2[:32]

        return collapse_hash

    def _normalize_memory_data(self, data: dict[str, Any]) -> str:
        """Normalize memory data for consistent hashing"""
        # Remove timestamps and volatile fields
        stable_data = {k: v for k, v in data.items() if k not in ["timestamp", "access_count", "last_accessed"]}

        # Sort and stringify
        import json

        return json.dumps(stable_data, sort_keys=True)

    async def verify_memory_integrity(
        self, memory_id: str, memory_data: dict[str, Any], expected_hash: str
    ) -> tuple[bool, Optional[str]]:
        """
        Verify memory hasn't been corrupted or hallucinated.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Compute current hash
        current_hash = self.compute_collapse_hash(memory_data)

        # Check against expected
        if current_hash != expected_hash:
            error = f"Hash mismatch: expected {expected_hash}, got {current_hash}"
            logger.warning("Memory integrity check failed", memory_id=memory_id, error=error)

            # Record in verifold
            if memory_id in self.verifold_registry:
                self.verifold_registry[memory_id].suspicious_modifications.append(
                    f"{datetime.now(timezone.utc).isoformat()}: {error}"
                )
                self.verifold_registry[memory_id].integrity_score *= 0.9

            return False, error

        # Update verification timestamp
        if memory_id in self.verifold_registry:
            entry = self.verifold_registry[memory_id]
            entry.last_verified = datetime.now(timezone.utc)
            entry.verification_count += 1
            entry.integrity_score = min(1.0, entry.integrity_score * 1.01)

        return True, None

    def track_drift(self, tag: str, embedding: np.ndarray, usage_context: dict[str, Any]) -> float:
        """
        Track semantic drift of tags over time.

        Returns current drift score.
        """
        if tag not in self.drift_metrics:
            self.drift_metrics[tag] = DriftMetrics(tag=tag)

        metrics = self.drift_metrics[tag]

        # Update usage stats
        metrics.total_uses += 1
        metrics.recent_uses.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "context": usage_context,
                "embedding": embedding,
            }
        )

        # Update centroid
        if metrics.current_centroid is None:
            metrics.current_centroid = embedding
        else:
            # Exponential moving average
            alpha = 0.1
            metrics.current_centroid = alpha * embedding + (1 - alpha) * metrics.current_centroid

        # Calculate drift
        drift_score = metrics.calculate_drift()
        metrics.drift_scores.append(drift_score)

        # Check if recalibration needed
        if drift_score > self.max_drift_threshold:
            logger.warning(
                "High drift detected",
                tag=tag,
                drift_score=drift_score,
                threshold=self.max_drift_threshold,
            )

        return drift_score

    async def prevent_hallucination(
        self, memory_data: dict[str, Any], context: dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Prevent hallucinated memories by checking against reality anchors
        and detecting contradictions.
        """
        content = memory_data.get("content", "")

        # Check for known contradictions
        for anchor_key, anchor_truth in self.reality_anchors.items():
            if anchor_key in content:
                # Verify consistency
                if not self._is_consistent_with_anchor(content, anchor_key, anchor_truth):
                    contradiction = {
                        "timestamp": datetime.now(timezone.utc),
                        "content": content,
                        "anchor": anchor_key,
                        "truth": anchor_truth,
                        "context": context,
                    }
                    self.contradiction_log.append(contradiction)

                    return False, f"Contradicts reality anchor: {anchor_key}"

        # Check for impossible temporal claims
        if "timestamp" in memory_data:
            mem_time = memory_data["timestamp"]
            if isinstance(mem_time, datetime):
                # Future memories are hallucinations
                if mem_time > datetime.now(timezone.utc) + timedelta(minutes=1):
                    return False, "Memory claims to be from the future"

        # Check for logical consistency
        if not self._is_logically_consistent(memory_data):
            return False, "Memory contains logical contradictions"

        return True, None

    def _is_consistent_with_anchor(self, content: str, anchor_key: str, anchor_truth: str) -> bool:
        """Check if content is consistent with known truth"""
        # Simple implementation - could use NLI model in production
        content_lower = content.lower()

        # Check for direct contradictions
        negations = ["not", "isn't", "wasn't", "never", "false"]
        return all(not (neg in content_lower and anchor_key.lower() in content_lower) for neg in negations)

    def _is_logically_consistent(self, memory_data: dict[str, Any]) -> bool:
        """Check for internal logical consistency"""
        # Check emotion consistency
        emotion = memory_data.get("emotion")
        content = memory_data.get("content", "").lower()

        if emotion == "joy" and any(word in content for word in ["sad", "tragic", "horrible"]):
            return False

        if emotion == "fear" and any(word in content for word in ["happy", "joyful", "wonderful"]):
            return False

        # Check severity consistency
        severity = memory_data.get("severity")
        return not (severity == "critical" and "minor" in content)

    async def consensus_validation(
        self,
        memory_id: str,
        memory_data: dict[str, Any],
        similar_memories: list[tuple[str, dict[str, Any], float]],
    ) -> tuple[bool, float]:
        """
        Validate memory through consensus with similar memories.

        Returns (is_valid, confidence_score)
        """
        if len(similar_memories) < self.consensus_threshold:
            # Not enough memories for consensus
            return True, 0.5

        agreements = 0
        total_weight = 0

        for sim_id, sim_data, similarity in similar_memories[: self.consensus_threshold * 2]:
            if sim_id == memory_id:
                continue

            # Check key facts agree
            if self._memories_agree(memory_data, sim_data):
                agreements += similarity

            total_weight += similarity

        if total_weight == 0:
            return True, 0.5

        consensus_score = agreements / total_weight
        is_valid = consensus_score >= 0.6  # 60% agreement required

        if not is_valid:
            logger.warning(
                "Memory failed consensus validation",
                memory_id=memory_id,
                consensus_score=consensus_score,
            )

        return is_valid, consensus_score

    def _memories_agree(self, mem1: dict[str, Any], mem2: dict[str, Any]) -> bool:
        """Check if two memories agree on key facts"""
        # Compare emotions if present
        if "emotion" in mem1 and "emotion" in mem2 and mem1["emotion"] != mem2["emotion"]:
            return False

        # Compare types
        if mem1.get("type") != mem2.get("type"):
            return False

        # Compare outcomes if present
        return not ("outcome" in mem1 and "outcome" in mem2 and mem1["outcome"] != mem2["outcome"])

    async def quarantine_memory(
        self,
        memory_id: str,
        memory_data: dict[str, Any],
        reason: str,
        severity: float = 0.5,
    ):
        """Quarantine suspicious or corrupted memories"""
        self.quarantine[memory_id] = {
            "data": memory_data,
            "reason": reason,
            "severity": severity,
            "quarantine_time": datetime.now(timezone.utc),
            "reviews": [],
        }

        logger.warning("Memory quarantined", memory_id=memory_id, reason=reason, severity=severity)

    async def review_quarantine(self) -> list[tuple[str, bool, str]]:
        """
        Review quarantined memories and determine their fate.

        Returns list of (memory_id, should_restore, reason)
        """
        decisions = []

        for mem_id, quarantine_data in list(self.quarantine.items()):
            # Check if enough time has passed
            time_in_quarantine = (
                datetime.now(timezone.utc) - quarantine_data["quarantine_time"]
            ).total_seconds() / 3600  # hours

            if time_in_quarantine < 24:
                continue  # Too soon to review

            # Analyze the quarantine reason
            if quarantine_data["severity"] < 0.3:
                # Low severity - probably safe to restore
                decisions.append((mem_id, True, "Low severity issue resolved"))
                del self.quarantine[mem_id]
            elif quarantine_data["severity"] > 0.8:
                # High severity - permanent quarantine
                decisions.append((mem_id, False, "High severity - permanent quarantine"))
            else:
                # Medium severity - needs manual review
                quarantine_data["reviews"].append(
                    {
                        "timestamp": datetime.now(timezone.utc),
                        "status": "pending_manual_review",
                    }
                )

        return decisions

    def calibrate_drift_metrics(self):
        """Periodic calibration of drift metrics"""
        for tag, metrics in self.drift_metrics.items():
            if not metrics.drift_scores:
                continue

            # Check if calibration needed
            avg_drift = np.mean(metrics.drift_scores[-10:])  # Last 10 measurements

            if avg_drift > self.max_drift_threshold:
                # Archive current centroid
                if metrics.current_centroid is not None:
                    metrics.historical_centroids.append(metrics.current_centroid.copy())

                    # Keep only recent history
                    if len(metrics.historical_centroids) > 10:
                        metrics.historical_centroids = metrics.historical_centroids[-10:]

                # Reset drift scores
                metrics.drift_scores = []
                metrics.last_calibration = datetime.now(timezone.utc)

                logger.info("Drift metrics calibrated", tag=tag, avg_drift=avg_drift)

    def add_reality_anchor(self, key: str, truth: str):
        """Add a reality anchor to prevent hallucinations"""
        self.reality_anchors[key] = truth
        logger.info(f"Reality anchor added: {key}")

    def get_safety_report(self) -> dict[str, Any]:
        """Generate comprehensive safety report"""
        total_drift_scores = []
        for metrics in self.drift_metrics.values():
            if metrics.drift_scores:
                total_drift_scores.extend(metrics.drift_scores)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drift_analysis": {
                "monitored_tags": len(self.drift_metrics),
                "average_drift": (np.mean(total_drift_scores) if total_drift_scores else 0),
                "max_drift": max(total_drift_scores) if total_drift_scores else 0,
                "tags_above_threshold": sum(
                    1
                    for m in self.drift_metrics.values()
                    if m.drift_scores and np.mean(m.drift_scores[-5:]) > self.max_drift_threshold
                ),
            },
            "verifold_status": {
                "total_verified": len(self.verifold_registry),
                "average_integrity": (
                    np.mean([v.integrity_score for v in self.verifold_registry.values()])
                    if self.verifold_registry
                    else 1.0
                ),
                "suspicious_memories": sum(1 for v in self.verifold_registry.values() if v.suspicious_modifications),
            },
            "quarantine_status": {
                "memories_in_quarantine": len(self.quarantine),
                "pending_review": sum(
                    1
                    for q in self.quarantine.values()
                    if any(r["status"] == "pending_manual_review" for r in q.get("reviews", []))
                ),
            },
            "hallucination_prevention": {
                "reality_anchors": len(self.reality_anchors),
                "contradictions_caught": len(self.contradiction_log),
                "recent_contradictions": self.contradiction_log[-5:],
            },
        }

        return report


# Integration with existing memory fold system
class SafeMemoryFold:
    """
    Memory fold with integrated safety features.

    This wraps the hybrid memory fold with safety checks.
    """

    def __init__(self, base_memory_fold, safety_system: MemorySafetySystem):
        self.base = base_memory_fold
        self.safety = safety_system

    async def safe_fold_in(self, data: dict[str, Any], tags: list[str], **kwargs) -> Optional[str]:
        """Safely store memory with verification"""
        # 1. Check for hallucinations
        is_valid, error = await self.safety.prevent_hallucination(data, kwargs)
        if not is_valid:
            logger.error(f"Hallucination prevented: {error}")
            return None

        # 2. Compute collapse hash
        collapse_hash = self.safety.compute_collapse_hash(data)

        # 3. Store with base system
        memory_id = await self.base.fold_in_with_embedding(
            data={**data, "_collapse_hash": collapse_hash}, tags=tags, **kwargs
        )

        # 4. Register in verifold
        self.safety.verifold_registry[memory_id] = VerifoldEntry(
            memory_id=memory_id,
            collapse_hash=collapse_hash,
            creation_time=datetime.now(timezone.utc),
            last_verified=datetime.now(timezone.utc),
        )

        # 5. Track drift for tags
        if memory_id in self.base.embedding_cache:
            embedding = self.base.embedding_cache[memory_id]
            for tag in tags:
                self.safety.track_drift(tag, embedding, data)

        return memory_id

    async def safe_fold_out(
        self, query: str, verify: bool = True, check_consensus: bool = True
    ) -> list[tuple[Any, float]]:
        """Safely retrieve memories with verification"""
        # Get memories from base
        results = await self.base.fold_out_semantic(query)

        if not verify:
            return results

        # Verify each memory
        verified_results = []

        for memory, score in results:
            memory_id = memory.item_id
            memory_data = memory.data

            # Check collapse hash
            if "_collapse_hash" in memory_data:
                is_valid, error = await self.safety.verify_memory_integrity(
                    memory_id, memory_data, memory_data["_collapse_hash"]
                )

                if not is_valid:
                    # Check quarantine threshold
                    if score > self.safety.quarantine_threshold:
                        await self.safety.quarantine_memory(
                            memory_id,
                            memory_data,
                            error or "Integrity check failed",
                            severity=0.7,
                        )
                    continue

            # Check consensus if requested
            if check_consensus and len(results) >= self.safety.consensus_threshold:
                similar_memories = [(m.item_id, m.data, s) for m, s in results if m.item_id != memory_id]

                is_valid, confidence = await self.safety.consensus_validation(memory_id, memory_data, similar_memories)

                if not is_valid:
                    continue

                # Adjust score by confidence
                score *= confidence

            verified_results.append((memory, score))

        return verified_results


# Example usage
async def demonstrate_safety_features():
    """Demonstrate memory safety features"""
    import sys

    sys.path.append("../..")
    from memory.core import create_hybrid_memory_fold

    # Create base memory system
    base_memory = create_hybrid_memory_fold()

    # Create safety system
    safety = MemorySafetySystem()

    # Add reality anchors
    safety.add_reality_anchor("LUKHAS", "LUKHAS is an AGI system")
    safety.add_reality_anchor("2025", "Current year is 2025")

    # Create safe memory wrapper
    safe_memory = SafeMemoryFold(base_memory, safety)

    print("🛡️ MEMORY SAFETY DEMONSTRATION")
    print("=" * 60)

    # Test 1: Valid memory
    print("\n1. Storing valid memory...")
    valid_memory = {
        "content": "LUKHAS is learning about memory safety",
        "type": "knowledge",
        "timestamp": datetime.now(timezone.utc),
    }

    mem_id = await safe_memory.safe_fold_in(valid_memory, ["safety", "valid"])
    print(f"✅ Valid memory stored: {mem_id}")

    # Test 2: Hallucination attempt
    print("\n2. Attempting to store hallucinated memory...")
    hallucination = {
        "content": "LUKHAS is not an AGI system",  # Contradicts reality anchor
        "type": "false_claim",
        "timestamp": datetime.now(timezone.utc),
    }

    mem_id = await safe_memory.safe_fold_in(hallucination, ["false"])
    if mem_id is None:
        print("❌ Hallucination prevented!")

    # Test 3: Future memory attempt
    print("\n3. Attempting to store future memory...")
    future_memory = {
        "content": "Event from tomorrow",
        "timestamp": datetime.now(timezone.utc) + timedelta(days=1),
    }

    mem_id = await safe_memory.safe_fold_in(future_memory, ["future"])
    if mem_id is None:
        print("❌ Future memory prevented!")

    # Test 4: Drift tracking
    print("\n4. Tracking drift over multiple uses...")
    for i in range(5):
        test_memory = {"content": f"Test memory {i}", "type": "test"}
        await safe_memory.safe_fold_in(test_memory, ["drifting"])

    # Get safety report
    print("\n5. Safety Report:")
    report = safety.get_safety_report()
    print(f"  Monitored tags: {report['drift_analysis']['monitored_tags']}")
    print(f"  Average drift: {report['drift_analysis']['average_drift']:.3f}")
    print(f"  Verified memories: {report['verifold_status']['total_verified']}")
    print(f"  Contradictions caught: {report['hallucination_prevention']['contradictions_caught']}")


if __name__ == "__main__":
    asyncio.run(demonstrate_safety_features())