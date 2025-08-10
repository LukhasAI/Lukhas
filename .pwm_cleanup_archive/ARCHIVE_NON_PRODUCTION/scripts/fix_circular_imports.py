#!/usr/bin/env python3
"""
Fix circular import dependencies in the LUKHAS codebase.
Identifies circular imports and provides solutions.
"""

import ast
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx


class CircularImportFixer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.import_graph = nx.DiGraph()
        self.module_imports = defaultdict(set)
        self.file_imports = defaultdict(set)
        self.circular_cycles = []
        self.fixes_applied = 0

    def analyze_imports(self):
        """Build import graph from codebase."""
        print("🔍 Analyzing imports for circular dependencies...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            self._analyze_file(py_file)

        print(f"✅ Analyzed {len(self.file_imports)} files")

    def _analyze_file(self, file_path: Path):
        """Analyze imports in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Get relative path for the file
            rel_path = file_path.relative_to(self.root_path)
            file_module = str(rel_path).replace(".py", "").replace("/", ".")

            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and not node.module.startswith("."):
                            # Only track internal imports
                            if self._is_internal_module(node.module):
                                imported_module = node.module
                                self.file_imports[file_module].add(imported_module)

                                # Add to graph
                                module_from = file_module.split(".")[0]
                                module_to = imported_module.split(".")[0]

                                if module_from != module_to:
                                    self.module_imports[module_from].add(module_to)
                                    self.import_graph.add_edge(module_from, module_to)

                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_internal_module(alias.name):
                                module_from = file_module.split(".")[0]
                                module_to = alias.name.split(".")[0]

                                if module_from != module_to:
                                    self.module_imports[module_from].add(module_to)
                                    self.import_graph.add_edge(module_from, module_to)

            except SyntaxError:
                pass

        except Exception:
            pass

    def _is_internal_module(self, module_name: str) -> bool:
        """Check if module is internal to project."""
        internal_prefixes = {
            "consciousness",
            "memory",
            "orchestration",
            "api",
            "core",
            "bio",
            "symbolic",
            "features",
            "creativity",
            "tools",
            "tests",
            "benchmarks",
            "scripts",
            "trace",
            "integration",
        }

        return any(module_name.startswith(prefix) for prefix in internal_prefixes)

    def find_circular_dependencies(self):
        """Find all circular import cycles."""
        print("\n🔄 Finding circular dependencies...")

        try:
            # Find all simple cycles
            cycles = list(nx.simple_cycles(self.import_graph))

            # Filter and sort cycles
            self.circular_cycles = []
            seen_cycles = set()

            for cycle in cycles:
                if len(cycle) > 1:
                    # Normalize cycle (start with smallest element)
                    normalized = tuple(sorted(cycle))
                    if normalized not in seen_cycles:
                        seen_cycles.add(normalized)
                        self.circular_cycles.append(cycle)

            # Sort by length (shorter cycles first)
            self.circular_cycles.sort(key=len)

            print(f"Found {len(self.circular_cycles)} unique circular dependencies")

            # Print top cycles
            for i, cycle in enumerate(self.circular_cycles[:10]):
                print(f"\n{i+1}. {' → '.join(cycle)} → {cycle[0]}")

        except Exception as e:
            print(f"Error finding cycles: {e}")

    def generate_fixes(self):
        """Generate fixes for circular dependencies."""
        print("\n🔧 Generating fixes for circular dependencies...")

        fixes = []

        # Analyze each cycle
        for cycle in self.circular_cycles[:20]:  # Fix top 20 cycles
            fix = self._analyze_cycle(cycle)
            if fix:
                fixes.append(fix)

        # Save fixes
        self._save_fixes(fixes)

        # Apply automatic fixes
        self._apply_automatic_fixes(fixes)

    def _analyze_cycle(self, cycle: list) -> dict:
        """Analyze a circular dependency cycle and suggest fixes."""
        # Find the weakest link in the cycle
        edge_weights = {}

        for i in range(len(cycle)):
            from_module = cycle[i]
            to_module = cycle[(i + 1) % len(cycle)]

            # Count how many imports exist between these modules
            import_count = 0
            for file_from, imports in self.file_imports.items():
                if file_from.startswith(from_module):
                    for imp in imports:
                        if imp.startswith(to_module):
                            import_count += 1

            edge_weights[(from_module, to_module)] = import_count

        # Find weakest link (least imports)
        weakest_link = min(edge_weights.items(), key=lambda x: x[1])

        return {
            "cycle": cycle,
            "break_at": weakest_link[0],
            "import_count": weakest_link[1],
            "suggestion": self._generate_suggestion(weakest_link[0], cycle),
        }

    def _generate_suggestion(self, link: tuple, cycle: list) -> dict:
        """Generate specific fix suggestion."""
        from_module, to_module = link

        # Common patterns and solutions
        if "core" in from_module and "memory" in to_module:
            return {
                "type": "move_to_interface",
                "description": f"Move shared interfaces from {from_module} to core.interfaces",
                "files_to_modify": self._find_files_with_import(from_module, to_module),
            }

        elif "features" in cycle and len(cycle) > 3:
            return {
                "type": "lazy_import",
                "description": f"Use lazy imports in {from_module} for {to_module}",
                "files_to_modify": self._find_files_with_import(from_module, to_module),
            }

        else:
            return {
                "type": "restructure",
                "description": f"Consider moving common code from {to_module} to {from_module} or create new shared module",
                "files_to_modify": self._find_files_with_import(from_module, to_module),
            }

    def _find_files_with_import(self, from_module: str, to_module: str) -> list:
        """Find files that have the problematic import."""
        files = []

        for file_path, imports in self.file_imports.items():
            if file_path.startswith(from_module):
                for imp in imports:
                    if imp.startswith(to_module):
                        files.append(file_path.replace(".", "/") + ".py")

        return files[:5]  # Return top 5 files

    def _save_fixes(self, fixes: list):
        """Save fix suggestions to file."""
        output = {
            "total_cycles": len(self.circular_cycles),
            "analyzed_cycles": len(fixes),
            "fixes": fixes,
            "automatic_fixes_available": sum(
                1 for f in fixes if f["suggestion"]["type"] == "lazy_import"
            ),
        }

        output_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "circular_import_fixes.json"
        )
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n📄 Fix suggestions saved to: {output_path}")

    def _apply_automatic_fixes(self, fixes: list):
        """Apply automatic fixes where possible."""
        print("\n🚀 Applying automatic fixes...")

        for fix in fixes:
            if fix["suggestion"]["type"] == "lazy_import":
                self._apply_lazy_import_fix(fix)

    def _apply_lazy_import_fix(self, fix: dict):
        """Apply lazy import fix to break circular dependency."""
        from_module, to_module = fix["break_at"]

        for file_path in fix["suggestion"]["files_to_modify"]:
            full_path = self.root_path / file_path

            if not full_path.exists():
                continue

            try:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()

                # Find imports from the problematic module
                lines = content.split("\n")
                modified_lines = []
                imports_moved = []

                for line in lines:
                    if f"from {to_module}" in line or f"import {to_module}" in line:
                        # Comment out the import
                        modified_lines.append(f"# {line}  # Moved to lazy import")
                        imports_moved.append(line.strip())
                    else:
                        modified_lines.append(line)

                if imports_moved:
                    # Add lazy import function
                    lazy_import_code = self._generate_lazy_import_code(
                        imports_moved, to_module
                    )

                    # Find where to insert (after other imports)
                    insert_pos = 0
                    for i, line in enumerate(modified_lines):
                        if line.strip() and not line.startswith(
                            ("import ", "from ", "#")
                        ):
                            insert_pos = i
                            break

                    # Insert lazy import code
                    modified_lines.insert(insert_pos, lazy_import_code)

                    # Write back
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(modified_lines))

                    print(f"  ✓ Applied lazy import fix to: {file_path}")
                    self.fixes_applied += 1

            except Exception as e:
                print(f"  ✗ Error fixing {file_path}: {e}")

    def _generate_lazy_import_code(self, imports: list, module: str) -> str:
        """Generate lazy import code."""
        code = f"""
# Lazy imports to break circular dependency
def _lazy_import_{module.replace('.', '_')}():
    \"\"\"Lazy import for {module} to avoid circular imports.\"\"\"
    global _lazy_{module.replace('.', '_')}_cache
    if '_lazy_{module.replace('.', '_')}_cache' not in globals():
"""

        for imp in imports:
            code += f"        {imp}\n"

        code += f"""        _lazy_{module.replace('.', '_')}_cache = True
    return locals()

# Usage: _lazy_import_{module.replace('.', '_')}() when needed
"""

        return code

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "build",
            "dist",
            ".pyc",
        }

        return any(pattern in str(path) for pattern in skip_patterns)

    def create_import_guidelines(self):
        """Create import guidelines to prevent future circular dependencies."""
        guidelines = """# LUKHAS Import Guidelines

## Import Hierarchy

To prevent circular dependencies, follow this import hierarchy:

```
1. core/           → Can only import from: stdlib, third-party
2. memory/         → Can import from: core, stdlib, third-party
3. orchestration/  → Can import from: core, memory, stdlib, third-party
4. consciousness/  → Can import from: core, memory, orchestration
5. bio/            → Can import from: core, memory, orchestration
6. symbolic/       → Can import from: core, memory
7. api/            → Can import from: ALL internal modules
8. features/       → Can import from: ALL internal modules
9. tools/          → Can import from: ALL internal modules
10. tests/         → Can import from: ALL internal modules
```

## Best Practices

1. **Use Type Annotations Carefully**
   ```python
   # Bad - causes import at module level
   from consciousness import ConsciousnessCore
   def process(core: ConsciousnessCore): ...

   # Good - deferred import
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from consciousness import ConsciousnessCore
   def process(core: 'ConsciousnessCore'): ...
   ```

2. **Lazy Imports for Optional Features**
   ```python
   def advanced_feature():
       from heavy_module import HeavyClass  # Import only when needed
       return HeavyClass()
   ```

3. **Create Interface Modules**
   ```python
   # In core/interfaces/memory_interface.py
   from abc import ABC, abstractmethod
   class MemoryInterface(ABC): ...

   # Both modules can import the interface without circular dependency
   ```

4. **Dependency Injection**
   ```python
   # Instead of importing directly
   class MyClass:
       def __init__(self, memory_system=None):
           self.memory = memory_system or self._create_default_memory()
   ```

## Common Patterns to Avoid

1. **Bidirectional Dependencies**
   - Module A imports from Module B
   - Module B imports from Module A
   - Solution: Extract common code to Module C

2. **Deep Chain Dependencies**
   - A → B → C → D → A
   - Solution: Flatten hierarchy or use interfaces

3. **Feature Creep**
   - Low-level modules importing from high-level
   - Solution: Move shared code down the hierarchy
"""

        guidelines_path = self.root_path / "docs" / "import_guidelines.md"
        guidelines_path.parent.mkdir(exist_ok=True)

        with open(guidelines_path, "w") as f:
            f.write(guidelines)

        print(f"\n📋 Import guidelines created at: {guidelines_path}")


def main():
    root_path = Path(".").resolve()
    fixer = CircularImportFixer(root_path)

    # Analyze imports
    fixer.analyze_imports()

    # Find circular dependencies
    fixer.find_circular_dependencies()

    # Generate and apply fixes
    fixer.generate_fixes()

    # Create guidelines
    fixer.create_import_guidelines()

    print(f"\n✅ Applied {fixer.fixes_applied} automatic fixes")
    print("⚠️  Manual intervention needed for remaining circular dependencies")
    print("📖 See docs/import_guidelines.md for best practices")


if __name__ == "__main__":
    main()
