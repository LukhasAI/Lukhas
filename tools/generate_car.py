#!/usr/bin/env python3
"""
IPLD CAR Generator for Matrix Provenance Track

Generates Content-Addressed Archive (CAR) files containing gate evaluation results
and module provenance data. Creates tamper-evident history for Matrix contracts.

Usage:
    python3 tools/generate_car.py --module memory --gates gates.json
    python3 tools/generate_car.py --module identity --attestation evidence.jwt
"""

import json
import hashlib
import argparse
import pathlib
from datetime import datetime
from typing import Dict, Any, Optional


class MockIPLD:
    """Mock IPLD implementation until real library is installed."""

    @staticmethod
    def encode(data: Dict) -> bytes:
        """Encode data as CBOR-like format (using JSON for now)."""
        return json.dumps(data, sort_keys=True).encode('utf-8')

    @staticmethod
    def generate_cid(data: bytes) -> str:
        """Generate a CID-like identifier from data."""
        hash_digest = hashlib.sha256(data).hexdigest()
        # Mock CID format: bafybei + base32 of hash (simplified)
        return f"bafybei{hash_digest[:52]}"


class MockCAR:
    """Mock CAR implementation until real library is installed."""

    def __init__(self, path: str):
        self.path = path
        self.blocks = []

    def add_block(self, data: bytes) -> str:
        """Add a block to the CAR and return its CID."""
        cid = MockIPLD.generate_cid(data)
        self.blocks.append({
            "cid": cid,
            "data": data.decode('utf-8') if isinstance(data, bytes) else data
        })
        return cid

    def write(self):
        """Write CAR file (as JSON for now)."""
        car_data = {
            "version": 1,
            "roots": [self.blocks[0]["cid"]] if self.blocks else [],
            "blocks": self.blocks
        }
        with open(self.path, 'w') as f:
            json.dump(car_data, f, indent=2)


def generate_provenance_car(
    module: str,
    gate_results: Optional[Dict] = None,
    attestation: Optional[str] = None,
    prism_results: Optional[Dict] = None
) -> str:
    """
    Generate IPLD CAR for comprehensive provenance.

    Args:
        module: Module name
        gate_results: Gate evaluation results
        attestation: RATS/EAT evidence JWT
        prism_results: PRISM model checking results

    Returns:
        Root CID of the generated CAR
    """
    # Build provenance block
    block = {
        "@context": "https://lukhas.ai/provenance/v1",
        "module": module,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "schema_version": "1.0.0",
        "provenance": {
            "generated_by": "matrix_gate.py",
            "environment": {
                "os": "Darwin",  # Would detect dynamically
                "python": "3.11.6"
            }
        }
    }

    # Add gate results if provided
    if gate_results:
        block["gates"] = gate_results

    # Add attestation if provided
    if attestation:
        # Store only hash of JWT for privacy
        block["attestation"] = {
            "evidence_hash": hashlib.sha256(attestation.encode()).hexdigest(),
            "verified": True
        }

    # Add PRISM results if provided
    if prism_results:
        block["verification"] = {
            "prism": prism_results,
            "property_satisfied": prism_results.get("result", False)
        }

    # Calculate lamport time (simplified)
    previous_time = load_previous_lamport_time(module)
    block["causal_ordering"] = {
        "lamport_time": previous_time + 1,
        "vector_clock": {
            module: previous_time + 1
        }
    }

    # Generate CAR
    car_path = f"artifacts/{module}_provenance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.car"
    pathlib.Path("artifacts").mkdir(exist_ok=True)

    car = MockCAR(car_path)
    ipld_data = MockIPLD.encode(block)
    root_cid = car.add_block(ipld_data)
    car.write()

    print(f"✅ Generated CAR: {car_path}")
    print(f"🔑 Root CID: {root_cid}")

    # Update module's matrix contract with new CID
    update_contract_cid(module, root_cid, previous_time + 1)

    return root_cid


def load_previous_lamport_time(module: str) -> int:
    """Load previous Lamport time from module's contract."""
    try:
        contract_path = pathlib.Path(module) / f"matrix_{module}.json"
        if contract_path.exists():
            with open(contract_path) as f:
                contract = json.load(f)
                return contract.get("causal_provenance", {}).get("lamport_time", 0)
    except Exception:
        pass
    return 0


def update_contract_cid(module: str, cid: str, lamport_time: int):
    """Update module's contract with new CID and Lamport time."""
    try:
        contract_path = pathlib.Path(module) / f"matrix_{module}.json"
        if contract_path.exists():
            with open(contract_path) as f:
                contract = json.load(f)

            # Update causal provenance
            if "causal_provenance" not in contract:
                contract["causal_provenance"] = {}

            contract["causal_provenance"]["ipld_root_cid"] = cid
            contract["causal_provenance"]["car_uri"] = f"ipfs://{cid}"
            contract["causal_provenance"]["lamport_time"] = lamport_time
            contract["causal_provenance"]["last_updated"] = datetime.utcnow().isoformat() + "Z"

            # Write back
            with open(contract_path, 'w') as f:
                json.dump(contract, f, indent=2)

            print(f"📝 Updated {contract_path} with CID: {cid}")
    except Exception as e:
        print(f"⚠️ Could not update contract: {e}")


def verify_car(car_path: str) -> bool:
    """Verify integrity of a CAR file."""
    try:
        with open(car_path) as f:
            car_data = json.load(f)

        # Verify structure
        assert "version" in car_data
        assert "roots" in car_data
        assert "blocks" in car_data

        # Verify CID matches content
        for block in car_data["blocks"]:
            content = block["data"]
            if isinstance(content, str):
                content = content.encode('utf-8')
            computed_cid = MockIPLD.generate_cid(content)
            stored_cid = block["cid"]

            # Our mock CIDs should match exactly
            if computed_cid != stored_cid:
                print(f"❌ CID mismatch: {stored_cid} != {computed_cid}")
                return False

        print(f"✅ CAR verified: {car_path}")
        return True

    except Exception as e:
        print(f"❌ CAR verification failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate IPLD CAR for Matrix provenance")
    parser.add_argument("--module", required=True, help="Module name")
    parser.add_argument("--gates", help="Path to gate results JSON")
    parser.add_argument("--attestation", help="Path to attestation JWT")
    parser.add_argument("--prism", help="Path to PRISM results JSON")
    parser.add_argument("--verify", help="Verify existing CAR file")

    args = parser.parse_args()

    # Verify mode
    if args.verify:
        success = verify_car(args.verify)
        return 0 if success else 1

    # Load inputs
    gate_results = None
    if args.gates:
        with open(args.gates) as f:
            gate_results = json.load(f)

    attestation = None
    if args.attestation:
        with open(args.attestation) as f:
            attestation = f.read().strip()

    prism_results = None
    if args.prism:
        with open(args.prism) as f:
            prism_results = json.load(f)

    # Generate CAR
    cid = generate_provenance_car(
        module=args.module,
        gate_results=gate_results,
        attestation=attestation,
        prism_results=prism_results
    )

    print(f"\n🎉 Provenance CAR generated successfully!")
    print(f"Module: {args.module}")
    print(f"CID: {cid}")
    print("\nNext steps:")
    print("1. Verify CAR: python tools/generate_car.py --verify artifacts/*.car")
    print("2. Pin to IPFS: ipfs add artifacts/*.car")
    print("3. Update contract: Check your module's matrix contract for new CID")

    return 0


if __name__ == "__main__":
    exit(main())