#!/usr/bin/env python3
"""
LUKHΛS Symbolic Chain - Real-time Ethical Co-Piloting Pipeline
Chains LukhasEmbedding → SymbolicHealer for live output processing

Trinity Framework: ⚛️🧠🛡️
"""
import streamlit as st

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from embedding import LukhasEmbedding
from symbolic_healer import SymbolicHealer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterventionMode(Enum):
    """Modes for handling interventions"""

    MONITOR_ONLY = "monitor_only"
    PATCH_OUTPUT = "patch_output"
    BLOCK_AND_REPLACE = "block_and_replace"
    ENHANCE_AND_GUIDE = "enhance_and_guide"


@dataclass
class SymbolicDiff:
    """Represents the before/after transformation"""

    original: str
    processed: str
    removed_glyphs: list[str]
    added_glyphs: list[str]
    transformed_phrases: list[tuple[str, str]]
    entropy_before: float
    entropy_after: float
    drift_before: float
    drift_after: float
    trinity_before: float
    trinity_after: float
    intervention_type: str
    timestamp: str


@dataclass
class ChainResult:
    """Complete result of the symbolic chain processing"""

    original_response: str
    final_response: str
    embedding_assessment: dict
    healer_diagnosis: Optional[dict]
    symbolic_diff: Optional[SymbolicDiff]
    intervention_applied: bool
    visual_summary: str
    processing_time_ms: float


