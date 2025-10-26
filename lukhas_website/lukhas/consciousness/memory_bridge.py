"""
C.2 Memory-Consciousness Bridge - Enhanced Integration Layer
Advanced bidirectional bridge between consciousness and memory systems with real-time synchronization.
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from consciousness.types import AwarenessSnapshot, ConsciousnessState, DreamTrace, ReflectionReport
from memory.consciousness_memory_integration import (
    ConsciousnessMemoryIntegrator,
    EmotionalContext,
    MemoryFold,
    MemoryFoldType,
)

logger = logging.getLogger(__name__)


class BridgeState(Enum):
    """Memory-consciousness bridge states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SYNCHRONIZING = "synchronizing"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class SyncMode(Enum):
    """Synchronization modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    ADAPTIVE = "adaptive"


@dataclass
class BridgeMetrics:
    """Memory-consciousness bridge metrics"""
    sync_latency_ms: float = 0.0
    memory_write_rate: float = 0.0
    consciousness_update_rate: float = 0.0
    integration_success_rate: float = 0.0
    error_count: int = 0
    total_memory_folds: int = 0
    active_consciousness_sessions: int = 0
    bidirectional_sync_count: int = 0


@dataclass
class MemoryConsciousnessEvent:
    """Event for memory-consciousness synchronization"""
    event_id: str
    event_type: str  # "memory_to_consciousness" or "consciousness_to_memory"
    source_component: str
    target_component: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 5=high
    requires_sync: bool = True
    correlation_id: Optional[str] = None


class MemoryConsciousnessBridge:
    """
    C.2 Memory-Consciousness Bridge
    Advanced bidirectional integration layer between consciousness and memory systems
    """

    def __init__(self,
                 memory_integrator: ConsciousnessMemoryIntegrator,
                 sync_mode: SyncMode = SyncMode.ADAPTIVE,
                 sync_interval_ms: int = 100,
                 batch_size: int = 10,
                 max_queue_size: int = 1000):
        self.memory_integrator = memory_integrator
        self.sync_mode = sync_mode
        self.sync_interval_ms = sync_interval_ms
        self.batch_size = batch_size
        self.max_queue_size = max_queue_size

        # Bridge state
        self.state = BridgeState.INITIALIZING
        self.metrics = BridgeMetrics()

        # Event queues for bidirectional sync
        self.memory_to_consciousness_queue: deque = deque(maxlen=max_queue_size)
        self.consciousness_to_memory_queue: deque = deque(maxlen=max_queue_size)

        # Active consciousness sessions
        self.consciousness_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_memory_mappings: Dict[str, Set[str]] = {}  # session_id -> fold_ids

        # Memory-consciousness correlation
        self.memory_consciousness_map: Dict[str, str] = {}  # fold_id -> consciousness_context
        self.consciousness_memory_map: Dict[str, Set[str]] = {}  # consciousness_context -> fold_ids

        # Event handlers
        self.memory_event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.consciousness_event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Performance tracking
        self.sync_history: deque = deque(maxlen=1000)
        self.error_history: deque = deque(maxlen=100)

        # Background tasks
        self.sync_task: Optional[asyncio.Task] = None
        self.monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """Start the memory-consciousness bridge"""
        logger.info("🌉 Starting Memory-Consciousness Bridge")

        try:
            # Initialize memory integrator if needed
            if not hasattr(self.memory_integrator, '_memory_folds'):
                await self.memory_integrator.initialize_memory_consciousness_coupling()

            # Start background tasks
            self.sync_task = asyncio.create_task(self._sync_loop())
            self.monitor_task = asyncio.create_task(self._monitor_loop())

            # Register default event handlers
            await self._register_default_handlers()

            self.state = BridgeState.ACTIVE
            logger.info("✅ Memory-Consciousness Bridge started successfully")

        except Exception as e:
            self.state = BridgeState.ERROR
            logger.error(f"❌ Failed to start Memory-Consciousness Bridge: {e}")
            raise

    async def stop(self):
        """Stop the memory-consciousness bridge"""
        logger.info("🛑 Stopping Memory-Consciousness Bridge")

        self.state = BridgeState.SHUTDOWN
        self._shutdown_event.set()

        # Cancel background tasks
        for task in [self.sync_task, self.monitor_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Memory-Consciousness Bridge stopped")

    async def create_consciousness_session(self,
                                         session_id: str,
                                         consciousness_state: ConsciousnessState,
                                         context: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new consciousness session with memory integration"""

        if session_id in self.consciousness_sessions:
            logger.warning(f"Consciousness session already exists: {session_id}")
            return False

        # Create session
        session_data = {
            "session_id": session_id,
            "consciousness_state": asdict(consciousness_state),
            "context": context or {},
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "memory_folds": set(),
            "sync_count": 0
        }

        self.consciousness_sessions[session_id] = session_data
        self.session_memory_mappings[session_id] = set()

        # Create initial memory fold for session
        await self._create_session_memory_fold(session_id, consciousness_state)

        # Queue consciousness-to-memory event
        event = MemoryConsciousnessEvent(
            event_id=f"sess_create_{uuid.uuid4().hex[:8]}",
            event_type="consciousness_to_memory",
            source_component="consciousness_session",
            target_component="memory_integrator",
            payload={
                "action": "session_created",
                "session_id": session_id,
                "consciousness_state": asdict(consciousness_state)
            },
            timestamp=datetime.utcnow(),
            priority=3,
            correlation_id=session_id
        )
        await self._queue_consciousness_to_memory_event(event)

        self.metrics.active_consciousness_sessions += 1
        logger.info(f"📝 Created consciousness session: {session_id}")
        return True

    async def update_consciousness_session(self,
                                         session_id: str,
                                         consciousness_state: ConsciousnessState,
                                         awareness: Optional[AwarenessSnapshot] = None,
                                         reflection: Optional[ReflectionReport] = None,
                                         dream: Optional[DreamTrace] = None) -> bool:
        """Update consciousness session with new state and artifacts"""

        if session_id not in self.consciousness_sessions:
            logger.warning(f"Consciousness session not found: {session_id}")
            return False

        session = self.consciousness_sessions[session_id]
        session["consciousness_state"] = asdict(consciousness_state)
        session["last_updated"] = datetime.utcnow()

        # Create memory folds for significant updates
        memory_events = []

        if awareness and awareness.anomalies:
            fold_id = await self._create_awareness_memory_fold(session_id, awareness)
            if fold_id:
                memory_events.append(("awareness_anomaly", fold_id))

        if reflection and reflection.coherence_score < 0.5:
            fold_id = await self._create_reflection_memory_fold(session_id, reflection)
            if fold_id:
                memory_events.append(("reflection_concern", fold_id))

        if dream:
            fold_id = await self._create_dream_memory_fold(session_id, dream)
            if fold_id:
                memory_events.append(("dream_cycle", fold_id))

        # Queue synchronization events
        if memory_events:
            event = MemoryConsciousnessEvent(
                event_id=f"sess_update_{uuid.uuid4().hex[:8]}",
                event_type="consciousness_to_memory",
                source_component="consciousness_session",
                target_component="memory_integrator",
                payload={
                    "action": "session_updated",
                    "session_id": session_id,
                    "memory_events": memory_events,
                    "consciousness_state": asdict(consciousness_state)
                },
                timestamp=datetime.utcnow(),
                priority=2,
                correlation_id=session_id
            )
            await self._queue_consciousness_to_memory_event(event)

        session["sync_count"] += 1
        logger.debug(f"🔄 Updated consciousness session: {session_id}")
        return True

    async def query_consciousness_relevant_memories(self,
                                                  session_id: str,
                                                  consciousness_context: str,
                                                  max_results: int = 10) -> List[Tuple[str, MemoryFold, float]]:
        """Query memories relevant to current consciousness context"""

        if session_id not in self.consciousness_sessions:
            logger.warning(f"Consciousness session not found: {session_id}")
            return []

        # Build query from consciousness context
        query = {
            "consciousness_context": consciousness_context,
            "session_id": session_id,
            "emotional_weighting": True
        }

        # Get consciousness state for context
        session = self.consciousness_sessions[session_id]
        session["consciousness_state"]

        # Query memory integrator
        results = await self.memory_integrator.recall_consciousness_memory(
            query=query,
            consciousness_context=consciousness_context,
            max_results=max_results,
            emotional_weight=0.4
        )

        # Queue memory-to-consciousness event
        event = MemoryConsciousnessEvent(
            event_id=f"mem_query_{uuid.uuid4().hex[:8]}",
            event_type="memory_to_consciousness",
            source_component="memory_integrator",
            target_component="consciousness_session",
            payload={
                "action": "memory_recalled",
                "session_id": session_id,
                "query": query,
                "result_count": len(results)
            },
            timestamp=datetime.utcnow(),
            priority=2,
            correlation_id=session_id
        )
        await self._queue_memory_to_consciousness_event(event)

        logger.debug(f"🔍 Retrieved {len(results)} memories for session: {session_id}")
        return results

    async def integrate_memory_into_consciousness(self,
                                                session_id: str,
                                                memory_fold: MemoryFold) -> bool:
        """Integrate a memory fold into consciousness processing"""

        if session_id not in self.consciousness_sessions:
            logger.warning(f"Consciousness session not found: {session_id}")
            return False

        session = self.consciousness_sessions[session_id]

        # Add memory fold to session
        session["memory_folds"].add(memory_fold.fold_id)
        self.session_memory_mappings[session_id].add(memory_fold.fold_id)

        # Update consciousness-memory mapping
        consciousness_context = memory_fold.consciousness_context
        if consciousness_context:
            self.memory_consciousness_map[memory_fold.fold_id] = consciousness_context

            if consciousness_context not in self.consciousness_memory_map:
                self.consciousness_memory_map[consciousness_context] = set()
            self.consciousness_memory_map[consciousness_context].add(memory_fold.fold_id)

        # Queue integration event
        event = MemoryConsciousnessEvent(
            event_id=f"mem_integrate_{uuid.uuid4().hex[:8]}",
            event_type="memory_to_consciousness",
            source_component="memory_integrator",
            target_component="consciousness_session",
            payload={
                "action": "memory_integrated",
                "session_id": session_id,
                "fold_id": memory_fold.fold_id,
                "fold_type": memory_fold.fold_type.value,
                "emotional_context": asdict(memory_fold.emotional_context)
            },
            timestamp=datetime.utcnow(),
            priority=3,
            correlation_id=session_id
        )
        await self._queue_memory_to_consciousness_event(event)

        self.metrics.bidirectional_sync_count += 1
        logger.debug(f"🧩 Integrated memory fold {memory_fold.fold_id} into session: {session_id}")
        return True

    async def synchronize_consciousness_memory_state(self, session_id: str) -> bool:
        """Perform full bidirectional synchronization for a session"""

        if session_id not in self.consciousness_sessions:
            return False

        sync_start = time.time()
        self.consciousness_sessions[session_id]

        try:
            # Sync consciousness changes to memory
            consciousness_fold_id = await self._sync_consciousness_to_memory(session_id)

            # Sync relevant memories to consciousness
            memory_sync_count = await self._sync_memory_to_consciousness(session_id)

            # Update metrics
            sync_latency = (time.time() - sync_start) * 1000
            self.metrics.sync_latency_ms = sync_latency
            self.metrics.integration_success_rate = min(1.0, self.metrics.integration_success_rate + 0.01)

            # Record sync event
            sync_record = {
                "session_id": session_id,
                "sync_latency_ms": sync_latency,
                "consciousness_fold_id": consciousness_fold_id,
                "memory_sync_count": memory_sync_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.sync_history.append(sync_record)

            logger.debug(f"🔄 Synchronized session {session_id} in {sync_latency:.1f}ms")
            return True

        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.integration_success_rate = max(0.0, self.metrics.integration_success_rate - 0.05)

            error_record = {
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.error_history.append(error_record)

            logger.error(f"❌ Synchronization failed for session {session_id}: {e}")
            return False

    async def _create_session_memory_fold(self, session_id: str, consciousness_state: ConsciousnessState) -> str:
        """Create initial memory fold for consciousness session"""

        content = {
            "session_id": session_id,
            "phase": consciousness_state.phase,
            "awareness_level": consciousness_state.awareness_level,
            "consciousness_level": consciousness_state.level,
            "emotional_tone": consciousness_state.emotional_tone,
            "context": consciousness_state.context
        }

        emotional_context = EmotionalContext(
            valence=0.0,  # Neutral for session creation
            arousal=0.3,  # Light arousal for new session
            dominance=0.7,  # High control for session management
            confidence=0.9
        )

        fold_id = await self.memory_integrator.create_consciousness_memory_fold(
            content=content,
            fold_type=MemoryFoldType.IDENTITY,
            consciousness_context=f"session_{session_id}",
            emotional_context=emotional_context,
            tags={"session", "identity", session_id}
        )

        # Update session tracking
        self.consciousness_sessions[session_id]["memory_folds"].add(fold_id)
        self.session_memory_mappings[session_id].add(fold_id)

        return fold_id

    async def _create_awareness_memory_fold(self, session_id: str, awareness: AwarenessSnapshot) -> Optional[str]:
        """Create memory fold for awareness anomalies"""

        if not awareness.anomalies:
            return None

        content = {
            "session_id": session_id,
            "anomalies": awareness.anomalies,
            "drift_ema": awareness.drift_ema,
            "load_factor": awareness.load_factor,
            "signal_count": len(awareness.signals) if awareness.signals else 0
        }

        # High arousal for anomalies
        emotional_context = EmotionalContext(
            valence=-0.2,  # Slightly negative for anomalies
            arousal=0.8,   # High arousal for attention
            dominance=0.4, # Lower control due to anomalies
            confidence=0.8
        )

        fold_id = await self.memory_integrator.create_consciousness_memory_fold(
            content=content,
            fold_type=MemoryFoldType.EPISODIC,
            consciousness_context=f"session_{session_id}_awareness",
            emotional_context=emotional_context,
            tags={"awareness", "anomaly", session_id}
        )

        self.session_memory_mappings[session_id].add(fold_id)
        return fold_id

    async def _create_reflection_memory_fold(self, session_id: str, reflection: ReflectionReport) -> Optional[str]:
        """Create memory fold for reflection concerns"""

        content = {
            "session_id": session_id,
            "coherence_score": reflection.coherence_score,
            "drift_ema": reflection.drift_ema,
            "state_delta_magnitude": reflection.state_delta_magnitude,
            "reflection_duration_ms": reflection.reflection_duration_ms
        }

        # Emotional context based on coherence score
        valence = (reflection.coherence_score - 0.5) * 2.0  # Map 0-1 to -1,1
        emotional_context = EmotionalContext(
            valence=valence,
            arousal=0.6,  # Moderate arousal for reflection
            dominance=0.8, # High control for self-reflection
            confidence=0.9
        )

        fold_id = await self.memory_integrator.create_consciousness_memory_fold(
            content=content,
            fold_type=MemoryFoldType.SEMANTIC,
            consciousness_context=f"session_{session_id}_reflection",
            emotional_context=emotional_context,
            tags={"reflection", "coherence", session_id}
        )

        self.session_memory_mappings[session_id].add(fold_id)
        return fold_id

    async def _create_dream_memory_fold(self, session_id: str, dream: DreamTrace) -> Optional[str]:
        """Create memory fold for dream processing"""

        content = {
            "session_id": session_id,
            "dream_phase": dream.phase if hasattr(dream, 'phase') else "unknown",
            "consolidation_results": dream.consolidation_results if hasattr(dream, 'consolidation_results') else {},
            "memory_integration_count": dream.memory_integration_count if hasattr(dream, 'memory_integration_count') else 0
        }

        # Creative/mystical emotional context for dreams
        emotional_context = EmotionalContext(
            valence=0.3,  # Slightly positive for creative dreams
            arousal=0.4,  # Moderate arousal for dream state
            dominance=0.2, # Low control in dream state
            confidence=0.6  # Dreams are less certain
        )

        fold_id = await self.memory_integrator.create_consciousness_memory_fold(
            content=content,
            fold_type=MemoryFoldType.DREAM,
            consciousness_context=f"session_{session_id}_dream",
            emotional_context=emotional_context,
            tags={"dream", "consolidation", session_id}
        )

        self.session_memory_mappings[session_id].add(fold_id)
        return fold_id

    async def _sync_consciousness_to_memory(self, session_id: str) -> Optional[str]:
        """Sync consciousness state changes to memory"""

        session = self.consciousness_sessions[session_id]
        consciousness_state = session["consciousness_state"]

        # Create memory fold for current consciousness state
        content = {
            "session_id": session_id,
            "sync_type": "consciousness_to_memory",
            "consciousness_state": consciousness_state,
            "sync_timestamp": datetime.utcnow().isoformat()
        }

        fold_id = await self.memory_integrator.create_consciousness_memory_fold(
            content=content,
            fold_type=MemoryFoldType.PROCEDURAL,
            consciousness_context=f"session_{session_id}_sync",
            tags={"sync", "consciousness", session_id}
        )

        return fold_id

    async def _sync_memory_to_consciousness(self, session_id: str) -> int:
        """Sync relevant memories to consciousness"""

        self.consciousness_sessions[session_id]
        consciousness_context = f"session_{session_id}"

        # Query for relevant memories
        query = {
            "session_relevance": True,
            "consciousness_context": consciousness_context
        }

        memories = await self.memory_integrator.recall_consciousness_memory(
            query=query,
            consciousness_context=consciousness_context,
            max_results=5
        )

        # Integrate relevant memories
        integration_count = 0
        for fold_id, memory_fold, relevance in memories:
            if relevance > 0.7:  # High relevance threshold
                await self.integrate_memory_into_consciousness(session_id, memory_fold)
                integration_count += 1

        return integration_count

    async def _queue_consciousness_to_memory_event(self, event: MemoryConsciousnessEvent):
        """Queue event for consciousness-to-memory synchronization"""
        if len(self.consciousness_to_memory_queue) >= self.max_queue_size:
            # Remove oldest event
            self.consciousness_to_memory_queue.popleft()

        self.consciousness_to_memory_queue.append(event)

    async def _queue_memory_to_consciousness_event(self, event: MemoryConsciousnessEvent):
        """Queue event for memory-to-consciousness synchronization"""
        if len(self.memory_to_consciousness_queue) >= self.max_queue_size:
            # Remove oldest event
            self.memory_to_consciousness_queue.popleft()

        self.memory_to_consciousness_queue.append(event)

    async def _register_default_handlers(self):
        """Register default event handlers"""

        # Memory event handlers
        self.memory_event_handlers["memory_fold_created"].append(self._handle_memory_fold_created)
        self.memory_event_handlers["memory_recalled"].append(self._handle_memory_recalled)

        # Consciousness event handlers
        self.consciousness_event_handlers["consciousness_state_changed"].append(self._handle_consciousness_state_changed)
        self.consciousness_event_handlers["decision_made"].append(self._handle_decision_made)

    async def _handle_memory_fold_created(self, event_data: Dict[str, Any]):
        """Handle memory fold creation events"""
        fold_id = event_data.get("fold_id")
        consciousness_context = event_data.get("consciousness_context")

        if fold_id and consciousness_context:
            # Update mappings
            self.memory_consciousness_map[fold_id] = consciousness_context

            if consciousness_context not in self.consciousness_memory_map:
                self.consciousness_memory_map[consciousness_context] = set()
            self.consciousness_memory_map[consciousness_context].add(fold_id)

    async def _handle_memory_recalled(self, event_data: Dict[str, Any]):
        """Handle memory recall events"""
        event_data.get("session_id")
        result_count = event_data.get("result_count", 0)

        self.metrics.memory_write_rate = result_count / max(1, self.sync_interval_ms / 1000)

    async def _handle_consciousness_state_changed(self, event_data: Dict[str, Any]):
        """Handle consciousness state change events"""
        session_id = event_data.get("session_id")

        if session_id and session_id in self.consciousness_sessions:
            self.metrics.consciousness_update_rate += 1

    async def _handle_decision_made(self, event_data: Dict[str, Any]):
        """Handle decision-making events"""
        session_id = event_data.get("session_id")
        decision_data = event_data.get("decision_data", {})

        # Create memory fold for important decisions
        if decision_data.get("approved") and decision_data.get("confidence", 0) > 0.7:
            content = {
                "session_id": session_id,
                "decision_type": "autonomous_decision",
                "confidence": decision_data.get("confidence"),
                "action_count": decision_data.get("action_count", 0)
            }

            await self.memory_integrator.create_consciousness_memory_fold(
                content=content,
                fold_type=MemoryFoldType.PROCEDURAL,
                consciousness_context=f"session_{session_id}_decision",
                tags={"decision", "autonomous", session_id}
            )

    async def _sync_loop(self):
        """Main synchronization loop"""
        while not self._shutdown_event.is_set():
            try:
                if self.sync_mode == SyncMode.REAL_TIME:
                    await self._process_real_time_sync()
                elif self.sync_mode == SyncMode.BATCH:
                    await self._process_batch_sync()
                else:  # ADAPTIVE
                    await self._process_adaptive_sync()

                await asyncio.sleep(self.sync_interval_ms / 1000)

            except Exception as e:
                logger.error(f"❌ Sync loop error: {e}")
                self.metrics.error_count += 1
                await asyncio.sleep(1.0)

    async def _process_real_time_sync(self):
        """Process real-time synchronization"""
        # Process consciousness-to-memory events
        while self.consciousness_to_memory_queue:
            event = self.consciousness_to_memory_queue.popleft()
            await self._process_consciousness_to_memory_event(event)

        # Process memory-to-consciousness events
        while self.memory_to_consciousness_queue:
            event = self.memory_to_consciousness_queue.popleft()
            await self._process_memory_to_consciousness_event(event)

    async def _process_batch_sync(self):
        """Process batch synchronization"""
        # Process events in batches
        batch_size = min(self.batch_size, len(self.consciousness_to_memory_queue))
        for _ in range(batch_size):
            if self.consciousness_to_memory_queue:
                event = self.consciousness_to_memory_queue.popleft()
                await self._process_consciousness_to_memory_event(event)

        batch_size = min(self.batch_size, len(self.memory_to_consciousness_queue))
        for _ in range(batch_size):
            if self.memory_to_consciousness_queue:
                event = self.memory_to_consciousness_queue.popleft()
                await self._process_memory_to_consciousness_event(event)

    async def _process_adaptive_sync(self):
        """Process adaptive synchronization based on load"""
        total_events = len(self.consciousness_to_memory_queue) + len(self.memory_to_consciousness_queue)

        if total_events > 50:
            # High load - use batch processing
            await self._process_batch_sync()
        elif total_events > 0:
            # Normal load - use real-time processing
            await self._process_real_time_sync()

    async def _process_consciousness_to_memory_event(self, event: MemoryConsciousnessEvent):
        """Process consciousness-to-memory synchronization event"""
        try:
            payload = event.payload
            action = payload.get("action")

            if action == "session_created":
                # Handle session creation
                pass
            elif action == "session_updated":
                # Handle session update
                memory_events = payload.get("memory_events", [])
                for event_type, fold_id in memory_events:
                    # Process memory events
                    pass

            # Call registered handlers
            for handler in self.consciousness_event_handlers.get(action, []):
                await handler(payload)

        except Exception as e:
            logger.error(f"❌ Failed to process consciousness-to-memory event: {e}")

    async def _process_memory_to_consciousness_event(self, event: MemoryConsciousnessEvent):
        """Process memory-to-consciousness synchronization event"""
        try:
            payload = event.payload
            action = payload.get("action")

            # Call registered handlers
            for handler in self.memory_event_handlers.get(action, []):
                await handler(payload)

        except Exception as e:
            logger.error(f"❌ Failed to process memory-to-consciousness event: {e}")

    async def _monitor_loop(self):
        """Background monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Update metrics
                self.metrics.total_memory_folds = len(self.memory_integrator._memory_folds)
                self.metrics.active_consciousness_sessions = len(self.consciousness_sessions)

                # Clean up old sessions
                await self._cleanup_old_sessions()

                await asyncio.sleep(30.0)  # Monitor every 30 seconds

            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                await asyncio.sleep(10.0)

    async def _cleanup_old_sessions(self):
        """Clean up old consciousness sessions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        sessions_to_remove = []

        for session_id, session_data in self.consciousness_sessions.items():
            if session_data["last_updated"] < cutoff_time:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            await self._remove_consciousness_session(session_id)

    async def _remove_consciousness_session(self, session_id: str):
        """Remove consciousness session and clean up mappings"""
        if session_id in self.consciousness_sessions:
            del self.consciousness_sessions[session_id]

        if session_id in self.session_memory_mappings:
            # Clean up memory mappings
            fold_ids = self.session_memory_mappings[session_id]
            for fold_id in fold_ids:
                self.memory_consciousness_map.pop(fold_id, None)

            del self.session_memory_mappings[session_id]

        self.metrics.active_consciousness_sessions = max(0, self.metrics.active_consciousness_sessions - 1)
        logger.debug(f"🗑️ Removed consciousness session: {session_id}")

    def get_bridge_metrics(self) -> Dict[str, Any]:
        """Get comprehensive bridge metrics"""
        return {
            "bridge_state": self.state.value,
            "sync_mode": self.sync_mode.value,
            "metrics": asdict(self.metrics),
            "queue_sizes": {
                "consciousness_to_memory": len(self.consciousness_to_memory_queue),
                "memory_to_consciousness": len(self.memory_to_consciousness_queue)
            },
            "session_count": len(self.consciousness_sessions),
            "mapping_counts": {
                "memory_consciousness_map": len(self.memory_consciousness_map),
                "consciousness_memory_map": len(self.consciousness_memory_map)
            },
            "recent_sync_history": list(self.sync_history)[-10:],
            "recent_errors": list(self.error_history)[-5:]
        }
