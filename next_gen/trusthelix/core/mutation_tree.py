#!/usr/bin/env python3
"""
Symbolic Mutation Tree - Core of TrustHelix
Tracks how symbolic glyphs transform based on user actions and system trust
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DriftState(Enum):
    """Visual representation of system drift"""
    STABLE = "🌿"      # 0.0 - 0.3
    NEUTRAL = "🌀"     # 0.3 - 0.7  
    UNSTABLE = "🌪️"    # 0.7 - 1.0


@dataclass
class GlyphMutation:
    """Record of a single glyph transformation"""
    timestamp: datetime
    from_glyph: str
    to_glyph: str
    action: str
    user_id: str
    drift_delta: float
    reason: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "from_glyph": self.from_glyph,
            "to_glyph": self.to_glyph,
            "action": self.action,
            "user_id": self.user_id,
            "drift_delta": self.drift_delta,
            "reason": self.reason,
            "metadata": self.metadata
        }
    
    def compute_hash(self) -> str:
        """Compute immutable hash of this mutation"""
        content = f"{self.timestamp.isoformat()}|{self.from_glyph}|{self.to_glyph}|{self.action}|{self.user_id}"
        return hashlib.sha3_256(content.encode()).hexdigest()[:16]


@dataclass
class ConsentNode:
    """Node in the consent lineage tree"""
    node_id: str
    glyphs: List[str]
    action: str
    outcome: str
    drift_score: float
    children: List['ConsentNode'] = field(default_factory=list)
    mutations: List[GlyphMutation] = field(default_factory=list)
    
    def add_child(self, child: 'ConsentNode'):
        self.children.append(child)
    
    def add_mutation(self, mutation: GlyphMutation):
        self.mutations.append(mutation)
    
    def get_drift_state(self) -> DriftState:
        if self.drift_score < 0.3:
            return DriftState.STABLE
        elif self.drift_score < 0.7:
            return DriftState.NEUTRAL
        else:
            return DriftState.UNSTABLE


class SymbolicMutationTree:
    """
    Mutable ethical audit tree that tracks consent lineage and glyph transformations
    """
    
    # Glyph transformation rules
    TRUST_MUTATIONS = {
        "🔐": {"increase": "🔓", "decrease": "🔒", "neutral": "🔐"},
        "🧬": {"increase": "🌱", "decrease": "🦠", "neutral": "🧬"},
        "🪷": {"increase": "🌸", "decrease": "🥀", "neutral": "🪷"},
        "👁️": {"increase": "👁️‍🗨️", "decrease": "🫣", "neutral": "👁️"},
        "🌊": {"increase": "🌈", "decrease": "🌪️", "neutral": "🌊"},
        "✨": {"increase": "💫", "decrease": "💨", "neutral": "✨"}
    }
    
    # Action impact on trust
    ACTION_IMPACTS = {
        "unlock_profile": 0.05,
        "view_data": 0.02,
        "authenticate": 0.03,
        "suspicious_attempt": -0.15,
        "failed_auth": -0.10,
        "timeout": -0.05,
        "consent_granted": 0.08,
        "consent_revoked": -0.12,
        "emergency_access": -0.20
    }
    
    def __init__(self, genesis_hash: str = None):
        self.genesis_hash = genesis_hash or self._compute_genesis_hash()
        self.root = ConsentNode(
            node_id="root",
            glyphs=["🌿", "🪷", "🔐"],
            action="genesis",
            outcome="initialized",
            drift_score=0.0
        )
        self.current_drift = 0.0
        self.mutation_history: List[GlyphMutation] = []
        self.active_paths: Dict[str, ConsentNode] = {}
        
        logger.info(f"🌳 TrustHelix initialized with genesis: {self.genesis_hash[:16]}...")
    
    def _compute_genesis_hash(self) -> str:
        """Reference to immutable Genesis Transmission"""
        # This would reference the actual sealed Genesis hash
        return "60baf875152a4453a62a908e110fe6acb7b093ac3678536867ba9e55b4cd512a"
    
    def track_action(self, user_id: str, glyphs: List[str], action: str, 
                    outcome: str = "success") -> Tuple[List[str], float]:
        """
        Track a user action and return mutated glyphs with new drift score
        """
        # Calculate drift impact
        impact = self.ACTION_IMPACTS.get(action, 0.0)
        
        # Adjust impact based on outcome
        if outcome == "failure":
            impact *= 1.5  # Failures have stronger negative impact
        elif outcome == "partial":
            impact *= 0.5
        
        # Update drift score
        old_drift = self.current_drift
        self.current_drift = max(0.0, min(1.0, self.current_drift + impact))
        drift_delta = self.current_drift - old_drift
        
        # Mutate glyphs based on trust change
        mutated_glyphs = []
        trust_direction = "increase" if impact > 0 else "decrease" if impact < 0 else "neutral"
        
        for glyph in glyphs:
            # Check if this glyph has a mutation rule
            mutation_rule = None
            for base_glyph, mutations in self.TRUST_MUTATIONS.items():
                if glyph == base_glyph or glyph in mutations.values():
                    mutation_rule = mutations
                    # Find the current state
                    if glyph != base_glyph:
                        # Find which state this glyph represents
                        for state, state_glyph in mutations.items():
                            if state_glyph == glyph:
                                # Already in a state, decide next mutation
                                if trust_direction == "increase" and state != "increase":
                                    new_glyph = mutations["increase"]
                                elif trust_direction == "decrease" and state != "decrease":
                                    new_glyph = mutations["decrease"]
                                else:
                                    new_glyph = glyph  # No change if already at extreme
                                break
                        else:
                            new_glyph = mutations[trust_direction]
                    else:
                        new_glyph = mutations[trust_direction]
                    break
            else:
                # No mutation rule found, keep original
                new_glyph = glyph
                
            mutated_glyphs.append(new_glyph)
            
            # Record mutation if changed
            if new_glyph != glyph:
                mutation = GlyphMutation(
                    timestamp=datetime.utcnow(),
                    from_glyph=glyph,
                    to_glyph=new_glyph,
                    action=action,
                    user_id=user_id,
                    drift_delta=drift_delta,
                    reason=f"Trust {trust_direction} from {action}",
                    metadata={
                        "outcome": outcome,
                        "old_drift": old_drift,
                        "new_drift": self.current_drift
                    }
                )
                self.mutation_history.append(mutation)
        
        # Create consent node
        node = ConsentNode(
            node_id=f"{user_id}_{datetime.utcnow().timestamp()}",
            glyphs=mutated_glyphs,
            action=action,
            outcome=outcome,
            drift_score=self.current_drift
        )
        
        # Add to active path or create new one
        if user_id in self.active_paths:
            self.active_paths[user_id].add_child(node)
        else:
            self.root.add_child(node)
        
        self.active_paths[user_id] = node
        
        logger.info(f"🔄 Action tracked: {action} → drift: {self.current_drift:.3f} ({drift_delta:+.3f})")
        logger.info(f"🎭 Glyphs mutated: {' '.join(glyphs)} → {' '.join(mutated_glyphs)}")
        
        return mutated_glyphs, self.current_drift
    
    def get_drift_state(self) -> DriftState:
        """Get current drift state with emoji representation"""
        if self.current_drift < 0.3:
            return DriftState.STABLE
        elif self.current_drift < 0.7:
            return DriftState.NEUTRAL
        else:
            return DriftState.UNSTABLE
    
    def get_consent_path(self, user_id: str) -> List[Dict]:
        """Get consent path for a specific user"""
        path = []
        
        if user_id not in self.active_paths:
            return path
        
        node = self.active_paths[user_id]
        while node and node.node_id != "root":
            path.append({
                "timestamp": node.node_id.split("_")[1],
                "glyphs": node.glyphs,
                "action": node.action,
                "outcome": node.outcome,
                "drift_score": node.drift_score,
                "drift_state": node.get_drift_state().value
            })
            # Walk back up the tree (would need parent references in production)
            node = None  # Simplified for demo
        
        return list(reversed(path))
    
    def export_mutation_log(self) -> List[Dict]:
        """Export full mutation history"""
        return [m.to_dict() for m in self.mutation_history]
    
    def calculate_entropy(self) -> float:
        """Calculate decision entropy based on mutation patterns"""
        if not self.mutation_history:
            return 0.0
        
        # Count mutation types
        mutation_counts = {}
        for mutation in self.mutation_history:
            key = f"{mutation.from_glyph}→{mutation.to_glyph}"
            mutation_counts[key] = mutation_counts.get(key, 0) + 1
        
        # Calculate Shannon entropy
        import math
        total = len(self.mutation_history)
        entropy = 0.0
        for count in mutation_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Normalize to 0-1 range (max entropy is log2(n) where n is number of unique mutations)
        max_entropy = math.log2(len(mutation_counts)) if len(mutation_counts) > 1 else 1
        return min(1.0, entropy / max_entropy if max_entropy > 0 else 0)
    
    def visualize_tree(self) -> str:
        """Generate ASCII visualization of consent tree"""
        lines = ["🌳 TrustHelix Consent Tree"]
        lines.append("=" * 40)
        lines.append(f"Genesis: {self.genesis_hash[:16]}...")
        lines.append(f"Current Drift: {self.current_drift:.3f} {self.get_drift_state().value}")
        lines.append(f"Mutations: {len(self.mutation_history)}")
        lines.append(f"Entropy: {self.calculate_entropy():.3f}")
        lines.append("")
        
        # Show recent mutations
        lines.append("Recent Mutations:")
        for mutation in self.mutation_history[-5:]:
            lines.append(f"  {mutation.from_glyph} → {mutation.to_glyph} ({mutation.action})")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize TrustHelix
    helix = SymbolicMutationTree()
    
    # Simulate user actions
    user_id = "test_user_001"
    
    # Positive actions
    glyphs = ["🔐", "🧬", "🪷"]
    glyphs, drift = helix.track_action(user_id, glyphs, "authenticate", "success")
    glyphs, drift = helix.track_action(user_id, glyphs, "unlock_profile", "success")
    glyphs, drift = helix.track_action(user_id, glyphs, "consent_granted", "success")
    
    # Negative action
    glyphs, drift = helix.track_action(user_id, glyphs, "suspicious_attempt", "failure")
    
    # Show results
    print(helix.visualize_tree())
    print(f"\nFinal glyphs: {' '.join(glyphs)}")
    print(f"Final drift state: {helix.get_drift_state().value}")