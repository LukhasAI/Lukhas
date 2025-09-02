"""
DAST Awareness Engine
=====================
Production-grade awareness tracking framework for the Dynamic AI Solutions Tracker (DAST)
Integrates environmental, cognitive, emotional, and social awareness with institutional compliance.

Author: Lukhas AI Research Team
Version: 1.0.0
Date: June 2025
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field

# ——— Configuration & Utilities —————————————————————————————— #


class ComplianceStatus(Enum):
    """Compliance status for DAST institutional alignment."""

    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    CRITICAL = "CRITICAL"


class AwarenessType(Enum):
    """Types of awareness modules in DAST."""

    ENVIRONMENTAL = "environmental"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    SOCIAL = "social"
    FINANCIAL = "financial"
    SUSTAINABILITY = "sustainability"
    MARKET = "market"


class AlignmentMetric(BaseModel):
    """DAST alignment scoring for institutional compliance."""

    score: float = Field(..., ge=0.0, le=100.0, description="Alignment score 0-100")
    status: ComplianceStatus
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    risk_factors: list[str] = Field(default_factory=list)


@dataclass
class DastConfig:
    """DAST Awareness Engine configuration."""

    log_level: str = "INFO"
    compliance_threshold_pass: float = 95.0
    compliance_threshold_warning: float = 80.0
    enable_quantum_processing: bool = False
    enable_real_time_monitoring: bool = True
    sustainability_weight: float = 0.3


def now_iso() -> str:
    """Generate ISO timestamp for DAST logging."""
    return datetime.utcnow().isoformat() + "Z"


def structured_log(event: str, payload: dict, level: str = "INFO"):
    """Structured JSON logging for DAST compliance."""
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": now_iso(),
        "event": event,
        "system": "DAST_Awareness_Engine",
        "payload": payload,
        "level": level,
    }
    logger = logging.getLogger("dast.awareness.logger")
    getattr(logger, level.lower())(json.dumps(record))


# ——— Core DAST Awareness Interfaces ————————————————————————————— #


class AwarenessInput(BaseModel):
    """Base model for any DAST awareness input."""

    timestamp: str = Field(default_factory=now_iso)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context_data: dict[str, Any] = Field(default_factory=dict)


class AwarenessOutput(BaseModel):
    """Base model for DAST awareness output with compliance metrics."""

    alignment: AlignmentMetric
    data: dict[str, Any]
    recommendations: list[str] = Field(default_factory=list)
    sustainability_score: Optional[float] = None
    processing_time_ms: float = 0.0


class DastReasoner(Protocol):
    """Protocol for pluggable DAST reasoners (neural, symbolic, quantum)."""

    def process(self, inputs: AwarenessInput) -> dict[str, Any]:
        """Process awareness inputs and return structured data."""
        ...

    def get_confidence(self) -> float:
        """Return confidence level of the reasoning process."""
        ...


class AwarenessModule(ABC):
    """Abstract base class for all DAST awareness modules."""

    def __init__(self, reasoner: DastReasoner, config: DastConfig = None):
        self.reasoner = reasoner
        self.config = config or DastConfig()
        self.module_type = self._get_module_type()

    def __call__(self, inputs: AwarenessInput) -> AwarenessOutput:
        """Main processing pipeline for awareness modules."""
        start_time = datetime.utcnow()

        try:
            # Core processing
            result = self.reasoner.process(inputs)

            # Compute alignment score
            align_score = self.evaluate_alignment(result, inputs)

            # Generate recommendations
            recommendations = self.generate_recommendations(result, inputs)

            # Calculate sustainability impact
            sustainability_score = self.calculate_sustainability_impact(result)

            # Create output
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            output = AwarenessOutput(
                alignment=AlignmentMetric(
                    score=align_score,
                    status=self._compliance_status(align_score),
                    confidence=self.reasoner.get_confidence(),
                    risk_factors=self._identify_risk_factors(result),
                ),
                data=result,
                recommendations=recommendations,
                sustainability_score=sustainability_score,
                processing_time_ms=processing_time,
            )

            # Structured logging
            structured_log(
                f"{self.__class__.__name__}_process",
                {
                    "module_type": self.module_type.value,
                    "inputs": inputs.dict(),
                    "output_summary": {
                        "alignment_score": align_score,
                        "compliance_status": output.alignment.status.value,
                        "processing_time_ms": processing_time,
                        "recommendations_count": len(recommendations),
                    },
                },
            )

            return output

        except Exception as e:
            # Error handling and logging
            structured_log(
                f"{self.__class__.__name__}_error",
                {"error": str(e), "inputs": inputs.dict()},
                "ERROR",
            )
            raise

    @abstractmethod
    def evaluate_alignment(self, result: dict[str, Any], inputs: AwarenessInput) -> float:
        """Evaluate DAST institutional alignment (0-100 scale)."""
        ...

    @abstractmethod
    def _get_module_type(self) -> AwarenessType:
        """Return the type of awareness module."""
        ...

    def generate_recommendations(self, result: dict[str, Any], inputs: AwarenessInput) -> list[str]:
        """Generate actionable recommendations based on awareness data."""
        return []

    def calculate_sustainability_impact(self, result: dict[str, Any]) -> float:
        """Calculate sustainability impact score (0-100)."""
        return 50.0  # Default neutral score

    def _compliance_status(self, score: float) -> ComplianceStatus:
        """Map alignment score to compliance status."""
        if score >= self.config.compliance_threshold_pass:
            return ComplianceStatus.PASS
        elif score >= self.config.compliance_threshold_warning:
            return ComplianceStatus.WARNING
        elif score >= 50:
            return ComplianceStatus.FAIL
        else:
            return ComplianceStatus.CRITICAL

    def _identify_risk_factors(self, result: dict[str, Any]) -> list[str]:
        """Identify potential risk factors from processing results."""
        risk_factors = []

        # Common risk factor detection
        if result.get("anomaly_detected", False):
            risk_factors.append("anomaly_detected")

        if result.get("confidence", 1.0) < 0.7:
            risk_factors.append("low_confidence")

        if result.get("data_quality", 1.0) < 0.8:
            risk_factors.append("poor_data_quality")

        return risk_factors


# ——— DAST Environmental Awareness Module ——————————————————————— #


class EnvironmentalAwarenessInput(AwarenessInput):
    """Environmental awareness inputs for DAST sustainability tracking."""

    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    ambient_noise: float = Field(..., ge=0, description="Noise level in dB")
    light_level: float = Field(..., ge=0, description="Light level in lux")
    air_quality_index: Optional[float] = Field(None, ge=0, le=500)
    location: tuple[float, float] = Field(..., description="Latitude, Longitude")
    energy_consumption: Optional[float] = Field(None, description="kWh consumption")


class EnvironmentalReasoner:
    """Environmental data processing with sustainability focus."""

    def process(self, inputs: EnvironmentalAwarenessInput) -> dict[str, Any]:
        """Process environmental data with DAST sustainability metrics."""

        # Normalize environmental factors

        def normalize(value, min_val, max_val, optimal_min=None, optimal_max=None):
            """Normalize with optional optimal range."""
            norm = max(0.0, min((value - min_val) / (max_val - min_val), 1.0))

            if optimal_min is not None and optimal_max is not None:
                if optimal_min <= value <= optimal_max:
                    return 1.0
                elif value < optimal_min:
                    return norm * 0.8  # Penalty for sub-optimal
                else:
                    return norm * 0.8  # Penalty for super-optimal
            return norm

        # Calculate environmental scores
        temp_score = normalize(inputs.temperature, -20, 50, 18, 24)
        humidity_score = normalize(inputs.humidity, 0, 100, 40, 60)
        noise_score = normalize(120 - inputs.ambient_noise, 0, 120, 80, 120)  # Lower noise is better
        light_score = normalize(inputs.light_level, 0, 2000, 300, 800)

        # Air quality impact
        air_quality_score = 1.0
        if inputs.air_quality_index:
            air_quality_score = normalize(500 - inputs.air_quality_index, 0, 500)

        # Location-based adjustments
        location_bonus = 0.05 if self._is_sustainable_location(inputs.location) else 0.0

        # Energy efficiency assessment
        energy_efficiency = 1.0
        if inputs.energy_consumption:
            energy_efficiency = max(0.1, 1.0 - (inputs.energy_consumption / 100))  # Penalize high consumption

        # Detect environmental anomalies
        anomaly_detected = self._detect_anomalies(inputs)

        # Calculate composite score
        base_score = (
            temp_score * 0.25 + humidity_score * 0.2 + noise_score * 0.2 + light_score * 0.15 + air_quality_score * 0.2
        ) + location_bonus

        # Apply energy efficiency multiplier
        final_score = base_score * energy_efficiency

        return {
            "environmental_score": final_score,
            "component_scores": {
                "temperature": temp_score,
                "humidity": humidity_score,
                "noise": noise_score,
                "light": light_score,
                "air_quality": air_quality_score,
                "energy_efficiency": energy_efficiency,
            },
            "anomaly_detected": anomaly_detected,
            "sustainability_rating": self._calculate_sustainability_rating(final_score, inputs),
            "carbon_impact": self._estimate_carbon_impact(inputs),
            "optimization_opportunities": self._identify_optimizations(inputs),
        }

    def get_confidence(self) -> float:
        """Return confidence level."""
        return 0.92

    def _is_sustainable_location(self, location: tuple[float, float]) -> bool:
        """Check if location is in a sustainable/green area."""
        # Placeholder for GIS lookup with sustainability databases
        # Could integrate with green building databases, renewable energy zones, etc.
        lat, lon = location
        return False  # Implement actual sustainability location lookup

    def _detect_anomalies(self, inputs: EnvironmentalAwarenessInput) -> bool:
        """Detect environmental anomalies."""
        anomalies = []

        if inputs.temperature < -10 or inputs.temperature > 45:
            anomalies.append("extreme_temperature")

        if inputs.ambient_noise > 85:  # WHO safe limit
            anomalies.append("excessive_noise")

        if inputs.air_quality_index and inputs.air_quality_index > 150:
            anomalies.append("poor_air_quality")

        return len(anomalies) > 0

    def _calculate_sustainability_rating(self, score: float, inputs: EnvironmentalAwarenessInput) -> str:
        """Calculate sustainability rating."""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Good"
        elif score >= 0.6:
            return "Fair"
        else:
            return "Poor"

    def _estimate_carbon_impact(self, inputs: EnvironmentalAwarenessInput) -> dict[str, float]:
        """Estimate carbon footprint impact."""
        base_impact = 0.0

        if inputs.energy_consumption:
            # Rough estimate: 0.5 kg CO2 per kWh (grid average)
            base_impact += inputs.energy_consumption * 0.5

        return {
            "estimated_co2_kg": base_impact,
            "category": ("low" if base_impact < 10 else "medium" if base_impact < 50 else "high"),
        }

    def _identify_optimizations(self, inputs: EnvironmentalAwarenessInput) -> list[str]:
        """Identify optimization opportunities."""
        optimizations = []

        if inputs.energy_consumption and inputs.energy_consumption > 20:
            optimizations.append("Consider energy-efficient alternatives")

        if inputs.ambient_noise > 70:
            optimizations.append("Noise reduction measures recommended")

        if inputs.air_quality_index and inputs.air_quality_index > 100:
            optimizations.append("Air purification system recommended")

        return optimizations


class EnvironmentalAwarenessModule(AwarenessModule):
    """DAST Environmental Awareness Module with sustainability focus."""

    def _get_module_type(self) -> AwarenessType:
        return AwarenessType.ENVIRONMENTAL

    def evaluate_alignment(self, result: dict[str, Any], inputs: AwarenessInput) -> float:
        """Evaluate environmental alignment with DAST sustainability goals."""
        base_score = result["environmental_score"] * 100

        # Sustainability bonus/penalty
        sustainability_rating = result.get("sustainability_rating", "Fair")
        if sustainability_rating == "Excellent":
            base_score += 5
        elif sustainability_rating == "Poor":
            base_score -= 10

        # Anomaly penalty
        if result.get("anomaly_detected", False):
            base_score -= 15

        # Carbon impact consideration
        carbon_impact = result.get("carbon_impact", {})
        if carbon_impact.get("category") == "high":
            base_score -= 20
        elif carbon_impact.get("category") == "low":
            base_score += 5

        return max(0.0, min(base_score, 100.0))

    def generate_recommendations(self, result: dict[str, Any], inputs: AwarenessInput) -> list[str]:
        """Generate environmental recommendations."""
        recommendations = []

        # Use optimization opportunities from reasoner
        recommendations.extend(result.get("optimization_opportunities", []))

        # Add DAST-specific recommendations
        if result.get("sustainability_rating") == "Poor":
            recommendations.append("Consider relocating to a more sustainable environment")

        if result.get("anomaly_detected"):
            recommendations.append("Environmental anomaly detected - immediate attention required")

        # Energy-specific recommendations
        energy_efficiency = result.get("component_scores", {}).get("energy_efficiency", 1.0)
        if energy_efficiency < 0.7:
            recommendations.append("Switch to renewable energy sources")
            recommendations.append("Implement energy-saving measures")

        return recommendations

    def calculate_sustainability_impact(self, result: dict[str, Any]) -> float:
        """Calculate sustainability impact score."""
        base_score = result["environmental_score"] * 100

        # Factor in carbon impact
        carbon_impact = result.get("carbon_impact", {})
        if carbon_impact.get("category") == "low":
            base_score += 10
        elif carbon_impact.get("category") == "high":
            base_score -= 20

        return max(0.0, min(base_score, 100.0))


# ——— DAST Cognitive Awareness Module ——————————————————————————— #


class CognitiveAwarenessInput(AwarenessInput):
    """Cognitive awareness inputs for DAST decision-making optimization."""

    attention_level: float = Field(..., ge=0, le=1, description="Attention level 0-1")
    cognitive_load: float = Field(..., ge=0, le=1, description="Cognitive load 0-1")
    decision_complexity: int = Field(..., ge=1, le=10, description="Decision complexity 1-10")
    information_overload: bool = Field(default=False)
    stress_indicators: list[str] = Field(default_factory=list)
    task_urgency: int = Field(..., ge=1, le=5, description="Task urgency 1-5")


class CognitiveReasoner:
    """Cognitive processing reasoner for DAST decision optimization."""

    def process(self, inputs: CognitiveAwarenessInput) -> dict[str, Any]:
        """Process cognitive state for optimal decision-making."""

        # Calculate cognitive efficiency
        efficiency = (inputs.attention_level * (1 - inputs.cognitive_load)) * 0.8

        # Adjust for decision complexity
        complexity_factor = max(0.1, 1.0 - (inputs.decision_complexity - 1) / 9)
        efficiency *= complexity_factor

        # Information overload penalty
        if inputs.information_overload:
            efficiency *= 0.7

        # Stress impact
        stress_penalty = len(inputs.stress_indicators) * 0.1
        efficiency -= stress_penalty

        # Urgency vs quality trade-off
        if inputs.task_urgency >= 4:
            efficiency *= 0.9  # Slight penalty for high urgency

        efficiency = max(0.0, min(efficiency, 1.0))

        # Decision quality prediction
        decision_quality = efficiency * 0.9 + (inputs.attention_level * 0.1)

        return {
            "cognitive_efficiency": efficiency,
            "decision_quality_prediction": decision_quality,
            "optimal_decision_timing": self._calculate_optimal_timing(inputs),
            "cognitive_state": self._assess_cognitive_state(inputs),
            "decision_support_needed": decision_quality < 0.7,
            "recommended_break": efficiency < 0.4,
            "information_filtering_needed": inputs.information_overload,
        }

    def get_confidence(self) -> float:
        return 0.88

    def _calculate_optimal_timing(self, inputs: CognitiveAwarenessInput) -> str:
        """Calculate optimal timing for decision-making."""
        if inputs.cognitive_load > 0.8:
            return "defer_decision"
        elif inputs.attention_level > 0.8 and inputs.cognitive_load < 0.4:
            return "optimal_now"
        else:
            return "moderate_timing"

    def _assess_cognitive_state(self, inputs: CognitiveAwarenessInput) -> str:
        """Assess current cognitive state."""
        if inputs.attention_level > 0.8 and inputs.cognitive_load < 0.3:
            return "peak_performance"
        elif inputs.cognitive_load > 0.8 or len(inputs.stress_indicators) > 2:
            return "cognitive_overload"
        else:
            return "normal_function"


class CognitiveAwarenessModule(AwarenessModule):
    """DAST Cognitive Awareness Module for decision optimization."""

    def _get_module_type(self) -> AwarenessType:
        return AwarenessType.COGNITIVE

    def evaluate_alignment(self, result: dict[str, Any], inputs: AwarenessInput) -> float:
        """Evaluate cognitive alignment with DAST decision-making goals."""
        base_score = result["decision_quality_prediction"] * 100

        # Bonus for optimal cognitive state
        cognitive_state = result.get("cognitive_state", "normal_function")
        if cognitive_state == "peak_performance":
            base_score += 10
        elif cognitive_state == "cognitive_overload":
            base_score -= 20

        # Decision support bonus
        if result.get("decision_support_needed") and not inputs.context_data.get("support_available", False):
            base_score -= 15

        return max(0.0, min(base_score, 100.0))

    def generate_recommendations(self, result: dict[str, Any], inputs: AwarenessInput) -> list[str]:
        """Generate cognitive optimization recommendations."""
        recommendations = []

        if result.get("recommended_break"):
            recommendations.append("Take a cognitive break to restore mental clarity")

        if result.get("information_filtering_needed"):
            recommendations.append("Apply information filtering to reduce cognitive load")

        if result.get("decision_support_needed"):
            recommendations.append("Seek decision support tools or expert consultation")

        timing = result.get("optimal_decision_timing", "moderate_timing")
        if timing == "defer_decision":
            recommendations.append("Defer decision until cognitive state improves")
        elif timing == "optimal_now":
            recommendations.append("Current state optimal for decision-making")

        return recommendations


# ——— DAST Awareness Engine Orchestrator ———————————————————————— #


class DastAwarenessEngine:
    """Main orchestrator for DAST Awareness Engine."""

    def __init__(self, config: DastConfig = None):
        self.config = config or DastConfig()
        self.modules: dict[AwarenessType, AwarenessModule] = {}
        self._setup_logging()
        self._initialize_modules()

    def _setup_logging(self):
        """Setup structured logging for DAST."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _initialize_modules(self):
        """Initialize awareness modules."""
        # Environmental Module
        env_reasoner = EnvironmentalReasoner()
        self.modules[AwarenessType.ENVIRONMENTAL] = EnvironmentalAwarenessModule(env_reasoner, self.config)

        # Cognitive Module
        cog_reasoner = CognitiveReasoner()
        self.modules[AwarenessType.COGNITIVE] = CognitiveAwarenessModule(cog_reasoner, self.config)

    def process_awareness(self, awareness_type: AwarenessType, inputs: AwarenessInput) -> AwarenessOutput:
        """Process awareness data through appropriate module."""
        if awareness_type not in self.modules:
            raise ValueError(f"Awareness type {awareness_type} not supported")

        return self.modules[awareness_type](inputs)

    async def process_multi_awareness(
        self, awareness_data: dict[AwarenessType, AwarenessInput]
    ) -> dict[AwarenessType, AwarenessOutput]:
        """Process multiple awareness types concurrently."""
        tasks = []
        for awareness_type, inputs in awareness_data.items():
            if awareness_type in self.modules:
                task = asyncio.create_task(asyncio.to_thread(self.process_awareness, awareness_type, inputs))
                tasks.append((awareness_type, task))

        results = {}
        for awareness_type, task in tasks:
            results[awareness_type] = await task

        return results

    def get_system_status(self) -> dict[str, Any]:
        """Get overall DAST awareness system status."""
        return {
            "engine_status": "active",
            "modules_loaded": list(self.modules.keys()),
            "config": self.config.__dict__,
            "timestamp": now_iso(),
        }


