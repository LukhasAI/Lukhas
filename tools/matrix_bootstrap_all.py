#!/usr/bin/env python3
"""
Matrix Contracts Bootstrap Generator

Discovers all Python modules under lukhas/ and generates schema-compliant
matrix_<module>.json contracts with intelligent defaults based on module type.

Features:
- Module discovery via __init__.py scanning
- Public API extraction from __all__ or function definitions
- Smart tier assignment based on module path
- Complete schema-compliant contract generation
- Safe overwrite protection with dry-run by default
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Repository structure
ROOT = Path(__file__).resolve().parents[1]  # repo root
SRC = ROOT / "lukhas"

# ΛiD tier system (canonical mapping)
TIERS = ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]
TIER_MAP_NUM = {tier: i for i, tier in enumerate(TIERS)}

# Module type to tier mapping (intelligent defaults)
MODULE_TIER_MAPPING = {
    "core": "inner_circle",        # Core system components
    "governance": "inner_circle",   # Governance and Guardian System
    "security": "inner_circle",     # Security-critical modules
    "identity": "trusted",          # Identity management
    "consciousness": "inner_circle", # Consciousness core
    "bridge": "friend",            # External integrations
    "adapters": "friend",          # Adapter modules
    "api": "trusted",              # API modules
    "orchestration": "trusted",    # Orchestration layer
    "memory": "trusted",           # Memory systems
    "observability": "trusted",    # Monitoring and telemetry
    "deployment": "friend",        # Deployment utilities
    "tools": "friend",             # Development tools
    "branding": "visitor",         # UI/branding components
    "accepted": "friend",          # Accepted modules
}

def discover_modules() -> list[tuple[str, Path]]:
    """Discover all Python modules under lukhas/ with __init__.py files."""
    modules = []

    for init_file in SRC.rglob("__init__.py"):
        pkg_dir = init_file.parent
        # Convert path to Python module name
        relative_path = pkg_dir.relative_to(SRC)
        pkg_name = ".".join(relative_path.parts) if relative_path.parts else "lukhas"

        # Skip if this is just the root lukhas package
        if pkg_name == "lukhas":
            pkg_name = "root"

        modules.append((pkg_name, pkg_dir))

    return sorted(modules)

def extract_public_api(pkg_dir: Path) -> list[dict[str, str]]:
    """Extract public API from package __init__.py file."""
    init_file = pkg_dir / "__init__.py"
    if not init_file.exists():
        return []

    try:
        content = init_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    api = []

    # Try to parse __all__ first
    all_match = re.search(r"__all__\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if all_match:
        # Extract items from __all__ list
        all_content = all_match.group(1)
        names = []
        for item in re.findall(r'["\']([^"\']+)["\']', all_content):
            names.append(item.strip())

        for name in names:
            api.append({
                "fn": name,
                "stability": "stable" if "_" not in name else "experimental",
                "doc": f"Public API: {name}"
            })

    # If no __all__, try to find top-level function definitions
    if not api:
        func_matches = re.findall(r"^def\s+([a-zA-Z_]\w*)\s*\(", content, re.MULTILINE)
        for func_name in func_matches:
            if not func_name.startswith("_"):  # Skip private functions
                api.append({
                    "fn": f"{func_name}()",
                    "stability": "experimental",
                    "doc": f"Function: {func_name}"
                })

    # If still no API found, try to find class definitions
    if not api:
        class_matches = re.findall(r"^class\s+([a-zA-Z_]\w*)", content, re.MULTILINE)
        for class_name in class_matches:
            if not class_name.startswith("_"):  # Skip private classes
                api.append({
                    "fn": class_name,
                    "stability": "experimental",
                    "doc": f"Class: {class_name}"
                })

    return api[:10]  # Limit to first 10 items to keep contracts manageable

def determine_module_tier(pkg_name: str) -> str:
    """Determine appropriate ΛiD tier for module based on path and type."""
    # Check for specific patterns in module path
    path_parts = pkg_name.split(".")

    for part in path_parts:
        if part in MODULE_TIER_MAPPING:
            return MODULE_TIER_MAPPING[part]

    # Special cases
    if "auth" in pkg_name or "identity" in pkg_name:
        return "trusted"
    if "test" in pkg_name or "example" in pkg_name:
        return "friend"
    if "internal" in pkg_name or "private" in pkg_name:
        return "inner_circle"

    # Default tier
    return "trusted"

def default_gates(pkg_name: str) -> list[dict[str, Any]]:
    """Generate baseline gates for module."""
    gates = [
        {"metric": "security.osv_high", "op": "==", "value": 0},
        {"metric": "symbolic.DriftScore", "op": ">=", "value": 0.010},
        {"metric": "attestation.rats_verified", "op": "==", "value": 1},
    ]

    # Add performance gates based on module type
    if "core" in pkg_name or "consciousness" in pkg_name:
        gates.append({"metric": "latency.runtime_s_10k", "op": "<=", "value": 10})
    elif "api" in pkg_name or "orchestration" in pkg_name:
        gates.append({"metric": "latency.runtime_s_1k", "op": "<=", "value": 5})
    else:
        gates.append({"metric": "latency.runtime_s_1k", "op": "<=", "value": 15})

    return gates

def telemetry_stub(pkg_name: str, semconv: str) -> dict[str, Any]:
    """Generate OpenTelemetry telemetry configuration."""
    simple_name = pkg_name.split(".")[-1] if "." in pkg_name else pkg_name

    return {
        "opentelemetry_semconv_version": semconv,
        "spans": [
            {
                "name": f"{simple_name}.operation",
                "attrs": ["code.function", "module", f"lukhas.{simple_name}.operation"]
            }
        ],
        "metrics": [
            {
                "name": f"lukhas.{simple_name}.latency",
                "unit": "s",
                "type": "histogram"
            },
            {
                "name": f"lukhas.{simple_name}.operations",
                "unit": "1",
                "type": "counter"
            }
        ]
    }

def identity_stub(pkg_name: str, default_tier: str) -> dict[str, Any]:
    """Generate ΛiD identity configuration for module."""
    tier = determine_module_tier(pkg_name)
    tier_num = TIER_MAP_NUM.get(tier, TIER_MAP_NUM.get(default_tier, 3))

    # Build required tiers list (current tier and above)
    required_tiers = TIERS[tier_num:]
    required_tiers_numeric = list(range(tier_num, len(TIERS)))

    simple_name = pkg_name.split(".")[-1] if "." in pkg_name else pkg_name

    # Generate appropriate scopes
    scopes = [f"{simple_name}.read"]

    # Add write scope for most modules
    if simple_name not in ["branding", "tools", "observability"]:
        scopes.append(f"{simple_name}.write")

    # Add admin scope for core/governance modules
    if tier_num >= 4:  # inner_circle and above
        scopes.append(f"{simple_name}.admin")

    # Determine accepted subjects
    accepted_subjects = ["lukhas:user:*"]

    # Add service accounts for system modules
    if tier_num >= 3:  # trusted and above
        accepted_subjects.append("lukhas:svc:orchestrator")

    # Core modules accept more service accounts
    if tier_num >= 4:
        accepted_subjects.extend(["lukhas:svc:guardian", "lukhas:svc:consciousness"])

    return {
        "requires_auth": True,
        "accepted_subjects": accepted_subjects,
        "required_tiers": required_tiers,
        "required_tiers_numeric": required_tiers_numeric,
        "scopes": scopes,
        "webauthn_required": tier_num >= 4,  # Require WebAuthn for sensitive modules
        "api_policies": []
    }

def base_contract(
    pkg_name: str,
    team: str,
    codeowners: list[str],
    api: list[dict[str, str]],
    semconv: str,
    default_tier: str
) -> dict[str, Any]:
    """Generate complete Matrix contract for module."""
    simple_name = pkg_name.split(".")[-1] if "." in pkg_name else pkg_name

    # Generate unique event ID
    event_id = f"urn:uuid:{hashlib.md5(pkg_name.encode()).hexdigest()[:8]}-" + \
               f"{hashlib.md5(pkg_name.encode()).hexdigest()[8:12]}-" + \
               f"{hashlib.md5(pkg_name.encode()).hexdigest()[12:16]}-" + \
               f"{hashlib.md5(pkg_name.encode()).hexdigest()[16:20]}-" + \
               f"{hashlib.md5(pkg_name.encode()).hexdigest()[20:32]}"

    return {
        "schema_version": "1.0.0",
        "module": pkg_name,
        "owner": {
            "team": team,
            "codeowners": codeowners
        },
        "interface": {
            "public_api": api,
            "contracts": [
                {
                    "name": "module_initialization",
                    "type": "postcondition",
                    "desc": "Module initializes without errors"
                }
            ]
        },
        "params": {
            "log_level": {"type": "string", "default": "INFO", "enum": ["DEBUG", "INFO", "WARN", "ERROR"]},
            "enable_telemetry": {"type": "bool", "default": True}
        },
        "gates": default_gates(pkg_name),
        "telemetry": telemetry_stub(pkg_name, semconv),
        "symbolic_diagnostics": {
            "CollapseHash": "sha256:pending",
            "DriftScore": 0.010,
            "EthicalDriftIndex": 0.0,
            "ConvergencePct": 0.0
        },
        "lineage": {
            "openlineage_event_id": event_id,
            "datasets_in": [],
            "datasets_out": [],
            "job": f"lukhas.{simple_name}.pipeline"
        },
        "provenance": {
            "@context": "https://www.w3.org/ns/prov.jsonld",
            "commit": "pending",
            "branch": "main",
            "built_by": {"prov:agent": "matrix_bootstrap_all.py"},
            "environment": {
                "os": "pending",
                "cpu": "pending",
                "python": "3.11+"
            },
            "config_fingerprint": "sha256:pending"
        },
        "causal_provenance": {
            "ipld_root_cid": "bafybeipending",
            "car_uri": f"ipfs://pending/{simple_name}.car",
            "lamport_time": 0,
            "vector_clock": {simple_name: 0, "consciousness": 0, "identity": 0},
            "bft": {"algorithm": "hotstuff", "view": 0, "qc_hash": "0x0000000000000000"},
            "crdt": {"type": "or-set", "last_join_cid": "bafybeipending"}
        },
        "formal": {
            "tla_plus": {
                "spec": f"specs/{simple_name}/module.tla",
                "result": "UNKNOWN"
            },
            "proofs": [],
            "probabilistic": {
                "tool": "prism",
                "model": f"models/{simple_name}/behavior.pm",
                "properties": ["P>=0.99 [F \"module_ready\"]"]
            }
        },
        "privacy": {
            "epsilon": 0.0,
            "delta": 0.0,
            "mechanism": "gaussian",
            "composition": "basic"
        },
        "attestation": {
            "rats": {
                "evidence_jwt": "pending",
                "verifier_policy": "rats/policy-v2.1.json"
            },
            "tee": [],
            "ebpf": {
                "program_id": "sha256:pending",
                "policy": f"opa://policies/{simple_name}.rego"
            }
        },
        "crypto": {
            "pqc": {
                "signatures": ["ML-DSA-65"],
                "kem": "ML-KEM-1024",
                "hash": "SHA3-512"
            }
        },
        "verifiable_claims": {
            "zk": {
                "scheme": "groth16",
                "circuit_cid": None,
                "proof_uri": None,
                "vk_uri": None,
                "setup": {"pot_round": None, "ref": None}
            },
            "mpc": {
                "protocol": "spdz",
                "threshold": "2/3",
                "participants": 3
            }
        },
        "capabilities": {
            "macaroons": [],
            "policy_engine": "opa",
            "policy_packages": [f"matrix.{simple_name}"]
        },
        "experiments": {
            "mlflow_tracking_uri": "mlflow://lukhas",
            "last_run_id": None,
            "dvc_metrics_ref": f"../dvc_metrics/{simple_name}.json"
        },
        "energy": {
            "tool": "codecarbon",
            "last_kwh_10k": None,
            "last_emissions_kg": None,
            "location": "US-CA",
            "artifact": f"../artifacts/{simple_name}_emissions.csv"
        },
        "supply_chain": {
            "sbom_ref": f"../sbom/{simple_name}.cdx.json",
            "licenses": ["Apache-2.0"],
            "sarif_report": f"../artifacts/{simple_name}.sarif.json",
            "osv_snapshot": f"../artifacts/{simple_name}.osv.json",
            "attestations": [
                {
                    "type": "slsa.provenance",
                    "uri": f"oci://registry/lukhas/{simple_name}@sha256:pending"
                }
            ]
        },
        "tokenization": {
            "enabled": False,
            "network": "solana",
            "standard": "solana:compressed-nft",
            "mint_address": None,
            "token_id": None,
            "anchor_txid": None,
            "anchor_block": None,
            "anchor_digest": None,
            "anchor_merkle_root": None,
            "issuer": None,
            "policy_version": None,
            "proof_uri": None,
            "note": None
        },
        "identity": identity_stub(pkg_name, default_tier),
        "docs": {
            "lens_markdown": f"../products/intelligence/lens/{simple_name}.qmd",
            "design_notes": f"../docs/{simple_name}/architecture.md"
        }
    }

def write_contract(pkg_dir: Path, pkg_name: str, data: dict[str, Any], overwrite: bool = False) -> bool:
    """Write Matrix contract to appropriate file location."""
    simple_name = pkg_name.split(".")[-1] if "." in pkg_name else pkg_name
    out_file = pkg_dir / f"matrix_{simple_name}.json"

    if out_file.exists() and not overwrite:
        print(f"SKIP (exists): {out_file}")
        return False

    try:
        out_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE: {out_file}")
        return True
    except OSError as e:
        print(f"ERROR writing {out_file}: {e}")
        return False

def main():
    """Main CLI for Matrix contract bootstrap generator."""
    parser = argparse.ArgumentParser(
        description="Bootstrap Matrix contracts for all LUKHAS modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run discovery
  python3 tools/matrix_bootstrap_all.py

  # Generate contracts (skip existing)
  python3 tools/matrix_bootstrap_all.py --write

  # Force overwrite existing contracts
  python3 tools/matrix_bootstrap_all.py --write --overwrite

  # Generate for specific modules only
  python3 tools/matrix_bootstrap_all.py --write --modules "governance,identity,consciousness"
        """
    )

    parser.add_argument("--write", action="store_true",
                       help="Actually write contract files (default: dry-run)")
    parser.add_argument("--overwrite", action="store_true",
                       help="Force overwrite existing contracts")
    parser.add_argument("--modules", type=str, default="",
                       help="Comma-separated list of modules to process (default: all)")
    parser.add_argument("--owner-team", type=str, default="Core",
                       help="Default team ownership")
    parser.add_argument("--codeowners", type=str, default="@gonzo.dominguez,@lukhas-core",
                       help="Comma-separated GitHub codeowners")
    parser.add_argument("--semconv", type=str, default="1.37.0",
                       help="OpenTelemetry semantic conventions version")
    parser.add_argument("--identity-default-tier", type=str, default="trusted",
                       choices=TIERS, help="Default ΛiD tier requirement")

    args = parser.parse_args()

    # Parse requested modules
    requested = set()
    if args.modules:
        requested = {m.strip() for m in args.modules.split(",") if m.strip()}

    # Parse codeowners
    codeowners = [s.strip() for s in args.codeowners.split(",") if s.strip()]

    print(f"🔍 Discovering modules under {SRC}...")
    modules = discover_modules()

    print(f"📦 Found {len(modules)} modules")
    if not args.write:
        print("🧪 DRY-RUN MODE (use --write to generate files)")

    written_count = 0
    skipped_count = 0

    for pkg_name, pkg_dir in modules:
        # Skip if specific modules requested and this isn't one
        if requested and pkg_name not in requested:
            continue

        print(f"\n📋 Processing module: {pkg_name}")

        # Extract public API
        api = extract_public_api(pkg_dir)
        print(f"   API functions: {len(api)}")

        # Generate contract
        contract_data = base_contract(
            pkg_name, args.owner_team, codeowners, api,
            args.semconv, args.identity_default_tier
        )

        # Determine tier assignment
        tier = determine_module_tier(pkg_name)
        print(f"   ΛiD tier: {tier} ({TIER_MAP_NUM[tier]})")

        if args.write:
            success = write_contract(pkg_dir, pkg_name, contract_data, args.overwrite)
            if success:
                written_count += 1
            else:
                skipped_count += 1
        else:
            simple_name = pkg_name.split(".")[-1] if "." in pkg_name else pkg_name
            contract_path = pkg_dir / f"matrix_{simple_name}.json"
            print(f"   Would write: {contract_path}")

    # Summary
    print("\n📊 Summary:")
    if args.write:
        print(f"   ✅ Contracts written: {written_count}")
        print(f"   ⏭️  Contracts skipped: {skipped_count}")
        print(f"   📂 Total processed: {written_count + skipped_count}")
    else:
        processed = len([m for m in modules if not requested or m[0] in requested])
        print(f"   📦 Modules discovered: {processed}")
        print("   💡 Use --write to generate contracts")

    return 0

if __name__ == "__main__":
    sys.exit(main())
