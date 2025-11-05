"""
🧠 Abstract Reasoning Brain Interface
Interface for the Bio-Quantum Symbolic Reasoning system with Radar Analytics Integration
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Union

from .core import AbstractReasoningBrainCore

# Import radar integration
try:
    from .bio_quantum_radar_integration import BioQuantumRadarIntegration

    RADAR_INTEGRATION_AVAILABLE = True
except ImportError:
    RADAR_INTEGRATION_AVAILABLE = False
    logging.warning("Radar integration not available", timezone)

logger = logging.getLogger("AbstractReasoningInterface")


class AbstractReasoningBrainInterface:
    """
    Interface for the Abstract Reasoning Brain

    Provides high-level methods for interacting with the Bio-Quantum
    Symbolic Reasoning Engine and Multi-Brain Symphony orchestration,
    with integrated radar analytics for performance monitoring.
    """

    def __init__(
        self,
        core: AbstractReasoningBrainCore | None = None,
        enable_radar_analytics: bool = True,
    ):
        self.core = core or AbstractReasoningBrainCore()
        self.interface_active = False

        # Radar analytics integration
        self.enable_radar_analytics = enable_radar_analytics and RADAR_INTEGRATION_AVAILABLE
        self.radar_integration = None
        if self.enable_radar_analytics:
            self.radar_integration = BioQuantumRadarIntegration(self)

    async def initialize(self) -> bool:
        """Initialize the abstract reasoning interface"""
        try:
            await self.core.activate_brain()
            self.interface_active = True

            if self.radar_integration:
                logger.info("🚀 Abstract Reasoning Interface initialized with Radar Analytics")
            else:
                logger.info("🚀 Abstract Reasoning Interface initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize interface: {e}")
            return False

    async def reason_abstractly(
        self,
        problem: Union[str, dict[str, Any]],
        context: dict[str, Any] | None = None,
        reasoning_type: str = "general_abstract",
        enable_radar_analytics: bool | None = None,
    ) -> dict[str, Any]:
        """
        Perform abstract reasoning on a problem with optional radar analytics

        Args:
            problem: The problem to reason about (string or structured data)
            context: Additional context for reasoning
            reasoning_type: Type of reasoning to perform
            enable_radar_analytics: Override radar analytics for this call

        Returns:
            Comprehensive reasoning result with confidence metrics and optional radar analytics
        """
        if not self.interface_active:
            await self.initialize()

        # Determine if radar analytics should be used for this call
        use_radar = enable_radar_analytics if enable_radar_analytics is not None else self.enable_radar_analytics

        # If radar analytics is enabled, use the integrated processing
        if use_radar and self.radar_integration:
            logger.info(f"🧠📊 Starting abstract reasoning with radar analytics: {reasoning_type}")

            problem_description = (
                problem if isinstance(problem, str) else problem.get("description", "Complex reasoning problem")
            )
            return await self.radar_integration.process_with_radar_analytics(
                problem_description, context, generate_visualization=True
            )

        # Standard reasoning without radar analytics
        logger.info(f"🧠 Starting abstract reasoning: {reasoning_type}")

        # Structure the input for the core processor
        if isinstance(problem, str):
            problem_space = {
                "description": problem,
                "type": reasoning_type,
                "complexity": "auto_detect",
            }
        else:
            problem_space = problem.copy()
            problem_space.update(
                {
                    "type": reasoning_type,
                    "complexity": problem_space.get("complexity", "auto_detect"),
                }
            )

        input_data = {
            "problem_space": problem_space,
            "context": context or {},
            "reasoning_type": reasoning_type,
            "interface_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = await self.core.process_independently(input_data)

            # Extract key components for easier access
            simplified_result = {
                "solution": result.get("reasoning_result", {}).get("solution", {}),
                "confidence": result.get("confidence_metrics", {}).get("meta_confidence", 0.0),
                "reasoning_path": result.get("reasoning_result", {}).get("reasoning_path", {}),
                "coherence": result.get("processing_metadata", {}).get("brain_symphony_coherence", 0.0),
                "uncertainty": result.get("confidence_metrics", {}).get("uncertainty_decomposition", {}),
                "full_result": result,
            }

            logger.info(f"✅ Abstract reasoning completed - Confidence: {simplified_result['confidence']:.3f}")

            return simplified_result

        except Exception as e:
            logger.error(f"❌ Abstract reasoning failed: {e}")
            return {
                "error": str(e),
                "solution": None,
                "confidence": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def orchestrate_brains(
        self,
        request: dict[str, Any],
        target_brains: list[str] | None = None,
    ) -> dict[str, Any]:
        """
            Orchestrate reasoning across specific brain systems

            Args:
                request: The reasoning request
                target_brains: List of brain types to include ["dreams", "emotional",
        "memory", "learning"]

            Returns:
                Results from orchestrated brain processing
        """
        if not self.interface_active:
            await self.initialize()

        logger.info(f"🎼 Orchestrating brains: {target_brains or 'all'}")

        try:
            result = await self.core.orchestrate_cross_brain_reasoning(request, target_brains)
            return result

        except Exception as e:
            logger.error(f"❌ Brain orchestration failed: {e}")
            return {
                "error": str(e),
                "orchestration_failed": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def analyze_confidence(self, reasoning_result: dict[str, Any]) -> dict[str, Any]:
        """
        Perform detailed confidence analysis on a reasoning result

        Args:
            reasoning_result: Result from abstract reasoning

        Returns:
            Detailed confidence analysis
        """
        try:
            confidence_metrics = reasoning_result.get("confidence_metrics", {})

            analysis = {
                "overall_confidence": confidence_metrics.get("meta_confidence", 0.0),
                "confidence_breakdown": {
                    "bayesian": confidence_metrics.get("bayesian_confidence", 0.0),
                    "quantum": confidence_metrics.get("qi_confidence", 0.0),
                    "symbolic": confidence_metrics.get("symbolic_confidence", 0.0),
                    "emotional": confidence_metrics.get("emotional_confidence", 0.0),
                },
                "uncertainty_analysis": confidence_metrics.get("uncertainty_decomposition", {}),
                "coherence_score": confidence_metrics.get("cross_brain_coherence", 0.0),
                "calibration_quality": confidence_metrics.get("calibration_score", 0.0),
                "confidence_interpretation": self._interpret_confidence(confidence_metrics),
            }

            return analysis

        except Exception as e:
            logger.error(f"❌ Confidence analysis failed: {e}")
            return {"error": str(e)}

    def _interpret_confidence(self, confidence_metrics: dict[str, Any]) -> dict[str, str]:
        """Interpret confidence metrics for human understanding"""
        meta_confidence = confidence_metrics.get("meta_confidence", 0.0)
        coherence = confidence_metrics.get("cross_brain_coherence", 0.0)

        interpretations = {}

        # Overall confidence interpretation
        if meta_confidence >= 0.9:
            interpretations["overall"] = "Very High - Strong agreement across all reasoning methods"
        elif meta_confidence >= 0.8:
            interpretations["overall"] = "High - Good agreement with minor uncertainties"
        elif meta_confidence >= 0.7:
            interpretations["overall"] = "Moderate - Reasonable confidence with some disagreement"
        elif meta_confidence >= 0.6:
            interpretations["overall"] = "Low-Moderate - Significant uncertainties present"
        else:
            interpretations["overall"] = "Low - High uncertainty, proceed with caution"

        # Coherence interpretation
        if coherence >= 0.8:
            interpretations["coherence"] = "Excellent - All brain systems in harmony"
        elif coherence >= 0.7:
            interpretations["coherence"] = "Good - Strong coordination between brain systems"
        elif coherence >= 0.6:
            interpretations["coherence"] = "Fair - Some discord between brain systems"
        else:
            interpretations["coherence"] = "Poor - Brain systems not well coordinated"

        # Uncertainty interpretation
        uncertainty = confidence_metrics.get("uncertainty_decomposition", {})
        dominant_uncertainty = max(uncertainty.items(), key=lambda x: x[1]) if uncertainty else ("unknown", 0)

        if dominant_uncertainty[1] > 0.3:
            interpretations["primary_uncertainty"] = f"Dominated by {dominant_uncertainty[0]} uncertainty"
        else:
            interpretations["primary_uncertainty"] = "Well-balanced uncertainty distribution"

        return interpretations

    async def provide_feedback(
        self,
        reasoning_result: dict[str, Any],
        actual_outcome: bool,
        feedback_notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Provide feedback on reasoning outcome for meta-learning

        Args:
            reasoning_result: The original reasoning result
            actual_outcome: Whether the reasoning was correct (True/False)
            feedback_notes: Optional notes about the feedback

        Returns:
            Feedback processing result
        """
        if not self.interface_active:
            await self.initialize()

        feedback_context = {
            "feedback_notes": feedback_notes,
            "feedback_timestamp": datetime.now(timezone.utc).isoformat(),
            "outcome_type": "binary_correctness",
        }

        try:
            await self.core.update_from_feedback(
                reasoning_result.get("full_result", reasoning_result),
                actual_outcome,
                feedback_context,
            )

            logger.info(f"📊 Feedback processed: outcome={actual_outcome}")

            return {
                "feedback_processed": True,
                "outcome": actual_outcome,
                "notes": feedback_notes,
                "timestamp": feedback_context["feedback_timestamp"],
            }

        except Exception as e:
            logger.error(f"❌ Feedback processing failed: {e}")
            return {"feedback_processed": False, "error": str(e)}

    async def get_reasoning_history(
        self, limit: int | None = 10, include_full_results: bool = False
    ) -> list[dict[str, Any]]:
        """
        Get history of reasoning sessions

        Args:
            limit: Maximum number of sessions to return
            include_full_results: Whether to include full detailed results

        Returns:
            List of reasoning session summaries
        """
        if not self.interface_active:
            await self.initialize()

        try:
            full_history = await self.core.get_reasoning_history(limit)

            if include_full_results:
                return full_history

            # Return simplified summaries
            summaries = []
            for session in full_history:
                summary = {
                    "timestamp": session.get("processing_metadata", {}).get("processing_timestamp"),
                    "reasoning_type": session.get("processing_metadata", {}).get("reasoning_type"),
                    "confidence": session.get("confidence_metrics", {}).get("meta_confidence", 0.0),
                    "coherence": session.get("processing_metadata", {}).get("brain_symphony_coherence", 0.0),
                    "success": session.get("confidence_metrics", {}).get("meta_confidence", 0.0) > 0.7,
                }
                summaries.append(summary)

            return summaries

        except Exception as e:
            logger.error(f"❌ Failed to get reasoning history: {e}")
            return []

    async def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary of the abstract reasoning brain"""
        if not self.interface_active:
            await self.initialize()

        try:
            status = self.core.get_brain_status()

            performance_summary = {
                "brain_status": {
                    "active": status["active"],
                    "specialization": status["specialization"],
                    "components_initialized": all(
                        [
                            status["brain_symphony_initialized"],
                            status["bio_quantum_reasoner_initialized"],
                            status["confidence_calibrator_initialized"],
                        ]
                    ),
                },
                "performance_metrics": status["performance_metrics"],
                "session_statistics": {
                    "total_sessions": status["reasoning_sessions_count"],
                    "calibration_quality": status.get("calibration_summary", {}).get("calibration_score", 0.0),
                },
                "capabilities": {
                    "bio_quantum_reasoning": True,
                    "multi_brain_orchestration": True,
                    "advanced_confidence_calibration": True,
                    "meta_learning": True,
                    "cross_brain_coherence": True,
                },
            }

            return performance_summary

        except Exception as e:
            logger.error(f"❌ Failed to get performance summary: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown the abstract reasoning interface"""
        try:
            await self.core.shutdown_brain()
            self.interface_active = False
            logger.info("🛑 Abstract Reasoning Interface shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown failed: {e}")

    # =============================================================================
    # 📊 RADAR ANALYTICS INTEGRATION METHODS
    # =============================================================================

    async def start_radar_monitoring(
        self,
        update_interval: float = 2.0,
        max_duration: float | None = None,
    ) -> bool:
        """
        Start real-time radar monitoring of Bio-Quantum reasoning performance.

        Args:
            update_interval: Seconds between radar updates
            max_duration: Optional maximum monitoring duration

        Returns:
            True if monitoring started successfully
        """
        if not self.radar_integration:
            logger.warning("Radar analytics not available for monitoring")
            return False

        logger.info(f"🔄 Starting radar monitoring (interval: {update_interval}s)")
        try:
            await self.radar_integration.start_real_time_monitoring(update_interval, max_duration)
            return True
        except Exception as e:
            logger.error(f"Failed to start radar monitoring: {e}")
            return False

    def stop_radar_monitoring(self) -> bool:
        """Stop real-time radar monitoring."""
        if not self.radar_integration:
            return False

        self.radar_integration.stop_real_time_monitoring()
        logger.info("🛑 Radar monitoring stopped")
        return True

    def export_radar_analytics(self, filepath: str | None = None) -> str | None:
        """
        Export comprehensive radar analytics session data.

        Args:
            filepath: Optional custom export path

        Returns:
            Path to exported file or None if failed
        """
        if not self.radar_integration:
            logger.warning("Radar analytics not available for export")
            return None

        try:
            export_path = self.radar_integration.export_session_analytics(filepath)
            logger.info(f"📁 Radar analytics exported to: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Failed to export radar analytics: {e}")
            return None

    def get_radar_performance_summary(self) -> dict[str, Any]:
        """
        Get current radar analytics performance summary.

        Returns:
            Performance summary dict or empty dict if unavailable
        """
        if not self.radar_integration:
            return {"status": "Radar analytics not available"}

        return self.radar_integration._get_performance_summary()

    async def reason_with_radar_visualization(
        self,
        problem: Union[str, dict[str, Any]],
        context: dict[str, Any] | None = None,
        reasoning_type: str = "general_abstract",
    ) -> dict[str, Any]:
        """
        Convenience method for reasoning with guaranteed radar visualization.

        Args:
            problem: Problem to reason about
            context: Additional context
            reasoning_type: Type of reasoning

        Returns:
            Reasoning result with radar analytics and visualization path
        """
        return await self.reason_abstractly(problem, context, reasoning_type, enable_radar_analytics=True)

    def configure_radar_analytics(self, config: dict[str, Any]) -> bool:
        """
        Update radar analytics configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if configuration updated successfully
        """
        if not self.radar_integration:
            logger.warning("Radar analytics not available for configuration")
            return False

        try:
            self.radar_integration.visualizer.config.update(config)
            logger.info("📊 Radar analytics configuration updated")
            return True
        except Exception as e:
            logger.error(f"Failed to update radar config: {e}")
            return False


