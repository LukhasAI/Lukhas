#!/usr/bin/env python3
"""
Execute Aggressive Consolidation
Automatically consolidates files according to the plan
"""

import json
import os
import shutil
from datetime import datetime


def load_consolidation_plan():
    """Load the consolidation plan"""
    plan_path = "docs/planning/_AGGRESSIVE_CONSOLIDATION_PLAN.json"
    with open(plan_path) as f:
        return json.load(f)


def create_module_manifests():
    """Create MODULE_MANIFEST.json for each core module"""
    core_modules = {
        "CORE": {
            "path": "core/",
            "description": "Central nervous system - GLYPH engine, symbolic processing",
            "submodules": ["glyph", "symbolic", "neural", "integration"],
            "hybrid": ["symbolic", "neural"],
        },
        "CONSCIOUSNESS": {
            "path": "consciousness/",
            "description": "Awareness, reflection, decision-making cortex",
            "submodules": ["awareness", "reflection", "unified", "states"],
            "hybrid": ["states", "reflection"],
        },
        "MEMORY": {
            "path": "memory/",
            "description": "Fold-based memory with causal chains",
            "submodules": ["folds", "causal", "temporal", "consolidation"],
            "hybrid": ["temporal", "causal"],
        },
        "QIM": {
            "path": "qim/",
            "description": "Quantum-Inspired Metaphors for advanced processing",
            "submodules": ["qi_states", "entanglement", "superposition", "bio"],
            "hybrid": ["superposition", "entanglement"],
        },
        "EMOTION": {
            "path": "emotion/",
            "description": "VAD affect and mood regulation",
            "submodules": ["vad", "mood", "empathy", "regulation"],
            "hybrid": ["empathy", "mood"],
        },
        "GOVERNANCE": {
            "path": "governance/",
            "description": "Guardian system and ethical oversight",
            "submodules": ["guardian", "ethics", "policy", "oversight"],
            "hybrid": ["ethics", "policy"],
        },
        "BRIDGE": {
            "path": "bridge/",
            "description": "External API connections and interfaces",
            "submodules": ["api", "external", "protocols", "adapters"],
            "hybrid": ["protocols", "adapters"],
        },
    }

    manifests_created = 0

    for module_name, module_info in core_modules.items():
        manifest = {
            "module": module_name,
            "version": "2.0.0",
            "description": module_info["description"],
            "path": module_info["path"],
            "submodules": {},
            "hybrid_components": module_info["hybrid"],
            "dependencies": [],
            "exports": [],
            "neuroplastic_config": {
                "can_reorganize": True,
                "stress_priority": 1,
                "hormone_receptors": ["cortisol", "dopamine", "serotonin", "oxytocin"],
            },
            "tags": ["#TAG:" + module_name.lower(), "#TAG:neuroplastic", "#TAG:colony"],
        }

        # Define submodules
        for submodule in module_info["submodules"]:
            manifest["submodules"][submodule] = {
                "description": f"{submodule} subsystem of {module_name}",
                "is_hybrid": submodule in module_info["hybrid"],
                "path": f"{module_info['path']}{submodule}/",
                "files": [],
                "colony_config": {
                    "can_propagate": True,
                    "base_colony": f"base_{submodule}_colony.py",
                },
            }

        # Create manifest file
        manifest_path = os.path.join(module_info["path"], "MODULE_MANIFEST.json")
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"✅ Created manifest for {module_name}")
        manifests_created += 1

        # Create submodule directories
        for submodule in module_info["submodules"]:
            submodule_path = os.path.join(module_info["path"], submodule)
            os.makedirs(submodule_path, exist_ok=True)

            # Create __init__.py for each submodule
            init_path = os.path.join(submodule_path, "__init__.py")
            if not os.path.exists(init_path):
                init_content = f'''"""
{module_name} - {submodule} Submodule
{"Hybrid component - exists in quantum superposition" if submodule in module_info["hybrid"] else ""}
#TAG:{module_name.lower()}
#TAG:{submodule}
#TAG:{"hybrid" if submodule in module_info["hybrid"] else "standard"}
"""

# Colony base for propagation
from typing import Any, Dict, List

class {submodule.title()}Colony:
    """Base colony for {submodule} components"""

    def __init__(self):
        self.colony_id = "{module_name}_{submodule}"
        self.propagation_enabled = True
        self.hormone_state = {{
            'cortisol': 0.0,
            'dopamine': 0.5,
            'serotonin': 0.5,
            'oxytocin': 0.3
        }

    def propagate(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Propagate signal through colony"""
        return {{
            'colony_id': self.colony_id,
            'signal': signal,
            'hormone_modulation': self.hormone_state
        }

# Initialize colony
colony = {submodule.title()}Colony()
'''
                with open(init_path, "w") as f:
                    f.write(init_content)

    return manifests_created


