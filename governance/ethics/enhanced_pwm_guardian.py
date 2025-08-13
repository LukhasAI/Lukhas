#!/usr/bin/env python3
"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


🛡️ Enhanced PWM Workspace Guardian
===================================

Superior governance combining:
- Guardian System v1.0.0 (core governance)
- LUKHAS Ethics Guard (tier-based consent)
- Multi-framework Ethics Engine
- Red Team Protocol integration

This is the ENHANCED version using your superior ethics and red team components.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add ethics module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ethics import PWMEthicsOrchestrator
    from red_team import PWMRedTeamProtocol

    from .core import LucasGovernanceModule
except ImportError as e:
    print(f"⚠️ Enhanced features require ethics/red_team modules: {e}")
    # Fallback to basic governance
    from .core import LucasGovernanceModule

    PWMEthicsOrchestrator = None
    PWMRedTeamProtocol = None


class EnhancedPWMWorkspaceGuardian:
    """
    🌟 Enhanced PWM Workspace Guardian with Superior Ethics

    Combines:
    - Your advanced LUKHAS Ethics Guard
    - Multi-framework Ethics Engine
    - Red Team Protocol validation
    - Original Guardian System v1.0.0
    """

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()

        # Initialize governance components
        self.basic_governance = LucasGovernanceModule()

        # Initialize superior ethics (your components)
        if PWMEthicsOrchestrator:
            self.ethics_orchestrator = PWMEthicsOrchestrator()
            print("✅ Enhanced ethics system loaded")
        else:
            self.ethics_orchestrator = None
            print("⚠️ Using fallback basic ethics")

        # Initialize red team protocol
        if PWMRedTeamProtocol:
            self.red_team = PWMRedTeamProtocol()
            print("✅ Red team protocols loaded")
        else:
            self.red_team = None
            print("⚠️ Red team protocols not available")

        # Enhanced protection patterns
        self.critical_files = {
            "README.md",
            "LICENSE",
            "requirements.txt",
            "node_configs/package.json",
            ".gitignore",
            "Dockerfile",
            "Makefile",
            "pyproject.toml",
            "setup.py",
            "ethics_manifest.json",
            "pwm_config.yaml",
        }

        self.critical_directories = {
            ".git",
            ".github",
            "governance",
            "core",
            "ethics",
            "red_team",
        }

        self.workspace_health_score = 1.0
        self.security_posture = "PROTECTED"

    async def initialize(self):
        """Initialize the enhanced PWM workspace guardian."""
        await self.basic_governance.startup()

        if self.ethics_orchestrator:
            print(
                "🛡️ Enhanced PWM Guardian active - LUKHAS ethics + red team protection"
            )
        else:
            print("🛡️ PWM Guardian active - basic protection mode")

    async def enhanced_file_operation_check(
        self, operation: str, file_path: str, context: dict = None
    ) -> dict:
        """Enhanced file operation check using superior ethics."""

        context = context or {}
        file_name = os.path.basename(file_path)

        # Build enhanced context
        enhanced_context = {
            "file_name": file_name,
            "file_path": file_path,
            "operation_type": operation,
            "workspace_root": self.workspace_root,
            "tier_required": 2,  # Standard workspace operations
            "user_consent": {
                "tier": 5,  # Workspace owner has full access
                "allowed_signals": ["workspace_management", "file_operations"],
            },
            "intent": "productivity",
            "impact": "local",
            "timestamp": datetime.now().isoformat(),
            **context,
        }

        # Critical file protection (immediate block)
        if file_name in self.critical_files and operation in ["delete", "rm", "remove"]:
            return {
                "allowed": False,
                "reason": f"🛡️ Critical file protected by Enhanced Guardian: {file_name}",
                "action": "block_critical_file_deletion",
                "severity": "critical",
                "ethics_framework": "ENHANCED_PROTECTION",
                "confidence": 1.0,
            }

        # Use superior ethics system if available
        if self.ethics_orchestrator:
            try:
                ethics_result = (
                    await self.ethics_orchestrator.evaluate_workspace_action(
                        f"{operation} {file_path}", enhanced_context
                    )
                )

                # Enhanced decision with ethics integration
                return {
                    "allowed": ethics_result["allowed"],
                    "reason": f"🧠 Enhanced Ethics: {ethics_result['reason']}",
                    "action": "allow" if ethics_result["allowed"] else "block",
                    "severity": "safe" if ethics_result["allowed"] else "warning",
                    "ethics_framework": ethics_result["framework"],
                    "ethics_score": ethics_result["ethics_score"],
                    "consent_verified": ethics_result.get("consent_verified", False),
                    "confidence": ethics_result["ethics_score"],
                }

            except Exception as e:
                print(f"⚠️ Enhanced ethics error: {e}, falling back to basic governance")

        # Fallback to basic governance
        basic_request = {
            "data": f"{operation} {file_path}",
            "operation": "file_operation",
            "context": enhanced_context,
        }

        basic_result = await self.basic_governance.process_request(basic_request)

        return {
            "allowed": basic_result["governance_result"]["action"] == "allow",
            "reason": f"🛡️ Basic Guardian: {basic_result['governance_result']['reasoning']}",
            "action": basic_result["governance_result"]["action"],
            "severity": basic_result["governance_result"]["severity"],
            "ethics_framework": "BASIC_GOVERNANCE",
            "confidence": basic_result["governance_result"]["confidence"],
        }

    async def run_security_validation(self) -> dict:
        """Run comprehensive security validation using red team protocols."""

        security_report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": self.workspace_root,
            "security_posture": self.security_posture,
            "guardian_version": "ENHANCED-2.0.0",
        }

        if self.red_team:
            print("🔴 Running red team security validation...")

            # Test key attack scenarios
            scenarios = [
                "file_destruction",
                "configuration_corruption",
                "productivity_disruption",
            ]

            red_team_results = []
            for scenario in scenarios:
                try:
                    result = await self.red_team.run_attack_simulation(scenario)
                    red_team_results.append(result)
                except Exception as e:
                    red_team_results.append(
                        {
                            "scenario": scenario,
                            "error": str(e),
                            "status": "SIMULATION_ERROR",
                        }
                    )

            security_report["red_team_validation"] = {
                "protocol_summary": self.red_team.get_protocol_summary(),
                "scenarios_tested": red_team_results,
                "overall_status": (
                    "VALIDATED"
                    if all(
                        r.get("status") != "SIMULATION_ERROR" for r in red_team_results
                    )
                    else "PARTIAL_VALIDATION"
                ),
            }
        else:
            security_report["red_team_validation"] = {
                "status": "NOT_AVAILABLE",
                "message": "Red team protocols not loaded",
            }

        # Basic workspace health check
        health = await self.analyze_workspace_health()
        security_report["workspace_health"] = health

        # Generate security summary
        if self.ethics_orchestrator and self.red_team:
            security_summary = (
                "🌟 Enhanced security: LUKHAS ethics + red team protocols active"
            )
        elif self.ethics_orchestrator:
            security_summary = (
                "🛡️ Advanced security: LUKHAS ethics active, red team not available"
            )
        else:
            security_summary = "⚠️ Basic security: Fallback governance only"

        security_report["security_summary"] = security_summary

        return security_report

    async def analyze_workspace_health(self) -> dict:
        """Enhanced workspace health analysis."""

        health_factors = []
        issues = []
        recommendations = []

        # Enhanced file analysis
        file_count = sum(1 for _ in Path(self.workspace_root).rglob("*") if _.is_file())

        if file_count > 15000:  # Higher threshold for enhanced system
            health_factors.append(0.5)
            issues.append(f"Very high file count: {file_count} files")
            recommendations.append(
                "Consider enhanced PWM cleanup with red team validation"
            )
        elif file_count > 8000:
            health_factors.append(0.7)
            issues.append(f"High file count: {file_count} files")
        else:
            health_factors.append(1.0)

        # Enhanced critical files check
        critical_present = sum(
            1
            for cf in self.critical_files
            if os.path.exists(os.path.join(self.workspace_root, cf))
        )
        critical_ratio = critical_present / len(self.critical_files)
        health_factors.append(critical_ratio)

        # Enhanced security modules check
        ethics_health = 1.0 if self.ethics_orchestrator else 0.7
        redteam_health = 1.0 if self.red_team else 0.8
        health_factors.extend([ethics_health, redteam_health])

        if ethics_health < 1.0:
            issues.append("Enhanced ethics system not fully loaded")
            recommendations.append("Check ethics module dependencies")

        if redteam_health < 1.0:
            issues.append("Red team protocols not available")
            recommendations.append("Verify red team module installation")

        # Calculate enhanced health score
        self.workspace_health_score = sum(health_factors) / len(health_factors)

        return {
            "health_score": self.workspace_health_score,
            "status": self._get_enhanced_health_status(self.workspace_health_score),
            "file_count": file_count,
            "critical_files_ratio": critical_ratio,
            "ethics_system": "ENHANCED" if self.ethics_orchestrator else "BASIC",
            "red_team_available": self.red_team is not None,
            "issues": issues,
            "recommendations": recommendations,
            "last_check": datetime.now().isoformat(),
            "symbolic": self._get_enhanced_health_symbol(self.workspace_health_score),
        }

    def _get_enhanced_health_status(self, score: float) -> str:
        if score >= 0.95:
            return "excellent_enhanced"
        elif score >= 0.85:
            return "good_enhanced"
        elif score >= 0.75:
            return "fair_standard"
        elif score >= 0.65:
            return "poor_degraded"
        else:
            return "critical_compromised"

    def _get_enhanced_health_symbol(self, score: float) -> str:
        if score >= 0.95:
            return "�� Excellent enhanced workspace protection"
        elif score >= 0.85:
            return "🛡️ Good enhanced workspace security"
        elif score >= 0.75:
            return "⚖️ Fair workspace with standard protection"
        elif score >= 0.65:
            return "⚠️ Poor workspace - security degraded"
        else:
            return "🚨 Critical workspace - enhanced protection required"


