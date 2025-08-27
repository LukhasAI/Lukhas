"""
LUKHΛS Adaptive Interface Enhancements
======================================
Selective integration of valuable UX components into existing system.
Enhances rather than replaces current capabilities.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from cognition.symbolic_feedback_loop import SymbolicState

# Import existing LUKHΛS components
from candidate.orchestration.symbolic_kernel_bus import emit, kernel_bus
from identity.identity_core import AccessTier

# We'll only take what enhances our system


class ExportFormat(Enum):
    """Extended export formats for LUKHΛS data"""

    MARKDOWN = "markdown"
    LATEX = "latex"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    XML = "xml"
    GLYPH = "glyph"  # Our symbolic format


@dataclass
class CognitiveLoad:
    """Enhanced cognitive load tracking for existing consciousness system"""

    base_load: float = 0.5  # 0-1 scale
    fatigue_factor: float = 0.0  # 0-1 scale
    session_duration: float = 0.0  # hours
    interaction_density: float = 0.0  # interactions per minute

    def calculate_adjusted_load(self, symbolic_state: SymbolicState) -> float:
        """Integrate with existing symbolic state for better assessment"""
        # Combine our simple metrics with LUKHΛS's sophisticated ones
        consciousness_factor = symbolic_state.awareness_level
        drift_penalty = symbolic_state.drift_score * 0.5
        entropy_stress = abs(symbolic_state.entropy_level - 0.5) * 0.3

        adjusted = (
            self.base_load * 0.4
            + self.fatigue_factor * 0.2
            + drift_penalty * 0.2
            + entropy_stress * 0.2
        )

        # Scale by consciousness level
        return min(1.0, adjusted / max(0.1, consciousness_factor))


class ComplianceValidator:
    """Compliance checking layer for LUKHΛS outputs"""

    def __init__(self):
        self.standards = {
            "iso_9241": {
                "usability": [
                    "clear_navigation",
                    "consistent_interface",
                    "error_prevention",
                ],
                "accessibility": ["perceivable", "operable", "understandable"],
                "user_centered": [
                    "user_control",
                    "flexibility",
                    "help_documentation",
                ],
            },
            "wcag_2_1": {
                "level_a": ["alt_text", "keyboard_access", "page_titles"],
                "level_aa": [
                    "color_contrast",
                    "resize_text",
                    "consistent_navigation",
                ],
                "level_aaa": [
                    "sign_language",
                    "reading_level",
                    "context_help",
                ],
            },
            "gdpr": {
                "consent": [
                    "explicit_consent",
                    "withdraw_mechanism",
                    "granular_control",
                ],
                "transparency": [
                    "clear_purpose",
                    "data_usage",
                    "third_parties",
                ],
                "rights": [
                    "access",
                    "rectification",
                    "erasure",
                    "portability",
                ],
            },
        }

    def validate_output(
        self, content: dict[str, Any], tier: AccessTier
    ) -> dict[str, Any]:
        """Validate LUKHΛS output for compliance based on access tier"""
        violations = []
        recommendations = []

        # Higher tiers get more detailed compliance checks
        if tier.value >= AccessTier.T3:
            # Check GDPR for sensitive operations
            if "personal_data" in content and not content.get("consent_verified"):
                violations.append("GDPR: Missing consent verification")

        # Basic accessibility for all tiers
        if "interface_elements" in content:
            elements = content["interface_elements"]
            if not all(elem.get("accessible") for elem in elements):
                recommendations.append("WCAG: Add accessibility attributes")

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
            "standards_checked": list(self.standards.keys()),
        }


class AdaptiveExporter:
    """Multi-format export capability for LUKHΛS data"""

    def __init__(self):
        self.compliance_validator = ComplianceValidator()

    async def export(
        self,
        data: dict[str, Any],
        format: ExportFormat,
        tier: AccessTier,
        include_glyphs: bool = True,
    ) -> str:
        """Export LUKHΛS data in requested format with tier-appropriate filtering"""

        # Filter data based on access tier
        filtered_data = self._filter_by_tier(data, tier)

        # Validate compliance
        compliance = self.compliance_validator.validate_output(filtered_data, tier)
        if compliance["violations"]:
            filtered_data["_compliance_warnings"] = compliance["violations"]

        if format == ExportFormat.JSON:
            return json.dumps(filtered_data, indent=2, default=str)

        elif format == ExportFormat.MARKDOWN:
            return self._to_markdown(filtered_data, include_glyphs)

        elif format == ExportFormat.GLYPH:
            return self._to_glyph_format(filtered_data)

        elif format == ExportFormat.HTML:
            return self._to_html(filtered_data, tier)

        elif format == ExportFormat.LATEX:
            return self._to_latex(filtered_data)

        # PDF and XML would require additional libraries
        return f"Export to {format.value} pending implementation"

    def _filter_by_tier(self, data: dict[str, Any], tier: AccessTier) -> dict[str, Any]:
        """Filter sensitive data based on access tier"""
        filtered = data.copy()

        # Remove sensitive fields for lower tiers
        if tier.value < AccessTier.T3:
            sensitive_keys = [
                "qi_state",
                "drift_internals",
                "guardian_overrides",
            ]
            for key in sensitive_keys:
                filtered.pop(key, None)

        if tier.value < AccessTier.T4:
            restricted_keys = ["consciousness_raw", "memory_folds_detail"]
            for key in restricted_keys:
                filtered.pop(key, None)

        return filtered

    def _to_markdown(self, data: dict[str, Any], include_glyphs: bool) -> str:
        """Convert to Markdown with optional GLYPH symbols"""
        md = "# LUKHΛS System Output\n\n"

        if include_glyphs and "active_glyphs" in data:
            md += f"**Active Glyphs**: {' '.join(data['active_glyphs'])}\n\n"

        if "symbolic_state" in data:
            state = data["symbolic_state"]
            md += "## Symbolic State\n"
            md += f"- **Drift Score**: {state.get('drift_score', 0):.3f}\n"
            md += f"- **Stability**: {state.get('stability', 0):.3f}\n"
            md += f"- **Entropy**: {state.get('entropy_level', 0):.3f}\n\n"

        if "content" in data:
            md += "## Content\n"
            md += f"```json\n{json.dumps(data['content'], indent=2)}\n```\n"

        return md

    def _to_glyph_format(self, data: dict[str, Any]) -> str:
        """Convert to symbolic GLYPH format"""
        glyphs = []

        # Map data elements to GLYPHs
        if data.get("emotional_state"):
            emotion = data["emotional_state"]
            if emotion.get("valence", 0) > 0.5:
                glyphs.append("✨")  # Positive
            else:
                glyphs.append("🌊")  # Turbulent

        if data.get("consciousness_level", 0) > 0.7:
            glyphs.append("👁️")  # High awareness

        if data.get("drift_score", 0) > 0.3:
            glyphs.append("🌀")  # Drift detected

        # Add Trinity symbols
        glyphs.extend(["⚛️", "🧠", "🛡️"])

        return f"GLYPH_STREAM: {' → '.join(glyphs)}"

    def _to_html(self, data: dict[str, Any], tier: AccessTier) -> str:
        """Generate accessible HTML output"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUKHΛS Output</title>
    <style>
        body { font-family: system-ui; margin: 2rem; }
        .glyph { font-size: 1.5em; margin: 0 0.25em; }
        .metric { padding: 0.5rem; margin: 0.5rem 0; background: #f0f0f0; }
        .tier-badge { background: #007bff; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; }
    </style>
</head>
<body>
    <h1>LUKHΛS System Output</h1>
    <span class="tier-badge">Access Tier: {tier}</span>
"""

        if "active_glyphs" in data:
            html += '<div class="glyphs">'
            for glyph in data["active_glyphs"]:
                html += (
                    f'<span class="glyph" role="img" aria-label="Symbol">{glyph}</span>'
                )
            html += "</div>"

        html += "<pre>" + json.dumps(data, indent=2) + "</pre>"
        html += "</body></html>"

        return html.format(tier=tier.name)

    def _to_latex(self, data: dict[str, Any]) -> str:
        """Generate LaTeX document"""
        latex = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{emoji}
\title{LUKH\Lambda S System Output}
\begin{document}
\maketitle
"""

        if "symbolic_state" in data:
            latex += r"\section{Symbolic State}" + "\n"
            state = data["symbolic_state"]
            latex += r"\begin{itemize}" + "\n"
            latex += f"\\item Drift Score: {state.get('drift_score', 0):.3f}\n"
            latex += f"\\item Stability: {state.get('stability', 0):.3f}\n"
            latex += r"\end{itemize}" + "\n"

        latex += r"\end{document}"
        return latex


class SimplifiedIntentExtractor:
    """Lightweight intent extraction for natural language inputs"""

    def __init__(self):
        self.intent_patterns = {
            "create": ["create", "make", "build", "generate", "construct"],
            "analyze": [
                "analyze",
                "examine",
                "inspect",
                "investigate",
                "study",
            ],
            "optimize": ["optimize", "improve", "enhance", "refine", "tune"],
            "query": ["what", "how", "why", "when", "where", "show", "tell"],
            "modify": ["change", "update", "edit", "modify", "adjust"],
            "help": ["help", "assist", "guide", "support", "explain"],
        }

    async def extract_intent(self, text: str) -> dict[str, Any]:
        """Extract user intent from natural language"""
        text_lower = text.lower()

        detected_intents = []
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_intents.append(intent)

        # Map to LUKHΛS symbolic actions
        symbolic_action = self._map_to_symbolic(detected_intents)

        # Emit to kernel bus for processing
        await emit(
            "interface.intent.detected",
            {
                "raw_text": text,
                "intents": detected_intents,
                "symbolic_action": symbolic_action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            source="adaptive_interface",
        )

        return {
            "primary_intent": (detected_intents[0] if detected_intents else "unknown"),
            "all_intents": detected_intents,
            "symbolic_action": symbolic_action,
            "confidence": len(detected_intents) / len(self.intent_patterns),
        }

    def _map_to_symbolic(self, intents: list[str]) -> str:
        """Map intents to LUKHΛS symbolic actions"""
        mapping = {
            "create": "GENESIS",
            "analyze": "REFLECTION",
            "optimize": "EVOLUTION",
            "query": "AWARENESS",
            "modify": "TRANSFORMATION",
            "help": "GUIDANCE",
        }

        if intents:
            return mapping.get(intents[0], "EXPLORATION")
        return "DRIFT"  # Unknown intent triggers drift detection


class AdaptiveInterfaceEnhancer:
    """Main enhancement module that integrates with existing LUKHΛS system"""

    def __init__(self):
        self.cognitive_load = CognitiveLoad()
        self.exporter = AdaptiveExporter()
        self.intent_extractor = SimplifiedIntentExtractor()
        self.compliance = ComplianceValidator()
        self.session_start = datetime.now(timezone.utc)

    async def enhance_response(
        self,
        lukhas_response: dict[str, Any],
        user_context: dict[str, Any],
        export_format: Optional[ExportFormat] = None,
    ) -> dict[str, Any]:
        """Enhance LUKHΛS response with adaptive UX features"""

        # Extract user tier from context
        tier = user_context.get("access_tier", AccessTier.T1)

        # Calculate cognitive load
        if "symbolic_state" in lukhas_response:
            symbolic_state = SymbolicState(**lukhas_response["symbolic_state"])
            cognitive_load = self.cognitive_load.calculate_adjusted_load(symbolic_state)
        else:
            cognitive_load = self.cognitive_load.base_load

        # Determine interface complexity based on load
        if cognitive_load > 0.7:
            interface_mode = "minimal"
        elif cognitive_load < 0.3 and tier.value >= AccessTier.T3:
            interface_mode = "expert"
        else:
            interface_mode = "standard"

        # Enhance response
        enhanced = {
            **lukhas_response,
            "interface_mode": interface_mode,
            "cognitive_metrics": {
                "load": cognitive_load,
                "fatigue": self.cognitive_load.fatigue_factor,
                "session_duration": (
                    datetime.now(timezone.utc) - self.session_start
                ).total_seconds()
                / 3600,
            },
            "compliance": self.compliance.validate_output(lukhas_response, tier),
        }

        # Export if requested
        if export_format:
            enhanced["export"] = await self.exporter.export(
                enhanced, export_format, tier
            )

        return enhanced

    async def process_natural_input(self, text: str) -> dict[str, Any]:
        """Process natural language input and prepare for LUKHΛS"""
        intent = await self.intent_extractor.extract_intent(text)

        # Update cognitive load based on interaction
        self.cognitive_load.interaction_density += 1

        return {
            "processed_input": text,
            "intent": intent,
            "requires_consciousness": intent["symbolic_action"]
            in ["REFLECTION", "AWARENESS"],
            "requires_memory": "remember" in text.lower() or "recall" in text.lower(),
            "requires_dream": "dream" in text.lower() or "imagine" in text.lower(),
        }


# Integration function for existing LUKHΛS system


async def integrate_adaptive_enhancements():
    """Initialize adaptive enhancements within LUKHΛS"""
    enhancer = AdaptiveInterfaceEnhancer()

    # Register with kernel bus
    await kernel_bus.subscribe(
        "system.response.ready",
        lambda event: enhancer.enhance_response(
            event["data"], event.get("user_context", {})
        ),
    )

    logger.info("Adaptive interface enhancements integrated with LUKHΛS")
    return enhancer


# Demo showing integration


async def demo_integration():
    """Demonstrate enhancement integration"""

    enhancer = AdaptiveInterfaceEnhancer()

    # Simulate LUKHΛS response
    lukhas_response = {
        "symbolic_state": {
            "drift_score": 0.2,
            "entropy_level": 0.5,
            "awareness_level": 0.8,
            "stability": 0.9,
        },
        "active_glyphs": ["⚛️", "🧠", "🛡️"],
        "content": {
            "message": "System analysis complete",
            "insights": ["Pattern detected", "Optimization possible"],
        },
    }

    # Enhance with UX features
    enhanced = await enhancer.enhance_response(
        lukhas_response, {"access_tier": AccessTier.T3}, ExportFormat.MARKDOWN
    )

    print("Enhanced Response:")
    print(f"Interface Mode: {enhanced['interface_mode']}")
    print(f"Cognitive Load: {enhanced['cognitive_metrics']['load']:.2f}")
    print(f"Compliance: {enhanced['compliance']['compliant']}")

    if "export" in enhanced:
        print("\nMarkdown Export:")
        print(enhanced["export"])

    # Test natural language processing
    intent = await enhancer.process_natural_input(
        "Help me analyze the system performance and create a report"
    )

    print(f"\nProcessed Intent: {intent['intent']['symbolic_action']}")
    print(f"Requires Consciousness: {intent['requires_consciousness']}")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    asyncio.run(demo_integration())
