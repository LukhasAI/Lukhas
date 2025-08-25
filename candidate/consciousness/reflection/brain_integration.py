"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


╔═══════════════════════════════════════════════════════════════════════════╗
║ MODULE        : brain_integration.py                                      ║
║ DESCRIPTION   : Core Brain Integration Module for LUCAS AGI               ║
║                 Connects memory, emotion, voice, LUCAS_ID and dreams      ║
║                 into a unified cognitive architecture                     ║
║ TYPE          : Core Neural Architecture         VERSION: v1.0.0          ║
║ AUTHOR        : LUCAS SYSTEMS                   CREATED: 2025-05-08       ║
╚═══════════════════════════════════════════════════════════════════════════╝
   DEPENDENCIES:
   - CORE.memory_learning.memory_manager
   - CORE.spine.fold_engine
   - DASHBOARD.lucas_as_agent.core.memory_folds (emotional memory)
   - AID.dream_engine
   - VOICE.voice_integrator
   - LUCAS_ID.vault
   - BIO_SYMBOLIC.quantum_attention
"""

from candidate.core.common import get_logger
import time
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from datetime import datetime
import os
import json
import uuid
import threading
from enum import Enum

# Configure logging
logger = logging.getLogger("lucas.brain")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Import core memory components - using try/except to handle potential import errors
try:
    # Import the sophisticated memory fold engine
#     from CORE.spine.fold_engine import (  # TODO: Install or implement CORE
        AGIMemory, MemoryFold, MemoryType, MemoryPriority, ContextReasoner
    )
except ImportError:
    logger.warning("Could not import fold_engine. Memory integration will be limited.")
    AGIMemory = None
    MemoryFold = None
    MemoryType = None
    MemoryPriority = None
    ContextReasoner = None

try:
    # Import the emotional memory components
#     from DASHBOARD.lucas_as_agent.core.memory_folds import (  # TODO: Install or implement DASHBOARD
        create_memory_fold,
        recall_memory_folds,
        calculate_emotion_distance,
        emotion_vectors,
    )
except ImportError:
    logger.warning("Could not import emotional memory folds. Emotional memory will be limited.")
    create_memory_fold = None
    recall_memory_folds = None
    calculate_emotion_distance = None
    emotion_vectors = None

try:
    # Import advanced memory manager
#     from CORE.memory_learning.memory_manager import (  # TODO: Install or implement CORE
        MemoryManager, MemoryAccessError
    )
except ImportError:
    logger.warning("Could not import lukhas.memory manager. Access control will be limited.")
    MemoryManager = None
    
# Import additional components with error handling
try:
    from LUCAS_ID.vault.lucas_id import LucasID, AccessTier
except ImportError:
    logger.warning("Could not import LUCAS_ID components. Identity integration will be limited.")
    LucasID = None
    class AccessTier(Enum):
        """Fallback access tier enum if import fails"""
        TIER_1 = 1
        TIER_2 = 2
        TIER_3 = 3
        TIER_4 = 4
        TIER_5 = 5

try:
#     from BIO_SYMBOLIC.quantum_attention import QIAttention  # TODO: Install or implement BIO_SYMBOLIC
except ImportError:
    logger.warning("Could not import qi attention. Cognitive integration will be limited.")
    QIAttention = None

try:
#     from AID.dream_engine.dream_reflection_loop import DreamReflectionLoop  # TODO: Install or implement AID
except ImportError:
    logger.warning("Could not import dream reflection loop. Dream integration will be limited.")
    DreamReflectionLoop = None

try:
    from VOICE.voice_integrator import VoiceIntegrator
except ImportError:
    logger.warning("Could not import voice integrator. Voice integration will be limited.")
    VoiceIntegrator = None


class EmotionVector:
    """Handles emotional vector operations and distance calculations"""
    
    def __init__(self):
        """Initialize the emotion vector system"""
        # Import emotion vectors from memory_folds or create default emotional space
        self.emotion_vectors = emotion_vectors if emotion_vectors else {
            # Default basic emotions if import failed
            "neutral": [0.0, 0.0, 0.0],
            "joy": [0.8, 0.9, 0.3],
            "sadness": [-0.8, -0.7, -0.2],
            "anger": [-0.8, 0.7, 0.3],
            "fear": [-0.7, 0.8, 0.0],
            "trust": [0.7, 0.5, 0.2],
            "surprise": [0.0, 0.9, 0.8],
            "anticipation": [0.6, 0.8, 0.0],
        }
        
    def calculate_distance(self, emotion1: str, emotion2: str) -> float:
        """Calculate the distance between two emotions in vector space"""
        if calculate_emotion_distance:
            # Use imported function if available
            return calculate_emotion_distance(emotion1, emotion2)
        else:
            # Fallback implementation
            if emotion1 not in self.emotion_vectors:
                emotion1 = "neutral"
            if emotion2 not in self.emotion_vectors:
                emotion2 = "neutral"
                
            import numpy as np
            vec1 = np.array(self.emotion_vectors[emotion1])
            vec2 = np.array(self.emotion_vectors[emotion2])
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            # Convert to distance (0-2, where lower is more similar)
            return 1.0 - similarity
            
    def closest_emotion(self, target_emotion: str, limit: int = 3) -> List[Tuple[str, float]]:
        """Find the closest emotions to a target emotion"""
        if target_emotion not in self.emotion_vectors:
            target_emotion = "neutral"
            
        distances = []
        for emotion in self.emotion_vectors:
            if emotion == target_emotion:
                continue
                
            distance = self.calculate_distance(target_emotion, emotion)
            distances.append((emotion, distance))
            
        # Sort by distance (closest first)
        distances.sort(key=lambda x: x[1])
        return distances[:limit]
        
    def get_vector(self, emotion: str) -> List[float]:
        """Get the vector for a specified emotion"""
        if emotion in self.emotion_vectors:
            return self.emotion_vectors[emotion]
        return self.emotion_vectors["neutral"]


class EmotionalOscillator:
    """
    Emotional oscillator that maintains emotional state and modulates responses.
    This component bridges emotional memory with voice/output modulation.
    """
    
    def __init__(self):
        """Initialize the emotional oscillator"""
        self.current_state = {
            "primary_emotion": "neutral",
            "intensity": 0.5,
            "secondary_emotions": {},  # emotion -> intensity
            "last_updated": datetime.now().isoformat(),
            "stability": 0.8,  # How stable the emotion is (0-1)
        }
        self.emotional_trend = []  # Track emotional changes over time
        self.emotion_vector = EmotionVector()
        self.max_trend_length = 20  # Max number of trend points to keep
        
    def update_emotional_state(self, 
                             primary_emotion: str,
                             intensity: float = None,
                             secondary_emotions: Dict[str, float] = None,
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update the current emotional state"""
        # Store previous state in trend before updating
        self.emotional_trend.append(self.current_state.copy())
        if len(self.emotional_trend) > self.max_trend_length:
            self.emotional_trend = self.emotional_trend[-self.max_trend_length:]
            
        # Update primary emotion if valid, otherwise keep current
        if primary_emotion in self.emotion_vector.emotion_vectors:
            self.current_state["primary_emotion"] = primary_emotion
            
        # Update intensity if provided
        if intensity is not None:
            self.current_state["intensity"] = max(0.0, min(1.0, intensity))
            
        # Update secondary emotions if provided
        if secondary_emotions:
            # Filter invalid emotions and normalize intensities
            valid_secondary = {
                e: max(0.0, min(1.0, i))
                for e, i in secondary_emotions.items():
                if e in self.emotion_vector.emotion_vectors:
            }
            self.current_state["secondary_emotions"] = valid_secondary
            
        # Update timestamp
        self.current_state["last_updated"] = datetime.now().isoformat()
        
        # Update stability based on how much the emotion changed
        if self.emotional_trend:
            previous = self.emotional_trend[-1]
            previous_emotion = previous["primary_emotion"]
            emotional_distance = self.emotion_vector.calculate_distance(
                previous_emotion,
                self.current_state["primary_emotion"]
            )
            # Higher distance = lower stability
            self.current_state["stability"] = max(0.1, 1.0 - (emotional_distance / 2.0))
            
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                if key not in ["primary_emotion", "intensity", "secondary_emotions", "last_updated", "stability"]:
                    self.current_state[key] = value
                    
        return self.current_state
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current emotional state"""
        return self.current_state
        
    def get_voice_modulation_params(self) -> Dict[str, Any]:
        """
        Generate voice modulation parameters based on the current emotional state.
        This bridges the emotional state to voice synthesis.
        """
        emotion = self.current_state["primary_emotion"]
        intensity = self.current_state["intensity"]
        stability = self.current_state["stability"]
        
        # Default parameters
        params = {
            "pitch_adjustment": 0.0,
            "speed_adjustment": 0.0,
            "energy_adjustment": 0.0,
            "pause_threshold": 0.3,
            "emphasis_level": 0.5,
        }
        
        # Apply emotion-specific adjustments
        emotion_adjustments = {
            "joy": {"pitch": 0.3, "speed": 0.2, "energy": 0.4, "emphasis": 0.7},
            "sadness": {"pitch": -0.3, "speed": -0.25, "energy": -0.3, "emphasis": 0.3},
            "anger": {"pitch": 0.2, "speed": 0.3, "energy": 0.5, "emphasis": 0.8},
            "fear": {"pitch": 0.4, "speed": 0.4, "energy": 0.2, "emphasis": 0.6},
            "surprise": {"pitch": 0.5, "speed": 0.1, "energy": 0.4, "emphasis": 0.7},
            "trust": {"pitch": -0.1, "speed": -0.1, "energy": 0.1, "emphasis": 0.4},
            "anticipation": {"pitch": 0.2, "speed": 0.1, "energy": 0.3, "emphasis": 0.6}
        }
        
        # Get adjustments for current emotion or use neutral
        adjustments = emotion_adjustments.get(emotion, {"pitch": 0, "speed": 0, "energy": 0, "emphasis": 0.5})
        
        # Apply adjustments, scaled by intensity
        params["pitch_adjustment"] = adjustments["pitch"] * intensity
        params["speed_adjustment"] = adjustments["speed"] * intensity
        params["energy_adjustment"] = adjustments["energy"] * intensity
        params["emphasis_level"] = adjustments["emphasis"] * intensity
        
        # Stability affects pauses (less stable = more varied pauses)
        params["pause_threshold"] = 0.3 + ((1.0 - stability) * 0.2)
        
        # Add secondary emotion influences
        secondary_emotions = self.current_state["secondary_emotions"]
        for emotion, sec_intensity in secondary_emotions.items():
            if emotion in emotion_adjustments and sec_intensity > 0.3:
                # Blend in secondary emotion effects at reduced strength
                sec_adjustments = emotion_adjustments[emotion]
                blend_factor = sec_intensity * 0.3  # 30% influence maximum
                
                params["pitch_adjustment"] += sec_adjustments["pitch"] * blend_factor
                params["speed_adjustment"] += sec_adjustments["speed"] * blend_factor
                params["energy_adjustment"] += sec_adjustments["energy"] * blend_factor
        
        # Ensure parameters are within reasonable ranges
        params["pitch_adjustment"] = max(-0.5, min(0.5, params["pitch_adjustment"]))
        params["speed_adjustment"] = max(-0.5, min(0.5, params["speed_adjustment"]))
        params["energy_adjustment"] = max(-0.5, min(0.5, params["energy_adjustment"]))
        
        return params


class MemoryEmotionalIntegrator:
    """
    Integrates the sophisticated memory system (AGIMemory) with the emotional memory system,
    providing a unified interface for emotional memory storing and retrieval.
    """
    
    def __init__(self, 
                memory_manager=None, 
                emotional_oscillator=None, 
                memory_path: str = "./memory_store"):
        """
        Initialize the Memory Emotional Integrator
        
        Args:
            memory_manager: Optional memory manager instance
            emotional_oscillator: Optional emotional oscillator instance
            memory_path: Path for storing memory data
        """
        self.memory_path = memory_path
        os.makedirs(memory_path, exist_ok=True)
        
        # Use provided components or create new ones
        self.memory_manager = memory_manager or (MemoryManager(memory_path) if MemoryManager else None)
        self.emotional_oscillator = emotional_oscillator or EmotionalOscillator()
        
        # Create primary memory fold system if imports succeeded
        if AGIMemory:
            self.memory_folds = AGIMemory()
            self.context_reasoner = ContextReasoner(self.memory_folds)
        else:
            self.memory_folds = None
            self.context_reasoner = None
            
        # Initialize emotional vector system
        self.emotion_vector = EmotionVector()
        
        # Track emotional memory statistics
        self.stats = {
            "total_memories": 0,
            "emotional_memories": 0,
            "emotional_recalls": 0,
            "consolidated_memories": 0
        }
        
        logger.info("Memory Emotional Integrator initialized")
    
    def store_memory_with_emotion(self,
                                key: str,
                                content: Any,
                                emotion: str = None,
                                tags: List[str] = None,
                                owner_id: str = None,
                                priority: Any = None,
                                additional_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Store memory with emotional context
        
        Args:
            key: Unique memory identifier
            content: Memory content to store
            emotion: Emotion to associate with memory (uses current state if None)
            tags: Optional tags for categorical retrieval
            owner_id: Optional owner identifier for access control
            priority: Optional priority level
            additional_metadata: Optional additional metadata
            
        Returns:
            Dict with status and memory information
        """
        # Get current emotional state if no emotion specified
        if emotion is None and self.emotional_oscillator:
            emotion = self.emotional_oscillator.get_current_state()["primary_emotion"]
            
        # Create basic metadata
        metadata = additional_metadata or {}
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["emotion"] = emotion
        
        # Add emotional vector
        if emotion:
            metadata["emotion_vector"] = self.emotion_vector.get_vector(emotion)
            
        # Store in sophisticated memory system if available
        status = {"memory_fold": False, "memory_manager": False}
        
        if self.memory_folds:
            # Determine memory type and priority
            memory_type = MemoryType.SEMANTIC
            if "memory_type" in metadata:
                memory_type_str = metadata["memory_type"]
                try:
                    memory_type = MemoryType(memory_type_str)
                except (ValueError, TypeError):
                    memory_type = MemoryType.SEMANTIC
            
            # Detect emotional memories
            if emotion:
                memory_type = MemoryType.EMOTIONAL
                
            # Determine priority
            mem_priority = MemoryPriority.MEDIUM if priority is None else priority
            
            # Create memory fold
            fold = self.memory_folds.add_fold(
                key=key,
                content=content,
                memory_type=memory_type,
                priority=mem_priority,
                owner_id=owner_id
            )
            
            # Add tags if provided
            if tags:
                for tag in tags:
                    fold.add_tag(tag)
                    
            # Add emotion as tag if available
            if emotion:
                fold.add_tag(emotion)
                
            status["memory_fold"] = True
        
        # Also store in memory manager if available (for access control)
        if self.memory_manager:
            try:
                mem_type = "emotional" if emotion else "semantic"
                self.memory_manager.store(
                    key=key,
                    data=content,
                    metadata=metadata,
                    memory_type=mem_type,
                    priority=priority or MemoryPriority.MEDIUM if hasattr(MemoryPriority, "MEDIUM") else 2,
                    owner_id=owner_id,
                    tags=tags
                )
                status["memory_manager"] = True
            except Exception as e:
                logger.error(f"Failed to store in memory manager: {e}")
        
        # Create emotional memory fold
        if emotion and create_memory_fold:
            context_snippet = str(content)[:100] if isinstance(content, str) else key
            emotional_fold = create_memory_fold(emotion, context_snippet)
            status["emotional_fold"] = True
            
            # Update stats
            self.stats["emotional_memories"] += 1
        
        self.stats["total_memories"] += 1
        
        return {
            "success": any(status.values()),
            "key": key,
            "emotion": emotion,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve_with_emotional_context(self,
                                      key: str,
                                      target_emotion: str = None,
                                      user_identity = None,
                                      include_similar_emotions: bool = False) -> Dict[str, Any]:
        """
        Retrieve memory with emotional context
        
        Args:
            key: Memory key to retrieve
            target_emotion: Optional target emotion to filter/enhance retrieval
            user_identity: Optional user identity for access control
            include_similar_emotions: Whether to include memories with similar emotions
            
        Returns:
            Dict containing the memory with emotional context
        """
        memory = None
        emotional_context = {}
        
        # Try retrieving from memory fold system
        if self.memory_folds:
            fold = self.memory_folds.get_fold(key)
            if fold:
                memory = fold.retrieve()
                
                # Get fold tags for emotions
                emotions = [tag for tag in fold.tags if tag in self.emotion_vector.emotion_vectors]
                if emotions:
                    emotional_context["emotions"] = emotions
        
        # If not found or additional metadata needed, try memory manager
        if not memory and self.memory_manager:
            try:
                memory = self.memory_manager.retrieve(key, user_identity)
                if memory and "metadata" in memory and "emotion" in memory["metadata"]:
                    emotional_context["primary_emotion"] = memory["metadata"]["emotion"]
            except Exception as e:
                logger.error(f"Failed to retrieve from memory manager: {e}")
                
        # If still not found, return failure
        if not memory:
            return {"success": False, "error": "Memory not found"}
            
        # Add emotional context from metadata if present
        if isinstance(memory, dict):
            if "metadata" in memory and "emotion" in memory["metadata"]:
                emotional_context["primary_emotion"] = memory["metadata"]["emotion"]
                
            if "metadata" in memory and "emotion_vector" in memory["metadata"]:
                emotional_context["emotion_vector"] = memory["metadata"]["emotion_vector"]
        
        # If target emotion is provided, calculate emotional relevance
        if target_emotion and target_emotion in self.emotion_vector.emotion_vectors:
            # Get the memory's primary emotion
            memory_emotion = emotional_context.get("primary_emotion", "neutral")
            
            # Calculate distance
            emotional_distance = self.emotion_vector.calculate_distance(memory_emotion, target_emotion)
            emotional_context["target_emotion"] = target_emotion
            emotional_context["emotional_distance"] = emotional_distance
            emotional_context["emotional_relevance"] = 1.0 - (emotional_distance / 2.0)
            
            # Find similar emotions if requested
            if include_similar_emotions:
                similar_emotions = self.emotion_vector.closest_emotion(memory_emotion)
                emotional_context["similar_emotions"] = similar_emotions
        
        self.stats["emotional_recalls"] += 1
        
        # Return memory with emotional context
        return {
            "success": True,
            "memory": memory,
            "emotional_context": emotional_context,
            "timestamp": datetime.now().isoformat()
        }
    
    def find_emotionally_similar_memories(self, 
                                        target_emotion: str, 
                                        limit: int = 5, 
                                        min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find memories with similar emotional context
        
        Args:
            target_emotion: Target emotion to match
            limit: Maximum number of memories to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar memories with scores
        """
        similar_memories = []
        
        # Check if target emotion is valid
        if target_emotion not in self.emotion_vector.emotion_vectors:
            return []
            
        # Search in memory folds if available
        if self.memory_folds:
            # Get all memory folds
            all_keys = self.memory_folds.list_folds()
            
            for key in all_keys:
                fold = self.memory_folds.get_fold(key)
                if not fold:
                    continue
                    
                # Check if the memory has emotional tags
                emotions = [tag for tag in fold.tags if tag in self.emotion_vector.emotion_vectors]
                
                # Skip if no emotions found
                if not emotions:
                    continue
                    
                # Calculate similarity with primary emotion tag
                primary_emotion = emotions[0]
                distance = self.emotion_vector.calculate_distance(primary_emotion, target_emotion)
                similarity = 1.0 - (distance / 2.0)
                
                # Skip if below similarity threshold
                if similarity < min_similarity:
                    continue
                    
                # Add to results
                memory_content = fold.retrieve()
                similar_memories.append({
                    "key": key,
                    "similarity": similarity,
                    "memory_emotion": primary_emotion,
                    "memory": memory_content,
                    "importance": fold.importance_score
                })
                
            # Sort by similarity (highest first)
            similar_memories.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Limit results
            return similar_memories[:limit]
        
        # Fallback to emotional memory folds if sophisticated memory not available
        elif recall_memory_folds:
            similar_folds = recall_memory_folds(filter_emotion=target_emotion, user_tier=5)
            
            # Convert to similar format as above
            for fold in similar_folds[:limit]:
                similar_memories.append({
                    "key": fold.get("hash", ""),
                    "similarity": 1.0,  # Direct match since we filtered by emotion
                    "memory_emotion": fold.get("emotion", target_emotion),
                    "memory": fold.get("context", ""),
                    "importance": fold.get("relevance_score", 0.5)
                })
                
            return similar_memories
            
        return []

    def dream_consolidate_memories(self, 
                                hours_limit: int = 24, 
                                max_memories: int = 100) -> Dict[str, Any]:
        """
        Consolidate recent memories through the dream system
        
        Args:
            hours_limit: Consider memories from last X hours
            max_memories: Maximum memories to consolidate at once
            
        Returns:
            Dict with consolidation results
        """
        if not self.memory_folds or not self.context_reasoner:
            return {"success": False, "error": "Required memory components not available"}
        
        logger.info("Starting memory consolidation through dream system")
        
        # Get recent memories
        all_keys = self.memory_folds.list_folds()
        recent_memories = []
        
        for key in all_keys:
            fold = self.memory_folds.get_fold(key)
            if not fold:
                continue
                
            # Check if memory is recent enough
            time_diff = (datetime.now() - fold.created_at).total_seconds()
            if time_diff <= (hours_limit * 3600):  # Convert hours to seconds:
                recent_memories.append(key)
                
            # Break if we have enough memories
            if len(recent_memories) >= max_memories:
                break
        
        if not recent_memories:
            return {"success": False, "message": "No recent memories to consolidate"}
        
        # Extract context clusters
        clusters = self.context_reasoner.extract_context_clusters(min_cluster_size=3)
        
        # Process each cluster
        consolidated = []
        for cluster in clusters:
            central_key = cluster["central_key"]
            cluster_keys = cluster["keys"]
            common_tags = cluster["common_tags"]
            
            # Create a consolidated memory for the cluster
            consolidated_key = f"consolidated_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            
            # Check cluster for emotional content
            emotional_context = self.context_reasoner.analyze_emotional_context(cluster_keys)
            
            # Create consolidated summary (would be more sophisticated in production)
            summary = {
                "type": "memory_consolidation",
                "source_memories": cluster_keys,
                "central_memory": central_key,
                "common_topics": common_tags,
                "emotional_context": emotional_context,
                "consolidation_time": datetime.now().isoformat()
            }
            
            # Determine primary emotion if available
            primary_emotion = "neutral"
            if emotional_context["emotional_content"] == "present" and emotional_context["dominant_emotions"]:
                primary_emotion = emotional_context["dominant_emotions"][0]
            
            # Store the consolidated memory
            result = self.store_memory_with_emotion(
                key=consolidated_key,
                content=summary,
                emotion=primary_emotion,
                tags=common_tags + ["consolidated_memory", "dream_system"],
                priority=MemoryPriority.HIGH if hasattr(MemoryPriority, "HIGH") else 1
            )
            
            # Associate consolidated memory with source memories
            for source_key in cluster_keys:
                if self.memory_folds:
                    self.memory_folds.associate_folds(consolidated_key, source_key)
            
            consolidated.append({
                "key": consolidated_key,
                "source_count": len(cluster_keys),
                "common_tags": common_tags,
                "primary_emotion": primary_emotion
            })
        
        # Apply memory decay to reduce importance of old, rarely accessed memories
        if self.context_reasoner:
            self.context_reasoner.apply_memory_decay()
        
        # Update stats
        self.stats["consolidated_memories"] += len(consolidated)
        
        return {
            "success": True,
            "consolidated_count": len(consolidated),
            "consolidated_memories": consolidated,
            "timestamp": datetime.now().isoformat()
        }


class MemoryVoiceIntegrator:
    """
    Integrates memory system with voice capabilities, enabling
    voice modulation based on emotional memory context.
    """
    
    def __init__(self, 
                memory_emotional_integrator=None,
                emotional_oscillator=None,
                voice_integrator=None):
        """
        Initialize the Memory-Voice Integrator
        
        Args:
            memory_emotional_integrator: Memory emotional integrator
            emotional_oscillator: Emotional oscillator component
            voice_integrator: Voice integrator component
        """
        self.memory_emotional = memory_emotional_integrator or MemoryEmotionalIntegrator()
        self.emotional_oscillator = emotional_oscillator or EmotionalOscillator()
        self.voice_integrator = voice_integrator
        
    def speak_with_emotional_context(self, 
                                  text: str, 
                                  context_keys: List[str] = None,
                                  override_emotion: str = None) -> Dict[str, Any]:
        """
        Speak text with emotional context from memory
        
        Args:
            text: Text to speak
            context_keys: Optional memory keys to use for context
            override_emotion: Optional emotion to override the context
            
        Returns:
            Dict with voice generation result
        """
        # Start with current emotional state
        emotional_state = self.emotional_oscillator.get_current_state()
        emotion = emotional_state["primary_emotion"]
        
        # Override from parameter if provided
        if override_emotion and override_emotion in self.memory_emotional.emotion_vector.emotion_vectors:
            emotion = override_emotion
        
        # Otherwise, use context from memories if provided
        elif context_keys:
            # Map of emotions to their counts
            emotion_counts = {}
            
            for key in context_keys:
                # Get emotional context from memory
                memory_result = self.memory_emotional.retrieve_with_emotional_context(key)
                
                if memory_result["success"] and "emotional_context" in memory_result:
                    context = memory_result["emotional_context"]
                    
                    if "primary_emotion" in context:
                        memory_emotion = context["primary_emotion"]
                        emotion_counts[memory_emotion] = emotion_counts.get(memory_emotion, 0) + 1
            
            # If we found emotions in the memories, use the most common one
            if emotion_counts:
                # Sort by count (highest first)
                sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
                emotion = sorted_emotions[0][0]
        
        # Generate voice modulation parameters
        # First update the emotional oscillator
        self.emotional_oscillator.update_emotional_state(primary_emotion=emotion)
        
        # Then get voice modulation parameters
        voice_params = self.emotional_oscillator.get_voice_modulation_params()
        
        # Generate speech if voice integrator is available
        if self.voice_integrator:
            try:
                result = self.voice_integrator.synthesize_speech(text, voice_params)
                return {
                    "success": True,
                    "text": text,
                    "emotion": emotion,
                    "voice_params": voice_params,
                    "result": result
                }
            except Exception as e:
                logger.error(f"Voice synthesis failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "text": text,
                    "emotion": emotion,
                    "voice_params": voice_params
                }
        else:
            # Just return the parameters if voice integrator not available
            return {
                "success": False,
                "reason": "Voice integrator not available",
                "text": text,
                "emotion": emotion,
                "voice_params": voice_params
            }


class LucasBrainIntegration:
    """
    Central brain integration class that connects all LUCAS AGI components:
    - Memory systems with emotional context
    - Voice modulation
    - Dream engine for memory consolidation
    - Identity and compliance
    - Quantum attention for cognitive focusing
    """
    
    def __init__(self, core_integrator=None, config=None):
        """
        Initialize the LUKHAS Brain Integration system
        
        Args:
            core_integrator: Optional core integrator reference
            config: Optional configuration dict
        """
        self.core = core_integrator
        self.config = config or {}
        
        # Initialize core components
        logger.info("Initializing Lucas Brain Integration system")
        
        # Create emotional oscillator (affects voice modulation)
        self.emotional_oscillator = EmotionalOscillator()
        
        # Initialize memory systems
        self.memory_emotional = MemoryEmotionalIntegrator(
            emotional_oscillator=self.emotional_oscillator
        )
        
        # Initialize voice integration
        voice_integrator = None
        if VoiceIntegrator:
            try:
                voice_integrator = VoiceIntegrator(core_integrator)
            except Exception as e:
                logger.error(f"Could not initialize voice integrator: {e}")
        
        self.memory_voice = MemoryVoiceIntegrator(
            memory_emotional_integrator=self.memory_emotional,
            emotional_oscillator=self.emotional_oscillator,
            voice_integrator=voice_integrator
        )
        
        # Initialize quantum attention if available
        self.quantum_attention = QIAttention() if QIAttention else None
        
        # Initialize ID system integration
        try:
            self.lucas_id = LucasID()
        except Exception:
            self.lucas_id = None
            logger.warning("Could not initialize Lucas ID system. Identity integration will be limited.")
        
        # Initialize dream engine integration
        try:
            if DreamReflectionLoop:
                self.dream_engine = DreamReflectionLoop()
            else:
                self.dream_engine = None
        except Exception:
            self.dream_engine = None
            logger.warning("Could not initialize Dream Engine. Dream integration will be limited.")
        
        # Background consolidation thread
        self.consolidation_thread = None
        self.consolidation_running = False
        
        # Register with core integrator if available
        if self.core:
            try:
                self.core.register_component("brain", self)
                logger.info("Registered with core integrator")
            except Exception as e:
                logger.error(f"Failed to register with core integrator: {e}")
        
        logger.info("Lucas Brain Integration system initialized")
    
    def process_message(self, message_envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming messages from the core integrator
        
        Args:
            message_envelope: Message envelope from core integrator
            
        Returns:
            Dict with response
        """
        content = message_envelope.get("content", {})
        metadata = message_envelope.get("metadata", {})
        
        # Extract message information
        message_type = metadata.get("message_type", "command")
        source = metadata.get("source")
        action = content.get("action")
        
        # Process based on action type
        if action == "store_memory":
            # Store memory with emotional context
            result = self.memory_emotional.store_memory_with_emotion(
                key=content.get("key", f"memory_{int(time.time())}"),
                content=content.get("content"),
                emotion=content.get("emotion"),
                tags=content.get("tags"),
                owner_id=content.get("owner_id"),
                priority=content.get("priority"),
                additional_metadata=content.get("metadata")
            )
            return {"status": "success", "result": result}
            
        elif action == "retrieve_memory":
            # Retrieve memory with emotional context
            result = self.memory_emotional.retrieve_with_emotional_context(
                key=content.get("key"),
                target_emotion=content.get("target_emotion"),
                user_identity=content.get("user_identity"),
                include_similar_emotions=content.get("include_similar", False)
            )
            return {"status": "success", "result": result}
            
        elif action == "find_similar_memories":
            # Find emotionally similar memories
            result = self.memory_emotional.find_emotionally_similar_memories(
                target_emotion=content.get("emotion"),
                limit=content.get("limit", 5),
                min_similarity=content.get("min_similarity", 0.7)
            )
            return {"status": "success", "result": result}
            
        elif action == "update_emotion":
            # Update emotional state
            result = self.emotional_oscillator.update_emotional_state(
                primary_emotion=content.get("emotion"),
                intensity=content.get("intensity"),
                secondary_emotions=content.get("secondary_emotions"),
                metadata=content.get("metadata")
            )
            return {"status": "success", "result": result}
            
        elif action == "speak":
            # Speak with emotional context
            result = self.memory_voice.speak_with_emotional_context(
                text=content.get("text"),
                context_keys=content.get("context_keys"),
                override_emotion=content.get("emotion")
            )
            return {"status": "success", "result": result}
            
        elif action == "consolidate_memories":
            # Trigger memory consolidation
            result = self.memory_emotional.dream_consolidate_memories(
                hours_limit=content.get("hours_limit", 24),
                max_memories=content.get("max_memories", 100)
            )
            return {"status": "success", "result": result}
            
        elif action == "start_consolidation_thread":
            # Start background consolidation thread
            self.start_consolidation_thread(
                interval_minutes=content.get("interval_minutes", 60)
            )
            return {"status": "success", "message": "Consolidation thread started"}
            
        elif action == "stop_consolidation_thread":
            # Stop background consolidation thread
            self.stop_consolidation_thread()
            return {"status": "success", "message": "Consolidation thread stopped"}
            
        elif action == "get_stats":
            # Get system statistics
            stats = {
                "memory": self.memory_emotional.stats,
                "current_emotion": self.emotional_oscillator.get_current_state(),
                "consolidation_running": self.consolidation_running
            }
            return {"status": "success", "stats": stats}
            
        else:
            # Unknown action
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "timestamp": datetime.now().isoformat()
            }
    
    def start_consolidation_thread(self, interval_minutes: int = 60) -> bool:
        """
        Start a background thread for periodic memory consolidation
        
        Args:
            interval_minutes: Minutes between consolidation runs
            
        Returns:
            bool: Success status
        """
        if self.consolidation_running:
            logger.warning("Consolidation thread already running")
            return False
            
        self.consolidation_running = True
        
        def consolidation_loop():
            logger.info(f"Starting memory consolidation loop (interval: {interval_minutes} minutes)")
            while self.consolidation_running:
                try:
                    # Run consolidation
                    self.memory_emotional.dream_consolidate_memories()
                    logger.info("Memory consolidation complete")
                except Exception as e:
                    logger.error(f"Error in consolidation thread: {e}")
                    
                # Sleep for the interval
                for _ in range(interval_minutes * 60):
                    if not self.consolidation_running:
                        break
                    time.sleep(1)
        
        # Start thread
        self.consolidation_thread = threading.Thread(
            target=consolidation_loop,
            name="ConsolidationThread",
            daemon=True
        )
        self.consolidation_thread.start()
        
        logger.info("Memory consolidation thread started")
        return True
    
    def stop_consolidation_thread(self) -> bool:
        """
        Stop the background consolidation thread
        
        Returns:
            bool: Success status
        """
        if not self.consolidation_running:
            logger.warning("No consolidation thread is running")
            return False
            
        self.consolidation_running = False
        
        # Wait for thread to finish (with timeout)
        if self.consolidation_thread and self.consolidation_thread.is_alive():
            self.consolidation_thread.join(timeout=5.0)
            
        logger.info("Memory consolidation thread stopped")
        return True
        
    def store_memory(self, **kwargs) -> Dict[str, Any]:
        """Convenience method to store memory directly"""
        return self.memory_emotional.store_memory_with_emotion(**kwargs)
        
    def retrieve_memory(self, **kwargs) -> Dict[str, Any]:
        """Convenience method to retrieve memory directly"""
        return self.memory_emotional.retrieve_with_emotional_context(**kwargs)
        
    def speak(self, **kwargs) -> Dict[str, Any]:
        """Convenience method to speak with emotional context directly"""
        return self.memory_voice.speak_with_emotional_context(**kwargs)


# Example usage
if __name__ == "__main__":
    # Create brain integration
    brain = LucasBrainIntegration()
    
    # Store a memory with emotional context
    result = brain.store_memory(
        key="test_memory",
        content="This is a test memory with emotional context",
        emotion="joy",
        tags=["test", "demo"],
    )
    print(f"Memory stored: {result}")
    
    # Retrieve the memory
    memory = brain.retrieve_memory(key="test_memory")
    print(f"Memory retrieved: {memory}")
    
    # Speak with emotional context
    speech = brain.speak(
        text="Hello, this is a test of emotional speech",
        context_keys=["test_memory"]
    )
    print(f"Speech generated: {speech}")