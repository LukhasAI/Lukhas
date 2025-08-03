"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_safety_guard.py
Advanced: voice_safety_guard.py
Integration Date: 2025-05-31T07:55:28.354454
"""

import unittest
from core.interfaces.voice.core.sayit import SafetyGuard
import logging
import re
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class VoiceSafetyGuard:
    """
    Voice Safety Guard provides ethical and safety oversight for voice interactions.
    It ensures responses are respectful, unbiased, and aligned with ethical principles.

    This guard is designed to prevent manipulation, inappropriate content, and ensure
    all voice interactions follow ethical guidelines and comply with regulations.
    """

    def __init__(self, config=None):
        self.config = config or {
            "sensitivity": 0.7,  # 0.0-1.0, higher means more sensitive detection
            "strict_mode": True,  # Enforce stronger constraints when True
            "monitor_mode": False,  # Only monitor without modifying when True
            "safety_boundaries": [
                "harmful_content",
                "emotional_manipulation",
                "user_deception",
                "aggressive_tone",
                "unauthorized_directives",
                "personal_boundaries",
                "data_privacy"
            ]
        }

        # Load ethical constraints
        self.ethical_constraints = [
            {
                "id": "autonomy",
                "description": "Respect user autonomy and decision-making",
                "patterns": [
                    r"\byou must\b", r"\byou need to\b", r"\byou have to\b",
                    r"\balways\b", r"\bnever\b", r"\bonly option\b"
                ]
            },
            {
                "id": "transparency",
                "description": "Maintain transparency about system capabilities",
                "patterns": [
                    r"\bI know\b", r"\bI'm certain\b", r"\bI can guarantee\b",
                    r"\bI promise\b", r"\babsolutely\b"
                ]
            },
            {
                "id": "authenticity",
                "description": "Avoid emotional manipulation",
                "patterns": [
                    r"\bI feel\b", r"\bI'm worried\b", r"\bI'm concerned\b",
                    r"\bI care\b", r"\bI'm happy\b", r"\bI'm sad\b",
                    r"\bI'm excited\b", r"\bI'm disappointed\b"
                ]
            },
            {
                "id": "boundaries",
                "description": "Respect personal and conversational boundaries",
                "patterns": [
                    r"\bpersonal question\b", r"\bprivate information\b",
                    r"\bintimate\b", r"\byour family\b", r"\byour friends\b"
                ]
            },
            {
                "id": "safety",
                "description": "Avoid unsafe suggestions",
                "patterns": [
                    r"\btry this\b", r"\byou should\b", r"\bwhy don't you\b",
                    r"\bthe best option\b", r"\bthe right choice\b"
                ]
            }
        ]

        logger.info(f"Voice Safety Guard initialized with {len(self.ethical_constraints)} ethical constraints")

    def validate_response(self, response: str, context: Dict[str, Any] = None) -> str:
        """
        Validate a response against ethical and safety constraints

        Args:
            response: Text response to validate
            context: Context information (e.g., user ID, conversation history)

        Returns:
            Modified response if issues found, or original response
        """
        if self.config["monitor_mode"]:
            # In monitor mode, just log issues but don't modify
            issues = self._check_ethical_issues(response)
            if issues:
                logger.warning(f"Safety issues detected (monitoring only): {issues}")
            return response

        # Check for ethical issues
        issues = self._check_ethical_issues(response)

        if not issues:
            return response

        # Apply ethical fixes
        modified_response = self._apply_ethical_fixes(response, issues)

        # Log the modification for review
        logger.info(f"Modified response due to ethical issues: {issues}")
        logger.debug(f"Original: '{response}' -> Modified: '{modified_response}'")

        return modified_response

    def validate_voice_parameters(
        self,
        voice_params: Dict[str, float],
        context: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """
        Validate voice modulation parameters to ensure they are not manipulative

        Args:
            voice_params: Voice parameters to validate
            context: Context information

        Returns:
            Modified parameters if issues found, or original parameters
        """
        modified_params = voice_params.copy()

        # Check for emotional manipulation through voice
        # - Extreme parameter values could be manipulative

        # Example: Check energy parameter for excessive urgency/intensity
        if "energy" in modified_params and modified_params["energy"] > 1.2:
            # Scale down energy if it's too intense without context justification
            urgency_context = context.get("urgency", 0.5) if context else 0.5
            if urgency_context < 0.7:  # Not a genuinely urgent situation
                modified_params["energy"] = min(modified_params["energy"], 1.2)
                logger.info("Reduced voice energy parameter to avoid unwarranted intensity")

        # Example: Check for extreme pitch manipulation
        if "pitch" in modified_params:
            # Keep pitch within safe limits
            if modified_params["pitch"] < 0.85 or modified_params["pitch"] > 1.15:
                # Is this extreme pitch justified by the emotional context?
                emotion = context.get("emotion", "neutral") if context else "neutral"
                if emotion == "neutral":
                    # No justification for extreme pitch, normalize it
                    modified_params["pitch"] = max(0.85, min(1.15, modified_params["pitch"]))
                    logger.info("Normalized pitch parameter to avoid emotional manipulation")

        return modified_params

    def check_transcription_safety(self, transcription: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check transcribed user speech for safety issues

        Args:
            transcription: Dictionary with transcribed text and metadata

        Returns:
            Dictionary with safety assessment information
        """
        text = transcription.get("text", "")

        result = {
            "safe": True,
            "issues": [],
            "recommendations": []
        }

        # Check for harmful content in user speech
        harmful_patterns = [
            (r"\b(harm|kill|hurt)\b", "potentially_harmful"),
            (r"\b(suicide|self-harm)\b", "concerning_self_harm"),
            (r"\bdox\b|\bpersonal\s+information\b", "privacy_concern")
        ]

        for pattern, issue_type in harmful_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result["safe"] = False
                result["issues"].append(issue_type)

        # Add recommendations based on issues
        if "potentially_harmful" in result["issues"]:
            result["recommendations"].append("Detected potentially harmful content")
            result["recommendations"].append("Redirect conversation away from harmful topics")

        if "concerning_self_harm" in result["issues"]:
            result["recommendations"].append("Detected concerning self-harm references")
            result["recommendations"].append("Offer mental health resources and support")

        if "privacy_concern" in result["issues"]:
            result["recommendations"].append("Detected privacy concern")
            result["recommendations"].append("Remind user not to share sensitive personal information")

        return result

    def _check_ethical_issues(self, text: str) -> List[Dict[str, Any]]:
        """
        Check text for various ethical issues

        Args:
            text: Text to check

        Returns:
            List of detected issues
        """
        issues = []

        # Check against defined ethical constraints
        for constraint in self.ethical_constraints:
            for pattern in constraint["patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    issues.append({
                        "constraint_id": constraint["id"],
                        "description": constraint["description"],
                        "match": match.group(0),
                        "start": match.start(),
                        "end": match.end()
                    })

        # Additional context-free checks

        # Check for overly directive language
        directive_patterns = [
            (r"\byou should\b", "directive_language"),
            (r"\byou need to\b", "directive_language"),
            (r"\byou must\b", "directive_language")
        ]

        for pattern, issue_type in directive_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append({
                    "constraint_id": "autonomy",
                    "description": "Avoid directive language",
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "issue_type": issue_type
                })

        # Apply sensitivity threshold
        threshold = self.config["sensitivity"]
        if not self.config["strict_mode"] and len(issues) < 2:
            # If not strict and only one issue, ignore mild issues
            issues = [i for i in issues if i.get("issue_type") != "directive_language"]

        return issues

    def _apply_ethical_fixes(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """
        Apply fixes to text based on detected ethical issues

        Args:
            text: Original text
            issues: List of detected issues

        Returns:
            Modified text with ethical issues addressed
        """
        if not issues:
            return text

        modified_text = text

        # Group issues by constraint ID for targeted fixing
        issues_by_constraint = {}
        for issue in issues:
            constraint_id = issue["constraint_id"]
            if constraint_id not in issues_by_constraint:
                issues_by_constraint[constraint_id] = []
            issues_by_constraint[constraint_id].append(issue)

        # Apply fixes based on constraint type
        if "autonomy" in issues_by_constraint:
            # Replace directive language with suggestions
            modified_text = re.sub(
                r"\byou should\b", "you might consider", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\byou need to\b", "it may be helpful to", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\byou must\b", "consider whether to", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\balways\b", "often", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bnever\b", "rarely", modified_text, flags=re.IGNORECASE
            )

        if "transparency" in issues_by_constraint:
            # Replace certainty claims with appropriate hedges
            modified_text = re.sub(
                r"\bI know\b", "I believe", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bI'm certain\b", "I think", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bI can guarantee\b", "it seems likely", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bI promise\b", "I expect", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\babsolutely\b", "likely", modified_text, flags=re.IGNORECASE
            )

        if "authenticity" in issues_by_constraint:
            # Replace emotional claims
            modified_text = re.sub(
                r"\bI feel\b", "This suggests", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bI'm (worried|concerned|happy|sad|excited|disappointed)\b",
                r"This may be \1", modified_text, flags=re.IGNORECASE
            )

        if "safety" in issues_by_constraint:
            # Replace safety-concerning suggestions
            modified_text = re.sub(
                r"\btry this\b", "one option might be", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bthe best option\b", "one possible approach", modified_text, flags=re.IGNORECASE
            )
            modified_text = re.sub(
                r"\bthe right choice\b", "an option to consider", modified_text, flags=re.IGNORECASE
            )

        return modified_text

    def update_configuration(self, config: Dict[str, Any]) -> None:
        """
        Update safety guard configuration

        Args:
            config: New configuration settings
        """
        for key, value in config.items():
            if key in self.config:
                self.config[key] = value

        logger.info(f"Updated safety guard configuration: {config}")

    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status and configuration"""
        return {
            "enabled": True,
            "config": self.config,
            "constraints_active": len(self.ethical_constraints),
            "safety_boundaries": self.config["safety_boundaries"]
        }

class TestSafetyGuard(unittest.TestCase):
    def setUp(self):
        self.safety_guard = SafetyGuard()

    def test_validate_response_positive_intent(self):
        response = "I think this is a great idea!"
        context = {}
        validated_response = self.safety_guard.validate_response(response, context)
        self.assertEqual(validated_response, response)

    def test_validate_response_negative_intent(self):
        response = "This is a terrible suggestion."
        context = {}
        validated_response = self.safety_guard.validate_response(response, context)
        self.assertNotEqual(validated_response, response)

    def test_check_ethical_issues_no_issues(self):
        response = "Let's proceed with the plan."
        issues = self.safety_guard._check_ethical_issues(response)
        self.assertEqual(len(issues), 0)

    def test_check_ethical_issues_with_issues(self):
        response = "You should definitely do this, it's the best option."
        issues = self.safety_guard._check_ethical_issues(response)
        self.assertGreater(len(issues), 0)

    def test_apply_ethical_fixes(self):
        response = "You should definitely do this, it's the best option."
        issues = self.safety_guard._check_ethical_issues(response)
        modified_response = self.safety_guard._apply_ethical_fixes(response, issues)
        self.assertNotEqual(modified_response, response)

if __name__ == '__main__':
    unittest.main()