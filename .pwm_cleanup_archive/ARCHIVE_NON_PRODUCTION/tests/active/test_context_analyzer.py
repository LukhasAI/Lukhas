# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: test_context_analyzer.py
# MODULE: core.advanced.brain.tests.test_context_analyzer
# DESCRIPTION: Pytest unit tests for the ContextAnalyzer, focusing on intent
#              detection, sentiment analysis, and contextual information extraction.
# DEPENDENCIES: pytest, logging, typing
#               (Assumed: ..context_analyzer.ContextAnalyzer relative to this test file)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
Unit tests for the ContextAnalyzer.
These tests cover basic intent analysis, sentiment detection, and extraction
of location, device, and historical context.
"""

import logging
from typing import Any, Dict, List  # Added for type hinting

import pytest

# Initialize logger for ΛTRACE
logger = logging.getLogger("ΛTRACE.core.advanced.brain.tests.test_context_analyzer")
logger.info("ΛTRACE: Initializing test_context_analyzer module.")

# TODO: Verify the correct import path for ContextAnalyzer.
#       The original was 'from core.context_analyzer import ContextAnalyzer'.
#       Assuming it should be relative to the 'core.advanced.brain' package,
#       e.g., 'core.advanced.brain.context_analyzer.py'.
CONTEXT_ANALYZER_AVAILABLE = False
ContextAnalyzer = None  # Placeholder
try:
    from ..context_analyzer import (
        ContextAnalyzer,  # Points to core/advanced/brain/context_analyzer.py
    )

    CONTEXT_ANALYZER_AVAILABLE = True
    logger.info(
        "ΛTRACE: ContextAnalyzer imported successfully from ..context_analyzer."
    )
except ImportError:
    logger.error(
        "ΛTRACE: Failed to import ContextAnalyzer from ..context_analyzer. Tests will be skipped."
    )

    # Define a dummy class if import fails, so pytest can at least parse the file
    class ContextAnalyzer:
        def analyze(
            self,
            user_input: str,
            metadata: Dict[str, Any],
            memory: List[Dict[str, Any]],
        ) -> Dict[str, Any]:
            logger.warning("ΛTRACE: Using DUMMY ContextAnalyzer due to import failure.")
            return {
                "intent": "dummy_intent",
                "sentiment": "dummy_sentiment",
                "error": "ContextAnalyzer not loaded",
            }


# Human-readable comment: Fixture to provide a ContextAnalyzer instance for tests.
@pytest.fixture
def context_analyzer_instance() -> ContextAnalyzer:  # Renamed fixture for clarity
    """Pytest fixture to provide an instance of ContextAnalyzer."""
    logger.debug("ΛTRACE: Creating ContextAnalyzer instance for test via fixture.")
    return ContextAnalyzer()


# Human-readable comment: Test for basic intent analysis.
@pytest.mark.skipif(
    not CONTEXT_ANALYZER_AVAILABLE, reason="ContextAnalyzer not available"
)
def test_analyze_basic_intent(context_analyzer_instance: ContextAnalyzer):
    """Tests basic intent detection from user input."""
    logger.info("ΛTRACE: Running test_analyze_basic_intent.")
    user_input = "I need help with my order."
    metadata: Dict[str, Any] = {}
    memory: List[Dict[str, Any]] = []

    logger.debug(
        f"ΛTRACE: Input: '{user_input}', Metadata: {metadata}, Memory: {memory}"
    )
    context = context_analyzer_instance.analyze(user_input, metadata, memory)
    logger.debug(f"ΛTRACE: Analysis result: {context}")

    assert context.get("intent") == "help_order", "Intent should be 'help_order'"
    assert context.get("sentiment") is not None, "Sentiment should be analyzed"
    logger.info("ΛTRACE: test_analyze_basic_intent finished.")


# Human-readable comment: Test for sentiment analysis.
@pytest.mark.skipif(
    not CONTEXT_ANALYZER_AVAILABLE, reason="ContextAnalyzer not available"
)
def test_analyze_sentiment(context_analyzer_instance: ContextAnalyzer):
    """Tests sentiment analysis from user input."""
    logger.info("ΛTRACE: Running test_analyze_sentiment.")
    user_input = "I'm really happy with the service!"
    metadata: Dict[str, Any] = {}
    memory: List[Dict[str, Any]] = []

    logger.debug(f"ΛTRACE: Input: '{user_input}'")
    context = context_analyzer_instance.analyze(user_input, metadata, memory)
    logger.debug(f"ΛTRACE: Analysis result: {context}")

    assert context.get("sentiment") == "happiness", "Sentiment should be 'happiness'"
    logger.info("ΛTRACE: test_analyze_sentiment finished.")


# Human-readable comment: Test for location context extraction from metadata.
@pytest.mark.skipif(
    not CONTEXT_ANALYZER_AVAILABLE, reason="ContextAnalyzer not available"
)
def test_analyze_location(context_analyzer_instance: ContextAnalyzer):
    """Tests extraction and use of location context from metadata."""
    logger.info("ΛTRACE: Running test_analyze_location.")
    user_input = "Where is the nearest store?"
    metadata = {"location": {"city": "New York"}}
    memory: List[Dict[str, Any]] = []

    logger.debug(f"ΛTRACE: Input: '{user_input}', Metadata: {metadata}")
    context = context_analyzer_instance.analyze(user_input, metadata, memory)
    logger.debug(f"ΛTRACE: Analysis result: {context}")

    assert (
        context.get("location_context", {}).get("city") == "New York"
    ), "Location context should include city 'New York'"
    logger.info("ΛTRACE: test_analyze_location finished.")


# Human-readable comment: Test for device context extraction from metadata.
@pytest.mark.skipif(
    not CONTEXT_ANALYZER_AVAILABLE, reason="ContextAnalyzer not available"
)
def test_analyze_device(context_analyzer_instance: ContextAnalyzer):
    """Tests extraction and use of device context from metadata."""
    logger.info("ΛTRACE: Running test_analyze_device.")
    user_input = "My battery is low."
    metadata = {"device_info": {"battery_level": 15}}
    memory: List[Dict[str, Any]] = []

    logger.debug(f"ΛTRACE: Input: '{user_input}', Metadata: {metadata}")
    context = context_analyzer_instance.analyze(user_input, metadata, memory)
    logger.debug(f"ΛTRACE: Analysis result: {context}")

    assert (
        context.get("device_context", {}).get("battery_level") == 15
    ), "Device context should include battery_level 15"
    logger.info("ΛTRACE: test_analyze_device finished.")


# Human-readable comment: Test for historical context extraction from memory.
@pytest.mark.skipif(
    not CONTEXT_ANALYZER_AVAILABLE, reason="ContextAnalyzer not available"
)
def test_analyze_historical_context(context_analyzer_instance: ContextAnalyzer):
    """Tests extraction and use of historical context from memory."""
    logger.info("ΛTRACE: Running test_analyze_historical_context.")
    user_input = "What did I ask last time?"
    metadata: Dict[str, Any] = {}
    memory = [
        {"input": "I need help with my order.", "context": {"intent": "help_order"}}
    ]

    logger.debug(f"ΛTRACE: Input: '{user_input}', Memory: {memory}")
    context = context_analyzer_instance.analyze(user_input, metadata, memory)
    logger.debug(f"ΛTRACE: Analysis result: {context}")

    historical_ctx = context.get("historical_context", {})
    assert (
        historical_ctx.get("familiarity", 0.0) > 0.1
    ), "Familiarity score should be greater than 0.1"
    assert (
        len(historical_ctx.get("related_interactions", [])) > 0
    ), "Should find related historical interactions"
    logger.info("ΛTRACE: test_analyze_historical_context finished.")


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: test_context_analyzer.py
# VERSION: 1.0.0
# TIER SYSTEM: Not applicable (Test Script)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Unit tests for ContextAnalyzer, verifying intent detection,
#               sentiment analysis, and extraction of location, device, and
#               historical context.
# FUNCTIONS: context_analyzer_instance (fixture), test_analyze_basic_intent,
#            test_analyze_sentiment, test_analyze_location, test_analyze_device,
#            test_analyze_historical_context.
# CLASSES: None (tests ContextAnalyzer class).
# DECORATORS: @pytest.fixture, @pytest.mark.skipif.
# DEPENDENCIES: pytest, logging, typing,
#               assumed ..context_analyzer.ContextAnalyzer.
# INTERFACES: Pytest test discovery and execution.
# ERROR HANDLING: Uses pytest assertions to check for expected outcomes.
# LOGGING: ΛTRACE_ENABLED for logging test execution and debug information.
# AUTHENTICATION: Not applicable.
# HOW TO USE:
#   Run with pytest: pytest core/advanced/brain/tests/test_context_analyzer.py
# INTEGRATION NOTES: Assumes ContextAnalyzer can be imported correctly. The import path
#                    might need adjustment based on the actual location of context_analyzer.py.
# MAINTENANCE: Update tests if ContextAnalyzer API or behavior changes.
#              Add more tests for different contexts, edge cases, and languages.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
