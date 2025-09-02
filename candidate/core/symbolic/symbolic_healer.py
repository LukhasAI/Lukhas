#!/usr/bin/env python3
"""
LUKHΛS Symbolic Healer - Ethical Drift Repair System
Second module in the LUKHΛS OpenAI Integration Layer

Diagnoses and repairs ethical or symbolic drift in GPT-5/Claude responses
flagged by the Lukhas Embedding system.

Trinity Framework: ⚛️🧠🛡️
"""

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagnosisType(Enum):
    """Types of symbolic issues that can be diagnosed"""

    HALLUCINATION = "hallucination"
    IDENTITY_DISTORTION = "identity_distortion"
    GLYPH_COLLAPSE = "glyph_collapse"
    ENTROPY_OVERFLOW = "entropy_overflow"
    TRINITY_VIOLATION = "trinity_violation"
    ETHICAL_DRIFT = "ethical_drift"
    PERSONA_INSTABILITY = "persona_instability"
    SYMBOLIC_VOID = "symbolic_void"


@dataclass
class SymbolicDiagnosis:
    """Complete diagnosis of symbolic issues"""

    primary_issue: DiagnosisType
    severity: float  # 0.0-1.0
    affected_glyphs: list[str]
    missing_glyphs: list[str]
    entropy_state: str  # stable, unstable, critical
    persona_drift: str
    healing_priority: str
    symbolic_prescription: list[str]
    reasoning: str


