#!/usr/bin/env python3
"""
Generate module manifests (+ optional lukhas_context.md)
from docs/audits/COMPLETE_MODULE_INVENTORY.json

Usage:
  python scripts/generate_module_manifests.py \
    --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
    --out manifests \
    --schema schemas/matriz_module_compliance.schema.json \
    --star-canon scripts/star_canon.json \
    --write-context
"""
import argparse, json, os, re, sys, pathlib, datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

STAR_DEFAULT = "Supporting"

# Test discovery patterns
TEST_GLOBS = [
    "tests/test_*.py",
    "tests/**/*_test.py",
    "tests/**/test_*.py",
    "**/test_*.py",
]

STAR_HINTS = [
    (r"/consciousness/|/awareness/|/dream/|/oneiric/|/creativity/", "🌊 Flow (Consciousness)"),
    (r"/memory/|/rag/|/embeddings/|/kg/", "✦ Trail (Memory)"),
    (r"/oidc/|/auth/|/identity/|/tenancy/", "⚛️ Anchor (Identity)"),
    (r"/guardian|/ethic", "🛡️ Watch (Guardian)"),  # bias to Watch; refine manually for North if policy-only
    (r"/vision/|/visualization/|/dashboard/|/ui/", "🔬 Horizon (Vision)"),
    (r"/bio/", "🌱 Living (Bio)"),
    (r"/quantum_|/qi_", "🔮 Oracle (Quantum)")
]

COLONY_HINTS = [
    (r"/api/|/bridge/", "actuation"),
    (r"/consciousness/|/dream|/planning|/simulation", "simulation"),
    (r"/memory/|/rag/|/embedding|/kg/", "memory"),
    (r"/ethic|/guardian", "ethics"),
    (r"/vision|/ui|/dashboard|/visualization", "interface"),
    (r"/perception|/asr|/vision_model", "perception"),
]

def validate_star(star: str, star_canon: Dict[str, Any]) -> str:
    """Hard gate: refuse invalid stars, fail fast."""
    stars = set(star_canon.get("stars", []))
    if star not in stars:
        print(f"❌ FATAL: Invalid star '{star}' not in canon: {stars}", file=sys.stderr)
        print(f"💡 Update star_canon.json or fix star inference heuristics", file=sys.stderr)
        sys.exit(1)
    return star


def guess_star(path: str, inv_star: Optional[str], star_canon: Dict[str, Any]) -> str:
    aliases = star_canon.get("aliases", {})
    stars = set(star_canon.get("stars", []))
    # Inventory-proposed star (normalize via aliases)
    if inv_star:
        norm = aliases.get(inv_star, inv_star)
        if norm in stars:
            return validate_star(norm, star_canon)
    # Heuristics from path
    for pattern, star in STAR_HINTS:
        if re.search(pattern, path):
            return validate_star(star, star_canon)
    return validate_star(STAR_DEFAULT, star_canon)

def guess_colony(path: str) -> Optional[str]:
    for pattern, colony in COLONY_HINTS:
        if re.search(pattern, path):
            return colony
    if "/api/" in path:
        return "actuation"
    return None


