#!/usr/bin/env python3
"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


SMART CONSOLIDATION - Only merge truly compatible files

This script analyzes file content and purpose before merging,
avoiding incompatible combinations like trauma repair + API services.
"""
import streamlit as st

import ast
from collections import defaultdict
from pathlib import Path


class SmartConsolidator:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.archived_path = root_path / "archived" / "pre_consolidation"

    def analyze_file_purpose(self, file_path: Path) -> dict[str, any]:
        """Analyze what a file actually does"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to understand structure
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return {"type": "unparseable", "classes": [], "functions": []}

            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

            # Categorize by actual purpose
            purpose = self._categorize_purpose(file_path.name, content, classes, functions)

            return {
                "type": purpose,
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "size": len(content),
                "has_main": "__main__" in content,
                "is_config": any(x in content.lower() for x in ["config", "settings", "yaml", "json"]),
                "is_test": any(x in file_path.name.lower() for x in ["test", "spec"]),
                "is_api": any(x in content.lower() for x in ["fastapi", "flask", "endpoint", "router"]),
                "is_database": any(x in content.lower() for x in ["sqlalchemy", "database", "db", "crud"]),
                "is_ui": any(x in content.lower() for x in ["streamlit", "html", "css", "javascript"]),
            }
        except Exception as e:
            return {"type": "error", "error": str(e)}

    def _categorize_purpose(self, filename: str, content: str, classes: list[str], functions: list[str]) -> str:
        """Determine the actual purpose of a file"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # Very specific purposes that should NOT be merged
        if "trauma" in filename_lower or "repair" in filename_lower:
            return "trauma_repair"
        if "resonance" in filename_lower:
            return "resonance_system"
        if "semantic" in filename_lower and "extract" in filename_lower:
            return "semantic_extraction"
        if "api" in filename_lower and any(x in content_lower for x in ["fastapi", "router", "endpoint"]):
            return "api_service"
        if "service" in filename_lower and any(x in content_lower for x in ["class", "def start", "def stop"]):
            return "system_service"
        if "bridge" in filename_lower:
            return "system_bridge"
        if "adapter" in filename_lower:
            return "system_adapter"
        if "validator" in filename_lower or "validation" in filename_lower:
            return "validation_system"
        if "processor" in filename_lower:
            return "data_processor"
        if "manager" in filename_lower:
            return "resource_manager"
        if "client" in filename_lower:
            return "api_client"
        if "db" in filename_lower or "database" in filename_lower:
            return "database_system"
        if "auth" in filename_lower or "login" in filename_lower:
            return "auth_system"
        if "config" in filename_lower or "settings" in filename_lower:
            return "configuration"
        if "test" in filename_lower:
            return "test_file"
        if "demo" in filename_lower or "example" in filename_lower:
            return "demo_example"

        # Only merge truly generic engines
        if "engine" in filename_lower and not any(
            specific in filename_lower for specific in ["trauma", "resonance", "semantic", "api", "bridge", "auth"]
        ):
            return "generic_engine"

        return "specific_component"

    def find_safe_merges(self) -> dict[str, list[Path]]:
        """Find files that can safely be merged together"""
        if not self.archived_path.exists():
            print("No archived files found - run consolidation first")
            return {}

        # Analyze all archived files
        file_analysis = {}
        for file_path in self.archived_path.rglob("*.py"):
            if file_path.is_file():
                analysis = self.analyze_file_purpose(file_path)
                file_analysis[file_path] = analysis

        # Group by compatible types only
        safe_groups = defaultdict(list)

        for file_path, analysis in file_analysis.items():
            file_type = analysis["type"]

            # Only group files with the same specific purpose
            # AND that are actually safe to merge
            if file_type in ["generic_engine", "configuration", "demo_example"]:
                safe_groups[file_type].append(file_path)
            # else: keep as individual files

        # Filter out groups with only 1 file
        return {k: v for k, v in safe_groups.items() if len(v) > 2}

    def undo_bad_consolidation(self):
        """Restore incorrectly consolidated files back to their original locations"""
        print("🔄 UNDOING INCORRECT CONSOLIDATION")
        print("=" * 50)

        if not self.archived_path.exists():
            print("No archived files found")
            return

        restored_count = 0

        # Restore all archived files to their original locations
        for archived_file in self.archived_path.rglob("*.py"):
            if archived_file.is_file():
                # Get relative path from archived location
                relative_path = archived_file.relative_to(self.archived_path)
                original_location = self.root_path / relative_path

                # Skip if it would overwrite existing file
                if original_location.exists():
                    continue

                # Create directory if needed
                original_location.parent.mkdir(parents=True, exist_ok=True)

                # Copy file back
                import shutil

                shutil.copy2(archived_file, original_location)
                print(f"✅ Restored: {relative_path}")
                restored_count += 1

        print(f"\n🎉 Restored {restored_count} files to original locations")

        # Remove the bad consolidated files
        bad_dirs = ["dream", "engines", "memory"]
        for dir_name in bad_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                # Only remove consolidated files, keep original ones
                for file in dir_path.glob("*.py"):
                    if file.name in [
                        "core_engine.py",
                        "commerce_api.py",
                        "visualization.py",
                        "consciousness_engine.py",
                        "creative_engine.py",
                        "identity_engine.py",
                        "learning_engine.py",
                        "communication_engine.py",
                        "unified_memory_core.py",
                        "memory_colonies.py",
                        "memory_visualization.py",
                        "episodic_memory.py",
                    ]:
                        file.unlink()
                        print(f"🗑️  Removed bad consolidation: {file}")

    def generate_smart_consolidation_plan(self):
        """Generate a plan that only merges truly compatible files"""
        safe_merges = self.find_safe_merges()

        print("🧠 SMART CONSOLIDATION ANALYSIS")
        print("=" * 50)
        print("Files that should NOT be merged:")

        if not self.archived_path.exists():
            print("No archived files to analyze")
            return

        incompatible_files = []
        for file_path in self.archived_path.rglob("*.py"):
            if file_path.is_file():
                analysis = self.analyze_file_purpose(file_path)
                if analysis["type"] in [
                    "trauma_repair",
                    "resonance_system",
                    "semantic_extraction",
                    "api_service",
                    "system_service",
                    "system_bridge",
                    "auth_system",
                    "database_system",
                    "validation_system",
                ]:
                    incompatible_files.append((file_path, analysis["type"]))

        print(f"\n❌ Files that should remain separate ({len(incompatible_files)}):")
        for file_path, file_type in incompatible_files[:20]:  # Show first 20
            relative_path = file_path.relative_to(self.archived_path)
            print(f"  - {relative_path} ({file_type})")

        if len(incompatible_files) > 20:
            print(f"  ... and {len(incompatible_files)} - 20} more")

        print(f"\n✅ Safe merges found ({len(safe_merges)} groups):")
        for group_type, files in safe_merges.items():
            print(f"  - {group_type}: {len(files)} files can be safely merged")

        return safe_merges


def main():
    root_path = Path(__file__).parent
    consolidator = SmartConsolidator(root_path)

    print("🧠 SMART CONSOLIDATION TOOL")
    print("Fixes the overly aggressive consolidation")
    print("=" * 50)

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--undo":
        consolidator.undo_bad_consolidation()
    else:
        consolidator.generate_smart_consolidation_plan()
        print("\nTo undo the bad consolidation, run:")
        print("python3 smart_consolidation.py --undo")


if __name__ == "__main__":
    main()