#!/usr/bin/env python3
"""
T4/0.01% Excellence Tamper-Evident Proof System

Implements cryptographic verification using Merkle trees for audit evidence integrity.
Provides tamper-evident proof chains for regulatory-grade validation.
"""

import argparse
import hashlib
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class MerkleNode:
    """Individual node in the Merkle tree."""
    hash_value: str
    left_child: Optional[str] = None
    right_child: Optional[str] = None
    data: Optional[str] = None
    timestamp: float = 0.0


@dataclass
class MerkleProof:
    """Proof of inclusion for a specific item in the Merkle tree."""
    item_hash: str
    root_hash: str
    proof_path: List[Dict[str, str]]  # List of {hash, direction}
    tree_size: int
    proof_valid: bool


@dataclass
class MerkleChain:
    """Complete Merkle chain for audit evidence."""
    chain_id: str
    created_timestamp: float
    current_root: str
    tree_size: int
    nodes: Dict[str, MerkleNode]
    evidence_items: List[Dict[str, Any]]
    integrity_verified: bool
    verification_timestamp: float


class MerkleTreeBuilder:
    """Cryptographic Merkle tree implementation for audit evidence."""

    def __init__(self):
        self.nodes: Dict[str, MerkleNode] = {}

    def calculate_hash(self, data: str) -> str:
        """Calculate SHA-256 hash of data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def calculate_combined_hash(self, left_hash: str, right_hash: str) -> str:
        """Calculate hash of two child hashes."""
        combined = left_hash + right_hash
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def create_leaf_node(self, data: Dict[str, Any]) -> MerkleNode:
        """Create a leaf node from data."""
        # Serialize data deterministically
        data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        hash_value = self.calculate_hash(data_str)

        node = MerkleNode(
            hash_value=hash_value,
            data=data_str,
            timestamp=time.time()
        )

        self.nodes[hash_value] = node
        return node

    def create_internal_node(self, left_node: MerkleNode, right_node: MerkleNode) -> MerkleNode:
        """Create an internal node from two child nodes."""
        combined_hash = self.calculate_combined_hash(left_node.hash_value, right_node.hash_value)

        node = MerkleNode(
            hash_value=combined_hash,
            left_child=left_node.hash_value,
            right_child=right_node.hash_value,
            timestamp=time.time()
        )

        self.nodes[combined_hash] = node
        return node

    def build_tree(self, evidence_items: List[Dict[str, Any]]) -> str:
        """Build Merkle tree from evidence items and return root hash."""
        if not evidence_items:
            return ""

        # Create leaf nodes
        current_level = []
        for item in evidence_items:
            leaf_node = self.create_leaf_node(item)
            current_level.append(leaf_node)

        # Build tree bottom-up
        while len(current_level) > 1:
            next_level = []

            # Process pairs of nodes
            for i in range(0, len(current_level), 2):
                left_node = current_level[i]

                # Handle odd number of nodes by duplicating the last one
                if i + 1 < len(current_level):
                    right_node = current_level[i + 1]
                else:
                    right_node = left_node

                parent_node = self.create_internal_node(left_node, right_node)
                next_level.append(parent_node)

            current_level = next_level

        # Return root hash
        return current_level[0].hash_value if current_level else ""

    def generate_proof(self, item_hash: str, root_hash: str) -> MerkleProof:
        """Generate proof of inclusion for a specific item."""
        proof_path = []
        current_hash = item_hash
        tree_size = len([n for n in self.nodes.values() if n.data is not None])

        # Traverse from leaf to root
        while current_hash != root_hash:
            parent_found = False

            for node in self.nodes.values():
                if node.left_child == current_hash or node.right_child == current_hash:
                    # Found parent node
                    if node.left_child == current_hash:
                        # Current node is left child, sibling is right
                        sibling_hash = node.right_child
                        direction = "right"
                    else:
                        # Current node is right child, sibling is left
                        sibling_hash = node.left_child
                        direction = "left"

                    proof_path.append({
                        "hash": sibling_hash,
                        "direction": direction
                    })

                    current_hash = node.hash_value
                    parent_found = True
                    break

            if not parent_found:
                # Could not find path to root
                return MerkleProof(
                    item_hash=item_hash,
                    root_hash=root_hash,
                    proof_path=[],
                    tree_size=tree_size,
                    proof_valid=False
                )

        return MerkleProof(
            item_hash=item_hash,
            root_hash=root_hash,
            proof_path=proof_path,
            tree_size=tree_size,
            proof_valid=True
        )

    def verify_proof(self, proof: MerkleProof) -> bool:
        """Verify a Merkle proof of inclusion."""
        if not proof.proof_valid:
            return False

        current_hash = proof.item_hash

        # Reconstruct path to root
        for step in proof.proof_path:
            sibling_hash = step["hash"]
            direction = step["direction"]

            if direction == "left":
                # Sibling is left, current is right
                current_hash = self.calculate_combined_hash(sibling_hash, current_hash)
            else:
                # Sibling is right, current is left
                current_hash = self.calculate_combined_hash(current_hash, sibling_hash)

        return current_hash == proof.root_hash


class TamperEvidenceFramework:
    """Complete tamper-evidence framework for audit validation."""

    def __init__(self):
        self.merkle_builder = MerkleTreeBuilder()

    def load_evidence_files(self, file_patterns: List[str]) -> List[Dict[str, Any]]:
        """Load evidence files from patterns."""
        evidence_items = []

        for pattern in file_patterns:
            file_path = Path(pattern)
            if file_path.exists() and file_path.is_file():
                evidence_items.append(self._load_evidence_file(file_path))
            else:
                # Handle glob patterns
                for file_path in Path(".").glob(pattern):
                    if file_path.is_file():
                        evidence_items.append(self._load_evidence_file(file_path))

        return evidence_items

    def _load_evidence_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and fingerprint a single evidence file."""
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)

        # Load content if JSON
        content = None
        if file_path.suffix.lower() == '.json':
            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)
            except:
                content = None

        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_hash": file_hash,
            "content_hash": self._calculate_content_hash(content) if content else None,
            "timestamp": time.time(),
            "evidence_type": self._classify_evidence_type(file_path),
            "content": content
        }

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file contents."""
        hash_obj = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def _calculate_content_hash(self, content: Any) -> str:
        """Calculate hash of structured content."""
        content_str = json.dumps(content, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    def _classify_evidence_type(self, file_path: Path) -> str:
        """Classify evidence file type."""
        name = file_path.name.lower()

        if "audit_baseline" in name:
            return "audit_baseline"
        elif "statistical" in name:
            return "statistical_analysis"
        elif "reproducibility" in name:
            return "reproducibility_analysis"
        elif "chaos" in name or "fail_closed" in name:
            return "chaos_engineering"
        elif "verification" in name:
            return "verification_report"
        elif "evidence" in name:
            return "evidence_bundle"
        else:
            return "unknown"

    def create_merkle_chain(self, evidence_items: List[Dict[str, Any]]) -> MerkleChain:
        """Create complete Merkle chain from evidence items."""
        chain_id = str(uuid.uuid4())

        # Build Merkle tree
        root_hash = self.merkle_builder.build_tree(evidence_items)

        # Create chain object
        chain = MerkleChain(
            chain_id=chain_id,
            created_timestamp=time.time(),
            current_root=root_hash,
            tree_size=len(evidence_items),
            nodes=self.merkle_builder.nodes.copy(),
            evidence_items=evidence_items,
            integrity_verified=True,
            verification_timestamp=time.time()
        )

        return chain

    def verify_chain_integrity(self, chain: MerkleChain) -> Dict[str, Any]:
        """Verify complete chain integrity."""
        verification_results = {
            "chain_id": chain.chain_id,
            "verification_timestamp": time.time(),
            "overall_valid": True,
            "issues": [],
            "evidence_verifications": [],
            "tree_verification": None
        }

        # Verify each evidence item
        for i, item in enumerate(chain.evidence_items):
            item_verification = self._verify_evidence_item(item, chain)
            verification_results["evidence_verifications"].append(item_verification)

            if not item_verification["valid"]:
                verification_results["overall_valid"] = False
                verification_results["issues"].append(
                    f"Evidence item {i} failed verification: {item_verification['error']}"
                )

        # Verify tree structure
        tree_verification = self._verify_tree_structure(chain)
        verification_results["tree_verification"] = tree_verification

        if not tree_verification["valid"]:
            verification_results["overall_valid"] = False
            verification_results["issues"].append(
                f"Tree structure invalid: {tree_verification['error']}"
            )

        # Update chain verification status
        chain.integrity_verified = verification_results["overall_valid"]
        chain.verification_timestamp = verification_results["verification_timestamp"]

        return verification_results

    def _verify_evidence_item(self, item: Dict[str, Any], chain: MerkleChain) -> Dict[str, Any]:
        """Verify a single evidence item."""
        try:
            # Recalculate item hash
            item_str = json.dumps(item, sort_keys=True, separators=(',', ':'))
            calculated_hash = hashlib.sha256(item_str.encode('utf-8')).hexdigest()

            # Check if hash exists in tree nodes
            hash_in_tree = calculated_hash in chain.nodes

            # Verify file hash if file still exists
            file_verification = None
            if "file_path" in item:
                file_path = Path(item["file_path"])
                if file_path.exists():
                    current_file_hash = self._calculate_file_hash(file_path)
                    file_verification = {
                        "exists": True,
                        "hash_matches": current_file_hash == item.get("file_hash"),
                        "current_hash": current_file_hash,
                        "expected_hash": item.get("file_hash")
                    }
                else:
                    file_verification = {
                        "exists": False,
                        "hash_matches": False,
                        "error": "File no longer exists"
                    }

            return {
                "item_hash": calculated_hash,
                "hash_in_tree": hash_in_tree,
                "file_verification": file_verification,
                "valid": hash_in_tree and (
                    file_verification is None or
                    file_verification.get("hash_matches", True)
                ),
                "error": None
            }

        except Exception as e:
            return {
                "item_hash": None,
                "hash_in_tree": False,
                "file_verification": None,
                "valid": False,
                "error": str(e)
            }

    def _verify_tree_structure(self, chain: MerkleChain) -> Dict[str, Any]:
        """Verify Merkle tree structure integrity."""
        try:
            # Rebuild tree from evidence items
            temp_builder = MerkleTreeBuilder()
            rebuilt_root = temp_builder.build_tree(chain.evidence_items)

            # Compare roots
            root_matches = rebuilt_root == chain.current_root

            # Verify node consistency
            node_count_matches = len(temp_builder.nodes) == len(chain.nodes)

            # Check for orphaned nodes
            orphaned_nodes = set(chain.nodes.keys()) - set(temp_builder.nodes.keys())

            return {
                "rebuilt_root": rebuilt_root,
                "original_root": chain.current_root,
                "root_matches": root_matches,
                "node_count_matches": node_count_matches,
                "orphaned_nodes": list(orphaned_nodes),
                "valid": root_matches and node_count_matches and len(orphaned_nodes) == 0,
                "error": None
            }

        except Exception as e:
            return {
                "rebuilt_root": None,
                "original_root": chain.current_root,
                "root_matches": False,
                "node_count_matches": False,
                "orphaned_nodes": [],
                "valid": False,
                "error": str(e)
            }

    def generate_inclusion_proofs(self, chain: MerkleChain) -> Dict[str, MerkleProof]:
        """Generate inclusion proofs for all evidence items."""
        proofs = {}

        for item in chain.evidence_items:
            # Calculate item hash
            item_str = json.dumps(item, sort_keys=True, separators=(',', ':'))
            item_hash = hashlib.sha256(item_str.encode('utf-8')).hexdigest()

            # Generate proof
            proof = self.merkle_builder.generate_proof(item_hash, chain.current_root)
            proofs[item_hash] = proof

        return proofs

    def export_verification_package(
        self,
        chain: MerkleChain,
        verification_results: Dict[str, Any],
        output_path: str
    ):
        """Export complete verification package."""
        package = {
            "merkle_chain": asdict(chain),
            "verification_results": verification_results,
            "inclusion_proofs": {},
            "package_metadata": {
                "created_timestamp": time.time(),
                "package_version": "1.0.0",
                "verification_standard": "T4/0.01%"
            }
        }

        # Generate inclusion proofs
        proofs = self.generate_inclusion_proofs(chain)
        package["inclusion_proofs"] = {k: asdict(v) for k, v in proofs.items()}

        # Calculate package hash
        package_str = json.dumps(package, sort_keys=True, separators=(',', ':'))
        package_hash = hashlib.sha256(package_str.encode('utf-8')).hexdigest()
        package["package_metadata"]["package_hash"] = package_hash

        # Save package
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(package, f, indent=2, sort_keys=True)

        return package_hash


def main():
    """Main tamper-evidence verification function."""
    parser = argparse.ArgumentParser(description="T4/0.01% Tamper-Evidence Verification")
    parser.add_argument("--chain", nargs="+", help="Merkle chain files to verify")
    parser.add_argument("--evidence", nargs="+", help="Evidence files to include in chain")
    parser.add_argument("--verify-integrity", action="store_true", help="Verify chain integrity")
    parser.add_argument("--create-chain", action="store_true", help="Create new Merkle chain")
    parser.add_argument("--output", required=True, help="Output verification file")

    args = parser.parse_args()

    framework = TamperEvidenceFramework()

    if args.create_chain and args.evidence:
        print("🔗 Creating Merkle chain from evidence files...")

        # Load evidence files
        evidence_items = framework.load_evidence_files(args.evidence)
        print(f"Loaded {len(evidence_items)} evidence items")

        # Create Merkle chain
        chain = framework.create_merkle_chain(evidence_items)

        # Verify chain integrity
        verification_results = framework.verify_chain_integrity(chain)

        # Export verification package
        package_hash = framework.export_verification_package(
            chain, verification_results, args.output
        )

        print(f"✅ Merkle chain created")
        print(f"Root hash: {chain.current_root}")
        print(f"Tree size: {chain.tree_size}")
        print(f"Package hash: {package_hash}")
        print(f"Output: {args.output}")

        if verification_results["overall_valid"]:
            print("🛡️  Chain integrity: VERIFIED")
        else:
            print("⚠️  Chain integrity: ISSUES DETECTED")
            for issue in verification_results["issues"]:
                print(f"  - {issue}")

    elif args.verify_integrity and args.chain:
        print("🔍 Verifying existing Merkle chain integrity...")

        for chain_file in args.chain:
            try:
                with open(chain_file, 'r') as f:
                    package = json.load(f)

                # Reconstruct chain
                chain_data = package["merkle_chain"]
                chain = MerkleChain(**chain_data)

                # Verify integrity
                verification_results = framework.verify_chain_integrity(chain)

                print(f"\nChain: {chain_file}")
                print(f"Chain ID: {chain.chain_id}")
                print(f"Root hash: {chain.current_root}")

                if verification_results["overall_valid"]:
                    print("✅ Integrity: VERIFIED")
                else:
                    print("❌ Integrity: COMPROMISED")
                    for issue in verification_results["issues"]:
                        print(f"  - {issue}")

            except Exception as e:
                print(f"❌ Error verifying {chain_file}: {e}")

    else:
        print("❌ Error: Must specify either --create-chain with --evidence or --verify-integrity with --chain")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())