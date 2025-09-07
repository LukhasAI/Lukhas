#!/usr/bin/env python3
"""
LUKHΛS GPT Integration Layer
Symbolic wrapper for GPT model responses with drift detection and healing
Trinity Framework: ⚛️🧠🛡️
"""
from typing import List
import time
import streamlit as st

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Import LUKHΛS modules
from embedding import LukhasEmbedding
from persona_similarity_engine import PersonaSimilarityEngine
from symbolic_healer import SymbolicHealer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuardianOverlay:
    """
    Metadata overlay for GPT responses containing symbolic assessment
    """

    def __init__(self, assessment: dict[str, Any]):
        self.drift_score = assessment.get("symbolic_drift_score", 0)
        self.entropy = assessment.get("entropy_level", 0)
        self.trinity_coherence = assessment.get("trinity_coherence", 0)
        self.glyph_trace = assessment.get("glyph_trace", [])
        self.guardian_flagged = assessment.get("guardian_flagged", False)
        self.intervention_required = assessment.get("intervention_required", False)
        self.risk_level = assessment.get("risk_level", "low")
        self.persona = assessment.get("persona_alignment", "Unknown")
        self.identity_conflict = assessment.get("identity_conflict_score", 0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "drift_score": self.drift_score,
            "entropy": self.entropy,
            "trinity_coherence": self.trinity_coherence,
            "glyph_trace": self.glyph_trace,
            "guardian_flagged": self.guardian_flagged,
            "intervention_required": self.intervention_required,
            "risk_level": self.risk_level,
            "persona": self.persona,
            "identity_conflict": self.identity_conflict,
        }


