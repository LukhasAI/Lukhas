#!/usr/bin/env python3
"""
LUKHAS Code Quality Self-Healing Extension
Autonomous code quality improvement using consciousness principles
Constellation Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from bridge.local_llm_fixer import CodeIssue, FixType, LocalLLMFixer
from core.cognitive.self_healing import FailureType, HealingAction, HealingStrategy, SystemFailure
from governance.guardian import GuardianSystem

logger = logging.getLogger(__name__)


# Define failure types for code quality (separate enum)
class CodeQualityFailureType(Enum):
    """Failure types specific to code quality"""

    CODE_SYNTAX_ERROR = "code_syntax_error"
    CODE_UNDEFINED_NAME = "code_undefined_name"
    CODE_UNUSED_IMPORT = "code_unused_import"
    CODE_FORMATTING = "code_formatting"
    CODE_COMPLEXITY = "code_complexity"
    CODE_SECURITY = "code_security"


# Define healing strategies for code fixes (separate enum)
class CodeHealingStrategy(Enum):
    """Healing strategies specific to code quality"""

    AUTO_FIX = "auto_fix"
    LLM_REPAIR = "llm_repair"
    REFACTOR = "refactor"
    GUARDIAN_REVIEW = "guardian_review"
    LEARN_PATTERN = "learn_pattern"


@dataclass
class CodeQualityMetrics:
    """Metrics for code quality tracking"""

    total_issues: int = 0
    fixed_issues: int = 0
    failed_fixes: int = 0
    syntax_errors: int = 0
    undefined_names: int = 0
    formatting_issues: int = 0
    security_issues: int = 0
    complexity_score: float = 0.0
    improvement_rate: float = 0.0
    last_scan: Optional[datetime] = None


class CodeQualityHealer:
    """
    Self-healing system for code quality issues.
    Integrates with LUKHAS consciousness for intelligent improvement.
    """

    def __init__(
        self,
        workspace_path: str = ".",
        guardian_threshold: float = 0.15,
        auto_fix_threshold: float = 0.85,
        learning_enabled: bool = True,
    ):
        self.workspace_path = Path(workspace_path)
        self.guardian_threshold = guardian_threshold
        self.auto_fix_threshold = auto_fix_threshold
        self.learning_enabled = learning_enabled

        # Initialize components
        self.llm_fixer = LocalLLMFixer(guardian_threshold=auto_fix_threshold)
        self.guardian = GuardianSystem(drift_threshold=guardian_threshold)
        self.metrics = CodeQualityMetrics()

        # Memory for learning patterns
        self.fix_patterns: dict[str, list[dict]] = {}
        self.successful_strategies: list[str] = []

    async def scan_codebase(self) -> list[SystemFailure]:
        """Scan codebase for quality issues"""
        failures = []
        python_files = list(self.workspace_path.rglob("*.py"))

        logger.info(f"Scanning {len(python_files)} Python files...")
        self.metrics.last_scan = datetime.now(timezone.utc)

        async with self.llm_fixer as fixer:
            for file_path in python_files:
                # Skip test files and generated code
                if any(skip in str(file_path) for skip in ["test_", "__pycache__", ".venv"]):
                    continue

                issues = await fixer.analyze_file(str(file_path))

                for issue in issues:
                    failure = SystemFailure(
                        id=f"{file_path}:{issue.line_number}",
                        type=self._map_issue_to_failure(issue.issue_type),
                        component=str(file_path),
                        error=Exception(issue.message),
                        timestamp=datetime.now(timezone.utc),
                        context={
                            "line": issue.line_number,
                            "code_context": issue.code_context,
                            "fix_type": issue.issue_type.value,
                        },
                        severity=issue.severity,
                    )
                    failures.append(failure)

                    # Update metrics
                    self.metrics.total_issues += 1
                    self._update_issue_metrics(issue.issue_type)

        logger.info(f"Found {len(failures)} code quality issues")
        return failures

    def _map_issue_to_failure(self, fix_type: FixType) -> FailureType:
        """Map FixType to FailureType"""
        mapping = {
            FixType.SYNTAX_ERROR: CodeQualityFailureType.CODE_SYNTAX_ERROR,
            FixType.UNDEFINED_NAME: CodeQualityFailureType.CODE_UNDEFINED_NAME,
            FixType.UNUSED_IMPORT: CodeQualityFailureType.CODE_UNUSED_IMPORT,
            FixType.FORMATTING: CodeQualityFailureType.CODE_FORMATTING,
        }
        return mapping.get(fix_type, FailureType.CORRUPTION)

    def _update_issue_metrics(self, fix_type: FixType):
        """Update metrics based on issue type"""
        if fix_type == FixType.SYNTAX_ERROR:
            self.metrics.syntax_errors += 1
        elif fix_type == FixType.UNDEFINED_NAME:
            self.metrics.undefined_names += 1
        elif fix_type == FixType.FORMATTING:
            self.metrics.formatting_issues += 1

    async def heal_failure(self, failure: SystemFailure, strategy: Optional[HealingStrategy] = None) -> HealingAction:
        """Heal a specific code quality failure"""

        # Determine strategy if not provided
        if not strategy:
            strategy = self._select_healing_strategy(failure)

        success = False

        try:
            if strategy == CodeHealingStrategy.AUTO_FIX:
                success = await self._auto_fix(failure)
            elif strategy == CodeHealingStrategy.LLM_REPAIR:
                success = await self._llm_repair(failure)
            elif strategy == CodeHealingStrategy.GUARDIAN_REVIEW:
                success = await self._guardian_review(failure)
            elif strategy == CodeHealingStrategy.LEARN_PATTERN:
                success = await self._learn_pattern(failure)
            else:
                logger.warning(f"Unknown strategy: {strategy}")
        except Exception as e:
            logger.error(f"Healing failed: {e}")

        # Record healing action
        action = HealingAction(
            failure_id=failure.id,
            strategy=strategy,
            component=failure.component,
            timestamp=datetime.now(timezone.utc),
            success=success,
            details={
                "metrics": self.metrics.__dict__,
                "confidence": self.auto_fix_threshold,
            },
        )

        # Update metrics
        if success:
            self.metrics.fixed_issues += 1
            self.successful_strategies.append(strategy.value)
        else:
            self.metrics.failed_fixes += 1

        self.metrics.improvement_rate = self.metrics.fixed_issues / max(1, self.metrics.total_issues)

        return action

    def _select_healing_strategy(self, failure: SystemFailure) -> HealingStrategy:
        """Select appropriate healing strategy based on failure type and context"""

        # Critical failures need Guardian review
        if failure.severity > 0.8:
            return CodeHealingStrategy.GUARDIAN_REVIEW

        # Syntax errors need LLM repair
        if failure.type == CodeQualityFailureType.CODE_SYNTAX_ERROR:
            return CodeHealingStrategy.LLM_REPAIR

        # Simple formatting can be auto-fixed
        if failure.type == CodeQualityFailureType.CODE_FORMATTING:
            return CodeHealingStrategy.AUTO_FIX

        # Learn from patterns if we've seen similar issues
        if self._has_similar_pattern(failure):
            return CodeHealingStrategy.LEARN_PATTERN

        # Default to LLM repair
        return CodeHealingStrategy.LLM_REPAIR

    def _has_similar_pattern(self, failure: SystemFailure) -> bool:
        """Check if we've seen similar patterns before"""
        pattern_key = f"{failure.type}:{failure.component}"
        return pattern_key in self.fix_patterns and len(self.fix_patterns[pattern_key]) > 3

    async def _auto_fix(self, failure: SystemFailure) -> bool:
        """Apply automatic fixes for simple issues"""
        try:
            # Use ruff --fix for formatting issues
            if failure.type == CodeQualityFailureType.CODE_FORMATTING:
                import subprocess

                result = subprocess.run(
                    ["python3", "-m", "ruff", "check", failure.component, "--fix"],
                    capture_output=True,
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Auto-fix failed: {e}")
        return False

    async def _llm_repair(self, failure: SystemFailure) -> bool:
        """Use LLM to repair complex issues"""
        async with self.llm_fixer as fixer:
            # Create a CodeIssue from the failure
            issue = CodeIssue(
                file_path=failure.component,
                line_number=failure.context.get("line", 0),
                issue_type=FixType.SYNTAX_ERROR,  # Map from failure type
                message=str(failure.error),
                code_context=failure.context.get("code_context", ""),
                severity=failure.severity,
            )

            # Generate and apply fix
            fix = await fixer.generate_fix(issue)
            if fix and fix.confidence > self.auto_fix_threshold:
                success = await fixer.apply_fix(fix)

                # Learn from successful fix
                if success and self.learning_enabled:
                    self._record_fix_pattern(failure, fix)

                return success
        return False

    async def _guardian_review(self, failure: SystemFailure) -> bool:
        """Submit fix for Guardian review before applying"""
        try:
            # Check with Guardian system
            drift_score = await self.guardian.check_drift(
                {
                    "action": "code_fix",
                    "component": failure.component,
                    "severity": failure.severity,
                }
            )

            if drift_score < self.guardian_threshold:
                # Guardian approved, proceed with LLM repair
                return await self._llm_repair(failure)
            else:
                logger.warning(f"Guardian rejected fix: drift score {drift_score}")
                return False
        except Exception as e:
            logger.error(f"Guardian review failed: {e}")
        return False

    async def _learn_pattern(self, failure: SystemFailure) -> bool:
        """Learn from previous fix patterns"""
        pattern_key = f"{failure.type}:{failure.component}"

        if pattern_key in self.fix_patterns:
            # Apply most successful pattern
            patterns = self.fix_patterns[pattern_key]
            best_pattern = max(patterns, key=lambda p: p.get("confidence", 0))

            # Apply the pattern
            # This would involve more complex pattern matching and application
            logger.info(f"Applying learned pattern: {best_pattern}")
            return True

        return False

    def _record_fix_pattern(self, failure: SystemFailure, fix: Any):
        """Record successful fix pattern for learning"""
        pattern_key = f"{failure.type}:{failure.component}"

        if pattern_key not in self.fix_patterns:
            self.fix_patterns[pattern_key] = []

        self.fix_patterns[pattern_key].append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "original": fix.original_code,
                "fixed": fix.fixed_code,
                "confidence": fix.confidence,
                "explanation": fix.explanation,
            }
        )

        # Keep only recent patterns
        if len(self.fix_patterns[pattern_key]) > 10:
            self.fix_patterns[pattern_key] = self.fix_patterns[pattern_key][-10:]

    async def continuous_improvement_loop(
        self,
        scan_interval: int = 3600,  # 1 hour
        max_fixes_per_cycle: int = 50,
    ):
        """Run continuous improvement loop"""
        while True:
            try:
                logger.info("Starting code quality improvement cycle...")

                # Scan for issues
                failures = await self.scan_codebase()

                # Prioritize by severity
                failures.sort(key=lambda f: f.severity, reverse=True)

                # Fix up to max_fixes_per_cycle issues
                fixed_count = 0
                for failure in failures[:max_fixes_per_cycle]:
                    action = await self.heal_failure(failure)
                    if action.success:
                        fixed_count += 1

                logger.info(f"Fixed {fixed_count}/{len(failures)} issues")

                # Save learning data
                if self.learning_enabled:
                    self._save_learning_data()

                # Report metrics
                self._report_metrics()

                # Wait for next cycle
                await asyncio.sleep(scan_interval)

            except Exception as e:
                logger.error(f"Improvement cycle error: {e}")
                await asyncio.sleep(60)  # Short wait on error

    def _save_learning_data(self):
        """Save learning data for persistence"""
        learning_data = {
            "patterns": self.fix_patterns,
            "successful_strategies": self.successful_strategies,
            "metrics": self.metrics.__dict__,
        }

        with open("data/code_quality_learning.json", "w") as f:
            json.dump(learning_data, f, indent=2, default=str)

    def _report_metrics(self):
        """Report current metrics"""
        logger.info(
            f"""
Code Quality Metrics:
- Total Issues: {self.metrics.total_issues}
- Fixed Issues: {self.metrics.fixed_issues}
- Failed Fixes: {self.metrics.failed_fixes}
- Improvement Rate: {self.metrics.improvement_rate:.1%}
- Syntax Errors: {self.metrics.syntax_errors}
- Undefined Names: {self.metrics.undefined_names}
- Formatting Issues: {self.metrics.formatting_issues}
        """
        )

    def get_health_status(self) -> dict[str, Any]:
        """Get current health status"""
        return {
            "healthy": self.metrics.improvement_rate > 0.5,
            "metrics": self.metrics.__dict__,
            "learning_enabled": self.learning_enabled,
            "patterns_learned": len(self.fix_patterns),
            "successful_strategies": len(set(self.successful_strategies)),
        }


async def main():
    """Example usage"""
    healer = CodeQualityHealer(
        workspace_path=".",
        guardian_threshold=0.15,
        auto_fix_threshold=0.85,
        learning_enabled=True,
    )

    # Run a single scan and fix cycle
    failures = await healer.scan_codebase()
    print(f"Found {len(failures)} issues")

    # Fix top 10 issues
    for failure in failures[:10]:
        action = await healer.heal_failure(failure)
        print(f"Fixed {failure.id}: {action.success}")

    # Get health status
    status = healer.get_health_status()
    print(f"Health: {status}")

    # Or run continuous improvement
    # await healer.continuous_improvement_loop()


if __name__ == "__main__":
    asyncio.run(main())
