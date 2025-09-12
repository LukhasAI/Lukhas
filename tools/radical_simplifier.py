#!/usr/bin/env python3
"""
The Jobs Simplifier - Radical Simplification Tool
"Simplicity is the ultimate sophistication" - Leonardo da Vinci (Steve's favorite quote)
"""

import ast
import hashlib
import os
from collections import defaultdict
from pathlib import Path


class RadicalSimplifier:
    """
    Following Steve Jobs' philosophy:
    1. Focus on what matters
    2. Say no to 1,000 things
    3. Simplicity is the ultimate sophistication
    """

    def __init__(self):
        self.core_vision = "AI that dreams, remembers, and understands emotions"
        self.core_modules = {
            "consciousness": "Self-awareness and decision making",
            "memory": "Learning and recall",
            "dream": "Creative generation and processing",
            "emotion": "Emotional understanding and response",
            "interface": "Human interaction layer",
        }
        self.usage_data = defaultdict(int)
        self.duplicate_functions = defaultdict(list)
        self.import_graph = defaultdict(set)

    def analyze_codebase(self) -> dict:
        """Analyze the entire codebase for simplification opportunities"""
        print("🔍 Analyzing codebase with Steve's eyes...")

        analysis = {
            "total_files": 0,
            "total_lines": 0,
            "duplicate_code": [],
            "unused_files": [],
            "complex_files": [],
            "non_core_modules": [],
            "simplification_opportunities": [],
        }

        # First pass: Identify what exists
        for root, _dirs, files in os.walk("."):
            if any(skip in root for skip in [".git", "__pycache__", "._cleanup_archive", "venv"]):
                continue

            for file in files:
                if file.endswith(".py"):
                    analysis["total_files"] += 1
                    filepath = os.path.join(root, file)

                    try:
                        with open(filepath) as f:
                            content = f.read()
                            lines = len(content.splitlines())
                            analysis["total_lines"] += lines

                            # Steve's rule: No file over 200 lines
                            if lines > 200:
                                analysis["complex_files"].append(
                                    {
                                        "path": filepath,
                                        "lines": lines,
                                        "reason": f"{lines} lines (Steve's limit: 200)",
                                    }
                                )

                            # Check if it's in a non-core module
                            module = root.split("/")[1] if len(root.split("/")) > 1 else ""
                            if module and module not in self.core_modules and module not in ["tools", "tests", "docs"]:
                                analysis["non_core_modules"].append(filepath)

                            # Analyze imports to build usage graph
                            self._analyze_imports(filepath, content)

                            # Find duplicate functionality
                            self._find_duplicates(filepath, content)

                    except Exception:
                        pass

        # Second pass: Find unused files
        all_files = set()
        imported_files = set()

        for file_path, imports in self.import_graph.items():
            all_files.add(file_path)
            imported_files.update(imports)

        # Files that are never imported (except main entry points)
        never_imported = all_files - imported_files
        for filepath in never_imported:
            if not any(entry in filepath for entry in ["main.py", "__init__.py", "test_", "setup.py"]):
                analysis["unused_files"].append(filepath)

        # Generate simplification opportunities
        analysis["simplification_opportunities"] = self._generate_simplifications(analysis)

        return analysis

    def _analyze_imports(self, filepath: str, content: str):
        """Build import dependency graph"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.import_graph[filepath].add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.import_graph[filepath].add(node.module)
        except BaseException:
            pass

    def _find_duplicates(self, filepath: str, content: str):
        """Find duplicate functions using AST fingerprinting"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Create a fingerprint of the function
                    fingerprint = self._function_fingerprint(node)
                    self.duplicate_functions[fingerprint].append(
                        {
                            "file": filepath,
                            "function": node.name,
                            "lines": (node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0),
                        }
                    )
        except BaseException:
            pass

    def _function_fingerprint(self, node: ast.FunctionDef) -> str:
        """Create a fingerprint for a function to detect duplicates"""
        # Simple fingerprint based on structure
        params = len(node.args.args)
        returns = 1 if node.returns else 0
        body_types = [type(n).__name__ for n in node.body]

        fingerprint_data = f"{params}:{returns}:{':'.join(body_types[:5])}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:8]

    def _generate_simplifications(self, analysis: dict) -> list[dict]:
        """Generate Steve-approved simplification suggestions"""
        suggestions = []

        # 1. Delete all non-core modules
        if analysis["non_core_modules"]:
            suggestions.append(
                {
                    "action": "DELETE_NON_CORE",
                    "description": f"Delete {len(analysis['non_core_modules'])} files from non-core modules",
                    "impact": f"Remove ~{len(analysis['non_core_modules']) * 100} lines",
                    "steve_says": "Focus means saying no to the hundred other good ideas",
                }
            )

        # 2. Merge duplicate functions
        duplicates_count = sum(len(v) for v in self.duplicate_functions.values() if len(v) > 1)
        if duplicates_count > 0:
            suggestions.append(
                {
                    "action": "MERGE_DUPLICATES",
                    "description": f"Merge {duplicates_count} duplicate functions",
                    "impact": f"Remove ~{duplicates_count * 20} lines",
                    "steve_says": "That's been one of my mantras - focus and simplicity",
                }
            )

        # 3. Refactor complex files
        if analysis["complex_files"]:
            suggestions.append(
                {
                    "action": "SPLIT_COMPLEX_FILES",
                    "description": f"Refactor {len(analysis['complex_files'])} files over 200 lines",
                    "impact": "Improve readability and maintainability",
                    "steve_says": "Simple can be harder than complex",
                }
            )

        # 4. The Big One - Reduce to 5 core modules
        suggestions.append(
            {
                "action": "RADICAL_CONSOLIDATION",
                "description": "Consolidate everything into 5 core modules",
                "impact": f"Reduce from {analysis['total_files']} files to ~50 files",
                "steve_says": "Innovation is saying no to 1,000 things",
            }
        )

        return suggestions

    def generate_simplification_plan(self, analysis: dict) -> str:
        """Generate an executable simplification plan"""
        plan = f"""# LUKHAS Radical Simplification Plan

## Current State (The Problem)
- Files: {analysis["total_files"]}
- Lines: {analysis["total_lines"]}
- Unused files: {len(analysis["unused_files"])}
- Complex files: {len(analysis["complex_files"])}

## Steve's Vision (The Solution)
"What is LUKHAS? AI that dreams, remembers, and understands emotions."
Everything else is noise.

## Execution Plan

### Phase 1: DELETE (Week 1)
Steve says: "I'm as proud of what we don't do as I am of what we do."

1. Delete all unused files ({len(analysis["unused_files"])} files)
2. Delete all non-core modules ({len(analysis["non_core_modules"])} files)
3. Archive anything with historical value

### Phase 2: CONSOLIDATE (Week 2)
Steve says: "It's not about money. It's about the people you have, how you're led,
    and how much you get it."

Target structure:
```
lukhas/
├── consciousness/     # One consciousness system
├── memory/           # One memory system
├── dream/            # One dream system
├── emotion/          # One emotion system
├── interface/        # One interface system
└── main.py          # One entry point
```

### Phase 3: SIMPLIFY (Week 3)
Steve says: "When you first start off trying to solve a problem, the first solutions you come up with are very complex."

1. Every module has ONE public API
2. No file over 200 lines
3. No function over 20 lines
4. No more than 3 levels of imports

### Success Metrics
- Before: {analysis["total_lines"]} lines
- Target: < 50,000 lines (94% reduction)
- Before: {analysis["total_files"]} files
- Target: < 50 files (98% reduction)

### The Jobs Test
Before keeping ANYTHING, ask:
1. ✓ Does this directly serve "AI that dreams, remembers, and understands emotions"?
2. ✓ Would I be proud to show this to Steve?
3. ✓ Is this the simplest possible solution?

If any answer is NO → DELETE IT.
"""
        return plan

    def execute_phase_1_delete(self, analysis: dict, dry_run: bool = True):
        """Execute Phase 1: Delete unused and non-core files"""
        if dry_run:
            print("\n🔥 DRY RUN - Phase 1: DELETE")
        else:
            print("\n🔥 EXECUTING - Phase 1: DELETE")

        files_to_delete = []

        # Add unused files
        files_to_delete.extend(analysis["unused_files"])

        # Add non-core modules
        files_to_delete.extend(analysis["non_core_modules"])

        # Remove duplicates
        files_to_delete = list(set(files_to_delete))

        print(f"\nFiles to delete: {len(files_to_delete)}")

        if not dry_run:
            archive_dir = Path("/Users/agi_dev/lukhas-archive/radical_simplification")
            archive_dir.mkdir(parents=True, exist_ok=True)

            for filepath in files_to_delete:
                try:
                    source = Path(filepath)
                    if source.exists():
                        # Archive it
                        dest = archive_dir / filepath
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        source.rename(dest)
                        print(f"  ✓ Archived: {filepath}")
                except Exception as e:
                    print(f"  ✗ Failed: {filepath} - {e}")
        else:
            # Just show what would be deleted
            for _i, filepath in enumerate(files_to_delete[:10]):
                print(f"  Would delete: {filepath}")
            if len(files_to_delete) > 10:
                print(f"  ... and {len(files_to_delete) - 10} more files")

        return len(files_to_delete)


