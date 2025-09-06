"""
Enhanced dream engine system integrating quantum features and dream reflection with FastAPI.

This module combines the best features from both prototypes:
- Quantum-enhanced dream processing from prot2
- Dream reflection and memory consolidation from prot1
- Dream storage and retrieval capabilities
- FastAPI web interface for dream processing

ΛTAG: dream_engine, fastapi, quantum, symbolic_ai, oneiric_core
ΛLOCKED: false
ΛCANONICAL: Consolidated FastAPI-enabled dream engine
"""

import asyncio
import contextlib
import logging
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger("enhanced_dream_fastapi")

# FastAPI imports


# TODO: Update to use unified tier system
# - Replace custom tier validation with @oneiric_tier_required decorator
# - Update user authentication to use centralized identity system
# - Add consent checking for dream operations
# - See TIER_UNIFICATION_MIGRATION_GUIDE.md for details

# LUKHAS imports (with fallback handling)
try:
    from dream.core.dream_engine import DreamEngineSystem
    from dream.core.qi_dream_adapter import DreamQuantumConfig, QIDreamAdapter

    from bio.core import BioOrchestrator
    from candidate.core.bio_systems.qi_layer import QIBioOscillator
    from candidate.core.unified_integration import UnifiedIntegration
    from consciousness.core_consciousness.dream_engine.dream_reflection_loop import (
        DreamReflectionLoop,
    )
    from lukhas.memory.core_memory.dream_memory_manager import DreamMemoryManager

    BIO_CORE_AVAILABLE = True
    MEMORY_MANAGER_AVAILABLE = True
    logger.info("Bio-core dream system and memory manager integration available")
except ImportError as e:
    logger.warning(f"Some LUKHAS modules not available: {e}")
    BIO_CORE_AVAILABLE = False
    MEMORY_MANAGER_AVAILABLE = False

    # Fallback classes
    class QIDreamAdapter:
        def __init__(self, *args, **kwargs):
            pass

    class DreamQuantumConfig:
        def __init__(self, *args, **kwargs):
            pass

    class BioOrchestrator:
        def __init__(self, *args, **kwargs):
            pass

    class QIBioOscillator:
        def __init__(self, *args, **kwargs):
            pass

    class UnifiedIntegration:
        def __init__(self, *args, **kwargs):
            pass

    class DreamEngineSystem:
        def __init__(self, *args, **kwargs):
            pass

    class DreamMemoryManager:
        def __init__(self, *args, **kwargs):
            pass

    class DreamReflectionLoop:
        def __init__(self, *args, **kwargs):
            pass


# ΛTAG: dream_engine, fastapi, quantum, symbolic_ai, oneiric_core
logger = logging.getLogger("enhanced_dream_fastapi")


# FastAPI models
class DreamRequest(BaseModel):
    """Request model for dream processing."""

    dream_content: str = Field(..., description="The dream content to process")
    qi_enhanced: bool = Field(default=True, description="Enable quantum-inspired processing")
    reflection_enabled: bool = Field(default=True, description="Enable dream reflection")
    symbolic_tags: list[str] = Field(default_factory=list, description="Symbolic tags")


class DreamResponse(BaseModel):
    """Response model for dream processing."""

    dream_id: str = Field(..., description="Unique dream identifier")
    processed_content: str = Field(..., description="Processed dream content")
    qi_metrics: dict[str, Any] = Field(default_factory=dict, description="Quantum-inspired processing metrics")
    reflection_results: dict[str, Any] = Field(default_factory=dict, description="Dream reflection results")
    symbolic_analysis: dict[str, Any] = Field(default_factory=dict, description="Symbolic analysis results")
    processing_time: float = Field(..., description="Processing time in seconds")


