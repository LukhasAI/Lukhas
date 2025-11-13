#!/usr/bin/env python3
"""
OpenAPI Specification Drift Detection Tool

Detects changes between OpenAPI specifications to prevent breaking API changes.
Supports deep JSON Schema comparison and provides machine-readable output.

Usage:
    python tools/check_openapi_drift.py --baseline baseline.json --current current.json
    python tools/check_openapi_drift.py --autofix  # Update baseline with current
    python tools/check_openapi_drift.py --format json > drift_report.json

# ΛTAG: api_drift_detection, openapi_validation, ci_cd_integration, api_stability
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from deepdiff import DeepDiff
    DEEPDIFF_AVAILABLE = True
except ImportError:
    DEEPDIFF_AVAILABLE = False
    print("⚠️  Warning: deepdiff not installed. Install with: pip install deepdiff", file=sys.stderr)


@dataclass
class DriftChange:
    """Represents a single drift change"""
    change_type: str  # added, removed, modified
    path: str
    severity: str  # breaking, compatible, informational
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    description: str = ""


@dataclass
class DriftReport:
    """Complete drift detection report"""
    baseline_version: str
    current_version: str
    has_drift: bool
    breaking_changes: int = 0
    compatible_changes: int = 0
    informational_changes: int = 0
    changes: List[DriftChange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "baseline_version": self.baseline_version,
            "current_version": self.current_version,
            "has_drift": self.has_drift,
            "summary": {
                "breaking_changes": self.breaking_changes,
                "compatible_changes": self.compatible_changes,
                "informational_changes": self.informational_changes,
                "total_changes": len(self.changes)
            },
            "changes": [asdict(change) for change in self.changes]
        }


class OpenAPIDriftDetector:
    """Detects drift between OpenAPI specifications"""

    # Breaking changes that violate backwards compatibility
    BREAKING_PATTERNS = {
        "paths_removed",
        "required_parameters_added",
        "response_schemas_removed",
        "enum_values_removed",
        "property_made_required",
        "type_changed",
    }

    # Compatible changes that don't break existing clients
    COMPATIBLE_PATTERNS = {
        "paths_added",
        "optional_parameters_added",
        "response_schemas_added",
        "enum_values_added",
        "property_made_optional",
    }

    def __init__(self, baseline_path: str, current_path: str):
        """
        Initialize drift detector

        Args:
            baseline_path: Path to baseline OpenAPI spec
            current_path: Path to current OpenAPI spec
        """
        self.baseline_path = Path(baseline_path)
        self.current_path = Path(current_path)

        self.baseline = self._load_spec(self.baseline_path)
        self.current = self._load_spec(self.current_path)

    def _load_spec(self, path: Path) -> Dict[str, Any]:
        """Load OpenAPI specification from file"""
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in {path}: {e}", file=sys.stderr)
            sys.exit(1)

    def detect_drift(self) -> DriftReport:
        """
        Detect drift between baseline and current specs

        Returns:
            DriftReport with all detected changes
        """
        baseline_version = self.baseline.get("info", {}).get("version", "unknown")
        current_version = self.current.get("info", {}).get("version", "unknown")

        report = DriftReport(
            baseline_version=baseline_version,
            current_version=current_version,
            has_drift=False
        )

        # Detect path changes
        path_changes = self._detect_path_changes()
        report.changes.extend(path_changes)

        # Detect schema changes
        schema_changes = self._detect_schema_changes()
        report.changes.extend(schema_changes)

        # Detect security changes
        security_changes = self._detect_security_changes()
        report.changes.extend(security_changes)

        # Detect server changes
        server_changes = self._detect_server_changes()
        report.changes.extend(server_changes)

        # Calculate summary
        report.has_drift = len(report.changes) > 0
        report.breaking_changes = sum(1 for c in report.changes if c.severity == "breaking")
        report.compatible_changes = sum(1 for c in report.changes if c.severity == "compatible")
        report.informational_changes = sum(1 for c in report.changes if c.severity == "informational")

        return report

    def _detect_path_changes(self) -> List[DriftChange]:
        """Detect changes in API paths"""
        changes = []

        baseline_paths = set(self.baseline.get("paths", {}).keys())
        current_paths = set(self.current.get("paths", {}).keys())

        # Removed paths (BREAKING)
        removed_paths = baseline_paths - current_paths
        for path in removed_paths:
            changes.append(DriftChange(
                change_type="removed",
                path=f"paths.{path}",
                severity="breaking",
                old_value=path,
                description=f"API endpoint removed: {path}"
            ))

        # Added paths (COMPATIBLE)
        added_paths = current_paths - baseline_paths
        for path in added_paths:
            changes.append(DriftChange(
                change_type="added",
                path=f"paths.{path}",
                severity="compatible",
                new_value=path,
                description=f"New API endpoint added: {path}"
            ))

        # Modified paths (check methods)
        common_paths = baseline_paths & current_paths
        for path in common_paths:
            method_changes = self._detect_method_changes(path)
            changes.extend(method_changes)

        return changes

    def _detect_method_changes(self, path: str) -> List[DriftChange]:
        """Detect changes in HTTP methods for a path"""
        changes = []

        baseline_methods = set(self.baseline["paths"][path].keys())
        current_methods = set(self.current["paths"][path].keys())

        # Removed methods (BREAKING)
        removed_methods = baseline_methods - current_methods
        for method in removed_methods:
            if method not in ["summary", "description", "parameters"]:
                changes.append(DriftChange(
                    change_type="removed",
                    path=f"paths.{path}.{method}",
                    severity="breaking",
                    old_value=method.upper(),
                    description=f"HTTP method removed: {method.upper()} {path}"
                ))

        # Added methods (COMPATIBLE)
        added_methods = current_methods - baseline_methods
        for method in added_methods:
            if method not in ["summary", "description", "parameters"]:
                changes.append(DriftChange(
                    change_type="added",
                    path=f"paths.{path}.{method}",
                    severity="compatible",
                    new_value=method.upper(),
                    description=f"New HTTP method added: {method.upper()} {path}"
                ))

        # Check parameter changes for common methods
        common_methods = baseline_methods & current_methods
        for method in common_methods:
            if method not in ["summary", "description", "parameters"]:
                param_changes = self._detect_parameter_changes(path, method)
                changes.extend(param_changes)

                response_changes = self._detect_response_changes(path, method)
                changes.extend(response_changes)

        return changes

    def _detect_parameter_changes(self, path: str, method: str) -> List[DriftChange]:
        """Detect changes in parameters for a method"""
        changes = []

        baseline_params = self.baseline["paths"][path].get(method, {}).get("parameters", [])
        current_params = self.current["paths"][path].get(method, {}).get("parameters", [])

        # Convert to dict for easier comparison
        baseline_params_dict = {p["name"]: p for p in baseline_params}
        current_params_dict = {p["name"]: p for p in current_params}

        baseline_names = set(baseline_params_dict.keys())
        current_names = set(current_params_dict.keys())

        # Removed parameters
        removed_params = baseline_names - current_names
        for param_name in removed_params:
            param = baseline_params_dict[param_name]
            severity = "breaking" if param.get("required", False) else "compatible"
            changes.append(DriftChange(
                change_type="removed",
                path=f"paths.{path}.{method}.parameters.{param_name}",
                severity=severity,
                old_value=param,
                description=f"Parameter removed: {param_name} ({severity})"
            ))

        # Added parameters
        added_params = current_names - baseline_names
        for param_name in added_params:
            param = current_params_dict[param_name]
            severity = "breaking" if param.get("required", False) else "compatible"
            changes.append(DriftChange(
                change_type="added",
                path=f"paths.{path}.{method}.parameters.{param_name}",
                severity=severity,
                new_value=param,
                description=f"New parameter added: {param_name} ({'required' if param.get('required') else 'optional'})"
            ))

        # Modified parameters
        common_params = baseline_names & current_names
        for param_name in common_params:
            baseline_param = baseline_params_dict[param_name]
            current_param = current_params_dict[param_name]

            # Check if required status changed
            if baseline_param.get("required") != current_param.get("required"):
                if current_param.get("required"):
                    # Made required (BREAKING)
                    changes.append(DriftChange(
                        change_type="modified",
                        path=f"paths.{path}.{method}.parameters.{param_name}.required",
                        severity="breaking",
                        old_value=False,
                        new_value=True,
                        description=f"Parameter '{param_name}' made required (BREAKING)"
                    ))
                else:
                    # Made optional (COMPATIBLE)
                    changes.append(DriftChange(
                        change_type="modified",
                        path=f"paths.{path}.{method}.parameters.{param_name}.required",
                        severity="compatible",
                        old_value=True,
                        new_value=False,
                        description=f"Parameter '{param_name}' made optional"
                    ))

        return changes

    def _detect_response_changes(self, path: str, method: str) -> List[DriftChange]:
        """Detect changes in responses for a method"""
        changes = []

        baseline_responses = self.baseline["paths"][path].get(method, {}).get("responses", {})
        current_responses = self.current["paths"][path].get(method, {}).get("responses", {})

        baseline_codes = set(baseline_responses.keys())
        current_codes = set(current_responses.keys())

        # Removed response codes (BREAKING for success codes)
        removed_codes = baseline_codes - current_codes
        for code in removed_codes:
            severity = "breaking" if code.startswith("2") else "informational"
            changes.append(DriftChange(
                change_type="removed",
                path=f"paths.{path}.{method}.responses.{code}",
                severity=severity,
                old_value=code,
                description=f"Response code removed: {code}"
            ))

        # Added response codes (COMPATIBLE)
        added_codes = current_codes - baseline_codes
        for code in added_codes:
            changes.append(DriftChange(
                change_type="added",
                path=f"paths.{path}.{method}.responses.{code}",
                severity="compatible",
                new_value=code,
                description=f"New response code added: {code}"
            ))

        return changes

    def _detect_schema_changes(self) -> List[DriftChange]:
        """Detect changes in component schemas"""
        changes = []

        baseline_schemas = self.baseline.get("components", {}).get("schemas", {})
        current_schemas = self.current.get("components", {}).get("schemas", {})

        baseline_names = set(baseline_schemas.keys())
        current_names = set(current_schemas.keys())

        # Removed schemas (BREAKING)
        removed_schemas = baseline_names - current_names
        for schema_name in removed_schemas:
            changes.append(DriftChange(
                change_type="removed",
                path=f"components.schemas.{schema_name}",
                severity="breaking",
                old_value=schema_name,
                description=f"Schema removed: {schema_name}"
            ))

        # Added schemas (COMPATIBLE)
        added_schemas = current_names - baseline_names
        for schema_name in added_schemas:
            changes.append(DriftChange(
                change_type="added",
                path=f"components.schemas.{schema_name}",
                severity="compatible",
                new_value=schema_name,
                description=f"New schema added: {schema_name}"
            ))

        # Use DeepDiff for modified schemas if available
        if DEEPDIFF_AVAILABLE:
            common_schemas = baseline_names & current_names
            for schema_name in common_schemas:
                schema_changes = self._detect_schema_property_changes(schema_name)
                changes.extend(schema_changes)

        return changes

    def _detect_schema_property_changes(self, schema_name: str) -> List[DriftChange]:
        """Detect changes in schema properties using DeepDiff"""
        changes = []

        if not DEEPDIFF_AVAILABLE:
            return changes

        baseline_schema = self.baseline["components"]["schemas"][schema_name]
        current_schema = self.current["components"]["schemas"][schema_name]

        diff = DeepDiff(baseline_schema, current_schema, ignore_order=True)

        # Analyze diff results
        if "dictionary_item_added" in diff:
            for item in diff["dictionary_item_added"]:
                changes.append(DriftChange(
                    change_type="added",
                    path=f"components.schemas.{schema_name}.{item}",
                    severity="compatible",
                    description=f"Property added to schema {schema_name}"
                ))

        if "dictionary_item_removed" in diff:
            for item in diff["dictionary_item_removed"]:
                changes.append(DriftChange(
                    change_type="removed",
                    path=f"components.schemas.{schema_name}.{item}",
                    severity="breaking",
                    description=f"Property removed from schema {schema_name}"
                ))

        if "values_changed" in diff:
            for path, change in diff["values_changed"].items():
                severity = "breaking" if "type" in path else "informational"
                changes.append(DriftChange(
                    change_type="modified",
                    path=f"components.schemas.{schema_name}.{path}",
                    severity=severity,
                    old_value=change.get("old_value"),
                    new_value=change.get("new_value"),
                    description=f"Property modified in schema {schema_name}"
                ))

        return changes

    def _detect_security_changes(self) -> List[DriftChange]:
        """Detect changes in security definitions"""
        changes = []

        baseline_security = self.baseline.get("components", {}).get("securitySchemes", {})
        current_security = self.current.get("components", {}).get("securitySchemes", {})

        baseline_names = set(baseline_security.keys())
        current_names = set(current_security.keys())

        # Removed security schemes (BREAKING)
        removed_schemes = baseline_names - current_names
        for scheme_name in removed_schemes:
            changes.append(DriftChange(
                change_type="removed",
                path=f"components.securitySchemes.{scheme_name}",
                severity="breaking",
                old_value=scheme_name,
                description=f"Security scheme removed: {scheme_name}"
            ))

        # Added security schemes (COMPATIBLE)
        added_schemes = current_names - baseline_names
        for scheme_name in added_schemes:
            changes.append(DriftChange(
                change_type="added",
                path=f"components.securitySchemes.{scheme_name}",
                severity="compatible",
                new_value=scheme_name,
                description=f"New security scheme added: {scheme_name}"
            ))

        return changes

    def _detect_server_changes(self) -> List[DriftChange]:
        """Detect changes in server definitions"""
        changes = []

        baseline_servers = self.baseline.get("servers", [])
        current_servers = self.current.get("servers", [])

        baseline_urls = {s.get("url") for s in baseline_servers}
        current_urls = {s.get("url") for s in current_servers}

        # Removed servers (INFORMATIONAL)
        removed_servers = baseline_urls - current_urls
        for url in removed_servers:
            if url:  # Skip None values
                changes.append(DriftChange(
                    change_type="removed",
                    path=f"servers",
                    severity="informational",
                    old_value=url,
                    description=f"Server URL removed: {url}"
                ))

        # Added servers (INFORMATIONAL)
        added_servers = current_urls - baseline_urls
        for url in added_servers:
            if url:  # Skip None values
                changes.append(DriftChange(
                    change_type="added",
                    path=f"servers",
                    severity="informational",
                    new_value=url,
                    description=f"New server URL added: {url}"
                ))

        return changes


def format_text_report(report: DriftReport) -> str:
    """Format drift report as human-readable text"""
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("OpenAPI Drift Detection Report")
    lines.append("=" * 80)
    lines.append(f"Baseline Version: {report.baseline_version}")
    lines.append(f"Current Version:  {report.current_version}")
    lines.append("")

    # Summary
    lines.append("Summary:")
    lines.append(f"  Total Changes: {len(report.changes)}")
    lines.append(f"  🚨 Breaking Changes:      {report.breaking_changes}")
    lines.append(f"  ✅ Compatible Changes:    {report.compatible_changes}")
    lines.append(f"  ℹ️  Informational Changes: {report.informational_changes}")
    lines.append("")

    if not report.has_drift:
        lines.append("✅ No drift detected - specifications are identical")
        return "\n".join(lines)

    # Group changes by severity
    breaking = [c for c in report.changes if c.severity == "breaking"]
    compatible = [c for c in report.changes if c.severity == "compatible"]
    informational = [c for c in report.changes if c.severity == "informational"]

    # Breaking changes
    if breaking:
        lines.append("🚨 Breaking Changes (Backwards Incompatible):")
        lines.append("-" * 80)
        for change in breaking:
            lines.append(f"  [{change.change_type.upper()}] {change.path}")
            lines.append(f"    {change.description}")
            if change.old_value:
                lines.append(f"    Old: {change.old_value}")
            if change.new_value:
                lines.append(f"    New: {change.new_value}")
            lines.append("")

    # Compatible changes
    if compatible:
        lines.append("✅ Compatible Changes (Backwards Compatible):")
        lines.append("-" * 80)
        for change in compatible:
            lines.append(f"  [{change.change_type.upper()}] {change.path}")
            lines.append(f"    {change.description}")
            lines.append("")

    # Informational changes
    if informational:
        lines.append("ℹ️  Informational Changes:")
        lines.append("-" * 80)
        for change in informational:
            lines.append(f"  [{change.change_type.upper()}] {change.path}")
            lines.append(f"    {change.description}")
            lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


def save_current_as_baseline(baseline_path: Path, current_path: Path):
    """Update baseline with current specification"""
    current_spec = json.loads(current_path.read_text())

    with open(baseline_path, 'w') as f:
        json.dump(current_spec, f, indent=2)

    print(f"✅ Updated baseline: {baseline_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Detect drift between OpenAPI specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare baseline and current
  python tools/check_openapi_drift.py --baseline api/baseline.json --current api/current.json

  # Output as JSON
  python tools/check_openapi_drift.py --baseline api/baseline.json --current api/current.json --format json

  # Update baseline (after reviewing changes)
  python tools/check_openapi_drift.py --baseline api/baseline.json --current api/current.json --autofix

  # CI Integration
  python tools/check_openapi_drift.py --baseline api/baseline.json --current api/current.json --fail-on-breaking
        """
    )

    parser.add_argument(
        "--baseline",
        required=True,
        help="Path to baseline OpenAPI specification"
    )

    parser.add_argument(
        "--current",
        required=True,
        help="Path to current OpenAPI specification"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "--autofix",
        action="store_true",
        help="Update baseline with current specification"
    )

    parser.add_argument(
        "--fail-on-breaking",
        action="store_true",
        help="Exit with code 1 if breaking changes detected (for CI)"
    )

    parser.add_argument(
        "--output",
        help="Output file (default: stdout)"
    )

    args = parser.parse_args()

    # Auto-fix mode
    if args.autofix:
        save_current_as_baseline(Path(args.baseline), Path(args.current))
        return 0

    # Detect drift
    detector = OpenAPIDriftDetector(args.baseline, args.current)
    report = detector.detect_drift()

    # Format output
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2)
    else:
        output = format_text_report(report)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"✅ Report written to: {args.output}")
    else:
        print(output)

    # Exit code
    if args.fail_on_breaking and report.breaking_changes > 0:
        print(f"\n❌ FAIL: {report.breaking_changes} breaking change(s) detected", file=sys.stderr)
        return 1

    if report.has_drift:
        print(f"\n⚠️  Drift detected: {len(report.changes)} change(s)")
        return 0 if report.breaking_changes == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
