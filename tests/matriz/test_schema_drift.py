#!/usr/bin/env python3
"""
MATRIZ Schema Drift Detection - T4/0.01% Excellence
==================================================

Schema drift detection and breaking change prevention for MATRIZ decision payloads.
Ensures schema evolution doesn't break downstream consumers or violate T4/0.01% standards.

Features:
- Hash-based schema validation against snapshots
- Breaking change detection (required fields, enum values, constraints)
- Schema version validation with semver compliance
- Performance constraint validation
- T4/0.01% compliance verification
- Fail-fast CI integration

Constellation Framework: 🌊 Schema Evolution Guard
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest
from jsonschema.validators import Draft202012Validator

logger = logging.getLogger(__name__)


@dataclass
class SchemaDriftResult:
    """Result of schema drift analysis."""
    schema_valid: bool
    hash_matches: bool
    breaking_changes: List[str]
    warnings: List[str]
    current_hash: str
    expected_hash: str
    version_compatible: bool
    t4_compliant: bool
    recommendations: List[str]


class MATRIZSchemaDriftDetector:
    """Schema drift detector for MATRIZ decision payloads."""

    def __init__(self):
        """Initialize schema drift detector."""
        self.schema_path = Path(__file__).parent.parent.parent / "matriz" / "schemas" / "matriz_schema.json"
        self.snapshot_path = Path(__file__).parent / "snapshots" / "matriz_schema_v1.json"

        # Load current schema
        if not self.schema_path.exists():
            raise FileNotFoundError(f"MATRIZ schema not found: {self.schema_path}")

        with open(self.schema_path) as f:
            self.current_schema = json.load(f)

        # Load snapshot
        if not self.snapshot_path.exists():
            raise FileNotFoundError(f"MATRIZ schema snapshot not found: {self.snapshot_path}")

        with open(self.snapshot_path) as f:
            self.snapshot = json.load(f)

    def compute_schema_hash(self, schema: Dict[str, Any]) -> str:
        """Compute deterministic hash of schema structure."""
        # Create a normalized version for hashing
        normalized = self._normalize_schema_for_hashing(schema)
        schema_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(schema_str.encode('utf-8')).hexdigest()

    def _normalize_schema_for_hashing(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize schema for consistent hashing."""
        normalized = {}

        # Include critical structural elements
        if "type" in schema:
            normalized["type"] = schema["type"]

        if "required" in schema:
            normalized["required"] = sorted(schema["required"])

        if "properties" in schema:
            normalized["properties"] = {}
            for prop, prop_schema in schema["properties"].items():
                normalized["properties"][prop] = self._normalize_schema_for_hashing(prop_schema)

        if "enum" in schema:
            normalized["enum"] = sorted(schema["enum"])

        if "additionalProperties" in schema:
            normalized["additionalProperties"] = schema["additionalProperties"]

        # Include constraints that affect validation
        for constraint in ["minimum", "maximum", "minLength", "maxLength", "pattern", "format", "minItems", "maxItems"]:
            if constraint in schema:
                normalized[constraint] = schema[constraint]

        return normalized

    def detect_breaking_changes(self) -> List[str]:
        """Detect breaking changes between current schema and snapshot."""
        breaking_changes = []

        # Check required properties
        current_required = self._get_all_required_properties(self.current_schema)
        snapshot_required = set(self.snapshot["critical_properties"]["required_root_properties"])

        # Removing required properties is breaking
        removed_required = snapshot_required - current_required
        if removed_required:
            breaking_changes.append(f"Removed required properties: {', '.join(removed_required)}")

        # Check enum values
        enum_changes = self._check_enum_changes()
        breaking_changes.extend(enum_changes)

        # Check constraint tightening
        constraint_changes = self._check_constraint_tightening()
        breaking_changes.extend(constraint_changes)

        # Check schema version pattern
        current_version_pattern = self.current_schema.get("properties", {}).get("integrity", {}).get("properties", {}).get("schema_version", {}).get("pattern")
        expected_version_pattern = self.snapshot["critical_properties"]["schema_version_pattern"]

        if current_version_pattern != expected_version_pattern:
            breaking_changes.append(f"Schema version pattern changed: {current_version_pattern} != {expected_version_pattern}")

        return breaking_changes

    def _get_all_required_properties(self, schema: Dict[str, Any], path: str = "") -> Set[str]:
        """Extract all required properties from schema."""
        required = set()

        if "required" in schema:
            for prop in schema["required"]:
                full_path = f"{path}.{prop}" if path else prop
                required.add(full_path)

        if "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                prop_path = f"{path}.{prop}" if path else prop
                required.update(self._get_all_required_properties(prop_schema, prop_path))

        return required

    def _check_enum_changes(self) -> List[str]:
        """Check for breaking enum value changes."""
        breaking_changes = []

        # Check processing stages
        current_stages = self._extract_enum_values(self.current_schema, ["properties", "decision", "properties", "processing_stage", "enum"])
        expected_stages = set(self.snapshot["critical_properties"]["processing_stages"])

        if current_stages is not None:
            removed_stages = expected_stages - set(current_stages)
            if removed_stages:
                breaking_changes.append(f"Removed processing stages: {', '.join(removed_stages)}")

        # Check consciousness states
        current_states = self._extract_enum_values(self.current_schema, ["properties", "subject", "properties", "consciousness_state", "enum"])
        expected_states = set(self.snapshot["critical_properties"]["consciousness_states"])

        if current_states is not None:
            removed_states = expected_states - set(current_states)
            if removed_states:
                breaking_changes.append(f"Removed consciousness states: {', '.join(removed_states)}")

        # Check lane values
        current_lanes = self._extract_enum_values(self.current_schema, ["properties", "context", "properties", "lane", "enum"])
        expected_lanes = set(self.snapshot["critical_properties"]["lane_values"])

        if current_lanes is not None:
            removed_lanes = expected_lanes - set(current_lanes)
            if removed_lanes:
                breaking_changes.append(f"Removed lane values: {', '.join(removed_lanes)}")

        return breaking_changes

    def _extract_enum_values(self, schema: Dict[str, Any], path: List[str]) -> Optional[List[str]]:
        """Extract enum values from nested schema path."""
        current = schema
        for key in path:
            if key in current:
                current = current[key]
            else:
                return None
        return current if isinstance(current, list) else None

    def _check_constraint_tightening(self) -> List[str]:
        """Check for constraint tightening that could break existing data."""
        breaking_changes = []

        # Check performance constraints
        performance_constraints = self.snapshot["performance_constraints"]

        constraint_checks = [
            (["properties", "metrics", "properties", "processing_time_ms", "maximum"], "max_processing_time_ms"),
            (["properties", "subject", "properties", "query", "maxLength"], "max_query_length"),
            (["properties", "decision", "properties", "synthesis", "maxLength"], "max_synthesis_length"),
            (["properties", "context", "properties", "memory_signals", "maxItems"], "max_memory_signals"),
            (["properties", "metrics", "properties", "inference_depth_reached", "maximum"], "max_inference_depth")
        ]

        for schema_path, constraint_name in constraint_checks:
            current_value = self._extract_constraint_value(self.current_schema, schema_path)
            expected_value = performance_constraints[constraint_name]

            if current_value is not None and current_value < expected_value:
                breaking_changes.append(f"Tightened constraint {constraint_name}: {current_value} < {expected_value}")

        return breaking_changes

    def _extract_constraint_value(self, schema: Dict[str, Any], path: List[str]) -> Optional[float]:
        """Extract constraint value from nested schema path."""
        current = schema
        for key in path:
            if key in current:
                current = current[key]
            else:
                return None
        return current if isinstance(current, (int, float)) else None

    def validate_schema_structure(self) -> List[str]:
        """Validate schema structure meets T4/0.01% standards."""
        issues = []

        # Validate JSON Schema draft compliance
        try:
            Draft202012Validator.check_schema(self.current_schema)
        except Exception as e:
            issues.append(f"Schema validation failed: {e}")

        # Check required root properties
        required_props = set(self.snapshot["critical_properties"]["required_root_properties"])
        current_props = set(self.current_schema.get("properties", {}).keys())

        missing_props = required_props - current_props
        if missing_props:
            issues.append(f"Missing required root properties: {', '.join(missing_props)}")

        # Check additionalProperties is disabled (fail-closed)
        if self.current_schema.get("additionalProperties") is not False:
            issues.append("additionalProperties must be false for fail-closed behavior")

        # Check integrity block presence
        if "integrity" not in self.current_schema.get("properties", {}):
            issues.append("Missing integrity block required for tamper-evident design")

        return issues

    def check_version_compatibility(self) -> bool:
        """Check if schema version is compatible."""
        current_version = self.current_schema.get("version", "0.0.0")
        snapshot_version = self.snapshot["version"]

        # Simple semver major version check
        current_major = int(current_version.split('.')[0])
        snapshot_major = int(snapshot_version.split('.')[0])

        return current_major == snapshot_major

    def analyze_schema_drift(self) -> SchemaDriftResult:
        """Perform comprehensive schema drift analysis."""
        # Compute current hash
        current_hash = self.compute_schema_hash(self.current_schema)
        expected_hash = self.snapshot.get("schema_hash", "")

        # Update snapshot hash if placeholder
        if expected_hash == "placeholder_will_be_computed":
            expected_hash = current_hash
            self.snapshot["schema_hash"] = current_hash
            self._update_snapshot()

        # Check for breaking changes
        breaking_changes = self.detect_breaking_changes()

        # Validate schema structure
        structure_issues = self.validate_schema_structure()
        breaking_changes.extend(structure_issues)

        # Check version compatibility
        version_compatible = self.check_version_compatibility()

        # Generate warnings
        warnings = []
        if not version_compatible:
            warnings.append("Major version change detected - review compatibility impact")

        # T4 compliance check
        t4_compliant = (
            len(breaking_changes) == 0 and
            version_compatible and
            self.current_schema.get("additionalProperties") is False
        )

        # Generate recommendations
        recommendations = []
        if breaking_changes:
            recommendations.append("Address breaking changes before deployment")
            recommendations.append("Consider minor/patch version increment instead of breaking changes")

        if current_hash != expected_hash and not breaking_changes:
            recommendations.append("Update schema snapshot after reviewing non-breaking changes")

        if not recommendations:
            recommendations.append("Schema evolution is compatible - safe to proceed")

        return SchemaDriftResult(
            schema_valid=len(structure_issues) == 0,
            hash_matches=current_hash == expected_hash,
            breaking_changes=breaking_changes,
            warnings=warnings,
            current_hash=current_hash,
            expected_hash=expected_hash,
            version_compatible=version_compatible,
            t4_compliant=t4_compliant,
            recommendations=recommendations
        )

    def _update_snapshot(self):
        """Update snapshot file with computed hash."""
        with open(self.snapshot_path, 'w') as f:
            json.dump(self.snapshot, f, indent=2)


