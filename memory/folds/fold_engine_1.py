"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: fold_engine.py
Advanced: fold_engine.py
Integration Date: 2025-05-31T07:55:28.106997
"""

"""
Memory Folds for v1_AGI

This module implements the concept of memory folding for the AGI system.
Memory folds are a way to organize and prioritize memories, inspired by
how the human brain processes and stores information in different ways.

Each memory fold can be thought of as a specialized container for different
types of memories (episodic, semantic, procedural, etc.) or different contexts.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger("v1_AGI.memory.folds")

class MemoryType(Enum):
    """Types of memories that can be stored in memory folds"""
    EPISODIC = "episodic"       # Event-based memories (experiences)
    SEMANTIC = "semantic"       # Factual knowledge
    PROCEDURAL = "procedural"   # Skills and procedures
    EMOTIONAL = "emotional"     # Emotion-linked memories
    ASSOCIATIVE = "associative" # Connected/linked memories
    SYSTEM = "system"           # System-related memories
    IDENTITY = "identity"       # User identity information
    CONTEXT = "context"         # Contextual information
    

class MemoryPriority(Enum):
    """Priority levels for memories"""
    CRITICAL = 0    # Highest priority, always preserved
    HIGH = 1        # High importance memories
    MEDIUM = 2      # Standard importance
    LOW = 3         # Lower priority, may be compressed or archived
    ARCHIVAL = 4    # Lowest priority, candidates for archiving
    

