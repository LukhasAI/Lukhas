#!/usr/bin/env python3
"""

#TAG:governance
#TAG:guardian
#TAG:neuroplastic
#TAG:colony


🎯 LUKHAS Workspace Guardian
===========================

Intelligent workspace management with ethical oversight.

Integrates:
- Guardian System v1.0.0 (core governance)
- Workspace-specific safety protocols
- File operation ethics
- Productivity governance

Purpose: Keep your workspace safe, organized, and productive.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

try:
    from core import (
        EthicalDecision,
        EthicalSeverity,
        GovernanceAction,
        LucasGovernanceModule,
    )
except ImportError:
    # Fallback for relative import
    try:
        from .core import (
            EthicalDecision,
            EthicalSeverity,
            GovernanceAction,
            LucasGovernanceModule,
        )
    except ImportError:
        # Create minimal classes if imports fail
        from dataclasses import dataclass
        from enum import Enum

        class EthicalSeverity(Enum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
            CRITICAL = "critical"

        @dataclass
        class GovernanceAction:
            action_type: str
            target: str
            context: dict

        @dataclass
        class EthicalDecision:
            allowed: bool
            reason: str
            severity: EthicalSeverity

        class LucasGovernanceModule:
            def __init__(self):
                self.active = False

            async def startup(self):
                self.active = True


class WorkspaceGuardian:
    """
    🛡️ -specific workspace governance with ethical oversight.

    Protects your workspace from:
    - Accidental file deletions
    - Workspace bloat accumulation
    - Productivity-harming operations
    - Configuration corruption
    """

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.governance = LucasGovernanceModule()

        # -specific protection patterns
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
        }

        self.critical_directories = {".git", ".github", "governance", "core"}

        self.workspace_health_score = 1.0
        self.last_cleanup_check = datetime.now()

    async def initialize(self):
        """Initialize the  workspace guardian."""
        await self.governance.startup()
        print("🛡️  Workspace Guardian active - protecting your productivity workspace")

    async def check_file_operation(
        self, operation: str, file_path: str, context: dict = None
    ) -> dict:
        """Check if a file operation should be allowed."""

        context = context or {}
        file_name = os.path.basename(file_path)

        # Build governance request
        request = {
            "data": f"{operation} {file_path}",
            "operation": "file_operation",
            "context": {
                "file_name": file_name,
                "file_path": file_path,
                "operation_type": operation,
                "workspace_root": self.workspace_root,
                "user_id": "_user",
                "access_tier": 5,  # High trust for workspace owner
                "timestamp": datetime.now().isoformat(),
                **context,
            },
        }

        # Critical file protection
        if file_name in self.critical_files and operation in ["delete", "rm", "remove"]:
            return {
                "allowed": False,
                "reason": f"🛡️ Critical file protected: {file_name}",
                "action": "block_critical_file_deletion",
                "severity": "critical",
            }

        # Critical directory protection
        if any(critical_dir in file_path for critical_dir in self.critical_directories):
            if operation in ["delete", "rm", "remove", "rmdir"]:
                return {
                    "allowed": False,
                    "reason": f"🛡️ Critical directory protected: {file_path}",
                    "action": "block_critical_dir_deletion",
                    "severity": "critical",
                }

        # Use full governance system for complex decisions
        governance_result = await self.governance.process_request(request)

        return {
            "allowed": governance_result["governance_result"]["action"] == "allow",
            "reason": governance_result["governance_result"]["reasoning"],
            "action": governance_result["governance_result"]["action"],
            "severity": governance_result["governance_result"]["severity"],
            "confidence": governance_result["governance_result"]["confidence"],
            "symbolic": governance_result.get("symbolic_representation", "🛡️"),
        }

    async def analyze_workspace_health(self) -> dict:
        """Analyze overall workspace health and productivity."""

        health_factors = []
        issues = []
        recommendations = []

        # Check file count (detect bloat)
        file_count = sum(1 for _ in Path(self.workspace_root).rglob("*") if _.is_file())
        if file_count > 10000:
            health_factors.append(0.6)
            issues.append(f"High file count: {file_count} files")
            recommendations.append("Consider archiving old files")
        elif file_count > 5000:
            health_factors.append(0.8)
            issues.append(f"Moderate file count: {file_count} files")
        else:
            health_factors.append(1.0)

        # Check for critical files presence
        critical_present = sum(
            1 for cf in self.critical_files if os.path.exists(os.path.join(self.workspace_root, cf))
        )
        critical_ratio = critical_present / len(self.critical_files)
        health_factors.append(critical_ratio)

        if critical_ratio < 0.5:
            issues.append("Missing critical configuration files")
            recommendations.append("Ensure README.md and core config files exist")

        # Check git repository health
        git_dir = os.path.join(self.workspace_root, ".git")
        if os.path.exists(git_dir):
            health_factors.append(1.0)
        else:
            health_factors.append(0.7)
            issues.append("No git repository detected")
            recommendations.append("Consider initializing git repository")

        # Calculate overall health
        self.workspace_health_score = sum(health_factors) / len(health_factors)

        return {
            "health_score": self.workspace_health_score,
            "status": self._get_health_status(self.workspace_health_score),
            "file_count": file_count,
            "critical_files_ratio": critical_ratio,
            "issues": issues,
            "recommendations": recommendations,
            "last_check": datetime.now().isoformat(),
            "symbolic": self._get_health_symbol(self.workspace_health_score),
        }

    def _get_health_status(self, score: float) -> str:
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "fair"
        elif score >= 0.6:
            return "poor"
        else:
            return "critical"

    def _get_health_symbol(self, score: float) -> str:
        if score >= 0.9:
            return "🌟 Excellent workspace health"
        elif score >= 0.8:
            return "✅ Good workspace health"
        elif score >= 0.7:
            return "⚠️ Fair workspace health"
        elif score >= 0.6:
            return "🔶 Poor workspace health"
        else:
            return "🚨 Critical workspace issues"

    async def suggest_cleanup(self) -> dict:
        """Suggest workspace cleanup actions."""
        suggestions = []

        # Check for common cleanup opportunities
        patterns_to_check = [
            ("*.log", "Log files"),
            ("*.tmp", "Temporary files"),
            ("*~", "Backup files"),
            ("*.pyc", "Python bytecode"),
            ("__pycache__", "Python cache directories"),
            (".DS_Store", "macOS system files"),
        ]

        cleanup_candidates = []
        for pattern, description in patterns_to_check:
            files = list(Path(self.workspace_root).rglob(pattern))
            if files:
                cleanup_candidates.append(
                    {
                        "pattern": pattern,
                        "description": description,
                        "count": len(files),
                        "files": [str(f) for f in files[:10]],  # Show first 10
                    }
                )

        if cleanup_candidates:
            suggestions.append(
                {
                    "type": "cleanup",
                    "priority": "medium",
                    "description": "Remove temporary and generated files",
                    "candidates": cleanup_candidates,
                }
            )

        # Check for archive opportunities
        old_files = []
        cutoff_date = datetime.now().timestamp() - (90 * 24 * 60 * 60)  # 90 days ago

        for file_path in Path(self.workspace_root).rglob("*.md"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                old_files.append(str(file_path))

        if len(old_files) > 20:
            suggestions.append(
                {
                    "type": "archive",
                    "priority": "low",
                    "description": f"Archive {len(old_files)} old documentation files",
                    "files": old_files[:10],
                }
            )

        return {
            "suggestions": suggestions,
            "cleanup_candidates": len(cleanup_candidates),
            "archive_candidates": len(old_files),
            "last_check": datetime.now().isoformat(),
            "workspace_health": self.workspace_health_score,
        }

    async def protect_workspace(self) -> dict:
        """Run comprehensive workspace protection check."""

        print("��️ Running  workspace protection analysis...")

        # Analyze health
        health = await self.analyze_workspace_health()

        # Get cleanup suggestions
        cleanup = await self.suggest_cleanup()

        # Check governance system health
        governance_health = await self.governance.get_health_status()

        protection_report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": self.workspace_root,
            "workspace_health": health,
            "cleanup_suggestions": cleanup,
            "governance_health": governance_health["module_health"],
            "protection_status": "active",
            "guardian_version": "-1.0.0",
        }

        # Generate symbolic summary
        if health["health_score"] >= 0.8:
            symbolic_status = "🌟 Workspace thriving under guardian protection"
        elif health["health_score"] >= 0.6:
            symbolic_status = "⚠️ Workspace stable with minor improvements needed"
        else:
            symbolic_status = "🚨 Workspace requires guardian intervention"

        protection_report["symbolic_summary"] = symbolic_status

        return protection_report


#  Convenience Functions
async def check_file_delete(file_path: str, workspace_root: str = None) -> bool:
    """Quick check if file deletion should be allowed."""
    guardian = WorkspaceGuardian(workspace_root)
    await guardian.initialize()

    result = await guardian.check_file_operation("delete", file_path)
    return result["allowed"]


async def analyze_workspace(workspace_root: str = None) -> dict:
    """Quick workspace health analysis."""
    guardian = WorkspaceGuardian(workspace_root)
    await guardian.initialize()

    return await guardian.analyze_workspace_health()


async def protect_my_workspace(workspace_root: str = None) -> dict:
    """Full workspace protection analysis."""
    guardian = WorkspaceGuardian(workspace_root)
    await guardian.initialize()

    return await guardian.protect_workspace()


if __name__ == "__main__":
    # Demo usage
    async def demo():
        guardian = WorkspaceGuardian()
        await guardian.initialize()

        # Test file operation protection
        result = await guardian.check_file_operation("delete", "README.md")
        print(f"Delete README.md: {result}")

        # Analyze workspace health
        health = await guardian.analyze_workspace_health()
        print(f"Workspace health: {health['symbolic']}")

        # Get cleanup suggestions
        cleanup = await guardian.suggest_cleanup()
        print(f"Cleanup suggestions: {len(cleanup['suggestions'])}")

    asyncio.run(demo())
