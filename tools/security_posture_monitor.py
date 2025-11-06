#!/usr/bin/env python3
"""
Security Posture Monitor for Matrix Tracks

Monitors security telemetry across all Matrix Tracks to provide comprehensive
security posture reporting and alerting. Tracks vulnerability exposure,
attestation health, and supply chain integrity.
"""

import datetime
import glob
import json
import sys
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _coerce_str(value: Any) -> str:
    """Convert ``value`` to a trimmed string, returning an empty string for falsy values."""

    if value is None:
        return ''
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _has_items(value: Any) -> bool:
    """Return ``True`` when ``value`` represents a non-empty collection."""

    if value is None:
        return False
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return bool(value)


def _is_policy_configured(policy: Any) -> bool:
    """Return ``True`` if the attestation policy is configured with real data."""

    if isinstance(policy, dict):
        if not policy:
            return False
        version = _coerce_str(policy.get('version'))
        identifier = _coerce_str(policy.get('id'))
        return not (version.lower() in {'', 'pending', 'tbd'} and identifier.lower() in {'', 'pending', 'tbd'})

    if isinstance(policy, str):
        normalized = policy.strip().lower()
        return normalized not in {'', 'pending', 'todo', 'tbd'}

    return bool(policy)


def _policy_version(policy: Any) -> str:
    """Best-effort extraction of a verifier policy version string."""

    if isinstance(policy, dict):
        version = _coerce_str(policy.get('version'))
        if version:
            return version
        identifier = _coerce_str(policy.get('id'))
        if identifier:
            return identifier
        ref = _coerce_str(policy.get('ref'))
        if ref:
            return ref
        return ''

    if isinstance(policy, str):
        return policy.strip()

    return ''


def _is_telemetry_feature_enabled(config: Any) -> bool:
    """Interpret telemetry configuration blocks of varying shapes."""

    if isinstance(config, bool):
        return config

    if isinstance(config, dict):
        if 'enabled' in config:
            return bool(config.get('enabled'))
        if 'active' in config:
            return bool(config.get('active'))
        return bool(config)

    if isinstance(config, (list, tuple, set)):
        return bool(config)

    if isinstance(config, str):
        normalized = config.strip().lower()
        return normalized not in {'', 'disabled', 'none', 'off'}

    return bool(config)


def _logs_are_structured(logs_config: Any) -> bool:
    """Return ``True`` if structured logging appears to be enabled."""

    if isinstance(logs_config, dict):
        if 'structured' in logs_config:
            return bool(logs_config.get('structured'))
        if 'enabled' in logs_config:
            return bool(logs_config.get('enabled'))
        return bool(logs_config)

    if isinstance(logs_config, bool):
        return logs_config

    if isinstance(logs_config, str):
        normalized = logs_config.strip().lower()
        return normalized not in {'', 'disabled', 'none', 'off'}

    return bool(logs_config)


def _estimate_telemetry_coverage(
    otel_instrumented: bool,
    metrics_exported: bool,
    traces_exported: bool,
    logs_structured: bool,
) -> float:
    """Heuristically estimate coverage when explicit metrics are missing."""

    score = 0.0
    if otel_instrumented:
        score += 40.0
    if metrics_exported:
        score += 25.0
    if traces_exported:
        score += 25.0
    if logs_structured:
        score += 10.0

    return score


@dataclass
class SecurityAlert:
    """Represents a security alert with severity and context."""
    severity: str  # critical, high, medium, low
    category: str  # vulnerability, attestation, supply_chain, telemetry
    message: str
    affected_modules: List[str]
    remediation: str
    timestamp: str


