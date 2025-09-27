#!/usr/bin/env python3
"""
Matrix Provenance CAR Generator

Creates IPLD CAR files containing the provenance DAG for Matrix contracts.
Provides tamper-evident history and content-addressed storage foundation
for future IPFS integration.
"""

import argparse
import base64
import hashlib
import json
import struct
import sys
import glob
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple
import io


class MockIPLDNode:
    """Mock IPLD DAG-CBOR node for provenance tracking."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.cid = self._generate_cid()

    def _generate_cid(self) -> str:
        """Generate deterministic mock CID for the node."""
        # Create deterministic JSON representation
        content = json.dumps(self.data, sort_keys=True, separators=(',', ':'))
        hash_bytes = hashlib.sha256(content.encode('utf-8')).digest()

        # Mock CIDv1 format: base32-encoded with prefix
        # Real CIDs are more complex, but this gives us a deterministic identifier
        encoded = base64.b32encode(hash_bytes).decode('ascii').rstrip('=').lower()
        return f"bafyrei{encoded[:48]}"  # Mock CIDv1 format

    def to_cbor_mock(self) -> bytes:
        """Convert to mock CBOR encoding."""
        # For sandbox mode, we'll use JSON as mock CBOR
        json_data = json.dumps(self.data, sort_keys=True)
        return json_data.encode('utf-8')


class MockCARFile:
    """Mock CAR (Content Addressable Archive) file generator."""

    def __init__(self):
        self.blocks: List[Tuple[str, bytes]] = []
        self.roots: List[str] = []

    def add_block(self, cid: str, data: bytes):
        """Add a block to the CAR file."""
        self.blocks.append((cid, data))

    def set_roots(self, roots: List[str]):
        """Set the root CIDs for the CAR file."""
        self.roots = roots

    def write(self, output_path: Path):
        """Write the CAR file to disk."""
        with open(output_path, 'wb') as f:
            # Write CAR header (simplified)
            header = {
                "version": 1,
                "roots": self.roots
            }
            header_json = json.dumps(header).encode('utf-8')
            header_length = len(header_json)

            # Write header length and header
            f.write(struct.pack('>I', header_length))
            f.write(header_json)

            # Write blocks
            for cid, data in self.blocks:
                # Write block header (CID + data length)
                cid_bytes = cid.encode('utf-8')
                cid_length = len(cid_bytes)
                data_length = len(data)

                f.write(struct.pack('>I', cid_length))
                f.write(cid_bytes)
                f.write(struct.pack('>I', data_length))
                f.write(data)


def load_contracts(pattern: str) -> List[Tuple[Path, Dict[str, Any]]]:
    """
    Load all Matrix contracts matching the pattern.

    Args:
        pattern: Glob pattern to match contract files

    Returns:
        List of (path, contract_data) tuples
    """
    contracts = []
    contract_paths = glob.glob(pattern, recursive=True)

    for contract_path in sorted(contract_paths):
        path = Path(contract_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contract_data = json.load(f)
            contracts.append((path, contract_data))
        except Exception as e:
            print(f"⚠️ Warning: Failed to load {path}: {e}", file=sys.stderr)

    return contracts


def create_contract_node(contract_path: Path, contract_data: Dict[str, Any]) -> MockIPLDNode:
    """
    Create an IPLD node for a Matrix contract.

    Args:
        contract_path: Path to the contract file
        contract_data: Contract JSON data

    Returns:
        Mock IPLD node
    """
    # Create deterministic hash of contract
    contract_json = json.dumps(contract_data, sort_keys=True, separators=(',', ':'))
    contract_hash = hashlib.sha256(contract_json.encode('utf-8')).hexdigest()

    # Extract key metadata
    module = contract_data.get("module", contract_path.stem.replace("matrix_", ""))
    schema_version = contract_data.get("schema_version", "unknown")

    # Create node data
    node_data = {
        "type": "matrix_contract",
        "path": str(contract_path),
        "module": module,
        "schema_version": schema_version,
        "sha256": contract_hash,
        "timestamp": "2025-09-27T12:00:00.000000Z",
        "size": len(contract_json),
        "v3_sections": []
    }

    # Track which v3 sections are present
    v3_sections = ["tokenization", "glyph_provenance", "dream_provenance",
                   "guardian_check", "biosymbolic_map", "quantum_proof"]

    for section in v3_sections:
        if section in contract_data:
            node_data["v3_sections"].append(section)

    # Add glyph provenance specific data if present
    if "glyph_provenance" in contract_data:
        glyph_data = contract_data["glyph_provenance"]
        node_data["glyph_signature"] = f"sha256:{contract_hash}"
        node_data["entropy_phase"] = glyph_data.get("entropy_phase", "null")
        node_data["drift_index"] = glyph_data.get("drift_index")

    return MockIPLDNode(node_data)


def create_root_node(contract_nodes: List[MockIPLDNode]) -> MockIPLDNode:
    """
    Create the root node linking all contract nodes.

    Args:
        contract_nodes: List of contract IPLD nodes

    Returns:
        Root IPLD node
    """
    # Create summary data
    modules = [node.data["module"] for node in contract_nodes]
    total_size = sum(node.data["size"] for node in contract_nodes)

    # Count v3 adoption
    v3_counts = {}
    for node in contract_nodes:
        for section in node.data["v3_sections"]:
            v3_counts[section] = v3_counts.get(section, 0) + 1

    root_data = {
        "type": "matrix_provenance_root",
        "timestamp": "2025-09-27T12:00:00.000000Z",
        "contracts": {
            "count": len(contract_nodes),
            "modules": sorted(modules),
            "total_size": total_size,
            "contract_links": [node.cid for node in contract_nodes]
        },
        "v3_adoption": v3_counts,
        "schema": {
            "version": "v3.0.0",
            "generator": "lukhas:matrix:provenance:sandbox",
            "format": "ipld-dag-cbor-mock"
        }
    }

    return MockIPLDNode(root_data)


def generate_provenance_report(root_node: MockIPLDNode, contract_nodes: List[MockIPLDNode]) -> Dict[str, Any]:
    """
    Generate a provenance report for external verification.

    Args:
        root_node: The root IPLD node
        contract_nodes: List of contract nodes

    Returns:
        Provenance report dictionary
    """
    return {
        "provenance_version": "v3.0.0",
        "generated": "2025-09-27T12:00:00.000000Z",
        "root_cid": root_node.cid,
        "summary": {
            "total_contracts": len(contract_nodes),
            "total_size": sum(node.data["size"] for node in contract_nodes),
            "v3_sections_present": root_node.data["v3_adoption"]
        },
        "contracts": [
            {
                "module": node.data["module"],
                "cid": node.cid,
                "sha256": node.data["sha256"],
                "v3_sections": node.data["v3_sections"]
            }
            for node in contract_nodes
        ],
        "verification": {
            "car_file": "artifacts/provenance.car",
            "root_cid": root_node.cid,
            "integrity_check": "sha256_verification_available"
        }
    }


def main():
    """Main CLI interface for Matrix provenance generation."""
    parser = argparse.ArgumentParser(
        description="Matrix Provenance CAR Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/matrix_provenance.py --contracts 'contracts/matrix_*.json'
  python3 tools/matrix_provenance.py --contracts '**/matrix_*.json' --output artifacts/full_provenance.car
  python3 tools/matrix_provenance.py --contracts 'contracts/matrix_identity*.json' --verbose
        """
    )

    parser.add_argument(
        "--contracts",
        default="contracts/matrix_*.json",
        help="Glob pattern for Matrix contracts (default: contracts/matrix_*.json)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/provenance.car"),
        help="Output CAR file path (default: artifacts/provenance.car)"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("artifacts/provenance_report.json"),
        help="Output report file path (default: artifacts/provenance_report.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )

    args = parser.parse_args()

    try:
        # Load contracts
        if args.verbose:
            print(f"📂 Loading contracts: {args.contracts}")

        contracts = load_contracts(args.contracts)

        if not contracts:
            print(f"❌ No contracts found matching pattern: {args.contracts}", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"📄 Found {len(contracts)} contracts")

        # Create IPLD nodes for each contract
        contract_nodes = []
        for contract_path, contract_data in contracts:
            node = create_contract_node(contract_path, contract_data)
            contract_nodes.append(node)

            if args.verbose:
                print(f"  📝 {contract_path.name} → {node.cid[:16]}...")

        # Create root node
        root_node = create_root_node(contract_nodes)

        if args.verbose:
            print(f"🌳 Root CID: {root_node.cid}")

        # Create CAR file
        car_file = MockCARFile()
        car_file.set_roots([root_node.cid])

        # Add root node
        car_file.add_block(root_node.cid, root_node.to_cbor_mock())

        # Add contract nodes
        for node in contract_nodes:
            car_file.add_block(node.cid, node.to_cbor_mock())

        # Ensure output directory exists
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)

        # Write CAR file
        car_file.write(args.output)

        # Generate provenance report
        report = generate_provenance_report(root_node, contract_nodes)

        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            f.write('\n')

        if args.verbose:
            print(f"💾 CAR file written: {args.output}")
            print(f"📊 Report written: {args.report}")
            print(f"🔗 Root CID: {root_node.cid}")
        else:
            print(f"✅ Generated provenance CAR with {len(contracts)} contracts → {root_node.cid[:16]}...")

        return 0

    except Exception as e:
        print(f"❌ Error generating provenance: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())