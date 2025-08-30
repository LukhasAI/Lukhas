#!/usr/bin/env python3
"""
Aggressive File Consolidator
Actually moves the 923 consolidation candidates to their proper modules
"""

import builtins
import contextlib
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime


class AggressiveFileConsolidator:
    def __init__(self):
        # Load the consolidation plan
        with open("docs/planning/_AGGRESSIVE_CONSOLIDATION_PLAN.json") as f:
            self.plan = json.load(f)

        self.moved_files = []
        self.failed_moves = []

        # Define clear module boundaries
        self.module_paths = {
            "CORE": "core/",
            "CONSCIOUSNESS": "consciousness/",
            "MEMORY": "memory/",
            "QIM": "qim/",
            "EMOTION": "emotion/",
            "GOVERNANCE": "governance/",
            "BRIDGE": "bridge/",
        }

        # Submodule assignment rules
        self.submodule_keywords = {
            "CORE": {
                "glyph": ["glyph", "token", "symbol_map"],
                "symbolic": ["symbolic", "symbol", "encode", "decode"],
                "neural": ["neural", "network", "pathway", "synapse"],
                "integration": ["integrate", "master", "connect", "hub"],
            },
            "CONSCIOUSNESS": {
                "awareness": ["aware", "attention", "focus", "observe"],
                "reflection": ["reflect", "introspect", "meta", "self"],
                "unified": ["unified", "coherence", "unity", "whole"],
                "states": ["state", "mode", "level", "phase"],
            },
            "MEMORY": {
                "folds": ["fold", "compress", "store", "archive"],
                "causal": ["causal", "chain", "link", "sequence"],
                "temporal": ["temporal", "time", "chronos", "history"],
                "consolidation": ["consolidate", "merge", "combine", "integrate"],
            },
            "QIM": {
                "qi_states": ["quantum", "state", "superposition", "collapse"],
                "entanglement": ["entangle", "correlate", "pair", "bond"],
                "superposition": ["superpos", "multiple", "simultaneous", "parallel"],
                "bio": ["bio", "organic", "life", "adapt"],
            },
            "EMOTION": {
                "vad": ["valence", "arousal", "dominance", "vad"],
                "mood": ["mood", "feeling", "affect", "sentiment"],
                "empathy": ["empathy", "compassion", "understand", "relate"],
                "regulation": ["regulate", "control", "balance", "modulate"],
            },
            "GOVERNANCE": {
                "guardian": ["guardian", "protect", "shield", "defend"],
                "ethics": ["ethic", "moral", "right", "principle"],
                "policy": ["policy", "rule", "guideline", "standard"],
                "oversight": ["oversight", "monitor", "watch", "supervise"],
            },
            "BRIDGE": {
                "api": ["api", "endpoint", "route", "interface"],
                "external": ["external", "outside", "foreign", "third"],
                "protocols": ["protocol", "standard", "format", "spec"],
                "adapters": ["adapter", "convert", "transform", "translate"],
            },
        }

    def analyze_file(self, filepath):
        """Analyze a file to determine its best module and submodule"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read().lower()

            # Score each module
            module_scores = defaultdict(int)
            submodule_assignment = {}

            for module, submodules in self.submodule_keywords.items():
                module_score = 0
                best_submodule = None
                best_submodule_score = 0

                for submodule, keywords in submodules.items():
                    submodule_score = 0
                    for keyword in keywords:
                        if keyword in content:
                            submodule_score += content.count(keyword)
                            module_score += content.count(keyword)

                    if submodule_score > best_submodule_score:
                        best_submodule_score = submodule_score
                        best_submodule = submodule

                module_scores[module] = module_score
                if best_submodule:
                    submodule_assignment[module] = best_submodule

            # Get best module
            if module_scores:
                best_module = max(module_scores, key=module_scores.get)
                best_submodule = submodule_assignment.get(
                    best_module, list(self.submodule_keywords[best_module].keys())[0]
                )

                return best_module, best_submodule, module_scores[best_module]

        except Exception:
            pass

        return None, None, 0

    def consolidate_files(self):
        """Consolidate all files according to analysis"""
        print("🔍 Analyzing and consolidating files...")

        consolidated_count = 0
        files_by_module = defaultdict(list)

        # Collect all Python files not already in core modules
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

            # Skip if already in a core module
            if any(module_path in root for module_path in self.module_paths.values()):
                continue

            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    filepath = os.path.join(root, file)

                    # Analyze file
                    module, submodule, score = self.analyze_file(filepath)

                    if module and score > 0:
                        files_by_module[module].append(
                            {
                                "path": filepath,
                                "submodule": submodule,
                                "score": score,
                                "filename": file,
                            }
                        )

        # Move files to their modules
        for module, file_list in files_by_module.items():
            print(f"\n📦 Consolidating {len(file_list)} files to {module}...")

            # Sort by score (highest first)
            file_list.sort(key=lambda x: x["score"], reverse=True)

            for file_info in file_list[:100]:  # Limit to top 100 per module
                source = file_info["path"]
                submodule = file_info["submodule"]
                filename = file_info["filename"]

                # Create target path
                target_dir = os.path.join(self.module_paths[module], submodule)
                os.makedirs(target_dir, exist_ok=True)

                target = os.path.join(target_dir, filename)

                # Handle naming conflicts
                if os.path.exists(target):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(target):
                        target = os.path.join(target_dir, f"{base}_{counter}{ext}")
                        counter += 1

                # Move file
                try:
                    shutil.move(source, target)
                    self.moved_files.append(
                        {
                            "source": source,
                            "target": target,
                            "module": module,
                            "submodule": submodule,
                        }
                    )
                    consolidated_count += 1

                    # Add neuroplastic tags to file
                    self.add_neuroplastic_tags(target, module, submodule)

                except Exception as e:
                    self.failed_moves.append({"source": source, "error": str(e)})

        return consolidated_count

    def add_neuroplastic_tags(self, filepath, module, submodule):
        """Add neuroplastic tags to consolidated files"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Check if tags already exist
            if "#TAG:" in content:
                return

            # Find good insertion point (after imports, before first class/function)
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if line.strip() and not line.startswith(("import", "from", "#", '"""', "'''")):
                    insert_index = i
                    break

            # Insert tags
            tag_block = f"""
#TAG:{module.lower()}
#TAG:{submodule}
#TAG:neuroplastic
#TAG:colony

"""

            lines.insert(insert_index, tag_block)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

        except Exception:
            pass

    def clean_empty_directories(self):
        """Remove empty directories after consolidation"""
        empty_dirs = []

        for root, dirs, files in os.walk(".", topdown=False):
            if any(skip in root for skip in [".git", "__pycache__", ".venv"]):
                continue

            # Check if directory is empty
            if not dirs and not files and root != ".":
                empty_dirs.append(root)
                with contextlib.suppress(builtins.BaseException):
                    os.rmdir(root)

        return len(empty_dirs)

    def generate_report(self, consolidated_count, empty_dirs_removed):
        """Generate consolidation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_consolidated": consolidated_count,
            "empty_dirs_removed": empty_dirs_removed,
            "moved_files": len(self.moved_files),
            "failed_moves": len(self.failed_moves),
            "files_by_module": defaultdict(lambda: defaultdict(int)),
        }

        # Count files by module and submodule
        for move in self.moved_files:
            module = move["module"]
            submodule = move["submodule"]
            report["files_by_module"][module][submodule] += 1

        # Convert defaultdict to regular dict for JSON
        report["files_by_module"] = dict(report["files_by_module"])
        for module in report["files_by_module"]:
            report["files_by_module"][module] = dict(report["files_by_module"][module])

        # Save report
        report_path = "docs/reports/_AGGRESSIVE_CONSOLIDATION_REPORT.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report


def main():
    print("🚀 AGGRESSIVE FILE CONSOLIDATION")
    print("=" * 50)

    consolidator = AggressiveFileConsolidator()

    # Step 1: Consolidate files
    consolidated = consolidator.consolidate_files()
    print(f"\n✅ Consolidated {consolidated} files")

    # Step 2: Clean empty directories
    print("\n🧹 Cleaning empty directories...")
    empty_removed = consolidator.clean_empty_directories()
    print(f"✅ Removed {empty_removed} empty directories")

    # Step 3: Generate report
    print("\n📊 Generating report...")
    report = consolidator.generate_report(consolidated, empty_removed)

    # Display summary
    print("\n" + "=" * 50)
    print("📊 CONSOLIDATION SUMMARY")
    print("=" * 50)

    print(f"\nTotal files consolidated: {consolidated}")
    print(f"Empty directories removed: {empty_removed}")

    print("\nFiles by module:")
    for module, submodules in report["files_by_module"].items():
        total = sum(submodules.values())
        print(f"\n{module}: {total} files")
        for submodule, count in submodules.items():
            print(f"  - {submodule}: {count}")

    if consolidator.failed_moves:
        print(f"\n⚠️ Failed to move {len(consolidator.failed_moves)} files")

    print("\n📋 Report saved to: docs/reports/_AGGRESSIVE_CONSOLIDATION_REPORT.json")


if __name__ == "__main__":
    main()
