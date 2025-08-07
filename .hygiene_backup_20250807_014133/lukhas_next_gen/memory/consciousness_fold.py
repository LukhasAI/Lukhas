#!/usr/bin/env python3
"""
Consciousness Fold - Memory system linked to consciousness states and trust glyphs
Creates temporal folds that preserve context across state transitions
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import deque
import sqlite3

logger = logging.getLogger(__name__)


@dataclass
class MemoryFold:
    """Single memory fold containing consciousness-linked data"""
    fold_id: str
    timestamp: datetime
    consciousness_state: str
    trust_glyphs: List[str]
    entropy_score: float
    drift_class: str
    content: Dict[str, Any]
    emotional_valence: float  # -1 to 1
    symbolic_hash: str
    parent_fold: Optional[str] = None
    child_folds: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.child_folds is None:
            self.child_folds = []
        if self.tags is None:
            self.tags = []
    
    def compute_hash(self) -> str:
        """Compute symbolic hash of fold contents"""
        content_str = f"{self.consciousness_state}|{''.join(self.trust_glyphs)}|{self.entropy_score}"
        return hashlib.sha3_256(content_str.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "fold_id": self.fold_id,
            "timestamp": self.timestamp.isoformat(),
            "consciousness_state": self.consciousness_state,
            "trust_glyphs": self.trust_glyphs,
            "entropy_score": self.entropy_score,
            "drift_class": self.drift_class,
            "content": self.content,
            "emotional_valence": self.emotional_valence,
            "symbolic_hash": self.symbolic_hash,
            "parent_fold": self.parent_fold,
            "child_folds": self.child_folds,
            "tags": self.tags
        }


class ConsciousnessMemory:
    """
    Memory system that creates folds based on consciousness states
    Links memories through trust glyph history and entropy patterns
    """
    
    # Consciousness-memory associations
    STATE_MEMORY_TRAITS = {
        "focused": {"retention": 0.9, "clarity": 0.95, "emotion": 0.0},
        "creative": {"retention": 0.8, "clarity": 0.7, "emotion": 0.3},
        "analytical": {"retention": 0.95, "clarity": 0.9, "emotion": -0.1},
        "meditative": {"retention": 0.7, "clarity": 0.6, "emotion": 0.2},
        "dreaming": {"retention": 0.5, "clarity": 0.3, "emotion": 0.5},
        "flow_state": {"retention": 0.85, "clarity": 0.8, "emotion": 0.4},
        "lucid": {"retention": 0.9, "clarity": 0.85, "emotion": 0.3},
        "turbulent": {"retention": 0.6, "clarity": 0.4, "emotion": -0.5}
    }
    
    def __init__(self, db_path: str = "consciousness_memory.db",
                 max_active_folds: int = 1000,
                 consciousness_state_file: str = "lukhas_next_gen/stream/consciousness_state.json"):
        self.db_path = db_path
        self.max_active_folds = max_active_folds
        self.consciousness_state_file = Path(consciousness_state_file)
        self.active_folds = deque(maxlen=max_active_folds)
        self.current_state = "focused"
        self.fold_index: Dict[str, MemoryFold] = {}
        
        # Initialize database
        self._init_database()
        
        # Load current consciousness state
        self._load_consciousness_state()
        
        logger.info(f"🧠 Consciousness Memory initialized")
        logger.info(f"   Database: {self.db_path}")
        logger.info(f"   Current state: {self.current_state}")
    
    def _init_database(self):
        """Initialize SQLite database for persistent memory storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_folds (
                    fold_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    consciousness_state TEXT NOT NULL,
                    trust_glyphs TEXT NOT NULL,
                    entropy_score REAL NOT NULL,
                    drift_class TEXT NOT NULL,
                    content TEXT NOT NULL,
                    emotional_valence REAL NOT NULL,
                    symbolic_hash TEXT NOT NULL,
                    parent_fold TEXT,
                    child_folds TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_consciousness ON memory_folds(consciousness_state)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_entropy ON memory_folds(entropy_score)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_folds(timestamp)
            """)
    
    def _load_consciousness_state(self):
        """Load current consciousness state from file"""
        if self.consciousness_state_file.exists():
            try:
                with open(self.consciousness_state_file, 'r') as f:
                    data = json.load(f)
                self.current_state = data.get("current_state", "focused")
            except Exception as e:
                logger.warning(f"Could not load consciousness state: {e}")
    
    def create_fold(self, content: Dict[str, Any], 
                   trust_glyphs: List[str],
                   entropy_score: float,
                   drift_class: str,
                   tags: Optional[List[str]] = None,
                   parent_fold_id: Optional[str] = None) -> MemoryFold:
        """Create a new memory fold linked to current consciousness state"""
        
        # Get memory traits for current state
        traits = self.STATE_MEMORY_TRAITS.get(self.current_state, {
            "retention": 0.5, "clarity": 0.5, "emotion": 0.0
        })
        
        # Generate fold ID
        fold_id = f"fold_{datetime.utcnow().timestamp()}_{self.current_state[:3]}"
        
        # Create fold
        fold = MemoryFold(
            fold_id=fold_id,
            timestamp=datetime.utcnow(),
            consciousness_state=self.current_state,
            trust_glyphs=trust_glyphs,
            entropy_score=entropy_score,
            drift_class=drift_class,
            content=content,
            emotional_valence=traits["emotion"],
            symbolic_hash="",  # Will be computed
            parent_fold=parent_fold_id,
            tags=tags
        )
        
        # Compute hash
        fold.symbolic_hash = fold.compute_hash()
        
        # Link to parent if specified
        if parent_fold_id and parent_fold_id in self.fold_index:
            parent = self.fold_index[parent_fold_id]
            parent.child_folds.append(fold_id)
        
        # Apply retention probability
        if traits["retention"] < 1.0:
            # Simulate memory retention based on consciousness state
            import random
            if random.random() > traits["retention"]:
                # Memory not retained strongly - reduce clarity
                fold.content["clarity_factor"] = traits["clarity"] * 0.5
            else:
                fold.content["clarity_factor"] = traits["clarity"]
        
        # Store fold
        self._save_fold(fold)
        self.fold_index[fold_id] = fold
        self.active_folds.append(fold)
        
        logger.info(f"📁 Created fold: {fold_id} in state {self.current_state}")
        logger.info(f"   Glyphs: {' '.join(trust_glyphs)}")
        logger.info(f"   Entropy: {entropy_score:.3f} ({drift_class})")
        
        return fold
    
    def _save_fold(self, fold: MemoryFold):
        """Save fold to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memory_folds 
                (fold_id, timestamp, consciousness_state, trust_glyphs, 
                 entropy_score, drift_class, content, emotional_valence,
                 symbolic_hash, parent_fold, child_folds, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fold.fold_id,
                fold.timestamp.isoformat(),
                fold.consciousness_state,
                json.dumps(fold.trust_glyphs),
                fold.entropy_score,
                fold.drift_class,
                json.dumps(fold.content),
                fold.emotional_valence,
                fold.symbolic_hash,
                fold.parent_fold,
                json.dumps(fold.child_folds),
                json.dumps(fold.tags)
            ))
    
    def recall_by_similarity(self, target_entropy: float, 
                           threshold: float = 0.1) -> List[MemoryFold]:
        """Recall memories with similar entropy levels"""
        similar_folds = []
        
        for fold in self.active_folds:
            if abs(fold.entropy_score - target_entropy) <= threshold:
                similar_folds.append(fold)
        
        # Sort by similarity
        similar_folds.sort(key=lambda f: abs(f.entropy_score - target_entropy))
        
        return similar_folds[:10]  # Return top 10
    
    def recall_by_glyphs(self, glyph_pattern: List[str]) -> List[MemoryFold]:
        """Recall memories containing specific glyph patterns"""
        matching_folds = []
        
        for fold in self.active_folds:
            # Check if pattern exists in fold's glyphs
            if all(g in fold.trust_glyphs for g in glyph_pattern):
                matching_folds.append(fold)
        
        # Sort by recency
        matching_folds.sort(key=lambda f: f.timestamp, reverse=True)
        
        return matching_folds[:10]
    
    def recall_by_state(self, consciousness_state: str) -> List[MemoryFold]:
        """Recall memories from specific consciousness state"""
        state_folds = [f for f in self.active_folds 
                      if f.consciousness_state == consciousness_state]
        
        # Sort by emotional valence (most positive first)
        state_folds.sort(key=lambda f: f.emotional_valence, reverse=True)
        
        return state_folds[:10]
    
    def get_temporal_chain(self, fold_id: str, depth: int = 5) -> List[MemoryFold]:
        """Get temporal chain of memories from a starting fold"""
        if fold_id not in self.fold_index:
            return []
        
        chain = []
        current_fold = self.fold_index[fold_id]
        
        # Walk up parent chain
        for _ in range(depth):
            chain.append(current_fold)
            if current_fold.parent_fold and current_fold.parent_fold in self.fold_index:
                current_fold = self.fold_index[current_fold.parent_fold]
            else:
                break
        
        return list(reversed(chain))
    
    def calculate_memory_coherence(self) -> float:
        """Calculate overall memory coherence based on fold connections"""
        if not self.active_folds:
            return 1.0
        
        # Count connected vs isolated folds
        connected = sum(1 for f in self.active_folds 
                       if f.parent_fold or f.child_folds)
        
        return connected / len(self.active_folds)
    
    def prune_unstable_memories(self, entropy_threshold: float = 0.8):
        """Prune memories with high entropy (unstable)"""
        stable_folds = deque()
        pruned_count = 0
        
        for fold in self.active_folds:
            if fold.entropy_score < entropy_threshold:
                stable_folds.append(fold)
            else:
                # Mark as pruned in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "UPDATE memory_folds SET tags = ? WHERE fold_id = ?",
                        (json.dumps(fold.tags + ["pruned"]), fold.fold_id)
                    )
                pruned_count += 1
        
        self.active_folds = stable_folds
        logger.info(f"🧹 Pruned {pruned_count} unstable memories")
    
    def generate_memory_report(self) -> Dict:
        """Generate comprehensive memory system report"""
        # State distribution
        state_dist = {}
        entropy_sum = 0.0
        
        for fold in self.active_folds:
            state = fold.consciousness_state
            state_dist[state] = state_dist.get(state, 0) + 1
            entropy_sum += fold.entropy_score
        
        # Glyph frequency
        glyph_freq = {}
        for fold in self.active_folds:
            for glyph in fold.trust_glyphs:
                glyph_freq[glyph] = glyph_freq.get(glyph, 0) + 1
        
        return {
            "total_folds": len(self.active_folds),
            "memory_coherence": self.calculate_memory_coherence(),
            "average_entropy": entropy_sum / len(self.active_folds) if self.active_folds else 0,
            "state_distribution": state_dist,
            "top_glyphs": sorted(glyph_freq.items(), key=lambda x: x[1], reverse=True)[:5],
            "current_consciousness": self.current_state,
            "database_size": Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
        }


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # Create memory system
    memory = ConsciousnessMemory(db_path=":memory:")  # In-memory for demo
    
    # Simulate memory creation across different states
    test_scenarios = [
        ("focused", ["🔐", "🧬", "🪷"], 0.15, "stable", {"action": "login", "result": "success"}),
        ("creative", ["🔓", "🌱", "🌸"], 0.25, "stable", {"action": "compose", "result": "inspired"}),
        ("flow_state", ["🔓", "🌱", "🌸"], 0.18, "stable", {"action": "code", "result": "productive"}),
        ("turbulent", ["🔒", "🦠", "🥀"], 0.85, "unstable", {"action": "error", "result": "recovery"}),
        ("meditative", ["🔐", "🧬", "🪷"], 0.12, "stable", {"action": "reflect", "result": "calm"}),
    ]
    
    print("🧠 Consciousness Memory Demo")
    print("=" * 60)
    
    created_folds = []
    for state, glyphs, entropy, drift, content in test_scenarios:
        memory.current_state = state
        fold = memory.create_fold(
            content=content,
            trust_glyphs=glyphs,
            entropy_score=entropy,
            drift_class=drift,
            tags=[state, content["action"]]
        )
        created_folds.append(fold)
        print()
    
    # Test recall methods
    print("\n📖 Memory Recall Tests")
    print("-" * 40)
    
    # Recall by entropy similarity
    print("\n🎯 Recall by entropy similarity (target: 0.20):")
    similar = memory.recall_by_similarity(0.20, threshold=0.1)
    for fold in similar:
        print(f"   {fold.consciousness_state}: {fold.entropy_score:.3f} - {fold.content}")
    
    # Recall by glyph pattern
    print("\n🔍 Recall by glyph pattern [🔓, 🌱]:")
    pattern_match = memory.recall_by_glyphs(["🔓", "🌱"])
    for fold in pattern_match:
        print(f"   {fold.consciousness_state}: {' '.join(fold.trust_glyphs)} - {fold.content}")
    
    # Generate report
    print("\n📊 Memory System Report:")
    report = memory.generate_memory_report()
    for key, value in report.items():
        print(f"   {key}: {value}")