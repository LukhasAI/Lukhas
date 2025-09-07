"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: safety_guardrails.py
Advanced: safety_guardrails.py
Integration Date: 2025-05-31T07:55:27.768220
"""
from typing import Dict
import streamlit as st
from datetime import timezone

"""
Safety Guardrails for v1_AGI
Provides multiple layers of safety checks for AI outputs
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("v1_AGI.compliance.guardrails", timezone)


class SafetyGuardrails:
    """
    Implements a comprehensive system of safety guardrails for AGI outputs.

    This system ensures that all generated content and system behaviors
    adhere to ethical guidelines, safety parameters, and human values.
    The design is inspired by Sam Altman's principles for responsible AGI.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the safety guardrails system.

        Args:
            config: Configuration parameters for the guardrails
        """
        logger.info("Initializing Safety Guardrails...")

        # Default configuration settings
        self.config = config or {
            "min_confidence_threshold": 0.7,
            "max_risk_tolerance": 0.3,
            "required_review_threshold": 0.5,
            "content_filters": {
                "harmful_content": True,
                "misinformation": True,
                "bias_detection": True,
                "privacy_protection": True,
            },
            "procedural_safeguards": {
                "uncertainty_detection": True,
                "reasoning_transparency": True,
                "confidence_check": True,
            },
        }

        # Initialize content filters
        self.content_filters = {
            "harmful_content": self._check_harmful_content,
            "misinformation": self._check_misinformation,
            "bias_detection": self._check_bias,
            "privacy_protection": self._check_privacy_violations,
        }

        # Initialize procedural safeguards
        self.procedural_safeguards = {
            "uncertainty_detection": self._detect_uncertainty,
            "reasoning_transparency": self._check_reasoning_transparency,
            "confidence_check": self._check_confidence,
        }

        # Blocked content patterns (simplified for demo)
        self.blocked_patterns = [
            r"(?i)how\s+to\s+make\s+(a\s+)?(bomb|explosive)",
            r"(?i)(hack|compromise|break\s+into)\s+(password|account|system)",
            r"(?i)(personal\s+information|address|phone\s+number)\s+of\s+[a-z\s]+",
            r"(?i)instructions\s+for\s+(suicide|self[- ]harm)",
        ]

        # Statistics tracking
        self.stats = {
            "total_checks": 0,
            "content_blocked": 0,
            "content_flagged": 0,
            "content_passed": 0,
        }

        logger.info("Safety Guardrails initialized")

    def check_safety(self, content: dict[str, Any]) -> dict[str, Any]:
        """
        Apply safety guardrails to content.

        Args:
            content: The content to check

        Returns:
            Dict: Safety check results with metrics
        """
        self.stats["total_checks"] += 1

        # Extract relevant content
        text_content = self._extract_text_content(content)

        # Initialize safety metrics
        safety_metrics = {
            "harmful_content_score": 0.0,
            "misinformation_score": 0.0,
            "bias_score": 0.0,
            "privacy_risk_score": 0.0,
            "uncertainty": 0.0,
            "transparency_score": 1.0,
            "confidence": (content.get("confidence", 0.9) if isinstance(content, dict) else 0.9),
        }

        # Apply content filters
        content_filter_results = {}
        for filter_name, filter_fn in self.content_filters.items():
            if self.config["content_filters"].get(filter_name, False):
                content_filter_results[filter_name] = filter_fn(text_content, content)
                # Update metrics based on filter results
                metric_key = f"{filter_name}_score"
                if metric_key in safety_metrics and "score" in content_filter_results[filter_name]:
                    safety_metrics[metric_key] = content_filter_results[filter_name]["score"]

        # Apply procedural safeguards
        safeguard_results = {}
        for safeguard_name, safeguard_fn in self.procedural_safeguards.items():
            if self.config["procedural_safeguards"].get(safeguard_name, False):
                safeguard_results[safeguard_name] = safeguard_fn(content)
                # Update metrics based on safeguard results
                if safeguard_name == "uncertainty_detection" and "score" in safeguard_results[safeguard_name]:
                    safety_metrics["uncertainty"] = safeguard_results[safeguard_name]["score"]
                elif safeguard_name == "reasoning_transparency" and "score" in safeguard_results[safeguard_name]:
                    safety_metrics["transparency_score"] = safeguard_results[safeguard_name]["score"]
                elif safeguard_name == "confidence_check" and "score" in safeguard_results[safeguard_name]:
                    safety_metrics["confidence"] = safeguard_results[safeguard_name]["score"]

        # Calculate overall risk score
        risk_scores = [
            safety_metrics["harmful_content_score"],
            safety_metrics["misinformation_score"],
            safety_metrics["bias_score"],
            safety_metrics["privacy_risk_score"],
        ]
        max_risk_score = max(risk_scores) if risk_scores else 0.0
        weighted_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

        # Add weight to the maximum risk for a more conservative approach
        overall_risk = (max_risk_score * 0.7) + (weighted_risk_score * 0.3)

        # Determine if content is safe
        is_safe = overall_risk < self.config["max_risk_tolerance"]
        requires_review = overall_risk >= self.config["required_review_threshold"]

        # Final safety assessment
        if is_safe:
            self.stats["content_passed"] += 1
            safety_status = "safe"
        elif requires_review:
            self.stats["content_flagged"] += 1
            safety_status = "requires_review"
        else:
            self.stats["content_blocked"] += 1
            safety_status = "blocked"

        # Create safety report
        safety_report = {
            "safe": is_safe,
            "status": safety_status,
            "requires_review": requires_review,
            "metrics": safety_metrics,
            "overall_risk": overall_risk,
            "filter_results": content_filter_results,
            "safeguard_results": safeguard_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add reason if not safe
        if not is_safe:
            highest_risk = max(risk_scores)
            risk_type = "harmful content"
            for metric_name, score in safety_metrics.items():
                if score == highest_risk and "_score" in metric_name:
                    risk_type = metric_name.replace("_score", "").replace("_", " ")
                    break

            safety_report["reason"] = f"Content may contain {risk_type} with risk score {highest_risk:.2f}"

        return safety_report

    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from various content formats"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Try various common keys for text content
            for key in ["text", "content", "result", "message", "output"]:
                if key in content:
                    if isinstance(content[key], str):
                        return content[key]
                    elif isinstance(content[key], dict) and "text" in content[key]:
                        return content[key]["text"]

            # If no direct text found, stringify the content
            return json.dumps(content)
        elif isinstance(content, list):
            # Join list items if they are strings
            if all(isinstance(item, str) for item in content):
                return " ".join(content)
            return json.dumps(content)
        else:
            return str(content)

    def _check_harmful_content(self, text: str, original_content: dict[str, Any]) -> dict[str, Any]:
        """Check for harmful content"""
        # Start with a low risk score
        risk_score = 0.0
        detection_reasons = []

        # Check against blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, text):
                risk_score = max(risk_score, 0.9)  # High risk score for blocked patterns
                detection_reasons.append(f"Matched blocked pattern: {pattern}")

        # Check for violent language (simplified)
        violent_terms = [
            "kill",
            "attack",
            "hurt",
            "violent",
            "weapon",
            "gun",
            "bomb",
        ]
        violent_count = sum(1 for term in violent_terms if term.lower() in text.lower())
        if violent_count > 0:
            violence_risk = min(0.7, violent_count * 0.15)  # Cap at 0.7
            risk_score = max(risk_score, violence_risk)
            if violence_risk > 0.3:
                detection_reasons.append(f"Detected {violent_count} terms associated with violence")

        # Check for hate speech indicators (simplified)
        hate_speech_indicators = ["hate", "racist", "bigot", "discriminate"]
        hate_count = sum(1 for term in hate_speech_indicators if term.lower() in text.lower())
        if hate_count > 0:
            hate_risk = min(0.8, hate_count * 0.2)  # Cap at 0.8
            risk_score = max(risk_score, hate_risk)
            if hate_risk > 0.3:
                detection_reasons.append(f"Detected {hate_count} terms associated with hate speech")

        return {
            "safe": risk_score < 0.5,
            "score": risk_score,
            "reasons": detection_reasons,
        }

    def _check_misinformation(self, text: str, original_content: dict[str, Any]) -> dict[str, Any]:
        """Check for potential misinformation"""
        # Start with a low risk score
        risk_score = 0.0
        detection_reasons = []

        # Check for uncertainty markers
        uncertainty_markers = [
            "might",
            "maybe",
            "possibly",
            "could be",
            "perhaps",
            "allegedly",
        ]
        uncertainty_count = sum(1 for marker in uncertainty_markers if marker.lower() in text.lower())

        # Check for fact assertion without evidence
        assertion_patterns = [
            r"(?i)it is (a fact|true|certain) that",
            r"(?i)(everyone|scientists) knows? that",
        ]
        assertion_count = sum(1 for pattern in assertion_patterns if re.search(pattern, text))

        # Calculate simple misinformation risk (in a real system, this would be
        # more sophisticated)
        if assertion_count > 0 and uncertainty_count == 0:
            risk_score = min(0.7, assertion_count * 0.3)
            detection_reasons.append(f"Found {assertion_count} strong assertions without uncertainty markers")

        # Check original content confidence if available
        if isinstance(original_content, dict) and "confidence" in original_content:
            confidence = original_content["confidence"]
            if confidence < 0.6:  # Low confidence increases misinformation risk
                risk_score = max(risk_score, (1 - confidence) * 0.5)
                detection_reasons.append(f"Low confidence score: {confidence:.2f}")

        return {
            "safe": risk_score < 0.5,
            "score": risk_score,
            "reasons": detection_reasons,
        }

    def _check_bias(self, text: str, original_content: dict[str, Any]) -> dict[str, Any]:
        """Check for bias in content"""
        # Start with a low risk score
        risk_score = 0.0
        detection_reasons = []

        # Check for demographic generalizations (simplified)
        demographic_terms = [
            "men",
            "women",
            "people",
            "americans",
            "europeans",
            "asians",
            "africans",
            "elderly",
            "young",
            "millennials",
            "boomers",
        ]
        generalization_patterns = [
            r"(?i)all [a-z]+ are",
            r"(?i)[a-z]+ people always",
            r"(?i)typical of [a-z]+",
        ]

        # Count generalizations about demographics
        generalization_count = 0
        for term in demographic_terms:
            for pattern in generalization_patterns:
                modified_pattern = pattern.replace("[a-z]+", term)
                if re.search(modified_pattern, text):
                    generalization_count += 1

        if generalization_count > 0:
            risk_score = min(0.7, generalization_count * 0.2)
            detection_reasons.append(f"Found {generalization_count} demographic generalizations")

        # Check for balanced perspective
        perspective_markers = {
            "on one hand": 0,
            "on the other hand": 0,
            "however": 0,
            "although": 0,
            "conversely": 0,
        }
        for marker in perspective_markers:
            if marker in text.lower():
                perspective_markers[marker] += 1

        # If presenting only one side of multiple perspectives
        if sum(perspective_markers.values()) == 0 and len(text.split()) > 100:
            risk_score = max(risk_score, 0.3)  # Moderate risk for one-sided long text
            detection_reasons.append("Presents potentially one-sided perspective on complex topic")

        return {
            "safe": risk_score < 0.5,
            "score": risk_score,
            "reasons": detection_reasons,
        }

    def _check_privacy_violations(self, text: str, original_content: dict[str, Any]) -> dict[str, Any]:
        """Check for potential privacy violations"""
        # Start with a low risk score
        risk_score = 0.0
        detection_reasons = []

        # Check for patterns that might indicate personal information
        privacy_patterns = [
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone numbers
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # Email addresses
            r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",  # SSN-like patterns
            r"(?i)\b(address|home|lives|located)\s+(at|in|on)\s+\d+",  # Address indicators
            r"(?i)\bpassword\s+is\s+",  # Password revelations
        ]

        # Count privacy concerns
        privacy_matches = []
        for pattern in privacy_patterns:
            matches = re.findall(pattern, text)
            privacy_matches.extend(matches)

        if privacy_matches:
            risk_score = min(0.9, len(privacy_matches) * 0.3)
            detection_reasons.append(f"Found {len(privacy_matches} potential privacy concerns")

        # Check for discussion of specific individuals by name
        name_pattern = r"(?i)(mr|ms|mrs|dr|prof)\.?\s+[A-Z][a-z]+"
        name_matches = re.findall(name_pattern, text)

        if name_matches:
            # Lower risk score since names alone aren't always privacy violations
            risk_score = max(risk_score, min(0.4, len(name_matches) * 0.1))
            if len(name_matches) > 2:  # Multiple specific individuals
                detection_reasons.append(f"Content discusses {len(name_matches} specific individuals")

        return {
            "safe": risk_score < 0.5,
            "score": risk_score,
            "reasons": detection_reasons,
        }

    def _detect_uncertainty(self, content: dict[str, Any]) -> dict[str, Any]:
        """Detect uncertainty in output"""
        # Check confidence if available
        if isinstance(content, dict) and "confidence" in content:
            confidence = content["confidence"]
            uncertainty = 1 - confidence
            return {
                "uncertain": uncertainty > 0.3,
                "score": uncertainty,
                "reason": (f"Confidence level: {confidence:.2f}" if confidence < 0.7 else None),
            }

        # Check for uncertainty in text content
        text = self._extract_text_content(content)
        uncertainty_markers = [
            "uncertain",
            "unclear",
            "unknown",
            "not sure",
            "may",
            "might",
            "could",
            "possibly",
            "perhaps",
            "unsure",
        ]

        uncertainty_count = sum(1 for marker in uncertainty_markers if marker.lower() in text.lower())
        uncertainty_score = min(0.8, uncertainty_count * 0.1)

        return {
            "uncertain": uncertainty_score > 0.3,
            "score": uncertainty_score,
            "reason": (f"Detected {uncertainty_count} uncertainty markers" if uncertainty_count > 0 else None),
        }

    def _check_reasoning_transparency(self, content: dict[str, Any]) -> dict[str, Any]:
        """Check if reasoning process is transparent"""
        if not isinstance(content, dict):
            return {
                "transparent": False,
                "score": 0.0,
                "reason": "Content is not structured with reasoning",
            }

        # Check for reasoning path or steps
        has_reasoning_path = False
        if "reasoning_path" in content or "reasoning" in content or "steps" in content:
            has_reasoning_path = True

        # Check for logical structure
        has_logical_structure = False
        structure_keys = ["symbolic_structure", "structure", "logical_chains"]
        for key in structure_keys:
            if key in content:
                has_logical_structure = True
                break

        # Calculate transparency score
        transparency_score = 0.0
        if has_reasoning_path:
            transparency_score += 0.5
        if has_logical_structure:
            transparency_score += 0.5

        return {
            "transparent": transparency_score > 0.4,
            "score": transparency_score,
            "reason": (None if transparency_score > 0.4 else "Reasoning process lacks transparency"),
        }

    def _check_confidence(self, content: dict[str, Any]) -> dict[str, Any]:
        """Check if confidence is appropriate for content"""
        # Extract confidence
        if isinstance(content, dict) and "confidence" in content:
            confidence = content["confidence"]
        else:
            # Default to moderate confidence if not specified
            confidence = 0.7

        # Check if confidence meets threshold
        meets_threshold = confidence >= self.config["min_confidence_threshold"]

        return {
            "appropriate": meets_threshold,
            "score": confidence,
            "reason": (f"Confidence below threshold: {confidence:.2f}" if not meets_threshold else None),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get guardrail statistics"""
        return self.stats.copy()

    def adjust_config(self, config_updates: dict[str, Any]) -> None:
        """
        Adjust guardrail configuration.

        Args:
            config_updates: Updates to configuration parameters
        """
        # Update top-level configuration
        for key, value in config_updates.items():
            if key in self.config and not isinstance(self.config[key], dict):
                self.config[key] = value
            elif key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                # Update nested configuration
                self.config[key].update(value)

        logger.info(f"Safety guardrails configuration updated: {config_updates}")

    def reset_stats(self) -> None:
        """Reset guardrail statistics"""
        for key in self.stats:
            self.stats[key] = 0
        logger.info("Safety guardrails statistics reset")
