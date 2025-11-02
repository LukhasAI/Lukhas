#!/usr/bin/env python3
"""
Generate comprehensive integration manifest for all 193 hidden gems.

This script creates:
1. JSON integration manifest (Codex-friendly)
2. Detailed integration guide with step-by-step instructions
3. Migration complexity analysis
4. Optimal MATRIZ location mapping

Usage:
    python3 scripts/generate_integration_manifest.py
    make integration-manifest  # via Makefile
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# MATRIZ Location Mapping Rules
LOCATION_RULES = {
    # Core consciousness capabilities
    "consciousness.awareness": "matriz/consciousness/awareness/",
    "consciousness.reflection": "matriz/consciousness/reflection/",
    "consciousness.cognitive": "matriz/consciousness/cognitive/",
    "consciousness.dream": "matriz/consciousness/dream/",
    "consciousness.core": "matriz/consciousness/core/",
    # Memory systems
    "memory.core": "matriz/memory/core/",
    "memory.temporal": "matriz/memory/temporal/",
    "memory.folds": "matriz/memory/folds/",
    # Identity & Auth
    "identity": "core/identity/",
    # Governance & Ethics
    "governance": "core/governance/",
    # Core integration
    "core.colonies": "core/colonies/",
    "core.glyph": "core/glyph/",
    "core.symbolic": "core/symbolic/",
    "core.integration": "core/integration/",
    # Bio-inspired systems
    "bio": "matriz/bio/",
    # Quantum-inspired
    "quantum": "matriz/quantum/",
    # API/Serve layer
    "serve": "serve/",
    "api": "serve/api/",
}


def determine_target_location(module_path: str) -> dict[str, str]:
    """
    Determine optimal MATRIZ location for a module.

    Returns:
        dict with 'target_dir', 'target_file', 'reasoning'
    """
    parts = module_path.split(".")

    # Remove labs/candidate prefix if present
    if parts[0] in ("labs", "candidate"):
        parts = parts[1:]

    # Check if already in matriz/core/serve
    if parts[0] in ("matriz", "core", "serve"):
        return {
            "target_dir": "/".join(parts[:-1]) + "/",
            "target_file": parts[-1] + ".py",
            "reasoning": "Already in production structure - verify placement",
        }

    # Match against location rules
    for pattern, target_dir in LOCATION_RULES.items():
        pattern_parts = pattern.split(".")

        # Check if module path matches pattern
        if len(parts) >= len(pattern_parts):
            if all(parts[i] == pattern_parts[i] for i in range(len(pattern_parts))):
                # Construct target path
                remaining = parts[len(pattern_parts) :]
                if remaining:
                    full_target = target_dir + "/".join(remaining[:-1]) + "/"
                    target_file = remaining[-1] + ".py"
                else:
                    full_target = target_dir
                    target_file = parts[-1] + ".py"

                return {
                    "target_dir": full_target,
                    "target_file": target_file,
                    "reasoning": f"Matches pattern '{pattern}' - move to {target_dir}",
                }

    # Default: keep domain, move to core
    domain = parts[0] if parts else "misc"
    return {
        "target_dir": f"core/{domain}/",
        "target_file": parts[-1] + ".py" if parts else "unknown.py",
        "reasoning": f"Default placement in core/{domain}/ - review manually",
    }


def calculate_integration_complexity(
    loc: int,
    classes: int,
    functions: int,
    imports_core: bool,
    imports_matriz: bool,
    score: float,
) -> dict[str, Any]:
    """
    Calculate integration complexity (low/medium/high).

    Returns:
        dict with 'complexity', 'effort_hours', 'risk_level', 'rationale'
    """
    # Base complexity from size
    base_complexity = 0
    if loc < 300:
        base_complexity = 1
        effort = 2
    elif loc < 800:
        base_complexity = 2
        effort = 6
    else:
        base_complexity = 3
        effort = 12

    # Adjust for structural complexity
    if classes > 10:
        base_complexity += 1
        effort += 4
    elif classes > 5:
        effort += 2

    if functions > 20:
        base_complexity += 1
        effort += 2

    # Reduce if already imports core/matriz (lower risk)
    if imports_core or imports_matriz:
        base_complexity = max(1, base_complexity - 1)
        effort = max(2, effort - 2)

    # Adjust for quality score (high score = lower risk)
    if score >= 85:
        risk = "low"
    elif score >= 75:
        risk = "medium"
    else:
        risk = "medium-high"

    # Final complexity rating
    if base_complexity <= 2:
        complexity = "low"
    elif base_complexity <= 4:
        complexity = "medium"
    else:
        complexity = "high"

    rationale_parts = []
    if loc >= 1000:
        rationale_parts.append(f"{loc} LOC")
    if classes > 5:
        rationale_parts.append(f"{classes} classes")
    if imports_core or imports_matriz:
        rationale_parts.append("already imports production code")
    if score >= 85:
        rationale_parts.append("high quality score")

    return {
        "complexity": complexity,
        "effort_hours": effort,
        "risk_level": risk,
        "rationale": ", ".join(rationale_parts) if rationale_parts else "standard module",
    }


def generate_integration_steps(
    module: dict[str, Any],
    location: dict[str, str],
    complexity: dict[str, Any],
) -> list[str]:
    """Generate step-by-step integration instructions."""
    steps = []

    source_path = module["module"].replace(".", "/") + ".py"
    target_path = location["target_dir"] + location["target_file"]

    # Step 1: Review
    steps.append(
        f"REVIEW: Read {source_path} and understand architecture "
        f"({module['loc']} LOC, {module['classes']} classes, {module['functions']} functions)"
    )

    # Step 2: Dependencies
    if module["imports_core"] == "yes" or module["imports_matriz"] == "yes":
        steps.append("CHECK_DEPS: Verify all imports from core/matriz are valid and available")
    else:
        steps.append("CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed")

    # Step 3: Tests
    steps.append(
        f"CREATE_TESTS: Write integration tests in tests/integration/test_{location['target_file'].replace('.py', '')}.py"
    )

    # Step 4: Move
    steps.append(f"MOVE: git mv {source_path} {target_path}")

    # Step 5: Update imports
    steps.append("UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules")

    # Step 6: Integration
    if "engine" in module["module"].lower() or "system" in module["module"].lower():
        steps.append("INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)")
    else:
        steps.append("INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)")

    # Step 7: Test
    steps.append("TEST: Run pytest tests/integration/ and tests/smoke/ to verify")

    # Step 8: Document
    steps.append("DOCUMENT: Update docs/architecture/ with new component location and purpose")

    # Step 9: Commit
    steps.append(
        f"COMMIT: git commit -m \"feat({location['target_dir'].split('/')[0]}): integrate {location['target_file'].replace('.py', '')} from labs\""
    )

    return steps


def load_hidden_gems(csv_path: Path) -> list[dict[str, Any]]:
    """Load all hidden gems from CSV."""
    gems = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["category"] == "hidden_gem":
                # Convert numeric fields
                row["score"] = float(row["score"])
                row["loc"] = int(row["loc"])
                row["classes"] = int(row["classes"])
                row["functions"] = int(row["functions"])
                row["last_modified_days"] = int(row["last_modified_days"])
                gems.append(row)

    return gems


def main():
    """Generate integration manifest and guide."""
    repo_root = Path(__file__).parent.parent
    csv_path = repo_root / "docs" / "audits" / "isolated_modules_scored.csv"
    output_dir = repo_root / "docs" / "audits"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading hidden gems from CSV...")
    gems = load_hidden_gems(csv_path)
    print(f"Found {len(gems)} hidden gems")

    print("Analyzing integration requirements...")
    integration_manifest = []

    for gem in gems:
        location = determine_target_location(gem["module"])
        complexity = calculate_integration_complexity(
            gem["loc"],
            gem["classes"],
            gem["functions"],
            gem["imports_core"] == "yes",
            gem["imports_matriz"] == "yes",
            gem["score"],
        )
        steps = generate_integration_steps(gem, location, complexity)

        integration_manifest.append(
            {
                "module": gem["module"],
                "score": gem["score"],
                "current_location": gem["module"].replace(".", "/") + ".py",
                "target_location": location["target_dir"] + location["target_file"],
                "location_reasoning": location["reasoning"],
                "complexity": complexity["complexity"],
                "effort_hours": complexity["effort_hours"],
                "risk_level": complexity["risk_level"],
                "complexity_rationale": complexity["rationale"],
                "loc": gem["loc"],
                "classes": gem["classes"],
                "functions": gem["functions"],
                "imports_core": gem["imports_core"] == "yes",
                "imports_matriz": gem["imports_matriz"] == "yes",
                "integration_steps": steps,
                "dependencies": {
                    "core": gem["imports_core"] == "yes",
                    "matriz": gem["imports_matriz"] == "yes",
                },
                "metadata": {
                    "last_modified_days": gem["last_modified_days"],
                    "in_archive": gem["archive"] == "yes",
                    "in_candidate_labs": gem["candidate_labs"] == "yes",
                },
            }
        )

    # Sort by score descending
    integration_manifest.sort(key=lambda x: x["score"], reverse=True)

    # Generate JSON manifest (Codex-friendly)
    json_path = output_dir / "integration_manifest.json"
    print(f"Writing JSON manifest to {json_path}...")
    with open(json_path, "w") as f:
        json.dump(
            {
                "generated": datetime.now().isoformat(),
                "total_modules": len(integration_manifest),
                "complexity_breakdown": {
                    "low": sum(1 for m in integration_manifest if m["complexity"] == "low"),
                    "medium": sum(1 for m in integration_manifest if m["complexity"] == "medium"),
                    "high": sum(1 for m in integration_manifest if m["complexity"] == "high"),
                },
                "total_effort_hours": sum(m["effort_hours"] for m in integration_manifest),
                "modules": integration_manifest,
            },
            f,
            indent=2,
        )

    # Generate detailed integration guide (Markdown)
    md_path = output_dir / "INTEGRATION_GUIDE.md"
    print(f"Writing integration guide to {md_path}...")

    with open(md_path, "w") as f:
        f.write("# Hidden Gems Integration Guide - All 193 Modules\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Modules**: {len(integration_manifest)}\n")
        f.write(f"**Total Effort**: ~{sum(m['effort_hours'] for m in integration_manifest)} hours\n\n")

        f.write("## Complexity Breakdown\n\n")
        low = sum(1 for m in integration_manifest if m["complexity"] == "low")
        med = sum(1 for m in integration_manifest if m["complexity"] == "medium")
        high = sum(1 for m in integration_manifest if m["complexity"] == "high")
        f.write(f"- **Low**: {low} modules (~2-4 hours each)\n")
        f.write(f"- **Medium**: {med} modules (~6-12 hours each)\n")
        f.write(f"- **High**: {high} modules (~12-24 hours each)\n\n")

        f.write("## Quick Navigation\n\n")
        f.write("- [JSON Manifest](#json-manifest) - Codex-friendly structured data\n")
        f.write("- [Top 20 Priority](#top-20-priority) - Highest value, lowest risk\n")
        f.write("- [By Complexity](#by-complexity) - Grouped by integration effort\n")
        f.write("- [By Target Location](#by-target-location) - Grouped by destination\n")
        f.write("- [All 193 Modules](#all-193-modules) - Complete detailed list\n\n")

        f.write("---\n\n")

        # Top 20 Priority
        f.write("## Top 20 Priority\n\n")
        f.write("Highest value, clear integration path, recommended for immediate work.\n\n")

        for i, module in enumerate(integration_manifest[:20], 1):
            f.write(f"### {i}. {module['module']} (Score: {module['score']})\n\n")
            f.write(f"**Current**: `{module['current_location']}`\n")
            f.write(f"**Target**: `{module['target_location']}`\n")
            f.write(f"**Complexity**: {module['complexity']} ({module['effort_hours']}h)\n")
            f.write(f"**Risk**: {module['risk_level']}\n\n")
            f.write(f"**Why**: {module['complexity_rationale']}\n\n")
            f.write(f"**Location Reasoning**: {module['location_reasoning']}\n\n")
            f.write("**Integration Steps**:\n\n")
            for step_num, step in enumerate(module["integration_steps"], 1):
                action = step.split(":")[0]
                detail = ":".join(step.split(":")[1:]).strip() if ":" in step else ""
                f.write(f"{step_num}. **{action}**: {detail}\n")
            f.write("\n---\n\n")

        # By Complexity
        f.write("## By Complexity\n\n")

        for complexity_level in ["low", "medium", "high"]:
            modules_at_level = [m for m in integration_manifest if m["complexity"] == complexity_level]
            if not modules_at_level:
                continue

            f.write(f"### {complexity_level.title()} Complexity ({len(modules_at_level)} modules)\n\n")
            f.write("| Module | Score | Target | Effort | Risk |\n")
            f.write("|--------|-------|--------|--------|------|\n")

            for m in modules_at_level[:10]:  # First 10 at each level
                short_name = m["module"].split(".")[-1]
                target_short = "/".join(m["target_location"].split("/")[-2:])
                f.write(
                    f"| {short_name} | {m['score']} | {target_short} | {m['effort_hours']}h | {m['risk_level']} |\n"
                )

            if len(modules_at_level) > 10:
                f.write(f"\n*...and {len(modules_at_level) - 10} more*\n")
            f.write("\n")

        # By Target Location
        f.write("## By Target Location\n\n")

        by_location = {}
        for m in integration_manifest:
            target_dir = m["target_location"].split("/")[0]
            if target_dir not in by_location:
                by_location[target_dir] = []
            by_location[target_dir].append(m)

        for location in sorted(by_location.keys()):
            modules = by_location[location]
            f.write(f"### {location}/ ({len(modules)} modules)\n\n")

            for m in modules[:5]:  # First 5 per location
                f.write(
                    f"- **{m['module'].split('.')[-1]}** (score: {m['score']}, "
                    f"complexity: {m['complexity']}) → `{m['target_location']}`\n"
                )

            if len(modules) > 5:
                f.write(f"- *...and {len(modules) - 5} more*\n")
            f.write("\n")

        # All 193 Modules
        f.write("---\n\n")
        f.write("## All 193 Modules\n\n")
        f.write("Complete list with integration instructions.\n\n")

        for i, module in enumerate(integration_manifest, 1):
            f.write(f"### {i}. {module['module']} (Score: {module['score']})\n\n")
            f.write("| Property | Value |\n")
            f.write("|----------|-------|\n")
            f.write(f"| Current Location | `{module['current_location']}` |\n")
            f.write(f"| Target Location | `{module['target_location']}` |\n")
            f.write(f"| Complexity | {module['complexity']} |\n")
            f.write(f"| Effort | {module['effort_hours']} hours |\n")
            f.write(f"| Risk Level | {module['risk_level']} |\n")
            f.write(f"| LOC | {module['loc']} |\n")
            f.write(f"| Classes | {module['classes']} |\n")
            f.write(f"| Functions | {module['functions']} |\n")
            f.write(f"| Imports Core | {'Yes' if module['imports_core'] else 'No'} |\n")
            f.write(f"| Imports MATRIZ | {'Yes' if module['imports_matriz'] else 'No'} |\n\n")

            f.write(f"**Reasoning**: {module['location_reasoning']}\n\n")
            f.write(f"**Complexity Rationale**: {module['complexity_rationale']}\n\n")

            f.write("**Integration Steps**:\n\n")
            for step_num, step in enumerate(module["integration_steps"], 1):
                f.write(f"{step_num}. {step}\n")

            f.write("\n---\n\n")

        # Footer
        f.write("## Usage\n\n")
        f.write("### Codex Integration\n\n")
        f.write("```python\n")
        f.write("import json\n")
        f.write("with open('docs/audits/integration_manifest.json') as f:\n")
        f.write("    manifest = json.load(f)\n")
        f.write("    for module in manifest['modules']:\n")
        f.write("        if module['complexity'] == 'low':\n")
        f.write("            # Process low-complexity integrations first\n")
        f.write("            print(module['integration_steps'])\n")
        f.write("```\n\n")

        f.write("### Manual Integration\n\n")
        f.write("1. Pick a module from Top 20 Priority\n")
        f.write("2. Follow integration steps sequentially\n")
        f.write("3. Run tests after each major step\n")
        f.write("4. Update documentation\n")
        f.write("5. Commit with proper message format\n\n")

        f.write("### Bulk Integration Script\n\n")
        f.write("See `scripts/bulk_integrate_gems.py` for automated migration (coming soon).\n")

    print("\n✅ Integration manifest generation complete!")
    print(f"   - JSON manifest: {json_path}")
    print(f"   - Integration guide: {md_path}")
    print(f"   - Total modules: {len(integration_manifest)}")
    print(f"   - Estimated effort: ~{sum(m['effort_hours'] for m in integration_manifest)} hours")
    print(f"\n📖 Review {md_path} for detailed integration instructions")


if __name__ == "__main__":
    main()
