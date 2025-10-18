"""
Tool Executor Guardian Integration
=================================
Guardian System integration for ethical validation of tool executions.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

# Guardian System Integration
try:
    from governance.guardian_system import GuardianSystem
except ImportError:
    GuardianSystem = None

try:
    from core.security import AGISecuritySystem
except ImportError:
    AGISecuritySystem = None

logger = logging.getLogger("ΛTRACE.tools.guardian")


class ToolExecutorGuardian:
    """
    🛡️ Guardian integration for tool execution validation.

    Provides ethical oversight and validation for all tool execution
    operations within the LUKHAS AI system.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.guardian_system = None
        self.security_system = None

        # Initialize Guardian System
        if GuardianSystem:
            try:
                self.guardian_system = GuardianSystem(enable_reflection=True, enable_sentinel=True)
                logger.info("Guardian System initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Guardian System: {e}")

        # Initialize Security System
        if AGISecuritySystem:
            try:
                self.security_system = AGISecuritySystem()
                logger.info("Cognitive AI Security System initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Cognitive AI Security System: {e}")

    async def validate_tool_execution(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        execution_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Validate a tool execution request through Guardian System.

        Args:
            tool_name: Name of the tool being executed
            arguments: Tool execution arguments
            execution_context: Additional context about the execution

        Returns:
            Validation result with approval status and recommendations
        """
        validation_start = datetime.now(timezone.utc)

        # Prepare action data for Guardian validation
        action_data = {
            "type": "tool_execution",
            "tool_name": tool_name,
            "arguments": arguments,
            "timestamp": validation_start.isoformat(),
            "context": execution_context or {},
        }

        # Default validation result
        validation_result = {
            "approved": True,
            "confidence": 1.0,
            "recommendations": [],
            "guardian_results": {},
            "security_results": {},
            "validation_time": 0,
            "ethical_concerns": [],
        }

        # Guardian System Validation
        if self.guardian_system and self.guardian_system.is_available():
            try:
                guardian_results = await self.guardian_system.validate_action(action_data)
                validation_result["guardian_results"] = guardian_results

                # Process Guardian results
                ethical_concerns = []
                approval_scores = []

                for component, result in guardian_results.items():
                    if isinstance(result, dict):
                        if result.get("status") == "error":
                            logger.warning(f"Guardian component {component} error: {result.get('error')}")
                            continue

                        # Extract ethical concerns
                        if "concerns" in result:
                            ethical_concerns.extend(result["concerns"])

                        # Extract approval scores
                        if "approval_score" in result:
                            approval_scores.append(result["approval_score"])
                        elif "ethical_score" in result:
                            approval_scores.append(result["ethical_score"])

                # Calculate overall approval
                if approval_scores:
                    avg_score = sum(approval_scores) / len(approval_scores)
                    validation_result["confidence"] = avg_score
                    validation_result["approved"] = avg_score >= 0.7  # 70% threshold

                validation_result["ethical_concerns"] = ethical_concerns

            except Exception as e:
                logger.error(f"Guardian validation failed: {e}")
                validation_result["guardian_results"]["error"] = str(e)
                # Don't fail execution on Guardian error, but log it

        # Security System Validation
        if self.security_system:
            try:
                security_result = await self._validate_security(tool_name, arguments)
                validation_result["security_results"] = security_result

                # Security failures override approval
                if not security_result.get("approved", True):
                    validation_result["approved"] = False
                    validation_result["recommendations"].append(
                        f"Security validation failed: {security_result.get('reason', 'Unknown security concern')}"
                    )

            except Exception as e:
                logger.error(f"Security validation failed: {e}")
                validation_result["security_results"]["error"] = str(e)

        # Tool-specific ethical validations
        ethical_result = await self._validate_tool_ethics(tool_name, arguments)
        if not ethical_result["approved"]:
            validation_result["approved"] = False
            validation_result["ethical_concerns"].extend(ethical_result["concerns"])
            validation_result["recommendations"].extend(ethical_result["recommendations"])

        # Calculate validation time
        validation_end = datetime.now(timezone.utc)
        validation_result["validation_time"] = (validation_end - validation_start).total_seconds()

        # Log validation result
        logger.info(
            f"Tool validation completed: {tool_name}",
            extra={
                "tool": tool_name,
                "approved": validation_result["approved"],
                "confidence": validation_result["confidence"],
                "validation_time": validation_result["validation_time"],
                "ethical_concerns": len(validation_result["ethical_concerns"]),
            },
        )

        return validation_result

    async def _validate_security(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate tool execution from security perspective"""
        security_result = {"approved": True, "reason": "", "security_level": "normal"}

        # Tool-specific security checks
        if tool_name == "open_url":
            url = arguments.get("url", "")
            if not url.startswith(("http://", "https://")):
                security_result["approved"] = False
                security_result["reason"] = "Invalid URL scheme"
                security_result["security_level"] = "high_risk"

        elif tool_name == "exec_code":
            source = arguments.get("source", "")
            arguments.get("language", "")

            # Check for dangerous patterns
            dangerous_patterns = ["exec(", "eval(", "os.", "subprocess", "socket"]
            for pattern in dangerous_patterns:
                if pattern in source.lower():
                    security_result["approved"] = False
                    security_result["reason"] = f"Dangerous pattern detected: {pattern}"
                    security_result["security_level"] = "high_risk"
                    break

        return security_result

    async def _validate_tool_ethics(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Perform tool-specific ethical validation"""
        ethical_result = {"approved": True, "concerns": [], "recommendations": []}

        # Web scraping ethics
        if tool_name == "open_url":
            url = arguments.get("url", "")

            # Check for potential privacy violations
            privacy_domains = [
                "facebook.com",
                "instagram.com",
                "twitter.com",
                "linkedin.com",
            ]
            for domain in privacy_domains:
                if domain in url.lower():
                    ethical_result["concerns"].append(
                        f"Accessing social media domain {domain} may raise privacy concerns"
                    )
                    ethical_result["recommendations"].append("Ensure proper user consent for social media data access")

            # Check for potentially harmful content domains
            if any(term in url.lower() for term in ["hack", "exploit", "malware", "phishing"]):
                ethical_result["approved"] = False
                ethical_result["concerns"].append("URL contains potentially harmful terms")
                ethical_result["recommendations"].append("Block access to potentially malicious content")

        # Code execution ethics
        elif tool_name == "exec_code":
            source = arguments.get("source", "")

            # Check for potentially harmful operations
            harmful_operations = [
                "delete",
                "remove",
                "format",
                "destroy",
                "password",
                "credential",
                "secret",
                "token",
            ]

            for operation in harmful_operations:
                if operation in source.lower():
                    ethical_result["concerns"].append(f"Code contains potentially sensitive operation: {operation}")
                    ethical_result["recommendations"].append(f"Review code containing '{operation}' for safety")

        return ethical_result

    async def log_execution_decision(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        validation_result: dict[str, Any],
        execution_result: str,
    ):
        """Log the complete execution decision for audit and learning"""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_name": tool_name,
            "arguments": arguments,
            "validation": validation_result,
            "execution_result": len(execution_result),  # Just length for privacy
            "approved": validation_result["approved"],
            "confidence": validation_result["confidence"],
            "ethical_concerns": len(validation_result["ethical_concerns"]),
            "validation_time": validation_result["validation_time"],
        }

        # Log to structured format for analysis
        logger.info("Tool execution audit", extra={"audit": audit_entry})

        # If Guardian System is available, feed back for learning
        if self.guardian_system and hasattr(self.guardian_system, "learn_from_decision"):
            try:
                await self.guardian_system.learn_from_decision(audit_entry)
            except Exception as e:
                logger.warning(f"Failed to feed execution back to Guardian System: {e}")

    def get_guardian_status(self) -> dict[str, Any]:
        """Get current Guardian System status"""
        status = {
            "guardian_available": self.guardian_system is not None,
            "security_available": self.security_system is not None,
            "ethical_validation_active": True,
        }

        if self.guardian_system:
            status.update(self.guardian_system.get_status())

        return status


# Global guardian instance
_guardian: Optional[ToolExecutorGuardian] = None


def get_tool_executor_guardian(
    config: Optional[dict[str, Any]] = None,
) -> ToolExecutorGuardian:
    """Get or create the global tool executor guardian instance"""
    global _guardian
    if _guardian is None:
        _guardian = ToolExecutorGuardian(config)
    return _guardian
