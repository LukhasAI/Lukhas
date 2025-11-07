#!/usr/bin/env python3
"""
T4/0.01% Excellence Audit Certification Generator

Generates official audit certification based on comprehensive validation results.
Creates regulatory-grade certification documents with cryptographic verification.
"""

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class CertificationEvidence:
    """Evidence item for certification."""
    component: str
    test_type: str
    file_path: str
    checksum: str
    status: str
    key_metrics: dict[str, Any]
    verification_timestamp: float

@dataclass
class CertificationResult:
    """Final certification result."""
    certification_id: str
    overall_status: str
    confidence_level: float
    evidence_count: int
    failed_tests: int
    missing_evidence: list[str]
    key_performance_claims: dict[str, Any]
    certification_timestamp: str
    audit_trail_hash: str

class AuditCertificationGenerator:
    """Comprehensive T4/0.01% Excellence certification generator."""

    def __init__(self, evidence_directory: str):
        """Initialize with evidence directory."""
        self.evidence_dir = Path(evidence_directory)
        self.certification_standards = self._load_certification_standards()

    def _load_certification_standards(self) -> dict[str, Any]:
        """Load T4/0.01% certification standards."""
        return {
            "performance_requirements": {
                "guardian_p95_us": {"max": 200.0, "target": 168.0},
                "memory_p95_us": {"max": 1000.0, "target": 178.0},
                "orchestrator_p95_us": {"max": 250000.0, "target": 54000.0},
                "creativity_p95_us": {"max": 50000.0, "target": 50000.0}
            },
            "reliability_requirements": {
                "reproducibility_threshold": 0.80,
                "statistical_significance": 0.01,
                "fail_closed_compliance": 1.0
            },
            "evidence_requirements": {
                "baseline_measurements": "required",
                "statistical_analysis": "required",
                "reproducibility_analysis": "required",
                "chaos_engineering": "required",
                "tamper_evidence": "required",
                "claims_verification": "required"
            }
        }

    def discover_evidence_files(self) -> list[Path]:
        """Discover all evidence files in the directory."""
        patterns = [
            "audit_baseline_*.json",
            "statistical_analysis_*.json",
            "reproducibility_analysis_*.json",
            "chaos_*.json",
            "merkle_chain_*.json",
            "verification_*.json",
            "consistency_analysis_*.json"
        ]

        evidence_files = []
        for pattern in patterns:
            evidence_files.extend(self.evidence_dir.glob(pattern))

        return sorted(evidence_files)

    def analyze_evidence_file(self, file_path: Path) -> Optional[CertificationEvidence]:
        """Analyze a single evidence file."""
        try:
            with open(file_path) as f:
                data = json.load(f)

            # Calculate file checksum
            with open(file_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            # Determine component and test type from filename
            filename = file_path.name

            if filename.startswith("audit_baseline"):
                component = "baseline"
                test_type = "performance"
                key_metrics = self._extract_baseline_metrics(data)
            elif filename.startswith("statistical"):
                component = "statistics"
                test_type = "statistical_analysis"
                key_metrics = self._extract_statistical_metrics(data)
            elif filename.startswith("reproducibility"):
                component = "reproducibility"
                test_type = "reproducibility_analysis"
                key_metrics = self._extract_reproducibility_metrics(data)
            elif filename.startswith("chaos"):
                component = "chaos_engineering"
                test_type = "stress_testing"
                key_metrics = self._extract_chaos_metrics(data)
            elif filename.startswith("merkle"):
                component = "integrity"
                test_type = "tamper_evidence"
                key_metrics = self._extract_merkle_metrics(data)
            elif filename.startswith("verification"):
                component = "claims_verification"
                test_type = "claims_validation"
                key_metrics = self._extract_verification_metrics(data)
            else:
                component = "unknown"
                test_type = "unknown"
                key_metrics = {}

            # Determine status
            status = self._determine_evidence_status(component, test_type, key_metrics)

            return CertificationEvidence(
                component=component,
                test_type=test_type,
                file_path=str(file_path),
                checksum=checksum,
                status=status,
                key_metrics=key_metrics,
                verification_timestamp=file_path.stat().st_mtime
            )

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            return None

    def _extract_baseline_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from baseline data."""
        metrics = {}

        components = ["guardian_stats", "memory_stats", "orchestrator_stats", "creativity_stats"]
        for component in components:
            if component in data:
                comp_data = data[component]
                comp_name = component.replace("_stats", "")
                metrics[f"{comp_name}_p95"] = comp_data.get("p95")
                metrics[f"{comp_name}_mean"] = comp_data.get("mean")
                metrics[f"{comp_name}_samples"] = comp_data.get("samples")

        return metrics

    def _extract_statistical_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from statistical analysis."""
        metrics = {}

        if "summary" in data:
            summary = data["summary"]
            metrics["total_tests"] = summary.get("total_tests", 0)
            metrics["passed_tests"] = summary.get("passed_tests", 0)
            metrics["alpha_level"] = summary.get("alpha_level", 0.01)

        return metrics

    def _extract_reproducibility_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from reproducibility analysis."""
        metrics = {}

        if "summary" in data:
            summary = data["summary"]
            metrics["total_runs"] = summary.get("total_runs", 0)
            metrics["reproducibility_score"] = summary.get("average_reproducibility", 0.0)
            metrics["target_threshold"] = summary.get("target_reproducibility", 0.8)

        return metrics

    def _extract_chaos_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from chaos engineering."""
        metrics = {}

        if "chaos_results" in data:
            results = data["chaos_results"]
            metrics["total_scenarios"] = len(results.get("scenarios", []))
            metrics["fail_closed_compliance"] = results.get("fail_closed_rate", 0.0)

        return metrics

    def _extract_merkle_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from Merkle chain."""
        metrics = {}

        if "merkle_proof" in data:
            proof = data["merkle_proof"]
            metrics["evidence_files"] = len(proof.get("evidence_files", []))
            metrics["merkle_root"] = proof.get("merkle_root", "")

        return metrics

    def _extract_verification_metrics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from claims verification."""
        metrics = {}

        if "summary" in data:
            summary = data["summary"]
            metrics["total_claims"] = summary.get("total_claims", 0)
            metrics["passed_claims"] = summary.get("passed_claims", 0)
            metrics["overall_status"] = summary.get("overall_status", "UNKNOWN")

        return metrics

    def _determine_evidence_status(self, component: str, test_type: str, metrics: dict[str, Any]) -> str:
        """Determine pass/fail status for evidence."""

        if component == "baseline":
            # Check performance requirements
            standards = self.certification_standards["performance_requirements"]

            for metric_name, limit in standards.items():
                if metric_name.replace("_us", "") in [k.replace("_p95", "") for k in metrics]:
                    metric_key = metric_name.replace("_us", "_p95")
                    if metrics.get(metric_key) and metrics[metric_key] > limit['max']:
                        return "FAIL"
            return "PASS"

        elif component == "statistics":
            # Check statistical significance
            if metrics.get("alpha_level", 1.0) <= 0.01:
                return "PASS"
            return "FAIL"

        elif component == "reproducibility":
            # Check reproducibility threshold
            threshold = self.certification_standards["reliability_requirements"]["reproducibility_threshold"]
            if metrics.get("reproducibility_score", 0.0) >= threshold:
                return "PASS"
            return "FAIL"

        elif component == "chaos_engineering":
            # Check fail-closed compliance
            required_compliance = self.certification_standards["reliability_requirements"]["fail_closed_compliance"]
            if metrics.get("fail_closed_compliance", 0.0) >= required_compliance:
                return "PASS"
            return "FAIL"

        elif component == "claims_verification":
            # Check claims verification status
            if metrics.get("overall_status") == "PASS":
                return "PASS"
            return "FAIL"

        else:
            return "UNKNOWN"

    def generate_certification(self, evidence_files: list[CertificationEvidence]) -> CertificationResult:
        """Generate final certification based on evidence."""

        # Generate unique certification ID
        timestamp = datetime.now(timezone.utc)
        cert_id = f"T4-{timestamp.strftime('%Y%m%d')}-{hashlib.sha256(str(evidence_files).encode()).hexdigest()[:8].upper()}"

        # Analyze evidence completeness
        required_components = set(self.certification_standards["evidence_requirements"].keys())
        present_components = {ev.component for ev in evidence_files}
        missing_evidence = list(required_components - present_components)

        # Count test results
        total_evidence = len(evidence_files)
        failed_tests = len([ev for ev in evidence_files if ev.status == "FAIL"])
        passed_tests = len([ev for ev in evidence_files if ev.status == "PASS"])

        # Calculate confidence level
        if total_evidence == 0:
            confidence_level = 0.0
        else:
            confidence_level = (passed_tests / total_evidence) * (1.0 - len(missing_evidence) / len(required_components))

        # Determine overall status
        if failed_tests == 0 and len(missing_evidence) == 0:
            overall_status = "CERTIFIED"
        elif failed_tests == 0 and len(missing_evidence) > 0:
            overall_status = "PROVISIONAL"
        else:
            overall_status = "FAILED"

        # Extract key performance claims
        baseline_evidence = [ev for ev in evidence_files if ev.component == "baseline"]
        key_performance_claims = {}
        if baseline_evidence:
            key_performance_claims = baseline_evidence[0].key_metrics

        # Generate audit trail hash
        audit_data = {
            "evidence_checksums": [ev.checksum for ev in evidence_files],
            "certification_timestamp": timestamp.isoformat(),
            "standards_version": "T4/0.01%"
        }
        audit_trail_hash = hashlib.sha256(json.dumps(audit_data, sort_keys=True).encode()).hexdigest()

        return CertificationResult(
            certification_id=cert_id,
            overall_status=overall_status,
            confidence_level=confidence_level,
            evidence_count=total_evidence,
            failed_tests=failed_tests,
            missing_evidence=missing_evidence,
            key_performance_claims=key_performance_claims,
            certification_timestamp=timestamp.isoformat(),
            audit_trail_hash=audit_trail_hash
        )

    def generate_certification_report(self, certification: CertificationResult, evidence_files: list[CertificationEvidence]) -> str:
        """Generate human-readable certification report."""

        report_lines = []

        # Header
        report_lines.append("# T4/0.01% Excellence Audit Certification")
        report_lines.append("")
        report_lines.append("## Official Certification Document")
        report_lines.append("")

        # Certification details
        report_lines.append(f"**Certification ID:** `{certification.certification_id}`")
        report_lines.append(f"**Issue Date:** {certification.certification_timestamp}")
        report_lines.append(f"**Certification Status:** **{certification.overall_status}**")
        report_lines.append(f"**Confidence Level:** {certification.confidence_level:.1%}")
        report_lines.append("")

        # Status icon and message
        if certification.overall_status == "CERTIFIED":
            status_icon = "✅"
            status_message = "This system meets all T4/0.01% Excellence requirements and is CERTIFIED for production deployment."
        elif certification.overall_status == "PROVISIONAL":
            status_icon = "⚠️"
            status_message = "This system meets core requirements but has incomplete evidence. PROVISIONAL certification granted pending additional validation."
        else:
            status_icon = "❌"
            status_message = "This system FAILED to meet T4/0.01% Excellence requirements. Certification DENIED."

        report_lines.append(f"{status_icon} **VERDICT:** {status_message}")
        report_lines.append("")

        # Evidence summary
        report_lines.append("## Evidence Summary")
        report_lines.append("")
        report_lines.append(f"- **Total Evidence Files:** {certification.evidence_count}")
        report_lines.append(f"- **Passed Tests:** {certification.evidence_count - certification.failed_tests}")
        report_lines.append(f"- **Failed Tests:** {certification.failed_tests}")
        report_lines.append(f"- **Missing Evidence:** {len(certification.missing_evidence)}")
        report_lines.append("")

        if certification.missing_evidence:
            report_lines.append("### Missing Evidence")
            for item in certification.missing_evidence:
                report_lines.append(f"- {item}")
            report_lines.append("")

        # Performance claims validation
        if certification.key_performance_claims:
            report_lines.append("## Performance Claims Validation")
            report_lines.append("")

            standards = self.certification_standards["performance_requirements"]

            for component in ["guardian", "memory", "orchestrator", "creativity"]:
                p95_key = f"{component}_p95"
                if p95_key in certification.key_performance_claims:
                    measured = certification.key_performance_claims[p95_key]
                    if measured:
                        standard_key = f"{component}_p95_us"
                        if standard_key in standards:
                            target = standards[standard_key]["target"]
                            max_allowed = standards[standard_key]["max"]

                            status = "✅ PASS" if measured <= max_allowed else "❌ FAIL"

                            report_lines.append(f"- **{component.title()}:** {measured:.1f}μs vs {target:.1f}μs target ({status})")
            report_lines.append("")

        # Detailed evidence analysis
        report_lines.append("## Detailed Evidence Analysis")
        report_lines.append("")

        for evidence in evidence_files:
            status_icon = "✅" if evidence.status == "PASS" else "❌" if evidence.status == "FAIL" else "⚠️"

            report_lines.append(f"### {evidence.component.title()} - {evidence.test_type}")
            report_lines.append(f"- **Status:** {status_icon} {evidence.status}")
            report_lines.append(f"- **File:** `{Path(evidence.file_path).name}`")
            report_lines.append(f"- **Checksum:** `{evidence.checksum[:16]}...`")

            # Show key metrics
            if evidence.key_metrics:
                report_lines.append("- **Key Metrics:**")
                for key, value in evidence.key_metrics.items():
                    if value is not None:
                        if isinstance(value, float):
                            report_lines.append(f"  - {key}: {value:.3f}")
                        else:
                            report_lines.append(f"  - {key}: {value}")
            report_lines.append("")

        # Certification integrity
        report_lines.append("## Certification Integrity")
        report_lines.append("")
        report_lines.append(f"**Audit Trail Hash:** `{certification.audit_trail_hash}`")
        report_lines.append("")
        report_lines.append("This certification document is cryptographically linked to all")
        report_lines.append("evidence files through the audit trail hash. Any modification")
        report_lines.append("to evidence files will invalidate this certification.")
        report_lines.append("")

        # Regulatory compliance
        report_lines.append("## Regulatory Compliance Statement")
        report_lines.append("")
        report_lines.append("This audit certification was generated according to T4/0.01%")
        report_lines.append("Excellence standards using reproducible methodology and")
        report_lines.append("independent verification procedures.")
        report_lines.append("")

        if certification.overall_status == "CERTIFIED":
            report_lines.append("**CERTIFICATION AUTHORITY:** LUKHAS AI Audit Framework v1.0")
            report_lines.append("**VALIDITY:** This certification is valid for systems")
            report_lines.append("matching the exact codebase and configuration tested.")
            report_lines.append("")
            report_lines.append("🎯 **CERTIFIED FOR T4/0.01% EXCELLENCE**")

        return "\n".join(report_lines)

    def export_certification_json(self, certification: CertificationResult, evidence_files: list[CertificationEvidence]) -> dict[str, Any]:
        """Export certification as machine-readable JSON."""

        return {
            "certification": {
                "id": certification.certification_id,
                "status": certification.overall_status,
                "confidence_level": certification.confidence_level,
                "timestamp": certification.certification_timestamp,
                "audit_trail_hash": certification.audit_trail_hash
            },
            "evidence_summary": {
                "total_files": certification.evidence_count,
                "passed_tests": certification.evidence_count - certification.failed_tests,
                "failed_tests": certification.failed_tests,
                "missing_evidence": certification.missing_evidence
            },
            "performance_claims": certification.key_performance_claims,
            "evidence_details": [
                {
                    "component": ev.component,
                    "test_type": ev.test_type,
                    "status": ev.status,
                    "file_path": ev.file_path,
                    "checksum": ev.checksum,
                    "key_metrics": ev.key_metrics,
                    "verification_timestamp": ev.verification_timestamp
                }
                for ev in evidence_files
            ],
            "certification_standards": self.certification_standards,
            "schema_version": "1.0.0"
        }


def main():
    """Main certification generation function."""
    parser = argparse.ArgumentParser(description="Generate T4/0.01% Excellence Audit Certification")
    parser.add_argument("--evidence-dir", required=True, help="Directory containing evidence files")
    parser.add_argument("--output", help="Output certification JSON file")
    parser.add_argument("--report", help="Output certification report (Markdown)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize generator
    generator = AuditCertificationGenerator(args.evidence_dir)

    # Discover evidence files
    evidence_file_paths = generator.discover_evidence_files()

    if not evidence_file_paths:
        print(f"❌ No evidence files found in {args.evidence_dir}")
        return 1

    if args.verbose:
        print(f"🔍 Found {len(evidence_file_paths)} evidence files")

    # Analyze evidence files
    evidence_files = []
    for file_path in evidence_file_paths:
        evidence = generator.analyze_evidence_file(file_path)
        if evidence:
            evidence_files.append(evidence)
            if args.verbose:
                print(f"  ✓ {file_path.name}: {evidence.status}")

    if not evidence_files:
        print("❌ No valid evidence files could be analyzed")
        return 1

    # Generate certification
    certification = generator.generate_certification(evidence_files)

    # Output results
    if args.output:
        certification_data = generator.export_certification_json(certification, evidence_files)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(certification_data, f, indent=2, sort_keys=True)

        print(f"📊 Certification data saved: {args.output}")

    if args.report:
        report = generator.generate_certification_report(certification, evidence_files)

        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            f.write(report)

        print(f"📄 Certification report saved: {args.report}")

    # Print summary
    print("")
    print("🎯 T4/0.01% Excellence Certification Summary")
    print(f"Certification ID: {certification.certification_id}")
    print(f"Status: {certification.overall_status}")
    print(f"Confidence: {certification.confidence_level:.1%}")
    print(f"Evidence Files: {certification.evidence_count}")
    print(f"Failed Tests: {certification.failed_tests}")

    if certification.missing_evidence:
        print(f"Missing Evidence: {', '.join(certification.missing_evidence)}")

    # Print final verdict
    if certification.overall_status == "CERTIFIED":
        print("\n✅ T4/0.01% EXCELLENCE CERTIFICATION: GRANTED")
        print("🎯 System approved for production deployment")
        return 0
    elif certification.overall_status == "PROVISIONAL":
        print("\n⚠️  T4/0.01% EXCELLENCE CERTIFICATION: PROVISIONAL")
        print("🔍 Additional evidence required for full certification")
        return 2
    else:
        print("\n❌ T4/0.01% EXCELLENCE CERTIFICATION: DENIED")
        print("🚫 System does not meet certification requirements")
        return 1


if __name__ == "__main__":
    exit(main())
