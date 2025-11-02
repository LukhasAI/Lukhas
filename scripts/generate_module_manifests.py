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
import argparse
import datetime
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional

from star_canon_utils import extract_canon_labels, normalize_star_label

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

STAR_DEFAULT = "Supporting"


# --- Star rules support (Phase 3) -------------------------------------------------
def load_star_rules(path: pathlib.Path):
    """Load star rule configuration JSON.

    Args:
        path (pathlib.Path): Path to a JSON rules file.

    Returns:
        dict | None: Parsed rules dict if readable, otherwise None.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def infer_star_from_rules(
    *,
    rules_cfg: dict,
    module_name: str,
    path: str,
    matriz_node: str,
    capabilities: list,
    owner: str,
) -> (str, float):
    """Infer constellation star suggestion from rules.

    Uses weighted heuristics in ``rules_cfg`` to compute a best star label
    and a confidence score.

    Args:
        rules_cfg (dict): Loaded rules configuration.
        module_name (str): Module name (e.g., "consciousness").
        path (str): Path context to evaluate against regex rules.
        matriz_node (str): MATRIZ node name for node overrides.
        capabilities (list): Capability dictionaries declared by the module.
        owner (str): Module owner for owner prior rules.

    Returns:
        tuple[str, float]: The suggested star label and confidence in [0, 1].

    Notes:
        Heuristic scoring weights consider:
        - Path regex hits (rules[])
        - Capability overrides
        - Node overrides
        - Owner priors
    """
    if not rules_cfg:
        return (STAR_DEFAULT, 0.0)

    weights = rules_cfg.get("weights", {})
    w_path = float(weights.get("path_regex", 0.4))
    w_cap = float(weights.get("capability_override", 0.6))
    w_node = float(weights.get("node_override", 0.5))
    w_owner = float(weights.get("owner_prior", 0.35))

    score = {}
    text = f"{module_name} {path}".lower()

    # apply exclusions
    for ex in rules_cfg.get("exclusions", []) or []:
        try:
            text = re.sub(ex.get("pattern", ""), " ", text, flags=re.IGNORECASE)
        except re.error:
            pass

    # rules: path keywords
    for r in rules_cfg.get("rules", []) or []:
        star = r.get("star")
        pat = r.get("pattern")
        try:
            if pat and re.search(pat, text, flags=re.IGNORECASE):
                score[star] = score.get(star, 0.0) + w_path
        except re.error:
            continue

    # capability overrides
    caps = {c.get("name", "").lower() for c in (capabilities or [])}
    for co in rules_cfg.get("capability_overrides", []) or []:
        cap = (co.get("capability") or "").lower()
        star = co.get("star")
        if cap and star and cap in caps:
            score[star] = score.get(star, 0.0) + w_cap

    # node overrides
    for no in rules_cfg.get("node_overrides", []) or []:
        if (no.get("node") or "").lower() == (matriz_node or "").lower():
            star = no.get("star")
            if star:
                score[star] = score.get(star, 0.0) + w_node

    # owner priors
    for op in rules_cfg.get("owner_priors", []) or []:
        try:
            if re.search(op.get("owner_regex", ""), owner or "", flags=re.IGNORECASE):
                star = op.get("star")
                if star:
                    score[star] = score.get(star, 0.0) + w_owner
        except re.error:
            pass

    if not score:
        return (STAR_DEFAULT, 0.0)
    best_star = max(score.items(), key=lambda kv: kv[1])[0]
    return (best_star, float(score[best_star]))


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
    (r"/quantum_|/qi_", "🔮 Oracle (Quantum)"),
]

COLONY_HINTS = [
    (r"/api/|/bridge/", "actuation"),
    (r"/consciousness/|/dream|/planning|/simulation", "simulation"),
    (r"/memory/|/rag/|/embedding|/kg/", "memory"),
    (r"/ethic|/guardian", "ethics"),
    (r"/vision|/ui|/dashboard|/visualization", "interface"),
    (r"/perception|/asr|/vision_model", "perception"),
]


def validate_star(star: str, star_canon: Dict[str, Any], *, labels: Optional[set[str]] = None) -> str:
    """Validate constellation star label against canonical definitions with fail-fast gating.

    Enforces strict validation of star labels to prevent invalid assignments
    from entering the manifest generation pipeline. Uses canonical star
    definitions from star_canon.json to ensure consistency across all modules.

    Args:
        star: Proposed star label to validate (e.g., "🛡️ Watch (Guardian)").
        star_canon: Canon mapping dictionary containing valid star definitions
            and aliases. Must include "stars" key with canonical labels.
        labels: Optional pre-extracted set of valid star labels. If None,
            labels will be extracted from star_canon. Defaults to None.

    Returns:
        str: The validated star label, unchanged if valid.

    Raises:
        SystemExit: When star is not found in canonical labels. Exits with
            code 1 and prints error message to stderr with remediation hints.

    Example:
        >>> canon = {"stars": [{"label": "🛡️ Watch (Guardian)"}]}
        >>> validate_star("🛡️ Watch (Guardian)", canon)
        '🛡️ Watch (Guardian)'
        >>> validate_star("Invalid Star", canon)
        ❌ FATAL: Invalid star 'Invalid Star' not in canon...
        SystemExit: 1
    """
    labels = labels or set(extract_canon_labels(star_canon))
    if star not in labels:
        print(f"❌ FATAL: Invalid star '{star}' not in canon: {labels}", file=sys.stderr)
        print("💡 Update star_canon.json or fix star inference heuristics", file=sys.stderr)
        sys.exit(1)
    return star


def guess_star(path: str, inv_star: Optional[str], star_canon: Dict[str, Any]) -> str:
    """Guess constellation star label with canonical normalization.

    Args:
        path (str): Module path hint for heuristics.
        inv_star (str | None): Star from inventory, if any.
        star_canon (dict): Canon mapping for normalization and aliases.

    Returns:
        str: Canonical star label (e.g., "🛡️ Watch (Guardian)").
    """
    labels = set(extract_canon_labels(star_canon))
    # Inventory-proposed star (normalize via aliases)
    if inv_star:
        norm = normalize_star_label(inv_star, star_canon)
        if norm in labels:
            return validate_star(norm, star_canon, labels=labels)
    # Heuristics from path
    for pattern, star in STAR_HINTS:
        if re.search(pattern, path):
            return validate_star(star, star_canon, labels=labels)
    return validate_star(STAR_DEFAULT, star_canon, labels=labels)


def guess_colony(path: str) -> Optional[str]:
    """Infer LUKHAS colony assignment from module path patterns.

    Colonies organize modules by functional domain (actuation, simulation,
    memory, ethics, interface, perception). Uses regex-based heuristics
    from COLONY_HINTS to match path patterns to colony assignments.

    Args:
        path: Module filesystem path (repo-relative, e.g., "lukhas/api/endpoints").
            Should include forward slashes as separators.

    Returns:
        str | None: Inferred colony name if a pattern matches (one of:
            "actuation", "simulation", "memory", "ethics", "interface",
            "perception"), otherwise None if no heuristic matches.

    Example:
        >>> guess_colony("lukhas/api/endpoints")
        'actuation'
        >>> guess_colony("candidate/memory/rag")
        'memory'
        >>> guess_colony("unknown/module")
        None
    """
    for pattern, colony in COLONY_HINTS:
        if re.search(pattern, path):
            return colony
    if "/api/" in path:
        return "actuation"
    return None


def infer_capabilities(path: str, star: str, matriz_node: str, module_name: str) -> List[Dict[str, Any]]:
    """Infer module capabilities from context using multi-source heuristics.

    Generates capability declarations for manifest compliance (schema requires
    minItems: 1). Combines MATRIZ node mappings, constellation star semantics,
    and path-specific patterns to infer plausible capabilities when explicit
    declarations are unavailable.

    Args:
        path: Module filesystem path for pattern matching (e.g., "lukhas/api/auth").
        star: Constellation star assignment (e.g., "⚛️ Anchor (Identity)").
        matriz_node: MATRIZ cognitive node (one of: memory, attention, thought,
            risk, intent, action, supporting).
        module_name: Module identifier for fallback TODO generation.

    Returns:
        list[dict]: Capability objects with keys: name (str), type (str),
            description (str), interfaces (list[str]). Always returns at
            least one capability to satisfy schema constraints.

    Example:
        >>> infer_capabilities(
        ...     "lukhas/api/auth",
        ...     "⚛️ Anchor (Identity)",
        ...     "supporting",
        ...     "auth"
        ... )
        [
            {'name': 'infrastructure_support', 'type': 'utility', ...},
            {'name': 'identity_management', 'type': 'authentication', ...},
            {'name': 'api_interface', 'type': 'api', ...},
            {'name': 'authentication', 'type': 'authentication', ...}
        ]
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
        "⚛️ Anchor (Identity)": (
            "identity_management",
            "authentication",
            "Manages authentication, authorization, and identity",
        ),
        "✦ Trail (Memory)": ("memory_persistence", "storage", "Provides persistent memory and recall"),
        "🔬 Horizon (Vision)": ("perception_processing", "processing", "Processes visual and perceptual inputs"),
        "🌱 Living (Bio)": ("bio_adaptation", "processing", "Implements bio-inspired adaptive behaviors"),
        "🌙 Drift (Dream)": ("creative_synthesis", "processing", "Generates creative outputs and novel patterns"),
        "⚖️ North (Ethics)": ("ethical_reasoning", "processing", "Applies ethical reasoning and value alignment"),
        "🛡️ Watch (Guardian)": ("policy_enforcement", "monitoring", "Enforces policies and constitutional constraints"),
        "🔮 Oracle (Quantum)": ("quantum_processing", "processing", "Applies quantum-inspired algorithms and patterns"),
        "🌊 Flow (Consciousness)": (
            "consciousness_integration",
            "orchestration",
            "Integrates consciousness-aware patterns",
        ),
    }

    # Primary capability from MATRIZ node
    if matriz_node in node_caps:
        name, cap_type, desc = node_caps[matriz_node]
        capabilities.append({"name": name, "type": cap_type, "description": desc, "interfaces": []})

    # Secondary capability from star (if different from Supporting)
    if star in star_caps and star != "Supporting":
        name, cap_type, desc = star_caps[star]
        # Only add if not duplicate
        if not any(c["name"] == name for c in capabilities):
            capabilities.append({"name": name, "type": cap_type, "description": desc, "interfaces": []})

    # Path-specific capabilities
    if "/api/" in path or "/bridge/" in path:
        capabilities.append(
            {
                "name": "api_interface",
                "type": "api",
                "description": "Exposes external API endpoints",
                "interfaces": ["REST", "HTTP"],
            }
        )

    if "/oauth" in path or "/oidc" in path or "/auth" in path:
        capabilities.append(
            {
                "name": "authentication",
                "type": "authentication",
                "description": "Handles authentication flows",
                "interfaces": ["OAuth2", "OIDC"],
            }
        )

    # Ensure at least one capability (schema requirement)
    if not capabilities:
        capabilities.append(
            {
                "name": "core_functionality",
                "type": "utility",
                "description": f"TODO: Document {module_name} capabilities",
                "interfaces": [],
            }
        )

    return capabilities