# FastAPI app initialization
app = FastAPI(
    title="LUKHAS Dream Engine API",
    description="FastAPI interface for the enhanced dream engine system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnhancedDreamEngine:
    """
    Enhanced dream engine combining quantum-inspired processing with advanced dream reflection.

    Features:
    - Quantum-enhanced dream processing using bio-oscillators
    - Memory consolidation with dream reflection
    - Dream storage and retrieval with emotional context
    - Integration with brain systems

    #ΛDREAM_LOOP #ΛMEMORY_TRACE
    """

    # ΛTAG: dream
    # ΛTAG: drift
    # ΛTAG: delta

    def __init__(
        self,
        orchestrator: BioOrchestrator,
        integration: UnifiedIntegration,
        config: Optional[DreamQuantumConfig] = None,
    ):
        """Initialize enhanced dream engine

        Args:
            orchestrator: Bio-orchestrator for quantum operations
            integration: Integration layer reference
            config: Optional quantum configuration
        """
        self.orchestrator = orchestrator
        self.integration = integration
        self.config = config or DreamQuantumConfig()

        # Initialize quantum adapter
        self.qi_adapter = QIDreamAdapter(orchestrator=self.orchestrator, config=self.config)

        # Initialize bio-core dream system integration
        if BIO_CORE_AVAILABLE:
            self.bio_dream_system = DreamEngineSystem(
                orchestrator=self.orchestrator,
                integration=self.integration,
                config_path=None,
            )
            logger.info("Bio-core dream system integrated")
        else:
            self.bio_dream_system = None
            logger.warning("Bio-core dream system not available")

        # Initialize memory manager integration
        if MEMORY_MANAGER_AVAILABLE:
            self.memory_manager = DreamMemoryManager()
            logger.info("Dream memory manager integrated")
        else:
            self.memory_manager = None
            logger.warning("Dream memory manager not available")

        # Initialize dream reflection loop
        self.dream_reflection = DreamReflectionLoop(
            core_interface=self.integration,
            brain_integration=None,
            bio_orchestrator=self.orchestrator,
            config=self.config.__dict__ if hasattr(self.config, "__dict__") else {},
        )

        # Initialize dream reflection components
        self.active = False
        self.processing_task = None
        self.current_cycle = None

        # Register with integration layer
        self.integration.register_component("enhanced_dream_engine", self.handle_message)

        logger.info("Enhanced dream engine initialized")

    @property
    def reflection_loop(self) -> DreamReflectionLoop:
        """Get the dream reflection loop instance."""
        return self.dream_reflection

    async def handle_message(self, message: dict[str, Any]) -> None:
        """Handle incoming messages

        Args:
            message: The message to handle
        """
        try:
            action = message.get("action")
            content = message.get("content", {})

            if action == "start_dream_cycle":
                await self._handle_start_cycle(content)
            elif action == "stop_dream_cycle":
                await self._handle_stop_cycle(content)
            elif action == "process_memory":
                await self._handle_process_memory(content)
            elif action == "consolidate_dreams":
                await self._handle_consolidate_dreams(content)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    # ΛPHASE_NODE
    async def start_dream_cycle(self, duration_minutes: int = 10) -> None:
        """Start a quantum-enhanced dream cycle

        Args:
            duration_minutes: Duration in minutes
        """
        if self.active:
            logger.warning("Dream cycle already active")
            return

        try:
            # Start quantum dream processing
            await self.qi_adapter.start_dream_cycle(duration_minutes)
            self.active = True

            # Start dream reflection task
            self.current_cycle = {
                "start_time": datetime.utcnow(),
                "duration_minutes": duration_minutes,
                "memories_processed": 0,
            }

            self.processing_task = asyncio.create_task(self._run_dream_cycle(duration_minutes))

            logger.info(f"Started enhanced dream cycle for {duration_minutes} minutes")

        except Exception as e:
            logger.error(f"Failed to start dream cycle: {e}")
            self.active = False

    # ΛPHASE_NODE
    async def stop_dream_cycle(self) -> None:
        """Stop the current dream cycle"""
        if not self.active:
            return

        try:
            # Stop quantum-inspired processing
            await self.qi_adapter.stop_dream_cycle()

            # Stop reflection task
            if self.processing_task:
                self.processing_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self.processing_task
                self.processing_task = None

            self.active = False
            self._log_cycle_stats()

            logger.info("Stopped dream cycle")

        except Exception as e:
            logger.error(f"Error stopping dream cycle: {e}")

    # ΛDREAM_LOOP #ΛRECALL_LOOP
    async def _run_dream_cycle(self, duration_minutes: int) -> None:
        """Run the dream cycle processing loop

        Args:
            duration_minutes: Duration in minutes
        """
        try:
            duration_seconds = duration_minutes * 60
            end_time = datetime.utcnow().timestamp() + duration_seconds

            while datetime.utcnow().timestamp() < end_time:
                # Process quantum dream state
                await self._process_quantum_dreams()

                # Run memory consolidation
                await self._consolidate_memories()

                # Brief pause between iterations
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Dream cycle cancelled")
        except Exception as e:
            logger.error(f"Error in dream cycle: {e}")
        finally:
            self.active = False

    # ΛMEMORY_TRACE
    async def _process_quantum_dreams(self) -> None:
        """Process dreams using superposition-like state"""
        try:
            # Get current quantum-like state
            q_state = await self.qi_adapter.get_quantum_like_state()

            # Extract dream insights
            if q_state.get("coherence", 0) >= self.config.coherence_threshold:
                insights = self._extract_dream_insights(q_state)

                # Store insights
                await self._store_dream_insights(insights)

        except Exception as e:
            logger.error(f"Error processing quantum dreams: {e}")

    # ΛMEMORY_TRACE #ΛCOLLAPSE_HOOK
    async def _consolidate_memories(self) -> None:
        """Run memory consolidation cycle with dream memory manager integration"""
        try:
            # Get memories waiting for consolidation
            unconsolidated = await self._get_unconsolidated_memories()

            for memory in unconsolidated:
                # Enhanced memory consolidation with dream memory manager
                if self.memory_manager:
                    # Use process_memory method instead of consolidate_memory
                    consolidated = await self.memory_manager.process_memory(memory)
                    if consolidated:
                        await self._store_consolidated_memory(consolidated)
                        if self.current_cycle:
                            self.current_cycle["memories_processed"] += 1

                # Also run dream reflection on the memory
                if self.dream_reflection:
                    # Use process_dream method instead of reflect
                    reflection_result = await self.dream_reflection.process_dream(memory.get("content", ""))
                    # Store reflection result
                    await self._store_dream_reflection(
                        {
                            "memory_id": memory.get("id"),
                            "reflection": reflection_result,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                # Bio-core rhythm integration
                if self.bio_dream_system:
                    await self._integrate_bio_rhythm(memory)

        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")

    async def _integrate_bio_rhythm(self, memory: dict[str, Any]) -> None:
        """Integrate memory processing with biological rhythm cycles"""
        try:
            if self.bio_dream_system and hasattr(self.bio_dream_system, "process_memory"):
                await self.bio_dream_system.process_memory(memory)
        except Exception as e:
            logger.error(f"Error integrating bio-rhythm: {e}")

    async def _store_consolidated_memory(self, memory: dict[str, Any]) -> None:
        """Store consolidated memory"""
        try:
            # For now, log the memory - in real implementation
            # this would store to persistent storage
            logger.info(f"Storing consolidated memory: {memory.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"Error storing consolidated memory: {e}")

    async def _store_dream_reflection(self, reflection: dict[str, Any]) -> None:
        """Store dream reflection result"""
        try:
            # For now, log the reflection - in real implementation
            # this would store to persistent storage
            logger.info(f"Storing dream reflection: {reflection.get('memory_id', 'unknown')}")
        except Exception as e:
            logger.error(f"Error storing dream reflection: {e}")

    async def _get_unconsolidated_memories(self) -> list[dict[str, Any]]:
        """Get memories waiting for consolidation"""
        try:
            # For now, simulate getting memories - in real implementation
            # this would query the actual memory storage
            memories = []
            return memories
        except Exception as e:
            logger.error(f"Error getting unconsolidated memories: {e}")
            return []

    async def _enhance_memory_quantum(self, memory: dict[str, Any]) -> dict[str, Any]:
        """Enhance memory with quantum-inspired processing

        Args:
            memory: The memory to enhance

        Returns:
            The enhanced memory
        """
        # Get quantum-like state
        q_state = await self.qi_adapter.get_quantum_like_state()

        # Apply quantum enhancement
        enhanced = memory.copy()
        enhanced["qi_coherence"] = q_state.get("coherence", 0)
        enhanced["qi_entanglement"] = q_state.get("entanglement", 0)

        # Add enhancement metadata
        enhanced["enhanced_timestamp"] = datetime.utcnow().isoformat()
        enhanced["enhancement_method"] = "quantum"

        return enhanced

    def _log_cycle_stats(self) -> None:
        """Log statistics from the current cycle"""
        if not self.current_cycle:
            return

        duration = datetime.utcnow() - self.current_cycle["start_time"]
        memories = self.current_cycle["memories_processed"]

        logger.info(f"Dream cycle completed: Duration={duration.total_seconds():.1f}s, Memories={memories}")

    async def _handle_start_cycle(self, content: dict[str, Any]) -> None:
        """Handle start cycle request"""
        duration = content.get("duration_minutes", 10)
        await self.start_dream_cycle(duration)

    async def _handle_stop_cycle(self, content: dict[str, Any]) -> None:
        """Handle stop cycle request"""
        await self.stop_dream_cycle()

    async def _handle_process_memory(self, content: dict[str, Any]) -> None:
        """Handle process memory request"""
        try:
            memory = content.get("memory")
            if not memory:
                logger.error("No memory provided")
                return

            enhanced = await self._enhance_memory_quantum(memory)
            await self._store_enhanced_memory(enhanced)

        except Exception as e:
            logger.error(f"Error processing memory: {e}")

    async def _handle_consolidate_dreams(self, content: dict[str, Any]) -> None:
        """Handle dream consolidation request"""
        try:
            await self._consolidate_memories()
        except Exception as e:
            logger.error(f"Error consolidating dreams: {e}")

    def _extract_dream_insights(self, qi_like_state: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract insights from qi dream state

        Args:
            qi_like_state: Current quantum-like state

        Returns:
            List of extracted insights
        """
        insights = []

        try:
            # Extract patterns from qi-like state
            coherence = qi_like_state.get("coherence", 0)
            entanglement = qi_like_state.get("entanglement", 0)

            if coherence >= self.config.coherence_threshold:
                # Create insight from high-coherence state
                insight = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "qi_pattern",
                    "coherence": coherence,
                    "entanglement": entanglement,
                    "confidence": coherence * entanglement,
                }
                insights.append(insight)

        except Exception as e:
            logger.error(f"Error extracting insights: {e}")

        return insights

    async def _store_dream_insights(self, insights: list[dict[str, Any]]) -> None:
        """Store extracted dream insights

        Args:
            insights: List of insights to store
        """
        try:
            for insight in insights:
                # Add storage metadata
                insight["storage_timestamp"] = datetime.utcnow().isoformat()

                # Store via integration layer
                await self.integration.store_data("dream_insights", insight)

        except Exception as e:
            logger.error(f"Error storing insights: {e}")

    async def _store_enhanced_memory(self, memory: dict[str, Any]) -> None:
        """Store an enhanced memory

        Args:
            memory: The enhanced memory to store
        """
        try:
            await self.integration.store_data("enhanced_memories", memory)
        except Exception as e:
            logger.error(f"Error storing enhanced memory: {e}")

    async def _store_enhanced_memory(self, memory: dict[str, Any]) -> None:
        """Store enhanced memory to persistent storage.

        Args:
            memory: The enhanced memory to store
        """
        try:
            # For now, log the memory - in real implementation
            # this would store to persistent storage
            logger.info(f"Storing enhanced memory: {memory.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"Error storing enhanced memory: {e}")

    async def _process_dreams_quantum(self, dreams: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process dreams through quantum-inspired processing

        Args:
            dreams: List of dreams to process

        Returns:
            List of processed dreams
        """
        processed_dreams = []

        for dream in dreams:
            try:
                # Check quantum-like state first
                qi_like_state = {
                    "coherence": 0.7,
                    "entanglement": 0.5,
                }  # Mock state

                if qi_like_state["coherence"] >= 0.5:
                    processed = await self._process_dream_quantum(dream, qi_like_state)
                    processed_dreams.append(processed)
                else:
                    logger.warning(f"Insufficient coherence-inspired processing for dream {dream.get('id', 'unknown')}")

            except Exception as e:
                logger.error(f"Error processing dream quantum: {e}")

        return processed_dreams

    async def process_dream(self, dream: dict[str, Any]) -> None:
        """Process a single dream

        Args:
            dream: The dream to process
        """
        if not self.active:
            logger.warning("Cannot process dream - engine not active")
            return

        try:
            # Update dream state
            dream["state"] = "processing"
            dream["metadata"]["last_processed"] = datetime.utcnow().isoformat()

            # Get current quantum-like state
            qi_like_state = await self.qi_adapter.get_quantum_like_state()

            # Only process if we have good coherence-inspired processing
            if qi_like_state["coherence"] >= self.config.coherence_threshold:
                # Extract dream patterns through quantum-inspired processing
                processed = await self._process_dream_quantum(dream, qi_like_state)

                # Store processed dream
                await self._store_processed_dream(processed)

                if self.current_cycle:
                    self.current_cycle["memories_processed"] += 1

            else:
                logger.warning(f"Insufficient coherence-inspired processing: {qi_like_state['coherence']:.2f}")

        except Exception as e:
            logger.error(f"Error processing dream: {e}")
            dream["state"] = "error"
            dream["metadata"]["error"] = str(e)

    async def _process_dream_quantum(self, dream: dict[str, Any], qi_like_state: dict) -> dict:
        """Process dream through quantum layer

        Args:
            dream: The dream to process
            qi_like_state: Current quantum-like state

        Returns:
            Dict: Processed dream with enhanced insights
        """
        # Deep copy to avoid modifying original
        processed = dict(dream)

        try:
            # Extract emotional patterns
            emotional = processed.get("emotional_context", {})

            # Quantum enhance the emotional context
            enhanced_emotions = await self.qi_adapter.enhance_emotional_state(emotional)

            # Get quantum insights
            insights = qi_like_state.get("insights", [])

            # Merge everything into the processed dream
            processed.update(
                {
                    "state": "consolidated",
                    "emotional_context": enhanced_emotions,
                    "qi_insights": insights,
                    "metadata": {
                        **processed.get("metadata", {}),
                        "qi_like_state": {
                            "coherence": qi_like_state["coherence"],
                            "timestamp": qi_like_state["timestamp"],
                        },
                        "consolidation_complete": True,
                        "consolidated_at": datetime.utcnow().isoformat(),
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error in quantum-inspired processing: {e}")
            processed["state"] = "error"
            processed["metadata"]["error"] = str(e)

        return processed

    async def _store_processed_dream(self, dream: dict[str, Any]) -> None:
        """Store a processed dream

        Args:
            dream: The processed dream to store
        """
        try:
            # Remove from unconsolidated memories
            unconsolidated = await self.integration.get_data("unconsolidated_memories")
            unconsolidated = [m for m in unconsolidated if m.get("id") != dream.get("id")]
            await self.integration.store_data("unconsolidated_memories", unconsolidated)

            # Add to enhanced memories
            await self.integration.store_data("enhanced_memories", dream)

        except Exception as e:
            logger.error(f"Error storing processed dream: {e}")


# Global dream engine instance
dream_engine_instance = None


def get_dream_engine():
    """Get or create the dream engine instance."""
    global dream_engine_instance
    if dream_engine_instance is None:
        # Initialize with fallback components
        try:
            orchestrator = BioOrchestrator()
            integration = UnifiedIntegration()
            dream_engine_instance = EnhancedDreamEngine(orchestrator, integration)
        except Exception as e:
            logger.error(f"Failed to initialize dream engine: {e}")
            # Create a minimal fallback
            dream_engine_instance = EnhancedDreamEngine(None, None)
    return dream_engine_instance


# FastAPI Routes
@app.get("/", summary="API Health Check")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LUKHAS Dream Engine API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/dream/process", response_model=DreamResponse, summary="Process Dream")
async def process_dream(request: DreamRequest):
    """
    Process a dream using the enhanced dream engine.

    ΛTAG: dream_processing, fastapi, quantum, symbolic_ai

    TODO: Add tier validation and user context
    - Add user parameter (from auth middleware)
    - Use @oneiric_tier_required(2) for standard dream processing
    - Extract user_id from authenticated user
    - Pass user_id to dream engine for tier-based features
    """
    start_time = datetime.now()

    try:
        dream_engine = get_dream_engine()

        # Generate unique dream ID
        dream_id = f"dream_{int(start_time.timestamp() * 1000)}"

        # Process the dream
        if hasattr(dream_engine, "process_dream"):
            result = await dream_engine.process_dream(
                {
                    "id": dream_id,
                    "content": request.dream_content,
                    "qi_enhanced": request.qi_enhanced,
                    "reflection_enabled": request.reflection_enabled,
                    "symbolic_tags": request.symbolic_tags,
                }
            )
        else:
            # Fallback processing
            result = {
                "id": dream_id,
                "processed_content": f"Processed: {request.dream_content}",
                "qi_metrics": {"enabled": request.qi_enhanced},
                "reflection_results": {"enabled": request.reflection_enabled},
                "symbolic_analysis": {"tags": request.symbolic_tags},
            }

        processing_time = (datetime.now() - start_time).total_seconds()

        return DreamResponse(
            dream_id=dream_id,
            processed_content=result.get("processed_content", ""),
            qi_metrics=result.get("qi_metrics", {}),
            reflection_results=result.get("reflection_results", {}),
            symbolic_analysis=result.get("symbolic_analysis", {}),
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Dream processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Dream processing failed: {e!s}")


@app.get("/dream/{dream_id}", summary="Get Dream")
async def get_dream(dream_id: str):
    """
    Retrieve a processed dream by ID.

    ΛTAG: dream_retrieval, fastapi, storage
    """
    try:
        dream_engine = get_dream_engine()

        # Try to retrieve the dream
        if hasattr(dream_engine, "get_dream"):
            dream = await dream_engine.get_dream(dream_id)
            if dream:
                return dream

        # Fallback response
        return {
            "id": dream_id,
            "status": "not_found",
            "message": "Dream not found or retrieval not implemented",
        }

    except Exception as e:
        logger.error(f"Dream retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Dream retrieval failed: {e!s}")


@app.get("/dreams", summary="List Dreams")
async def list_dreams(limit: int = 10, offset: int = 0):
    """
    List processed dreams with pagination.

    ΛTAG: dream_listing, fastapi, pagination
    """
    try:
        dream_engine = get_dream_engine()

        # Try to list dreams
        if hasattr(dream_engine, "list_dreams"):
            dreams = await dream_engine.list_dreams(limit=limit, offset=offset)
            return {
                "dreams": dreams,
                "limit": limit,
                "offset": offset,
                "count": len(dreams),
            }

        # Fallback response
        return {
            "dreams": [],
            "limit": limit,
            "offset": offset,
            "count": 0,
            "message": "Dream listing not implemented",
        }

    except Exception as e:
        logger.error(f"Dream listing error: {e}")
        raise HTTPException(status_code=500, detail=f"Dream listing failed: {e!s}")


@app.get("/status", summary="Dream Engine Status")
async def get_status():
    """
    Get the current status of the dream engine.

    ΛTAG: status, monitoring, fastapi
    """
    try:
        dream_engine = get_dream_engine()

        return {
            "status": ("active" if hasattr(dream_engine, "active") and dream_engine.active else "inactive"),
            "engine_type": "EnhancedDreamEngine",
            "qi_enabled": hasattr(dream_engine, "qi_adapter") and dream_engine.qi_adapter is not None,
            "reflection_enabled": True,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {e!s}")


# ================= PHASE 3B: MEMORY RECURRENCE LOOP & SNAPSHOT API =================


class SnapshotRequest(BaseModel):
    """Request model for creating dream snapshots."""

    fold_id: str = Field(..., description="Memory fold identifier")
    dream_state: dict[str, Any] = Field(..., description="Current dream state")
    introspective_content: dict[str, Any] = Field(..., description="Introspective analysis")
    symbolic_annotations: Optional[dict[str, Any]] = Field(None, description="Symbolic annotations")


class SnapshotResponse(BaseModel):
    """Response model for dream snapshot operations."""

    snapshot_id: str = Field(..., description="Unique snapshot identifier")
    fold_id: str = Field(..., description="Memory fold identifier")
    timestamp: str = Field(..., description="Snapshot creation timestamp")
    status: str = Field(..., description="Operation status")


@app.post("/memory/snapshot", response_model=SnapshotResponse, summary="Create Dream Snapshot")
async def create_dream_snapshot(request: SnapshotRequest):
    """
    Create a dream snapshot with symbolic annotation for memory recurrence.

    This endpoint implements the Phase 3B memory recurrence loop functionality,
    allowing for persistent introspective content with symbolic annotation.

    Tags: #LUKHAS_TAG: snapshot_memory, #RECUR_LOOP

    TODO: Add tier validation for memory snapshot creation
    - Requires LAMBDA_TIER_3 for snapshot creation
    - Add consent check for "memory_snapshot"
    - Include user_id in snapshot metadata
    """
    try:
        dream_engine = get_dream_engine()

        if not dream_engine.reflection_loop:
            raise HTTPException(status_code=503, detail="Dream reflection loop not available")

        snapshot_id = await dream_engine.reflection_loop.create_dream_snapshot(
            fold_id=request.fold_id,
            dream_state=request.dream_state,
            introspective_content=request.introspective_content,
            symbolic_annotations=request.symbolic_annotations,
        )

        if not snapshot_id:
            raise HTTPException(status_code=500, detail="Failed to create dream snapshot")

        return SnapshotResponse(
            snapshot_id=snapshot_id,
            fold_id=request.fold_id,
            timestamp=datetime.now().isoformat(),
            status="created",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dream snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Snapshot creation failed: {e!s}")


@app.get("/memory/fold/{fold_id}/snapshots", summary="Get Memory Fold Snapshots")
async def get_fold_snapshots(fold_id: str):
    """
    Get all snapshots for a memory fold.

    Retrieves all dream snapshots stored in the specified memory fold,
    providing access to the complete history of introspective content.
    """
    try:
        dream_engine = get_dream_engine()

        if not dream_engine.reflection_loop:
            raise HTTPException(status_code=503, detail="Dream reflection loop not available")

        snapshots = await dream_engine.reflection_loop.get_fold_snapshots(fold_id)

        return {
            "fold_id": fold_id,
            "snapshot_count": len(snapshots),
            "snapshots": snapshots,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving fold snapshots: {e}")
        raise HTTPException(status_code=500, detail=f"Snapshot retrieval failed: {e!s}")


@app.get("/memory/fold/{fold_id}/statistics", summary="Get Memory Fold Statistics")
async def get_fold_statistics(fold_id: str):
    """
    Get statistics and metrics for a memory fold.

    Provides comprehensive statistics about the memory fold including
    convergence scores, drift metrics, and symbolic analysis.
    """
    try:
        dream_engine = get_dream_engine()

        if not dream_engine.reflection_loop:
            raise HTTPException(status_code=503, detail="Dream reflection loop not available")

        stats = await dream_engine.reflection_loop.get_fold_statistics(fold_id)

        return {
            "fold_id": fold_id,
            "statistics": stats,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving fold statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {e!s}")


@app.post("/memory/fold/{fold_id}/sync", summary="Synchronize Memory Fold")
async def sync_memory_fold(fold_id: str):
    """
    Synchronize a memory fold with persistent storage.

    Ensures all snapshots and fold metadata are persisted to storage,
    enabling reliable memory recurrence across system restarts.
    """
    try:
        dream_engine = get_dream_engine()

        if not dream_engine.reflection_loop:
            raise HTTPException(status_code=503, detail="Dream reflection loop not available")

        success = await dream_engine.reflection_loop.sync_memory_fold(fold_id)

        return {
            "fold_id": fold_id,
            "sync_successful": success,
            "timestamp": datetime.now().isoformat(),
            "status": "synchronized" if success else "failed",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing memory fold: {e}")
        raise HTTPException(status_code=500, detail=f"Fold synchronization failed: {e!s}")


# ================= END PHASE 3B ENDPOINTS =================


# Main execution
if __name__ == "__main__":
    import uvicorn

    # ΛTAG: main, fastapi, server
    logger.info("Starting LUKHAS Dream Engine FastAPI server...")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
