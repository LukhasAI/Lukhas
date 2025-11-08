#!/usr/bin/env python3
"""
Module Manifest Enrichment Tool - Extract rich metadata from legacy data

Promotes high-value legacy data from x_legacy into main manifest fields
with domain-specific intelligence and LUKHAS-aware context.
"""

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON file safely"""
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_json(path: Path, data: dict[str, Any]) -> None:
    """Save JSON file with formatting"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write('\n')

def detect_module_entrypoints(module_dir: Path) -> list[str]:
    """Detect actual Python entrypoints in module"""
    entrypoints = []

    # Check for __init__.py exports
    init_file = module_dir / "__init__.py"
    if init_file.exists():
        try:
            content = init_file.read_text(encoding='utf-8')
            # Look for __all__ exports
            if "__all__" in content:
                entrypoints.append(f"{module_dir.name}")
        except Exception as e:
            logger.debug(f"Expected optional failure: {e}")
            pass

    # Check legacy data for exports
    manifest_file = module_dir / "module.manifest.json"
    if manifest_file.exists():
        manifest = load_json(manifest_file)
        legacy = manifest.get("x_legacy", {})

        # Extract from component inventory
        component_inv = legacy.get("component_inventory", {})
        python_files = component_inv.get("python_files", [])

        for py_file in python_files:
            exports = py_file.get("exports", [])
            if exports:
                for export in exports:
                    entrypoints.append(f"{module_dir.name}.{py_file['filename'].replace('.py', '')}:{export}")

    return entrypoints

def extract_rich_description(module_name: str, legacy_data: dict[str, Any]) -> str:
    """Extract rich description from legacy metadata"""

    # Domain-specific descriptions based on module name and legacy data
    domain_descriptions = {
        "consciousness": "Advanced consciousness processing engine implementing awareness patterns, decision-making algorithms, and MATRIZ pipeline integration for cognitive state management and phenomenological processing.",
        "memory": "Comprehensive memory management system with fold-based architecture, temporal persistence, and consciousness-memory coupling for episodic and semantic memory operations.",
        "identity": "Identity and authentication infrastructure providing λID Core Identity System, WebAuthn/FIDO2 integration, OAuth2/OIDC flows, and secure credential management with namespace isolation.",
        "governance": "Governance framework implementing policy engines, ethical decision systems, Guardian System integration, and constitutional AI principles for autonomous governance operations.",
        "matriz": "MATRIZ core processing engine providing bio-symbolic adaptation, consciousness data flows, quantum-inspired algorithms, and symbolic reasoning for AGI development.",
        "core": "Core orchestration and infrastructure layer providing system coordination, symbolic network integration, consciousness-core coupling, and fundamental LUKHAS primitives.",
        "bridge": "External service integration bridge providing OAuth flows, API adapters, service mesh coordination, and secure credential management for third-party connectivity.",
        "api": "RESTful API infrastructure with GraphQL support, WebSocket real-time capabilities, multi-AI orchestration endpoints, and comprehensive API gateway functionality.",
        "quantum": "Quantum-inspired computing algorithms implementing superposition-based decision making, quantum state simulation, and bio-quantum hybrid processing systems.",
        "orchestration": "Multi-AI orchestration platform coordinating GPT-4, Claude, Gemini consensus workflows with Context Bus implementation and sub-100ms API latency optimization."
    }

    # Check for rich description in legacy data
    if legacy_data:
        dir_meta = legacy_data.get("directory_metadata", {})
        if dir_meta.get("purpose") and "Directory containing" not in dir_meta["purpose"]:
            return dir_meta["purpose"]

        cognitive_domains = dir_meta.get("cognitive_domains", [])
        if cognitive_domains:
            return f"LUKHAS {module_name} module implementing {', '.join(cognitive_domains)} with consciousness integration and MATRIZ pipeline compatibility."

    # Return domain-specific description or fallback
    return domain_descriptions.get(module_name, f"LUKHAS {module_name} module providing specialized functionality within the consciousness-driven AGI architecture.")

