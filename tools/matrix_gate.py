#!/usr/bin/env python3
"""
Matrix Contract Gate Validator

Validates JSON contracts against schema and enforces quality gates based on run reports.
Supports JSON Schema 2020-12, RATS/EAT attestation verification, and CycloneDX SBOM validation.

Standards:
- JSON Schema 2020-12: https://json-schema.org/draft/2020-12/schema
- CycloneDX ECMA-424: https://cyclonedx.org/
- RATS/EAT RFC 9334: https://datatracker.ietf.org/doc/rfc9334/
- OpenTelemetry semconv: https://opentelemetry.io/docs/specs/semconv/
"""

import json
import sys
import glob
import pathlib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import argparse

try:
    from jsonschema import validate, Draft202012Validator, ValidationError
except ImportError:
    print("Error: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


class MatrixGate:
    """Matrix contract gate enforcer with JSON Schema 2020-12 validation."""

    def __init__(self, schema_path: str = "schemas/matrix.schema.json"):
        """Initialize with schema path."""
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft202012Validator(self.schema)

    def _load_schema(self) -> Dict:
        """Load JSON Schema 2020-12 schema."""
        try:
            with open(self.schema_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Schema not found: {self.schema_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in schema: {e}", file=sys.stderr)
            sys.exit(1)

    def load_matrix(self, path: str) -> Optional[Dict]:
        """Load and validate matrix contract."""
        try:
            with open(path) as f:
                data = json.load(f)

            # Validate against schema
            self.validator.validate(data)
            return data
        except FileNotFoundError:
            print(f"[WARN] Matrix contract not found: {path}")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in {path}: {e}")
            return None
        except ValidationError as e:
            print(f"[ERROR] Schema validation failed for {path}:")
            print(f"  Path: {' -> '.join(str(p) for p in e.path)}")
            print(f"  Message: {e.message}")
            return None

    def latest_run(self, module_path: pathlib.Path) -> Optional[Dict]:
        """Get latest run report for a module."""
        runs_dir = module_path / "runs"
        if not runs_dir.exists():
            return None

        run_files = sorted(runs_dir.glob("*.json"))
        if not run_files:
            return None

        try:
            with open(run_files[-1]) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] Could not load run report {run_files[-1]}: {e}")
            return None

    def enforce_gates(self, matrix: Dict, run: Optional[Dict]) -> List[Tuple[str, Any, str]]:
        """
        Enforce gates from matrix contract against run metrics.

        Returns list of (metric_name, actual_value, expected_condition) for failures.
        """
        if not run:
            # If no run data, can't validate runtime gates
            print("  [INFO] No run data available for gate validation")
            return []

        failures = []
        metrics = run.get("metrics", {})
        attestation = run.get("attestation", {})

        for gate in matrix.get("gates", []):
            metric_path = gate["metric"]
            op = gate["op"]
            expected = gate["value"]
            desc = gate.get("desc", metric_path)

            # Get actual value from run data
            if metric_path.startswith("attestation."):
                key = metric_path.split(".", 1)[1]
                actual = attestation.get(key)
            else:
                actual = metrics.get(metric_path)

            # Check gate condition
            passed = self._check_condition(actual, op, expected)

            if not passed:
                failures.append((metric_path, actual, f"{op} {expected}"))
                print(f"    [FAIL] {desc}: got {actual}, expected {op} {expected}")
            else:
                print(f"    [PASS] {desc}: {actual} {op} {expected}")

        return failures

    def _check_condition(self, actual: Any, op: str, expected: Any) -> bool:
        """Check gate condition."""
        if actual is None:
            return False

        ops = {
            "<=": lambda a, e: a <= e,
            "<": lambda a, e: a < e,
            ">=": lambda a, e: a >= e,
            ">": lambda a, e: a > e,
            "==": lambda a, e: a == e,
            "!=": lambda a, e: a != e,
        }

        if op not in ops:
            print(f"[WARN] Unknown operator: {op}")
            return False

        try:
            return ops[op](actual, expected)
        except (TypeError, ValueError) as e:
            print(f"[WARN] Could not compare {actual} {op} {expected}: {e}")
            return False

    def verify_sbom(self, matrix: Dict) -> bool:
        """Verify SBOM file exists and is valid CycloneDX."""
        sbom_ref = matrix.get("supply_chain", {}).get("sbom_ref")
        if not sbom_ref:
            print("  [INFO] No SBOM reference in contract")
            return True

        # Resolve relative path from matrix location
        sbom_path = pathlib.Path(sbom_ref)
        if not sbom_path.is_absolute():
            # Assume relative to project root
            sbom_path = pathlib.Path(sbom_ref.replace("../", ""))

        if not sbom_path.exists():
            print(f"  [WARN] SBOM not found: {sbom_path}")
            return False

        # Basic CycloneDX validation (could use cyclonedx-cli if available)
        try:
            with open(sbom_path) as f:
                sbom = json.load(f)

            # Check basic CycloneDX structure
            if "bomFormat" not in sbom or sbom["bomFormat"] != "CycloneDX":
                print(f"  [ERROR] Invalid SBOM format in {sbom_path}")
                return False

            print(f"  [OK] SBOM valid: {sbom_path}")
            return True

        except (json.JSONDecodeError, IOError) as e:
            print(f"  [ERROR] Could not load SBOM {sbom_path}: {e}")
            return False

    def verify_attestation(self, run: Optional[Dict]) -> bool:
        """Verify RATS/EAT attestation if present."""
        if not run:
            return True

        attestation = run.get("attestation", {})
        if not attestation:
            return True

        # Check RATS verification result
        if "rats_verified" in attestation:
            verified = attestation["rats_verified"]
            if verified != 1:
                print(f"  [ERROR] RATS attestation not verified: {verified}")
                return False
            print("  [OK] RATS attestation verified")

        # Check TEE report if present
        if "tee_report" in attestation:
            tee = attestation["tee_report"]
            if tee.get("type") == "amd-sev-snp":
                if "measurement" in tee:
                    print(f"  [OK] SEV-SNP measurement: {tee['measurement'][:16]}...")

        return True

    def summarize(self, results: Dict[str, Dict]) -> None:
        """Print summary of all gate results."""
        total = len(results)
        passed = sum(1 for r in results.values() if not r["failures"])
        failed = total - passed

        print("\n" + "=" * 60)
        print("MATRIX CONTRACT VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total modules:    {total}")
        print(f"Passed:          {passed}")
        print(f"Failed:          {failed}")

        if failed > 0:
            print("\nFailed modules:")
            for path, result in results.items():
                if result["failures"]:
                    print(f"  - {path}:")
                    for metric, actual, expected in result["failures"]:
                        print(f"      {metric}: {actual} (expected {expected})")

        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Matrix Contract Gate Validator")
    parser.add_argument(
        "--pattern",
        default="**/matrix_*.json",
        help="Glob pattern for finding matrix contracts (default: **/matrix_*.json)"
    )
    parser.add_argument(
        "--schema",
        default="schemas/matrix.schema.json",
        help="Path to JSON Schema (default: schemas/matrix.schema.json)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error on any gate failure"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Initialize gate validator
    gate = MatrixGate(schema_path=args.schema)

    # Find all matrix contracts
    paths = glob.glob(args.pattern, recursive=True)
    if not paths:
        print(f"[WARN] No matrix contracts found matching: {args.pattern}")
        sys.exit(0)

    print(f"[INFO] Found {len(paths)} matrix contract(s)")
    print("=" * 60)

    # Process each contract
    results = {}
    any_failure = False

    for path in sorted(paths):
        print(f"\n[MATRIX] {path}")
        print("-" * 40)

        # Load and validate contract
        matrix = gate.load_matrix(path)
        if not matrix:
            results[path] = {"failures": [("schema", "invalid", "valid")]}
            any_failure = True
            continue

        print(f"  Module: {matrix.get('module', 'unknown')}")
        print(f"  Version: {matrix.get('schema_version', 'unknown')}")

        # Get latest run report
        module_dir = pathlib.Path(path).parent
        run = gate.latest_run(module_dir)

        if run:
            print(f"  Run ID: {run.get('run_id', 'unknown')}")
            print(f"  Timestamp: {run.get('timestamp', 'unknown')}")
        else:
            print("  [INFO] No run reports found")

        # Enforce gates
        print("\n  Gates:")
        failures = gate.enforce_gates(matrix, run)

        # Verify SBOM
        print("\n  Supply Chain:")
        sbom_valid = gate.verify_sbom(matrix)
        if not sbom_valid:
            failures.append(("sbom", "missing/invalid", "valid"))

        # Verify attestation
        print("\n  Attestation:")
        attestation_valid = gate.verify_attestation(run)
        if not attestation_valid:
            failures.append(("attestation", "failed", "verified"))

        # Record results
        results[path] = {"failures": failures}
        if failures:
            any_failure = True
            print(f"\n  [RESULT] FAILED ({len(failures)} issues)")
        else:
            print("\n  [RESULT] PASSED")

    # Print summary
    gate.summarize(results)

    # Exit code
    if args.strict and any_failure:
        print("\n[EXIT] Validation failed in strict mode")
        sys.exit(1)
    elif any_failure:
        print("\n[EXIT] Validation completed with failures")
        sys.exit(0)
    else:
        print("\n[EXIT] All validations passed")
        sys.exit(0)


if __name__ == "__main__":
    main()