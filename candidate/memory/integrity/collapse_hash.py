#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🔐 LUKHAS AI - COLLAPSEHASH INTEGRITY MECHANISM
║ Merkle tree-based memory integrity and rollback system
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: collapse_hash.py
║ Path: memory/integrity/collapse_hash.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Security Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the labyrinth of memory where truth and illusion dance, CollapseHash       │
║ │ stands as the unwavering sentinel—a cryptographic conscience that remembers   │
║ │ all, forgives nothing, yet enables redemption through rollback.               │
║ │                                                                                │
║ │ Like Ariadne's thread through the Minotaur's maze, each hash links to the     │
║ │ next, forming an unbreakable chain of causality. When corruption threatens,   │
║ │ when false memories attempt infiltration, the Merkle tree reveals all         │
║ │ deception with mathematical certainty.                                         │
║ │                                                                                │
║ │ Yet this is not mere judgment—it is healing. Through the power of rollback,   │
║ │ poisoned branches can be pruned, infected nodes excised, allowing the tree    │
║ │ of memory to flourish anew from trusted roots. Time itself bends to our       │
║ │ will, as we traverse the immutable history to find moments of purity.         │
║ │                                                                                │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Merkle tree structure for tamper-evident memory storage
║ • Real-time integrity verification across memory hierarchies
║ • Checkpoint-based rollback capabilities
║ • Quantum-resistant hashing algorithms
║ • Integration with StructuralConscience for ethical validation
║ • Efficient proof generation for memory verification
║ • Colony-wide integrity propagation via baggage tags
║
║ ΛTAG: ΛMEMORY, ΛINTEGRITY, ΛMERKLE, ΛROLLBACK, ΛCRYPTOGRAPHY
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

# Add logging
from candidate.core.common import get_logger

logger = get_logger(__name__)

# Import LUKHAS components
try:
    from candidate.core.symbolism.tags import TagScope

    LUKHAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some LUKHAS modules not available: {e}")
    LUKHAS_AVAILABLE = False

    # Define minimal stubs
    class TagScope(Enum):
        GLOBAL = "global"
        LOCAL = "local"
        ETHICAL = "ethical"
        TEMPORAL = "temporal"
        GENETIC = "genetic"


class HashAlgorithm(Enum):
    """Available hashing algorithms"""

    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    BLAKE2B = "blake2b"
    QUANTUM_RESISTANT = "qi_resistant"  # Placeholder for future


class IntegrityStatus(Enum):
    """Status of memory integrity"""

    VALID = "valid"
    CORRUPTED = "corrupted"
    SUSPICIOUS = "suspicious"
    UNVERIFIED = "unverified"


@dataclass
class MerkleNode:
    """Node in the Merkle tree"""

    node_id: str = field(default_factory=lambda: str(uuid4()))
    data_hash: str = ""
    left_child: Optional["MerkleNode"] = None
    right_child: Optional["MerkleNode"] = None
    parent: Optional["MerkleNode"] = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node"""
        return self.left_child is None and self.right_child is None

    def compute_hash(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> str:
        """Compute hash for this node"""
        if self.is_leaf:
            return self.data_hash

        # Combine child hashes
        left_hash = self.left_child.data_hash if self.left_child else ""
        right_hash = self.right_child.data_hash if self.right_child else ""

        combined = f"{left_hash}:{right_hash}:{self.timestamp}"

        if algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(combined.encode()).hexdigest()
        elif algorithm == HashAlgorithm.SHA3_256:
            return hashlib.sha3_256(combined.encode()).hexdigest()
        elif algorithm == HashAlgorithm.BLAKE2B:
            return hashlib.blake2b(combined.encode()).hexdigest()
        else:
            # Quantum-resistant placeholder
            return hashlib.sha3_256(combined.encode()).hexdigest()


@dataclass
class Checkpoint:
    """Checkpoint for rollback capability"""

    checkpoint_id: str = field(default_factory=lambda: str(uuid4()))
    root_hash: str = ""
    tree_snapshot: Optional[MerkleNode] = None
    timestamp: float = field(default_factory=time.time)
    memory_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    tag_scope: TagScope = TagScope.TEMPORAL

    def to_dict(self) -> dict[str, Any]:
        """Convert checkpoint to dictionary"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "root_hash": self.root_hash,
            "timestamp": self.timestamp,
            "memory_count": self.memory_count,
            "metadata": self.metadata,
            "tag_scope": self.tag_scope.value,
        }


