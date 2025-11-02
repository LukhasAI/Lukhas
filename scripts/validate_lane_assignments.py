#!/usr/bin/env python3
"""
LUKHAS Lane Assignment Validator
Production Schema v1.0.0

Validates lane assignment configuration and ensures T4/0.01% compliance.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class LaneAssignmentValidator:
    """Validates lane assignments for T4/0.01% compliance"""

    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path(__file__).parent.parent / "ops" / "lane_assignments.yaml"
        self.config: Dict[str, Any] = {}
        self.validation_results: Dict[str, Any] = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "compliance_status": {},
            "promotion_recommendations": [],
        }

    def load_config(self) -> bool:
        """Load lane assignment configuration"""
        try:
            if not self.config_file.exists():
                logger.error(f"Configuration file not found: {self.config_file}")
                return False

            with open(self.config_file, "r") as f:
                self.config = yaml.safe_load(f)

            logger.info(f"✅ Loaded lane assignment configuration: {self.config_file}")
            return True

        except yaml.YAMLError as e:
            logger.error(f"❌ Invalid YAML in configuration: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            return False

    def validate_component_assignments(self) -> None:
        """Validate individual component lane assignments"""
        components = self.config.get("components", {})

        for component_name, component_config in components.items():
            current_lane = component_config.get("current_lane")
            target_lane = component_config.get("target_lane")
            deployment_percentage = component_config.get("deployment_percentage", 0)

            # Validate required fields
            required_fields = ["current_lane", "target_lane", "rationale", "last_updated"]
            missing_fields = [field for field in required_fields if field not in component_config]

            if missing_fields:
                self.validation_results["issues"].append(
                    f"Component {component_name} missing required fields: {missing_fields}"
                )
                self.validation_results["valid"] = False

            # Validate lane progression
            if current_lane and target_lane:
                if not self._is_valid_lane_progression(current_lane, target_lane):
                    self.validation_results["issues"].append(
                        f"Component {component_name} has invalid lane progression: {current_lane} → {target_lane}"
                    )
                    self.validation_results["valid"] = False

            # Validate deployment percentages
            if current_lane == "production" and deployment_percentage != 100:
                self.validation_results["warnings"].append(
                    f"Component {component_name} in production lane but deployment < 100%"
                )

            # Check for stale assignments
            if self._is_assignment_stale(component_config):
                self.validation_results["warnings"].append(
                    f"Component {component_name} has stale assignment (last updated: {component_config.get('last_updated')})"
                )

    def _is_valid_lane_progression(self, current: str, target: str) -> bool:
        """Check if lane progression is valid"""
        valid_progressions = {
            "integration": ["integration", "production_canary"],
            "production_canary": ["production_canary", "production"],
            "production": ["production"],
        }

        return target in valid_progressions.get(current, [])

    def _is_assignment_stale(self, component_config: Dict[str, Any]) -> bool:
        """Check if component assignment is stale (>30 days old)"""
        last_updated_str = component_config.get("last_updated")
        if not last_updated_str:
            return True

        try:
            last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d")
            return (datetime.now() - last_updated) > timedelta(days=30)
        except ValueError:
            return True

    def validate_user_requirements(self) -> None:
        """Validate against specific user requirements"""
        components = self.config.get("components", {})

        # Check Registry is Production (100%)
        registry = components.get("registry", {})
        if registry.get("current_lane") != "production" or registry.get("deployment_percentage") != 100:
            self.validation_results["issues"].append("Registry must be in Production (100%) lane")
            self.validation_results["valid"] = False
        else:
            logger.info("✅ Registry correctly assigned to Production (100%)")

        # Check Guardian DSL + kill-switch is Production Canary (10-25%)
        guardian = components.get("guardian", {})
        guardian_pct = guardian.get("deployment_percentage", 0)
        if guardian.get("current_lane") != "production_canary" or not (10 <= guardian_pct <= 25):
            self.validation_results["issues"].append(
                f"Guardian should be in Production Canary (10-25%), currently: {guardian.get('current_lane')} ({guardian_pct}%)"
            )
            self.validation_results["valid"] = False
        else:
            logger.info(f"✅ Guardian correctly assigned to Production Canary ({guardian_pct}%)")

        # Check O.2 Multi-AI Router is Production Canary (10-25%)
        orchestration = components.get("orchestration", {})
        orch_pct = orchestration.get("deployment_percentage", 0)
        if orchestration.get("current_lane") != "production_canary" or not (10 <= orch_pct <= 25):
            self.validation_results["issues"].append(
                f"Orchestration should be in Production Canary (10-25%), currently: {orchestration.get('current_lane')} ({orch_pct}%)"
            )
            self.validation_results["valid"] = False
        else:
            logger.info(f"✅ Orchestration correctly assigned to Production Canary ({orch_pct}%)")

        # Check I.4 WebAuthn is Integration (with promotion path)
        webauthn = components.get("identity_webauthn", {})
        if webauthn.get("current_lane") != "integration":
            self.validation_results["warnings"].append(
                f"WebAuthn should be in Integration lane until CI job + alerts complete, currently: {webauthn.get('current_lane')}"
            )
        else:
            logger.info("✅ WebAuthn correctly assigned to Integration lane")

            # Check promotion criteria
            promotion_criteria = webauthn.get("promotion_criteria", [])
            if len(promotion_criteria) < 4:
                self.validation_results["warnings"].append("WebAuthn promotion criteria incomplete")

    def validate_environment_config(self) -> None:
        """Validate environment-specific configurations"""
        environments = self.config.get("environments", {})

        for env_name, env_config in environments.items():
            # Validate Guardian mode settings
            guardian_mode = env_config.get("guardian_mode")
            if env_name == "production" and guardian_mode != "production":
                self.validation_results["issues"].append(
                    f"Production environment must have guardian_mode=production, found: {guardian_mode}"
                )
                self.validation_results["valid"] = False

            # Validate feature flag consistency
            feature_flags = env_config.get("feature_flags", {})
            provider_calls = feature_flags.get("LUKHAS_ENABLE_PROVIDER_CALLS")

            if env_name == "production" and provider_calls is True:
                self.validation_results["warnings"].append(
                    "Production has LUKHAS_ENABLE_PROVIDER_CALLS=true - ensure this is intentional"
                )

    def validate_t4_compliance(self) -> None:
        """Validate T4/0.01% compliance requirements"""
        t4_config = self.config.get("t4_compliance", {})

        if not t4_config.get("required_for_production", False):
            self.validation_results["issues"].append("T4/0.01% compliance must be required for production")
            self.validation_results["valid"] = False

        # Check performance targets
        metrics = t4_config.get("metrics", {})
        expected_metrics = {"api_latency_p95": "< 500ms", "webauthn_latency_p95": "< 100ms", "error_rate": "< 0.01%"}

        for metric, expected in expected_metrics.items():
            if metrics.get(metric) != expected:
                self.validation_results["warnings"].append(
                    f"T4 metric {metric} should be '{expected}', found: '{metrics.get(metric)}'"
                )

    def check_promotion_opportunities(self) -> None:
        """Check for components ready for promotion"""
        components = self.config.get("components", {})

        for component_name, component_config in components.items():
            current_lane = component_config.get("current_lane")
            component_config.get("target_lane")
            status = component_config.get("status")

            # WebAuthn promotion check
            if (
                component_name == "identity_webauthn"
                and current_lane == "integration"
                and status == "promotion_pending"
            ):

                # Check if CI job exists
                ci_job_exists = self._check_ci_job_exists("identity-suite")
                alerts_exist = self._check_alert_files_exist()

                if ci_job_exists and alerts_exist:
                    self.validation_results["promotion_recommendations"].append(
                        f"✅ {component_name}: Ready for promotion to production_canary - CI job and alerts implemented"
                    )
                else:
                    missing = []
                    if not ci_job_exists:
                        missing.append("CI job")
                    if not alerts_exist:
                        missing.append("alert rules")

                    self.validation_results["promotion_recommendations"].append(
                        f"⏳ {component_name}: Waiting for {', '.join(missing)} before promotion"
                    )

    def _check_ci_job_exists(self, job_name: str) -> bool:
        """Check if specific CI job exists"""
        ci_dir = Path(__file__).parent.parent / ".github" / "workflows"
        for workflow_file in ci_dir.glob("*.yml"):
            try:
                with open(workflow_file, "r") as f:
                    content = f.read()
                    if job_name in content:
                        return True
            except Exception:
                continue
        return False

    def _check_alert_files_exist(self) -> bool:
        """Check if alert files exist"""
        alerts_dir = Path(__file__).parent.parent / "monitoring" / "alerts"
        return alerts_dir.exists() and len(list(alerts_dir.glob("*.yml"))) > 0

    def validate_all(self) -> Dict[str, Any]:
        """Run all validations"""
        logger.info("🔍 Starting lane assignment validation...")

        if not self.load_config():
            return self.validation_results

        logger.info("Validating component assignments...")
        self.validate_component_assignments()

        logger.info("Validating user requirements...")
        self.validate_user_requirements()

        logger.info("Validating environment configuration...")
        self.validate_environment_config()

        logger.info("Validating T4/0.01% compliance...")
        self.validate_t4_compliance()

        logger.info("Checking promotion opportunities...")
        self.check_promotion_opportunities()

        return self.validation_results

    def generate_report(self) -> None:
        """Generate validation report"""
        results = self.validation_results

        logger.info("=" * 60)
        logger.info("🎯 LUKHAS Lane Assignment Validation Report")
        logger.info("=" * 60)

        # Overall status
        if results["valid"]:
            logger.info("✅ Overall Status: VALID")
        else:
            logger.error("❌ Overall Status: INVALID")

        # Issues
        if results["issues"]:
            logger.error(f"🚨 Issues ({len(results['issues'])}):")
            for issue in results["issues"]:
                logger.error(f"  - {issue}")

        # Warnings
        if results["warnings"]:
            logger.warning(f"⚠️ Warnings ({len(results['warnings'])}):")
            for warning in results["warnings"]:
                logger.warning(f"  - {warning}")

        # Promotion recommendations
        if results["promotion_recommendations"]:
            logger.info(f"🚀 Promotion Recommendations ({len(results['promotion_recommendations'])}):")
            for rec in results["promotion_recommendations"]:
                logger.info(f"  - {rec}")

        logger.info("=" * 60)

    def save_results(self, output_file: Path = None) -> None:
        """Save validation results to file"""
        if output_file is None:
            output_file = Path(__file__).parent.parent / "artifacts" / "lane_assignment_validation.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        logger.info(f"💾 Results saved to: {output_file}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate LUKHAS lane assignments")
    parser.add_argument("--config", type=Path, help="Path to lane assignments config")
    parser.add_argument("--output", type=Path, help="Output file for results")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit with error code on validation failures")

    args = parser.parse_args()

    # Run validation
    validator = LaneAssignmentValidator(config_file=args.config)
    results = validator.validate_all()

    # Generate report
    validator.generate_report()

    # Save results
    validator.save_results(output_file=args.output)

    # Check if we should fail on errors
    if args.fail_on_error and not results["valid"]:
        logger.error("❌ Lane assignment validation failed - exiting with error")
        sys.exit(1)

    logger.info("✅ Lane assignment validation completed")
    return 0 if results["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
