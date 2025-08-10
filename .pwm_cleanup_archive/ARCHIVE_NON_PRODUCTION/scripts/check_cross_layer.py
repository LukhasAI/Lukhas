#!/usr/bin/env python3
"""
Cross-Layer Import Checker
Identifies and validates cross-layer imports in the LUKHAS codebase.
"""
import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class CrossLayerChecker:
    """Analyzes cross-layer imports and validates architectural boundaries."""

    # Define layer hierarchy (lower number = more foundational)
    LAYER_HIERARCHY = {
        "core": 0,
        "memory": 1,
        "identity": 1,
        "bio": 2,
        "symbolic": 2,
        "quantum": 2,
        "orchestration": 3,
        "ethics": 3,
        "bridge": 3,
        "consciousness": 4,
        "learning": 4,
        "reasoning": 4,
        "emotion": 5,
        "creativity": 5,
        "dream": 5,
        "dreams": 5,
        "features": 6,
        "voice": 6,
        "api": 7,
        "dashboard": 7,
        "tools": 8,
        "tests": 9,
        "benchmarks": 9,
        "examples": 9,
    }

    # Cross-layer import pattern
    CROSS_LAYER_PATTERN = re.compile(r"#\s*🔁\s*Cross-layer:\s*(.+)")

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.cross_layer_imports = []
        self.violations = []
        self.tagged_imports = []

    def get_module_layer(self, module_path: str) -> str:
        """Determine which layer a module belongs to."""
        parts = module_path.split(".")
        for part in parts:
            if part in self.LAYER_HIERARCHY:
                return part

        # Check file path if module path doesn't reveal layer
        for layer in self.LAYER_HIERARCHY:
            if f"/{layer}/" in module_path or module_path.startswith(f"{layer}/"):
                return layer

        return "unknown"

    def is_valid_cross_layer(self, from_layer: str, to_layer: str) -> bool:
        """Check if a cross-layer import is architecturally valid."""
        if from_layer == "unknown" or to_layer == "unknown":
            return True  # Can't validate unknown layers

        from_level = self.LAYER_HIERARCHY.get(from_layer, 999)
        to_level = self.LAYER_HIERARCHY.get(to_layer, 999)

        # Higher layers can import from lower layers
        # Same level imports are OK
        # Lower layers should NOT import from higher layers
        return from_level >= to_level

    def extract_imports(self, file_path: Path) -> List[Tuple[str, str, bool, str]]:
        """Extract imports from a Python file."""
        imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            tree = ast.parse(content)

            # Get the module's layer
            rel_path = str(file_path.relative_to(self.root_path))
            from_layer = self.get_module_layer(rel_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        to_layer = self.get_module_layer(alias.name)

                        # Check if there's a cross-layer tag
                        line_no = node.lineno - 1
                        tagged = False
                        tag_comment = ""

                        if line_no < len(lines):
                            next_line = (
                                lines[line_no] if line_no < len(lines) - 1 else ""
                            )
                            match = self.CROSS_LAYER_PATTERN.search(next_line)
                            if match:
                                tagged = True
                                tag_comment = match.group(1)

                        imports.append((alias.name, to_layer, tagged, tag_comment))

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        to_layer = self.get_module_layer(node.module)

                        # Check for cross-layer tag
                        line_no = node.lineno - 1
                        tagged = False
                        tag_comment = ""

                        if line_no < len(lines):
                            next_line = (
                                lines[line_no] if line_no < len(lines) - 1 else ""
                            )
                            match = self.CROSS_LAYER_PATTERN.search(next_line)
                            if match:
                                tagged = True
                                tag_comment = match.group(1)

                        imports.append((node.module, to_layer, tagged, tag_comment))

            # Check all imports for cross-layer violations
            for module, to_layer, tagged, comment in imports:
                if (
                    from_layer != to_layer
                    and from_layer != "unknown"
                    and to_layer != "unknown"
                ):
                    is_valid = self.is_valid_cross_layer(from_layer, to_layer)

                    import_info = {
                        "file": str(file_path.relative_to(self.root_path)),
                        "from_layer": from_layer,
                        "to_layer": to_layer,
                        "module": module,
                        "valid": is_valid,
                        "tagged": tagged,
                        "tag_comment": comment,
                    }

                    self.cross_layer_imports.append(import_info)

                    if not is_valid:
                        self.violations.append(import_info)

                    if tagged:
                        self.tagged_imports.append(import_info)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return imports

    def scan_codebase(self):
        """Scan the entire codebase for cross-layer imports."""
        python_files = list(self.root_path.rglob("*.py"))

        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"Processing file {i}/{len(python_files)}...")

            # Skip test files and migrations
            if any(
                skip in str(file_path) for skip in ["__pycache__", "migration", ".pyc"]
            ):
                continue

            self.extract_imports(file_path)

    def generate_report(self) -> Dict:
        """Generate a comprehensive report of cross-layer imports."""

        # Count violations by layer pair
        violation_matrix = defaultdict(lambda: defaultdict(int))
        for v in self.violations:
            violation_matrix[v["from_layer"]][v["to_layer"]] += 1

        # Count all cross-layer imports by layer pair
        import_matrix = defaultdict(lambda: defaultdict(int))
        for imp in self.cross_layer_imports:
            import_matrix[imp["from_layer"]][imp["to_layer"]] += 1

        report = {
            "summary": {
                "total_cross_layer_imports": len(self.cross_layer_imports),
                "architectural_violations": len(self.violations),
                "tagged_imports": len(self.tagged_imports),
                "violation_rate": (
                    len(self.violations) / len(self.cross_layer_imports)
                    if self.cross_layer_imports
                    else 0
                ),
            },
            "layer_hierarchy": self.LAYER_HIERARCHY,
            "violations": self.violations[:50],  # Top 50 violations
            "violation_matrix": dict(violation_matrix),
            "import_matrix": dict(import_matrix),
            "tagged_imports": self.tagged_imports[:20],  # Sample of tagged imports
        }

        return report

    def print_summary(self):
        """Print a summary of findings."""
        print("\n🔍 Cross-Layer Import Analysis")
        print("=" * 50)

        print("\n📊 Summary:")
        print(f"  Total cross-layer imports: {len(self.cross_layer_imports)}")
        print(f"  Architectural violations: {len(self.violations)}")
        print(f"  Tagged cross-layer imports: {len(self.tagged_imports)}")

        if self.violations:
            print("\n❌ Top Violations (showing first 10):")
            for v in self.violations[:10]:
                print(f"  {v['from_layer']} → {v['to_layer']}: {v['file']}")
                print(f"    Importing: {v['module']}")

        if self.tagged_imports:
            print("\n✅ Tagged Cross-Layer Imports (showing first 5):")
            for t in self.tagged_imports[:5]:
                print(f"  {t['from_layer']} → {t['to_layer']}: {t['tag_comment']}")
                print(f"    File: {t['file']}")


def main():
    """Main entry point."""
    root_path = Path(__file__).parent.parent

    print("🔁 Checking cross-layer imports in LUKHAS codebase...")

    checker = CrossLayerChecker(root_path)
    checker.scan_codebase()

    # Generate report
    report = checker.generate_report()

    # Save report
    report_path = root_path / "scripts" / "cross_layer_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Report saved to: {report_path}")

    # Print summary
    checker.print_summary()

    # Exit with error code if violations found
    if checker.violations:
        print(f"\n⚠️  Found {len(checker.violations)} architectural violations!")
        return 1
    else:
        print("\n✅ No architectural violations found!")
        return 0


if __name__ == "__main__":
    exit(main())