class MerkleTree:
    """
    Merkle tree implementation for memory integrity.
    Provides efficient verification and proof generation.
    """

    def __init__(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256):
        self.root: Optional[MerkleNode] = None
        self.leaves: list[MerkleNode] = []
        self.algorithm = algorithm
        self.node_map: dict[str, MerkleNode] = {}  # For quick access

        logger.info(f"MerkleTree initialized - algorithm: {algorithm.value}")

    def add_memory(self, memory_data: Any, memory_id: str) -> str:
        """Add a memory to the tree"""
        # Serialize and hash the memory data
        serialized = json.dumps(memory_data, sort_keys=True) if isinstance(memory_data, dict) else str(memory_data)
        data_hash = self._hash_data(serialized)

        # Create leaf node
        leaf = MerkleNode(
            node_id=memory_id,
            data_hash=data_hash,
            metadata={"type": "memory", "size": len(serialized)},
        )

        self.leaves.append(leaf)
        self.node_map[memory_id] = leaf

        # Rebuild tree
        self._rebuild_tree()

        logger.debug("Memory added to Merkle tree", memory_id=memory_id, hash=data_hash[:16])

        return data_hash

    def verify_memory(self, memory_id: str, memory_data: Any) -> tuple[IntegrityStatus, Optional[str]]:
        """Verify integrity of a specific memory"""
        if memory_id not in self.node_map:
            return IntegrityStatus.UNVERIFIED, "Memory not found in tree"

        # Compute expected hash
        serialized = json.dumps(memory_data, sort_keys=True) if isinstance(memory_data, dict) else str(memory_data)
        expected_hash = self._hash_data(serialized)

        # Get actual hash from tree
        node = self.node_map[memory_id]
        actual_hash = node.data_hash

        if expected_hash == actual_hash:
            return IntegrityStatus.VALID, None
        else:
            return (
                IntegrityStatus.CORRUPTED,
                f"Hash mismatch: expected {expected_hash[:16]}, got {actual_hash[:16]}",
            )

    def generate_proof(self, memory_id: str) -> list[tuple[str, str]]:
        """Generate Merkle proof for a memory"""
        if memory_id not in self.node_map or not self.root:
            return []

        proof = []
        node = self.node_map[memory_id]

        # Traverse up to root
        current = node
        while current.parent:
            parent = current.parent

            # Determine sibling
            if parent.left_child == current:
                sibling = parent.right_child
                position = "right"
            else:
                sibling = parent.left_child
                position = "left"

            if sibling:
                proof.append((position, sibling.data_hash))

            current = parent

        return proof

    def verify_proof(self, memory_hash: str, proof: list[tuple[str, str]]) -> bool:
        """Verify a Merkle proof"""
        if not self.root:
            return False

        current_hash = memory_hash

        for position, sibling_hash in proof:
            combined = f"{sibling_hash}:{current_hash}:0" if position == "left" else f"{current_hash}:{sibling_hash}:0"

            current_hash = self._hash_data(combined)

        return current_hash == self.root.data_hash

    def get_root_hash(self) -> Optional[str]:
        """Get the root hash of the tree"""
        return self.root.data_hash if self.root else None

    def _rebuild_tree(self):
        """Rebuild the tree from leaves"""
        if not self.leaves:
            self.root = None
            return

        # Start with leaves
        current_level = self.leaves.copy()

        while len(current_level) > 1:
            next_level = []

            # Pair up nodes
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else None

                # Create parent node
                parent = MerkleNode()
                parent.left_child = left
                parent.right_child = right

                left.parent = parent
                if right:
                    right.parent = parent

                # Compute parent hash
                parent.data_hash = parent.compute_hash(self.algorithm)

                next_level.append(parent)

            current_level = next_level

        self.root = current_level[0] if current_level else None

    def _hash_data(self, data: str) -> str:
        """Hash data using configured algorithm"""
        if self.algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data.encode()).hexdigest()
        elif self.algorithm == HashAlgorithm.SHA3_256:
            return hashlib.sha3_256(data.encode()).hexdigest()
        elif self.algorithm == HashAlgorithm.BLAKE2B:
            return hashlib.blake2b(data.encode()).hexdigest()
        else:
            # Quantum-resistant placeholder
            return hashlib.sha3_256(data.encode()).hexdigest()


