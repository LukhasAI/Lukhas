#!/usr/bin/env python3
"""
LUKHAS Module Schema Validator

CI/CD validation tool for module schemas. Validates all module schemas against
the JSON Schema definition and performs additional consistency checks.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import json
import sys
from pathlib import Path

import jsonschema
import yaml


class ModuleSchemaValidator:
    """Validates module schemas for CI/CD pipeline"""

    def __init__(self, schema_path: Path, modules_dir: Path):
        self.schema_path = Path(schema_path)
        self.modules_dir = Path(modules_dir)
        self.errors = []
        self.warnings = []

        # Load JSON schema
        with open(self.schema_path) as f:
            self.json_schema = json.load(f)

    def validate_all_schemas(self) -> tuple[bool, list[str], list[str]]:
        """Validate all module schemas"""
        print("🔍 Validating module schemas...")

        schema_files = list(self.modules_dir.glob("*.yaml"))
        if not schema_files:
            self.errors.append("No schema files found in modules directory")
            return False, self.errors, self.warnings

        print(f"Found {len(schema_files)} schema files")

        valid_count = 0
        for schema_file in schema_files:
            if self.validate_schema_file(schema_file):
                valid_count += 1

        # Additional consistency checks
        self._check_cross_schema_consistency(schema_files)

        success = len(self.errors) == 0
        print(f"\n{'✅' if success else '❌'} Validation complete: {valid_count}/{len(schema_files)} schemas valid")

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings found")

        return success, self.errors, self.warnings

    def validate_schema_file(self, schema_file: Path) -> bool:
        """Validate a single schema file"""
        try:
            with open(schema_file) as f:
                schema_data = yaml.safe_load(f)

            # JSON schema validation
            jsonschema.validate(instance=schema_data, schema=self.json_schema)

            # Additional semantic validation
            self._validate_module_semantics(schema_file.name, schema_data)

            return True

        except yaml.YAMLError as e:
            self.errors.append(f"{schema_file.name}: Invalid YAML - {e}")
            return False
        except jsonschema.ValidationError as e:
            self.errors.append(f"{schema_file.name}: Schema validation failed - {e.message}")
            return False
        except Exception as e:
            self.errors.append(f"{schema_file.name}: Validation error - {e}")
            return False

    def _validate_module_semantics(self, filename: str, schema_data: dict) -> None:
        """Perform additional semantic validation"""
        module_name = schema_data.get("identity", {}).get("name", "")
        expected_filename = f"{module_name.replace('.', '_')}.yaml"

        # Check filename matches module name
        if filename != expected_filename:
            self.warnings.append(f"{filename}: Filename should be {expected_filename}")

        # Check tier consistency
        tier = schema_data.get("identity", {}).get("tier", 0)
        lifecycle = schema_data.get("ownership", {}).get("lifecycle", "")

        if tier == 1 and lifecycle not in ["stable"]:
            self.warnings.append(f"{filename}: Tier 1 modules should be stable")

        # Check coverage targets
        coverage = schema_data.get("test_posture", {}).get("coverage", {})
        current_cov = coverage.get("current", 0)
        target_cov = coverage.get("target", 0)

        if current_cov > target_cov:
            self.warnings.append(f"{filename}: Current coverage ({current_cov}) exceeds target ({target_cov})")

        # Check SLO consistency
        slos = schema_data.get("observability", {}).get("slos", {})
        if "latency_p95_ms" in slos and "latency_p99_ms" in slos:
            p95 = slos["latency_p95_ms"]
            p99 = slos["latency_p99_ms"]
            if p99 < p95:
                self.errors.append(f"{filename}: P99 latency cannot be less than P95 latency")

    def _check_cross_schema_consistency(self, schema_files: list[Path]) -> None:
        """Check consistency across all schemas"""
        print("🔗 Checking cross-schema consistency...")

        all_modules = set()
        dependency_graph = {}

        # Load all schemas
        schemas = {}
        for schema_file in schema_files:
            try:
                with open(schema_file) as f:
                    schema_data = yaml.safe_load(f)
                    module_name = schema_data.get("identity", {}).get("name", "")
                    if module_name:
                        all_modules.add(module_name)
                        schemas[module_name] = schema_data

                        # Build dependency graph
                        deps = schema_data.get("dependencies", {}).get("internal", {}).get("requires", [])
                        dependency_graph[module_name] = set(deps)
            except Exception as e:
                self.warnings.append(f"Could not load {schema_file.name} for consistency check: {e}")

        # Check for missing dependencies
        for module, deps in dependency_graph.items():
            for dep in deps:
                if dep not in all_modules:
                    self.warnings.append(f"{module}: Depends on unknown module '{dep}'")

        # Check for circular dependencies
        self._detect_circular_dependencies(dependency_graph)

        # Check lane isolation
        self._check_lane_isolation(schemas)

    def _detect_circular_dependencies(self, dependency_graph: dict[str, set[str]]) -> None:
        """Detect circular dependencies"""

        def has_path(start: str, end: str, visited: set[str]) -> bool:
            if start == end:
                return True
            if start in visited:
                return False

            visited.add(start)
            return any(has_path(neighbor, end, visited) for neighbor in dependency_graph.get(start, set()))

        for module in dependency_graph:
            for dep in dependency_graph.get(module, set()):
                if has_path(dep, module, set()):
                    self.errors.append(f"Circular dependency detected: {module} <-> {dep}")

    def _check_lane_isolation(self, schemas: dict[str, dict]) -> None:
        """Check lane isolation rules"""
        for module_name, schema in schemas.items():
            if module_name.startswith("lukhas."):
                # Lukhas modules should not depend on candidate modules
                deps = schema.get("dependencies", {}).get("internal", {}).get("requires", [])
                for dep in deps:
                    if dep.startswith("candidate."):
                        self.errors.append(f"{module_name}: Lukhas module cannot depend on candidate module '{dep}'")


def main():
    """Main entry point for CI/CD validation"""
    if len(sys.argv) < 3:
        print("Usage: python module_schema_validator.py <schema_file> <modules_dir>")
        sys.exit(1)

    schema_path = Path(sys.argv[1])
    modules_dir = Path(sys.argv[2])

    if not schema_path.exists():
        print(f"Error: Schema file {schema_path} not found")
        sys.exit(1)

    if not modules_dir.exists():
        print(f"Error: Modules directory {modules_dir} not found")
        sys.exit(1)

    print("🚀 LUKHAS Module Schema Validator")
    print(f"Schema: {schema_path}")
    print(f"Modules: {modules_dir}")
    print("-" * 50)

    validator = ModuleSchemaValidator(schema_path, modules_dir)
    success, errors, warnings = validator.validate_all_schemas()

    # Print results
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if success:
        print("\n✅ All schemas are valid!")
        sys.exit(0)
    else:
        print(f"\n❌ Validation failed with {len(errors)} errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
