#!/usr/bin/env python3
"""
LUKHAS  Aggressive Consolidation Analyzer
Identifies and maps all files for aggressive modular consolidation
"""
from consciousness.qi import qi
import time
import streamlit as st

import ast
import json
import os
from collections import defaultdict
from datetime import datetime, timezone


class AggressiveConsolidator:
    def __init__(self):
        self.core_modules = {
            "CORE": {
                "path": "core/",
                "description": "Central nervous system - GLYPH engine, symbolic processing",
                "submodules": ["glyph", "symbolic", "neural", "integration"],
                "hybrid": ["symbolic", "neural"],  # These exist in multiple modules
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
                "submodules": [
                    "qi_states",
                    "entanglement",
                    "superposition",
                    "bio",
                ],
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

        self.file_mapping = defaultdict(list)
        self.orphaned_files = []
        self.consolidation_candidates = defaultdict(list)

    def analyze_workspace(self):
        """Analyze entire workspace for consolidation"""
        print("🔍 Analyzing LUKHAS  workspace for aggressive consolidation...")

        total_files = 0

        for root, _dirs, files in os.walk("."):
            # Skip certain directories
            if any(
                skip in root
                for skip in [
                    ".git",
                    "__pycache__",
                    ".venv",
                    "quarantine",
                    "._cleanup_archive",
                ]
            ):
                continue

            for file in files:
                if file.endswith(".py"):
                    total_files += 1
                    filepath = os.path.join(root, file)
                    self.categorize_file(filepath)

        print(f"\n📊 Total Python files analyzed: {total_files}")
        return self.generate_consolidation_plan()

    def categorize_file(self, filepath):
        """Categorize a file into appropriate module"""
        path_parts = filepath.split(os.sep)

        # Check if file belongs to a core module
        module_found = False
        for module_name, module_info in self.core_modules.items():
            if module_info["path"].rstrip("/") in path_parts:
                self.file_mapping[module_name].append(filepath)
                module_found = True
                break

        if not module_found:
            # Analyze file content to determine best module
            suggested_module = self.analyze_file_content(filepath)
            if suggested_module:
                self.consolidation_candidates[suggested_module].append(filepath)
            else:
                self.orphaned_files.append(filepath)

    def analyze_file_content(self, filepath):
        """Analyze file content to suggest appropriate module"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read().lower()

            # Keywords for each module
            module_keywords = {
                "CORE": ["glyph", "symbolic", "neural", "engine", "processor"],
                "CONSCIOUSNESS": ["awareness", "conscious", "reflection", "decision"],
                "MEMORY": ["memory", "fold", "recall", "temporal", "storage"],
                "QIM": ["quantum", "superposition", "entangle", "wave", "collapse"],
                "EMOTION": ["emotion", "feeling", "mood", "affect", "empathy"],
                "GOVERNANCE": ["governance", "guardian", "ethics", "policy", "safety"],
                "BRIDGE": ["api", "bridge", "external", "interface", "connect"],
            }

            # Count keyword matches
            scores = {}
            for module, keywords in module_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content)
                if score > 0:
                    scores[module] = score

            # Return module with highest score
            if scores:
                return max(scores, key=scores.get)

            # Check imports for hints
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            for module in self.core_modules:
                                if module.lower() in alias.name.lower():
                                    return module
            except BaseException:
                pass

        except Exception:
            pass

        return None

    def generate_consolidation_plan(self):
        """Generate aggressive consolidation plan"""
        plan = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis": {},
            "consolidation_actions": [],
            "hybrid_modules": {},
        }

        # Analyze current distribution
        for module_name, files in self.file_mapping.items():
            module_info = self.core_modules[module_name]
            plan["analysis"][module_name] = {
                "current_files": len(files),
                "candidates_for_consolidation": len(self.consolidation_candidates.get(module_name, [])),
                "submodules": module_info["submodules"],
                "hybrid_submodules": module_info["hybrid"],
            }

        # Create consolidation actions
        for module_name, candidates in self.consolidation_candidates.items():
            if candidates:
                plan["consolidation_actions"].append(
                    {
                        "action": "MOVE_FILES",
                        "target_module": module_name,
                        "files": candidates[:10],  # Show first 10
                        "total_files": len(candidates),
                        "reason": "Content analysis suggests these files belong to this module",
                    }
                )

        # Define hybrid modules
        for module_name, module_info in self.core_modules.items():
            for hybrid in module_info["hybrid"]:
                f"{module_name}.{hybrid}"
                if hybrid not in plan["hybrid_modules"]:
                    plan["hybrid_modules"][hybrid] = {
                        "description": "Hybrid submodule existing in quantum superposition",
                        "primary_module": module_name,
                        "also_exists_in": [],
                    }
                else:
                    plan["hybrid_modules"][hybrid]["also_exists_in"].append(module_name)

        # Orphaned files
        if self.orphaned_files:
            plan["orphaned_files"] = {
                "count": len(self.orphaned_files),
                "sample": self.orphaned_files[:20],
                "recommendation": "Review and assign to appropriate modules or archive",
            }

        return plan

    def create_module_manifest(self, module_name):
        """Create a manifest for a module"""
        module_info = self.core_modules[module_name]
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
                "hormone_receptors": ["cortisol", "dopamine", "serotonin"],
            },
        }

        # Define submodules
        for submodule in module_info["submodules"]:
            manifest["submodules"][submodule] = {
                "description": f"{submodule} subsystem of {module_name}",
                "is_hybrid": submodule in module_info["hybrid"],
                "files": [],
            }

        return manifest

    def execute_consolidation(self, plan):
        """Execute the consolidation plan"""
        print("\n🔨 Executing aggressive consolidation...")

        # Create module manifests
        for module_name in self.core_modules:
            manifest_path = os.path.join(self.core_modules[module_name]["path"], "MODULE_MANIFEST.json")
            manifest = self.create_module_manifest(module_name)

            os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"✅ Created manifest for {module_name}")

        # Move files according to plan
        moved_count = 0
        for action in plan["consolidation_actions"]:
            if action["action"] == "MOVE_FILES":
                target_path = self.core_modules[action["target_module"]]["path"]
                for file in action["files"]:
                    try:
                        # Determine submodule based on content
                        submodule = self.determine_submodule(file, action["target_module"])
                        new_path = os.path.join(target_path, submodule, os.path.basename(file))

                        os.makedirs(os.path.dirname(new_path), exist_ok=True)

                        # Move file
                        if os.path.exists(file) and not os.path.exists(new_path):
                            os.rename(file, new_path)
                            moved_count += 1
                    except Exception as e:
                        print(f"⚠️ Could not move {file}: {e}")

        print(f"\n✅ Moved {moved_count} files to their proper modules")

        return moved_count

    def determine_submodule(self, filepath, module_name):
        """Determine which submodule a file belongs to"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read().lower()

            submodules = self.core_modules[module_name]["submodules"]

            # Simple keyword matching for submodule assignment
            for submodule in submodules:
                if submodule in content:
                    return submodule

            # Default to first submodule
            return submodules[0]

        except BaseException:
            return self.core_modules[module_name]["submodules"][0]


def main():
    consolidator = AggressiveConsolidator()

    # Analyze workspace
    plan = consolidator.analyze_workspace()

    # Save plan
    plan_path = "docs/planning/_AGGRESSIVE_CONSOLIDATION_PLAN.json"
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    with open(plan_path, "w") as f:
        json.dump(plan, f, indent=2)

    print(f"\n📋 Consolidation plan saved to: {plan_path}")

    # Show summary
    print("\n📊 CONSOLIDATION SUMMARY")
    print("=" * 50)

    for module, analysis in plan["analysis"].items():
        print(f"\n{module}:")
        print(f"  Current files: {analysis['current_files']}")
        print(f"  Consolidation candidates: {analysis['candidates_for_consolidation']}")
        print(f"  Hybrid submodules: {', '.join(analysis['hybrid_submodules'])}")

    if "orphaned_files" in plan:
        print(f"\n🔍 Orphaned files: {plan['orphaned_files']['count']}")

    print(f"\n🧬 Hybrid modules identified: {len(plan['hybrid_modules'])}")
    for hybrid, info in plan["hybrid_modules"].items():
        print(f"  - {hybrid}: Primary in {info['primary_module']}, also in {info['also_exists_in']}")

    # Ask to execute
    print("\n" + "=" * 50)
    print("Ready to execute aggressive consolidation?")
    print("This will:")
    print("  1. Create MODULE_MANIFEST.json in each core module")
    print("  2. Move files to their appropriate modules")
    print("  3. Organize files into submodules")
    print("\nType 'yes' to proceed: ", end="")

    response = input().strip().lower()
    if response == "yes":
        moved = consolidator.execute_consolidation(plan)
        print(f"\n✅ Consolidation complete! Moved {moved} files.")
    else:
        print("\n❌ Consolidation cancelled.")


if __name__ == "__main__":
    main()