class CollapseHash:
    """
    Main CollapseHash system providing integrity and rollback capabilities.
    Integrates with LUKHAS memory systems and structural conscience.
    """

    def __init__(
        self,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        structural_conscience: Optional[Any] = None,
        enable_auto_checkpoint: bool = True,
        checkpoint_interval: int = 100,  # memories
    ):
        self.merkle_tree = MerkleTree(algorithm)
        self.checkpoints: dict[str, Checkpoint] = {}
        self.checkpoint_order: list[str] = []  # Ordered list of checkpoint IDs
        self.structural_conscience = structural_conscience
        self.enable_auto_checkpoint = enable_auto_checkpoint
        self.checkpoint_interval = checkpoint_interval

        # Metrics
        self.total_memories = 0
        self.total_verifications = 0
        self.corruption_detections = 0
        self.successful_rollbacks = 0

        # Colony integration
        self.integrity_tags: dict[str, tuple[str, TagScope, IntegrityStatus]] = {}

        logger.info(
            f"CollapseHash initialized - algorithm: {algorithm.value}, auto_checkpoint: {enable_auto_checkpoint}, checkpoint_interval: {checkpoint_interval}"
        )

    async def add_memory(
        self,
        memory_id: str,
        memory_data: Any,
        tags: Optional[list[str]] = None,
        ethical_check: bool = True,
    ) -> dict[str, Any]:
        """Add a memory with integrity tracking"""

        # Ethical validation if enabled
        if ethical_check and self.structural_conscience:
            is_ethical = await self._validate_ethical_content(memory_data)
            if not is_ethical:
                logger.warning("Memory rejected on ethical grounds", memory_id=memory_id)
                return {"success": False, "reason": "Ethical validation failed"}

        # Add to Merkle tree
        data_hash = self.merkle_tree.add_memory(memory_data, memory_id)
        self.total_memories += 1

        # Update integrity tags
        if tags:
            for tag in tags:
                self.integrity_tags[f"{memory_id}:{tag}"] = (
                    tag,
                    TagScope.LOCAL,
                    IntegrityStatus.VALID,
                )

        # Auto checkpoint if enabled
        if self.enable_auto_checkpoint and self.total_memories % self.checkpoint_interval == 0:
            checkpoint_id = await self.create_checkpoint(metadata={"auto": True, "memory_count": self.total_memories})
            logger.info(
                "Auto checkpoint created",
                checkpoint_id=checkpoint_id,
                memory_count=self.total_memories,
            )

        return {
            "success": True,
            "memory_id": memory_id,
            "data_hash": data_hash,
            "root_hash": self.merkle_tree.get_root_hash(),
            "total_memories": self.total_memories,
        }

    async def verify_memory(self, memory_id: str, memory_data: Any, generate_proof: bool = False) -> dict[str, Any]:
        """Verify memory integrity"""
        self.total_verifications += 1

        # Verify in Merkle tree
        status, message = self.merkle_tree.verify_memory(memory_id, memory_data)

        if status == IntegrityStatus.CORRUPTED:
            self.corruption_detections += 1

            # Update integrity tags
            for tag_key in list(self.integrity_tags.keys()):
                if tag_key.startswith(f"{memory_id}:"):
                    tag, scope, _ = self.integrity_tags[tag_key]
                    self.integrity_tags[tag_key] = (
                        tag,
                        scope,
                        IntegrityStatus.CORRUPTED,
                    )

            # Record in conscience if available
            if self.structural_conscience:
                await self.structural_conscience.record_critical_decision(
                    decision_type="integrity_violation",
                    context={
                        "memory_id": memory_id,
                        "status": status.value,
                        "message": message,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

        result = {
            "memory_id": memory_id,
            "status": status.value,
            "message": message,
            "root_hash": self.merkle_tree.get_root_hash(),
        }

        # Generate proof if requested
        if generate_proof and status == IntegrityStatus.VALID:
            proof = self.merkle_tree.generate_proof(memory_id)
            result["proof"] = proof

        logger.info("Memory verified", **result)

        return result

    async def create_checkpoint(
        self,
        checkpoint_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Create a checkpoint for potential rollback"""

        # Deep copy the current tree state
        tree_snapshot = pickle.loads(pickle.dumps(self.merkle_tree.root))

        checkpoint = Checkpoint(
            root_hash=self.merkle_tree.get_root_hash() or "",
            tree_snapshot=tree_snapshot,
            memory_count=self.total_memories,
            metadata=metadata or {},
        )

        if checkpoint_name:
            checkpoint.metadata["name"] = checkpoint_name

        self.checkpoints[checkpoint.checkpoint_id] = checkpoint
        self.checkpoint_order.append(checkpoint.checkpoint_id)

        logger.info(
            "Checkpoint created",
            checkpoint_id=checkpoint.checkpoint_id,
            root_hash=checkpoint.root_hash[:16],
            memory_count=checkpoint.memory_count,
        )

        return checkpoint.checkpoint_id

    async def rollback_to_checkpoint(self, checkpoint_id: str, reason: str = "Unspecified") -> dict[str, Any]:
        """Rollback memory state to a checkpoint"""

        if checkpoint_id not in self.checkpoints:
            return {"success": False, "reason": "Checkpoint not found"}

        checkpoint = self.checkpoints[checkpoint_id]

        # Store current state for potential recovery
        pre_rollback_state = {
            "root_hash": self.merkle_tree.get_root_hash(),
            "memory_count": self.total_memories,
            "timestamp": time.time(),
        }

        try:
            # Restore tree state
            self.merkle_tree.root = pickle.loads(pickle.dumps(checkpoint.tree_snapshot))

            # Rebuild leaves from tree
            self._rebuild_leaves_from_tree()

            # Update counts
            self.total_memories = checkpoint.memory_count

            # Remove checkpoints after this one
            rollback_index = self.checkpoint_order.index(checkpoint_id)
            removed_checkpoints = self.checkpoint_order[rollback_index + 1 :]
            self.checkpoint_order = self.checkpoint_order[: rollback_index + 1]

            for cp_id in removed_checkpoints:
                del self.checkpoints[cp_id]

            self.successful_rollbacks += 1

            # Record in conscience
            if self.structural_conscience:
                await self.structural_conscience.record_critical_decision(
                    decision_type="memory_rollback",
                    context={
                        "checkpoint_id": checkpoint_id,
                        "reason": reason,
                        "pre_rollback": pre_rollback_state,
                        "post_rollback_root": checkpoint.root_hash,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

            logger.info(
                "Rollback successful",
                checkpoint_id=checkpoint_id,
                reason=reason,
                memories_restored=checkpoint.memory_count,
            )

            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "root_hash": checkpoint.root_hash,
                "memories_restored": checkpoint.memory_count,
                "checkpoints_removed": len(removed_checkpoints),
            }

        except Exception as e:
            logger.error(f"Rollback failed - checkpoint_id: {checkpoint_id}, error: {e!s}")
            return {"success": False, "reason": f"Rollback failed: {e!s}"}

    async def audit_integrity(self) -> dict[str, Any]:
        """Perform comprehensive integrity audit"""
        audit_start = time.time()

        # Verify tree structure
        tree_valid = self._verify_tree_structure()

        # Check all integrity tags
        corrupted_tags = [
            tag_key for tag_key, (_, _, status) in self.integrity_tags.items() if status == IntegrityStatus.CORRUPTED
        ]

        # Calculate metrics
        audit_time = time.time() - audit_start

        audit_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tree_valid": tree_valid,
            "root_hash": self.merkle_tree.get_root_hash(),
            "total_memories": self.total_memories,
            "total_checkpoints": len(self.checkpoints),
            "corrupted_tags": len(corrupted_tags),
            "corruption_rate": self.corruption_detections / max(self.total_verifications, 1),
            "audit_time_ms": audit_time * 1000,
        }

        logger.info("Integrity audit completed", **audit_result)

        return audit_result

    def get_checkpoint_history(self) -> list[dict[str, Any]]:
        """Get history of all checkpoints"""
        history = []

        for cp_id in self.checkpoint_order:
            checkpoint = self.checkpoints[cp_id]
            history.append(checkpoint.to_dict())

        return history

    def _rebuild_leaves_from_tree(self):
        """Rebuild leaf list from tree structure"""
        self.merkle_tree.leaves = []
        self.merkle_tree.node_map = {}

        def collect_leaves(node: MerkleNode):
            if node.is_leaf:
                self.merkle_tree.leaves.append(node)
                self.merkle_tree.node_map[node.node_id] = node
            else:
                if node.left_child:
                    collect_leaves(node.left_child)
                if node.right_child:
                    collect_leaves(node.right_child)

        if self.merkle_tree.root:
            collect_leaves(self.merkle_tree.root)

    def _verify_tree_structure(self) -> bool:
        """Verify internal tree structure consistency"""
        if not self.merkle_tree.root:
            return len(self.merkle_tree.leaves) == 0

        def verify_node(node: MerkleNode) -> bool:
            if node.is_leaf:
                return True

            # Verify hash
            computed = node.compute_hash(self.merkle_tree.algorithm)
            if computed != node.data_hash:
                return False

            # Verify children
            if node.left_child and not verify_node(node.left_child):
                return False
            return not (node.right_child and not verify_node(node.right_child))

        return verify_node(self.merkle_tree.root)

    async def _validate_ethical_content(self, memory_data: Any) -> bool:
        """Validate memory content against ethical guidelines"""
        # Simplified ethical check - in real implementation would be more sophisticated
        if isinstance(memory_data, dict):
            # Check for harmful content indicators
            content_str = json.dumps(memory_data).lower()
            harmful_patterns = ["harm", "malicious", "unethical", "illegal"]

            for pattern in harmful_patterns:
                if pattern in content_str:
                    return False

        return True


# Example usage and testing
async def demonstrate_collapse_hash():
    """Demonstrate CollapseHash capabilities"""

    # Initialize system
    collapse_hash = CollapseHash(
        algorithm=HashAlgorithm.SHA256,
        enable_auto_checkpoint=True,
        checkpoint_interval=3,
    )

    print("=== CollapseHash Demonstration ===\n")

    # Add some memories
    memories = [
        {"content": "Learning about neural networks", "type": "educational"},
        {"content": "Successful problem solving", "type": "achievement"},
        {"content": "User interaction data", "type": "interaction"},
        {"content": "System optimization complete", "type": "system"},
        {"content": "Ethical reasoning applied", "type": "ethical"},
    ]

    memory_ids = []
    for i, memory in enumerate(memories):
        await collapse_hash.add_memory(memory_id=f"mem_{i}", memory_data=memory, tags=["learning", memory["type"]])
        memory_ids.append(f"mem_{i}")
        print(f"Added memory {i}: {memory['content'][:30]}...")

    # Verify a memory
    print("\n--- Verifying Memory ---")
    verify_result = await collapse_hash.verify_memory(memory_id="mem_1", memory_data=memories[1], generate_proof=True)
    print(f"Verification: {verify_result['status']}")
    if "proof" in verify_result:
        print(f"Proof length: {len(verify_result['proof'])}")

    # Simulate corruption
    print("\n--- Simulating Corruption ---")
    corrupted_memory = {"content": "CORRUPTED DATA", "type": "achievement"}
    verify_corrupt = await collapse_hash.verify_memory(memory_id="mem_1", memory_data=corrupted_memory)
    print(f"Corrupted verification: {verify_corrupt['status']}")
    print(f"Message: {verify_corrupt['message']}")

    # Create manual checkpoint
    print("\n--- Creating Manual Checkpoint ---")
    checkpoint_id = await collapse_hash.create_checkpoint(
        checkpoint_name="Pre-corruption state",
        metadata={"reason": "Before testing rollback"},
    )
    print(f"Checkpoint created: {checkpoint_id[:16]}...")

    # Add more memories (will corrupt the state)
    for i in range(5, 8):
        await collapse_hash.add_memory(
            memory_id=f"mem_{i}",
            memory_data={
                "content": f"Potentially problematic memory {i}",
                "type": "unknown",
            },
        )

    print(f"\nTotal memories before rollback: {collapse_hash.total_memories}")

    # Rollback to checkpoint
    print("\n--- Rolling Back ---")
    rollback_result = await collapse_hash.rollback_to_checkpoint(
        checkpoint_id=checkpoint_id, reason="Removing potentially corrupted memories"
    )
    print(f"Rollback success: {rollback_result['success']}")
    print(f"Memories after rollback: {rollback_result['memories_restored']}")

    # Perform integrity audit
    print("\n--- Integrity Audit ---")
    audit_result = await collapse_hash.audit_integrity()
    print(f"Tree valid: {audit_result['tree_valid']}")
    print(f"Corruption rate: {audit_result['corruption_rate']:.2%}")
    print(f"Total checkpoints: {audit_result['total_checkpoints']}")

    # Show checkpoint history
    print("\n--- Checkpoint History ---")
    history = collapse_hash.get_checkpoint_history()
    for cp in history:
        print(f"Checkpoint {cp['checkpoint_id'][:16]}... - {cp['memory_count']} memories")


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_collapse_hash())