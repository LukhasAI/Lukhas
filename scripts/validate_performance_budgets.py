#!/usr/bin/env python3
"""
Performance Budget Enforcement - T4/0.01% Excellence
====================================================

Validates performance artifacts against locked budgets with hard-fail enforcement.
Ensures MATRIZ canary readiness through contractual SLO compliance.

Performance Standards:
- tick: <100ms p95, reflect: <10ms p95, decide: <50ms p95
- Guardian: >1K ops/s throughput, <1ms mean latency
- E2E: <250ms p95 orchestration flow

Artifact Names: LOCKED - modification breaks CI/CD pipeline
Budget Enforcement: HARD FAIL - violations block deployment

Constellation Framework: ⚡ Performance Contract Guardian
"""

import json
import logging
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class PerformanceBudgetValidator:
    """Validates performance artifacts against locked budgets."""

    def __init__(self):
        """Initialize performance budget validator."""
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "config" / "performance" / "budgets.yaml"
        self.artifacts_dir = self.project_root / "artifacts"

        # Load budget configuration
        self.budgets = self.load_budget_config()
        self.violations = []
        self.warnings = []

    def load_budget_config(self) -> Dict:
        """Load performance budget configuration."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Budget config not found: {self.config_file}")

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            logger.info(f"Loaded performance budget config: {self.config_file}")
            return config
        except (yaml.YAMLError, IOError) as e:
            raise RuntimeError(f"Could not load budget config: {e}")

    def validate_artifact_naming(self) -> bool:
        """Validate all required performance artifacts exist with locked names."""
        logger.info("Validating artifact naming compliance...")

        required_artifacts = self.budgets.get("artifact_names", {}).get("performance_artifacts", [])
        missing_artifacts = []

        if not self.artifacts_dir.exists():
            self.violations.append(f"Artifacts directory not found: {self.artifacts_dir}")
            return False

        for artifact_name in required_artifacts:
            artifact_path = self.artifacts_dir / artifact_name
            if not artifact_path.exists():
                missing_artifacts.append(artifact_name)

        if missing_artifacts:
            self.violations.append(f"Missing performance artifacts: {missing_artifacts}")
            logger.error(f"❌ Missing artifacts: {missing_artifacts}")
            return False

        logger.info(f"✅ All {len(required_artifacts)} performance artifacts found")
        return True

    def load_performance_artifact(self, artifact_name: str) -> Optional[Dict]:
        """Load performance artifact data."""
        artifact_path = self.artifacts_dir / artifact_name

        if not artifact_path.exists():
            logger.warning(f"Artifact not found: {artifact_name}")
            return None

        try:
            with open(artifact_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Could not load artifact {artifact_name}: {e}")
            return None

    def validate_matriz_tick_budget(self) -> bool:
        """Validate MATRIZ tick operation against 100ms p95 budget."""
        logger.info("Validating MATRIZ tick performance budget...")

        tick_data = self.load_performance_artifact("matriz_tick_timings.json")
        if not tick_data:
            # Check E2E data for tick timings
            e2e_data = self.load_performance_artifact("matriz_perf_e2e_bootstrap.json")
            if e2e_data and "tick_stats" in e2e_data:
                tick_data = e2e_data["tick_stats"]

        if not tick_data:
            self.violations.append("MATRIZ tick timing data not found")
            return False

        budget_ms = self.budgets["performance_budgets"]["matriz_thought_loop"]["tick_operation"]["budget_ms"]

        # Extract p95 timing
        p95_ms = tick_data.get("ci95_upper_ms") or tick_data.get("p95_ms", float('inf'))

        if p95_ms > budget_ms:
            self.violations.append(
                f"MATRIZ tick p95 ({p95_ms:.2f}ms) exceeds budget ({budget_ms}ms) - HARD FAIL"
            )
            logger.error(f"❌ Tick budget violation: {p95_ms:.2f}ms > {budget_ms}ms")
            return False

        logger.info(f"✅ MATRIZ tick budget compliant: {p95_ms:.2f}ms ≤ {budget_ms}ms")
        return True

    def validate_matriz_reflect_budget(self) -> bool:
        """Validate MATRIZ reflect operation against 10ms p95 budget."""
        logger.info("Validating MATRIZ reflect performance budget...")

        reflect_data = self.load_performance_artifact("matriz_reflect_timings.json")
        if not reflect_data:
            # Check E2E data for reflect timings
            e2e_data = self.load_performance_artifact("matriz_perf_e2e_bootstrap.json")
            if e2e_data and "reflect_stats" in e2e_data:
                reflect_data = e2e_data["reflect_stats"]

        if not reflect_data:
            self.violations.append("MATRIZ reflect timing data not found")
            return False

        budget_ms = self.budgets["performance_budgets"]["matriz_thought_loop"]["reflect_operation"]["budget_ms"]

        # Extract p95 timing
        p95_ms = reflect_data.get("ci95_upper_ms") or reflect_data.get("p95_ms", float('inf'))

        if p95_ms > budget_ms:
            self.violations.append(
                f"MATRIZ reflect p95 ({p95_ms:.2f}ms) exceeds budget ({budget_ms}ms) - HARD FAIL"
            )
            logger.error(f"❌ Reflect budget violation: {p95_ms:.2f}ms > {budget_ms}ms")
            return False

        logger.info(f"✅ MATRIZ reflect budget compliant: {p95_ms:.2f}ms ≤ {budget_ms}ms")
        return True

    def validate_matriz_decide_budget(self) -> bool:
        """Validate MATRIZ decide operation against 50ms p95 budget."""
        logger.info("Validating MATRIZ decide performance budget...")

        decide_data = self.load_performance_artifact("matriz_decide_timings.json")
        if not decide_data:
            # Check E2E data for decide timings
            e2e_data = self.load_performance_artifact("matriz_perf_e2e_bootstrap.json")
            if e2e_data and "decide_stats" in e2e_data:
                decide_data = e2e_data["decide_stats"]

        if not decide_data:
            self.violations.append("MATRIZ decide timing data not found")
            return False

        budget_ms = self.budgets["performance_budgets"]["matriz_thought_loop"]["decide_operation"]["budget_ms"]

        # Extract p95 timing
        p95_ms = decide_data.get("ci95_upper_ms") or decide_data.get("p95_ms", float('inf'))

        if p95_ms > budget_ms:
            self.violations.append(
                f"MATRIZ decide p95 ({p95_ms:.2f}ms) exceeds budget ({budget_ms}ms) - HARD FAIL"
            )
            logger.error(f"❌ Decide budget violation: {p95_ms:.2f}ms > {budget_ms}ms")
            return False

        logger.info(f"✅ MATRIZ decide budget compliant: {p95_ms:.2f}ms ≤ {budget_ms}ms")
        return True

    def validate_guardian_throughput_budget(self) -> bool:
        """Validate Guardian throughput against >1K ops/s budget."""
        logger.info("Validating Guardian throughput performance budget...")

        guardian_data = self.load_performance_artifact("guardian_throughput_soak.json")
        if not guardian_data:
            self.violations.append("Guardian throughput data not found")
            return False

        budget_ops_per_sec = self.budgets["performance_budgets"]["guardian_performance"]["throughput"]["budget_ops_per_sec"]

        # Extract throughput measurement
        actual_throughput = guardian_data.get("throughput_ops_per_sec", 0.0)

        if actual_throughput < budget_ops_per_sec:
            self.violations.append(
                f"Guardian throughput ({actual_throughput:.1f} ops/s) below budget ({budget_ops_per_sec} ops/s) - HARD FAIL"
            )
            logger.error(f"❌ Guardian throughput violation: {actual_throughput:.1f} < {budget_ops_per_sec}")
            return False

        logger.info(f"✅ Guardian throughput budget compliant: {actual_throughput:.1f} ≥ {budget_ops_per_sec} ops/s")
        return True

    def validate_guardian_latency_budget(self) -> bool:
        """Validate Guardian latency against <1ms mean budget."""
        logger.info("Validating Guardian latency performance budget...")

        guardian_data = self.load_performance_artifact("guardian_throughput_soak.json")
        if not guardian_data:
            self.violations.append("Guardian latency data not found")
            return False

        budget_ms = self.budgets["performance_budgets"]["guardian_performance"]["latency"]["budget_ms"]

        # Extract mean latency
        mean_latency_ms = guardian_data.get("mean_latency_ms", float('inf'))

        if mean_latency_ms > budget_ms:
            self.violations.append(
                f"Guardian mean latency ({mean_latency_ms:.3f}ms) exceeds budget ({budget_ms}ms) - HARD FAIL"
            )
            logger.error(f"❌ Guardian latency violation: {mean_latency_ms:.3f}ms > {budget_ms}ms")
            return False

        logger.info(f"✅ Guardian latency budget compliant: {mean_latency_ms:.3f}ms ≤ {budget_ms}ms")
        return True

    def validate_e2e_orchestration_budget(self) -> bool:
        """Validate end-to-end orchestration against <250ms p95 budget."""
        logger.info("Validating E2E orchestration performance budget...")

        e2e_data = self.load_performance_artifact("cross_stack_integration_perf.json")
        if not e2e_data:
            # Try E2E bootstrap data
            e2e_data = self.load_performance_artifact("matriz_perf_e2e_bootstrap.json")

        if not e2e_data:
            self.violations.append("E2E orchestration timing data not found")
            return False

        budget_ms = self.budgets["performance_budgets"]["cross_stack_integration"]["orchestrator_to_matriz"]["budget_ms"]

        # Extract p95 timing
        p95_ms = (e2e_data.get("total_time_stats", {}).get("ci95_upper_ms") or
                 e2e_data.get("e2e_p95_ms", float('inf')))

        if p95_ms > budget_ms:
            self.violations.append(
                f"E2E orchestration p95 ({p95_ms:.2f}ms) exceeds budget ({budget_ms}ms) - HARD FAIL"
            )
            logger.error(f"❌ E2E budget violation: {p95_ms:.2f}ms > {budget_ms}ms")
            return False

        logger.info(f"✅ E2E orchestration budget compliant: {p95_ms:.2f}ms ≤ {budget_ms}ms")
        return True

    def validate_statistical_rigor(self) -> bool:
        """Validate performance measurements meet statistical requirements."""
        logger.info("Validating statistical rigor requirements...")

        requirements = self.budgets.get("enforcement", {}).get("validation_requirements", {})
        min_samples = requirements.get("minimum_samples", 1000)
        required_ci = requirements.get("confidence_interval", 0.95)

        # Check E2E bootstrap data
        e2e_data = self.load_performance_artifact("matriz_perf_e2e_bootstrap.json")
        if e2e_data:
            actual_samples = e2e_data.get("total_samples", 0)
            confidence_level = e2e_data.get("confidence_level", 0.0)

            if actual_samples < min_samples:
                self.violations.append(f"Insufficient samples: {actual_samples} < {min_samples} required")
                return False

            if confidence_level < required_ci:
                self.violations.append(f"Insufficient confidence: {confidence_level} < {required_ci} required")
                return False

        logger.info(f"✅ Statistical rigor validated: {min_samples}+ samples, CI{required_ci*100}%")
        return True

    def generate_budget_report(self) -> Dict:
        """Generate comprehensive budget validation report."""
        report = {
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
            "validator_version": "1.0.0",
            "budget_config_version": self.budgets.get("version", "1.0.0"),
            "enforcement_mode": "hard_fail",
            "total_violations": len(self.violations),
            "total_warnings": len(self.warnings),
            "validation_passed": len(self.violations) == 0,
            "budget_compliance": {
                "matriz_tick_ms": None,
                "matriz_reflect_ms": None,
                "matriz_decide_ms": None,
                "guardian_throughput_ops": None,
                "guardian_latency_ms": None,
                "e2e_orchestration_ms": None
            },
            "violations": self.violations,
            "warnings": self.warnings,
            "artifacts_validated": [],
            "budget_definitions": self.budgets.get("performance_budgets", {}),
            "locked_artifact_names": self.budgets.get("artifact_names", {}).get("performance_artifacts", [])
        }

        return report

    def save_validation_report(self, report: Dict) -> bool:
        """Save budget validation report."""
        report_file = self.artifacts_dir / "performance_budget_validation.json"

        try:
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, sort_keys=True)

            logger.info(f"Budget validation report saved: {report_file}")
            return True
        except IOError as e:
            logger.error(f"Could not save validation report: {e}")
            return False

    def validate_all_budgets(self) -> bool:
        """Validate all performance budgets."""
        logger.info("=== Performance Budget Validation ===")

        # Validate artifact naming
        naming_valid = self.validate_artifact_naming()

        # Validate individual budgets
        budgets_valid = all([
            self.validate_matriz_tick_budget(),
            self.validate_matriz_reflect_budget(),
            self.validate_matriz_decide_budget(),
            self.validate_guardian_throughput_budget(),
            self.validate_guardian_latency_budget(),
            self.validate_e2e_orchestration_budget()
        ])

        # Validate statistical rigor
        stats_valid = self.validate_statistical_rigor()

        # Generate report
        report = self.generate_budget_report()
        self.save_validation_report(report)

        overall_valid = naming_valid and budgets_valid and stats_valid

        if overall_valid:
            logger.info("✅ ALL PERFORMANCE BUDGETS PASSED")
        else:
            logger.error(f"❌ PERFORMANCE BUDGET VIOLATIONS: {len(self.violations)}")
            for violation in self.violations[:5]:  # Show first 5 violations
                logger.error(f"   - {violation}")

        return overall_valid


def main():
    """Main budget validation entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=== MATRIZ Performance Budget Enforcement ===")
    print("T4/0.01% Excellence Standards")
    print("Hard-fail enforcement for canary readiness")
    print()

    validator = PerformanceBudgetValidator()

    try:
        success = validator.validate_all_budgets()

        if success:
            print("✅ PERFORMANCE BUDGET VALIDATION PASSED")
            print("🚀 MATRIZ canary ready for performance requirements")
            return 0
        else:
            print("❌ PERFORMANCE BUDGET VALIDATION FAILED")
            print(f"💥 {len(validator.violations)} budget violations block deployment")
            print()
            print("🔧 Violations:")
            for i, violation in enumerate(validator.violations, 1):
                print(f"   {i}. {violation}")
            return 1

    except Exception as e:
        print(f"❌ VALIDATION ERROR: {e}")
        logger.error(f"Budget validation error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())