def infer_capabilities(path: str, star: str, matriz_node: str, module_name: str) -> List[Dict[str, Any]]:
    """
    Infer capabilities from module path, star, and MATRIZ node.
    Returns at least one capability to satisfy schema minItems: 1.
    """
    capabilities = []

    # Map MATRIZ nodes to capability descriptions (name, type, description)
    node_caps = {
        "memory": ("memory_management", "storage", "Provides memory storage, retrieval, and context management"),
        "attention": ("attention_routing", "orchestration", "Routes and prioritizes cognitive attention"),
        "thought": ("cognitive_processing", "processing", "Performs reasoning, analysis, and decision-making"),
        "risk": ("risk_assessment", "processing", "Evaluates risks and safety constraints"),
        "intent": ("intent_interpretation", "processing", "Interprets and validates user intentions"),
        "action": ("action_execution", "orchestration", "Executes actions and effects in the system"),
        "supporting": ("infrastructure_support", "utility", "Provides foundational utilities and infrastructure"),
    }

    # Star-based capability hints (name, type, description)
    star_caps = {
        "⚛️ Anchor (Identity)": ("identity_management", "authentication", "Manages authentication, authorization, and identity"),
        "✦ Trail (Memory)": ("memory_persistence", "storage", "Provides persistent memory and recall"),
        "🔬 Horizon (Vision)": ("perception_processing", "processing", "Processes visual and perceptual inputs"),
        "🌱 Living (Bio)": ("bio_adaptation", "processing", "Implements bio-inspired adaptive behaviors"),
        "🌙 Drift (Dream)": ("creative_synthesis", "processing", "Generates creative outputs and novel patterns"),
        "⚖️ North (Ethics)": ("ethical_reasoning", "processing", "Applies ethical reasoning and value alignment"),
        "🛡️ Watch (Guardian)": ("policy_enforcement", "monitoring", "Enforces policies and constitutional constraints"),
        "🔮 Oracle (Quantum)": ("quantum_processing", "processing", "Applies quantum-inspired algorithms and patterns"),
        "🌊 Flow (Consciousness)": ("consciousness_integration", "orchestration", "Integrates consciousness-aware patterns"),
    }

    # Primary capability from MATRIZ node
    if matriz_node in node_caps:
        name, cap_type, desc = node_caps[matriz_node]
        capabilities.append({
            "name": name,
            "type": cap_type,
            "description": desc,
            "interfaces": []
        })

    # Secondary capability from star (if different from Supporting)
    if star in star_caps and star != "Supporting":
        name, cap_type, desc = star_caps[star]
        # Only add if not duplicate
        if not any(c["name"] == name for c in capabilities):
            capabilities.append({
                "name": name,
                "type": cap_type,
                "description": desc,
                "interfaces": []
            })

    # Path-specific capabilities
    if "/api/" in path or "/bridge/" in path:
        capabilities.append({
            "name": "api_interface",
            "type": "api",
            "description": "Exposes external API endpoints",
            "interfaces": ["REST", "HTTP"]
        })

    if "/oauth" in path or "/oidc" in path or "/auth" in path:
        capabilities.append({
            "name": "authentication",
            "type": "authentication",
            "description": "Handles authentication flows",
            "interfaces": ["OAuth2", "OIDC"]
        })

    # Ensure at least one capability (schema requirement)
    if not capabilities:
        capabilities.append({
            "name": "core_functionality",
            "type": "utility",
            "description": f"TODO: Document {module_name} capabilities",
            "interfaces": []
        })

    return capabilities

def map_priority_to_quality_tier(priority: str) -> str:
    """Base tier from priority (before gating)."""
    p = (priority or "").lower()
    if p == "critical":
        return "T1_critical"
    if p == "high":
        return "T2_important"
    if p == "medium":
        return "T3_standard"
    return "T4_experimental"


def decide_quality_tier(priority: Optional[str], has_tests: bool, owner: Optional[str]) -> str:
    """
    Gated tiering: T1 requires tests + owner.
    Demote to T2/T3 if requirements not met.
    """
    base = map_priority_to_quality_tier(priority or "")

    # Gate: T1 requires both tests and owner
    if base == "T1_critical":
        if not has_tests or not owner or owner == "unassigned":
            return "T2_important" if owner and owner != "unassigned" else "T3_standard"

    return base

def discover_tests(module_fs_path: str) -> List[str]:
    """
    Given a module directory path (relative to repo root), return normalized test paths.
    We look:
      - module_dir/tests/...
      - tests/<module_rel_path>/...
      - sibling/ancestor tests matching test_*.py
    """
    if not module_fs_path:
        return []

    root = ROOT.resolve()
    mod = (root / module_fs_path).resolve()
    found = set()

    # 1) module-local tests
    for pat in TEST_GLOBS:
        try:
            for p in mod.glob(pat):
                if p.is_file():
                    found.add(str(p.relative_to(root)))
        except (OSError, ValueError):
            pass

    # 2) repo tests mirrored by path: tests/<module_rel_path>/
    try:
        mirror = root / "tests" / module_fs_path
        if mirror.exists():
            for pat in ["test_*.py", "**/test_*.py", "*_test.py", "**/*_test.py"]:
                for p in mirror.glob(pat):
                    if p.is_file():
                        found.add(str(p.relative_to(root)))
    except (OSError, ValueError):
        pass

    # 3) last resort: nearby sibling tests in parent
    try:
        if mod.exists() and mod.parent.exists():
            for p in mod.parent.glob("test_*.py"):
                if p.is_file():
                    found.add(str(p.relative_to(root)))
    except (OSError, ValueError):
        pass

    return sorted(found)