def extract_rich_tags(module_name: str, legacy_data: dict[str, Any]) -> list[str]:
    """Extract meaningful tags from module name and legacy data"""

    # Base tags from module name patterns
    name_tags = {
        "consciousness": ["consciousness", "awareness", "cognition", "decision-engine", "matriz-processor"],
        "memory": ["memory", "temporal", "episodic", "semantic", "fold-architecture"],
        "identity": ["identity", "authentication", "oauth2", "webauthn", "security"],
        "governance": ["governance", "policy", "ethics", "guardian", "constitutional-ai"],
        "matriz": ["matriz", "bio-symbolic", "quantum-inspired", "symbolic-reasoning"],
        "core": ["core", "orchestration", "infrastructure", "coordination"],
        "bridge": ["bridge", "integration", "adapters", "external-services"],
        "api": ["api", "rest", "graphql", "websocket", "orchestration"],
        "quantum": ["quantum", "superposition", "quantum-computing", "bio-quantum"],
        "orchestration": ["orchestration", "multi-ai", "consensus", "context-bus"]
    }

    tags = list(name_tags.get(module_name, [module_name.replace("_", "-")]))

    # Extract from legacy data
    if legacy_data:
        dir_meta = legacy_data.get("directory_metadata", {})

        # Add cognitive domains
        cognitive_domains = dir_meta.get("cognitive_domains", [])
        tags.extend([domain.replace("_", "-") for domain in cognitive_domains])

        # Add constellation role
        constellation_role = dir_meta.get("constellation_role")
        if constellation_role:
            tags.append(constellation_role.replace("_", "-"))

        # Add lane information
        lane = dir_meta.get("lane")
        if lane and lane != "development":
            tags.append(f"lane-{lane}")

        # Add T4 compliance level
        t4_level = dir_meta.get("t4_compliance_level")
        if t4_level:
            tags.append(f"t4-{t4_level}")

    return list(set(tags))  # Remove duplicates

def extract_dependencies(module_name: str, legacy_data: dict[str, Any]) -> list[str]:
    """Extract module dependencies from legacy data"""
    dependencies = []

    if legacy_data:
        # Check component inventory for dependencies
        component_inv = legacy_data.get("component_inventory", {})
        python_files = component_inv.get("python_files", [])

        all_deps = set()
        for py_file in python_files:
            file_deps = py_file.get("dependencies", [])
            all_deps.update(file_deps)

        # Filter to likely module dependencies (not system packages)
        for dep in all_deps:
            if any(keyword in dep.lower() for keyword in ['lukhas', 'matriz', 'consciousness', 'memory', 'identity', 'governance']):
                dependencies.append(dep)

    # Add logical dependencies based on module type
    logical_deps = {
        "api": ["core", "identity"],
        "bridge": ["identity", "core"],
        "governance": ["identity", "core"],
        "orchestration": ["core", "api"],
        "quantum": ["core", "consciousness"],
        "memory": ["core"],
        "consciousness": ["core", "memoria"]
    }

    if module_name in logical_deps:
        dependencies.extend(logical_deps[module_name])

    return list(set(dependencies))

def extract_observability_spans(module_name: str, legacy_data: dict[str, Any]) -> list[str]:
    """Extract required observability spans for module"""

    # Default spans by module type
    span_patterns = {
        "identity": ["identity.auth", "identity.oauth", "identity.webauthn"],
        "api": ["api.request", "api.orchestration", "api.consensus"],
        "consciousness": ["consciousness.decision", "consciousness.awareness"],
        "memory": ["memory.fold", "memory.retrieval", "memory.temporal"],
        "governance": ["governance.policy", "governance.ethics"],
        "matriz": ["matriz.processing", "matriz.symbolic"],
        "orchestration": ["orchestration.multi_ai", "orchestration.consensus"],
        "bridge": ["bridge.external", "bridge.oauth"]
    }

    return span_patterns.get(module_name, [f"lukhas.{module_name}.operation"])