def main():
    """Run the radical simplifier"""
    simplifier = RadicalSimplifier()

    print("🎯 Starting Radical Simplification Analysis...")
    print("Following Steve Jobs' philosophy: 'Simplicity is the ultimate sophistication'\n")

    # Analyze
    analysis = simplifier.analyze_codebase()

    # Generate plan
    plan = simplifier.generate_simplification_plan(analysis)

    # Save plan
    with open("RADICAL_SIMPLIFICATION_PLAN.md", "w") as f:
        f.write(plan)

    print("\n📋 Simplification Plan Generated: RADICAL_SIMPLIFICATION_PLAN.md")

    # Show summary
    print("\n📊 Summary:")
    print(f"   Total files: {analysis['total_files']}")
    print(f"   Total lines: {analysis['total_lines']}")
    print(f"   Files to delete: {len(analysis['unused_files']) + len(analysis['non_core_modules'])}")
    print("   Complexity reduction: 94% target")

    print("\n💡 Top Simplification Opportunities:")
    for i, opp in enumerate(analysis["simplification_opportunities"][:3], 1):
        print(f"\n{i}. {opp['action']}")
        print(f"   {opp['description']}")
        print(f"   Impact: {opp['impact']}")
        print(f"   Steve says: '{opp['steve_says']}'")

    # Ask to execute
    print("\n\n🤔 Ready to execute Phase 1: DELETE?")
    print("This will archive unused and non-core files.")
    print("\nRun with --execute to actually delete files")


if __name__ == "__main__":
    import sys

    if "--execute" in sys.argv:
        simplifier = RadicalSimplifier()
        analysis = simplifier.analyze_codebase()
        simplifier.execute_phase_1_delete(analysis, dry_run=False)
    else:
        main()
