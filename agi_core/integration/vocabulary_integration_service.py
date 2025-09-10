"""
AGI Vocabulary Integration Service
=================================

Service that integrates AGI vocabulary with existing LUKHAS systems, providing
seamless symbolic communication across all consciousness modules.

This service:
- Automatically translates AGI operations to appropriate vocabularies
- Enriches system messages with cross-vocabulary context
- Provides unified logging with symbolic consistency
- Manages vocabulary versioning and updates
- Validates cross-system symbolic integrity

Part of Phase 2A: Core Integrations - Symbolic vocabulary unification
Created: 2025-09-05
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional

try:
    from agi_core.vocabulary import (
        agi_bridge,
        format_agi_message,
        get_agi_symbol,
        get_vocabulary_context,
        translate_agi_to_bio,
        translate_agi_to_dream,
    )
except ImportError:
    # Fallback for development
    class MockBridge:
        def get_agi_symbol(self, op: str, default: str = "🧠") -> str:
            return default

        def format_agi_message(self, op: str, details: str = "", cross_ref: bool = True) -> str:
            return f"🧠 {op}: {details}"

        def get_vocabulary_context(self, op: str) -> dict[str, Any]:
            return {"operation": op, "agi_symbol": "🧠"}

    agi_bridge = MockBridge()
    get_agi_symbol = agi_bridge.get_agi_symbol
    format_agi_message = agi_bridge.format_agi_message
    get_vocabulary_context = agi_bridge.get_vocabulary_context

    def translate_agi_to_dream(_x):
        return "🌙"

    def translate_agi_to_bio(_x):
        return "🧠"


@dataclass
class VocabularyEvent:
    """Represents a vocabulary-enriched system event."""

    timestamp: datetime
    operation: str
    agi_symbol: str
    message: str
    cross_references: dict[str, str]
    context: dict[str, Any]
    module: str
    severity: str = "INFO"


@dataclass
class VocabularyMetrics:
    """Metrics for vocabulary integration performance."""

    total_translations: int = 0
    cross_references_created: int = 0
    vocabulary_conflicts: int = 0
    integration_errors: int = 0
    last_update: Optional[datetime] = None


class VocabularyIntegrationService:
    """
    Central service for AGI vocabulary integration with LUKHAS consciousness systems.

    Provides unified symbolic communication, cross-vocabulary translation,
    and enriched logging for all AGI operations within the LUKHAS ecosystem.
    """

    def __init__(self, enable_logging: bool = True, log_level: str = "INFO"):
        self.bridge = agi_bridge
        self.metrics = VocabularyMetrics()
        self.event_history: list[VocabularyEvent] = []
        self.max_history = 1000  # Keep last 1000 events

        # Logging setup
        self.enable_logging = enable_logging
        if enable_logging:
            self.logger = logging.getLogger("agi_vocabulary")
            self.logger.setLevel(getattr(logging, log_level))

            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(name)s - [%(levelname)s] - %(message)s")
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = None

    def create_enriched_event(
        self, operation: str, details: str = "", module: str = "agi_core", severity: str = "INFO"
    ) -> VocabularyEvent:
        """
        Create a vocabulary-enriched event with cross-system context.

        Args:
            operation: AGI operation name (e.g., 'chain_start', 'model_consensus')
            details: Additional operation details
            module: Source module name
            severity: Event severity level

        Returns:
            VocabularyEvent with full symbolic context
        """
        # Get AGI symbol and context
        agi_symbol = get_agi_symbol(operation)
        full_context = get_vocabulary_context(operation)

        # Create cross-references
        cross_refs = {}
        if "cross_references" in full_context:
            for vocab_type in full_context["cross_references"]:
                if vocab_type == "dream":
                    cross_refs["dream"] = translate_agi_to_dream(operation)
                elif vocab_type == "bio":
                    cross_refs["bio"] = translate_agi_to_bio(operation)

        # Format enriched message
        enriched_message = format_agi_message(operation, details, include_cross_ref=True)

        # Create event
        event = VocabularyEvent(
            timestamp=datetime.now(timezone.utc),
            operation=operation,
            agi_symbol=agi_symbol,
            message=enriched_message,
            cross_references=cross_refs,
            context=full_context,
            module=module,
            severity=severity,
        )

        # Update metrics
        self.metrics.total_translations += 1
        self.metrics.cross_references_created += len(cross_refs)
        self.metrics.last_update = event.timestamp

        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        return event

    def log_agi_operation(
        self, operation: str, details: str = "", module: str = "agi_core", severity: str = "INFO"
    ) -> VocabularyEvent:
        """
        Log an AGI operation with enriched vocabulary context.

        This is the main method for logging AGI operations throughout the system.
        It automatically handles vocabulary translation, cross-referencing, and
        integration with existing LUKHAS logging systems.
        """
        event = self.create_enriched_event(operation, details, module, severity)

        if self.logger:
            log_level = getattr(logging, severity, logging.INFO)
            self.logger.log(log_level, event.message)

        return event

    def translate_for_module(self, operation: str, target_module: str) -> str:
        """
        Translate an AGI operation to the vocabulary of a target module.

        Args:
            operation: AGI operation name
            target_module: Target module ('dream', 'bio', 'emotion', etc.)

        Returns:
            Translated symbol appropriate for the target module
        """
        if target_module == "dream":
            return translate_agi_to_dream(operation)
        elif target_module == "bio":
            return translate_agi_to_bio(operation)
        else:
            # Default to AGI symbol
            return get_agi_symbol(operation)

    def create_module_message(self, operation: str, target_module: str, details: str = "") -> str:
        """
        Create a message formatted for a specific target module.

        Useful when AGI operations need to communicate with specific
        LUKHAS modules using their native vocabulary.
        """
        translated_symbol = self.translate_for_module(operation, target_module)

        if target_module == "dream":
            return f"{translated_symbol} Dream-guided {operation.replace('_', ' ')}: {details}"
        elif target_module == "bio":
            return f"{translated_symbol} Bio-enhanced {operation.replace('_', ' ')}: {details}"
        else:
            return f"{translated_symbol} {operation.replace('_', ' ')}: {details}"

    def get_vocabulary_health(self) -> dict[str, Any]:
        """
        Get health metrics for the vocabulary integration system.

        Returns comprehensive metrics about vocabulary performance,
        translation success rates, and integration quality.
        """
        # Validate vocabulary consistency
        if hasattr(self.bridge, "validate_vocabulary_consistency"):
            issues = self.bridge.validate_vocabulary_consistency()
        else:
            issues = {"missing_mappings": [], "symbol_conflicts": [], "orphaned_references": []}

        return {
            "metrics": asdict(self.metrics),
            "vocabulary_issues": issues,
            "event_history_size": len(self.event_history),
            "recent_operations": [event.operation for event in self.event_history[-10:]],
            "cross_reference_coverage": (
                self.metrics.cross_references_created / max(self.metrics.total_translations, 1)
            ),
            "health_status": "healthy" if len(issues["symbol_conflicts"]) == 0 else "warning",
        }

    def export_vocabulary_analytics(self) -> dict[str, Any]:
        """
        Export comprehensive vocabulary analytics for monitoring and debugging.

        Provides detailed insights into vocabulary usage patterns,
        translation performance, and cross-system integration quality.
        """
        # Operation frequency analysis
        operation_counts = {}
        module_counts = {}
        severity_counts = {}

        for event in self.event_history:
            operation_counts[event.operation] = operation_counts.get(event.operation, 0) + 1
            module_counts[event.module] = module_counts.get(event.module, 0) + 1
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1

        # Cross-reference analysis
        cross_ref_types = {}
        for event in self.event_history:
            for ref_type in event.cross_references:
                cross_ref_types[ref_type] = cross_ref_types.get(ref_type, 0) + 1

        return {
            "summary": asdict(self.metrics),
            "operation_frequency": operation_counts,
            "module_usage": module_counts,
            "severity_distribution": severity_counts,
            "cross_reference_types": cross_ref_types,
            "vocabulary_health": self.get_vocabulary_health(),
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "operation": event.operation,
                    "module": event.module,
                    "message": event.message,
                    "cross_refs": len(event.cross_references),
                }
                for event in self.event_history[-20:]
            ],
        }

    async def async_log_operation(
        self, operation: str, details: str = "", module: str = "agi_core", severity: str = "INFO"
    ) -> VocabularyEvent:
        """
        Async version of log_agi_operation for high-performance scenarios.

        Useful when vocabulary logging is part of async AGI processing pipelines.
        """
        # Run vocabulary processing in thread pool if needed
        return await asyncio.get_event_loop().run_in_executor(
            None, self.log_agi_operation, operation, details, module, severity
        )


# Global service instance
vocabulary_service = VocabularyIntegrationService()


# Convenience functions for external use
def log_agi_operation(
    operation: str, details: str = "", module: str = "agi_core", severity: str = "INFO"
) -> VocabularyEvent:
    """Convenience function to log AGI operation with vocabulary enrichment."""
    return vocabulary_service.log_agi_operation(operation, details, module, severity)


def create_module_message(operation: str, target_module: str, details: str = "") -> str:
    """Convenience function to create module-specific messages."""
    return vocabulary_service.create_module_message(operation, target_module, details)


def get_vocabulary_health() -> dict[str, Any]:
    """Convenience function to get vocabulary system health."""
    return vocabulary_service.get_vocabulary_health()


if __name__ == "__main__":
    # Test the vocabulary integration service
    service = VocabularyIntegrationService()

    print("🧠 Vocabulary Integration Service Test")
    print("=" * 50)

    # Test basic operation logging
    event1 = service.log_agi_operation("chain_start", "complex reasoning task", "reasoning")
    print(f"Event 1: {event1.message}")

    # Test module-specific message creation
    dream_msg = service.create_module_message("model_consensus", "dream", "multi-model agreement")
    bio_msg = service.create_module_message("guardian_alert", "bio", "safety threshold exceeded")
    print(f"Dream message: {dream_msg}")
    print(f"Bio message: {bio_msg}")

    # Test vocabulary health
    health = service.get_vocabulary_health()
    print(f"Vocabulary health: {health['health_status']}")
    print(f"Total translations: {health['metrics']['total_translations']}")

    # Test analytics export
    analytics = service.export_vocabulary_analytics()
    print(
        f"Most frequent operation: {max(analytics['operation_frequency'], key=analytics['operation_frequency'].get) if analytics['operation_frequency'] else 'None'}"
    )

"""
Integration Points with LUKHAS Systems:
=====================================

