"""
PWM Intelligence Adapter
========================
Adapter layer for integrating Lukhas Intelligence Engine with PWM systems.

Usage:
    from intelligence.pwm_intelligence_adapter import PWMIntelligenceManager

    # Initialize intelligence for PWM
    intelligence = PWMIntelligenceManager()
    await intelligence.initialize()

    # Use for PWM optimization
    optimized_params = await intelligence.optimize_pwm_parameters(
        current_params={'frequency': 1000, 'duty_cycle': 0.5},
        target_performance={'efficiency': 0.95, 'ripple': 0.02}
    )
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

# Import the main intelligence engine
from .intelligence_engine import (
    LukhasAutonomousGoalEngine,
    LukhasCausalReasoningEngine,
    LukhasCuriosityEngine,
    LukhasDimensionalIntelligenceEngine,
    LukhasMetaCognitiveEngine,
    LukhasSubsystemOrchestrator,
    LukhasTheoryOfMindEngine,
)

logger = logging.getLogger("PWM_Intelligence")


class PWMIntelligenceManager:
    """
    Main manager class for PWM-specific intelligence operations
    """

    def __init__(self):
        self.engines = {}
        self.pwm_optimization_history = []
        self.safety_bounds = {
            "max_frequency": 100000,  # Hz
            "min_frequency": 100,  # Hz
            "max_duty_cycle": 0.95,
            "min_duty_cycle": 0.05,
        }

    async def initialize(self):
        """Initialize all intelligence engines for PWM use"""
        logger.info("🚀 Initializing PWM Intelligence Manager")

        # Initialize core engines
        self.engines = {
            "meta_cognitive": LukhasMetaCognitiveEngine(),
            "causal": LukhasCausalReasoningEngine(),
            "autonomous_goals": LukhasAutonomousGoalEngine(),
            "curiosity": LukhasCuriosityEngine(),
            "theory_of_mind": LukhasTheoryOfMindEngine(),
            "dimensional": LukhasDimensionalIntelligenceEngine(),
            "orchestrator": LukhasSubsystemOrchestrator(),
        }

        # Initialize each engine
        for name, engine in self.engines.items():
            await engine.initialize()
            logger.info(f"✅ Initialized {name} engine")

        logger.info("🧠 PWM Intelligence Manager ready")

    async def optimize_pwm_parameters(
        self, current_params: Dict, target_performance: Dict
    ) -> Dict[str, Any]:
        """
        Use AGI to optimize PWM parameters for target performance

        Args:
            current_params: Current PWM parameters (frequency, duty_cycle, etc.)
            target_performance: Target performance metrics (efficiency, ripple, etc.)

        Returns:
            Optimized parameters and reasoning
        """

        # Meta-cognitive analysis of optimization request
        optimization_request = (
            f"Optimize PWM from {current_params} for {target_performance}"
        )
        meta_analysis = await self.engines["meta_cognitive"].analyze_request(
            optimization_request,
            context={"current_params": current_params, "targets": target_performance},
        )

        # Causal reasoning about parameter relationships
        causal_analysis = await self.engines["causal"].analyze_request_causality(
            optimization_request, current_params
        )

        # Multi-dimensional analysis for holistic optimization
        dimensional_analysis = await self.engines[
            "dimensional"
        ].analyze_multi_dimensional(
            {
                "technical": current_params,
                "performance": target_performance,
                "temporal": {"optimization_urgency": "medium"},
            }
        )

        # Generate optimized parameters
        optimized_params = await self._calculate_optimized_parameters(
            current_params,
            target_performance,
            meta_analysis,
            causal_analysis,
            dimensional_analysis,
        )

        # Safety validation
        safety_check = await self._validate_parameter_safety(optimized_params)

        if not safety_check["safe"]:
            logger.warning(
                f"⚠️ Proposed parameters failed safety check: {safety_check['issues']}"
            )
            optimized_params = await self._apply_safety_constraints(optimized_params)

        # Store optimization history
        self.pwm_optimization_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "original_params": current_params,
                "optimized_params": optimized_params,
                "target_performance": target_performance,
                "meta_analysis": meta_analysis,
                "safety_validated": safety_check["safe"],
            }
        )

        return {
            "optimized_parameters": optimized_params,
            "optimization_confidence": meta_analysis["meta_confidence"],
            "reasoning": dimensional_analysis["optimal_solution"][
                "top_recommendations"
            ],
            "safety_validated": safety_check["safe"],
            "expected_improvements": await self._predict_performance_improvements(
                current_params, optimized_params, target_performance
            ),
        }

    async def analyze_pwm_anomaly(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Analyze PWM system anomalies using curiosity and causal reasoning"""

        # Express curiosity about the anomaly
        curiosity_response = await self.engines["curiosity"].express_curiosity(
            telemetry_data
        )

        if not curiosity_response["curiosity_triggered"]:
            return {"anomaly_detected": False, "status": "normal"}

        # Perform causal analysis of the anomaly
        causal_analysis = await self.engines["causal"].analyze_request_causality(
            f"PWM anomaly: {telemetry_data}", telemetry_data
        )

        # Multi-dimensional analysis
        dimensional_analysis = await self.engines[
            "dimensional"
        ].analyze_multi_dimensional(
            {
                "technical": telemetry_data,
                "temporal": {"anomaly_duration": telemetry_data.get("duration", 0)},
            }
        )

        return {
            "anomaly_detected": True,
            "surprise_level": curiosity_response["surprise_level"],
            "investigation_questions": curiosity_response["questions"],
            "causal_chains": causal_analysis["causal_chains"],
            "recommended_actions": dimensional_analysis["optimal_solution"][
                "top_recommendations"
            ],
            "confidence": causal_analysis["causal_confidence"],
        }

    async def _calculate_optimized_parameters(
        self, current: Dict, targets: Dict, meta: Dict, causal: Dict, dimensional: Dict
    ) -> Dict:
        """Calculate optimized PWM parameters based on intelligence analysis"""

        optimized = current.copy()

        # Simple optimization logic (replace with sophisticated algorithms)
        if "efficiency" in targets:
            target_efficiency = targets["efficiency"]
            current_efficiency = current.get("efficiency", 0.8)

            if target_efficiency > current_efficiency:
                # Increase frequency for better efficiency (simplified)
                frequency_multiplier = min(1.2, target_efficiency / current_efficiency)
                optimized["frequency"] = min(
                    current["frequency"] * frequency_multiplier,
                    self.safety_bounds["max_frequency"],
                )

        if "ripple" in targets:
            target_ripple = targets["ripple"]
            # Adjust duty cycle for ripple reduction (simplified)
            if target_ripple < 0.05:  # Low ripple target
                optimized["duty_cycle"] = min(0.5, optimized.get("duty_cycle", 0.5))

        return optimized

    async def _validate_parameter_safety(self, params: Dict) -> Dict[str, Any]:
        """Validate PWM parameters against safety bounds"""

        issues = []

        if "frequency" in params:
            freq = params["frequency"]
            if freq > self.safety_bounds["max_frequency"]:
                issues.append(
                    f"Frequency {freq} exceeds maximum {self.safety_bounds['max_frequency']}"
                )
            if freq < self.safety_bounds["min_frequency"]:
                issues.append(
                    f"Frequency {freq} below minimum {self.safety_bounds['min_frequency']}"
                )

        if "duty_cycle" in params:
            duty = params["duty_cycle"]
            if duty > self.safety_bounds["max_duty_cycle"]:
                issues.append(
                    f"Duty cycle {duty} exceeds maximum {self.safety_bounds['max_duty_cycle']}"
                )
            if duty < self.safety_bounds["min_duty_cycle"]:
                issues.append(
                    f"Duty cycle {duty} below minimum {self.safety_bounds['min_duty_cycle']}"
                )

        return {"safe": len(issues) == 0, "issues": issues}

    async def _apply_safety_constraints(self, params: Dict) -> Dict:
        """Apply safety constraints to parameters"""

        constrained = params.copy()

        if "frequency" in constrained:
            constrained["frequency"] = max(
                self.safety_bounds["min_frequency"],
                min(constrained["frequency"], self.safety_bounds["max_frequency"]),
            )

        if "duty_cycle" in constrained:
            constrained["duty_cycle"] = max(
                self.safety_bounds["min_duty_cycle"],
                min(constrained["duty_cycle"], self.safety_bounds["max_duty_cycle"]),
            )

        return constrained

    async def _predict_performance_improvements(
        self, current: Dict, optimized: Dict, targets: Dict
    ) -> Dict:
        """Predict performance improvements from optimization"""

        # Simplified prediction logic
        improvements = {}

        if "frequency" in optimized and "frequency" in current:
            freq_improvement = (
                optimized["frequency"] - current["frequency"]
            ) / current["frequency"]
            improvements["frequency_change"] = f"{freq_improvement:.2%}"

        if "efficiency" in targets:
            # Estimate efficiency improvement (simplified)
            estimated_improvement = (
                min(0.1, abs(freq_improvement) * 0.05)
                if "freq_improvement" in locals()
                else 0.02
            )
            improvements["estimated_efficiency_gain"] = f"{estimated_improvement:.2%}"

        return improvements


# Example usage for PWM teams
async def example_pwm_intelligence_usage():
    """Example of how to use PWM intelligence in your code"""

    # Initialize intelligence manager
    intelligence = PWMIntelligenceManager()
    await intelligence.initialize()

    # Optimize PWM parameters
    current_pwm_params = {
        "frequency": 1000,  # Hz
        "duty_cycle": 0.5,  # 50%
        "switching_pattern": "SPWM",
    }

    target_performance = {
        "efficiency": 0.95,  # 95% efficiency target
        "ripple": 0.02,  # 2% ripple target
    }

    optimization_result = await intelligence.optimize_pwm_parameters(
        current_pwm_params, target_performance
    )

    print("🎯 PWM Optimization Results:")
    print(f"Optimized Parameters: {optimization_result['optimized_parameters']}")
    print(f"Confidence: {optimization_result['optimization_confidence']:.2f}")
    print(f"Safety Validated: {optimization_result['safety_validated']}")
    print(f"Expected Improvements: {optimization_result['expected_improvements']}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_pwm_intelligence_usage())
