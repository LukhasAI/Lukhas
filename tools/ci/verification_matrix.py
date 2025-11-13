#!/usr/bin/env python3
"""
T4-Compliant Verification Matrix
PLANNING_TODO.md Section 8 Implementation

Implements verification requirements for each component type to ensure quality gates
and safety protocols as specified in PLANNING_TODO.md Section 8.
"""

import json
from typing import Any, Optional


class VerificationMatrix:
    """Implements verification requirements from PLANNING_TODO.md Section 8"""

    def __init__(self):
        self.verification_rules = self._initialize_verification_rules()

    def _initialize_verification_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize verification matrix as specified in PLANNING_TODO.md Section 8"""
        return {
            "identity_trace": {
                "description": "Identity/Trace verification requirements",
                "requirements": [
                    "New persistence layer → integration test writes/reads records",
                    "Audit chain linking verified via deterministic hash chain",
                    "ΛTRACE integration confirmed with live data flow",
                    "Identity namespace isolation tested",
                ],
                "test_patterns": ["test_*_identity_*", "test_*_trace_*", "test_*_persistence_*", "test_*_audit_*"],
                "modules": ["identity", "trace", "audit", "persistence"],
                "risk_level": "high",
                "requires_integration_test": True,
                "requires_hash_verification": True,
            },
            "consent_tier": {
                "description": "Consent/Tier verification requirements",
                "requirements": [
                    "Load tier boundaries from consent_tiers.json",
                    "Negative tests for out-of-range values",
                    "ZK proof stub gated behind feature flags",
                    "Consent model compliance verified",
                ],
                "test_patterns": ["test_*_consent_*", "test_*_tier_*", "test_*_boundary_*"],
                "modules": ["consent", "tier", "governance", "scopes"],
                "risk_level": "high",
                "requires_boundary_testing": True,
                "requires_feature_flags": True,
            },
            "guardian_ethics": {
                "description": "Guardian/Ethics verification requirements",
                "requirements": [
                    "Safety boundaries reconcile with global ΛTIER",
                    "Intent analysis integration mocked then real",
                    "Escalation paths tested",
                    "Ethical compliance verification",
                ],
                "test_patterns": ["test_*_guardian_*", "test_*_ethics_*", "test_*_safety_*", "test_*_intent_*"],
                "modules": ["guardian", "ethics", "safety", "intent"],
                "risk_level": "critical",
                "requires_safety_testing": True,
                "requires_escalation_testing": True,
            },
            "qi_entropy_qrg": {
                "description": "QI/Entropy/QRG verification requirements",
                "requirements": [
                    "Entropy sources mocked (no real entropy in tests)",
                    "SurfaceCode stubs compile behind feature flags",
                    "Replay/session logic has stateful tests",
                    "Quantum interfaces properly stubbed",
                ],
                "test_patterns": ["test_*_qi_*", "test_*_quantum_*", "test_*_entropy_*", "test_*_qrg_*"],
                "modules": ["qi", "quantum", "entropy", "qrg"],
                "risk_level": "critical",
                "requires_feature_flags": True,
                "requires_mocking": True,
                "no_production": True,
            },
            "dashboards": {
                "description": "Dashboard verification requirements",
                "requirements": [
                    "Streamlit widgets guarded against undefined references",
                    "Undefined refs removed from UI components",
                    "CI snapshot tests prevent regressions",
                    "Live data integration tested",
                ],
                "test_patterns": ["test_*_dashboard_*", "test_*_visual_*", "test_*_ui_*", "test_*_widget_*"],
                "modules": ["dashboard", "visual", "ui", "widget"],
                "risk_level": "medium",
                "requires_ui_testing": True,
                "requires_snapshot_testing": True,
            },
            "consciousness": {
                "description": "Consciousness system verification requirements",
                "requirements": [
                    "Consciousness state transitions tested",
                    "Awareness protocol compliance verified",
                    "Memory integration properly isolated",
                    "Constellation Framework alignment confirmed",
                ],
                "test_patterns": ["test_*_consciousness_*", "test_*_awareness_*", "test_*_trinity_*"],
                "modules": ["consciousness", "awareness", "constellation"],
                "risk_level": "critical",
                "requires_state_testing": True,
                "requires_isolation_testing": True,
            },
            "orchestration": {
                "description": "Orchestration system verification requirements",
                "requirements": [
                    "Workflow state management tested",
                    "Service integration verified",
                    "Error handling and recovery tested",
                    "Performance benchmarks established",
                ],
                "test_patterns": ["test_*_orchestration_*", "test_*_workflow_*", "test_*_service_*"],
                "modules": ["orchestration", "workflow", "service"],
                "risk_level": "high",
                "requires_integration_test": True,
                "requires_performance_testing": True,
            },
        }

    def verify_todo(self, todo: dict[str, Any]) -> dict[str, Any]:
        """Verify a manifest task against the appropriate verification matrix."""
        todo.get("module", "").lower()
        todo.get("risk", "medium")
        todo.get("est", {}).get("type", "unknown")

        # Determine verification category
        verification_category = self._categorize_todo(todo)

        if not verification_category:
            return self._create_basic_verification(todo)

        rules = self.verification_rules[verification_category]

        return {
            "todo_id": todo.get("task_id", "unknown"),
            "verification_category": verification_category,
            "risk_level": rules["risk_level"],
            "requirements": rules["requirements"],
            "acceptance_criteria": self._generate_acceptance_criteria(todo, rules),
            "test_requirements": self._generate_test_requirements(todo, rules),
            "safety_requirements": self._generate_safety_requirements(todo, rules),
            "evidence_requirements": self._generate_evidence_requirements(todo, rules),
        }

    def _categorize_todo(self, todo: dict[str, Any]) -> Optional[str]:
        """Categorize a task based on module and content."""
        module = todo.get("module", "").lower()
        title = todo.get("title", "").lower()
        file_path = todo.get("file", "").lower()

        # Check each verification category
        for category, rules in self.verification_rules.items():
            for module_pattern in rules["modules"]:
                if module_pattern in module or module_pattern in title or module_pattern in file_path:
                    return category

        return None

    def _create_basic_verification(self, todo: dict[str, Any]) -> dict[str, Any]:
        """Create basic verification for uncategorized tasks."""
        return {
            "todo_id": todo.get("task_id", "unknown"),
            "verification_category": "basic",
            "risk_level": todo.get("risk", "medium"),
            "requirements": [
                "Code changes reviewed for correctness",
                "Unit tests cover basic functionality",
                "Documentation updated if applicable",
            ],
            "acceptance_criteria": [
                "Implementation matches task description",
                "No breaking changes introduced",
                "Code follows project style guidelines",
            ],
            "test_requirements": ["Unit tests for core functionality"],
            "safety_requirements": ["Code review required"],
            "evidence_requirements": ["Passing tests", "Code review approval"],
        }

    def _generate_acceptance_criteria(self, todo: dict[str, Any], rules: dict[str, Any]) -> list[str]:
        """Generate acceptance criteria based on verification rules"""
        criteria = [
            "Implementation completes the recorded task requirements",
            "All verification requirements satisfied",
        ]

        if rules.get("requires_integration_test"):
            criteria.append("Integration tests pass with live components")

        if rules.get("requires_feature_flags"):
            criteria.append("Feature flags properly implemented and defaulted")

        if rules.get("requires_mocking"):
            criteria.append("External dependencies properly mocked")

        if rules.get("requires_safety_testing"):
            criteria.append("Safety boundaries tested and verified")

        if rules.get("requires_ui_testing"):
            criteria.append("UI components tested for undefined references")

        if rules.get("no_production"):
            criteria.append("Code gated to prevent production deployment")

        return criteria

    def _generate_test_requirements(self, todo: dict[str, Any], rules: dict[str, Any]) -> list[str]:
        """Generate test requirements based on verification rules"""
        tests = ["Unit tests cover happy path scenarios"]

        if rules.get("requires_integration_test"):
            tests.append("Integration tests with end-to-end data flow")

        if rules.get("requires_boundary_testing"):
            tests.append("Boundary testing for edge cases and invalid inputs")

        if rules.get("requires_escalation_testing"):
            tests.append("Error escalation paths tested")

        if rules.get("requires_state_testing"):
            tests.append("State transition testing")

        if rules.get("requires_isolation_testing"):
            tests.append("Component isolation testing")

        if rules.get("requires_snapshot_testing"):
            tests.append("UI snapshot tests for regression prevention")

        if rules.get("requires_performance_testing"):
            tests.append("Performance benchmarks established")

        return tests

    def _generate_safety_requirements(self, todo: dict[str, Any], rules: dict[str, Any]) -> list[str]:
        """Generate safety requirements based on verification rules"""
        safety = []

        if rules["risk_level"] == "critical":
            safety.append("Claude Code review required")
            safety.append("Comprehensive testing before merge")

        if rules.get("requires_feature_flags"):
            safety.append("Feature flags with safe defaults")
            safety.append("Kill switch functionality")

        if rules.get("no_production"):
            safety.append("Production deployment blocked")
            safety.append("Development environment only")

        if rules.get("requires_safety_testing"):
            safety.append("Safety boundary verification")
            safety.append("Escalation path testing")

        if rules.get("requires_hash_verification"):
            safety.append("Cryptographic hash verification")
            safety.append("Deterministic audit chain")

        return safety

    def _generate_evidence_requirements(self, todo: dict[str, Any], rules: dict[str, Any]) -> list[str]:
        """Generate evidence requirements for verification"""
        evidence = ["Passing test suite", "Code review approval", "Documentation updated"]

        if rules.get("requires_integration_test"):
            evidence.append("Integration test results")

        if rules.get("requires_feature_flags"):
            evidence.append("Feature flag configuration")

        if rules.get("requires_ui_testing"):
            evidence.append("UI test screenshots/videos")

        if rules.get("requires_performance_testing"):
            evidence.append("Performance benchmark results")

        return evidence

    def generate_verification_report(self, todos: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate comprehensive verification report for all tracked tasks."""
        verifications = [self.verify_todo(todo) for todo in todos]

        # Count by category and risk level
        by_category = {}
        by_risk = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for verification in verifications:
            category = verification["verification_category"]
            risk = verification["risk_level"]

            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1

            if risk in by_risk:
                by_risk[risk] += 1

        return {
            "total_todos": len(todos),
            "verification_categories": by_category,
            "risk_distribution": by_risk,
            "high_risk_count": by_risk["critical"] + by_risk["high"],
            "verification_details": verifications,
            "summary": {
                "critical_safety_todos": by_risk["critical"],
                "feature_flag_required": len(
                    [v for v in verifications if "Feature flags" in str(v.get("safety_requirements", []))]
                ),
                "claude_review_required": len([v for v in verifications if v["risk_level"] in ["critical", "high"]]),
                "production_blocked": len(
                    [
                        v
                        for v in verifications
                        if "Production deployment blocked" in str(v.get("safety_requirements", []))
                    ]
                ),
            },
        }


def main():
    """Generate verification matrix for current manifest"""
    import argparse

    parser = argparse.ArgumentParser(description="T4-Compliant Verification Matrix")
    parser.add_argument("--manifest", required=True, help="Manifest JSON file")
    parser.add_argument("--output", help="Output file for verification report")

    args = parser.parse_args()

    # Load manifest
    with open(args.manifest) as f:
        manifest = json.load(f)

    # Generate verification matrix
    verifier = VerificationMatrix()
    report = verifier.generate_verification_report(manifest.get("todos", []))

    # Save report
    output_file = args.output or args.manifest.replace(".json", "_verification.json")
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Generated verification matrix: {output_file}")
    print(f"📊 Summary: {report['total_todos']} tracked tasks, {report['high_risk_count']} high-risk")
    print(
        f"🛡️ Safety: {report['summary']['claude_review_required']} need review, "
        f"{report['summary']['feature_flag_required']} need feature flags"
    )


if __name__ == "__main__":
    main()
