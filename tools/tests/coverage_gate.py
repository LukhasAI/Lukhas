# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
# do_not_edit: true
# human_editable: false
#
#!/usr/bin/env python3
"""
T4 Coverage Gate - Coverage Ratcheting System
=============================================

Stores and ratchets per-module coverage baselines.
Ensures coverage never decreases on touched modules.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


class CoverageGate:
    """Manage coverage baselines and ratcheting."""

    def __init__(self, baselines_file: Path):
        self.baselines_file = baselines_file
        self.baselines = self.load_baselines()

    def load_baselines(self) -> Dict[str, Any]:
        """Load existing coverage baselines."""
        if self.baselines_file.exists():
            with self.baselines_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {"modules": {}, "global": {"line_rate": 0.0, "branch_rate": 0.0}}

    def save_baselines(self):
        """Save baselines to file."""
        self.baselines_file.parent.mkdir(parents=True, exist_ok=True)
        with self.baselines_file.open("w", encoding="utf-8") as f:
            json.dump(self.baselines, f, indent=2)

    def parse_coverage_xml(self, xml_path: Path) -> Dict[str, Dict[str, float]]:
        """Parse coverage XML report."""
        if not xml_path.exists():
            return {}

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Global coverage
        global_line_rate = float(root.get("line-rate", 0))
        global_branch_rate = float(root.get("branch-rate", 0))

        # Per-module coverage
        modules = {}

        for package in root.findall(".//package"):
            package.get("name", "")

            for class_elem in package.findall("classes/class"):
                filename = class_elem.get("filename", "")
                line_rate = float(class_elem.get("line-rate", 0))
                branch_rate = float(class_elem.get("branch-rate", 0))

                # Convert filename to module name
                module_name = self.filename_to_module(filename)
                if module_name:
                    modules[module_name] = {"line_rate": line_rate, "branch_rate": branch_rate, "filename": filename}

        return {"global": {"line_rate": global_line_rate, "branch_rate": global_branch_rate}, "modules": modules}

    def filename_to_module(self, filename: str) -> str:
        """Convert filename to module name."""
        # candidate/aka_qualia/memory.py -> candidate.aka_qualia.memory
        path = Path(filename)

        # Remove common prefixes and .py extension
        parts = path.with_suffix("").parts

        # Skip common root directories
        if parts and parts[0] in ["src", "lib"]:
            parts = parts[1:]

        return ".".join(parts) if parts else ""

    def check_ratchet(self, current_coverage: Dict[str, Dict[str, float]]) -> List[str]:
        """Check coverage ratchet violations."""
        violations = []

        # Check global coverage
        current_global = current_coverage.get("global", {})
        baseline_global = self.baselines.get("global", {})

        current_line_rate = current_global.get("line_rate", 0)
        baseline_line_rate = baseline_global.get("line_rate", 0)

        if current_line_rate < baseline_line_rate - 0.01:  # 1% tolerance
            violations.append(f"Global line coverage decreased: {baseline_line_rate:.1%} -> {current_line_rate:.1%}")

        # Check per-module coverage
        current_modules = current_coverage.get("modules", {})
        baseline_modules = self.baselines.get("modules", {})

        for module_name, current_module in current_modules.items():
            baseline_module = baseline_modules.get(module_name, {})

            current_line_rate = current_module.get("line_rate", 0)
            baseline_line_rate = baseline_module.get("line_rate", 0)

            if current_line_rate < baseline_line_rate - 0.05:  # 5% tolerance for modules
                violations.append(
                    f"Module {module_name} coverage decreased: " f"{baseline_line_rate:.1%} -> {current_line_rate:.1%}"
                )

        return violations

    def update_baselines(self, current_coverage: Dict[str, Dict[str, float]]):
        """Update baselines with improved coverage only (ratchet up)."""
        updated = []

        # Update global baseline
        current_global = current_coverage.get("global", {})
        baseline_global = self.baselines.get("global", {})

        for metric in ["line_rate", "branch_rate"]:
            current_value = current_global.get(metric, 0)
            baseline_value = baseline_global.get(metric, 0)

            if current_value > baseline_value:
                self.baselines.setdefault("global", {})[metric] = current_value
                updated.append(f"Global {metric}: {baseline_value:.1%} -> {current_value:.1%}")

        # Update module baselines
        current_modules = current_coverage.get("modules", {})

        for module_name, current_module in current_modules.items():
            baseline_module = self.baselines.setdefault("modules", {}).setdefault(module_name, {})

            for metric in ["line_rate", "branch_rate"]:
                current_value = current_module.get(metric, 0)
                baseline_value = baseline_module.get(metric, 0)

                if current_value > baseline_value:
                    baseline_module[metric] = current_value
                    updated.append(f"{module_name} {metric}: {baseline_value:.1%} -> {current_value:.1%}")

        return updated

    def generate_priority_matrix(self, current_coverage: Dict[str, Dict[str, float]], output_file: Path):
        """Generate priority matrix CSV for low-coverage modules."""
        modules = current_coverage.get("modules", {})

        # Sort by coverage (lowest first)
        sorted_modules = sorted(modules.items(), key=lambda x: x[1].get("line_rate", 0))

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as f:
            f.write("module,line_rate,branch_rate,priority,tier\n")

            for module_name, module_data in sorted_modules:
                line_rate = module_data.get("line_rate", 0)
                branch_rate = module_data.get("branch_rate", 0)

                # Assign priority based on coverage and criticality
                if line_rate < 0.2:
                    priority = "critical"
                    tier = (
                        "tier1"
                        if any(x in module_name.lower() for x in ["core", "identity", "consciousness"])
                        else "tier2"
                    )
                elif line_rate < 0.5:
                    priority = "high"
                    tier = "tier2"
                elif line_rate < 0.8:
                    priority = "medium"
                    tier = "tier3"
                else:
                    priority = "low"
                    tier = "tier3"

                f.write(f"{module_name},{line_rate:.3f},{branch_rate:.3f},{priority},{tier}\n")


def main():
    """Main coverage gate entry point."""
    parser = argparse.ArgumentParser(description="T4 Coverage Gate")
    parser.add_argument("coverage_xml", help="Coverage XML report file")
    parser.add_argument("--baselines", default="reports/tests/coverage_baselines.json", help="Coverage baselines file")
    parser.add_argument("--ratchet", choices=["global", "per-module", "both"], default="both", help="Ratchet mode")
    parser.add_argument("--matrix", default="reports/tests/priority_matrix.csv", help="Priority matrix output file")
    parser.add_argument("--strict", action="store_true", help="Fail on violations")
    args = parser.parse_args()

    coverage_xml = Path(args.coverage_xml)
    baselines_file = Path(args.baselines)
    matrix_file = Path(args.matrix)

    gate = CoverageGate(baselines_file)
    current_coverage = gate.parse_coverage_xml(coverage_xml)

    if not current_coverage:
        print("Warning: No coverage data found")
        return

    # Check violations
    violations = gate.check_ratchet(current_coverage)

    if violations:
        print("Coverage Ratchet Violations:")
        for violation in violations:
            print(f"  ❌ {violation}")

        if args.strict:
            sys.exit(1)

    # Update baselines (ratchet up)
    if args.ratchet in ["global", "both"]:
        updated = gate.update_baselines(current_coverage)
        if updated:
            print("Updated coverage baselines:")
            for update in updated:
                print(f"  ✅ {update}")

    # Generate priority matrix
    gate.generate_priority_matrix(current_coverage, matrix_file)
    print(f"Generated priority matrix: {matrix_file}")

    # Save baselines
    gate.save_baselines()

    # Summary
    global_coverage = current_coverage.get("global", {})
    print(f"Current coverage: {global_coverage.get('line_rate', 0):.1%} lines")


if __name__ == "__main__":
    main()
