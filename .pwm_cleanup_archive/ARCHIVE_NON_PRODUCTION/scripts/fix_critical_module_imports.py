#!/usr/bin/env python3
"""
Fix critical module imports based on actual broken patterns.
Focus on internal module references that need updating.
"""

import re
from pathlib import Path


class CriticalImportFixer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.fixes_applied = 0

        # Define critical import fixes based on module reorganization
        self.import_fixes = {
            # Consciousness module fixes
            "from consciousness.core import": "from consciousness.core_consciousness import",
            "from consciousness.stream import": "from consciousness.stream_consciousness import",
            "import consciousness.core": "import consciousness.core_consciousness",
            # Memory module fixes (after consolidation)
            "from memory.unified_memory_system import": "from memory.core import",
            "import memory.unified_memory_system": "import memory.core",
            # Orchestration fixes
            "import orchestration.agi_brain_orchestrator": "from orchestration.brain import agi_brain_orchestrator",
            "from orchestration.agi_brain_orchestrator import": "from orchestration.brain.agi_brain_orchestrator import",
            # Core module fixes
            "import core.symbolic": "from core.symbolic import",
            "from core.symbolic import": "from core.symbolic.base import",
            # Fix reasoning imports
            "import reasoning.symbolic_reasoning": "from reasoning import symbolic_reasoning",
            "from reasoning.symbolic_reasoning import": "from reasoning.symbolic_reasoning import",
            # Fix incomplete imports (most common pattern)
            "from dataclasses import\n": "from dataclasses import dataclass, field\n",
            "from typing import\n": "from typing import Dict, List, Any, Optional\n",
            "from pathlib import\n": "from pathlib import Path\n",
            "from datetime import\n": "from datetime import datetime, timedelta\n",
            "from collections import\n": "from collections import defaultdict, Counter\n",
            "from enum import\n": "from enum import Enum, auto\n",
            # Bio module fixes
            "from bio.systems import": "from bio.systems.orchestration import",
            "from bio.symbolic import": "from symbolic.bio import",
            # Features module fixes
            "from features.memory import": "from memory.features import",
            "from features.integration import": "from integration.features import",
        }

        # Module-specific import completions
        self.module_specific_fixes = {
            "consciousness": {
                "from consciousness import": "from consciousness.core_consciousness import ConsciousnessCore",
                "import consciousness.": "from consciousness.core_consciousness import ",
            },
            "memory": {
                "from memory import": "from memory.core import MemoryCore",
                "from memory.systems import": "from memory.systems.memory_fold import MemoryFold",
            },
            "orchestration": {
                "from orchestration import": "from orchestration.orchestrator import Orchestrator",
                "from orchestration.brain import": "from orchestration.brain.brain_orchestrator import BrainOrchestrator",
            },
            "api": {
                "from api import": "from api.routes import router",
                "import api.": "from api import ",
            },
        }

    def fix_critical_modules(self):
        """Fix imports in critical modules."""
        print("Fixing critical module imports...")

        # Priority modules to fix
        critical_modules = [
            "consciousness",
            "memory",
            "orchestration",
            "api",
            "core",
            "features",
        ]

        for module in critical_modules:
            print(f"\n🔧 Fixing {module} module...")
            self._fix_module(module)

        print(f"\n✅ Total fixes applied: {self.fixes_applied}")

    def _fix_module(self, module_name: str):
        """Fix imports in a specific module."""
        module_path = self.root_path / module_name

        if not module_path.exists():
            print(f"  Module {module_name} not found")
            return

        fixed_files = 0

        for py_file in module_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            if self._fix_file(py_file, module_name):
                fixed_files += 1

        print(f"  Fixed {fixed_files} files in {module_name}")

    def _fix_file(self, file_path: Path, module_name: str) -> bool:
        """Fix imports in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply general fixes
            for pattern, replacement in self.import_fixes.items():
                if pattern in content:
                    content = content.replace(pattern, replacement)
                    self.fixes_applied += 1

            # Apply module-specific fixes
            if module_name in self.module_specific_fixes:
                for pattern, replacement in self.module_specific_fixes[
                    module_name
                ].items():
                    if pattern in content and replacement not in content:
                        content = content.replace(pattern, replacement)
                        self.fixes_applied += 1

            # Fix incomplete imports with regex
            content = self._fix_incomplete_imports(content)

            # Fix broken internal imports
            content = self._fix_internal_imports(content, module_name)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"    ✓ {file_path.relative_to(self.root_path)}")
                return True

        except Exception as e:
            print(f"    ✗ Error fixing {file_path.relative_to(self.root_path)}: {e}")

        return False

    def _fix_incomplete_imports(self, content: str) -> str:
        """Fix incomplete import statements using regex."""
        # Pattern to match incomplete imports (from X import with nothing after)
        incomplete_pattern = r"from\s+(\S+)\s+import\s*$"

        # Common completions based on module
        completions = {
            "dataclasses": "dataclass, field",
            "typing": "Dict, List, Any, Optional, Union",
            "pathlib": "Path",
            "datetime": "datetime, timedelta",
            "collections": "defaultdict, Counter, deque",
            "enum": "Enum, auto",
            "asyncio": "create_task, gather, sleep",
            "abc": "ABC, abstractmethod",
            "functools": "wraps, lru_cache",
            "itertools": "chain, combinations, permutations",
        }

        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            match = re.match(incomplete_pattern, line)
            if match:
                module = match.group(1)
                base_module = module.split(".")[-1]

                if base_module in completions:
                    fixed_line = f"from {module} import {completions[base_module]}"
                    fixed_lines.append(fixed_line)
                    self.fixes_applied += 1
                else:
                    # For unknown modules, add a placeholder
                    fixed_line = f"from {module} import *  # TODO: Specify imports"
                    fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_internal_imports(self, content: str, module_name: str) -> str:
        """Fix broken internal module imports."""
        # Fix relative imports that might be broken
        if module_name == "consciousness":
            content = re.sub(
                r"from \.\.core import",
                "from consciousness.core_consciousness import",
                content,
            )
        elif module_name == "memory":
            content = re.sub(
                r"from \.\.systems import", "from memory.systems import", content
            )

        return content

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = {"__pycache__", ".pyc", ".git", "venv", ".venv"}

        path_str = str(path)
        return any(pattern in path_str for pattern in skip_patterns)

    def generate_import_map_update(self):
        """Generate an updated import mapping for remaining fixes."""
        print("\n📊 Generating import map for remaining fixes...")

        import_map = {
            "description": "Import mapping for LUKHAS module reorganization",
            "mappings": {
                # Consciousness mappings
                "consciousness.core": "consciousness.core_consciousness",
                "consciousness.stream": "consciousness.stream_consciousness",
                # Memory mappings
                "memory.unified_memory_system": "memory.core",
                "memory.systems.memory_fold_system": "memory.systems.memory_fold",
                # Orchestration mappings
                "orchestration.agi_brain_orchestrator": "orchestration.brain.agi_brain_orchestrator",
                "orchestration.orchestrator": "orchestration.core_orchestrator",
                # Bio mappings
                "bio.symbolic": "symbolic.bio",
                "bio.systems": "bio.systems.orchestration",
                # Features mappings
                "features.memory": "memory.features",
                "features.integration": "integration.features",
            },
            "import_completions": {
                "dataclasses": ["dataclass", "field", "asdict", "astuple"],
                "typing": ["Dict", "List", "Any", "Optional", "Union", "Tuple", "Set"],
                "pathlib": ["Path", "PurePath"],
                "datetime": ["datetime", "timedelta", "timezone"],
                "collections": ["defaultdict", "Counter", "deque", "OrderedDict"],
            },
        }

        output_path = (
            self.root_path / "scripts" / "import_migration" / "import_mappings.json"
        )
        import json

        with open(output_path, "w") as f:
            json.dump(import_map, f, indent=2)

        print(f"Import map saved to: {output_path}")


def main():
    root_path = Path(".").resolve()
    fixer = CriticalImportFixer(root_path)

    # Fix critical modules
    fixer.fix_critical_modules()

    # Generate import map
    fixer.generate_import_map_update()


if __name__ == "__main__":
    main()