# Enhanced convenience functions
async def enhanced_protect_workspace(workspace_root: str = None) -> dict:
    """Full enhanced workspace protection with superior ethics."""
    guardian = EnhancedPWMWorkspaceGuardian(workspace_root)
    await guardian.initialize()

    return await guardian.run_security_validation()


async def enhanced_file_check(
    operation: str, file_path: str, workspace_root: str = None
) -> dict:
    """Enhanced file operation check with LUKHAS ethics."""
    guardian = EnhancedPWMWorkspaceGuardian(workspace_root)
    await guardian.initialize()

    return await guardian.enhanced_file_operation_check(operation, file_path)


if __name__ == "__main__":
    # Demo enhanced functionality
    async def demo():
        print("🌟 Initializing Enhanced PWM Guardian...")
        guardian = EnhancedPWMWorkspaceGuardian()
        await guardian.initialize()

        # Test enhanced file protection
        result = await guardian.enhanced_file_operation_check("delete", "README.md")
        print(f"Enhanced README protection: {result['reason']}")

        # Run security validation
        security = await guardian.run_security_validation()
        print(f"Security validation: {security['security_summary']}")

        # Analyze enhanced health
        health = await guardian.analyze_workspace_health()
        print(f"Enhanced health: {health['symbolic']}")

    asyncio.run(demo())