# Convenience functions for quick access


async def reason_about(
    problem: Union[str, dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Quick function to perform abstract reasoning

    Args:
        problem: Problem to reason about
        context: Optional context

    Returns:
        Reasoning result
    """
    interface = AbstractReasoningBrainInterface()
    await interface.initialize()

    try:
        result = await interface.reason_abstractly(problem, context)
        return result
    finally:
        await interface.shutdown()


async def analyze_reasoning_confidence(
    reasoning_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Quick function to analyze confidence in a reasoning result

    Args:
        reasoning_result: Result from abstract reasoning

    Returns:
        Confidence analysis
    """
    interface = AbstractReasoningBrainInterface()
    await interface.initialize()

    try:
        analysis = await interface.analyze_confidence(reasoning_result)
        return analysis
    finally:
        await interface.shutdown()


# =============================================================================
# 📊 RADAR-ENHANCED CONVENIENCE FUNCTIONS
# =============================================================================


async def reason_about_with_radar(
    problem_description: str,
    context: dict[str, Any] | None = None,
    reasoning_type: str = "general_abstract",
) -> dict[str, Any]:
    """
    Convenience function for abstract reasoning with radar analytics.

    Args:
        problem_description: Description of the problem to solve
        context: Additional context for reasoning
        reasoning_type: Type of reasoning to perform

    Returns:
        Comprehensive result with reasoning and radar analytics
    """
    interface = AbstractReasoningBrainInterface(enable_radar_analytics=True)
    await interface.initialize()

    try:
        result = await interface.reason_with_radar_visualization(problem_description, context, reasoning_type)
        return result
    finally:
        await interface.shutdown()


async def start_radar_monitoring_session(update_interval: float = 2.0, duration: float = 30.0) -> str:
    """
    Start a radar monitoring session and return analytics export path.

    Args:
        update_interval: Seconds between updates
        duration: Total monitoring duration

    Returns:
        Path to exported analytics file
    """
    interface = AbstractReasoningBrainInterface(enable_radar_analytics=True)
    await interface.initialize()

    try:
        # Start monitoring
        await interface.start_radar_monitoring(update_interval, duration)

        # Export analytics
        export_path = interface.export_radar_analytics()
        return export_path or "Export failed"
    finally:
        interface.stop_radar_monitoring()
        await interface.shutdown()


# Legacy function compatibility


async def reason_about(
    problem_description: str,
    context: dict[str, Any] | None = None,
    reasoning_type: str = "general_abstract",
) -> dict[str, Any]:
    """
    Simple reasoning function - now with optional radar analytics.

    Args:
        problem_description: Description of the problem to solve
        context: Additional context for reasoning
        reasoning_type: Type of reasoning to perform

    Returns:
        Reasoning result
    """
    interface = AbstractReasoningBrainInterface()
    await interface.initialize()

    try:
        result = await interface.reason_abstractly(problem_description, context, reasoning_type)
        # Return just the reasoning result for backward compatibility
        if isinstance(result, dict) and "reasoning_result" in result:
            return result["reasoning_result"]
        return result
    finally:
        await interface.shutdown()


# =============================================================================
# 📊 DEMONSTRATION AND TESTING FUNCTIONS
# =============================================================================


async def demo_radar_integration():
    """Comprehensive demonstration of radar analytics integration."""
    print("🧠⚛️📊 Bio-Quantum Radar Analytics Integration Demo")
    print("=" * 60)

    # Test 1: Single reasoning with radar
    print("\n1️⃣ Testing single reasoning with radar analytics...")
    result = await reason_about_with_radar(
        "Design a quantum-biological hybrid consciousness detection system",
        context={
            "domain": "consciousness_research",
            "complexity": "very_high",
        },
    )
    print(f"   ✅ Confidence: {result['reasoning_result']['confidence']:.3f}")
    print(f"   📊 Visualization: {result['visualization_path']}")

    # Test 2: Real-time monitoring
    print("\n2️⃣ Testing real-time monitoring (10 seconds)...")
    export_path = await start_radar_monitoring_session(update_interval=1.0, duration=10.0)
    print(f"   📁 Analytics exported to: {export_path}")

    # Test 3: Multiple reasoning calls with analytics
    print("\n3️⃣ Testing multiple reasoning calls with analytics...")
    interface = AbstractReasoningBrainInterface(enable_radar_analytics=True)
    await interface.initialize()

    try:
        problems = [
            "Optimize entanglement-like correlation for bio-neural interfaces",
            "Design self-improving AI safety protocols",
            "Create consciousness-aware computing architectures",
        ]

        for i, problem in enumerate(problems, 1):
            result = await interface.reason_with_radar_visualization(problem)
            print(
                f"   {i}. Confidence: {result['reasoning_result']['confidence']:.3f}, "
                f"Coherence: {result['reasoning_result']['coherence']:.3f}"
            )

        # Export comprehensive session
        final_export = interface.export_radar_analytics()
        print(f"   📊 Final session analytics: {final_export}")

    finally:
        await interface.shutdown()

    print("\n🎉 Radar integration demo completed successfully!")


if __name__ == "__main__":
    # Run the radar integration demo
    import asyncio

    asyncio.run(demo_radar_integration())