class SecurityPostureMonitor:
    """Monitors and reports on Matrix Tracks security posture."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.alerts: List[SecurityAlert] = []
        self.metrics = {
            'vulnerability_exposure': 0.0,
            'attestation_coverage': 0.0,
            'supply_chain_integrity': 0.0,
            'telemetry_compliance': 0.0,
            'overall_posture_score': 0.0
        }
        self.overlays = self._load_overlay_data()

    def _load_overlay_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Load optional overlay data for SBOM, attestation, and telemetry."""

        overlays: Dict[str, Dict[str, Dict[str, Any]]] = {
            'sboms': {},
            'attestations': {},
            'telemetry': {},
        }

        overlay_paths = {
            'sboms': Path('security/sboms/index.json'),
            'attestations': Path('security/attestations/index.json'),
            'telemetry': Path('security/telemetry/index.json'),
        }

        for key, path in overlay_paths.items():
            try:
                with path.open('r', encoding='utf-8') as handle:
                    data = json.load(handle)
                modules = data.get('modules', {})
                if isinstance(modules, dict):
                    overlays[key] = modules
                else:
                    self.log(f"Overlay file {path} missing 'modules' mapping")
            except FileNotFoundError:
                self.log(f"Overlay file not found: {path}")
            except Exception as exc:  # pragma: no cover - defensive logging
                self.log(f"Failed to load {key} overlay from {path}: {exc}")

        return overlays

    def log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"🔍 {message}")

    def collect_security_telemetry(self, pattern: str = "**/matrix_*.json") -> Dict[str, Any]:
        """Collect security telemetry from all Matrix Track contracts."""
        self.log("Collecting security telemetry from Matrix Track contracts...")

        contracts = glob.glob(pattern, recursive=True)
        telemetry = {
            'total_modules': len(contracts),
            'vulnerability_findings': [],
            'attestation_status': {},
            'supply_chain_refs': {},
            'telemetry_coverage': {},
            'timestamp': datetime.datetime.now(timezone.utc).isoformat()
        }

        for contract_path in contracts:
            try:
                with open(contract_path) as f:
                    contract = json.load(f)

                module_name = contract.get('module', Path(contract_path).stem)

                # Collect vulnerability data
                vuln_data = self._extract_vulnerability_data(contract, module_name)
                if vuln_data:
                    telemetry['vulnerability_findings'].extend(vuln_data)

                # Collect attestation status
                attestation_status = self._extract_attestation_status(contract, module_name)
                telemetry['attestation_status'][module_name] = attestation_status

                # Collect supply chain references
                supply_chain = self._extract_supply_chain_data(contract, module_name)
                telemetry['supply_chain_refs'][module_name] = supply_chain

                # Collect telemetry coverage
                telemetry_coverage = self._extract_telemetry_coverage(contract, module_name)
                telemetry['telemetry_coverage'][module_name] = telemetry_coverage

            except Exception as e:
                self.log(f"Error processing {contract_path}: {e}")
                continue

        return telemetry

    def _extract_vulnerability_data(self, contract: Dict, module: str) -> List[Dict]:
        """Extract vulnerability findings from contract gates."""
        findings = []

        gates = contract.get('gates', [])
        for gate in gates:
            if gate.get('type') == 'osv_vulnerability_scan':
                results = gate.get('results', {})
                if 'vulnerabilities' in results:
                    for vuln in results['vulnerabilities']:
                        findings.append({
                            'module': module,
                            'vulnerability_id': vuln.get('id', 'unknown'),
                            'severity': vuln.get('severity', 'unknown'),
                            'package': vuln.get('package', {}).get('name', 'unknown'),
                            'fixed_version': vuln.get('fixed', ''),
                            'introduced': vuln.get('introduced', ''),
                            'timestamp': datetime.datetime.now(timezone.utc).isoformat()
                        })

        return findings

    def _extract_attestation_status(self, contract: Dict, module: str) -> Dict:
        """Extract attestation health status."""
        attestation = contract.get('attestation') or {}
        if not isinstance(attestation, dict):
            attestation = {}

        rats_data = attestation.get('rats') or {}
        if not isinstance(rats_data, dict):
            rats_data = {}

        verifier_policy = rats_data.get('verifier_policy')
        verifier_configured = _is_policy_configured(verifier_policy)
        verifier_version = _policy_version(verifier_policy)

        overlay_entry = self.overlays.get('attestations', {}).get(module, {})
        overlay_policy = overlay_entry.get('verifier_policy') if isinstance(overlay_entry, dict) else None

        if overlay_policy and not verifier_configured:
            verifier_configured = _is_policy_configured(overlay_policy)
        overlay_version = _policy_version(overlay_policy) if overlay_policy else ''
        if overlay_version:
            verifier_version = overlay_version

        combined_rats = dict(rats_data)

        if isinstance(overlay_entry, dict):
            overlay_jwt = overlay_entry.get('evidence_jwt')
            if overlay_jwt:
                combined_rats['evidence_jwt'] = overlay_jwt

            overlay_timestamp = overlay_entry.get('timestamp')
            if overlay_timestamp:
                combined_rats['timestamp'] = overlay_timestamp

        evidence = combined_rats.get('evidence_jwt')
        evidence_collected = bool(evidence and evidence != 'pending')

        return {
            'verifier_configured': verifier_configured or bool(overlay_policy),
            'evidence_collected': evidence_collected,
            'attestation_valid': self._validate_attestation(combined_rats),
            'last_attestation': _coerce_str(combined_rats.get('timestamp', '')),
            'verifier_version': verifier_version,
        }

    def _extract_supply_chain_data(self, contract: Dict, module: str) -> Dict:
        """Extract supply chain integrity data."""
        supply_chain = contract.get('supply_chain') or {}
        if not isinstance(supply_chain, dict):
            supply_chain = {}

        causal_provenance = contract.get('causal_provenance') or {}
        if not isinstance(causal_provenance, dict):
            causal_provenance = {}

        overlay_entry = self.overlays.get('sboms', {}).get(module, {})
        if not isinstance(overlay_entry, dict):
            overlay_entry = {}

        sbom_ref = _coerce_str(supply_chain.get('sbom_ref', ''))
        overlay_ref = _coerce_str(overlay_entry.get('sbom_path', ''))
        if not sbom_ref and overlay_ref:
            sbom_ref = overlay_ref

        sbom_format = _coerce_str(supply_chain.get('format', '')) or _coerce_str(overlay_entry.get('format', ''))

        provenance_cid = _coerce_str(causal_provenance.get('ipld_root_cid', ''))
        overlay_cid = _coerce_str(overlay_entry.get('provenance_cid', ''))
        if overlay_cid and (not provenance_cid or provenance_cid == 'bafybeipending'):
            provenance_cid = overlay_cid

        reproducible = bool(supply_chain.get('reproducible')) or bool(overlay_entry.get('reproducible_build'))

        return {
            'sbom_present': bool(sbom_ref),
            'sbom_ref': sbom_ref,
            'sbom_format': sbom_format,
            'provenance_available': bool(provenance_cid and provenance_cid != 'bafybeipending'),
            'provenance_cid': provenance_cid,
            'build_reproducible': reproducible,
        }

    def _extract_telemetry_coverage(self, contract: Dict, module: str) -> Dict:
        """Extract telemetry and observability coverage."""
        telemetry = contract.get('telemetry') or {}
        if not isinstance(telemetry, dict):
            telemetry = {}

        spans = telemetry.get('spans')
        otel_instrumented = bool(telemetry.get('opentelemetry')) or _has_items(spans)

        metrics_data = telemetry.get('metrics')
        metrics_exported = _is_telemetry_feature_enabled(metrics_data)

        traces_data = telemetry.get('traces')
        if traces_data is None:
            traces_exported = _has_items(spans)
        else:
            traces_exported = _is_telemetry_feature_enabled(traces_data)

        logs_data = telemetry.get('logs')
        logs_structured = _logs_are_structured(logs_data)

        semconv_version = (
            _coerce_str(telemetry.get('semconv_version'))
            or _coerce_str(telemetry.get('opentelemetry_semconv_version'))
        )

        coverage = telemetry.get('coverage_percentage')
        if not isinstance(coverage, (int, float)):
            coverage = _estimate_telemetry_coverage(
                otel_instrumented,
                metrics_exported,
                traces_exported,
                logs_structured,
            )

        overlay_entry = self.overlays.get('telemetry', {}).get(module, {})
        if isinstance(overlay_entry, dict):
            otel_instrumented = otel_instrumented or bool(overlay_entry.get('otel_instrumented'))
            metrics_exported = metrics_exported or bool(overlay_entry.get('metrics_exported'))
            traces_exported = traces_exported or bool(overlay_entry.get('traces_exported'))
            logs_structured = logs_structured or bool(overlay_entry.get('logs_structured'))

            overlay_coverage = overlay_entry.get('coverage_percentage')
            if isinstance(overlay_coverage, (int, float)):
                coverage = max(float(coverage), float(overlay_coverage))

            if not semconv_version:
                semconv_version = _coerce_str(overlay_entry.get('semconv_version', ''))

        return {
            'otel_instrumented': otel_instrumented,
            'metrics_exported': metrics_exported,
            'traces_exported': traces_exported,
            'logs_structured': logs_structured,
            'semconv_version': semconv_version,
            'instrumentation_coverage': float(coverage),
        }

    def _validate_attestation(self, rats_data: Dict) -> bool:
        """Validate attestation evidence integrity."""
        if not rats_data.get('evidence_jwt'):
            return False

        # Basic JWT structure validation
        jwt = rats_data.get('evidence_jwt', '')
        if jwt == 'pending':
            return False

        parts = jwt.split('.')
        return len(parts) == 3  # header.payload.signature

    def analyze_vulnerability_exposure(self, telemetry: Dict) -> float:
        """Analyze vulnerability exposure across all modules."""
        findings = telemetry.get('vulnerability_findings', [])
        telemetry.get('total_modules', 1)

        if not findings:
            self.log("No vulnerability findings detected")
            return 100.0  # Perfect score if no vulnerabilities

        # Calculate exposure score based on severity
        severity_weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 1}
        total_weighted_vulns = sum(severity_weights.get(f.get('severity', 'low'), 1) for f in findings)

        # Create alerts for critical/high vulnerabilities
        for finding in findings:
            if finding.get('severity') in ['critical', 'high']:
                self.alerts.append(SecurityAlert(
                    severity=finding.get('severity'),
                    category='vulnerability',
                    message=f"Vulnerability {finding.get('vulnerability_id')} found in {finding.get('package')}",
                    affected_modules=[finding.get('module')],
                    remediation=f"Update to fixed version: {finding.get('fixed_version', 'latest')}",
                    timestamp=datetime.datetime.now(timezone.utc).isoformat()
                ))

        # Score: 100 = no vulnerabilities, decreases with weighted vulnerability count
        exposure_score = max(0, 100 - (total_weighted_vulns * 5))  # Each weighted vuln costs 5 points

        self.log(f"Vulnerability exposure score: {exposure_score:.1f}/100 ({len(findings)} findings)")
        return exposure_score

    def analyze_attestation_coverage(self, telemetry: Dict) -> float:
        """Analyze attestation coverage and health."""
        attestation_status = telemetry.get('attestation_status', {})
        total_modules = len(attestation_status)

        if total_modules == 0:
            return 0.0

        sum(1 for status in attestation_status.values()
                             if status.get('verifier_configured'))
        sum(1 for status in attestation_status.values()
                           if status.get('evidence_collected'))
        valid_count = sum(1 for status in attestation_status.values()
                         if status.get('attestation_valid'))

        # Check for attestation issues
        for module, status in attestation_status.items():
            if status.get('verifier_configured') and not status.get('evidence_collected'):
                self.alerts.append(SecurityAlert(
                    severity='medium',
                    category='attestation',
                    message=f"Attestation evidence collection failing for {module}",
                    affected_modules=[module],
                    remediation="Check verifier configuration and evidence collection pipeline",
                    timestamp=datetime.datetime.now(timezone.utc).isoformat()
                ))

        # Coverage score based on valid attestations
        coverage_score = (valid_count / total_modules) * 100

        self.log(f"Attestation coverage: {coverage_score:.1f}% ({valid_count}/{total_modules} valid)")
        return coverage_score

    def analyze_supply_chain_integrity(self, telemetry: Dict) -> float:
        """Analyze supply chain integrity posture."""
        supply_chain_data = telemetry.get('supply_chain_refs', {})
        total_modules = len(supply_chain_data)

        if total_modules == 0:
            return 0.0

        sbom_count = sum(1 for data in supply_chain_data.values() if data.get('sbom_present'))
        provenance_count = sum(1 for data in supply_chain_data.values()
                              if data.get('provenance_available') and
                              data.get('provenance_cid') != 'bafybeipending')
        reproducible_count = sum(1 for data in supply_chain_data.values()
                               if data.get('build_reproducible'))

        # Check for missing supply chain artifacts
        for module, data in supply_chain_data.items():
            if not data.get('sbom_present'):
                self.alerts.append(SecurityAlert(
                    severity='low',
                    category='supply_chain',
                    message=f"Missing SBOM for {module}",
                    affected_modules=[module],
                    remediation="Generate and reference SBOM in matrix contract",
                    timestamp=datetime.datetime.now(timezone.utc).isoformat()
                ))

        # Integrity score based on multiple factors
        sbom_score = (sbom_count / total_modules) * 40
        provenance_score = (provenance_count / total_modules) * 40
        reproducible_score = (reproducible_count / total_modules) * 20

        integrity_score = sbom_score + provenance_score + reproducible_score

        self.log(f"Supply chain integrity: {integrity_score:.1f}% "
                f"(SBOM: {sbom_count}/{total_modules}, "
                f"Provenance: {provenance_count}/{total_modules})")
        return integrity_score

    def analyze_telemetry_compliance(self, telemetry: Dict) -> float:
        """Analyze telemetry and observability compliance."""
        telemetry_coverage = telemetry.get('telemetry_coverage', {})
        total_modules = len(telemetry_coverage)

        if total_modules == 0:
            return 0.0

        otel_count = sum(1 for data in telemetry_coverage.values()
                        if data.get('otel_instrumented'))
        metrics_count = sum(1 for data in telemetry_coverage.values()
                           if data.get('metrics_exported'))
        traces_count = sum(1 for data in telemetry_coverage.values()
                          if data.get('traces_exported'))

        avg_coverage = sum(data.get('instrumentation_coverage', 0)
                          for data in telemetry_coverage.values()) / total_modules

        # Check for telemetry gaps
        for module, data in telemetry_coverage.items():
            if data.get('instrumentation_coverage', 0) < 70:
                self.alerts.append(SecurityAlert(
                    severity='low',
                    category='telemetry',
                    message=f"Low telemetry coverage in {module}: {data.get('instrumentation_coverage', 0)}%",
                    affected_modules=[module],
                    remediation="Increase OpenTelemetry instrumentation coverage",
                    timestamp=datetime.datetime.now(timezone.utc).isoformat()
                ))

        # Compliance score based on instrumentation and export coverage
        otel_score = (otel_count / total_modules) * 30
        export_score = ((metrics_count + traces_count) / (total_modules * 2)) * 30
        coverage_score = (avg_coverage / 100) * 40

        compliance_score = otel_score + export_score + coverage_score

        self.log(f"Telemetry compliance: {compliance_score:.1f}% "
                f"(OTel: {otel_count}/{total_modules}, Avg coverage: {avg_coverage:.1f}%)")
        return compliance_score

    def calculate_overall_posture_score(self) -> float:
        """Calculate weighted overall security posture score."""
        # Weighted scoring: vulnerabilities matter most, then attestation
        weights = {
            'vulnerability_exposure': 0.35,
            'attestation_coverage': 0.25,
            'supply_chain_integrity': 0.25,
            'telemetry_compliance': 0.15
        }

        overall_score = sum(self.metrics[metric] * weight
                           for metric, weight in weights.items())

        self.log(f"Overall security posture score: {overall_score:.1f}/100")
        return overall_score

    def generate_security_report(self, output_path: Optional[str] = None) -> Dict:
        """Generate comprehensive security posture report."""
        report = {
            'security_posture_report': {
                'timestamp': datetime.datetime.now(timezone.utc).isoformat(),
                'metrics': self.metrics,
                'alerts': [
                    {
                        'severity': alert.severity,
                        'category': alert.category,
                        'message': alert.message,
                        'affected_modules': alert.affected_modules,
                        'remediation': alert.remediation,
                        'timestamp': alert.timestamp
                    }
                    for alert in self.alerts
                ],
                'summary': {
                    'total_alerts': len(self.alerts),
                    'critical_alerts': len([a for a in self.alerts if a.severity == 'critical']),
                    'high_alerts': len([a for a in self.alerts if a.severity == 'high']),
                    'medium_alerts': len([a for a in self.alerts if a.severity == 'medium']),
                    'low_alerts': len([a for a in self.alerts if a.severity == 'low']),
                    'posture_grade': self._calculate_posture_grade(self.metrics['overall_posture_score'])
                },
                'recommendations': self._generate_recommendations()
            }
        }

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.log(f"Security report written to {output_path}")

        return report

    def _calculate_posture_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_recommendations(self) -> List[str]:
        """Generate security improvement recommendations."""
        recommendations = []

        if self.metrics['vulnerability_exposure'] < 80:
            recommendations.append("Address high-severity vulnerabilities immediately")
            recommendations.append("Implement automated vulnerability scanning in CI/CD")

        if self.metrics['attestation_coverage'] < 70:
            recommendations.append("Increase attestation coverage across modules")
            recommendations.append("Review and fix attestation evidence collection")

        if self.metrics['supply_chain_integrity'] < 60:
            recommendations.append("Generate SBOMs for all modules")
            recommendations.append("Implement provenance tracking for builds")

        if self.metrics['telemetry_compliance'] < 70:
            recommendations.append("Increase OpenTelemetry instrumentation coverage")
            recommendations.append("Enable structured logging across all modules")

        if not recommendations:
            recommendations.append("Security posture is excellent - maintain current practices")

        return recommendations

    def run_full_analysis(self, pattern: str = "**/matrix_*.json") -> Dict:
        """Run complete security posture analysis."""
        print("🛡️ Running Matrix Tracks Security Posture Analysis...")

        # Collect telemetry
        telemetry = self.collect_security_telemetry(pattern)

        # Run all analyses
        self.metrics['vulnerability_exposure'] = self.analyze_vulnerability_exposure(telemetry)
        self.metrics['attestation_coverage'] = self.analyze_attestation_coverage(telemetry)
        self.metrics['supply_chain_integrity'] = self.analyze_supply_chain_integrity(telemetry)
        self.metrics['telemetry_compliance'] = self.analyze_telemetry_compliance(telemetry)
        self.metrics['overall_posture_score'] = self.calculate_overall_posture_score()

        # Generate report
        report = self.generate_security_report()

        # Print summary
        self._print_summary()

        return report

    def _print_summary(self):
        """Print security posture summary."""
        score = self.metrics['overall_posture_score']
        grade = self._calculate_posture_grade(score)

        print("\n🛡️ Security Posture Summary")
        print(f"   Overall Score: {score:.1f}/100 (Grade: {grade})")
        print(f"   Vulnerability Exposure: {self.metrics['vulnerability_exposure']:.1f}%")
        print(f"   Attestation Coverage: {self.metrics['attestation_coverage']:.1f}%")
        print(f"   Supply Chain Integrity: {self.metrics['supply_chain_integrity']:.1f}%")
        print(f"   Telemetry Compliance: {self.metrics['telemetry_compliance']:.1f}%")

        # Print alerts summary
        critical_count = len([a for a in self.alerts if a.severity == 'critical'])
        high_count = len([a for a in self.alerts if a.severity == 'high'])

        if critical_count > 0:
            print(f"   🚨 {critical_count} CRITICAL alert(s)")
        if high_count > 0:
            print(f"   ⚠️ {high_count} HIGH alert(s)")
        if len(self.alerts) == 0:
            print("   ✅ No security alerts")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Matrix Tracks Security Posture Monitor")
    parser.add_argument("--pattern", default="**/matrix_*.json",
                       help="Glob pattern for matrix contracts")
    parser.add_argument("--output", help="Output file for security report")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--alert-on-critical", action="store_true",
                       help="Exit with error code if critical alerts found")

    args = parser.parse_args()

    # Run analysis
    monitor = SecurityPostureMonitor(verbose=args.verbose)
    report = monitor.run_full_analysis(args.pattern)

    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

    # Exit with error if critical alerts and flag is set
    if args.alert_on_critical:
        critical_count = report['security_posture_report']['summary']['critical_alerts']
        if critical_count > 0:
            print(f"\n❌ Exiting with error due to {critical_count} critical security alert(s)")
            sys.exit(1)

    print("\n✅ Security posture analysis complete")


if __name__ == "__main__":
    main()