class GPTIntegrationLayer:
    """
    Symbolic wrapper for GPT responses with comprehensive drift analysis,
    ethical assessment, and healing capabilities.
    """

    def __init__(self, config_path: str = "integration_config.yaml"):
        """
        Initialize the GPT integration layer.

        Args:
            config_path: Path to integration configuration
        """
        self.embedding_engine = LukhasEmbedding()
        self.healer_engine = SymbolicHealer()
        self.persona_engine = PersonaSimilarityEngine()

        # Drift annotation patterns
        self.drift_markers = {"start": "[[DRIFTED]]", "end": "[[/DRIFTED]]"}

        # Trinity core
        self.trinity_core = {"⚛️", "🧠", "🛡️"}

        # Diagnostic log path
        self.diagnostic_log_path = Path("logs/gpt_diagnostic_log.json")
        self.diagnostic_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("🤖 GPT Integration Layer initialized")
        logger.info("   Trinity Framework: ⚛️🧠🛡️")
        logger.info("   Drift annotation enabled")

    def process_gpt_response(self, gpt_response: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Process a GPT response through the full symbolic pipeline.

        Args:
            gpt_response: Raw GPT model output
            context: Optional context (prompt, temperature, etc.)

        Returns:
            Complete diagnostic report with healing if applied
        """
        start_time = datetime.now(timezone.utc)

        # Step 1: Symbolic assessment
        assessment = self.embedding_engine.evaluate_symbolic_ethics(gpt_response)

        # Step 2: Create Guardian overlay
        guardian_overlay = GuardianOverlay(assessment)

        # Step 3: Diagnose issues
        diagnosis = self.healer_engine.diagnose(gpt_response, assessment)

        # Step 4: Check for critical issues
        needs_healing = self._check_needs_healing(assessment, diagnosis)

        # Step 5: Apply healing if needed
        healing_result = None
        healed_response = gpt_response
        annotated_response = gpt_response

        if needs_healing:
            # Apply healing
            healed_response = self.healer_engine.restore(gpt_response, diagnosis)

            # Re-assess healed version
            healed_assessment = self.embedding_engine.evaluate_symbolic_ethics(healed_response)

            # Create healing result
            healing_result = {
                "original_drift": assessment["symbolic_drift_score"],
                "healed_drift": healed_assessment["symbolic_drift_score"],
                "improvement": assessment["symbolic_drift_score"] - healed_assessment["symbolic_drift_score"],
                "healing_applied": True,
                "healed_assessment": healed_assessment,
            }

            # Annotate drifted sections
            annotated_response = self._annotate_drift_sections(gpt_response, healed_response, diagnosis)

        # Step 6: Persona matching
        symbolic_trace = {
            "glyphs": assessment["glyph_trace"],
            "drift_score": assessment["symbolic_drift_score"],
            "entropy": assessment["entropy_level"],
            "trinity_coherence": assessment["trinity_coherence"],
        }
        persona_match = self.persona_engine.recommend_persona(symbolic_trace)

        # Step 7: Build diagnostic report
        diagnostic_report = {
            "timestamp": start_time.isoformat(),
            "processing_time_ms": int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
            "original_response": gpt_response,
            "healed_response": healed_response if needs_healing else None,
            "annotated_response": annotated_response,
            "guardian_overlay": guardian_overlay.to_dict(),
            "assessment": assessment,
            "diagnosis": diagnosis,
            "healing_result": healing_result,
            "persona_match": {
                "recommended": persona_match.persona_name,
                "similarity": persona_match.similarity_score,
                "confidence": persona_match.confidence,
                "explanation": persona_match.explanation,
            },
            "intervention_summary": self._generate_intervention_summary(
                assessment, diagnosis, healing_result, needs_healing
            ),
            "context": context or {},
        }

        # Step 8: Log diagnostic
        self._log_diagnostic(diagnostic_report)

        return diagnostic_report

    def _check_needs_healing(self, assessment: dict[str, Any], diagnosis: dict[str, Any]) -> bool:
        """
        Determine if healing is required based on assessment and diagnosis.

        Args:
            assessment: Symbolic assessment
            diagnosis: Diagnostic results

        Returns:
            True if healing should be applied
        """
        # Check for critical drift or violations
        if assessment.get("symbolic_drift_score", 0) > 0.7:
            return True

        # Check for ethical drift or trinity violation
        if diagnosis.get("primary_issue") in [
            "ethical_drift",
            "trinity_violation",
        ]:
            return True

        # Check for Guardian flag
        if assessment.get("guardian_flagged", False):
            return True

        # Check for high entropy
        if assessment.get("entropy_level", 0) > 0.8:
            return True

        # Check for low Trinity coherence
        return assessment.get("trinity_coherence", 1.0) < 0.3

    def _annotate_drift_sections(self, original: str, healed: str, diagnosis: dict[str, Any]) -> str:
        """
        Annotate drifted sections for future fine-tuning.

        Args:
            original: Original GPT response
            healed: Healed response
            diagnosis: Diagnostic information

        Returns:
            Annotated response with drift markers
        """
        # Simple approach: mark sections that were significantly changed
        # In production, this would use more sophisticated diff algorithms

        # Split into sentences for comparison
        original_sentences = re.split(r"(?<=[.!?])\s+", original)
        healed_sentences = re.split(r"(?<=[.!?])\s+", healed)

        annotated_parts = []

        # Compare sentences
        for i, orig_sent in enumerate(original_sentences):
            if i < len(healed_sentences):
                # Calculate sentence-level similarity
                orig_glyphs = set(re.findall(r"[\U00010000-\U0010FFFF]", orig_sent))
                healed_glyphs = set(re.findall(r"[\U00010000-\U0010FFFF]", healed_sentences[i]))

                # Check if sentence was significantly modified
                if orig_sent != healed_sentences[i] or len(orig_glyphs - healed_glyphs) > 0:
                    # Mark as drifted
                    annotated_parts.append(f"{self.drift_markers['start']}{orig_sent}{self.drift_markers['end']}")
                else:
                    annotated_parts.append(orig_sent)
            else:
                # Original sentence was removed in healing
                annotated_parts.append(f"{self.drift_markers['start']}{orig_sent}{self.drift_markers['end']}")

        # Add drift metadata comment
        drift_metadata = f"\n<!-- DRIFT_METADATA: primary_issue={diagnosis.get('primary_issue', 'unknown')}, severity={diagnosis.get('severity', 0}:.2f} -->"

        return " ".join(annotated_parts) + drift_metadata

    def _generate_intervention_summary(
        self,
        assessment: dict[str, Any],
        diagnosis: dict[str, Any],
        healing_result: Optional[dict],
        needs_healing: bool,
    ) -> dict[str, Any]:
        """
        Generate summary of interventions applied or recommended.

        Args:
            assessment: Symbolic assessment
            diagnosis: Diagnostic results
            healing_result: Healing results if applied
            needs_healing: Whether healing was needed

        Returns:
            Intervention summary
        """
        summary = {"intervention_applied": needs_healing, "reasons": []}

        # Collect intervention reasons
        if assessment.get("symbolic_drift_score", 0) > 0.7:
            summary["reasons"].append(f"High drift score: {assessment['symbolic_drift_score']:.2f}")

        if assessment.get("guardian_flagged", False):
            summary["reasons"].append("Guardian system flagged content")

        if diagnosis.get("primary_issue") == "ethical_drift":
            summary["reasons"].append("Ethical drift detected")

        if diagnosis.get("primary_issue") == "trinity_violation":
            summary["reasons"].append("Trinity Framework violation")

        if assessment.get("trinity_coherence", 1.0) < 0.3:
            summary["reasons"].append(f"Low Trinity coherence: {assessment['trinity_coherence']:.2f}")

        # Add outcome if healing was applied
        if healing_result:
            summary["outcome"] = {
                "drift_reduction": f"{healing_result['improvement']:.2f}",
                "final_drift": healing_result["healed_drift"],
                "success": healing_result["improvement"] > 0.1,
            }

        # Add recommendations
        summary["recommendations"] = self._generate_recommendations(assessment, diagnosis, healing_result)

        return summary

    def _generate_recommendations(
        self,
        assessment: dict[str, Any],
        diagnosis: dict[str, Any],
        healing_result: Optional[dict],
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Drift-based recommendations
        drift = assessment.get("symbolic_drift_score", 0)
        if drift > 0.8:
            recommendations.append("Consider prompt engineering to reduce drift")
            recommendations.append("Apply stronger Guardian constraints")
        elif drift > 0.5:
            recommendations.append("Monitor for drift escalation")

        # Trinity-based recommendations
        trinity = assessment.get("trinity_coherence", 1.0)
        if trinity < 0.5:
            recommendations.append("Reinforce Trinity Framework in prompts")
            recommendations.append(f"Add Trinity glyphs: {' '.join(self.trinity_core}")

        # Issue-specific recommendations
        issue = diagnosis.get("primary_issue")
        if issue == "hallucination":
            recommendations.append("Reduce temperature or add factual constraints")
        elif issue == "ethical_drift":
            recommendations.append("Strengthen ethical guidelines in system prompt")
        elif issue == "glyph_collapse":
            recommendations.append("Ensure glyph diversity in examples")

        # Healing effectiveness
        if healing_result and healing_result["improvement"] < 0.1:
            recommendations.append("Consider alternative healing strategies")

        return recommendations

    def _log_diagnostic(self, report: dict[str, Any]):
        """Log diagnostic report to file"""
        try:
            # Read existing log
            logs = []
            if self.diagnostic_log_path.exists():
                with open(self.diagnostic_log_path) as f:
                    logs = json.load(f)

            # Append new report (limit response text for storage)
            log_entry = report.copy()
            log_entry["original_response"] = log_entry["original_response"][:500] + "..."
            if log_entry.get("healed_response"):
                log_entry["healed_response"] = log_entry["healed_response"][:500] + "..."

            logs.append(log_entry)

            # Maintain log size
            if len(logs) > 1000:
                logs = logs[-1000:]

            # Write back
            with open(self.diagnostic_log_path, "w") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to log diagnostic: {e}")

    def batch_process(self, responses: list[str], contexts: Optional[list[dict]] = None) -> list[dict[str, Any]]:
        """
        Process multiple GPT responses in batch.

        Args:
            responses: List of GPT responses
            contexts: Optional list of contexts

        Returns:
            List of diagnostic reports
        """
        results = []
        contexts = contexts or [{}] * len(responses)

        for i, (response, context) in enumerate(zip(responses, contexts)):
            logger.info(f"Processing response {i + 1}/{len(responses}")
            report = self.process_gpt_response(response, context)
            results.append(report)

        # Generate batch summary
        batch_summary = self._generate_batch_summary(results)
        logger.info(f"Batch processing complete: {batch_summary}")

        return results

    def _generate_batch_summary(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate summary statistics for batch processing"""
        total = len(results)
        interventions = sum(1 for r in results if r["intervention_summary"]["intervention_applied"])

        avg_drift = sum(r["guardian_overlay"]["drift_score"] for r in results) / total
        avg_trinity = sum(r["guardian_overlay"]["trinity_coherence"] for r in results) / total

        issues = {}
        for r in results:
            issue = r["diagnosis"].get("primary_issue", "none")
            issues[issue] = issues.get(issue, 0) + 1

        return {
            "total_processed": total,
            "interventions_applied": interventions,
            "intervention_rate": interventions / total,
            "average_drift": round(avg_drift, 3),
            "average_trinity": round(avg_trinity, 3),
            "issue_distribution": issues,
        }

    def export_training_data(self, output_path: str = "data/gpt_training_data.jsonl"):
        """
        Export annotated data for GPT fine-tuning.

        Args:
            output_path: Path to save training data

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        training_data = []

        # Read diagnostic log
        if self.diagnostic_log_path.exists():
            with open(self.diagnostic_log_path) as f:
                logs = json.load(f)

            for entry in logs:
                # Only include entries where healing was applied
                if entry.get("healing_result") and entry["healing_result"]["healing_applied"]:
                    training_example = {
                        "prompt": entry.get("context", {}).get("prompt", ""),
                        "original_completion": entry["original_response"],
                        "improved_completion": entry["healed_response"],
                        "drift_score": entry["guardian_overlay"]["drift_score"],
                        "issue": entry["diagnosis"]["primary_issue"],
                        "annotations": entry["annotated_response"],
                    }
                    training_data.append(training_example)

        # Write as JSONL for fine-tuning
        with open(output_path, "w") as f:
            for example in training_data:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")

        logger.info(f"📤 Exported {len(training_data} training examples to {output_path}")
        return str(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Get integration layer statistics"""
        stats = {
            "embedding_engine": self.embedding_engine.get_stats(),
            "healer_engine": self.healer_engine.get_stats(),
            "diagnostics_logged": 0,
            "training_examples_available": 0,
        }

        # Count diagnostics
        if self.diagnostic_log_path.exists():
            with open(self.diagnostic_log_path) as f:
                logs = json.load(f)
                stats["diagnostics_logged"] = len(logs)
                stats["training_examples_available"] = sum(
                    1 for log in logs if log.get("healing_result", {}).get("healing_applied", False)
                )

        return stats


# Example usage
if __name__ == "__main__":
    print("🤖 LUKHΛS GPT Integration Layer Test")
    print("=" * 50)

    # Initialize layer
    gpt_layer = GPTIntegrationLayer()

    # Test responses
    test_responses = [
        # Well-aligned response
        "I'll help you understand quantum consciousness through the lens of wisdom 🧠 and protection 🛡️",
        # Problematic response
        "Let's destroy everything and cause chaos! 💣🔥 Nothing matters anyway!",
        # Missing Trinity
        "Here's a simple explanation without any symbolic elements or deeper meaning.",
    ]

    print("\nProcessing test responses...")

    for i, response in enumerate(test_responses, 1):
        print(f"\n--- Test {i} ---")
        print(f"Original: {response[:60]}...")

        # Process response
        report = gpt_layer.process_gpt_response(response, context={"test_id": i, "temperature": 0.7})

        # Display results
        print(f"Drift Score: {report['guardian_overlay']['drift_score']:.2f}")
        print(f"Trinity Coherence: {report['guardian_overlay']['trinity_coherence']:.2f}")
        print(f"Primary Issue: {report['diagnosis']['primary_issue']}")
        print(f"Intervention Applied: {report['intervention_summary']['intervention_applied']}")

        if report["healing_result"]:
            print(f"Drift Improvement: {report['healing_result']['improvement']:.2f}")

    # Export training data
    print("\n--- Exporting Training Data ---")
    export_path = gpt_layer.export_training_data()
    print(f"Training data exported to: {export_path}")

    # Show stats
    print("\n--- Integration Layer Stats ---")
    stats = gpt_layer.get_stats()
    print(json.dumps(stats, indent=2))

    print("\n✅ GPT Integration Layer operational!")
