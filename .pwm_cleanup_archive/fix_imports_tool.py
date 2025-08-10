#!/usr/bin/env python3
"""
LUKHAS Import Fixer Tool
Intelligently fixes import statements after reorganization
"""

import ast
import json
import re
from pathlib import Path
from typing import Optional


class ImportFixer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.file_moves = {}
        self.module_mapping = {}
        self.import_updates = []

        # Track where files moved to
        self.reorganization_map = {
            # Dream system moves
            "core.utils.dream_utils": "dream.core.dream_utils",
            "core.bridges.nias_dream_bridge": "dream.core.nias_dream_bridge",
            "core.interfaces.tools.cli.dream_cli": "dream.core.dream_cli",
            "memory.dream_memory_manager": "dream.core.dream_memory_manager",
            "creativity.dream": "dream",
            "creativity.dream_systems": "dream.core",
            # Memory system moves
            "memory.manager": "memory.core.quantum_memory_manager",
            "memory.base_manager": "memory.core.base_manager",
            "memory.enhanced_memory_fold": "memory.fold_system.enhanced_memory_fold",
            "memory.systems.memory_fold_system": "memory.fold_system.memory_fold_system",
            "memory.episodic_memory": "memory.episodic.episodic_memory",
            "memory.systems.episodic_replay_buffer": "memory.episodic.episodic_replay_buffer",
            "memory.systems.memory_consolidation": "memory.consolidation.memory_consolidation",
            "memory.systems.memory_consolidator": "memory.consolidation.memory_consolidator",
            # Personality moves
            "orchestration.brain.brain": "personality.brain.brain",
            "voice.voice_narrator": "personality.voice.voice_narrator",
            "creativity.creative_core": "personality.creative_core.creative_core",
            "consciousness.systems.cognitive_systems.voice_personality": "personality.voice.voice_personality",
            "dream.dream_narrator_queue": "personality.narrative_engine.dream_narrator_queue",
        }

        # Common import patterns to fix
        self.import_patterns = [
            (r"from creativity\.dream", "from dream"),
            (r"import creativity\.dream", "import dream"),
            (
                r"from memory\.manager import",
                "from memory.core.quantum_memory_manager import",
            ),
            (r"from orchestration\.brain\.brain", "from personality.brain"),
        ]

    def scan_and_fix_imports(self):
        """Main entry point to fix all imports"""
        print("🔍 Scanning for Python files with broken imports...")

        # First, build a complete file mapping
        self._build_file_mapping()

        # Then fix imports in all Python files
        fixed_count = 0
        error_count = 0

        for py_file in self.root_path.rglob("*.py"):
            if any(
                skip in str(py_file)
                for skip in ["__pycache__", ".git", "venv", "node_modules"]
            ):
                continue

            try:
                if self._fix_file_imports(py_file):
                    fixed_count += 1
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing {py_file}: {e}")

        print(f"\n✅ Fixed imports in {fixed_count} files")
        print(f"❌ Errors in {error_count} files")

        # Save report
        self._save_report()

    def _build_file_mapping(self):
        """Build a mapping of all Python modules"""
        print("📦 Building module mapping...")

        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ["__pycache__", ".git", "venv"]):
                continue

            relative_path = py_file.relative_to(self.root_path)
            module_path = str(relative_path).replace(".py", "").replace("/", ".")

            # Skip __init__ files in mapping
            if module_path.endswith(".__init__"):
                module_path = module_path[:-9]

            self.module_mapping[py_file.stem] = module_path

    def _fix_file_imports(self, file_path: Path) -> bool:
        """Fix imports in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()
        except:
            return False

        content = original_content
        modified = False

        # Parse AST to find imports
        try:
            tree = ast.parse(content)

            # Collect all imports
            imports_to_fix = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        old_import = alias.name
                        new_import = self._get_new_import_path(old_import)
                        if new_import and new_import != old_import:
                            imports_to_fix.append((old_import, new_import, "import"))

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        old_import = node.module
                        new_import = self._get_new_import_path(old_import)
                        if new_import and new_import != old_import:
                            imports_to_fix.append((old_import, new_import, "from"))

            # Apply fixes
            for old_import, new_import, import_type in imports_to_fix:
                if import_type == "import":
                    # Handle "import X" statements
                    pattern = rf"\bimport\s+{re.escape(old_import)}\b"
                    replacement = f"import {new_import}"
                else:
                    # Handle "from X import" statements
                    pattern = rf"\bfrom\s+{re.escape(old_import)}\s+import"
                    replacement = f"from {new_import} import"

                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True
                    self.import_updates.append(
                        {
                            "file": str(file_path.relative_to(self.root_path)),
                            "old": old_import,
                            "new": new_import,
                        }
                    )

        except SyntaxError:
            # Fallback to regex-based fixes for files with syntax errors
            for old_pattern, new_pattern in self.import_patterns:
                new_content = re.sub(old_pattern, new_pattern, content)
                if new_content != content:
                    content = new_content
                    modified = True

        # Also check for relative imports that might need updating
        content = self._fix_relative_imports(content, file_path)
        if content != original_content:
            modified = True

        # Write back if modified
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Fixed imports in: {file_path.relative_to(self.root_path)}")
            return True

        return False

    def _get_new_import_path(self, old_import: str) -> Optional[str]:
        """Get the new import path for a moved module"""
        # Check direct mapping
        if old_import in self.reorganization_map:
            return self.reorganization_map[old_import]

        # Check if it's a submodule of a moved module
        for old_base, new_base in self.reorganization_map.items():
            if old_import.startswith(old_base + "."):
                suffix = old_import[len(old_base) :]
                return new_base + suffix

        return None

    def _fix_relative_imports(self, content: str, file_path: Path) -> str:
        """Fix relative imports based on file location"""
        # Get the module path of the current file
        current_module = (
            str(file_path.relative_to(self.root_path))
            .replace(".py", "")
            .replace("/", ".")
        )

        # Fix relative imports that might be broken
        # This is a simplified version - expand as needed
        if "dream" in str(file_path) and "from ..dream" in content:
            content = content.replace("from ..dream", "from dream")

        if "memory" in str(file_path) and "from ..memory" in content:
            content = content.replace("from ..memory", "from memory")

        return content

    def _save_report(self):
        """Save a report of all import fixes"""
        report = {
            "total_updates": len(self.import_updates),
            "reorganization_map": self.reorganization_map,
            "updates": self.import_updates,
        }

        with open("IMPORT_FIX_REPORT.json", "w") as f:
            json.dump(report, f, indent=2)

        # Also create a markdown summary
        with open("IMPORT_FIX_SUMMARY.md", "w") as f:
            f.write("# Import Fix Summary\n\n")
            f.write(
                f"Total files updated: {len(set(u['file'] for u in self.import_updates))}\n"
            )
            f.write(f"Total imports fixed: {len(self.import_updates)}\n\n")

            f.write("## Most Common Fixes\n\n")
            fix_counts = {}
            for update in self.import_updates:
                key = f"{update['old']} → {update['new']}"
                fix_counts[key] = fix_counts.get(key, 0) + 1

            for fix, count in sorted(
                fix_counts.items(), key=lambda x: x[1], reverse=True
            )[:20]:
                f.write(f"- {fix} ({count} occurrences)\n")


def main():
    """Run the import fixer"""
    print("🚀 LUKHAS Import Fixer Tool")
    print("=" * 50)

    fixer = ImportFixer(".")
    fixer.scan_and_fix_imports()

    print("\n✅ Import fixing complete!")
    print("Check IMPORT_FIX_REPORT.json and IMPORT_FIX_SUMMARY.md for details")


if __name__ == "__main__":
    main()