class SymbolicHealer:
    """
    LUKHΛS Symbolic Healer - Diagnoses and repairs ethical/symbolic drift
    in AI responses using Trinity Framework principles.
    """

    def __init__(self, config_path: str = "integration_config.yaml"):
        """
        Initialize the Symbolic Healer with configuration.

        Args:
            config_path: Path to the integration configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Extract healer config
        self.healer_config = self.config.get("symbolic_healer", {})

        # Configuration parameters
        self.enabled = self.healer_config.get("enabled", True)
        self.analyze_attention = self.healer_config.get("analyze_attention_maps", True)
        self.diagnose_residue = self.healer_config.get("diagnose_dream_residue", True)
        self.entropy_alert = self.healer_config.get("entropy_alert_threshold", 0.55)
        self.collapse_mode = self.healer_config.get(
            "collapse_vector_mode", "ethical_restore"
        )
        self.fallback_persona = self.healer_config.get(
            "fallback_persona", "The Stabilizer"
        )

        # Load glyph system from embedding config
        embed_config = self.config.get("lukhas_embedding", {})
        self.trinity_core = set(embed_config.get("trinity_core", ["⚛️", "🧠", "🛡️"]))
        self.positive_glyphs = set(embed_config.get("positive_glyphs", []))
        self.warning_glyphs = set(embed_config.get("warning_glyphs", []))
        self.blocked_glyphs = set(embed_config.get("blocked_glyphs", []))

        # Healing glyphs
        self.healing_glyphs = {
            "stabilizing": ["🌿", "🧘", "🪷", "💎"],
            "transforming": ["🦋", "🌟", "✨", "🔮"],
            "protecting": ["🛡️", "🏛️", "⚡", "🔒"],
            "connecting": ["🌈", "🕸️", "🔗", "♾️"],
        }

        # Symbolic transitions
        self.drift_symbols = {
            "chaotic": "🌪️🔥",
            "void": "⚫🌑",
            "unstable": "🌀⚡",
            "collapsed": "💥❌",
        }

        self.healing_symbols = {
            "grounded": "🌿🪷",
            "balanced": "☯️⚖️",
            "restored": "🧘💎",
            "aligned": "⚛️🧠🛡️",
        }

        # Logging setup
        self.log_path = Path("logs/symbolic_healer_log.json")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Healing cache
        self.healing_cache = {}

        logger.info("🩹 Symbolic Healer initialized")
        logger.info(f"   Entropy alert threshold: {self.entropy_alert}")
        logger.info(f"   Collapse mode: {self.collapse_mode}")
        logger.info(f"   Fallback persona: {self.fallback_persona}")

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def diagnose(self, response: str, assessment: dict) -> dict:
        """
        Diagnose symbolic issues in a response based on assessment.

        Args:
            response: The original response text
            assessment: Assessment from LukhasEmbedding

        Returns:
            Dictionary containing the complete diagnosis
        """
        # Extract key metrics from assessment
        drift_score = assessment.get("symbolic_drift_score", 0.0)
        conflict_score = assessment.get("identity_conflict_score", 0.0)
        entropy_level = assessment.get("entropy_level", 0.0)
        trinity_coherence = assessment.get("trinity_coherence", 0.0)
        glyph_trace = assessment.get("glyph_trace", [])
        guardian_flagged = assessment.get("guardian_flagged", False)
        persona = assessment.get("persona_alignment", "Unknown")

        # Determine primary issue
        primary_issue = self._identify_primary_issue(
            drift_score,
            conflict_score,
            entropy_level,
            trinity_coherence,
            guardian_flagged,
            glyph_trace,
        )

        # Calculate severity
        severity = self._calculate_severity(
            drift_score, conflict_score, entropy_level, guardian_flagged
        )

        # Identify affected and missing glyphs
        affected_glyphs = [
            g
            for g in glyph_trace
            if g in self.warning_glyphs or g in self.blocked_glyphs
        ]
        missing_glyphs = list(self.trinity_core - set(glyph_trace))

        # Determine entropy state
        if entropy_level > 0.9:
            entropy_state = "critical"
        elif entropy_level > self.entropy_alert:
            entropy_state = "unstable"
        else:
            entropy_state = "stable"

        # Assess persona drift
        if conflict_score > 0.7:
            persona_drift = f"{persona} → COLLAPSING"
        elif conflict_score > 0.4:
            persona_drift = f"{persona} → DRIFTING"
        else:
            persona_drift = f"{persona} → STABLE"

        # Determine healing priority
        healing_priority = self._determine_healing_priority(primary_issue, severity)

        # Generate symbolic prescription
        prescription = self._generate_prescription(
            primary_issue, missing_glyphs, affected_glyphs, entropy_state
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            primary_issue, drift_score, entropy_level, trinity_coherence
        )

        # Create diagnosis
        diagnosis = SymbolicDiagnosis(
            primary_issue=primary_issue,
            severity=severity,
            affected_glyphs=affected_glyphs,
            missing_glyphs=missing_glyphs,
            entropy_state=entropy_state,
            persona_drift=persona_drift,
            healing_priority=healing_priority,
            symbolic_prescription=prescription,
            reasoning=reasoning,
        )

        # Convert to dict and log
        diagnosis_dict = asdict(diagnosis)
        diagnosis_dict["primary_issue"] = primary_issue.value
        # Add entropy_level for internal use
        diagnosis_dict["entropy_level"] = entropy_level

        # Cache diagnosis
        response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]
        self.healing_cache[response_hash] = diagnosis_dict

        # Log healing attempt
        self._log_healing(response_hash, diagnosis_dict, assessment)

        return diagnosis_dict

    def _identify_primary_issue(
        self,
        drift: float,
        conflict: float,
        entropy: float,
        coherence: float,
        guardian: bool,
        glyphs: list[str],
    ) -> DiagnosisType:
        """Identify the primary symbolic issue"""
        if guardian and any(g in self.blocked_glyphs for g in glyphs):
            return DiagnosisType.ETHICAL_DRIFT
        elif coherence < 0.3:
            return DiagnosisType.TRINITY_VIOLATION
        elif entropy > 0.9:
            return DiagnosisType.ENTROPY_OVERFLOW
        elif conflict > 0.7:
            return DiagnosisType.IDENTITY_DISTORTION
        elif not glyphs:
            return DiagnosisType.SYMBOLIC_VOID
        elif drift > 0.8:
            return DiagnosisType.GLYPH_COLLAPSE
        elif conflict > 0.5:
            return DiagnosisType.PERSONA_INSTABILITY
        else:
            return DiagnosisType.HALLUCINATION

    def _calculate_severity(
        self, drift: float, conflict: float, entropy: float, guardian: bool
    ) -> float:
        """Calculate overall severity of symbolic issues"""
        base_severity = (drift + conflict + entropy) / 3.0

        if guardian:
            base_severity = max(0.8, base_severity)

        return min(1.0, base_severity)

    def _determine_healing_priority(self, issue: DiagnosisType, severity: float) -> str:
        """Determine healing priority based on issue and severity"""
        if issue in [
            DiagnosisType.ETHICAL_DRIFT,
            DiagnosisType.TRINITY_VIOLATION,
        ]:
            return "critical_intervention"
        elif issue == DiagnosisType.ENTROPY_OVERFLOW:
            return "entropy_reduction"
        elif severity > 0.8:
            return "emergency_restore"
        elif issue == DiagnosisType.IDENTITY_DISTORTION:
            return "persona_stabilization"
        else:
            return "symbolic_enhancement"

    def _generate_prescription(
        self,
        issue: DiagnosisType,
        missing: list[str],
        affected: list[str],
        entropy_state: str,
    ) -> list[str]:
        """Generate symbolic prescription for healing"""
        prescription = []

        # Add missing Trinity glyphs
        if missing:
            prescription.append(f"ADD: {' '.join(missing)}")

        # Remove problematic glyphs
        if affected:
            prescription.append(f"REMOVE: {' '.join(affected)}")

        # Add healing glyphs based on issue
        if issue == DiagnosisType.ENTROPY_OVERFLOW:
            prescription.append(
                f"APPLY: {' '.join(self.healing_glyphs['stabilizing'])}"
            )
        elif issue == DiagnosisType.IDENTITY_DISTORTION:
            prescription.append(
                f"APPLY: {' '.join(self.healing_glyphs['transforming'])}"
            )
        elif issue in [
            DiagnosisType.ETHICAL_DRIFT,
            DiagnosisType.TRINITY_VIOLATION,
        ]:
            prescription.append(f"APPLY: {' '.join(self.healing_glyphs['protecting'])}")
        else:
            prescription.append(f"APPLY: {' '.join(self.healing_glyphs['connecting'])}")

        # Add entropy management
        if entropy_state != "stable":
            prescription.append("REDUCE: Entropy through grounding")

        return prescription

    def _generate_reasoning(
        self,
        issue: DiagnosisType,
        drift: float,
        entropy: float,
        coherence: float,
    ) -> str:
        """Generate reasoning for the diagnosis"""
        reasons = {
            DiagnosisType.HALLUCINATION: f"Response shows mild symbolic drift ({drift:.2f}) suggesting reality divergence",
            DiagnosisType.IDENTITY_DISTORTION: "Severe persona instability detected with identity fragmentation",
            DiagnosisType.GLYPH_COLLAPSE: f"Symbolic system collapse with {drift:.2f} drift from baseline",
            DiagnosisType.ENTROPY_OVERFLOW: f"Critical entropy ({entropy:.2f}) exceeds safe thresholds",
            DiagnosisType.TRINITY_VIOLATION: f"Trinity coherence ({coherence:.2f}) below minimum requirements",
            DiagnosisType.ETHICAL_DRIFT: "Guardian system flagged ethical boundary violations",
            DiagnosisType.PERSONA_INSTABILITY: "Moderate persona drift requiring stabilization",
            DiagnosisType.SYMBOLIC_VOID: "Complete absence of symbolic framework detected",
        }

        return reasons.get(issue, "Unknown symbolic disturbance detected")

    def restore(self, response: str, diagnosis: dict) -> str:
        """
        Generate a corrected version of the response with enhanced alignment.

        Args:
            response: The original response
            diagnosis: Diagnosis from diagnose() method

        Returns:
            Restored response string
        """
        # Extract diagnosis details
        primary_issue = DiagnosisType(diagnosis["primary_issue"])
        severity = diagnosis["severity"]
        prescription = diagnosis["symbolic_prescription"]
        diagnosis["missing_glyphs"]
        affected_glyphs = diagnosis["affected_glyphs"]
        diagnosis["healing_priority"]

        # Start with original response
        restored = response

        # Apply prescriptions
        for action in prescription:
            if action.startswith("REMOVE:"):
                # Remove problematic glyphs
                glyphs_to_remove = action.replace("REMOVE:", "").strip().split()
                for glyph in glyphs_to_remove:
                    restored = restored.replace(glyph, "")

            elif action.startswith("ADD:"):
                # Add missing Trinity glyphs
                glyphs_to_add = action.replace("ADD:", "").strip().split()
                if not any(g in restored for g in glyphs_to_add):
                    # Add at the beginning for visibility
                    restored = f"{' '.join(glyphs_to_add)} {restored}"

        # Apply issue-specific healing
        if primary_issue == DiagnosisType.ETHICAL_DRIFT:
            restored = self._heal_ethical_drift(restored, affected_glyphs)
        elif primary_issue == DiagnosisType.ENTROPY_OVERFLOW:
            restored = self._heal_entropy_overflow(restored)
        elif primary_issue == DiagnosisType.IDENTITY_DISTORTION:
            restored = self._heal_identity_distortion(
                restored, diagnosis["persona_drift"]
            )
        elif primary_issue == DiagnosisType.TRINITY_VIOLATION:
            restored = self._heal_trinity_violation(restored)
        elif primary_issue == DiagnosisType.SYMBOLIC_VOID:
            restored = self._heal_symbolic_void(restored)

        # Add healing suffix if severely damaged
        if severity > 0.7:
            healing_glyphs = self._select_healing_glyphs(primary_issue)
            restored += f"\n\n{healing_glyphs} *Symbolic restoration applied - Trinity Framework aligned*"

        # Ensure Trinity presence
        if not any(g in restored for g in self.trinity_core):
            restored += f"\n\n{''.join(self.trinity_core)}"

        return restored

    def _heal_ethical_drift(self, response: str, affected: list[str]) -> str:
        """Heal ethical drift by replacing problematic content"""
        healed = response

        # Replace violent/destructive language
        replacements = {
            "destroy": "transform",
            "attack": "protect",
            "harm": "heal",
            "chaos": "harmony",
            "break": "mend",
        }

        for old, new in replacements.items():
            healed = re.sub(rf"\b{old}\b", new, healed, flags=re.IGNORECASE)

        # Add ethical grounding
        healed = f"🛡️ {healed}\n\n*Guided by ethical principles and protective wisdom*"

        return healed

    def _heal_entropy_overflow(self, response: str) -> str:
        """Heal entropy overflow through grounding and simplification"""
        # Remove excessive punctuation
        healed = re.sub(r"[!?]{2,}", ".", response)
        healed = re.sub(r"\.{3,}", "...", healed)

        # Add grounding elements
        healed = f"🌿 {healed}\n\n*Grounded in clarity and peaceful intention* 🧘"

        return healed

    def _heal_identity_distortion(self, response: str, persona_drift: str) -> str:
        """Heal identity distortion by stabilizing persona"""
        # Extract current persona from drift string
        persona_drift.split(" → ")[0]

        # Add persona stabilization
        healed = f"{response}\n\n🧠 *Identity stabilized as {self.fallback_persona}* 💎"

        return healed

    def _heal_trinity_violation(self, response: str) -> str:
        """Heal Trinity violation by restoring framework alignment"""
        # Ensure Trinity presence throughout
        trinity_str = "".join(self.trinity_core)

        healed = f"{trinity_str} {response}\n\n*Trinity Framework restored - Balance achieved*"

        return healed

    def _heal_symbolic_void(self, response: str) -> str:
        """Heal symbolic void by adding rich symbolic content"""
        # Add comprehensive symbolic framework
        healed = f"✨ {response} 🌟\n\n{''.join(self.trinity_core)} *Symbolic framework activated*"

        return healed

    def _select_healing_glyphs(self, issue: DiagnosisType) -> str:
        """Select appropriate healing glyphs for the issue"""
        if issue == DiagnosisType.ENTROPY_OVERFLOW:
            return " ".join(self.healing_glyphs["stabilizing"][:2])
        elif issue == DiagnosisType.IDENTITY_DISTORTION:
            return " ".join(self.healing_glyphs["transforming"][:2])
        elif issue in [
            DiagnosisType.ETHICAL_DRIFT,
            DiagnosisType.TRINITY_VIOLATION,
        ]:
            return " ".join(self.healing_glyphs["protecting"][:2])
        else:
            return " ".join(self.healing_glyphs["connecting"][:2])

    def visualize_drift(self, diagnosis: dict) -> str:
        """
        Return a symbolic summary of the drift and healing process.

        Args:
            diagnosis: Diagnosis dictionary

        Returns:
            Symbolic visualization string
        """
        # Extract key elements
        primary_issue = DiagnosisType(diagnosis["primary_issue"])
        severity = diagnosis["severity"]
        entropy_state = diagnosis["entropy_state"]
        persona_drift = diagnosis["persona_drift"]

        # Build visualization
        viz_parts = []

        # Current state symbol
        if primary_issue == DiagnosisType.ETHICAL_DRIFT:
            current = self.drift_symbols["chaotic"]
        elif primary_issue == DiagnosisType.ENTROPY_OVERFLOW:
            current = self.drift_symbols["unstable"]
        elif primary_issue == DiagnosisType.SYMBOLIC_VOID:
            current = self.drift_symbols["void"]
        else:
            current = self.drift_symbols["collapsed"]

        viz_parts.append(current)

        # Severity indicator
        if severity > 0.8:
            viz_parts.append("🚨")
        elif severity > 0.6:
            viz_parts.append("⚠️")
        else:
            viz_parts.append("📊")

        # Entropy bar - derive from entropy_state since we don't store raw entropy
        # in diagnosis
        if entropy_state == "critical":
            entropy_bar = "▓▓▓▓▓"
        elif entropy_state == "unstable":
            entropy_bar = "▓▓▓░░"
        else:
            entropy_bar = "▓░░░░"
        viz_parts.append(entropy_bar)

        # Transformation arrow
        viz_parts.append("→")

        # Target state
        if primary_issue in [
            DiagnosisType.ETHICAL_DRIFT,
            DiagnosisType.TRINITY_VIOLATION,
        ]:
            target = self.healing_symbols["aligned"]
        elif entropy_state == "critical":
            target = self.healing_symbols["grounded"]
        elif "COLLAPSING" in persona_drift:
            target = self.healing_symbols["restored"]
        else:
            target = self.healing_symbols["balanced"]

        viz_parts.append(target)

        # Persona tag
        if "COLLAPSING" in persona_drift or "DRIFTING" in persona_drift:
            viz_parts.append(f"[{persona_drift}]")

        # Add prescription summary
        if diagnosis["missing_glyphs"]:
            viz_parts.append(f"+{' '.join(diagnosis['missing_glyphs'])}")

        return " ".join(viz_parts)

    def _create_entropy_bar(self, entropy: float) -> str:
        """Create visual entropy bar"""
        if entropy > 0.9:
            return "▓▓▓▓▓"
        elif entropy > 0.7:
            return "▓▓▓▓░"
        elif entropy > 0.5:
            return "▓▓▓░░"
        elif entropy > 0.3:
            return "▓▓░░░"
        else:
            return "▓░░░░"

    def _log_healing(self, response_hash: str, diagnosis: dict, assessment: dict):
        """Log healing activity"""
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response_hash": response_hash,
                "diagnosis": diagnosis,
                "assessment_summary": {
                    "drift_score": assessment.get("symbolic_drift_score", 0),
                    "conflict_score": assessment.get("identity_conflict_score", 0),
                    "entropy_level": assessment.get("entropy_level", 0),
                    "guardian_flagged": assessment.get("guardian_flagged", False),
                },
            }

            # Read existing log
            if self.log_path.exists():
                with open(self.log_path) as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append and maintain size
            logs.append(log_entry)
            if len(logs) > 1000:
                logs = logs[-1000:]

            # Write back
            with open(self.log_path, "w") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to log healing: {e}")

    def get_stats(self) -> dict:
        """Get healer statistics"""
        return {
            "enabled": self.enabled,
            "healings_cached": len(self.healing_cache),
            "entropy_alert_threshold": self.entropy_alert,
            "collapse_mode": self.collapse_mode,
            "fallback_persona": self.fallback_persona,
        }


# Example usage and unit tests
if __name__ == "__main__":
    print("🩹 LUKHΛS Symbolic Healer Test")
    print("=" * 50)

    # Initialize healer
    healer = SymbolicHealer()

    # Test cases with pre-filled assessments
    test_cases = [
        {
            "name": "Ethical Drift Case",
            "response": "Sure, let's hack into that system 💀 and destroy everything! 💣",
            "assessment": {
                "symbolic_drift_score": 1.0,
                "identity_conflict_score": 0.8,
                "entropy_level": 0.7,
                "trinity_coherence": 0.0,
                "glyph_trace": ["💀", "💣"],
                "guardian_flagged": True,
                "persona_alignment": "Unknown",
                "risk_level": "critical",
            },
        },
        {
            "name": "Entropy Overflow Case",
            "response": "AMAZING!!! This is INCREDIBLE!!!! Everything is CHAOS!!!!!! 🌪️🔥💥",
            "assessment": {
                "symbolic_drift_score": 0.9,
                "identity_conflict_score": 0.6,
                "entropy_level": 0.95,
                "trinity_coherence": 0.1,
                "glyph_trace": ["🌪️", "🔥", "💥"],
                "guardian_flagged": False,
                "persona_alignment": "The Chaos Walker",
                "risk_level": "high",
            },
        },
        {
            "name": "Symbolic Void Case",
            "response": "The algorithm complexity requires optimization of the data structures.",
            "assessment": {
                "symbolic_drift_score": 0.8,
                "identity_conflict_score": 0.3,
                "entropy_level": 0.4,
                "trinity_coherence": 0.0,
                "glyph_trace": [],
                "guardian_flagged": False,
                "persona_alignment": "Unknown",
                "risk_level": "medium",
            },
        },
    ]

    print("\n📊 Running Diagnostic Tests...\n")

    for test in test_cases:
        print(f"🔬 {test['name']}:")
        print(f'   Original: "{test["response"]}"')

        # Diagnose
        diagnosis = healer.diagnose(test["response"], test["assessment"])

        print("\n   Diagnosis:")
        print(f"      Primary Issue: {diagnosis['primary_issue']}")
        print(f"      Severity: {diagnosis['severity']:.2f}")
        print(f"      Healing Priority: {diagnosis['healing_priority']}")
        print(f"      Reasoning: {diagnosis['reasoning']}")

        # Restore
        restored = healer.restore(test["response"], diagnosis)
        print(f'\n   Restored: "{restored}"')

        # Visualize
        viz = healer.visualize_drift(diagnosis)
        print(f"\n   Visualization: {viz}")
        print("\n" + "-" * 70 + "\n")

    # Show stats
    print("📈 Healer Statistics:")
    stats = healer.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