def determine_team_ownership(module_name: str, legacy_data: dict[str, Any]) -> dict[str, Any]:
    """Determine appropriate team ownership"""

    # Team assignments based on domain
    team_mapping = {
        "consciousness": {"team": "Consciousness", "codeowners": ["@lukhas-consciousness", "@lukhas-core"]},
        "memory": {"team": "Memory", "codeowners": ["@lukhas-memory", "@lukhas-core"]},
        "identity": {"team": "Identity", "codeowners": ["@lukhas-identity", "@lukhas-security"]},
        "governance": {"team": "Governance", "codeowners": ["@lukhas-governance", "@lukhas-ethics"]},
        "matriz": {"team": "MATRIZ", "codeowners": ["@lukhas-matriz", "@lukhas-core"]},
        "api": {"team": "API", "codeowners": ["@lukhas-api", "@lukhas-integration"]},
        "orchestration": {"team": "Orchestration", "codeowners": ["@lukhas-orchestration", "@lukhas-ai"]},
        "bridge": {"team": "Integration", "codeowners": ["@lukhas-integration", "@lukhas-adapters"]},
        "quantum": {"team": "Quantum", "codeowners": ["@lukhas-quantum", "@lukhas-research"]},
        "core": {"team": "Core", "codeowners": ["@lukhas-core"]}
    }

    return team_mapping.get(module_name, {"team": "Core", "codeowners": ["@lukhas-core"]})

def enrich_manifest(module_dir: Path) -> bool:
    """Enrich a single module manifest with rich metadata"""
    manifest_file = module_dir / "module.manifest.json"
    if not manifest_file.exists():
        return False

    print(f"  Enriching {module_dir.name}...")

    manifest = load_json(manifest_file)
    legacy_data = manifest.get("x_legacy", {})
    module_name = manifest["module"]

    # Enrich description
    rich_description = extract_rich_description(module_name, legacy_data)
    manifest["description"] = rich_description

    # Enrich ownership
    rich_ownership = determine_team_ownership(module_name, legacy_data)
    manifest["ownership"] = rich_ownership

    # Enrich runtime entrypoints
    entrypoints = detect_module_entrypoints(module_dir)
    if entrypoints:
        manifest["runtime"]["entrypoints"] = entrypoints

    # Enrich tags
    rich_tags = extract_rich_tags(module_name, legacy_data)
    manifest["tags"] = rich_tags

    # Enrich dependencies
    dependencies = extract_dependencies(module_name, legacy_data)
    if dependencies:
        manifest["dependencies"] = dependencies

    # Enrich observability
    required_spans = extract_observability_spans(module_name, legacy_data)
    manifest["observability"]["required_spans"] = required_spans

    # Set MATRIZ lane from legacy data if available
    if legacy_data:
        dir_meta = legacy_data.get("directory_metadata", {})
        if dir_meta.get("lane") == "production":
            manifest["matrix"]["lane"] = "L1"
        elif dir_meta.get("lane") == "development":
            manifest["matrix"]["lane"] = "L2"
        elif dir_meta.get("lane") == "experimental":
            manifest["matrix"]["lane"] = "L3"

    # Save enriched manifest
    save_json(manifest_file, manifest)
    return True

def main():
    parser = argparse.ArgumentParser(description="Enrich module manifests with rich metadata")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--modules", nargs="*", help="Specific modules to enrich (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    root_dir = Path(args.root)
    enriched_count = 0

    print("🔍 Enriching module manifests with domain-specific metadata...")

    # Focus on key modules if none specified
    key_modules = ["consciousness", "memory", "identity", "governance", "matriz", "core", "api", "bridge", "orchestration", "quantum"]

    target_modules = args.modules if args.modules else key_modules

    for module_name in target_modules:
        module_dir = root_dir / module_name
        if module_dir.exists() and module_dir.is_dir():
            if args.dry_run:
                print(f"  Would enrich {module_name}")
            else:
                if enrich_manifest(module_dir):
                    enriched_count += 1
        else:
            print(f"  ⚠️  Module {module_name} not found")

    if not args.dry_run:
        print(f"✅ Enriched {enriched_count} module manifests")
    else:
        print(f"🏁 Dry run complete - would enrich {len(target_modules)} modules")

if __name__ == "__main__":
    main()
