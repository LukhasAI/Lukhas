#!/usr/bin/env python3
"""
MATRIZ Schema Evolution Guard - T4/0.01% Excellence
==================================================

Regression protection ensuring MATRIZ schema rejects removal of required properties.
Prevents breaking changes that would impact downstream consumers and production systems.

Evolution Rules:
- FORBIDDEN: Removal of required properties
- FORBIDDEN: Removal of enum values
- FORBIDDEN: Constraint tightening (e.g., maxLength reduction)
- ALLOWED: Addition of optional properties
- ALLOWED: Addition of enum values
- ALLOWED: Constraint relaxation

Performance Targets:
- Schema validation: <50ms p95
- Evolution check: <100ms p95
- Regression detection: <10ms p95

Constellation Framework: 🔒 Schema Evolution Protection
"""

import copy
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest

logger = logging.getLogger(__name__)


@dataclass
class EvolutionViolation:
    """Represents a schema evolution violation."""
    violation_type: str
    field_path: str
    old_value: Any
    new_value: Any
    severity: str  # 'breaking', 'warning', 'info'
    description: str


class SchemaEvolutionGuard:
    """Guards against breaking schema changes."""

    def __init__(self):
        """Initialize schema evolution guard."""
        self.project_root = Path(__file__).parent.parent.parent
        self.schema_file = self.project_root / "MATRIZ" / "schemas" / "matriz_schema.json"
        self.snapshots_dir = self.project_root / "tests" / "matriz" / "snapshots"

    def load_current_schema(self) -> Dict[str, Any]:
        """Load current MATRIZ schema."""
        with open(self.schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_baseline_schema(self) -> Dict[str, Any]:
        """Load baseline schema snapshot."""
        baseline_file = self.snapshots_dir / "matriz_schema_1.0.0.json"

        if not baseline_file.exists():
            pytest.skip("Baseline schema snapshot not found - run schema snapshot generation first")

        with open(baseline_file, 'r', encoding='utf-8') as f:
            snapshot_data = json.load(f)

        # Extract actual schema from snapshot format
        canonical_schema_str = snapshot_data["integrity"]["canonical_schema"]
        return json.loads(canonical_schema_str)

    def extract_required_fields(self, schema: Dict[str, Any], path: str = "") -> Set[str]:
        """Extract all required fields from schema recursively."""
        required_fields = set()

        if isinstance(schema, dict):
            # Add direct required fields
            if "required" in schema and isinstance(schema["required"], list):
                for field in schema["required"]:
                    field_path = f"{path}.{field}" if path else field
                    required_fields.add(field_path)

            # Recursively check properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    required_fields.update(
                        self.extract_required_fields(prop_schema, prop_path)
                    )

        return required_fields

    def extract_enum_values(self, schema: Dict[str, Any], path: str = "") -> Dict[str, List[Any]]:
        """Extract all enum values from schema recursively."""
        enum_values = {}

        if isinstance(schema, dict):
            # Check if this schema defines enum values
            if "enum" in schema:
                enum_values[path] = schema["enum"]

            # Recursively check properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    enum_values.update(
                        self.extract_enum_values(prop_schema, prop_path)
                    )

        return enum_values

    def extract_constraints(self, schema: Dict[str, Any], path: str = "") -> Dict[str, Dict[str, Any]]:
        """Extract constraints (minLength, maxLength, minimum, maximum, etc.)."""
        constraints = {}

        if isinstance(schema, dict):
            # Extract constraint properties
            constraint_keys = {
                'minLength', 'maxLength', 'minimum', 'maximum',
                'minItems', 'maxItems', 'pattern'
            }

            schema_constraints = {}
            for key in constraint_keys:
                if key in schema:
                    schema_constraints[key] = schema[key]

            if schema_constraints:
                constraints[path] = schema_constraints

            # Recursively check properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    constraints.update(
                        self.extract_constraints(prop_schema, prop_path)
                    )

        return constraints

    def detect_violations(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> List[EvolutionViolation]:
        """Detect schema evolution violations."""
        violations = []

        # Check required field removal
        baseline_required = self.extract_required_fields(baseline)
        current_required = self.extract_required_fields(current)
        removed_required = baseline_required - current_required

        for field in removed_required:
            violations.append(EvolutionViolation(
                violation_type="required_field_removal",
                field_path=field,
                old_value=True,
                new_value=False,
                severity="breaking",
                description=f"Required field '{field}' was removed - breaks downstream consumers"
            ))

        # Check enum value removal
        baseline_enums = self.extract_enum_values(baseline)
        current_enums = self.extract_enum_values(current)

        for path, baseline_values in baseline_enums.items():
            if path in current_enums:
                current_values = set(current_enums[path])
                baseline_values_set = set(baseline_values)
                removed_values = baseline_values_set - current_values

                for removed_value in removed_values:
                    violations.append(EvolutionViolation(
                        violation_type="enum_value_removal",
                        field_path=path,
                        old_value=list(baseline_values_set),
                        new_value=list(current_values),
                        severity="breaking",
                        description=f"Enum value '{removed_value}' removed from '{path}' - breaks compatibility"
                    ))

        # Check constraint tightening
        baseline_constraints = self.extract_constraints(baseline)
        current_constraints = self.extract_constraints(current)

        for path, baseline_constraint_dict in baseline_constraints.items():
            if path in current_constraints:
                current_constraint_dict = current_constraints[path]

                # Check for constraint tightening
                for constraint_key, baseline_value in baseline_constraint_dict.items():
                    if constraint_key in current_constraint_dict:
                        current_value = current_constraint_dict[constraint_key]

                        # Detect tightening based on constraint type
                        is_tightening = False
                        if constraint_key in ['minLength', 'minimum', 'minItems'] and current_value > baseline_value:
                            is_tightening = True
                        elif constraint_key in ['maxLength', 'maximum', 'maxItems'] and current_value < baseline_value:
                            is_tightening = True

                        if is_tightening:
                            violations.append(EvolutionViolation(
                                violation_type="constraint_tightening",
                                field_path=f"{path}.{constraint_key}",
                                old_value=baseline_value,
                                new_value=current_value,
                                severity="breaking",
                                description=f"Constraint '{constraint_key}' tightened from {baseline_value} to {current_value} in '{path}'"
                            ))

        return violations

    def simulate_required_field_removal(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate removal of a required field for testing."""
        modified_schema = copy.deepcopy(schema)

        # Remove 'decision' from root required fields
        if 'required' in modified_schema and 'decision' in modified_schema['required']:
            modified_schema['required'].remove('decision')
            logger.info("Simulated removal of 'decision' from required fields")

        return modified_schema

    def simulate_enum_value_removal(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate removal of enum values for testing."""
        modified_schema = copy.deepcopy(schema)

        # Find and modify processing_stage enum in decision properties
        decision_props = modified_schema.get("properties", {}).get("decision", {}).get("properties", {})
        if "processing_stage" in decision_props and "enum" in decision_props["processing_stage"]:
            enum_values = decision_props["processing_stage"]["enum"]
            if "finalization" in enum_values:
                enum_values.remove("finalization")
                logger.info("Simulated removal of 'finalization' from processing_stage enum")

        return modified_schema

    def simulate_constraint_tightening(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate constraint tightening for testing."""
        modified_schema = copy.deepcopy(schema)

        # Tighten maxLength constraint for decision.synthesis
        decision_props = modified_schema.get("properties", {}).get("decision", {}).get("properties", {})
        if "synthesis" in decision_props and "maxLength" in decision_props["synthesis"]:
            # Reduce from 10000 to 5000
            decision_props["synthesis"]["maxLength"] = 5000
            logger.info("Simulated constraint tightening: synthesis maxLength 10000 -> 5000")

        return modified_schema


@pytest.mark.schema
@pytest.mark.evolution
class TestSchemaEvolutionGuard:
    """Test schema evolution protection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.guard = SchemaEvolutionGuard()
        self.baseline_schema = self.guard.load_baseline_schema()
        self.current_schema = self.guard.load_current_schema()

    def test_current_schema_no_violations(self):
        """Test current schema has no evolution violations against baseline."""
        start_time = time.perf_counter()

        violations = self.guard.detect_violations(self.baseline_schema, self.current_schema)

        detection_time_ms = (time.perf_counter() - start_time) * 1000

        # Performance target: <100ms p95
        assert detection_time_ms < 100, f"Evolution detection took {detection_time_ms:.2f}ms (target: <100ms)"

        # Log any non-breaking violations for visibility
        breaking_violations = [v for v in violations if v.severity == 'breaking']

        if violations:
            logger.info(f"Detected {len(violations)} schema evolution items:")
            for violation in violations[:5]:  # Log first 5
                logger.info(f"  {violation.violation_type}: {violation.description}")

        # Assert no breaking changes
        assert len(breaking_violations) == 0, (
            "Schema evolution violations detected:\n" +
            "\n".join([f"  - {v.description}" for v in breaking_violations[:3]])
        )

        logger.info(f"✅ Schema evolution validation passed in {detection_time_ms:.2f}ms")

    def test_required_field_removal_detection(self):
        """Test detection of required field removal."""
        # Simulate required field removal
        modified_schema = self.guard.simulate_required_field_removal(self.baseline_schema)

        start_time = time.perf_counter()
        violations = self.guard.detect_violations(self.baseline_schema, modified_schema)
        detection_time_ms = (time.perf_counter() - start_time) * 1000

        # Should detect violation
        required_violations = [v for v in violations if v.violation_type == "required_field_removal"]
        assert len(required_violations) > 0, "Failed to detect required field removal"

        # Verify violation details
        decision_violation = next((v for v in required_violations if "decision" in v.field_path), None)
        assert decision_violation is not None, "Failed to detect 'decision' field removal"
        assert decision_violation.severity == "breaking", "Required field removal should be breaking"

        # Performance check
        assert detection_time_ms < 100, f"Detection took {detection_time_ms:.2f}ms (target: <100ms)"

        logger.info(f"✅ Required field removal detection passed in {detection_time_ms:.2f}ms")

    def test_enum_value_removal_detection(self):
        """Test detection of enum value removal."""
        # Simulate enum value removal
        modified_schema = self.guard.simulate_enum_value_removal(self.baseline_schema)

        start_time = time.perf_counter()
        violations = self.guard.detect_violations(self.baseline_schema, modified_schema)
        detection_time_ms = (time.perf_counter() - start_time) * 1000

        # Should detect violation
        enum_violations = [v for v in violations if v.violation_type == "enum_value_removal"]
        assert len(enum_violations) > 0, "Failed to detect enum value removal"

        # Verify violation details
        processing_stage_violation = next(
            (v for v in enum_violations if "processing_stage" in v.field_path), None
        )
        assert processing_stage_violation is not None, "Failed to detect processing_stage enum removal"
        assert processing_stage_violation.severity == "breaking", "Enum removal should be breaking"

        # Performance check
        assert detection_time_ms < 100, f"Detection took {detection_time_ms:.2f}ms (target: <100ms)"

        logger.info(f"✅ Enum value removal detection passed in {detection_time_ms:.2f}ms")

    def test_constraint_tightening_detection(self):
        """Test detection of constraint tightening."""
        # Simulate constraint tightening
        modified_schema = self.guard.simulate_constraint_tightening(self.baseline_schema)

        start_time = time.perf_counter()
        violations = self.guard.detect_violations(self.baseline_schema, modified_schema)
        detection_time_ms = (time.perf_counter() - start_time) * 1000

        # Should detect violation
        constraint_violations = [v for v in violations if v.violation_type == "constraint_tightening"]
        assert len(constraint_violations) > 0, "Failed to detect constraint tightening"

        # Verify violation details
        max_length_violation = next(
            (v for v in constraint_violations if "maxLength" in v.field_path), None
        )
        assert max_length_violation is not None, "Failed to detect maxLength constraint tightening"
        assert max_length_violation.severity == "breaking", "Constraint tightening should be breaking"
        assert max_length_violation.old_value == 10000, "Incorrect old maxLength value"
        assert max_length_violation.new_value == 5000, "Incorrect new maxLength value"

        # Performance check
        assert detection_time_ms < 100, f"Detection took {detection_time_ms:.2f}ms (target: <100ms)"

        logger.info(f"✅ Constraint tightening detection passed in {detection_time_ms:.2f}ms")

    def test_allowed_evolution_changes(self):
        """Test that allowed evolution changes don't trigger violations."""
        modified_schema = copy.deepcopy(self.baseline_schema)

        # Add optional property (allowed)
        if "properties" in modified_schema:
            modified_schema["properties"]["new_optional_field"] = {
                "type": "string",
                "description": "New optional field for testing"
            }

        # Add enum value (allowed)
        decision_props = modified_schema.get("properties", {}).get("decision", {}).get("properties", {})
        if "processing_stage" in decision_props and "enum" in decision_props["processing_stage"]:
            decision_props["processing_stage"]["enum"].append("new_experimental_stage")

        # Relax constraint (allowed) - increase maxLength
        if "synthesis" in decision_props and "maxLength" in decision_props["synthesis"]:
            decision_props["synthesis"]["maxLength"] = 15000

        start_time = time.perf_counter()
        violations = self.guard.detect_violations(self.baseline_schema, modified_schema)
        detection_time_ms = (time.perf_counter() - start_time) * 1000

        # Should have no breaking violations
        breaking_violations = [v for v in violations if v.severity == 'breaking']
        assert len(breaking_violations) == 0, (
            "Allowed changes incorrectly flagged as breaking:\n" +
            "\n".join([f"  - {v.description}" for v in breaking_violations])
        )

        # Performance check
        assert detection_time_ms < 100, f"Detection took {detection_time_ms:.2f}ms (target: <100ms)"

        logger.info(f"✅ Allowed evolution changes validation passed in {detection_time_ms:.2f}ms")

    def test_comprehensive_evolution_guard_performance(self):
        """Test comprehensive evolution guard performance under load."""
        large_schema = copy.deepcopy(self.baseline_schema)

        # Add many properties to stress test
        for i in range(100):
            large_schema["properties"][f"test_prop_{i}"] = {
                "type": "string",
                "maxLength": 100,
                "enum": [f"value_{j}" for j in range(10)]
            }

        # Run multiple iterations to get stable timing
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            violations = self.guard.detect_violations(large_schema, large_schema)
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)

        mean_time = sum(times) / len(times)
        p95_time = sorted(times)[int(0.95 * len(times))]

        # Should have no violations (identical schemas)
        assert len(violations) == 0, "Identical schemas should have no violations"

        # Performance targets
        assert mean_time < 50, f"Mean detection time {mean_time:.2f}ms exceeds 50ms target"
        assert p95_time < 100, f"P95 detection time {p95_time:.2f}ms exceeds 100ms target"

        logger.info(f"✅ Performance test passed - mean: {mean_time:.2f}ms, p95: {p95_time:.2f}ms")

    def test_evolution_guard_integration(self):
        """Test evolution guard integration with CI/CD pipeline."""
        # This would typically be called by CI to validate schema changes
        start_time = time.perf_counter()

        try:
            baseline = self.guard.load_baseline_schema()
            current = self.guard.load_current_schema()
            violations = self.guard.detect_violations(baseline, current)

            # Generate evolution report
            report = {
                "validation_timestamp": time.time(),
                "baseline_hash": hashlib.sha256(json.dumps(baseline, sort_keys=True).encode()).hexdigest()[:16],
                "current_hash": hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest()[:16],
                "violations": [
                    {
                        "type": v.violation_type,
                        "path": v.field_path,
                        "severity": v.severity,
                        "description": v.description
                    } for v in violations
                ],
                "breaking_changes": len([v for v in violations if v.severity == 'breaking']),
                "validation_passed": len([v for v in violations if v.severity == 'breaking']) == 0
            }

            validation_time_ms = (time.perf_counter() - start_time) * 1000
            report["validation_time_ms"] = validation_time_ms

            # Save report for CI artifacts
            report_file = Path(__file__).parent.parent.parent / "artifacts" / "schema_evolution_report.json"
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Evolution validation report saved: {report_file}")

            # Assert CI readiness
            assert report["validation_passed"], f"Schema evolution violations block deployment: {report['breaking_changes']} breaking changes"
            assert validation_time_ms < 100, f"CI validation took {validation_time_ms:.2f}ms (target: <100ms)"

            logger.info(f"✅ CI integration validation passed in {validation_time_ms:.2f}ms")

        except Exception as e:
            logger.error(f"Evolution guard integration failed: {e}")
            raise


if __name__ == "__main__":
    # Run schema evolution validation standalone
    def run_evolution_validation():
        print("Running MATRIZ Schema Evolution Validation...")
        print("T4/0.01% Excellence Standards")
        print()

        guard = SchemaEvolutionGuard()

        try:
            baseline = guard.load_baseline_schema()
            current = guard.load_current_schema()

            print("Checking for breaking schema changes...")
            start_time = time.perf_counter()
            violations = guard.detect_violations(baseline, current)
            detection_time = (time.perf_counter() - start_time) * 1000

            breaking_violations = [v for v in violations if v.severity == 'breaking']

            if breaking_violations:
                print(f"❌ BREAKING CHANGES DETECTED ({len(breaking_violations)}):")
                for violation in breaking_violations:
                    print(f"   - {violation.description}")
                print("\n💥 Schema evolution blocks deployment")
                return False
            else:
                print("✅ No breaking changes detected")
                print(f"⚡ Validation completed in {detection_time:.2f}ms")

                if violations:
                    print(f"\n💡 Non-breaking changes detected ({len(violations)}):")
                    for violation in violations[:3]:
                        print(f"   - {violation.description}")

                return True

        except Exception as e:
            print(f"❌ Evolution validation failed: {e}")
            return False

    import sys
    success = run_evolution_validation()
    sys.exit(0 if success else 1)