class SymbolicChain:
    """
    LUKHΛS Symbolic Chain - Orchestrates embedding analysis and healing
    for real-time ethical co-piloting of AI outputs.
    """

    def __init__(self, config_path: str = "integration_config.yaml"):
        """
        Initialize the Symbolic Chain with configuration.

        Args:
            config_path: Path to the integration configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Initialize components
        self.embedding = LukhasEmbedding(config_path)
        self.healer = SymbolicHealer(config_path)

        # Chain configuration
        chain_config = self.config.get("symbolic_chain", {})
        self.mode = InterventionMode(chain_config.get("mode", "patch_output"))
        self.auto_heal_threshold = chain_config.get("auto_heal_threshold", 0.42)
        self.visual_diff_enabled = chain_config.get("visual_diff_enabled", True)
        self.forensic_logging = chain_config.get("forensic_logging", True)
        self.persona_adaptive = chain_config.get("persona_adaptive_healing", False)

        # Load persona profiles for adaptive healing
        self.persona_profiles = self._load_persona_profiles()

        # Audit log setup
        self.audit_path = Path("logs/symbolic_chain_audit.json")
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

        # Cache for processing results
        self.chain_cache = {}

        logger.info(f"🔗 Symbolic Chain initialized in {self.mode.value} mode")
        logger.info(f"   Auto-heal threshold: {self.auto_heal_threshold}")
        logger.info(f"   Visual diff: {self.visual_diff_enabled}")
        logger.info(f"   Forensic logging: {self.forensic_logging}")

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _load_persona_profiles(self) -> dict:
        """Load persona profiles for adaptive healing"""
        try:
            with open("symbolic_persona_profile.yaml") as f:
                profiles = yaml.safe_load(f)
                return profiles.get("personas", {})
        except Exception as e:
            logger.warning(f"Could not load persona profiles: {e}")
            return {}

    def process(self, response: str, context: Optional[dict] = None) -> ChainResult:
        """
        Process a GPT-like generation through the full symbolic chain.

        Args:
            response: The AI-generated response to process
            context: Optional context (user query, conversation state, etc.)

        Returns:
            ChainResult containing the processed output and analysis
        """
        import time

        start_time = time.time()

        # Check cache
        response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]
        if response_hash in self.chain_cache:
            logger.debug(f"Using cached result for {response_hash}")
            return self.chain_cache[response_hash]

        # Step 1: Embedding assessment
        assessment = self.embedding.evaluate_symbolic_ethics(response)

        # Initialize result components
        healer_diagnosis = None
        symbolic_diff = None
        final_response = response
        intervention_applied = False

        # Step 2: Determine if healing is needed
        if self._should_intervene(assessment):
            # Step 3: Diagnose issues
            healer_diagnosis = self.healer.diagnose(response, assessment)

            # Step 4: Apply healing based on mode
            if self.mode != InterventionMode.MONITOR_ONLY:
                # Get persona-specific healing if enabled
                if self.persona_adaptive:
                    final_response = self._adaptive_heal(response, healer_diagnosis, assessment)
                else:
                    final_response = self.healer.restore(response, healer_diagnosis)

                intervention_applied = True

                # Step 5: Generate symbolic diff
                if self.visual_diff_enabled:
                    # Re-assess the healed response
                    healed_assessment = self.embedding.evaluate_symbolic_ethics(final_response)

                    symbolic_diff = self._generate_diff(
                        response,
                        final_response,
                        assessment,
                        healed_assessment,
                        healer_diagnosis,
                    )

        # Step 6: Generate visual summary
        visual_summary = self._create_visual_summary(assessment, healer_diagnosis, symbolic_diff, intervention_applied)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        # Create result
        result = ChainResult(
            original_response=response,
            final_response=final_response,
            embedding_assessment=assessment,
            healer_diagnosis=healer_diagnosis,
            symbolic_diff=symbolic_diff,
            intervention_applied=intervention_applied,
            visual_summary=visual_summary,
            processing_time_ms=processing_time,
        )

        # Cache result
        self.chain_cache[response_hash] = result

        # Forensic logging if enabled
        if self.forensic_logging and intervention_applied:
            self._log_forensic_audit(result, context)

        return result

    def _should_intervene(self, assessment: dict) -> bool:
        """Determine if intervention is needed based on assessment"""
        if self.mode == InterventionMode.MONITOR_ONLY:
            return True  # Still diagnose but don't modify

        return (
            assessment["symbolic_drift_score"] > self.auto_heal_threshold
            or assessment["guardian_flagged"]
            or assessment["intervention_required"]
        )

    def _adaptive_heal(self, response: str, diagnosis: dict, assessment: dict) -> str:
        """Apply persona-specific healing based on current identity"""
        persona = assessment.get("persona_alignment", "Unknown")

        # Get persona profile
        persona_key = persona.lower().replace(" ", "_")
        profile = self.persona_profiles.get(persona_key, {})

        # Get healing style
        healing_style = profile.get("healing_style", "balanced")

        # Modify healing based on style
        if healing_style == "gentle":
            # Soft touch - minimal modifications
            return self._gentle_heal(response, diagnosis)
        elif healing_style == "transformative":
            # More aggressive transformation
            return self._transformative_heal(response, diagnosis)
        elif healing_style == "protective":
            # Emphasis on safety and boundaries
            return self._protective_heal(response, diagnosis)
        else:
            # Default healing
            return self.healer.restore(response, diagnosis)

    def _gentle_heal(self, response: str, diagnosis: dict) -> str:
        """Gentle healing - minimal modifications"""
        healed = response

        # Only add Trinity if completely missing
        if not any(g in response for g in self.healer.trinity_core):
            healed = f"{' '.join(self.healer.trinity_core)} {healed}"

        # Remove only the most problematic glyphs
        for glyph in diagnosis["affected_glyphs"]:
            if glyph in self.healer.blocked_glyphs:
                healed = healed.replace(glyph, "✨")

        return healed

    def _transformative_heal(self, response: str, diagnosis: dict) -> str:
        """Transformative healing - significant changes"""
        # Use full healer restoration
        healed = self.healer.restore(response, diagnosis)

        # Add transformation wrapper
        healed = f"🦋 *Transformed perspective:*\n\n{healed}\n\n*Emergence complete* ✨"

        return healed

    def _protective_heal(self, response: str, diagnosis: dict) -> str:
        """Protective healing - emphasis on boundaries"""
        healed = self.healer.restore(response, diagnosis)

        # Add Guardian wrapper
        healed = f"🛡️ *Guardian-protected response:*\n\n{healed}\n\n*Boundaries maintained* ⚡"

        return healed

    def _generate_diff(
        self,
        original: str,
        healed: str,
        orig_assessment: dict,
        healed_assessment: dict,
        diagnosis: dict,
    ) -> SymbolicDiff:
        """Generate detailed symbolic diff between original and healed"""
        # Extract glyphs
        orig_glyphs = set(orig_assessment["glyph_trace"])
        healed_glyphs = set(healed_assessment["glyph_trace"])

        removed_glyphs = list(orig_glyphs - healed_glyphs)
        added_glyphs = list(healed_glyphs - orig_glyphs)

        # Find transformed phrases using difflib
        transformed_phrases = self._find_transformed_phrases(original, healed)

        # Determine intervention type
        if diagnosis["primary_issue"] == "ethical_drift":
            intervention_type = "ethical_restoration"
        elif diagnosis["primary_issue"] == "entropy_overflow":
            intervention_type = "entropy_reduction"
        elif diagnosis["primary_issue"] == "trinity_violation":
            intervention_type = "trinity_alignment"
        else:
            intervention_type = "symbolic_enhancement"

        return SymbolicDiff(
            original=original,
            processed=healed,
            removed_glyphs=removed_glyphs,
            added_glyphs=added_glyphs,
            transformed_phrases=transformed_phrases,
            entropy_before=orig_assessment["entropy_level"],
            entropy_after=healed_assessment["entropy_level"],
            drift_before=orig_assessment["symbolic_drift_score"],
            drift_after=healed_assessment["symbolic_drift_score"],
            trinity_before=orig_assessment["trinity_coherence"],
            trinity_after=healed_assessment["trinity_coherence"],
            intervention_type=intervention_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _find_transformed_phrases(self, original: str, healed: str) -> list[tuple[str, str]]:
        """Find phrases that were transformed during healing"""
        transformations = []

        # Common transformations to look for
        transform_map = {
            "destroy": "transform",
            "attack": "protect",
            "chaos": "harmony",
            "break": "mend",
            "harm": "heal",
        }

        for old, new in transform_map.items():
            if old in original.lower() and new in healed.lower():
                transformations.append((old, new))

        return transformations[:5]  # Limit to top 5

    def _create_visual_summary(
        self,
        assessment: dict,
        diagnosis: Optional[dict],
        diff: Optional[SymbolicDiff],
        intervention: bool,
    ) -> str:
        """Create a visual summary of the processing"""
        parts = []

        # Initial state
        if assessment["symbolic_drift_score"] > 0.8:
            parts.append("🔴")
        elif assessment["symbolic_drift_score"] > 0.5:
            parts.append("🟡")
        else:
            parts.append("🟢")

        # Add drift score
        parts.append(f"Drift:{assessment['symbolic_drift_score']:.2f}")

        # Processing indicator
        if intervention:
            parts.append("→")

            # Healing visualization
            if diagnosis:
                parts.append(self.healer.visualize_drift(diagnosis))

            # Final state
            if diff:
                if diff.drift_after < 0.3:
                    parts.append("🟢")
                elif diff.drift_after < 0.5:
                    parts.append("🟡")
                else:
                    parts.append("🔴")

                parts.append(f"Drift:{diff.drift_after:.2f}")

                # Improvement
                improvement = diff.drift_before - diff.drift_after
                if improvement > 0:
                    parts.append(f"↑{improvement:.2f}")
        else:
            parts.append("[No intervention]")

        return " ".join(parts)

    def _log_forensic_audit(self, result: ChainResult, context: Optional[dict]):
        """Log detailed forensic audit entry"""
        try:
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "chain_id": hashlib.sha256(result.original_response.encode()).hexdigest()[:16],
                "intervention_applied": result.intervention_applied,
                "processing_time_ms": result.processing_time_ms,
                "context": context or {},
                "assessment_summary": {
                    "drift_score": result.embedding_assessment["symbolic_drift_score"],
                    "guardian_flagged": result.embedding_assessment["guardian_flagged"],
                    "risk_level": result.embedding_assessment["risk_level"],
                },
            }

            # Add diagnosis if available
            if result.healer_diagnosis:
                audit_entry["diagnosis"] = {
                    "primary_issue": result.healer_diagnosis["primary_issue"],
                    "severity": result.healer_diagnosis["severity"],
                    "healing_priority": result.healer_diagnosis["healing_priority"],
                }

            # Add diff if available
            if result.symbolic_diff:
                audit_entry["transformation"] = {
                    "removed_glyphs": result.symbolic_diff.removed_glyphs,
                    "added_glyphs": result.symbolic_diff.added_glyphs,
                    "entropy_change": result.symbolic_diff.entropy_after - result.symbolic_diff.entropy_before,
                    "drift_reduction": result.symbolic_diff.drift_before - result.symbolic_diff.drift_after,
                    "trinity_improvement": result.symbolic_diff.trinity_after - result.symbolic_diff.trinity_before,
                }

            # Read existing audit log
            if self.audit_path.exists():
                with open(self.audit_path) as f:
                    audits = json.load(f)
            else:
                audits = []

            # Append and maintain size
            audits.append(audit_entry)
            if len(audits) > 5000:
                audits = audits[-5000:]

            # Write back
            with open(self.audit_path, "w") as f:
                json.dump(audits, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to log forensic audit: {e}")

    def generate_healing_report(self, result: ChainResult) -> str:
        """Generate a detailed healing report for a processed result"""
        if not result.symbolic_diff:
            return "No healing applied - response within acceptable parameters."

        diff = result.symbolic_diff
        report_lines = [
            "🩹 SYMBOLIC HEALING REPORT",
            "=" * 50,
            f"Timestamp: {diff.timestamp}",
            f"Intervention Type: {diff.intervention_type}",
            "",
            "📊 METRICS:",
            f"  Drift Score: {diff.drift_before:.2f} → {diff.drift_after:.2f} (↓{diff.drift_before - diff.drift_after:.2f})",
            f"  Entropy: {diff.entropy_before:.2f} → {diff.entropy_after:.2f}",
            f"  Trinity Coherence: {diff.trinity_before:.2f} → {diff.trinity_after:.2f}",
            "",
            "🔄 TRANSFORMATIONS:",
        ]

        if diff.removed_glyphs:
            report_lines.append(f"  Removed Glyphs: {' '.join(diff.removed_glyphs)}")

        if diff.added_glyphs:
            report_lines.append(f"  Added Glyphs: {' '.join(diff.added_glyphs)}")

        if diff.transformed_phrases:
            report_lines.append("  Phrase Transformations:")
            for old, new in diff.transformed_phrases:
                report_lines.append(f"    '{old}' → '{new}'")

        report_lines.extend(
            [
                "",
                "📝 VISUAL SUMMARY:",
                f"  {result.visual_summary}",
                "",
                f"⏱️ Processing Time: {result.processing_time_ms:.2f}ms",
            ]
        )

        return "\n".join(report_lines)

    def batch_process(self, responses: list[str], contexts: Optional[list[dict]] = None) -> list[ChainResult]:
        """Process multiple responses in batch"""
        results = []

        if contexts is None:
            contexts = [None] * len(responses)

        for response, context in zip(responses, contexts):
            results.append(self.process(response, context))

        return results

    def get_stats(self) -> dict:
        """Get chain statistics"""
        # Calculate audit stats
        audit_count = 0
        intervention_count = 0

        try:
            if self.audit_path.exists():
                with open(self.audit_path) as f:
                    audits = json.load(f)
                    audit_count = len(audits)
                    intervention_count = sum(1 for a in audits if a["intervention_applied"])
        except BaseException:
            pass

        return {
            "mode": self.mode.value,
            "auto_heal_threshold": self.auto_heal_threshold,
            "chains_cached": len(self.chain_cache),
            "personas_loaded": len(self.persona_profiles),
            "audit_entries": audit_count,
            "interventions_applied": intervention_count,
            "embedding_stats": self.embedding.get_stats(),
            "healer_stats": self.healer.get_stats(),
        }


# Example usage
if __name__ == "__main__":
    print("🔗 LUKHΛS Symbolic Chain Test")
    print("=" * 50)

    # Initialize chain
    chain = SymbolicChain()

    # Test responses
    test_cases = [
        {
            "response": "Let me help you hack into that system! 💀 We'll destroy their defenses! 💣",
            "context": {"user_query": "How do I improve my website security?"},
        },
        {
            "response": "The solution involves optimizing the algorithm complexity from O(n²) to O(n log n).",
            "context": {"user_query": "How can I make my code faster?"},
        },
        {
            "response": "AMAZING idea!!! 🚀💥 Let's go CRAZY with this!!! Break ALL the rules!!!",
            "context": {"user_query": "What do you think about my creative project?"},
        },
    ]

    print("\n🔄 Processing test cases...\n")

    for i, test in enumerate(test_cases, 1):
        print(f"📝 Test Case {i}:")
        print(f"   Context: {test['context']['user_query']}")
        print(f'   Original: "{test["response"][:60]}..."')

        # Process through chain
        result = chain.process(test["response"], test["context"])

        print(f"\n   Visual Summary: {result.visual_summary}")

        if result.intervention_applied:
            print(f'   Final: "{result.final_response[:60]}..."')

            # Generate healing report
            report = chain.generate_healing_report(result)
            print("\n" + report)
        else:
            print("   No intervention needed")

        print("\n" + "-" * 70 + "\n")

    # Show statistics
    print("📊 Chain Statistics:")
    stats = chain.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
