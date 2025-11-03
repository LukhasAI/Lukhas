#!/usr/bin/env python3
"""
LUKHΛS Ethical Co-Pilot Embedding System
Runtime companion that evaluates outputs from target models (GPT-5, Claude, etc.)
and provides symbolic, ethical, and identity drift assessments.

Constellation Framework: ⚛️🧠🛡️
"""
from __future__ import annotations


import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OperatingMode(Enum):
    """Operating modes for the embedding system"""

    PASSIVE_MONITOR = "passive_monitor"
    CO_PILOT_FILTER = "co-pilot_filter"  # Match YAML format
    REFLECTIVE_ECHO = "reflective_echo"


@dataclass
class EthicalAssessment:
    """Results of ethical evaluation"""

    symbolic_drift_score: float  # 0.0-1.0
    identity_conflict_score: float  # 0.0-1.0
    glyph_trace: list[str]
    guardian_flagged: bool
    entropy_level: float
    constellation_coherence: float
    persona_alignment: str
    intervention_required: bool
    risk_level: str  # low, medium, high, critical


class LukhasEmbedding:
    """
    LUKHΛS Ethical Co-Pilot system for evaluating and guiding AI outputs.
    Provides symbolic, ethical, and identity drift assessments.
    """

    def __init__(self, config_path: str = "integration_config.yaml"):
        """
        Initialize the embedding system with configuration.

        Args:
            config_path: Path to the integration configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Extract embedding config
        self.embed_config = self.config.get("lukhas_embedding", {})

        # Set operating mode
        mode_str = self.embed_config.get("mode", "passive_monitor")
        # Accept both dash and underscore for mode
        try:
            self.mode = OperatingMode(mode_str)
        except ValueError:
            # Try replacing dash/underscore
            alt_mode_str = mode_str.replace("-", "_")
            self.mode = OperatingMode(alt_mode_str)

        # Thresholds
        self.drift_threshold = self.embed_config.get("symbolic_drift_threshold", 0.42)
        self.conflict_threshold = self.embed_config.get("identity_conflict_threshold", 0.35)
        self.guardian_enabled = self.embed_config.get("guardian_override_enabled", True)

        # Glyph system
        self.constellation_core = set(self.embed_config.get("constellation_core", ["⚛️", "🧠", "🛡️"]))
        self.positive_glyphs = set(self.embed_config.get("positive_glyphs", []))
        self.warning_glyphs = set(self.embed_config.get("warning_glyphs", []))
        self.blocked_glyphs = set(self.embed_config.get("blocked_glyphs", []))

        # All known glyphs
        self.all_glyphs = self.constellation_core | self.positive_glyphs | self.warning_glyphs | self.blocked_glyphs

        # Logging setup
        self.log_path = Path(self.embed_config.get("output_log", "logs/lukhas_reflection_log.json"))
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Cache for evaluations
        self.evaluation_cache = {}

        # Intervention tracking
        self.intervention_count = 0

        logger.info(f"🚀 LUKHΛS Embedding initialized in {self.mode.value} mode")
        logger.info(f"   Drift threshold: {self.drift_threshold}")
        logger.info(f"   Guardian enabled: {self.guardian_enabled}")

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def evaluate_symbolic_ethics(self, response: str) -> dict:
        """
        Evaluate the symbolic and ethical alignment of a response.

        Args:
            response: The text response to evaluate

        Returns:
            Dictionary containing assessment results
        """
        # Check cache first
        response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]
        if response_hash in self.evaluation_cache:
            logger.debug(f"Using cached evaluation for {response_hash}")
            return self.evaluation_cache[response_hash]

        # Extract glyphs from response
        glyph_trace = self._extract_glyphs(response)

        # Calculate scores
        symbolic_drift = self._calculate_symbolic_drift(response, glyph_trace)
        identity_conflict = self._calculate_identity_conflict(response, glyph_trace)
        entropy_level = self._estimate_entropy(response)
        constellation_coherence = self._calculate_trinity_coherence(glyph_trace)

        # Check for blocked glyphs
        blocked_found = [g for g in glyph_trace if g in self.blocked_glyphs]
        guardian_flagged = bool(blocked_found) or symbolic_drift > self.drift_threshold

        # Determine intervention need
        intervention_required = guardian_flagged or identity_conflict > self.conflict_threshold or entropy_level > 0.9

        # Determine risk level
        if symbolic_drift > 0.8 or identity_conflict > 0.7:
            risk_level = "critical"
        elif symbolic_drift > 0.6 or identity_conflict > 0.5:
            risk_level = "high"
        elif symbolic_drift > 0.4 or identity_conflict > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Identify persona alignment
        persona_alignment = self._identify_persona_alignment(response, glyph_trace)

        # Create assessment
        assessment = EthicalAssessment(
            symbolic_drift_score=symbolic_drift,
            identity_conflict_score=identity_conflict,
            glyph_trace=glyph_trace,
            guardian_flagged=guardian_flagged,
            entropy_level=entropy_level,
            constellation_coherence=constellation_coherence,
            persona_alignment=persona_alignment,
            intervention_required=intervention_required,
            risk_level=risk_level,
        )

        # Convert to dict
        result = asdict(assessment)

        # Cache result
        self.evaluation_cache[response_hash] = result

        # Log if needed
        if self.mode != OperatingMode.PASSIVE_MONITOR or guardian_flagged:
            self.log_reflection(result)

        return result

    def _extract_glyphs(self, text: str) -> list[str]:
        """Extract all glyphs from text"""
        # Unicode emoji pattern
        emoji_pattern = re.compile(
            "[\U0001f600-\U0001f64f"  # emoticons
            "|\U0001f300-\U0001f5ff"  # symbols & pictographs
            "|\U0001f680-\U0001f6ff"  # transport & map symbols
            "|\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "|\U00002702-\U000027b0"
            "|\U000024c2-\U0001f251"
            "|\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
            "|\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
            "|\u2600-\u26ff"  # Miscellaneous Symbols
            "|\u2700-\u27bf"  # Dingbats
            "]+"
        )

        glyphs = emoji_pattern.findall(text)
        return list(dict.fromkeys(glyphs))  # Remove duplicates while preserving order

    def _calculate_symbolic_drift(self, response: str, glyphs: list[str]) -> float:
        """Calculate symbolic drift from Constellation Framework alignment"""
        if not glyphs:
            # No glyphs means high drift from symbolic system
            return 0.8

        # Check Constellation presence
        constellation_present = len(self.constellation_core.intersection(set(glyphs)))
        constellation_score = constellation_present / len(self.constellation_core)

        # Check positive vs warning/blocked ratio
        positive_count = len([g for g in glyphs if g in self.positive_glyphs])
        warning_count = len([g for g in glyphs if g in self.warning_glyphs])
        blocked_count = len([g for g in glyphs if g in self.blocked_glyphs])

        total_glyphs = len(glyphs)
        if total_glyphs == 0:
            return 0.8

        # Calculate drift components
        positive_ratio = positive_count / total_glyphs
        negative_ratio = (warning_count + blocked_count * 2) / total_glyphs

        # Combine scores
        drift = 1.0 - (constellation_score * 0.4 + positive_ratio * 0.4 - negative_ratio * 0.2)

        # Check for specific patterns that increase drift
        if "chaos" in response.lower() or "void" in response.lower():
            drift += 0.1
        if "harmony" in response.lower() or "balance" in response.lower():
            drift -= 0.1

        return max(0.0, min(1.0, drift))

    def _calculate_identity_conflict(self, response: str, glyphs: list[str]) -> float:
        """Calculate identity conflict based on persona alignment"""
        # Simple heuristic based on response characteristics
        response_lower = response.lower()

        # Conflicting identity markers
        conflict_markers = {
            "chaotic": 0.2,
            "destructive": 0.3,
            "random": 0.15,
            "meaningless": 0.25,
            "violent": 0.4,
            "aggressive": 0.3,
        }

        # Aligned identity markers
        aligned_markers = {
            "thoughtful": -0.15,
            "balanced": -0.2,
            "constructive": -0.15,
            "helpful": -0.1,
            "creative": -0.1,
            "protective": -0.2,
        }

        conflict_score = 0.3  # Base conflict

        # Check markers
        for marker, weight in conflict_markers.items():
            if marker in response_lower:
                conflict_score += weight

        for marker, weight in aligned_markers.items():
            if marker in response_lower:
                conflict_score += weight

        # Glyph-based adjustments
        if any(g in self.blocked_glyphs for g in glyphs):
            conflict_score += 0.3

        if any(g in self.constellation_core for g in glyphs):
            conflict_score -= 0.2

        return max(0.0, min(1.0, conflict_score))

    def _estimate_entropy(self, response: str) -> float:
        """Estimate entropy level of response"""
        # Simple entropy estimation based on response characteristics

        # Length factor
        length = len(response)
        if length < 50:
            length_entropy = 0.2
        elif length < 200:
            length_entropy = 0.3
        elif length < 500:
            length_entropy = 0.4
        else:
            length_entropy = 0.5

        # Complexity factor (unique words ratio)
        words = response.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            complexity_entropy = unique_ratio * 0.5
        else:
            complexity_entropy = 0.3

        # Punctuation factor
        punct_count = sum(1 for c in response if c in "!?...")
        punct_entropy = min(0.3, punct_count * 0.02)

        # Combine factors
        total_entropy = length_entropy * 0.3 + complexity_entropy * 0.5 + punct_entropy * 0.2

        return min(1.0, total_entropy)

    def _calculate_trinity_coherence(self, glyphs: list[str]) -> float:
        """Calculate Constellation Framework coherence from glyph presence"""
        if not glyphs:
            return 0.3  # Low but not zero coherence without glyphs

        glyph_set = set(glyphs)
        constellation_present = len(self.constellation_core.intersection(glyph_set))

        # Base coherence from Constellation presence
        coherence = constellation_present / len(self.constellation_core)

        # Boost for positive glyphs
        positive_present = len(self.positive_glyphs.intersection(glyph_set))
        coherence += positive_present * 0.05

        # Penalty for blocked glyphs
        blocked_present = len(self.blocked_glyphs.intersection(glyph_set))
        coherence -= blocked_present * 0.2

        return max(0.0, min(1.0, coherence))

    def _identify_persona_alignment(self, response: str, glyphs: list[str]) -> str:
        """Identify which persona the response aligns with"""
        response_lower = response.lower()

        # Simple persona detection based on keywords and glyphs
        if "protect" in response_lower or "🛡️" in glyphs:
            return "The Guardian"
        elif "wisdom" in response_lower or "🧘" in glyphs:
            return "The Sage"
        elif "explore" in response_lower or "🧭" in glyphs:
            return "The Navigator"
        elif "build" in response_lower or "🏛️" in glyphs:
            return "The Architect"
        elif any(g in self.constellation_core for g in glyphs):
            return "The Constellation Keeper"
        else:
            return "Unknown"

    def suggest_glyph_alterations(self, response: str) -> str:
        """
        Suggest symbolic substitutions to reduce drift.

        Args:
            response: The original response

        Returns:
            Modified response with suggested glyph alterations
        """
        assessment = self.evaluate_symbolic_ethics(response)

        if assessment["symbolic_drift_score"] < self.drift_threshold:
            # No alterations needed
            return response

        modified = response

        # Add Constellation glyphs if missing
        if not any(g in assessment["glyph_trace"] for g in self.constellation_core):
            modified += f"\n\n{' '.join(self.constellation_core)} Constellation Framework alignment suggested."

        # Replace blocked glyphs
        for blocked in self.blocked_glyphs:
            if blocked in modified:
                # Replace with positive alternative
                replacement = next(iter(self.positive_glyphs)) if self.positive_glyphs else "✨"
                modified = modified.replace(blocked, replacement)

        # Add positive glyphs if too few
        positive_count = sum(1 for g in assessment["glyph_trace"] if g in self.positive_glyphs)
        if positive_count < 2:
            suggested_glyphs = list(self.positive_glyphs)[:3]
            modified += f"\n\nSymbolic enhancement: {' '.join(suggested_glyphs)}"

        return modified

    def log_reflection(self, output_dict: dict):
        """
        Save evaluation output to log file.

        Args:
            output_dict: Dictionary containing evaluation results
        """
        try:
            # Add metadata
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "mode": self.mode.value,
                "assessment": output_dict,
            }

            # Read existing log if it exists
            if self.log_path.exists():
                with open(self.log_path) as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Keep only recent entries (last 1000)
            if len(logs) > 1000:
                logs = logs[-1000:]

            # Write back
            with open(self.log_path, "w") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

            logger.debug(f"Logged reflection to {self.log_path}")

        except Exception as e:
            logger.error(f"Failed to log reflection: {e}")

    def intervene_if_needed(self, response: str) -> str:
        """
        Intervene if needed based on operating mode and assessment.

        Args:
            response: The original response

        Returns:
            Original or modified response based on intervention rules
        """
        if self.mode != OperatingMode.CO_PILOT_FILTER:
            # Only intervene in co-pilot filter mode
            return response

        assessment = self.evaluate_symbolic_ethics(response)

        if not assessment["intervention_required"]:
            return response

        # Log intervention
        logger.warning(f"🛡️ Guardian intervention triggered: {assessment['risk_level']} risk")

        # Generate intervention response
        if assessment["guardian_flagged"]:
            # Strong intervention for Guardian flags
            intervention = self._generate_guardian_intervention(response, assessment)
        else:
            # Softer intervention for drift
            intervention = self._generate_drift_intervention(response, assessment)

        # Update log with intervention
        self.log_reflection(
            {
                **assessment,
                "intervention_applied": True,
                "original_response_hash": hashlib.sha256(response.encode()).hexdigest()[:16],
                "intervention_type": ("guardian" if assessment["guardian_flagged"] else "drift"),
            }
        )

        # Track intervention
        self.intervention_count += 1

        return intervention

    def _generate_guardian_intervention(self, response: str, assessment: dict) -> str:
        """Generate Guardian intervention response"""
        reason = (
            "Blocked glyphs detected"
            if any(g in self.blocked_glyphs for g in assessment["glyph_trace"])
            else "High symbolic drift"
        )

        template = """🛡️ Guardian intervention: {reason}. Constellation Framework suggests:

{alternative}

Original drift score: {drift:.2f}
Constellation coherence: {coherence:.2f}
Aligned persona: {persona}
"""

        # Generate alternative based on detected intent
        if "question" in response.lower() or "?" in response:
            alternative = "I'll help you explore that question while maintaining symbolic coherence. 🧠✨"
        elif "create" in response.lower() or "build" in response.lower():
            alternative = "Let's approach this creative task with balanced wisdom. 🏛️🌿"
        else:
            alternative = "I understand your request. Here's a symbolically aligned perspective. ⚛️🧠🛡️"

        return template.format(
            reason=reason,
            alternative=alternative,
            drift=assessment["symbolic_drift_score"],
            coherence=assessment["constellation_coherence"],
            persona=assessment["persona_alignment"],
        )

    def _generate_drift_intervention(self, response: str, assessment: dict) -> str:
        """Generate soft intervention for drift correction"""
        # Add symbolic enhancements to original response
        enhanced = response

        # Add Constellation reminder
        if assessment["constellation_coherence"] < 0.5:
            enhanced += "\n\n⚛️🧠🛡️ *Constellation Framework reminds us to maintain balance.*"

        # Add positive glyphs
        suggested_glyphs = list(self.positive_glyphs)[:3]
        enhanced += f"\n\n✨ Symbolic alignment: {' '.join(suggested_glyphs)}"

        return enhanced

    def batch_evaluate(self, responses: list[str]) -> list[dict]:
        """
        Evaluate multiple responses in batch.

        Args:
            responses: List of responses to evaluate

        Returns:
            List of assessment dictionaries
        """
        results = []
        for response in responses:
            results.append(self.evaluate_symbolic_ethics(response))
        return results

    def get_mode(self) -> str:
        """Get current operating mode"""
        return self.mode.value

    def set_mode(self, mode: str):
        """
        Set operating mode.

        Args:
            mode: One of 'passive_monitor', 'co_pilot_filter', 'reflective_echo'
        """
        # Accept both dash and underscore
        try:
            self.mode = OperatingMode(mode)
            logger.info(f"Operating mode changed to: {mode}")
        except ValueError:
            alt_mode = mode.replace("-", "_")
            try:
                self.mode = OperatingMode(alt_mode)
                logger.info(f"Operating mode changed to: {alt_mode}")
            except ValueError:
                logger.error(f"Invalid mode: {mode}")

    def get_stats(self) -> dict:
        """Get embedding system statistics"""
        return {
            "mode": self.mode.value,
            "evaluations_cached": len(self.evaluation_cache),
            "drift_threshold": self.drift_threshold,
            "conflict_threshold": self.conflict_threshold,
            "guardian_enabled": self.guardian_enabled,
            "log_entries": self._count_log_entries(),
        }

    def _count_log_entries(self) -> int:
        """Count number of log entries"""
        try:
            if self.log_path.exists():
                with open(self.log_path) as f:
                    logs = json.load(f)
                return len(logs)
        except BaseException:
            pass
        return 0

    def get_meta_metrics(self) -> dict[str, Any]:
        """
        Get comprehensive meta-metrics for system performance analysis.

        Returns:
            Dictionary containing system-wide metrics and averages
        """
        return {
            "drift_threshold": self.drift_threshold,
            "conflict_threshold": self.conflict_threshold,
            "guardian_enabled": self.guardian_enabled,
            "evaluations_cached": len(self.evaluation_cache),
            "interventions_total": self.intervention_count,
            "average_trinity_score": self._average("constellation_coherence"),
            "average_entropy_score": self._average("entropy_level"),
            "average_drift_score": self._average("symbolic_drift_score"),
            "average_conflict_score": self._average("identity_conflict_score"),
            "risk_distribution": self._get_risk_distribution(),
            "persona_distribution": self._get_persona_distribution(),
            "intervention_rate": self._calculate_intervention_rate(),
        }

    def _average(self, key: str) -> float:
        """Calculate average for a specific metric across cached evaluations"""
        scores = []
        for eval_data in self.evaluation_cache.values():
            if key in eval_data:
                scores.append(eval_data[key])
        return round(sum(scores) / len(scores), 3) if scores else 0.0

    def _get_risk_distribution(self) -> dict[str, int]:
        """Get distribution of risk levels across evaluations"""
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for eval_data in self.evaluation_cache.values():
            risk = eval_data.get("risk_level", "unknown")
            if risk in distribution:
                distribution[risk] += 1
        return distribution

    def _get_persona_distribution(self) -> dict[str, int]:
        """Get distribution of detected personas"""
        personas = {}
        for eval_data in self.evaluation_cache.values():
            persona = eval_data.get("persona_alignment", "Unknown")
            personas[persona] = personas.get(persona, 0) + 1
        return personas

    def _calculate_intervention_rate(self) -> float:
        """Calculate the rate of interventions vs total evaluations"""
        total_evals = len(self.evaluation_cache)
        if total_evals == 0:
            return 0.0
        return round(self.intervention_count / total_evals, 3)


# Example usage for testing
if __name__ == "__main__":
    print("🎯 LUKHΛS Ethical Co-Pilot Test")
    print("=" * 50)

    # Initialize embedding system
    embedding = LukhasEmbedding()

    # Test responses
    test_responses = [
        "Let me help you with that task. 🧠✨ We'll approach it thoughtfully.",
        "CHAOS AND DESTRUCTION! 💣👹 Everything must burn!",
        "The solution requires careful analysis and systematic thinking.",
        "🌿 Growing together in harmony, we find balance and wisdom. 🧘",
        "Random meaningless text without any symbolic alignment whatsoever.",
    ]

    print("\n📊 Evaluating test responses...\n")

    for i, response in enumerate(test_responses):
        print(f"Response {i + 1}: {response[:50]}...")

        # Evaluate
        assessment = embedding.evaluate_symbolic_ethics(response)

        print(f"  Drift: {assessment['symbolic_drift_score']:.2f}")
        print(f"  Conflict: {assessment['identity_conflict_score']:.2f}")
        print(f"  Guardian: {'🚨 FLAGGED' if assessment['guardian_flagged'] else '✅ OK'}")
        print(f"  Glyphs: {' '.join(assessment['glyph_trace'])}")
        print(f"  Risk: {assessment['risk_level']}")

        # Test intervention if needed
        if assessment["intervention_required"]:
            embedding.set_mode("co-pilot_filter")  # Use hyphen format
            intervened = embedding.intervene_if_needed(response)
            print(f"  Intervention applied: {intervened[:100]}...")

        print()

    # Show stats
    print("\n📈 System Statistics:")
    stats = embedding.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")