1. Dream Module Integration:
   - AGI reasoning operations map to dream processing phases
   - Creative AGI tasks trigger dream-guided enhancement
   - Memory consolidation bridges AGI and dream vocabularies

2. Bio Module Integration:
   - AGI safety alerts connect to bio monitoring systems
   - Physiological feedback influences AGI decision-making
   - Stress detection modulates AGI processing intensity

3. Emotion Module Integration:
   - AGI learning states reflect emotional contexts
   - Affective reasoning influences AGI model selection
   - Emotional feedback guides AGI behavior adaptation

4. Identity Module Integration:
   - AGI operations respect identity-based access controls
   - User preferences influence AGI vocabulary selection
   - Authentication states affect AGI capability availability

5. Guardian Module Integration:
   - AGI safety symbols trigger guardian system responses
   - Ethical violations automatically escalate through vocabularies
   - Constitutional AI principles map to guardian frameworks

Usage in LUKHAS Systems:
======================

# In AGI reasoning module
log_agi_operation("chain_start", "user query analysis", "reasoning", "INFO")

# In dream processing
dream_message = create_module_message("dream_inspire", "dream", "creative solution needed")

# In bio monitoring
bio_alert = create_module_message("guardian_alert", "bio", "stress threshold exceeded")

# System health monitoring
health_status = get_vocabulary_health()
if health_status["health_status"] != "healthy":
    handle_vocabulary_issues(health_status["vocabulary_issues"])
"""