def map_priority_to_quality_tier(priority: str) -> str:
    """Map priority labels to quality tier classifications (pre-gating).

    Provides base tier assignment before validation gates are applied.
    Final tier may be demoted by decide_quality_tier() if requirements
    (tests, ownership) are not met for the proposed tier.

    Args:
        priority: Priority string from inventory (case-insensitive). Expected
            values: "critical", "high", "medium", "low", or empty/None.

    Returns:
        str: Quality tier constant (one of: "T1_critical", "T2_important",
            "T3_standard", "T4_experimental"). Defaults to T4_experimental
            for unrecognized priorities.

    Example:
        >>> map_priority_to_quality_tier("critical")
        'T1_critical'
        >>> map_priority_to_quality_tier("LOW")
        'T4_experimental'
        >>> map_priority_to_quality_tier(None)
        'T4_experimental'
    """
    p = (priority or "").lower()
    if p == "critical":
        return "T1_critical"
    if p == "high":
        return "T2_important"
    if p == "medium":
        return "T3_standard"
    return "T4_experimental"


def decide_quality_tier(priority: Optional[str], has_tests: bool, owner: Optional[str]) -> str:
    """Apply quality gates to determine final tier assignment.

    Enforces T1 requirements (tests + assigned owner) with automatic demotion
    when criteria are not met. Implements defensive tier assignment to prevent
    modules from claiming T1_critical without necessary quality infrastructure.

    Args:
        priority: Priority label from inventory ("critical", "high", "medium",
            "low", or None). Determines base tier before gating.
        has_tests: Whether module has discovered test coverage (bool). T1
            modules MUST have tests.
        owner: Module owner identifier. Must be non-empty and not "unassigned"
            for T1 qualification. None or "unassigned" triggers demotion.

    Returns:
        str: Final quality tier after applying gates (one of: "T1_critical",
            "T2_important", "T3_standard", "T4_experimental").

    Example:
        >>> decide_quality_tier("critical", True, "alice")
        'T1_critical'
        >>> decide_quality_tier("critical", False, "alice")
        'T2_important'
        >>> decide_quality_tier("critical", False, "unassigned")
        'T3_standard'
        >>> decide_quality_tier("medium", True, "bob")
        'T3_standard'
    """
    base = map_priority_to_quality_tier(priority or "")

    # Gate: T1 requires both tests and owner
    if base == "T1_critical":
        if not has_tests or not owner or owner == "unassigned":
            return "T2_important" if owner and owner != "unassigned" else "T3_standard"

    return base