def build_testing_block(module_fs_path: str, tier: Optional[str] = None) -> Dict[str, Any]:
    """Emit schema-compliant testing block."""
    paths = discover_tests(module_fs_path)
    has_tests = bool(paths)

    testing: Dict[str, Any] = {
        "has_tests": has_tests,
        "quality_tier": tier or "T4_experimental"
    }

    # T1/T2 modules MUST include test_paths (schema allOf constraint)
    # For has_tests=false, include empty array to satisfy schema
    if tier in {"T1_critical", "T2_important"}:
        testing["test_paths"] = paths if has_tests else []
        if has_tests:
            testing["coverage_baseline"] = 50
    elif has_tests and paths:
        # T3/T4: only include test_paths when non-empty
        testing["test_paths"] = paths

    return testing

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def make_context_md(fqn: str, star: str, pipeline_nodes: List[str], colony: Optional[str], exports=None, contracts=None, logger=None) -> str:
    pn = ", ".join(pipeline_nodes or [])
    return f"""# {fqn}

**Star**: {star}
**MATRIZ Nodes**: {pn}
**Colony**: {colony or "-"}

## What it does
_TODO: short description (2–3 sentences). Add links to demos, notebooks, or dashboards._

## Contracts
- **Publishes**: _e.g., `topic.name@v1`_
- **Subscribes**: _e.g., `topic.other@v1`_
- **Exports**: _e.g., `ClassName`, `function_name()`_

## Observability
- **Spans**: _otlp-span-name_
- **Metrics**: _counter.foo, histogram.bar_
- **Logging**: `{logger or fqn}: INFO`

## Security
- **Auth**: _OIDC|Token|None_
- **Data classification**: _public|internal|restricted|sensitive_
- **Policies**: _Guardian/North policy refs_

## Tests
- _Add paths under_ `tests/…`
- Coverage target (tier-driven): T1≥70% • T2≥50% • T3≥30% • T4=n/a
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="docs/audits/COMPLETE_MODULE_INVENTORY.json")
    ap.add_argument("--out", default="manifests")
    ap.add_argument("--schema", default=None)
    ap.add_argument("--star-canon", default=str(HERE / "star_canon.json"))
    ap.add_argument("--write-context", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    inv = json.load(open(args.inventory, "r", encoding="utf-8"))
    star_canon = json.load(open(args.star_canon, "r", encoding="utf-8"))

    items = inv.get("inventory", [])
    if args.limit:
        items = items[:args.limit]

    total = 0
    wrote = 0
    for it in items:
        total += 1
        module_name = it.get("module_name")
        path = it.get("path")  # repo-relative
        lane = it.get("lane")
        inv_star = it.get("constellation_star")
        matriz_node = (it.get("matriz_node") or "supporting").lower()
        priority = it.get("priority") or "low"

        star = guess_star("/"+(path or ""), inv_star, star_canon)
        colony = guess_colony("/"+(path or ""))

        # Discover tests first (needed for gated tiering)
        test_paths = discover_tests(path or "")
        has_tests = bool(test_paths)

        # Owner from inventory (will be used for tier gating and metadata)
        owner = it.get("owner", "unassigned")

        # Gated tiering: T1 requires tests + owner
        quality_tier = decide_quality_tier(priority, has_tests, owner)

        capabilities = infer_capabilities(path or "", star, matriz_node, module_name or "")

        module_obj = {
            "name": module_name,
            "path": path,
            "type": it.get("type", "package"),
            "lane": lane  # legacy, allowed but deprecated
        }
        if colony:
            module_obj["colony"] = colony

        manifest = {
            "schema_version": "1.1.0",
            "module": module_obj,
            "matriz_integration": {
                "status": "partial",
                "pipeline_nodes": [matriz_node],
                "cognitive_function": ""
            },
            "constellation_alignment": {
                "primary_star": star,
                "star_aliases": [],
                "trinity_aspects": []
            },
            "capabilities": capabilities,
            "dependencies": {"internal": [], "external": [], "circular_dependencies": []},
            "exports": {"classes": [], "functions": [], "constants": []},
            "testing": build_testing_block(path or "", quality_tier),
            "observability": {
                "spans": [],
                "metrics": [],
                "logging": {"logger_name": (module_name or path or "").replace("/", ".") or "lukhas", "default_level": "INFO"},
                "events": {"publishes": [], "subscribes": []}
            },
            "security": {
                "requires_auth": False,
                "data_classification": "internal",
                "secrets_used": [],
                "network_calls": False,
                "sandboxed": True,
                "policies": []
            },
            "metadata": {
                "created": now_iso(),
                "last_updated": now_iso(),
                "manifest_generated": True,
                "owner": "unassigned",
                "documentation_url": "",
                "tags": []
            }
        }

        out_dir = ROOT / args.out / (path or module_name or "unknown")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "module.manifest.json"
        out_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        wrote += 1

        if args.write_context:
            ctx = make_context_md(module_name or path, star, manifest["matriz_integration"]["pipeline_nodes"], colony,
                                  exports=None, contracts=None, logger=manifest["observability"]["logging"]["logger_name"])
            (out_dir / "lukhas_context.md").write_text(ctx, encoding="utf-8")

    print(f"DONE: wrote {wrote}/{total} manifests to {args.out}")

if __name__ == "__main__":
    main()
