"""
🧠 Enhanced Brain Integration System
LUKHAS AI Multi-Brain Symphony Architecture

This module provides a complete brain integration system that combines:
- Multi-Brain Symphony orchestration
- Emotional memory integration
- Voice modulation
- Dream processing
- Advanced memory systems

Replaces and enhances the previous brain_integration.py with superior architecture.
"""

import asyncio
import logging
import os
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any, Callable, Optional

# ΛTAG: consciousness_legacy_imports
from core.consciousness.drift_detector import ConsciousnessDriftDetector
from core.symbolic.glyph_specialist import GlyphConsensusResult, GlyphSpecialist

# Configure logging
logger = logging.getLogger("Enhanced.BrainIntegration")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Import MultiBrainSymphony components with fallback paths
try:
    from .MultiBrainSymphony import (  # TODO: convert to absolute import
        DreamBrainSpecialist,
        LearningBrainSpecialist,
        MemoryBrainSpecialist,
        MultiBrainSymphonyOrchestrator,
    )
    SYMPHONY_AVAILABLE = True
except ImportError:
    try:
        # from MultiBrainSymphony  # External dependency import
        from MultiBrainSymphony import (
            DreamBrainSpecialist,  # noqa: F401  # TODO: MultiBrainSymphony.DreamBrainS...
            LearningBrainSpecialist,  # noqa: F401  # TODO: MultiBrainSymphony.LearningBra...
            MemoryBrainSpecialist,  # noqa: F401  # TODO: MultiBrainSymphony.MemoryBrain...
            MultiBrainSymphonyOrchestrator,
        )
        SYMPHONY_AVAILABLE = True
    except ImportError:
        logger.warning("MultiBrainSymphony components not available")
        SYMPHONY_AVAILABLE = False
        MultiBrainSymphonyOrchestrator = None

# Import core components with fallbacks
try:
    from core.orchestration.brain.spine.fold_engine import (  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for multi-AI agent coordination
        AGIMemory,
        MemoryFold,
        MemoryPriority,
        MemoryType,
    )
except ImportError:
    logger.warning("Core memory components not available - using fallbacks")
    AGIMemory = None

try:
    # from DASHBOARD.Λ_as_agent.core.memory_folds import create_memory_fold, recall_memory_folds  # TODO: Install or implement DASHBOARD
    # from DASHBOARD.as_agent.core.memory_folds import create_memory_fold, recall_memory_folds  # TODO: Install or implement DASHBOARD
    pass  # Placeholder since imports are commented out
except ImportError:
    logger.warning("Emotional memory folds not available")
    create_memory_fold = None
    recall_memory_folds = None

try:
    from VOICE.voice_integrator import VoiceIntegrator
except ImportError:
    VoiceIntegrator = None

try:
    from consciousness.core_consciousness.dream_engine.dream_reflection_loop import (
        DreamReflectionLoop,
    )
except ImportError:
    DreamReflectionLoop = None


