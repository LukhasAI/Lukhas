"""
LUKHΛS Intent Router
====================

Natural Language Understanding for routing user intents to appropriate handlers.
Integrates with Trinity Framework for symbolic understanding.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Supported intent types in LUKHΛS system."""

    QUERY_MEMORY = "query_memory"
    EXPLORE_CONSCIOUSNESS = "explore_consciousness"
    CHECK_DRIFT = "check_drift"
    ANALYZE_TRINITY = "analyze_trinity"
    REQUEST_INTERVENTION = "request_intervention"
    SYSTEM_STATUS = "system_status"
    SYMBOLIC_TRANSLATION = "symbolic_translation"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Detected intent with confidence and parameters."""

    type: IntentType
    confidence: float
    parameters: dict[str, Any]
    raw_text: str
    glyphs: list[str]


class IntentRouter:
    """
    Routes natural language queries to appropriate system handlers.
    Uses pattern matching and symbolic understanding.
    """

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.glyph_map = self._initialize_glyph_map()

    def _initialize_patterns(:
        self,
    ) -> dict[IntentType, list[tuple[str, float]]]:
        """Initialize regex patterns for intent detection."""
        return {
            IntentType.QUERY_MEMORY: [
                (
                    r"(show|find|search|get|retrieve)\s+(memory|memories|fold|folds)",
                    0.9,
                ),
                (r"what do you remember about", 0.8),
                (r"recall.*about", 0.7),
                (r"memory.*(?:of|about|regarding)", 0.8),
            ],
            IntentType.EXPLORE_CONSCIOUSNESS: [
                (
                    r"(explore|show|display)\s+(consciousness|awareness|state)",
                    0.9,
                ),
                (r"consciousness.*(?:level|state|status)", 0.8),
                (r"how.*(?:aware|conscious)", 0.7),
                (r"trinity.*(?:score|status)", 0.8),
            ],
            IntentType.CHECK_DRIFT: [
                (r"(check|show|monitor)\s+(drift|deviation|anomaly)", 0.9),
                (r"drift.*(?:score|level|status)", 0.8),
                (r"(?:ethical|behavioral)\s+drift", 0.9),
                (r"guardian.*intervention", 0.7),
            ],
            IntentType.ANALYZE_TRINITY: [
                (r"trinity.*(?:framework|status|analysis)", 0.9),
                (r"analyze.*trinity", 0.8),
                (
                    r"(?:identity|consciousness|guardian)\s+(?:status|health)",
                    0.7,
                ),
            ],
            IntentType.REQUEST_INTERVENTION: [
                (
                    r"(?:need|require|request)\s+(?:help|intervention|guardian)",
                    0.9,
                ),
                (r"emergency|urgent|critical", 0.8),
                (r"intervene|protect|shield", 0.7),
            ],
            IntentType.SYSTEM_STATUS: [
                (r"(?:system|module)\s+(?:status|health|check)", 0.9),
                (r"(?:what|how)\s+is.*(?:working|functioning)", 0.7),
                (r"operational.*status", 0.8),
            ],
            IntentType.SYMBOLIC_TRANSLATION: [
                (r"(?:translate|convert|explain).*(?:symbol|glyph)", 0.9),
                (r"what.*(?:mean|means|meaning)", 0.7),
                (r"symbolic.*(?:meaning|interpretation)", 0.8),
            ],
        }

    def _initialize_glyph_map(self) -> dict[str, list[str]]:
        """Map intents to relevant glyphs."""
        return {
            IntentType.QUERY_MEMORY.value: ["🧠", "💭", "📚"],
            IntentType.EXPLORE_CONSCIOUSNESS.value: ["🧠", "👁️", "✨"],
            IntentType.CHECK_DRIFT.value: ["⚠️", "📊", "🔍"],
            IntentType.ANALYZE_TRINITY.value: ["⚛️", "🧠", "🛡️"],
            IntentType.REQUEST_INTERVENTION.value: ["🛡️", "⚡", "🆘"],
            IntentType.SYSTEM_STATUS.value: ["📊", "✅", "🔍"],
            IntentType.SYMBOLIC_TRANSLATION.value: ["🔤", "🔮", "📖"],
        }

    def detect_intent(self, text: str) -> Intent:
        """
        Detect intent from natural language text.

        Args:
            text: User input text

        Returns:
            Detected Intent with confidence and parameters
        """
        text_lower = text.lower().strip()
        best_match = IntentType.UNKNOWN
        best_confidence = 0.0
        parameters = {}

        # Check each intent pattern
        for intent_type, patterns in self.patterns.items():
            for pattern, base_confidence in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Adjust confidence based on match quality
                    confidence = base_confidence
                    if match.group(0) == text_lower:  # Full match:
                        confidence = min(1.0, confidence + 0.1)

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent_type
                        parameters = self._extract_parameters(text, intent_type, match)

        # Get relevant glyphs
        glyphs = self.glyph_map.get(best_match.value, ["❓"])

        return Intent(
            type=best_match,
            confidence=best_confidence,
            parameters=parameters,
            raw_text=text,
            glyphs=glyphs,
        )

    def _extract_parameters(:
        self, text: str, intent_type: IntentType, match: re.Match
    ) -> dict[str, Any]:
        """Extract relevant parameters from the matched text."""
        parameters = {}

        # Extract time references
        time_patterns = [
            (r"(?:last|past)\s+(\d+)\s+(hour|day|week|month)", "time_range"),
            (r"(?:since|after|before)\s+(.+?)(?:\s|$)", "time_reference"),
            (r"(?:on|at)\s+(\d{4}-\d{2}-\d{2})", "specific_date"),
        ]

        for pattern, param_name in time_patterns:
            time_match = re.search(pattern, text.lower())
            if time_match:
                parameters[param_name] = time_match.group(1)

        # Extract entity references
        if intent_type == IntentType.QUERY_MEMORY:
            # Look for specific topics
            topic_match = re.search(
                r"about\s+(.+?)(?:\s+(?:from|since|before)|$)", text.lower()
            )
            if topic_match:
                parameters["topic"] = topic_match.group(1).strip()

        # Extract module names
        modules = [
            "consciousness",
            "memory",
            "guardian",
            "identity",
            "quantum",
            "emotion",
        ]
        for module in modules:
            if module in text.lower():
                parameters["module"] = module
                break

        return parameters

    def route_to_handler(self, intent: Intent) -> dict[str, Any]:
        """
        Route detected intent to appropriate handler.

        Args:
            intent: Detected intent

        Returns:
            Handler response with action and data
        """
        handlers = {
            IntentType.QUERY_MEMORY: self._handle_memory_query,
            IntentType.EXPLORE_CONSCIOUSNESS: self._handle_consciousness_exploration,
            IntentType.CHECK_DRIFT: self._handle_drift_check,
            IntentType.ANALYZE_TRINITY: self._handle_trinity_analysis,
            IntentType.REQUEST_INTERVENTION: self._handle_intervention_request,
            IntentType.SYSTEM_STATUS: self._handle_system_status,
            IntentType.SYMBOLIC_TRANSLATION: self._handle_symbolic_translation,
        }

        handler = handlers.get(intent.type, self._handle_unknown)
        return handler(intent)

    def _handle_memory_query(self, intent: Intent) -> dict[str, Any]:
        """Handle memory-related queries."""
        return {
            "action": "query_memory",
            "endpoint": "/api/memory/explore",
            "parameters": intent.parameters,
            "glyphs": intent.glyphs,
            "message": f"Searching memory folds for: {intent.parameters.get('topic',"}
                                                                            'all memories')}",
        }

    def _handle_consciousness_exploration(self, intent: Intent) -> dict[str, Any]:
        """Handle consciousness exploration requests."""
        return {
            "action": "explore_consciousness",
            "endpoint": "/api/consciousness/state",
            "parameters": intent.parameters,
            "glyphs": intent.glyphs,
            "message": "Exploring consciousness state and Trinity alignment",
        }

    def _handle_drift_check(self, intent: Intent) -> dict[str, Any]:
        """Handle drift monitoring requests."""
        return {
            "action": "check_drift",
            "endpoint": "/api/guardian/drift",
            "parameters": intent.parameters,
            "glyphs": intent.glyphs,
            "message": "Checking system drift and Guardian status",
        }

    def _handle_trinity_analysis(self, intent: Intent) -> dict[str, Any]:
        """Handle Trinity Framework analysis."""
        return {
            "action": "analyze_trinity",
            "endpoint": "/api/trinity/status",
            "parameters": intent.parameters,
            "glyphs": ["⚛️", "🧠", "🛡️"],
            "message": "Analyzing Trinity Framework coherence",
        }

    def _handle_intervention_request(self, intent: Intent) -> dict[str, Any]:
        """Handle Guardian intervention requests."""
        return {
            "action": "request_intervention",
            "endpoint": "/api/guardian/intervene",
            "parameters": {
                **intent.parameters,
                "urgency": "high",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "glyphs": intent.glyphs,
            "message": "Guardian intervention requested - analyzing situation",
        }

    def _handle_system_status(self, intent: Intent) -> dict[str, Any]:
        """Handle system status queries."""
        module = intent.parameters.get("module", "all")
        return {
            "action": "system_status",
            "endpoint": f"/api/status/{module}",
            "parameters": intent.parameters,
            "glyphs": intent.glyphs,
            "message": f"Checking {module} system status",
        }

    def _handle_symbolic_translation(self, intent: Intent) -> dict[str, Any]:
        """Handle symbolic translation requests."""
        return {
            "action": "symbolic_translation",
            "endpoint": "/api/symbolic/translate",
            "parameters": intent.parameters,
            "glyphs": intent.glyphs,
            "message": "Translating symbolic meanings",
        }

    def _handle_unknown(self, intent: Intent) -> dict[str, Any]:
        """Handle unknown intents."""
        return {
            "action": "unknown",
            "endpoint": None,
            "parameters": intent.parameters,
            "glyphs": ["❓", "🤔"],
            "message": "I'm not sure what you're asking. Could you please rephrase?",
            "suggestions": [
                "Query memory about [topic]",
                "Show consciousness state",
                "Check drift status",
                "Analyze Trinity Framework",
            ],
        }


# Global router instance
intent_router = IntentRouter()