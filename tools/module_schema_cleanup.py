#!/usr/bin/env python3
"""
LUKHAS Module Schema Cleanup Tool

Cleans up common issues in generated module schemas to improve validation rates.
Handles dependency cleanup, format fixes, and validation improvements.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml


class ModuleSchemaCleanup:
    """Cleans up module schemas to improve validation"""

    def __init__(self, modules_dir: Path):
        self.modules_dir = Path(modules_dir)
        self.all_modules = self._discover_valid_modules()
        self.cleaned_count = 0

    def _discover_valid_modules(self) -> set[str]:
        """Discover all valid module names from schema files"""
        valid_modules = set()

        for schema_file in self.modules_dir.glob("*.yaml"):
            if schema_file.name == "module_schema_template.yaml":
                continue

            try:
                with open(schema_file) as f:
                    schema = yaml.safe_load(f)

                module_name = schema.get("identity", {}).get("name")
                if module_name:
                    valid_modules.add(module_name)
            except Exception:
                continue

        return valid_modules

    def cleanup_all_schemas(self) -> None:
        """Clean up all schemas in the directory"""
        print("🧹 Cleaning up module schemas...")
        print(f"Found {len(self.all_modules)} valid modules")

        schema_files = [f for f in self.modules_dir.glob("*.yaml") if f.name != "module_schema_template.yaml"]

        for schema_file in schema_files:
            if self._cleanup_schema_file(schema_file):
                self.cleaned_count += 1

        print(f"✅ Cleaned {self.cleaned_count}/{len(schema_files)} schemas")

    def _cleanup_schema_file(self, schema_file: Path) -> bool:
        """Clean up a single schema file"""
        try:
            with open(schema_file) as f:
                schema = yaml.safe_load(f)

            modified = False

            # 1. Clean up dependencies
            if self._cleanup_dependencies(schema):
                modified = True

            # 2. Fix API version formats
            if self._fix_api_versions(schema):
                modified = True

            # 3. Clean up empty arrays and improve structure
            if self._cleanup_empty_values(schema):
                modified = True

            # 4. Add missing required fields
            if self._add_missing_fields(schema):
                modified = True

            # Save if modified
            if modified:
                with open(schema_file, "w") as f:
                    yaml.dump(schema, f, default_flow_style=False, sort_keys=False, indent=2)
                print(f"  ✅ Cleaned {schema_file.name}")
                return True

            return False

        except Exception as e:
            print(f"  ❌ Error cleaning {schema_file.name}: {e}")
            return False

    def _cleanup_dependencies(self, schema: dict) -> bool:
        """Clean up dependency references"""
        modified = False

        deps_section = schema.get("dependencies", {}).get("internal", {})
        if "requires" in deps_section:
            original_deps = deps_section["requires"]

            # Filter out invalid dependencies
            valid_deps = []
            for dep in original_deps:
                if dep in self.all_modules:
                    valid_deps.append(dep)
                elif self._is_valid_external_import(dep):
                    # Keep some common external imports as they might be valid
                    valid_deps.append(dep)
                # Remove invalid dependencies

            if len(valid_deps) != len(original_deps):
                deps_section["requires"] = valid_deps
                modified = True
                print(f"    Cleaned dependencies: {len(original_deps)} → {len(valid_deps)}")

        return modified

    def _is_valid_external_import(self, import_name: str) -> bool:
        """Check if import might be a valid external library"""
        # Keep some common external libraries
        valid_externals = [
            "asyncio",
            "dataclasses",
            "typing",
            "pathlib",
            "json",
            "yaml",
            "requests",
            "aiohttp",
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "redis",
            "lmdb",
            "numpy",
            "pandas",
            "torch",
            "transformers",
        ]

        root_import = import_name.split(".")[0]
        return root_import in valid_externals

    def _fix_api_versions(self, schema: dict) -> bool:
        """Fix API version formats"""
        modified = False

        api_section = schema.get("contracts", {}).get("api", {})
        if "version" in api_section:
            version = api_section["version"]

            # Fix version format if needed
            if isinstance(version, str) and not version.startswith("v"):
                if version.replace(".", "").isdigit():
                    api_section["version"] = f"v{version}"
                    modified = True
            elif not isinstance(version, str):
                api_section["version"] = f"v{version}"
                modified = True

        return modified

    def _cleanup_empty_values(self, schema: dict) -> bool:
        """Clean up empty arrays and improve structure"""
        modified = False

        # Remove empty import patterns that don't make sense
        discovery = schema.get("discovery", {})
        if "import_patterns" in discovery and not discovery["import_patterns"]:
            module_name = schema.get("identity", {}).get("name", "")
            if module_name:
                # Add a sensible default import pattern
                discovery["import_patterns"] = [f"from {module_name} import *"]
                modified = True

        return modified

    def _add_missing_fields(self, schema: dict) -> bool:
        """Add missing required fields with sensible defaults"""
        modified = False

        # Ensure all required sections exist
        required_sections = {
            "identity": {},
            "ownership": {},
            "contracts": {"api": {}},
            "dependencies": {"internal": {}, "external": {}},
            "runtime": {"processes": {}, "config": {}, "resources": {}},
            "data_and_events": {"pii": {}},
            "security": {"secrets": {}, "compliance": {}},
            "observability": {"logs": {}, "metrics": {}, "slos": {}},
            "test_posture": {"coverage": {}, "tests": {}},
            "risk_and_change": {"risks": []},
            "provenance": {},
        }

        for section, default_value in required_sections.items():
            if section not in schema:
                schema[section] = default_value
                modified = True

        # Add missing required fields in existing sections
        if "authz_model" not in schema.get("security", {}):
            schema["security"]["authz_model"] = "internal_only"
            modified = True

        if "key_metrics" not in schema.get("observability", {}).get("metrics", {}):
            module_name = schema.get("identity", {}).get("name", "unknown")
            safe_name = module_name.replace(".", "_")
            schema["observability"]["metrics"]["key_metrics"] = [
                {"name": f"{safe_name}_health", "target": ">0", "type": "gauge"}
            ]
            modified = True

        return modified


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python module_schema_cleanup.py <modules_dir>")
        sys.exit(1)

    modules_dir = Path(sys.argv[1])

    if not modules_dir.exists():
        print(f"Error: Directory {modules_dir} not found")
        sys.exit(1)

    print("🚀 LUKHAS Module Schema Cleanup Tool")
    print(f"Modules directory: {modules_dir}")
    print("-" * 40)

    cleanup = ModuleSchemaCleanup(modules_dir)
    cleanup.cleanup_all_schemas()

    print("\n🎉 Cleanup complete!")
    print("\nNext steps:")
    print("1. Run validation: python tools/module_schema_validator.py modules/schema_validator.json modules/")
    print("2. Review and commit changes")


if __name__ == "__main__":
    main()
