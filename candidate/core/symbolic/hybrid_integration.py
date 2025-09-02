"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Enhanced Core TypeScript - Integrated from Advanced Systems
Original: hybrid_integration.py
Advanced: hybrid_integration.py
Integration Date: 2025-05-31T07:55:28.226819
"""

import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class NeuroSymbolicIntegrator:
    """
    Core integration engine that bridges neural networks with symbolic reasoning.
    This hybrid approach enables efficient pattern recognition and logical inference
    while maintaining transparency and ethical alignment.

    Inspired by minimalist design principles and ethical AI considerations.
    """

    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.symbolic_weight = self.config.get("symbolic_weight", 0.6)
        self.neural_weight = self.config.get("neural_weight", 0.4)
        self.integration_method = self.config.get("integration_method", "weighted")
        self.processing_history = []
        self.last_processed = None

    def _default_config(self):
        """Default configuration with emphasis on symbolic processing"""
        return {
            "symbolic_weight": 0.6,  # Higher weight for symbolic to prioritize explainability
            "neural_weight": 0.4,
            "integration_method": "weighted",  # Other options: 'maximal', 'adaptive'
            "confidence_threshold": 0.7,
        }

    async def process_input(
        self,
        input_data: dict[str, Any],
        symbolic_engine=None,
        neural_engine=None,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Process input using both neural and symbolic engines

        Args:
            input_data: Input data to process
            symbolic_engine: Symbolic reasoning engine
            neural_engine: Neural processing engine
            context: Additional context for processing

        Returns:
            Dict containing processed response and metadata
        """
        logger.info("Processing input with neuro-symbolic integration")

        # Process through symbolic reasoning engine
        symbolic_results = await self._process_symbolic(
            input_data, symbolic_engine, context
        )

        # Process through neural engine
        neural_results = await self._process_neural(input_data, neural_engine, context)

        # Integrate results
        integrated_results = self._integrate_results(
            symbolic_results, neural_results, context
        )

        # Update processing history
        self._update_history(
            input_data, symbolic_results, neural_results, integrated_results
        )

        return integrated_results

    async def _process_symbolic(
        self,
        input_data: dict[str, Any],
        symbolic_engine,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Process input through symbolic reasoning engine"""
        if symbolic_engine is None:
            # If no engine provided, return empty results
            return {
                "type": "symbolic",
                "results": None,
                "confidence": 0.0,
                "error": "No symbolic engine provided",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            # Process data through symbolic engine
            symbolic_results = await symbolic_engine.reason(input_data)
            return {
                "type": "symbolic",
                "results": symbolic_results,
                "confidence": symbolic_results.get("confidence", 0.5),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error in symbolic processing: {e!s}")
            return {
                "type": "symbolic",
                "results": None,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _process_neural(
        self,
        input_data: dict[str, Any],
        neural_engine,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Process input through neural engine"""
        if neural_engine is None:
            # If no engine provided, return empty results
            return {
                "type": "neural",
                "results": None,
                "confidence": 0.0,
                "error": "No neural engine provided",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            # Process data through neural engine
            neural_results = await neural_engine.process(input_data, context)
            return {
                "type": "neural",
                "results": neural_results,
                "confidence": neural_results.get("confidence", 0.5),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error in neural processing: {e!s}")
            return {
                "type": "neural",
                "results": None,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _integrate_results(
        self,
        symbolic_results: dict[str, Any],
        neural_results: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Integrate results from symbolic and neural processing

        Different integration methods provide varying balance between symbolic reasoning
        and neural pattern recognition.
        """
        integration_method = context.get("integration_method", self.integration_method)

        # Check for errors in processing
        if symbolic_results.get("error") and neural_results.get("error"):
            return {
                "status": "error",
                "message": "Both symbolic and neural processing failed",
                "symbolic_error": symbolic_results.get("error"),
                "neural_error": neural_results.get("error"),
                "timestamp": datetime.now().isoformat(),
            }

        # Extract confidences
        symbolic_results.get("confidence", 0.0)
        neural_results.get("confidence", 0.0)

        # Different integration methods
        if integration_method == "weighted":
            # Weighted combination based on configured weights
            return self._weighted_integration(symbolic_results, neural_results, context)
        elif integration_method == "maximal":
            # Select result with highest confidence
            return self._maximal_integration(symbolic_results, neural_results, context)
        elif integration_method == "adaptive":
            # Adapt weights based on input characteristics
            return self._adaptive_integration(symbolic_results, neural_results, context)
        else:
            # Default to weighted
            return self._weighted_integration(symbolic_results, neural_results, context)

    def _weighted_integration(
        self,
        symbolic_results: dict[str, Any],
        neural_results: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Integrate results using weighted combination"""
        symbolic_confidence = symbolic_results.get("confidence", 0.0)
        neural_confidence = neural_results.get("confidence", 0.0)

        # Adjust weights if one engine failed
        if symbolic_results.get("error"):
            effective_symbolic_weight = 0.0
            effective_neural_weight = 1.0
        elif neural_results.get("error"):
            effective_symbolic_weight = 1.0
            effective_neural_weight = 0.0
        else:
            effective_symbolic_weight = self.symbolic_weight
            effective_neural_weight = self.neural_weight

        # Calculate weighted confidence
        if effective_symbolic_weight + effective_neural_weight > 0:
            integrated_confidence = (
                (symbolic_confidence * effective_symbolic_weight)
                + (neural_confidence * effective_neural_weight)
            ) / (effective_symbolic_weight + effective_neural_weight)
        else:
            integrated_confidence = 0.0

        # Determine primary response source based on weighted contribution
        symbolic_contribution = symbolic_confidence * effective_symbolic_weight
        neural_contribution = neural_confidence * effective_neural_weight

        if symbolic_contribution > neural_contribution:
            primary_source = "symbolic"
            primary_results = symbolic_results.get("results")
            secondary_results = neural_results.get("results")
        else:
            primary_source = "neural"
            primary_results = neural_results.get("results")
            secondary_results = symbolic_results.get("results")

        # Construct integrated response
        return {
            "status": "success",
            "integrated_confidence": integrated_confidence,
            "primary_source": primary_source,
            "symbolic_confidence": symbolic_confidence,
            "neural_confidence": neural_confidence,
            "symbolic_weight": effective_symbolic_weight,
            "neural_weight": effective_neural_weight,
            "primary_results": primary_results,
            "secondary_results": secondary_results,
            "symbolic_results": symbolic_results,
            "neural_results": neural_results,
            "reasoning_trace": self._extract_reasoning_trace(
                symbolic_results, neural_results, primary_source
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def _maximal_integration(
        self,
        symbolic_results: dict[str, Any],
        neural_results: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Integrate results by selecting the one with highest confidence"""
        symbolic_confidence = symbolic_results.get("confidence", 0.0)
        neural_confidence = neural_results.get("confidence", 0.0)

        # Check for errors
        if symbolic_results.get("error"):
            symbolic_confidence = 0.0
        if neural_results.get("error"):
            neural_confidence = 0.0

        # Select source with highest confidence
        if symbolic_confidence >= neural_confidence:
            primary_source = "symbolic"
            primary_results = symbolic_results.get("results")
            integrated_confidence = symbolic_confidence
            secondary_results = neural_results.get("results")
        else:
            primary_source = "neural"
            primary_results = neural_results.get("results")
            integrated_confidence = neural_confidence
            secondary_results = symbolic_results.get("results")

        # Construct integrated response
        return {
            "status": "success",
            "integrated_confidence": integrated_confidence,
            "primary_source": primary_source,
            "symbolic_confidence": symbolic_confidence,
            "neural_confidence": neural_confidence,
            "primary_results": primary_results,
            "secondary_results": secondary_results,
            "symbolic_results": symbolic_results,
            "neural_results": neural_results,
            "reasoning_trace": self._extract_reasoning_trace(
                symbolic_results, neural_results, primary_source
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def _adaptive_integration(
        self,
        symbolic_results: dict[str, Any],
        neural_results: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Adaptively integrate results based on input characteristics

        This method dynamically adjusts weights based on the nature of the input
        and the confidence levels of each processor.
        """
        symbolic_confidence = symbolic_results.get("confidence", 0.0)
        neural_confidence = neural_results.get("confidence", 0.0)

        # Check for errors
        if symbolic_results.get("error"):
            symbolic_confidence = 0.0
        if neural_results.get("error"):
            neural_confidence = 0.0

        # Adaptive weighting based on confidence gap
        confidence_gap = abs(symbolic_confidence - neural_confidence)

        # If one engine is significantly more confident, favor it more strongly
        if confidence_gap > 0.3:  # Significant gap
            if symbolic_confidence > neural_confidence:
                adaptive_symbolic_weight = 0.8
                adaptive_neural_weight = 0.2
            else:
                adaptive_symbolic_weight = 0.2
                adaptive_neural_weight = 0.8
        else:
            # Smaller gap, use more balanced weights but still favor symbolic for
            # explainability
            adaptive_symbolic_weight = self.symbolic_weight
            adaptive_neural_weight = self.neural_weight

        # Calculate weighted confidence
        if adaptive_symbolic_weight + adaptive_neural_weight > 0:
            integrated_confidence = (
                (symbolic_confidence * adaptive_symbolic_weight)
                + (neural_confidence * adaptive_neural_weight)
            ) / (adaptive_symbolic_weight + adaptive_neural_weight)
        else:
            integrated_confidence = 0.0

        # Determine primary response source
        symbolic_contribution = symbolic_confidence * adaptive_symbolic_weight
        neural_contribution = neural_confidence * adaptive_neural_weight

        if symbolic_contribution > neural_contribution:
            primary_source = "symbolic"
            primary_results = symbolic_results.get("results")
            secondary_results = neural_results.get("results")
        else:
            primary_source = "neural"
            primary_results = neural_results.get("results")
            secondary_results = symbolic_results.get("results")

        # Construct integrated response
        return {
            "status": "success",
            "integrated_confidence": integrated_confidence,
            "primary_source": primary_source,
            "symbolic_confidence": symbolic_confidence,
            "neural_confidence": neural_confidence,
            "symbolic_weight": adaptive_symbolic_weight,
            "neural_weight": adaptive_neural_weight,
            "primary_results": primary_results,
            "secondary_results": secondary_results,
            "symbolic_results": symbolic_results,
            "neural_results": neural_results,
            "confidence_gap": confidence_gap,
            "reasoning_trace": self._extract_reasoning_trace(
                symbolic_results, neural_results, primary_source
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def _extract_reasoning_trace(
        self,
        symbolic_results: dict[str, Any],
        neural_results: dict[str, Any],
        primary_source: str,
    ) -> list[dict[str, Any]]:
        """Extract reasoning trace from results for transparency"""
        reasoning_trace = []

        # Add symbolic reasoning steps if available
        if (
            symbolic_results
            and "results" in symbolic_results
            and symbolic_results["results"]
            and "reasoning_path" in symbolic_results["results"]
        ):
            symbolic_path = symbolic_results["results"]["reasoning_path"]
            if symbolic_path:
                for step in symbolic_path:
                    reasoning_trace.append(
                        {
                            "source": "symbolic",
                            "step": step.get("step", len(reasoning_trace) + 1),
                            "type": step.get("type", "unknown"),
                            "content": step.get("content", ""),
                            "confidence": step.get("confidence", 0.0),
                        }
                    )

        # Add primary conclusion from symbolic reasoning if available
        if (
            symbolic_results
            and "results" in symbolic_results
            and symbolic_results["results"]
            and "primary_conclusion" in symbolic_results["results"]
            and symbolic_results["results"]["primary_conclusion"]
        ):
            primary_conclusion = symbolic_results["results"]["primary_conclusion"]
            reasoning_trace.append(
                {
                    "source": "symbolic",
                    "step": len(reasoning_trace) + 1,
                    "type": "conclusion",
                    "content": primary_conclusion.get("summary", ""),
                    "confidence": primary_conclusion.get("confidence", 0.0),
                }
            )

        # Add neural reasoning insights if available
        if neural_results and "results" in neural_results and neural_results["results"]:
            neural_results_data = neural_results["results"]

            # If neural results contain reasoning steps
            if (
                isinstance(neural_results_data, dict)
                and "reasoning_steps" in neural_results_data
            ):
                for step in neural_results_data["reasoning_steps"]:
                    reasoning_trace.append(
                        {
                            "source": "neural",
                            "step": len(reasoning_trace) + 1,
                            "type": step.get("type", "neural_step"),
                            "content": step.get("content", ""),
                            "confidence": step.get(
                                "confidence",
                                neural_results.get("confidence", 0.0),
                            ),
                        }
                    )

            # Include relevant insights from neural processing
            if (
                isinstance(neural_results_data, dict)
                and "insights" in neural_results_data
            ):
                insights = neural_results_data["insights"]
                if isinstance(insights, list):
                    for insight in insights:
                        reasoning_trace.append(
                            {
                                "source": "neural",
                                "step": len(reasoning_trace) + 1,
                                "type": "insight",
                                "content": (
                                    insight
                                    if isinstance(insight, str)
                                    else str(insight)
                                ),
                                "confidence": neural_results.get("confidence", 0.0),
                            }
                        )

        # Add integration step
        reasoning_trace.append(
            {
                "source": "integration",
                "step": len(reasoning_trace) + 1,
                "type": "integration",
                "content": f"Integrated results with primary source: {primary_source}",
                "confidence": None,
            }
        )

        return reasoning_trace

    def _update_history(
        self,
        input_data: dict[str, Any],
        symbolic_results: dict[str, Any],
        neural_results: dict[str, Any],
        integrated_results: dict[str, Any],
    ) -> None:
        """Update processing history"""
        # Create minimal history entry to reduce memory usage
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "input_type": input_data.get("type", "unknown"),
            "symbolic_confidence": symbolic_results.get("confidence", 0.0),
            "neural_confidence": neural_results.get("confidence", 0.0),
            "integrated_confidence": integrated_results.get(
                "integrated_confidence", 0.0
            ),
            "primary_source": integrated_results.get("primary_source", "unknown"),
        }

        # Add to history
        self.processing_history.append(history_entry)
        self.last_processed = datetime.now().isoformat()

        # Limit history size
        if len(self.processing_history) > 50:  # Reduced for efficiency
            self.processing_history = self.processing_history[-50:]