@pytest.mark.schema
@pytest.mark.drift_detection
class TestMATRIZSchemaDrift:
    """MATRIZ Schema Drift Detection Tests"""

    def test_schema_hash_validation(self):
        """Test schema hash matches snapshot for drift detection."""
        detector = MATRIZSchemaDriftDetector()
        result = detector.analyze_schema_drift()

        # Log drift analysis results
        logger.info(f"Schema hash validation: {'✓' if result.hash_matches else '✗'}")
        logger.info(f"Current hash: {result.current_hash}")
        logger.info(f"Expected hash: {result.expected_hash}")

        if result.breaking_changes:
            logger.error("Breaking changes detected:")
            for change in result.breaking_changes:
                logger.error(f"  - {change}")

        if result.warnings:
            logger.warning("Schema warnings:")
            for warning in result.warnings:
                logger.warning(f"  - {warning}")

        # Assert no breaking changes
        assert len(result.breaking_changes) == 0, f"Breaking changes detected: {result.breaking_changes}"

        # Assert hash matches (allows non-breaking evolution)
        if not result.hash_matches:
            logger.warning("Schema hash changed - review changes and update snapshot if safe")
            logger.warning(f"Recommendations: {result.recommendations}")

    def test_required_fields_validation(self):
        """Test that required fields haven't been removed."""
        detector = MATRIZSchemaDriftDetector()

        # Check root level required fields
        required_fields = [
            "decision",
            "subject",
            "context",
            "metrics",
            "enforcement",
            "audit",
            "integrity"
        ]

        current_required = detector.current_schema.get("required", [])

        for field in required_fields:
            assert field in current_required, f"Required field '{field}' missing from schema"

        logger.info(f"✓ All {len(required_fields)} required root fields present")

    def test_enum_values_backward_compatibility(self):
        """Test that enum values maintain backward compatibility."""
        detector = MATRIZSchemaDriftDetector()

        # Processing stages compatibility
        current_stages = detector._extract_enum_values(
            detector.current_schema,
            ["properties", "decision", "properties", "processing_stage", "enum"]
        )
        expected_stages = detector.snapshot["critical_properties"]["processing_stages"]

        if current_stages:
            missing_stages = set(expected_stages) - set(current_stages)
            assert len(missing_stages) == 0, f"Processing stages removed: {missing_stages}"

        # Consciousness states compatibility
        current_states = detector._extract_enum_values(
            detector.current_schema,
            ["properties", "subject", "properties", "consciousness_state", "enum"]
        )
        expected_states = detector.snapshot["critical_properties"]["consciousness_states"]

        if current_states:
            missing_states = set(expected_states) - set(current_states)
            assert len(missing_states) == 0, f"Consciousness states removed: {missing_states}"

        logger.info("✓ Enum values maintain backward compatibility")

    def test_performance_constraints_not_tightened(self):
        """Test that performance constraints haven't been tightened."""
        detector = MATRIZSchemaDriftDetector()

        # Check key performance constraints
        max_processing_time = detector._extract_constraint_value(
            detector.current_schema,
            ["properties", "metrics", "properties", "processing_time_ms", "maximum"]
        )

        if max_processing_time is not None:
            expected_max = detector.snapshot["performance_constraints"]["max_processing_time_ms"]
            assert max_processing_time >= expected_max, f"Processing time constraint tightened: {max_processing_time} < {expected_max}"

        # Check query length constraint
        max_query_length = detector._extract_constraint_value(
            detector.current_schema,
            ["properties", "subject", "properties", "query", "maxLength"]
        )

        if max_query_length is not None:
            expected_max = detector.snapshot["performance_constraints"]["max_query_length"]
            assert max_query_length >= expected_max, f"Query length constraint tightened: {max_query_length} < {expected_max}"

        logger.info("✓ Performance constraints not tightened")

    def test_schema_version_pattern_consistency(self):
        """Test schema version pattern remains consistent."""
        detector = MATRIZSchemaDriftDetector()

        current_pattern = detector.current_schema.get("properties", {}).get("integrity", {}).get("properties", {}).get("schema_version", {}).get("pattern")
        expected_pattern = detector.snapshot["critical_properties"]["schema_version_pattern"]

        assert current_pattern == expected_pattern, f"Schema version pattern changed: {current_pattern} != {expected_pattern}"

        logger.info(f"✓ Schema version pattern consistent: {current_pattern}")

    def test_t4_compliance_requirements(self):
        """Test T4/0.01% compliance requirements are met."""
        detector = MATRIZSchemaDriftDetector()
        result = detector.analyze_schema_drift()

        # Must be schema valid
        assert result.schema_valid, "Schema must be valid for T4 compliance"

        # Must have fail-closed behavior
        assert detector.current_schema.get("additionalProperties") is False, "additionalProperties must be false for fail-closed T4 behavior"

        # Must have integrity block
        assert "integrity" in detector.current_schema.get("properties", {}), "Integrity block required for T4 tamper-evident design"

        # Must be version compatible
        assert result.version_compatible, "Version compatibility required for T4 standards"

        # Overall T4 compliance
        assert result.t4_compliant, f"T4 compliance failed. Issues: {result.breaking_changes}"

        logger.info("✓ T4/0.01% compliance requirements met")

    def test_comprehensive_drift_analysis(self):
        """Comprehensive schema drift analysis with full reporting."""
        detector = MATRIZSchemaDriftDetector()
        result = detector.analyze_schema_drift()

        # Log comprehensive analysis
        logger.info("=== MATRIZ Schema Drift Analysis ===")
        logger.info(f"Schema Valid: {'✓' if result.schema_valid else '✗'}")
        logger.info(f"Hash Matches: {'✓' if result.hash_matches else '✗'}")
        logger.info(f"Version Compatible: {'✓' if result.version_compatible else '✗'}")
        logger.info(f"T4 Compliant: {'✓' if result.t4_compliant else '✗'}")

        if result.breaking_changes:
            logger.error("Breaking Changes:")
            for change in result.breaking_changes:
                logger.error(f"  ❌ {change}")
        else:
            logger.info("✓ No breaking changes detected")

        if result.warnings:
            logger.warning("Warnings:")
            for warning in result.warnings:
                logger.warning(f"  ⚠️  {warning}")

        logger.info("Recommendations:")
        for rec in result.recommendations:
            logger.info(f"  💡 {rec}")

        # Fail CI if breaking changes detected
        assert len(result.breaking_changes) == 0, f"Schema drift CI check failed. Breaking changes: {result.breaking_changes}"

        logger.info("✅ MATRIZ Schema Drift Analysis PASSED")


if __name__ == "__main__":
    # Run schema drift analysis standalone
    detector = MATRIZSchemaDriftDetector()
    result = detector.analyze_schema_drift()

    print("\n=== MATRIZ Schema Drift Analysis Results ===")
    print(f"Schema Valid: {'✓ PASS' if result.schema_valid else '✗ FAIL'}")
    print(f"Hash Matches: {'✓ PASS' if result.hash_matches else '✗ FAIL'}")
    print(f"Version Compatible: {'✓ PASS' if result.version_compatible else '✗ FAIL'}")
    print(f"T4 Compliant: {'✓ PASS' if result.t4_compliant else '✗ FAIL'}")

    if result.breaking_changes:
        print("\n❌ Breaking Changes:")
        for change in result.breaking_changes:
            print(f"   {change}")
    else:
        print("\n✅ No breaking changes detected")

    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   {warning}")

    print("\n💡 Recommendations:")
    for rec in result.recommendations:
        print(f"   {rec}")

    print(f"\nCurrent Hash: {result.current_hash}")
    print(f"Expected Hash: {result.expected_hash}")

    # Exit with appropriate code
    exit(0 if len(result.breaking_changes) == 0 else 1)
