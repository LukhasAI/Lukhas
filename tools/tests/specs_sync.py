# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
# do_not_edit: true
# human_editable: false
#
#!/usr/bin/env python3
"""
T4 Specs Sync - Architecture-Driven Spec Generation
===================================================

Generates spec stubs from LUKHAS_ARCHITECTURE_MASTER.json.
JSON-driven test specification creation.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import yaml


def load_architecture_master(arch_path: Path) -> dict[str, Any]:
    """Load the architecture master JSON."""
    if not arch_path.exists():
        print(f"Warning: Architecture master not found at {arch_path}")
        return {"modules": {}}

    with arch_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_spec_template(template_path: Path) -> dict[str, Any]:
    """Load the spec template YAML."""
    if not template_path.exists():
        # Create default template if missing
        default_template = {"module": "", "description": "", "version": "1.0.0", "tier": "tier3", "tests": []}
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with template_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(default_template, f, sort_keys=False)
        print(f"Created default spec template at {template_path}")
        return default_template

    with template_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_spec_stubs(arch_path: Path, template_path: Path, output_dir: Path):
    """Generate spec stubs from architecture master."""
    arch = load_architecture_master(arch_path)
    template = load_spec_template(template_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    generated_count = 0

    for module_name, module_info in arch.get("modules", {}).items():
        spec = dict(template)  # shallow copy of template
        spec["module"] = module_name
        spec["description"] = module_info.get("description", f"{module_name} module")
        spec["tier"] = module_info.get("tier", "tier3")
        spec["tests"] = []

        # Generate test stubs from features
        for feature in module_info.get("features", []):
            test_stub = {
                "name": f"test_{feature['name']}",
                "description": feature.get("description", f"Test {feature['name']} functionality"),
                "input": feature.get("input_spec", {}),
                "expected": feature.get("expected_output", {}),
                "tags": feature.get("tags", [spec["tier"]]),
            }
            spec["tests"].append(test_stub)

        # If no features, create basic test stub
        if not spec["tests"]:
            spec["tests"] = [
                {
                    "name": f"test_{module_name}_basic",
                    "description": f"Basic functionality test for {module_name}",
                    "input": {},
                    "expected": {},
                    "tags": [spec["tier"]],
                }
            ]

        output_path = output_dir / f"{module_name}_spec.yaml"
        with output_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(spec, f, sort_keys=False, default_flow_style=False)

        print(f"Generated spec stub: {output_path}")
        generated_count += 1

    print(f"✅ Generated {generated_count} spec stubs in {output_dir}")


def main():
    """Main specs sync entry point."""
    parser = argparse.ArgumentParser(description="T4 Specs Sync")
    parser.add_argument("--arch", default="LUKHAS_ARCHITECTURE_MASTER.json", help="Architecture master JSON file")
    parser.add_argument("--template", default="tests/specs/SPEC_TEMPLATE.yaml", help="Spec template file")
    parser.add_argument("--out", default="tests/specs", help="Output directory for specs")
    args = parser.parse_args()

    arch_path = Path(args.arch)
    template_path = Path(args.template)
    output_dir = Path(args.out)

    generate_spec_stubs(arch_path, template_path, output_dir)


if __name__ == "__main__":
    main()
