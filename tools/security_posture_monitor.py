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
from pathlib import Path
from typing import Any, Dict, List


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
            'timestamp': datetime.datetime.utcnow().isoformat()
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
                            'timestamp': datetime.datetime.utcnow().isoformat()
                        })

        return findings

    def _extract_attestation_status(self, contract: Dict, module: str) -> Dict:
        """Extract attestation health status."""
        attestation = contract.get('attestation', {})
        rats_data = attestation.get('rats', {})

        return {
            'verifier_configured': bool(rats_data.get('verifier_policy')),
            'evidence_collected': bool(rats_data.get('evidence_jwt') and
                                     rats_data.get('evidence_jwt') != 'pending'),
            'attestation_valid': self._validate_attestation(rats_data),
            'last_attestation': rats_data.get('timestamp', ''),
            'verifier_version': rats_data.get('verifier_policy', {}).get('version', '')
        }

    def _extract_supply_chain_data(self, contract: Dict, module: str) -> Dict:
        """Extract supply chain integrity data."""
        supply_chain = contract.get('supply_chain', {})

        return {
            'sbom_present': bool(supply_chain.get('sbom_ref')),
            'sbom_ref': supply_chain.get('sbom_ref', ''),
            'sbom_format': supply_chain.get('format', ''),
            'provenance_available': bool(contract.get('causal_provenance', {}).get('ipld_root_cid')),
            'provenance_cid': contract.get('causal_provenance', {}).get('ipld_root_cid', ''),
            'build_reproducible': supply_chain.get('reproducible', False)
        }

    def _extract_telemetry_coverage(self, contract: Dict, module: str) -> Dict:
        """Extract telemetry and observability coverage."""
        telemetry = contract.get('telemetry', {})

        return {
            'otel_instrumented': bool(telemetry.get('opentelemetry')),
            'metrics_exported': bool(telemetry.get('metrics', {}).get('enabled')),
            'traces_exported': bool(telemetry.get('traces', {}).get('enabled')),
            'logs_structured': bool(telemetry.get('logs', {}).get('structured')),
            'semconv_version': telemetry.get('semconv_version', ''),
            'instrumentation_coverage': telemetry.get('coverage_percentage', 0)
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
                    timestamp=datetime.datetime.utcnow().isoformat()
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
                    timestamp=datetime.datetime.utcnow().isoformat()
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
                    timestamp=datetime.datetime.utcnow().isoformat()
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
                    timestamp=datetime.datetime.utcnow().isoformat()
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

    def generate_security_report(self, output_path: str = None) -> Dict:
        """Generate comprehensive security posture report."""
        report = {
            'security_posture_report': {
                'timestamp': datetime.datetime.utcnow().isoformat(),
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