# ——— Example Usage & Testing ————————————————————————————————— #


if __name__ == "__main__":
    # Initialize DAST Awareness Engine
    config = DastConfig(
        log_level="INFO",
        enable_real_time_monitoring=True,
        sustainability_weight=0.4,
    )

    engine = DastAwarenessEngine(config)

    # Test Environmental Awareness
    print("=== DAST Environmental Awareness Test ===")
    env_input = EnvironmentalAwarenessInput(
        temperature=22.5,
        humidity=45,
        ambient_noise=35,
        light_level=400,
        air_quality_index=75,
        location=(37.7749, -122.4194),  # San Francisco
        energy_consumption=15.5,
        user_id="user_123",
        session_id="session_456",
    )

    env_output = engine.process_awareness(AwarenessType.ENVIRONMENTAL, env_input)
    print(f"Environmental Alignment Score: {env_output.alignment.score:.2f}")
    print(f"Compliance Status: {env_output.alignment.status.value}")
    print(f"Sustainability Score: {env_output.sustainability_score:.2f}")
    print(f"Recommendations: {env_output.recommendations}")

    # Test Cognitive Awareness
    print("\n=== DAST Cognitive Awareness Test ===")
    cog_input = CognitiveAwarenessInput(
        attention_level=0.8,
        cognitive_load=0.6,
        decision_complexity=7,
        information_overload=True,
        stress_indicators=["time_pressure", "multitasking"],
        task_urgency=4,
        user_id="user_123",
        session_id="session_456",
    )

    cog_output = engine.process_awareness(AwarenessType.COGNITIVE, cog_input)
    print(f"Cognitive Alignment Score: {cog_output.alignment.score:.2f}")
    print(f"Compliance Status: {cog_output.alignment.status.value}")
    print(f"Recommendations: {cog_output.recommendations}")

    # System Status
    print("\n=== DAST System Status ===")
    status = engine.get_system_status()
    print(json.dumps(status, indent=2))