class MemoryFold:
    """
    A fold representing a specific memory unit.
    
    Memory folds encapsulate individual memories with metadata
    and provide methods for retrieval, updating, and management.
    """
    
    def __init__(self, key: str, content: Any, 
                memory_type: MemoryType = MemoryType.SEMANTIC,
                priority: MemoryPriority = MemoryPriority.MEDIUM,
                owner_id: Optional[str] = None):
        """
        Initialize a memory fold.
        
        Args:
            key: Unique identifier for this memory
            content: The memory content
            memory_type: Type of memory
            priority: Priority level of the memory
            owner_id: ID of the memory owner (user or system)
        """
        self.key = key
        self.content = content
        self.memory_type = memory_type
        self.priority = priority
        self.owner_id = owner_id
        self.created_at = datetime.now()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.importance_score = self._calculate_initial_importance()
        self.associated_keys = set()  # Related memory keys
        self.tags = set()  # Tags for categorical search
        
    def retrieve(self) -> Any:
        """
        Retrieve the memory content.
        
        Returns:
            The memory content
        """
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.content
    
    def update(self, new_content: Any) -> bool:
        """
        Update the memory content.
        
        Args:
            new_content: New content to store
            
        Returns:
            bool: Success status
        """
        old_content = self.content
        self.content = new_content
        self.last_accessed = datetime.now()
        
        # Recalculate importance after update
        self.importance_score = self._calculate_importance()
        return True
    
    def add_association(self, related_key: str) -> bool:
        """
        Add an association to another memory.
        
        Args:
            related_key: Key of the related memory
            
        Returns:
            bool: Success status
        """
        if related_key == self.key:
            return False  # Can't associate with self
        
        self.associated_keys.add(related_key)
        return True
    
    def add_tag(self, tag: str) -> bool:
        """
        Add a tag to the memory.
        
        Args:
            tag: Tag to add
            
        Returns:
            bool: Success status
        """
        if not tag or len(tag.strip()) == 0:
            return False
        
        self.tags.add(tag.lower().strip())
        return True
    
    def matches_tag(self, tag: str) -> bool:
        """
        Check if memory has a specific tag.
        
        Args:
            tag: Tag to check for
            
        Returns:
            bool: True if memory has the tag
        """
        return tag.lower().strip() in self.tags
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert memory fold to a dictionary.
        
        Returns:
            Dict: Dictionary representation
        """
        return {
            "key": self.key,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "priority": self.priority.value,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
            "associated_keys": list(self.associated_keys),
            "tags": list(self.tags)
        }
    
    def _calculate_initial_importance(self) -> float:
        """
        Calculate initial importance score.
        
        Returns:
            float: Importance score (0.0-1.0)
        """
        # Base importance from priority
        priority_map = {
            MemoryPriority.CRITICAL: 0.95,
            MemoryPriority.HIGH: 0.8,
            MemoryPriority.MEDIUM: 0.5,
            MemoryPriority.LOW: 0.3,
            MemoryPriority.ARCHIVAL: 0.1
        }
        
        base_score = priority_map.get(self.priority, 0.5)
        
        # Adjust based on memory type
        type_adjustments = {
            MemoryType.EPISODIC: 0.0,
            MemoryType.SEMANTIC: 0.05,
            MemoryType.PROCEDURAL: 0.1,
            MemoryType.EMOTIONAL: 0.15,
            MemoryType.ASSOCIATIVE: 0.0,
            MemoryType.SYSTEM: 0.2,
            MemoryType.IDENTITY: 0.25,
            MemoryType.CONTEXT: -0.05
        }
        
        adjustment = type_adjustments.get(self.memory_type, 0.0)
        
        # Calculate final score with caps
        return max(0.05, min(0.99, base_score + adjustment))
    
    def _calculate_importance(self) -> float:
        """
        Calculate current importance score based on usage patterns.
        
        Returns:
            float: Importance score (0.0-1.0)
        """
        base_score = self._calculate_initial_importance()
        
        # Adjust for recency (higher for recently accessed memories)
        time_since_access = (datetime.now() - self.last_accessed).total_seconds()
        recency_factor = max(0.0, 1.0 - (time_since_access / (3600 * 24 * 7)))  # 7-day decay
        
        # Adjust for access frequency (higher for frequently accessed)
        frequency_factor = min(0.5, self.access_count / 20)  # Caps at 20 accesses
        
        # Adjust for associations (more associations = more important)
        association_factor = min(0.15, len(self.associated_keys) * 0.03)
        
        # Calculate final score with caps
        final_score = base_score + (recency_factor * 0.2) + (frequency_factor * 0.2) + association_factor
        return max(0.05, min(0.99, final_score))


class SymbolicPatternEngine:
    """
    Enhanced pattern recognition engine integrated from OXN symbolic_ai.
    Provides deeper pattern analysis and formal reasoning capabilities.
    """
    
    def __init__(self):
        self.pattern_registry = {}
        self.confidence_threshold = 0.75
        self.temporal_patterns = []
        self.semantic_patterns = []
        
    def register_pattern(self, pattern_id: str, pattern_template: Dict[str, Any], 
                        weight: float = 1.0, pattern_type: str = "semantic"):
        """Register a new symbolic pattern template"""
        self.pattern_registry[pattern_id] = {
            "template": pattern_template,
            "weight": weight,
            "type": pattern_type,
            "matches": []
        }
        
    def analyze_memory_fold(self, fold: MemoryFold) -> Dict[str, Any]:
        """Analyze a memory fold for symbolic patterns"""
        patterns = []
        content = fold.retrieve()
        
        # Apply registered patterns
        for pattern_id, pattern_info in self.pattern_registry.items():
            match_score = self._calculate_pattern_match(content, pattern_info["template"])
            if match_score >= self.confidence_threshold:
                patterns.append({
                    "pattern_id": pattern_id,
                    "confidence": match_score,
                    "type": pattern_info["type"]
                })
        
        # Look for temporal sequences
        if fold.memory_type == MemoryType.EPISODIC:
            temporal_patterns = self._analyze_temporal_patterns(fold)
            patterns.extend(temporal_patterns)
            
        return {
            "fold_key": fold.key,
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
        
    def _calculate_pattern_match(self, content: Any, template: Dict[str, Any]) -> float:
        """Calculate pattern match confidence score"""
        # Implementation would depend on pattern structure
        # This is a simplified version
        match_score = 0.0
        
        if isinstance(content, dict) and isinstance(template, dict):
            # Check for matching keys and values
            matching_keys = set(content.keys()) & set(template.keys())
            if matching_keys:
                scores = []
                for key in matching_keys:
                    if isinstance(content[key], (str, int, float, bool)):
                        if content[key] == template[key]:
                            scores.append(1.0)
                        else:
                            scores.append(0.0)
                    elif isinstance(content[key], dict):
                        subscore = self._calculate_pattern_match(content[key], template[key])
                        scores.append(subscore)
                        
                if scores:
                    match_score = sum(scores) / len(scores)
                    
        return match_score
        
    def _analyze_temporal_patterns(self, fold: MemoryFold) -> List[Dict[str, Any]]:
        """Analyze temporal patterns in episodic memories"""
        patterns = []
        
        # Add to temporal pattern sequence
        self.temporal_patterns.append({
            "key": fold.key,
            "timestamp": fold.created_at,
            "type": "temporal_sequence"
        })
        
        # Keep only recent patterns for analysis
        recent_cutoff = datetime.now() - timedelta(days=7)
        self.temporal_patterns = [
            p for p in self.temporal_patterns 
            if p["timestamp"] > recent_cutoff
        ]
        
        # Look for sequences
        if len(self.temporal_patterns) >= 3:
            patterns.append({
                "type": "temporal_sequence",
                "sequence_length": len(self.temporal_patterns),
                "confidence": 0.8
            })
            
        return patterns


class AGIMemory:
    """
    Main memory management system for AGI using the concept of memory folds.
    
    This system organizes memories into folds, manages priorities, and
    handles retrieval, updating, and associative linking of memories.
    """
    
    def __init__(self):
        """Initialize the AGI memory system."""
        self.folds = {}  # key -> MemoryFold
        self.type_indices = {t: set() for t in MemoryType}  # Type -> set of keys
        self.priority_indices = {p: set() for p in MemoryPriority}  # Priority -> set of keys
        self.owner_index = {}  # owner_id -> set of keys
        self.tag_index = {}  # tag -> set of keys
        self.association_index = {}  # key -> set of associated keys (bidirectional)
        self.pattern_engine = SymbolicPatternEngine()
        
    def add_fold(self, key: str, content: Any, 
                memory_type: Union[MemoryType, str] = MemoryType.SEMANTIC,
                priority: Union[MemoryPriority, int] = MemoryPriority.MEDIUM,
                owner_id: Optional[str] = None) -> MemoryFold:
        """
        Add a new memory fold with symbolic pattern analysis.
        
        Args:
            key: Unique identifier for this memory
            content: The memory content
            memory_type: Type of memory (enum or string)
            priority: Priority level (enum or int)
            owner_id: ID of the memory owner
            
        Returns:
            MemoryFold: The created memory fold
        """
        # Convert string type to enum if needed
        if isinstance(memory_type, str):
            try:
                memory_type = MemoryType(memory_type)
            except ValueError:
                memory_type = MemoryType.SEMANTIC
                
        # Convert int priority to enum if needed
        if isinstance(priority, int):
            try:
                priority = MemoryPriority(priority)
            except ValueError:
                priority = MemoryPriority.MEDIUM
        
        # Create new memory fold
        fold = MemoryFold(key, content, memory_type, priority, owner_id)
        
        # Update fold if it already exists
        if key in self.folds:
            self._remove_from_indices(key)
            logger.debug(f"Updating existing memory fold: {key}")
        
        # Store the fold
        self.folds[key] = fold
        
        # Update indices
        self._add_to_indices(fold)
        
        # Analyze patterns in new memory
        patterns = self.pattern_engine.analyze_memory_fold(fold)
        
        # Register any strong patterns found
        for pattern in patterns["patterns"]:
            if pattern["confidence"] > 0.9:
                self.pattern_engine.register_pattern(
                    f"learned_pattern_{uuid.uuid4().hex[:8]}",
                    {"content": content},
                    weight=pattern["confidence"]
                )
        
        return fold
    
    def get_fold(self, key: str) -> Optional[MemoryFold]:
        """
        Get a memory fold by key.
        
        Args:
            key: Fold key to retrieve
            
        Returns:
            Optional[MemoryFold]: The memory fold, or None if not found
        """
        return self.folds.get(key)
    
    def list_folds(self) -> List[str]:
        """
        List all memory fold keys.
        
        Returns:
            List[str]: List of all memory fold keys
        """
        return list(self.folds.keys())
    
    def remove_fold(self, key: str) -> bool:
        """
        Remove a memory fold.
        
        Args:
            key: Key of the fold to remove
            
        Returns:
            bool: Success status
        """
        if key not in self.folds:
            return False
        
        # Remove from indices first
        self._remove_from_indices(key)
        
        # Remove the fold
        del self.folds[key]
        return True
    
    def associate_folds(self, key1: str, key2: str) -> bool:
        """
        Create a bidirectional association between two memory folds.
        
        Args:
            key1: Key of the first fold
            key2: Key of the second fold
            
        Returns:
            bool: Success status
        """
        # Ensure both folds exist
        if key1 not in self.folds or key2 not in self.folds:
            return False
        
        # Update fold associations
        fold1 = self.folds[key1]
        fold2 = self.folds[key2]
        
        fold1.add_association(key2)
        fold2.add_association(key1)
        
        # Update association index
        if key1 not in self.association_index:
            self.association_index[key1] = set()
        if key2 not in self.association_index:
            self.association_index[key2] = set()
            
        self.association_index[key1].add(key2)
        self.association_index[key2].add(key1)
        
        return True
    
    def get_associated_folds(self, key: str) -> List[str]:
        """
        Get all associated memory fold keys.
        
        Args:
            key: Key to get associations for
            
        Returns:
            List[str]: List of associated fold keys
        """
        if key not in self.association_index:
            return []
            
        return list(self.association_index[key])
    
    def tag_fold(self, key: str, tag: str) -> bool:
        """
        Add a tag to a memory fold.
        
        Args:
            key: Key of the fold to tag
            tag: Tag to add
            
        Returns:
            bool: Success status
        """
        if key not in self.folds:
            return False
            
        fold = self.folds[key]
        success = fold.add_tag(tag)
        
        if success:
            # Update tag index
            tag = tag.lower().strip()
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(key)
            
        return success
    
    def get_folds_by_tag(self, tag: str) -> List[str]:
        """
        Get all fold keys with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List[str]: List of fold keys with this tag
        """
        tag = tag.lower().strip()
        if tag not in self.tag_index:
            return []
            
        return list(self.tag_index[tag])
    
    def get_folds_by_type(self, memory_type: Union[MemoryType, str]) -> List[str]:
        """
        Get all fold keys of a specific memory type.
        
        Args:
            memory_type: Type of memory to filter by
            
        Returns:
            List[str]: List of fold keys with this type
        """
        # Convert string type to enum if needed
        if isinstance(memory_type, str):
            try:
                memory_type = MemoryType(memory_type)
            except ValueError:
                return []
                
        if memory_type not in self.type_indices:
            return []
            
        return list(self.type_indices[memory_type])
    
    def get_folds_by_priority(self, priority: Union[MemoryPriority, int]) -> List[str]:
        """
        Get all fold keys with a specific priority.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List[str]: List of fold keys with this priority
        """
        # Convert int priority to enum if needed
        if isinstance(priority, int):
            try:
                priority = MemoryPriority(priority)
            except ValueError:
                return []
                
        if priority not in self.priority_indices:
            return []
            
        return list(self.priority_indices[priority])
    
    def get_folds_by_owner(self, owner_id: str) -> List[str]:
        """
        Get all fold keys belonging to a specific owner.
        
        Args:
            owner_id: Owner ID to filter by
            
        Returns:
            List[str]: List of fold keys belonging to this owner
        """
        if owner_id not in self.owner_index:
            return []
            
        return list(self.owner_index[owner_id])
    
    def update_fold_content(self, key: str, new_content: Any) -> bool:
        """
        Update the content of a memory fold.
        
        Args:
            key: Key of the fold to update
            new_content: New content to store
            
        Returns:
            bool: Success status
        """
        if key not in self.folds:
            return False
            
        fold = self.folds[key]
        return fold.update(new_content)
    
    def update_fold_priority(self, key: str, 
                           new_priority: Union[MemoryPriority, int]) -> bool:
        """
        Update the priority of a memory fold.
        
        Args:
            key: Key of the fold to update
            new_priority: New priority level
            
        Returns:
            bool: Success status
        """
        if key not in self.folds:
            return False
            
        # Convert int priority to enum if needed
        if isinstance(new_priority, int):
            try:
                new_priority = MemoryPriority(new_priority)
            except ValueError:
                return False
                
        # Get fold and update indices
        fold = self.folds[key]
        old_priority = fold.priority
        
        # Remove from old priority index
        if old_priority in self.priority_indices and key in self.priority_indices[old_priority]:
            self.priority_indices[old_priority].remove(key)
            
        # Update fold and add to new priority index
        fold.priority = new_priority
        if new_priority not in self.priority_indices:
            self.priority_indices[new_priority] = set()
        self.priority_indices[new_priority].add(key)
        
        # Recalculate importance
        fold.importance_score = fold._calculate_importance()
        
        return True
    
    def get_important_folds(self, count: int = 10) -> List[str]:
        """
        Get the most important memory folds.
        
        Args:
            count: Number of important folds to return
            
        Returns:
            List[str]: List of important fold keys
        """
        # Sort folds by importance score
        sorted_folds = sorted(
            self.folds.values(), 
            key=lambda f: f.importance_score,
            reverse=True
        )
        
        # Return top N keys
        return [f.key for f in sorted_folds[:count]]
    
    def recalculate_importance(self) -> None:
        """Recalculate importance scores for all memory folds."""
        for fold in self.folds.values():
            fold.importance_score = fold._calculate_importance()
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert all memory folds to a dictionary.
        
        Returns:
            Dict: Dictionary mapping keys to fold data
        """
        return {key: fold.to_dict() for key, fold in self.folds.items()}
    
    def _add_to_indices(self, fold: MemoryFold) -> None:
        """
        Add a fold to all relevant indices.
        
        Args:
            fold: Memory fold to index
        """
        key = fold.key
        
        # Add to type index
        if fold.memory_type not in self.type_indices:
            self.type_indices[fold.memory_type] = set()
        self.type_indices[fold.memory_type].add(key)
        
        # Add to priority index
        if fold.priority not in self.priority_indices:
            self.priority_indices[fold.priority] = set()
        self.priority_indices[fold.priority].add(key)
        
        # Add to owner index if owner exists
        if fold.owner_id:
            if fold.owner_id not in self.owner_index:
                self.owner_index[fold.owner_id] = set()
            self.owner_index[fold.owner_id].add(key)
            
        # Add to tag index for each tag
        for tag in fold.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(key)
            
        # Add to association index for each association
        if fold.associated_keys:
            if key not in self.association_index:
                self.association_index[key] = set()
            self.association_index[key].update(fold.associated_keys)
            
            # Add bidirectional associations
            for associated_key in fold.associated_keys:
                if associated_key not in self.association_index:
                    self.association_index[associated_key] = set()
                self.association_index[associated_key].add(key)
    
    def _remove_from_indices(self, key: str) -> None:
        """
        Remove a fold from all indices.
        
        Args:
            key: Key of the fold to remove
        """
        if key not in self.folds:
            return
            
        fold = self.folds[key]
        
        # Remove from type index
        if fold.memory_type in self.type_indices and key in self.type_indices[fold.memory_type]:
            self.type_indices[fold.memory_type].remove(key)
            
        # Remove from priority index
        if fold.priority in self.priority_indices and key in self.priority_indices[fold.priority]:
            self.priority_indices[fold.priority].remove(key)
            
        # Remove from owner index
        if fold.owner_id and fold.owner_id in self.owner_index and key in self.owner_index[fold.owner_id]:
            self.owner_index[fold.owner_id].remove(key)
            
        # Remove from tag index
        for tag in fold.tags:
            if tag in self.tag_index and key in self.tag_index[tag]:
                self.tag_index[tag].remove(key)
                
        # Remove from association index and update bidirectional associations
        if key in self.association_index:
            associated_keys = self.association_index[key].copy()
            
            # Remove bidirectional associations
            for associated_key in associated_keys:
                if associated_key in self.association_index and key in self.association_index[associated_key]:
                    self.association_index[associated_key].remove(key)
                    
            # Remove the main entry
            del self.association_index[key]