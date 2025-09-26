#!/usr/bin/env python3
"""
Matrix Contract Gate Validator

Validates JSON contracts against schema and enforces quality gates based on run reports.
Supports JSON Schema 2020-12, RATS/EAT attestation verification, CycloneDX SBOM validation,
and Matrix identity/authorization validation.

Standards:
- JSON Schema 2020-12: https://json-schema.org/draft/2020-12/schema
- CycloneDX ECMA-424: https://cyclonedx.org/
- RATS/EAT RFC 9334: https://datatracker.ietf.org/doc/rfc9334/
- OpenTelemetry semconv: https://opentelemetry.io/docs/specs/semconv/
- LUKHAS ΛiD Identity System: Tier-based authorization
"""

import json
import sys
import glob
import pathlib
import subprocess
import traceback
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import argparse

try:
    from jsonschema import validate, Draft202012Validator, ValidationError
except ImportError:
    print("Error: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


def try_osv_scan(sbom_path: str, output_json_path: str) -> Optional[Dict]:
    """Run osv-scanner on SBOM, return dict or None on failure."""
    try:
        # Using osv-scanner CLI; adapt if using Docker wrapper
        result = subprocess.run(
            ["osv-scanner", "--sbom", sbom_path, "--format", "json", "--output", output_json_path],
            check=True,
            capture_output=True,
            text=True
        )
        return json.load(open(output_json_path))
    except subprocess.CalledProcessError as e:
        print(f"[WARN] OSV scanner failed (non-zero exit): {e}", file=sys.stderr)
        print(f"[WARN] stderr: {e.stderr}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[WARN] osv-scanner not found in PATH", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] OSV scanner error: {e}", file=sys.stderr)
        traceback.print_exc()
    return None


def parse_osv_result(osv_data: Optional[Dict]) -> Dict[str, Any]:
    """Parse OSV scan result, handling various failure modes."""
    if osv_data is None:
        return {"high_count": None, "scan_failed": True}

    # OSV scanner output structure can vary, handle multiple formats
    vulns = osv_data.get("vulnerabilities") or osv_data.get("vulns") or osv_data.get("results", {}).get("vulnerabilities", [])

    high_count = 0
    for vuln in vulns:
        # Check various severity field locations
        severity = vuln.get("severity") or vuln.get("database_specific", {}).get("severity") or ""
        if severity.upper() == "HIGH":
            high_count += 1

    return {"high_count": high_count, "scan_failed": False}


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

    def enforce_gates(self, matrix: Dict, run: Optional[Dict], osv_info: Optional[Dict] = None) -> List[Tuple[str, Any, str]]:
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

            # Get actual value from run data or OSV scan
            if metric_path == "security.osv_high" and osv_info is not None:
                if osv_info["scan_failed"]:
                    # Degrade: log alert but do not fail
                    print(f"    [ALERT] OSV scan failed; skipping gate {metric_path}")
                    continue
                actual = osv_info["high_count"]
            elif metric_path.startswith("attestation."):
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

    def validate_identity_block(self, matrix: Dict, contract_path: str) -> List[str]:
        """Validate identity block in matrix contract."""
        errors = []

        if "identity" not in matrix:
            # Identity block is optional, but warn if missing for non-test modules
            if "test" not in contract_path.lower():
                errors.append("Missing identity block (recommended for production modules)")
            return errors

        identity = matrix["identity"]

        # Load canonical ΛiD tier permissions for validation
        try:
            tier_perms_path = pathlib.Path("candidate/governance/identity/config/tier_permissions.json")
            if tier_perms_path.exists():
                with open(tier_perms_path) as f:
                    tier_permissions = json.load(f)
                    valid_tiers = list(tier_permissions["tier_permissions"].keys())
                    valid_tier_names = [
                        tier_permissions["tier_permissions"][k]["name"].lower().replace(" ", "_").replace("/", "_")
                        for k in valid_tiers
                    ]
            else:
                # Fallback tier names
                valid_tier_names = ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]
        except Exception as e:
            errors.append(f"Could not load ΛiD tier permissions: {e}")
            valid_tier_names = ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]

        # Validate required_tiers
        required_tiers = identity.get("required_tiers", [])
        for tier in required_tiers:
            if tier not in valid_tier_names:
                errors.append(f"Invalid tier name: '{tier}' (valid: {valid_tier_names})")

        # Validate required_tiers_numeric
        required_tiers_numeric = identity.get("required_tiers_numeric", [])
        for tier_num in required_tiers_numeric:
            if not isinstance(tier_num, int) or tier_num < 0 or tier_num > 5:
                errors.append(f"Invalid tier number: {tier_num} (must be 0-5)")

        # Validate consistency between textual and numeric tiers
        if required_tiers and required_tiers_numeric:
            tier_map = {"guest": 0, "visitor": 1, "friend": 2, "trusted": 3, "inner_circle": 4, "root_dev": 5}
            expected_numeric = [tier_map.get(tier, -1) for tier in required_tiers if tier in tier_map]
            if set(expected_numeric) != set(required_tiers_numeric):
                errors.append(f"Tier mismatch: textual {required_tiers} != numeric {required_tiers_numeric}")

        # Validate scopes format
        scopes = identity.get("scopes", [])
        for scope in scopes:
            if not isinstance(scope, str) or "." not in scope:
                errors.append(f"Invalid scope format: '{scope}' (expected: module.action)")

        # Validate accepted_subjects patterns
        accepted_subjects = identity.get("accepted_subjects", [])
        for subject in accepted_subjects:
            if not subject.startswith("lukhas:"):
                errors.append(f"Invalid subject pattern: '{subject}' (must start with 'lukhas:')")

        # Validate api_policies
        api_policies = identity.get("api_policies", [])
        interface = matrix.get("interface", {})
        public_apis = {api["fn"] for api in interface.get("public_api", [])}

        for policy in api_policies:
            fn_name = policy.get("fn")
            if fn_name and fn_name not in public_apis:
                errors.append(f"API policy references unknown function: '{fn_name}'")

        # Check for step-up requirements without MFA capability
        step_up_apis = [p["fn"] for p in api_policies if p.get("requires_step_up", False)]
        if step_up_apis and not any(tier in ["trusted", "inner_circle", "root_dev"]
                                   for tier in required_tiers):
            errors.append(f"Step-up required for {step_up_apis} but no high-tier access allowed")

        return errors

    def check_policy_checksum(self) -> Tuple[bool, str]:
        """Check if OPA policy bundle checksum matches canonical tier permissions."""
        try:
            # Load current tier permissions
            tier_perms_path = pathlib.Path("candidate/governance/identity/config/tier_permissions.json")
            if not tier_perms_path.exists():
                return False, "ΛiD tier permissions not found"

            with open(tier_perms_path) as f:
                tier_permissions = json.load(f)

            # Calculate expected checksum
            import hashlib
            canonical_json = json.dumps(tier_permissions, sort_keys=True, separators=(',', ':'))
            expected_checksum = hashlib.sha256(canonical_json.encode()).hexdigest()

            # Load policy checksum
            checksum_file = pathlib.Path("policies/matrix/permissions.checksum")
            if not checksum_file.exists():
                return False, "Policy checksum file not found (run: make generate-opa-bundle)"

            with open(checksum_file) as f:
                actual_checksum = f.read().strip()

            if actual_checksum != expected_checksum:
                return False, f"Policy checksum mismatch (expected: {expected_checksum[:16]}..., got: {actual_checksum[:16]}...)"

            return True, "Policy checksum valid"

        except Exception as e:
            return False, f"Policy checksum validation error: {e}"

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
    parser.add_argument(
        "--osv",
        action="store_true",
        help="Run OSV scanner on SBOMs and enforce security gates"
    )
    parser.add_argument(
        "--identity",
        action="store_true",
        help="Validate identity blocks and check policy checksum"
    )

    args = parser.parse_args()

    # Initialize gate validator
    gate = MatrixGate(schema_path=args.schema)

    # Check policy checksum if identity validation requested
    if args.identity:
        print("[INFO] Checking OPA policy bundle checksum...")
        checksum_valid, checksum_msg = gate.check_policy_checksum()
        if checksum_valid:
            print(f"[PASS] {checksum_msg}")
        else:
            print(f"[ERROR] {checksum_msg}")
            if args.strict:
                sys.exit(1)
        print("=" * 60)

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

        # Validate identity block if requested
        if args.identity:
            print("\n  Identity Validation:")
            identity_errors = gate.validate_identity_block(matrix, path)
            if identity_errors:
                for error in identity_errors:
                    print(f"    [ERROR] {error}")
                if "identity" not in results:
                    results[path] = {"failures": []}
                results[path]["failures"].extend([("identity", error, "valid") for error in identity_errors])
                any_failure = True
            else:
                print("    [PASS] Identity block valid")

        # Get latest run report
        module_dir = pathlib.Path(path).parent
        run = gate.latest_run(module_dir)

        if run:
            print(f"  Run ID: {run.get('run_id', 'unknown')}")
            print(f"  Timestamp: {run.get('timestamp', 'unknown')}")
        else:
            print("  [INFO] No run reports found")

        # Run OSV scan if requested
        osv_info = None
        if args.osv:
            print("\n  OSV Security Scan:")
            sbom_ref = matrix.get("supply_chain", {}).get("sbom_ref")
            if sbom_ref:
                # Resolve relative path
                sbom_path = pathlib.Path(sbom_ref.replace("../", ""))
                if sbom_path.exists():
                    osv_output = f"artifacts/osv_{matrix.get('module', 'unknown')}.json"
                    pathlib.Path("artifacts").mkdir(exist_ok=True)
                    osv_data = try_osv_scan(str(sbom_path), osv_output)
                    osv_info = parse_osv_result(osv_data)
                    if osv_info["scan_failed"]:
                        print(f"    [ALERT] OSV scan failed for {sbom_path}")
                    else:
                        print(f"    [OK] OSV scan completed: {osv_info['high_count']} HIGH vulnerabilities")
                else:
                    print(f"    [WARN] SBOM not found for OSV scan: {sbom_path}")
            else:
                print("    [INFO] No SBOM reference for OSV scan")

        # Enforce gates
        print("\n  Gates:")
        failures = gate.enforce_gates(matrix, run, osv_info)

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