def create_hybrid_links():
    """Create symbolic links for hybrid components"""
    hybrid_components = {
        "symbolic": ["core", "consciousness"],
        "neural": ["core", "bridge"],
        "states": ["consciousness", "qim"],
        "reflection": ["consciousness", "memory"],
        "temporal": ["memory", "qim"],
        "causal": ["memory", "governance"],
        "superposition": ["qim", "consciousness"],
        "entanglement": ["qim", "bridge"],
        "empathy": ["emotion", "consciousness"],
        "mood": ["emotion", "governance"],
        "ethics": ["governance", "consciousness"],
        "policy": ["governance", "bridge"],
        "protocols": ["bridge", "core"],
        "adapters": ["bridge", "qim"],
    }

    links_created = 0

    for component, modules in hybrid_components.items():
        if len(modules) >= 2:
            # Create hybrid marker file in primary module
            primary = modules[0]
            marker_path = f"{primary}/{component}/HYBRID_COMPONENT.json"

            os.makedirs(os.path.dirname(marker_path), exist_ok=True)

            hybrid_info = {
                "component": component,
                "type": "hybrid",
                "primary_module": primary,
                "also_exists_in": modules[1:],
                "qi_state": "superposition",
                "description": "This component exists in multiple modules simultaneously",
            }

            with open(marker_path, "w") as f:
                json.dump(hybrid_info, f, indent=2)

            links_created += 1
            print(f"🔗 Created hybrid marker for {component}")

    return links_created


def consolidate_orphaned_files():
    """Move orphaned files to appropriate modules"""
    # Common directories that often contain orphaned files
    orphan_sources = [
        "architectures/",
        "systems/",
        "modules/",
        "components/",
        "tools/",
        "utils/",
        "helpers/",
        "services/",
    ]

    moved_count = 0

    # Module assignment rules based on content
    assignment_rules = {
        "api": "BRIDGE",
        "memory": "MEMORY",
        "quantum": "QIM",
        "conscious": "CONSCIOUSNESS",
        "emotion": "EMOTION",
        "govern": "GOVERNANCE",
        "glyph": "CORE",
        "symbolic": "CORE",
        "neural": "CORE",
    }

    for source in orphan_sources:
        if os.path.exists(source):
            for root, _dirs, files in os.walk(source):
                for file in files:
                    if file.endswith(".py") and not file.startswith("test_"):
                        filepath = os.path.join(root, file)

                        # Determine target module
                        target_module = None
                        file_lower = file.lower()

                        for keyword, module in assignment_rules.items():
                            if keyword in file_lower:
                                target_module = module
                                break

                        if target_module:
                            # Move to appropriate module
                            module_paths = {
                                "CORE": "core/integration/",
                                "CONSCIOUSNESS": "consciousness/unified/",
                                "MEMORY": "memory/consolidation/",
                                "QIM": "qim/qi_states/",
                                "EMOTION": "emotion/regulation/",
                                "GOVERNANCE": "governance/oversight/",
                                "BRIDGE": "bridge/adapters/",
                            }

                            target_path = module_paths[target_module]
                            os.makedirs(target_path, exist_ok=True)

                            new_filepath = os.path.join(target_path, file)

                            try:
                                if not os.path.exists(new_filepath):
                                    shutil.move(filepath, new_filepath)
                                    moved_count += 1
                                    print(f"  ➡️ Moved {file} to {target_module}")
                            except Exception:
                                pass

    return moved_count


def update_imports():
    """Update imports to reflect new structure"""
    # This would be more complex in practice, but here's a simple version
    updates_needed = []

    for root, _dirs, files in os.walk("."):
        if any(skip in root for skip in [".git", "__pycache__", ".venv", "quarantine"]):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()

                    # Check for old import patterns
                    if "from qi" in content and "from qim" not in content:
                        updates_needed.append({"file": filepath, "old": "from qi", "new": "from qim"})
                except BaseException:
                    pass

    return updates_needed


def main():
    print("🚀 EXECUTING AGGRESSIVE CONSOLIDATION")
    print("=" * 50)

    # Load plan
    plan = load_consolidation_plan()

    print("\n📊 Consolidation targets:")
    total_candidates = sum(info["candidates_for_consolidation"] for info in plan["analysis"].values())
    print(f"  - Total consolidation candidates: {total_candidates}")
    print(f"  - Orphaned files: {plan.get('orphaned_files', {)}).get('count', 0)}")

    # Step 1: Create module manifests and structure
    print("\n📝 Creating module manifests...")
    manifests = create_module_manifests()
    print(f"  ✅ Created {manifests} module manifests")

    # Step 2: Create hybrid component markers
    print("\n🔗 Setting up hybrid components...")
    hybrids = create_hybrid_links()
    print(f"  ✅ Created {hybrids} hybrid component markers")

    # Step 3: Consolidate orphaned files
    print("\n📦 Consolidating orphaned files...")
    moved = consolidate_orphaned_files()
    print(f"  ✅ Moved {moved} orphaned files to appropriate modules")

    # Step 4: Check for import updates needed
    print("\n🔍 Checking imports...")
    updates = update_imports()
    print(f"  ⚠️ Found {len(updates)} files needing import updates")

    # Summary
    print("\n" + "=" * 50)
    print("✅ AGGRESSIVE CONSOLIDATION COMPLETE!")
    print("\nSummary:")
    print(f"  - Module manifests created: {manifests}")
    print(f"  - Hybrid components linked: {hybrids}")
    print(f"  - Files consolidated: {moved}")
    print(f"  - Import updates needed: {len(updates)}")

    # Save consolidation report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "manifests_created": manifests,
        "hybrid_components": hybrids,
        "files_moved": moved,
        "import_updates_needed": len(updates),
        "next_steps": [
            "Run import updater to fix old imports",
            "Test all modules for functionality",
            "Create integration tests for hybrid components",
            "Document new modular architecture",
        ],
    }

    report_path = "docs/reports/_CONSOLIDATION_REPORT.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📋 Report saved to: {report_path}")


if __name__ == "__main__":
    main()