class ConsciousnessLegacyConsensus:
    """Legacy consciousness consensus orchestrated through GLYPH specialist."""

    def __init__(
        self,
        glyph_specialist: GlyphSpecialist,
        drift_detector: ConsciousnessDriftDetector,
        telemetry_logger: logging.Logger,
        drift_threshold: float = 0.3,
    ) -> None:
        self._glyph_specialist = glyph_specialist
        self._drift_detector = drift_detector
        self._telemetry_logger = telemetry_logger
        self._drift_threshold = drift_threshold
        self._last_result: Optional[dict[str, Any]] = None

    def ingest_layer_snapshot(
        self,
        layer_id: str,
        driftScore: float,
        affect_delta: float,
        glyph_markers: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a snapshot and evaluate consensus."""

        snapshot = self._drift_detector.record_snapshot(
            layer_id=layer_id,
            driftScore=driftScore,
            affect_delta=affect_delta,
            glyph_markers=glyph_markers or [],
            metadata=metadata,
        )
        signals = self._drift_detector.build_glyph_signals()
        if not signals:
            self._last_result = self._build_result(None, signals_count=0)
            return self._last_result

        consensus_result = self._glyph_specialist.evaluate(signals)
        result = self._build_result(consensus_result, signals_count=len(signals))

        if not consensus_result.consensus or consensus_result.driftScore > self._drift_threshold:
            self._emit_alert(result, snapshot)
        else:
            self._telemetry_logger.info(
                "# ΛTAG: consciousness_legacy -- consensus stable",
                extra={
                    "layer_id": layer_id,
                    "driftScore": result["driftScore"],
                    "affect_delta": result["affect_delta"],
                    "agreement_ratio": result["agreement_ratio"],
                },
            )

        self._last_result = result
        return result

    def evaluate(self) -> dict[str, Any]:
        """Evaluate consensus using existing signals."""
        signals = self._drift_detector.build_glyph_signals()
        if not signals:
            self._last_result = self._build_result(None, signals_count=0)
            return self._last_result

        consensus_result = self._glyph_specialist.evaluate(signals)
        result = self._build_result(consensus_result, signals_count=len(signals))
        if not consensus_result.consensus or consensus_result.driftScore > self._drift_threshold:
            self._emit_alert(result, None)
        self._last_result = result
        return result

    def latest_result(self) -> Optional[dict[str, Any]]:
        """Return the most recent consensus payload."""
        return self._last_result

    def update_threshold(self, drift_threshold: float) -> None:
        """Update both local and GLYPH drift thresholds."""
        self._drift_threshold = drift_threshold
        self._glyph_specialist.update_threshold(drift_threshold)

    def _build_result(
        self,
        consensus_result: Optional[GlyphConsensusResult],
        *,
        signals_count: int,
    ) -> dict[str, Any]:
        if consensus_result is None:
            return {
                "status": "no_data",
                "driftScore": 0.0,
                "affect_delta": 0.0,
                "agreement_ratio": 0.0,
                "dissenting_layers": [],
                "glyph_signature": [],
                "signals_count": signals_count,
                "drift_threshold": self._drift_threshold,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        status = "aligned" if consensus_result.consensus else "drift_alert"
        return {
            "status": status,
            "driftScore": consensus_result.driftScore,
            "affect_delta": consensus_result.affect_delta,
            "agreement_ratio": consensus_result.agreement_ratio,
            "dissenting_layers": consensus_result.dissenting_layers,
            "glyph_signature": consensus_result.glyph_signature,
            "signals_count": signals_count,
            "drift_threshold": self._drift_threshold,
            "timestamp": consensus_result.evaluated_at.isoformat(),
        }

    def _emit_alert(self, result: dict[str, Any], snapshot: Optional[Any]) -> None:
        """Emit telemetry alert for drift events."""
        alert_payload = result.copy()
        if snapshot is not None:
            alert_payload["layer_id"] = snapshot.layer_id
            alert_payload["affect_snapshot"] = snapshot.affect_delta
        self._telemetry_logger.warning(
            "# ΛTAG: consciousness_legacy_alert -- drift threshold exceeded",
            extra=alert_payload,
        )


class EnhancedEmotionalProcessor:
    """Enhanced emotional processing with vector operations and voice integration"""

    def __init__(self):
        self.emotion_vectors = {
            "neutral": [0.0, 0.0, 0.0],
            "joy": [0.8, 0.9, 0.3],
            "sadness": [-0.8, -0.7, -0.2],
            "anger": [-0.8, 0.7, 0.3],
            "fear": [-0.7, 0.8, 0.0],
            "trust": [0.7, 0.5, 0.2],
            "surprise": [0.0, 0.9, 0.8],
            "anticipation": [0.6, 0.8, 0.0],
        }

        self.current_state = {
            "primary_emotion": "neutral",
            "intensity": 0.5,
            "secondary_emotions": {},
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "stability": 0.8,
        }

        self.emotional_history = []
        self.max_history = 50

    def update_emotional_state(self, primary_emotion: str, intensity: Optional[float] = None,
                              secondary_emotions: Optional[dict[str, float]] = None,
                              metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Update emotional state with enhanced tracking"""

        # Store previous state
        self.emotional_history.append(self.current_state.copy())
        if len(self.emotional_history) > self.max_history:
            self.emotional_history = self.emotional_history[-self.max_history:]

        # Update state
        if primary_emotion in self.emotion_vectors:
            self.current_state["primary_emotion"] = primary_emotion

        if intensity is not None:
            self.current_state["intensity"] = max(0.0, min(1.0, intensity))

        if secondary_emotions:
            valid_secondary = {
                e: max(0.0, min(1.0, i))
                for e, i in secondary_emotions.items()
                if e in self.emotion_vectors
            }
            self.current_state["secondary_emotions"] = valid_secondary

        self.current_state["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Calculate stability based on emotional change
        if self.emotional_history:
            previous = self.emotional_history[-1]
            distance = self._calculate_emotion_distance(
                previous["primary_emotion"],
                self.current_state["primary_emotion"]
            )
            self.current_state["stability"] = max(0.1, 1.0 - (distance / 2.0))

        return self.current_state

    def _calculate_emotion_distance(self, emotion1: str, emotion2: str) -> float:
        """Calculate distance between emotions in vector space"""
        if emotion1 not in self.emotion_vectors:
            emotion1 = "neutral"
        if emotion2 not in self.emotion_vectors:
            emotion2 = "neutral"

        vec1 = self.emotion_vectors[emotion1]
        vec2 = self.emotion_vectors[emotion2]

        # Simple Euclidean distance
        distance = sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5
        return distance

    def get_voice_modulation_params(self) -> dict[str, Any]:
        """Generate voice modulation parameters based on emotional state"""
        emotion = self.current_state["primary_emotion"]
        intensity = self.current_state["intensity"]

        emotion_adjustments = {
            "joy": {"pitch": 0.3, "speed": 0.2, "energy": 0.4},
            "sadness": {"pitch": -0.3, "speed": -0.25, "energy": -0.3},
            "anger": {"pitch": 0.2, "speed": 0.3, "energy": 0.5},
            "fear": {"pitch": 0.4, "speed": 0.4, "energy": 0.2},
            "surprise": {"pitch": 0.5, "speed": 0.1, "energy": 0.4},
            "trust": {"pitch": -0.1, "speed": -0.1, "energy": 0.1},
            "anticipation": {"pitch": 0.2, "speed": 0.1, "energy": 0.3}
        }

        adjustments = emotion_adjustments.get(emotion, {"pitch": 0, "speed": 0, "energy": 0})

        return {
            "pitch_adjustment": adjustments["pitch"] * intensity,
            "speed_adjustment": adjustments["speed"] * intensity,
            "energy_adjustment": adjustments["energy"] * intensity,
            "emphasis_level": 0.5 + (intensity * 0.3),
            "pause_threshold": 0.3 + ((1.0 - self.current_state["stability"]) * 0.2)
        }

class EnhancedMemorySystem:
    """Enhanced memory system with emotional integration and dream consolidation"""

    def __init__(self, emotional_processor: EnhancedEmotionalProcessor, memory_path: str = "./enhanced_memory"):
        self.emotional_processor = emotional_processor
        self.memory_path = memory_path
        os.makedirs(memory_path, exist_ok=True)

        self.memory_store = {}
        self.emotional_associations = {}
        self.consolidation_queue = []

        # Statistics
        self.stats = {
            "total_memories": 0,
            "emotional_memories": 0,
            "consolidations": 0,
            "retrievals": 0
        }

    def store_memory_with_emotion(self, key: str, content: Any, emotion: Optional[str] = None,
                                  tags: Optional[list[str]] = None, priority: str = "medium",
                                  metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Store memory with emotional context"""

        # Use current emotional state if none provided
        if emotion is None:
            emotion = self.emotional_processor.current_state["primary_emotion"]

        memory_entry = {
            "key": key,
            "content": content,
            "emotion": emotion,
            "tags": tags or [],
            "priority": priority,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "access_count": 0,
            "emotional_intensity": self.emotional_processor.current_state["intensity"]
        }

        # Store in memory
        self.memory_store[key] = memory_entry

        # Create emotional associations
        if emotion not in self.emotional_associations:
            self.emotional_associations[emotion] = []
        self.emotional_associations[emotion].append(key)

        # Update statistics
        self.stats["total_memories"] += 1
        if emotion != "neutral":
            self.stats["emotional_memories"] += 1

        # Add to consolidation queue if high priority
        if priority in ["high", "critical"]:
            self.consolidation_queue.append(key)

        logger.info(f"Stored memory '{key}' with emotion '{emotion}'")

        return {
            "status": "success",
            "key": key,
            "emotion": emotion,
            "memory_id": str(uuid.uuid4()),
            "timestamp": memory_entry["timestamp"]
        }

    def retrieve_with_emotional_context(self, key: Optional[str] = None, target_emotion: Optional[str] = None,
                                        similarity_threshold: float = 0.7) -> dict[str, Any]:
        """Retrieve memories with emotional context"""

        self.stats["retrievals"] += 1

        if key and key in self.memory_store:
            # Direct retrieval
            memory = self.memory_store[key]
            memory["access_count"] += 1
            return {
                "status": "success",
                "memory": memory,
                "retrieval_type": "direct"
            }

        elif target_emotion:
            # Emotional retrieval
            similar_memories = []

            for emotion, keys in self.emotional_associations.items():
                distance = self.emotional_processor._calculate_emotion_distance(target_emotion, emotion)
                if distance <= (2.0 - similarity_threshold * 2.0):  # Convert threshold to distance
                    for memory_key in keys:
                        memory = self.memory_store[memory_key]
                        memory["emotional_distance"] = distance
                        similar_memories.append(memory)

            # Sort by emotional similarity and recency
            similar_memories.sort(key=lambda m: (m.get("emotional_distance", 1.0), m["timestamp"]))

            return {
                "status": "success",
                "memories": similar_memories[:10],  # Return top 10
                "retrieval_type": "emotional_similarity",
                "target_emotion": target_emotion
            }

        else:
            return {
                "status": "error",
                "message": "Either key or target_emotion must be provided"
            }

    def dream_consolidate_memories(self, max_memories: int = 50) -> dict[str, Any]:
        """Consolidate memories through dream-like processing"""

        if not self.consolidation_queue:
            return {"status": "no_memories_to_consolidate"}

        consolidated_memories = []

        # Process memories in consolidation queue
        for key in self.consolidation_queue[:max_memories]:
            if key in self.memory_store:
                memory = self.memory_store[key]

                # Dream-like processing: create associations and strengthen important memories
                consolidated_memory = {
                    "original_key": key,
                    "content": memory["content"],
                    "emotion": memory["emotion"],
                    "consolidation_strength": memory["emotional_intensity"] * memory["access_count"],
                    "dream_associations": self._generate_dream_associations(memory),
                    "consolidated_at": datetime.now(timezone.utc).isoformat()
                }

                consolidated_memories.append(consolidated_memory)

        # Clear processed items from queue
        self.consolidation_queue = self.consolidation_queue[max_memories:]
        self.stats["consolidations"] += len(consolidated_memories)

        logger.info(f"Consolidated {len(consolidated_memories)} memories through dream processing")

        return {
            "status": "success",
            "consolidated_count": len(consolidated_memories),
            "remaining_queue": len(self.consolidation_queue),
            "consolidated_memories": consolidated_memories
        }

    def _generate_dream_associations(self, memory: dict[str, Any]) -> list[str]:
        """Generate dream-like associations for memory consolidation"""
        associations = []

        # Find emotionally similar memories
        emotion = memory["emotion"]
        if emotion in self.emotional_associations:
            similar_keys = self.emotional_associations[emotion][:3]  # Top 3 similar
            associations.extend([f"emotional_link_{key}" for key in similar_keys])

        # Add content-based associations (simplified)
        content_str = str(memory["content"]).lower()
        if "creative" in content_str:
            associations.append("creativity_network")
        if "memory" in content_str:
            associations.append("meta_memory_network")
        if "learning" in content_str:
            associations.append("learning_network")

        return associations


class MultiBrain:
    """MultiBrain specialist orchestrator for distributed cognitive processing."""

    SUPPORTED_SPECIALIST_TYPES = {"symbolic", "neural", "quantum", "bio", "general"}
    _TELEMETRY_WINDOW = 25

    def __init__(self, *, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.loop = loop
        self.specialists: dict[str, list[dict[str, Any]]] = {}
        self.telemetry: dict[str, dict[str, Any]] = {}
        self.routing_history: deque[dict[str, Any]] = deque(maxlen=128)
        self._lock = threading.RLock()

    # ΛTAG: multi_brain_registry
    def register_specialist(
        self,
        specialist_type: str,
        specialist: Any,
        *,
        capabilities: Optional[set[str]] = None,
        max_parallel_tasks: int = 1,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Register a specialist instance for coordinated routing."""

        normalized_type = (specialist_type or "general").lower()
        if normalized_type not in self.SUPPORTED_SPECIALIST_TYPES:
            logger.warning("Unknown specialist type '%s', defaulting to general", normalized_type)
            normalized_type = "general"

        specialist_id = f"{normalized_type}-{uuid.uuid4().hex}"
        entry = {
            "id": specialist_id,
            "instance": specialist,
            "capabilities": set(capabilities or set()),
            "max_parallel_tasks": max(1, int(max_parallel_tasks or 1)),
            "current_load": 0,
            "metadata": metadata or {},
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

        telemetry_snapshot = {
            "latency_ms": deque(maxlen=self._TELEMETRY_WINDOW),
            "throughput": deque(maxlen=self._TELEMETRY_WINDOW),
            "accuracy": deque(maxlen=self._TELEMETRY_WINDOW),
            "driftScore": 0.0,  # ΛTAG: driftScore
            "affect_delta": 0.0,  # ΛTAG: affect_delta
            "collapseHash": None,
            "last_update": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self.specialists.setdefault(normalized_type, []).append(entry)
            self.telemetry[specialist_id] = telemetry_snapshot

        logger.info("Registered MultiBrain specialist %s (%s)", specialist_id, normalized_type)
        return specialist_id

    def update_specialist_metrics(
        self,
        specialist_id: str,
        *,
        latency_ms: Optional[float] = None,
        throughput: Optional[float] = None,
        accuracy: Optional[float] = None,
        drift_score: Optional[float] = None,
        affect_delta: Optional[float] = None,
        collapse_hash: Optional[str] = None,
    ) -> None:
        """Update telemetry for a specialist."""

        with self._lock:
            telemetry = self.telemetry.get(specialist_id)
            if telemetry is None:
                raise KeyError(f"Specialist '{specialist_id}' not found")

            if latency_ms is not None:
                telemetry["latency_ms"].append(float(latency_ms))
            if throughput is not None:
                telemetry["throughput"].append(float(throughput))
            if accuracy is not None:
                telemetry["accuracy"].append(float(accuracy))
            if drift_score is not None:
                telemetry["driftScore"] = float(drift_score)
            if affect_delta is not None:
                telemetry["affect_delta"] = float(affect_delta)
            if collapse_hash is not None:
                telemetry["collapseHash"] = collapse_hash
            telemetry["last_update"] = datetime.now(timezone.utc).isoformat()

    def broadcast_message(
        self,
        message: dict[str, Any],
        *,
        origin: Optional[str] = None,
        include_types: Optional[set[str]] = None,
    ) -> list[dict[str, Any]]:
        """Broadcast a message to matching specialists."""

        responses: list[dict[str, Any]] = []
        target_types = include_types or set(self.specialists.keys())

        with self._lock:
            for specialist_type in target_types:
                for entry in self.specialists.get(specialist_type, []):
                    response = self._deliver_message(entry, message, origin=origin)
                    responses.append(response)

        return responses

    def relay_between_specialists(
        self,
        origin_type: str,
        target_type: str,
        message: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Relay a message from one specialist type to another."""

        payload = {
            "origin_type": origin_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        }
        return self.broadcast_message(payload, origin=origin_type, include_types={target_type})

    def route_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Select a specialist for the provided task."""

        task_type = str(task.get("type", "general")).lower()
        complexity = str(task.get("complexity", "medium")).lower()
        context = {str(value).lower() for value in task.get("context", [])}
        created_at = datetime.now(timezone.utc).isoformat()

        candidate_types = self._resolve_candidate_types(task_type, context)
        decision_trace: dict[str, Any] = {
            "task_type": task_type,
            "complexity": complexity,
            "context": sorted(context),
            "candidates": [],
        }

        chosen: Optional[tuple[str, dict[str, Any]]] = None
        highest_score = float("-inf")

        with self._lock:
            available_candidates: list[tuple[str, dict[str, Any]]] = []
            for candidate_type in candidate_types:
                available_candidates.extend(
                    (candidate_type, entry)
                    for entry in self.specialists.get(candidate_type, [])
                )

            if not available_candidates:
                # Fallback to any available specialist if routing map is empty
                for specialist_type, entries in self.specialists.items():
                    available_candidates.extend((specialist_type, entry) for entry in entries)

            for specialist_type, entry in available_candidates:
                telemetry = self.telemetry.get(entry["id"], {})
                score = self._score_specialist(
                    specialist_type,
                    entry,
                    telemetry,
                    complexity=complexity,
                    context=context,
                )

                decision_trace["candidates"].append(
                    {
                        "specialist_id": entry["id"],
                        "specialist_type": specialist_type,
                        "score": round(score, 4),
                        "current_load": entry["current_load"],
                        "capabilities": sorted(entry["capabilities"]),
                    }
                )

                if score > highest_score:
                    chosen = (specialist_type, entry)
                    highest_score = score

            if chosen:
                chosen_type, chosen_entry = chosen
                chosen_entry["current_load"] = min(
                    chosen_entry["current_load"] + 1,
                    chosen_entry["max_parallel_tasks"],
                )
                decision = {
                    "specialist_id": chosen_entry["id"],
                    "specialist_type": chosen_type,
                    "timestamp": created_at,
                    "decision_trace": decision_trace,
                }
                self.routing_history.append(
                    {
                        "task": task,
                        "decision": decision,
                    }
                )
                # ΛTAG: multi_brain_route
                logger.info(
                    "MultiBrain routed task '%s' to %s (%s) [score=%.3f]",
                    task_type,
                    chosen_entry["id"],
                    chosen_type,
                    highest_score,
                )
                return decision

        logger.info(
            "MultiBrain routed task '%s' using general fallback (no specialists available)",
            task_type,
        )
        # TODO: Add reinforcement learning feedback loop for routing quality adjustments
        fallback_decision = {
            "specialist_id": None,
            "specialist_type": "general",
            "timestamp": created_at,
            "decision_trace": decision_trace,
        }
        self.routing_history.append({"task": task, "decision": fallback_decision})
        return fallback_decision

    def complete_task(self, specialist_id: str) -> None:
        """Reduce load counter when a specialist finishes a task."""

        with self._lock:
            for entries in self.specialists.values():
                for entry in entries:
                    if entry["id"] == specialist_id:
                        entry["current_load"] = max(0, entry["current_load"] - 1)
                        return

    def get_specialist_snapshot(self, specialist_id: str) -> dict[str, Any]:
        """Return telemetry snapshot for the given specialist."""

        with self._lock:
            telemetry = self.telemetry.get(specialist_id)
            if telemetry is None:
                raise KeyError(f"Specialist '{specialist_id}' not found")

            return {
                "specialist_id": specialist_id,
                "latency_ms": list(telemetry["latency_ms"]),
                "throughput": list(telemetry["throughput"]),
                "accuracy": list(telemetry["accuracy"]),
                "avg_latency_ms": self._average(telemetry["latency_ms"]),
                "avg_throughput": self._average(telemetry["throughput"]),
                "avg_accuracy": self._average(telemetry["accuracy"]),
                "driftScore": telemetry.get("driftScore"),
                "affect_delta": telemetry.get("affect_delta"),
                "collapseHash": telemetry.get("collapseHash"),
                "last_update": telemetry.get("last_update"),
            }

    def _deliver_message(
        self,
        entry: dict[str, Any],
        message: dict[str, Any],
        *,
        origin: Optional[str],
    ) -> dict[str, Any]:
        handler: Optional[Callable[..., Any]] = None
        if hasattr(entry["instance"], "handle_message"):
            handler = entry["instance"].handle_message
        elif hasattr(entry["instance"], "process_signal"):
            handler = entry["instance"].process_signal

        if handler is None:
            return {
                "specialist_id": entry["id"],
                "status": "unhandled",
                "reason": "no_handler",
            }

        try:
            response = handler(message, origin=origin)
            if asyncio.iscoroutine(response):
                response = self._resolve_async(response)
            logger.debug(
                "MultiBrain delivered message to %s (origin=%s)",
                entry["id"],
                origin,
            )
            return {
                "specialist_id": entry["id"],
                "status": "ok",
                "response": response,
            }
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Specialist %s message handling failed", entry["id"], exc_info=exc)
            return {
                "specialist_id": entry["id"],
                "status": "error",
                "error": str(exc),
            }

    def _resolve_async(self, awaitable: Any) -> Any:
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(awaitable, self.loop)
            return future.result()

        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if running_loop and running_loop.is_running():
            # Execute in a dedicated loop to avoid interfering with the caller loop
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(awaitable)
            finally:
                new_loop.close()

        return asyncio.run(awaitable)

    def _resolve_candidate_types(self, task_type: str, context: set[str]) -> set[str]:
        mapping = {
            "reasoning": {"symbolic"},
            "analysis": {"symbolic", "neural"},
            "pattern": {"neural"},
            "optimization": {"quantum", "symbolic"},
            "adaptation": {"bio", "neural"},
            "memory": {"symbolic", "bio"},
        }
        if context & {"bio", "somatic"}:
            mapping.setdefault(task_type, set()).add("bio")
        if context & {"quantum", "qpu"}:
            mapping.setdefault(task_type, set()).add("quantum")

        return mapping.get(task_type, {task_type} & self.SUPPORTED_SPECIALIST_TYPES)

    def _score_specialist(
        self,
        specialist_type: str,
        entry: dict[str, Any],
        telemetry: dict[str, Any],
        *,
        complexity: str,
        context: set[str],
    ) -> float:
        capability_bonus = len(entry["capabilities"] & context)
        load_penalty = entry["current_load"] / max(1, entry["max_parallel_tasks"])
        latency_penalty = self._average(telemetry.get("latency_ms", [])) * 0.01 if telemetry else 0.0
        accuracy_bonus = self._average(telemetry.get("accuracy", [])) * 0.5 if telemetry else 0.25
        throughput_bonus = self._average(telemetry.get("throughput", [])) * 0.1 if telemetry else 0.0
        drift_penalty = telemetry.get("driftScore", 0.0) * 0.2 if telemetry else 0.0

        base_score = 1.0
        if complexity == "high" and specialist_type in {"quantum", "symbolic"}:
            base_score += 1.0
        elif complexity == "low":
            base_score += 0.2

        return (
            base_score
            + capability_bonus
            + accuracy_bonus
            + throughput_bonus
            - load_penalty
            - latency_penalty
            - drift_penalty
        )

    @staticmethod
    def _average(values: Any) -> float:
        values_list = list(values)
        if not values_list:
            return 0.0
        return sum(values_list) / len(values_list)


class EnhancedBrainIntegration:
    """
    Enhanced Brain Integration System combining Multi-Brain Symphony with
    emotional memory processing, voice modulation, and dream consolidation.

    This is the superior replacement for the previous brain_integration.py
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the Enhanced Brain Integration System"""

        self.config = config or {}
        logger.info("🧠 Initializing Enhanced Brain Integration System")

        # Initialize core components
        self.emotional_processor = EnhancedEmotionalProcessor()
        self.memory_system = EnhancedMemorySystem(self.emotional_processor)
        self.multi_brain = MultiBrain()
        self.multi_brain.register_specialist(
            "general",
            self,
            capabilities={"coordination", "fallback"},
            metadata={"role": "enhanced_brain_integration"},
        )

        # Initialize Multi-Brain Symphony if available
        if SYMPHONY_AVAILABLE:
            try:
                self.symphony_orchestrator = MultiBrainSymphonyOrchestrator(
                    emotional_oscillator=self.emotional_processor,
                    memory_integrator=self.memory_system
                )
                self.symphony_available = True
                logger.info("🎼 Multi-Brain Symphony orchestrator integrated")
                self.multi_brain.register_specialist(
                    "symbolic",
                    self.symphony_orchestrator,
                    capabilities={"coordination", "symbolic", "symphony"},
                    metadata={"role": "symphony_orchestrator"},
                )
            except Exception as e:
                logger.error(f"Failed to initialize symphony: {e}")
                self.symphony_orchestrator = None
                self.symphony_available = False
        else:
            self.symphony_orchestrator = None
            self.symphony_available = False

        # Initialize voice integration if available
        try:
            if VoiceIntegrator:
                self.voice_integrator = VoiceIntegrator()
            else:
                self.voice_integrator = None
        except Exception as e:
            logger.warning(f"Voice integrator not available: {e}")
            self.voice_integrator = None

        # Initialize dream engine if available
        try:
            if DreamReflectionLoop:
                self.dream_engine = DreamReflectionLoop()
            else:
                self.dream_engine = None
        except Exception as e:
            logger.warning(f"Dream engine not available: {e}")
            self.dream_engine = None

        # ΛTAG: consciousness_legacy_setup
        legacy_config = self.config.get("consciousness_legacy", {})
        drift_threshold = float(legacy_config.get("drift_threshold", 0.3))
        retention = int(legacy_config.get("retention", 12))
        self.consciousness_drift_detector = ConsciousnessDriftDetector(retention=retention)
        self.glyph_specialist = GlyphSpecialist(drift_threshold=drift_threshold)
        self.consciousness_legacy = ConsciousnessLegacyConsensus(
            glyph_specialist=self.glyph_specialist,
            drift_detector=self.consciousness_drift_detector,
            telemetry_logger=logger,
            drift_threshold=drift_threshold,
        )
        self.last_consciousness_consensus: Optional[dict[str, Any]] = None

        # Background processing
        self.consolidation_running = False
        self.consolidation_thread = None

        # Processing statistics
        self.stats = {
            "symphony_processes": 0,
            "emotional_updates": 0,
            "memory_operations": 0,
            "voice_outputs": 0,
            "dream_consolidations": 0,
            "consciousness_consensus_events": 0,
            "consciousness_drift_alerts": 0,
        }

        logger.info("✅ Enhanced Brain Integration System initialized successfully")

    async def process_with_symphony(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input through Multi-Brain Symphony if available, fallback to standard processing"""

        routing_decision = self.multi_brain.route_task(
            {
                "type": input_data.get("type", "general"),
                "complexity": input_data.get("complexity", "medium"),
                "context": input_data.get("context", []),
            }
        )

        if self.symphony_available and self.symphony_orchestrator:
            try:
                # Initialize symphony if not already done
                if not self.symphony_orchestrator.symphony_active:
                    await self.symphony_orchestrator.initialize_symphony()

                # Conduct symphony processing
                symphony_result = await self.symphony_orchestrator.conduct_symphony(input_data)

                # Integrate results with brain systems
                integrated_result = await self._integrate_symphony_results(symphony_result, input_data)

                self.stats["symphony_processes"] += 1

                if routing_decision.get("specialist_id"):
                    self.multi_brain.complete_task(routing_decision["specialist_id"])

                return {
                    "status": "success",
                    "processing_type": "symphony_enhanced",
                    "symphony_result": symphony_result,
                    "integrated_result": integrated_result,
                    "coordination_quality": symphony_result.get("coordination_quality", 0.0),
                    "routing_decision": routing_decision,
                }

            except Exception as e:
                logger.error(f"Symphony processing failed, falling back to standard: {e}")
                return await self._standard_processing(input_data)
        else:
            return await self._standard_processing(input_data)

    async def _integrate_symphony_results(self, symphony_result: dict[str, Any],
                                          original_input: dict[str, Any]) -> dict[str, Any]:
        """Integrate symphony results with brain subsystems"""

        integrated = {
            "emotional_processing": {},
            "memory_integration": {},
            "voice_modulation": {},
            "dream_insights": [],
            "learning_adaptations": []
        }

        # Process emotional context from symphony
        emotional_context = symphony_result.get("emotional_context", {})
        if emotional_context and "primary_emotion" in emotional_context:
            self.emotional_processor.update_emotional_state(
                primary_emotion=emotional_context["primary_emotion"],
                intensity=emotional_context.get("intensity", 0.5),
                metadata={"source": "symphony_processing"}
            )
            integrated["emotional_processing"] = self.emotional_processor.current_state
            self.stats["emotional_updates"] += 1

        # Process specialized brain outputs
        specialized_processing = symphony_result.get("specialized_processing", {})

        # Memory brain integration
        if "memory" in specialized_processing:
            memory_result = specialized_processing["memory"]
            if memory_result.get("status") != "failed":
                # Store symphony insights as memories
                insights = symphony_result.get("synthesized_insights", [])
                for i, insight in enumerate(insights):
                    memory_key = f"symphony_insight_{int(time.time())}_{i}"
                    self.memory_system.store_memory_with_emotion(
                        key=memory_key,
                        content=insight,
                        emotion=emotional_context.get("primary_emotion", "neutral"),
                        tags=["symphony", "insight"],
                        priority="medium"
                    )
                integrated["memory_integration"] = memory_result
                self.stats["memory_operations"] += 1

        # Dreams brain integration
        if "dreams" in specialized_processing:
            dreams_result = specialized_processing["dreams"]
            if dreams_result.get("status") != "failed":
                integrated["dream_insights"] = dreams_result.get("creative_insights", [])

        # Learning brain integration
        if "learning" in specialized_processing:
            learning_result = specialized_processing["learning"]
            if learning_result.get("status") != "failed":
                integrated["learning_adaptations"] = learning_result.get("adaptation_recommendations", [])

        # Generate voice modulation parameters
        integrated["voice_modulation"] = self.emotional_processor.get_voice_modulation_params()

        return integrated

    async def _standard_processing(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Standard processing fallback when symphony is not available"""

        # Extract content
        content = input_data.get("content", str(input_data))

        # Emotional analysis (simplified)
        emotion = "neutral"
        intensity = 0.5

        # Simple emotion detection based on content
        content_lower = content.lower()
        if any(word in content_lower for word in ["happy", "joy", "great", "excellent"]):
            emotion = "joy"
            intensity = 0.7
        elif any(word in content_lower for word in ["sad", "disappointed", "bad"]):
            emotion = "sadness"
            intensity = 0.6
        elif any(word in content_lower for word in ["angry", "frustrated", "annoyed"]):
            emotion = "anger"
            intensity = 0.8

        routing_decision = self.multi_brain.route_task(
            {
                "type": input_data.get("type", "general"),
                "complexity": input_data.get("complexity", "medium"),
                "context": input_data.get("context", []),
            }
        )

        # Update emotional state
        self.emotional_processor.update_emotional_state(emotion, intensity)

        # Store as memory
        memory_key = f"standard_process_{int(time.time())}"
        memory_result = self.memory_system.store_memory_with_emotion(
            key=memory_key,
            content=content,
            emotion=emotion,
            tags=["standard_processing"]
        )

        self.stats["memory_operations"] += 1
        self.stats["emotional_updates"] += 1

        if routing_decision.get("specialist_id"):
            self.multi_brain.complete_task(routing_decision["specialist_id"])

        return {
            "status": "success",
            "processing_type": "standard",
            "emotional_state": self.emotional_processor.current_state,
            "memory_result": memory_result,
            "voice_modulation": self.emotional_processor.get_voice_modulation_params(),
            "routing_decision": routing_decision,
        }

    def handle_message(self, message: dict[str, Any], origin: Optional[str] = None) -> dict[str, Any]:
        """Allow MultiBrain to deliver coordination messages back to the integrator."""

        logger.info(
            "EnhancedBrainIntegration received message from %s: %s",
            origin,
            message.get("topic", "general"),
        )
        return {
            "status": "received",
            "origin": origin,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "echo": message,
        }

    def speak_with_emotion(self, text: str, override_emotion: Optional[str] = None) -> dict[str, Any]:
        """Generate speech with emotional modulation"""

        # Use override emotion or current state
        if override_emotion:
            self.emotional_processor.update_emotional_state(override_emotion)

        voice_params = self.emotional_processor.get_voice_modulation_params()

        # If voice integrator available, use it
        if self.voice_integrator:
            try:
                voice_result = self.voice_integrator.speak_with_modulation(text, voice_params)
                self.stats["voice_outputs"] += 1
                return voice_result
            except Exception as e:
                logger.error(f"Voice integration failed: {e}")

        # Fallback response
        self.stats["voice_outputs"] += 1
        return {
            "status": "text_only",
            "text": text,
            "emotional_modulation": voice_params,
            "current_emotion": self.emotional_processor.current_state["primary_emotion"]
        }

    def start_dream_consolidation(self, interval_minutes: int = 60) -> bool:
        """Start background dream consolidation process"""

        if self.consolidation_running:
            return False

        self.consolidation_running = True

        def consolidation_loop():
            logger.info(f"🌙 Starting dream consolidation loop (every {interval_minutes} minutes)")

            while self.consolidation_running:
                try:
                    result = self.memory_system.dream_consolidate_memories()
                    if result["status"] == "success":
                        self.stats["dream_consolidations"] += 1
                        logger.info(f"Dream consolidation: {result['consolidated_count']} memories processed")

                except Exception as e:
                    logger.error(f"Dream consolidation error: {e}")

                # Sleep with interruption checking
                for _ in range(interval_minutes * 60):
                    if not self.consolidation_running:
                        break
                    time.sleep(1)

        self.consolidation_thread = threading.Thread(target=consolidation_loop, daemon=True)
        self.consolidation_thread.start()

        return True

    def stop_dream_consolidation(self) -> bool:
        """Stop background dream consolidation"""
        if self.consolidation_running:
            self.consolidation_running = False
            return True
        return False

    # ΛTAG: consciousness_legacy_api
    def record_consciousness_layer_state(
        self,
        layer_id: str,
        *,
        driftScore: float,
        affect_delta: float,
        glyph_markers: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a consciousness layer snapshot and run legacy consensus."""

        result = self.consciousness_legacy.ingest_layer_snapshot(
            layer_id=layer_id,
            driftScore=driftScore,
            affect_delta=affect_delta,
            glyph_markers=glyph_markers,
            metadata=metadata,
        )
        self.stats["consciousness_consensus_events"] += 1
        if result["status"] == "drift_alert":
            self.stats["consciousness_drift_alerts"] += 1
        self.last_consciousness_consensus = result
        return result

    def evaluate_consciousness_consensus(self) -> dict[str, Any]:
        """Evaluate consensus from previously recorded layer snapshots."""

        result = self.consciousness_legacy.evaluate()
        self.last_consciousness_consensus = result
        return result

    def get_comprehensive_status(self) -> dict[str, Any]:
        """Get comprehensive status of all brain systems"""

        status = {
            "system_active": True,
            "components": {
                "emotional_processor": True,
                "memory_system": True,
                "symphony_orchestrator": self.symphony_available,
                "voice_integrator": self.voice_integrator is not None,
                "dream_engine": self.dream_engine is not None
            },
            "current_emotional_state": self.emotional_processor.current_state,
            "memory_stats": self.memory_system.stats,
            "processing_stats": self.stats,
            "consolidation_active": self.consolidation_running,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "consciousness_legacy": {
                "last_consensus": self.last_consciousness_consensus,
                "drift_summary": self.consciousness_drift_detector.summarize_layers(),
            },
        }

        # Add symphony status if available
        if self.symphony_available and self.symphony_orchestrator:
            try:
                status["symphony_status"] = self.symphony_orchestrator.get_symphony_status()
            except Exception as e:
                status["symphony_status"] = {"error": str(e)}

        return status

# Factory function for easy integration

def create_enhanced_brain_integration(config: Optional[dict[str, Any]] = None) -> EnhancedBrainIntegration:
    """
    Factory function to create Enhanced Brain Integration system

    Args:
        config: Configuration dictionary

    Returns:
        EnhancedBrainIntegration instance
    """
    return EnhancedBrainIntegration(config)

# Demonstration
async def demo_enhanced_integration():
    """Demonstrate the Enhanced Brain Integration system"""

    print("🧠 Enhanced Brain Integration Demo")

    # Create system
    brain = create_enhanced_brain_integration()

    # Test data
    test_inputs = [
        {"content": "I'm feeling creative and want to learn something new",
    "type": "creative_learning"},
        {"content": "This is a sad memory I want to remember", "type": "emotional_memory"},
        {"content": "I'm excited about this new discovery!", "type": "positive_discovery"}
    ]

    # Process each input
    for i, test_input in enumerate(test_inputs):
        print(f"\n--- Test {i+1}: {test_input['type']} ---")

        result = await brain.process_with_symphony(test_input)
        print(f"Processing: {result['processing_type']}")

        if result["processing_type"] == "symphony_enhanced":
            print(f"Coordination Quality: {result['coordination_quality']:.2f}")
            print(f"Insights: {len(result['symphony_result'].get('synthesized_insights', []))}")

        # Test speech
        speech_result = brain.speak_with_emotion(test_input["content"])
        print(f"Speech emotion: {speech_result.get('current_emotion', 'unknown')}")

    # Show final status
    status = brain.get_comprehensive_status()
    print("\n🎼 Final Status:")
    print(f"Symphony available: {status['components']['symphony_orchestrator']}")
    print(f"Total memories: {status['memory_stats']['total_memories']}")
    print(f"Emotional memories: {status['memory_stats']['emotional_memories']}")
    print(f"Symphony processes: {status['processing_stats']['symphony_processes']}")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_integration())