def discover_tests(module_fs_path: str) -> List[str]:
    """Discover test files for a module using multi-location search strategy.

    Searches common test locations (module-local tests/, repo-level tests/,
    sibling test files) to build comprehensive test path inventory. Uses
    standard pytest naming conventions (test_*.py, *_test.py) and multiple
    glob patterns to maximize discovery coverage.

    Args:
        module_fs_path: Module directory path relative to repository root
            (e.g., "lukhas/api/auth" or "candidate/memory/rag"). Empty
            string returns empty list.

    Returns:
        list[str]: Sorted list of discovered test file paths, normalized
            relative to repository root. Empty list if no tests found or
            path is empty/invalid.

    Example:
        >>> discover_tests("lukhas/identity")
        [
            'lukhas/identity/tests/test_oauth.py',
            'tests/lukhas/identity/test_integration.py'
        ]
        >>> discover_tests("")
        []
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
    """Build schema-compliant testing configuration block for manifest.

    Generates testing metadata matching matriz_module_compliance.schema.json
    requirements. Applies tier-specific constraints (T1/T2 MUST include
    test_paths even when empty; T3/T4 only include when non-empty). Sets
    baseline coverage targets for modules with tests.

    Args:
        module_fs_path: Module directory path for test discovery (repo-relative).
            Passed to discover_tests() for file enumeration.
        tier: Quality tier constant ("T1_critical", "T2_important",
            "T3_standard", "T4_experimental", or None). Defaults to
            "T4_experimental" if None.

    Returns:
        dict: Testing block with keys:
            - has_tests (bool): Whether tests were discovered
            - quality_tier (str): Tier assignment
            - test_paths (list[str]): Test file paths (T1/T2 always included,
              T3/T4 only when non-empty)
            - coverage_baseline (int): Target coverage % (50% when has_tests=True)

    Example:
        >>> build_testing_block("lukhas/identity", "T1_critical")
        {
            'has_tests': True,
            'quality_tier': 'T1_critical',
            'test_paths': ['tests/test_identity.py'],
            'coverage_baseline': 50
        }
    """
    paths = discover_tests(module_fs_path)
    has_tests = bool(paths)

    testing: Dict[str, Any] = {"has_tests": has_tests, "quality_tier": tier or "T4_experimental"}

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
    """Generate ISO 8601 timestamp string in UTC with Zulu timezone indicator.

    Produces timestamps suitable for manifest metadata fields (created,
    last_updated). Strips microseconds for readability while preserving
    second-level precision.

    Returns:
        str: UTC timestamp in ISO 8601 format with 'Z' suffix
            (e.g., "2025-10-20T14:32:15Z"). Microseconds are zeroed.

    Example:
        >>> now_iso()
        '2025-10-20T14:32:15Z'
    """
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def make_context_md(
    fqn: str, star: str, pipeline_nodes: List[str], colony: Optional[str], exports=None, contracts=None, logger=None
) -> str:
    """Generate lukhas_context.md template with architectural metadata placeholders.

    Creates structured Markdown documentation template for module context files.
    Includes constellation alignment, MATRIZ integration, contracts, observability,
    security, and testing guidance. Template sections use TODO markers to guide
    manual completion by module owners.

    Args:
        fqn: Fully qualified module name (e.g., "lukhas.identity.oauth").
        star: Constellation star label (e.g., "⚛️ Anchor (Identity)").
        pipeline_nodes: MATRIZ cognitive nodes list (e.g., ["memory", "attention"]).
        colony: Colony assignment or None (e.g., "actuation", "memory").
        exports: Reserved for future use (currently ignored).
        contracts: Reserved for future use (currently ignored).
        logger: Logger name for observability section. Defaults to fqn if None.

    Returns:
        str: Multi-line Markdown template with sections:
            - Module header (star, MATRIZ nodes, colony)
            - What it does (TODO placeholder)
            - Contracts (publish/subscribe/exports)
            - Observability (spans, metrics, logging)
            - Security (auth, data classification, policies)
            - Tests (paths, tier-based coverage targets)

    Example:
        >>> md = make_context_md(
        ...     "lukhas.identity",
        ...     "⚛️ Anchor (Identity)",
        ...     ["supporting"],
        ...     "actuation",
        ...     logger="lukhas.identity.oauth"
        ... )
        >>> "# lukhas.identity" in md
        True
        >>> "T1≥70%" in md
        True
    """
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
    """Generate manifests and optional context files from inventory JSON.

    Args:
        --inventory: Path to the COMPLETE_MODULE_INVENTORY.json file.
        --out: Output directory for manifests.
        --schema: Optional schema path for validation.
        --star-canon: Canon mapping file for constellation stars.
        --write-context: If set, also write lukhas_context.md files.
        --limit: Optional maximum number of items to process.
        --star-from-rules: Use star_rules.json to override default star.
        --star-rules: Path to rules file.
        --star-confidence-min: Minimum confidence to accept rule-suggested star.

    Returns:
        None
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="docs/audits/COMPLETE_MODULE_INVENTORY.json")
    ap.add_argument("--out", default="manifests")
    ap.add_argument("--schema", default=None)
    ap.add_argument("--star-canon", default=str(HERE / "star_canon.json"))
    ap.add_argument("--write-context", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument(
        "--star-from-rules", action="store_true", help="Use configs/star_rules.json to override 'Supporting'"
    )
    ap.add_argument("--star-rules", default=str(ROOT / "configs" / "star_rules.json"))
    ap.add_argument("--star-confidence-min", type=float, default=0.70)
    args = ap.parse_args()

    inv = json.load(open(args.inventory, "r", encoding="utf-8"))
    star_canon = json.load(open(args.star_canon, "r", encoding="utf-8"))
    extract_canon_labels(star_canon)

    items = inv.get("inventory", [])
    if args.limit:
        items = items[: args.limit]

    rules_cfg = None
    if args.star_from_rules:
        rules_cfg = load_star_rules(pathlib.Path(args.star_rules))

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

        star = guess_star("/" + (path or ""), inv_star, star_canon)
        colony = guess_colony("/" + (path or ""))

        # Discover tests first (needed for gated tiering)
        test_paths = discover_tests(path or "")
        has_tests = bool(test_paths)

        # Owner from inventory (will be used for tier gating and metadata)
        owner = it.get("owner", "unassigned")

        # Gated tiering: T1 requires tests + owner
        quality_tier = decide_quality_tier(priority, has_tests, owner)

        capabilities = infer_capabilities(path or "", star, matriz_node, module_name or "")

        # Optional star promotion via rules (only if currently Supporting)
        if args.star_from_rules and star == STAR_DEFAULT and rules_cfg:
            owner = it.get("owner", "") or ""
            suggest_star, conf = infer_star_from_rules(
                rules_cfg=rules_cfg,
                module_name=module_name or "",
                path=path or "",
                matriz_node=matriz_node,
                capabilities=capabilities,
                owner=owner,
            )
            min_auto = float((rules_cfg.get("confidence", {}) or {}).get("min_autopromote", args.star_confidence_min))
            if conf >= min_auto:
                star = validate_star(suggest_star, star_canon)

        module_obj = {
            "name": module_name,
            "path": path,
            "type": it.get("type", "package"),
            "lane": lane,  # legacy, allowed but deprecated
        }
        if colony:
            module_obj["colony"] = colony

        manifest = {
            "schema_version": "1.1.0",
            "module": module_obj,
            "matriz_integration": {"status": "partial", "pipeline_nodes": [matriz_node], "cognitive_function": ""},
            "constellation_alignment": {"primary_star": star, "star_aliases": [], "trinity_aspects": []},
            "capabilities": capabilities,
            "dependencies": {"internal": [], "external": [], "circular_dependencies": []},
            "exports": {"classes": [], "functions": [], "constants": []},
            "testing": build_testing_block(path or "", quality_tier),
            "observability": {
                "spans": [],
                "metrics": [],
                "logging": {
                    "logger_name": (module_name or path or "").replace("/", ".") or "lukhas",
                    "default_level": "INFO",
                },
                "events": {"publishes": [], "subscribes": []},
            },
            "security": {
                "requires_auth": False,
                "data_classification": "internal",
                "secrets_used": [],
                "network_calls": False,
                "sandboxed": True,
                "policies": [],
            },
            "metadata": {
                "created": now_iso(),
                "last_updated": now_iso(),
                "manifest_generated": True,
                "owner": "unassigned",
                "documentation_url": "",
                "tags": [],
            },
        }

        out_dir = ROOT / args.out / (path or module_name or "unknown")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "module.manifest.json"
        out_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        wrote += 1

        if args.write_context:
            ctx = make_context_md(
                module_name or path,
                star,
                manifest["matriz_integration"]["pipeline_nodes"],
                colony,
                exports=None,
                contracts=None,
                logger=manifest["observability"]["logging"]["logger_name"],
            )
            (out_dir / "lukhas_context.md").write_text(ctx, encoding="utf-8")

    print(f"DONE: wrote {wrote}/{total} manifests to {args.out}")


if __name__ == "__main__":
    main()
