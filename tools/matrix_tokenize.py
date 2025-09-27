#!/usr/bin/env python3
"""
Matrix Tokenization Sandbox

Creates mock blockchain anchors for Matrix contracts with deterministic
transaction IDs and timestamps. Provides the foundation for future
real Solana/EVM integration while maintaining safe sandbox defaults.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def hash_contract(contract_data: Dict[str, Any]) -> str:
    """
    Generate deterministic SHA256 hash of contract data.

    Args:
        contract_data: The contract JSON data

    Returns:
        Hexadecimal SHA256 hash string
    """
    # Create deterministic JSON string (sorted keys, no whitespace)
    contract_json = json.dumps(contract_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(contract_json.encode('utf-8')).hexdigest()


def generate_mock_txid(contract_hash: str, network: str = "solana") -> str:
    """
    Generate deterministic mock transaction ID.

    Args:
        contract_hash: SHA256 hash of the contract
        network: Target network (solana, ethereum, etc.)

    Returns:
        Mock transaction ID string
    """
    network_prefixes = {
        "solana": "SOLANA_MOCK_",
        "ethereum": "ETH_MOCK_",
        "polygon": "MATIC_MOCK_",
        "base": "BASE_MOCK_",
        "arbitrum": "ARB_MOCK_"
    }

    prefix = network_prefixes.get(network.lower(), "MOCK_")
    return f"{prefix}{contract_hash[:8].upper()}"


def generate_mock_block_info(contract_hash: str, network: str = "solana") -> Dict[str, Any]:
    """
    Generate deterministic mock block information.

    Args:
        contract_hash: SHA256 hash of the contract
        network: Target network

    Returns:
        Dictionary with mock block information
    """
    # Use hash to deterministically generate block info
    hash_int = int(contract_hash[:8], 16)

    if network.lower() == "solana":
        return {
            "slot": 200000000 + (hash_int % 1000000),  # Mock Solana slot
            "blockhash": f"MOCK_BLOCK_{contract_hash[:16].upper()}"
        }
    else:
        return {
            "block_number": 18000000 + (hash_int % 1000000),  # Mock EVM block
            "block_hash": f"0xMOCK{contract_hash[:56]}"
        }


def create_anchor_artifact(
    contract_path: Path,
    contract_data: Dict[str, Any],
    network: str = "solana",
    devnet: bool = True
) -> Dict[str, Any]:
    """
    Create tokenization anchor artifact for a Matrix contract.

    Args:
        contract_path: Path to the contract file
        contract_data: The contract JSON data
        network: Target blockchain network
        devnet: Whether to use devnet/testnet (True) or mainnet (False)

    Returns:
        Anchor artifact dictionary
    """
    contract_hash = hash_contract(contract_data)
    txid = generate_mock_txid(contract_hash, network)
    block_info = generate_mock_block_info(contract_hash, network)

    # Network suffix for devnet/testnet
    network_name = network.lower()
    if devnet:
        network_name += "-devnet" if network.lower() == "solana" else "-testnet"
    else:
        network_name += "-mainnet"

    # Extract module name from contract
    module_name = contract_data.get("module", contract_path.stem.replace("matrix_", ""))

    artifact = {
        "contract": contract_path.name,
        "module": module_name,
        "sha256": contract_hash,
        "txid": txid,
        "network": network_name,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "anchor_type": "mock_sandbox",
        "block_info": block_info,
        "tokenization": {
            "enabled": True,
            "standard": f"{network.lower()}:mock-anchor",
            "anchor_txid": txid,
            "anchor_digest": f"sha256:{contract_hash}",
            "issuer": "lukhas:matrix:sandbox",
            "policy_version": "v3.0.0",
            "note": f"Mock {network} anchor for sandbox validation"
        }
    }

    return artifact


def main():
    """Main CLI interface for Matrix tokenization."""
    parser = argparse.ArgumentParser(
        description="Matrix Tokenization Sandbox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/matrix_tokenize.py --contract contracts/matrix_memoria.json
  python3 tools/matrix_tokenize.py --contract contracts/matrix_identity.json --network ethereum
  python3 tools/matrix_tokenize.py --contract contracts/matrix_governance.json --output artifacts/gov_anchor.json
        """
    )

    parser.add_argument(
        "--contract",
        type=Path,
        required=True,
        help="Path to the Matrix contract to tokenize"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/token_anchor.json"),
        help="Output path for anchor artifact (default: artifacts/token_anchor.json)"
    )
    parser.add_argument(
        "--network",
        choices=["solana", "ethereum", "polygon", "base", "arbitrum"],
        default="solana",
        help="Target blockchain network (default: solana)"
    )
    parser.add_argument(
        "--mainnet",
        action="store_true",
        help="Use mainnet instead of devnet/testnet"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )

    args = parser.parse_args()

    # Validate contract file exists
    if not args.contract.exists():
        print(f"❌ Contract file not found: {args.contract}", file=sys.stderr)
        return 1

    try:
        # Load contract
        with open(args.contract, 'r', encoding='utf-8') as f:
            contract_data = json.load(f)

        if args.verbose:
            print(f"📄 Loading contract: {args.contract}")
            print(f"🌐 Target network: {args.network}")
            print(f"🔧 Mode: {'mainnet' if args.mainnet else 'devnet/testnet'}")

        # Create anchor artifact
        artifact = create_anchor_artifact(
            args.contract,
            contract_data,
            args.network,
            devnet=not args.mainnet
        )

        # Ensure output directory exists
        args.output.parent.mkdir(parents=True, exist_ok=True)

        # Write artifact
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2)
            f.write('\n')

        if args.verbose:
            print(f"🔗 Generated anchor: {artifact['txid']}")
            print(f"📝 Contract hash: {artifact['sha256'][:16]}...")
            print(f"💾 Output written: {args.output}")
        else:
            print(f"✅ Tokenized {args.contract.name} → {artifact['txid']}")

        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in contract file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error tokenizing contract: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())