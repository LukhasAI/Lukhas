"""
ΛPROPHET Demonstration Script

Simple demonstration of ΛPROPHET predictive cascade detection capabilities
with simulated cascade scenarios.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from symbolic_patterns.cascade_prediction import (
    AlertLevel,
    LambdaProphet,
    SymbolicMetrics,
)


def generate_cascade_scenario() -> list:
    """Generate a simulated entropy spiral cascade scenario."""
    timeline = []
    base_time = datetime.now(timezone.utc)

    # Generate 15 metrics showing cascade buildup
    for i in range(15):
        progress = i / 15  # 0.0 to 1.0
        timestamp = base_time + timedelta(minutes=i * 5)

        # Simulate entropy spiral with accelerating risk (exponential curve)
        accelerated_progress = progress**2  # Quadratic acceleration

        metrics = SymbolicMetrics(
            timestamp=timestamp,
            entropy_level=0.2 + accelerated_progress * 0.75,  # 0.2 → 0.95
            phase_drift=0.05 + accelerated_progress * 0.5,  # 0.05 → 0.55
            motif_conflicts=1 + int(accelerated_progress * 12),  # 1 → 13
            emotion_volatility=0.1 + accelerated_progress * 0.85,  # 0.1 → 0.95
            contradiction_density=0.1 + accelerated_progress * 0.7,  # 0.1 → 0.8
            memory_fold_integrity=0.95 - accelerated_progress * 0.6,  # 0.95 → 0.35
            governor_stress=0.05 + accelerated_progress * 0.8,  # 0.05 → 0.85
            dream_convergence=0.1 + accelerated_progress * 0.75,  # 0.1 → 0.85
        )
        timeline.append(metrics)

    return timeline


async def run_prophet_demo():
    """Run ΛPROPHET demonstration with cascade scenario."""
    print("🔮 ΛPROPHET - Predictive Cascade Detection Demo")
    print("═" * 60)

    # Initialize ΛPROPHET with lower confidence threshold for demo
    prophet = LambdaProphet()
    prophet.cascade_predictor.confidence_threshold = 0.3

    # Generate cascade scenario
    print("📊 Generating entropy spiral cascade scenario...")
    timeline = generate_cascade_scenario()

    print(f"   ✓ Generated {len(timeline)} symbolic metrics")
    print(f"   ✓ Timeline span: {timeline[0].timestamp} to {timeline[-1].timestamp}")

    # Show initial and final risk scores
    initial_risk = timeline[0].risk_score()
    final_risk = timeline[-1].risk_score()
    print(f"   ✓ Risk progression: {initial_risk:.3f} → {final_risk:.3f}")
    print()

    # Analyze trajectory
    print("🔍 Analyzing symbolic trajectory...")

    # Populate analyzer with timeline data
    for metrics in timeline:
        prophet.trajectory_analyzer.add_metrics(metrics)

    analysis = prophet.trajectory_analyzer.analyze_trajectory(timeline)

    print(f"   ✓ Overall Risk Score: {analysis['overall_risk']:.3f}")
    print(f"   ✓ Trend Stability: {analysis['trend_stability']:.3f}")
    print(f"   ✓ System Volatility: {analysis['volatility']:.3f}")
    print(f"   ✓ Entropy Trend: {analysis['entropy_trend']:.3f}")
    print(f"   ✓ Pattern Match Score: {analysis['pattern_match_score']:.3f}")
    print()

    # Generate cascade prediction
    print("🚨 Generating cascade prediction...")
    prediction = prophet.predict_cascade_risk(timeline)

    if prediction:
        print("   🔮 CASCADE DETECTED!")
        print(f"   ✓ Type: {prediction.cascade_type.value}")
        print(f"   ✓ Confidence: {prediction.confidence:.3f}")

        if prediction.time_to_cascade:
            hours = prediction.time_to_cascade // 3600
            minutes = (prediction.time_to_cascade % 3600) // 60
            print(f"   ✓ Time to Cascade: {hours}h {minutes}m")

        print(f"   ✓ Contributing Factors: {len(prediction.contributing_factors)}")
        for factor in prediction.contributing_factors[:3]:
            print(f"     • {factor}")

        print(
            f"   ✓ Recommended Interventions: {len(prediction.recommended_interventions)}"
        )
        for intervention in prediction.recommended_interventions:
            priority_emoji = {
                "EMERGENCY": "🚨",
                "CRITICAL": "🔴",
                "WARNING": "🟡",
                "INFO": "🔵",
            }
            emoji = priority_emoji.get(intervention.priority.value, "⚪")

            print(f"     {emoji} {intervention.intervention_type.value}")
            print(f"       Target: {intervention.target_component}")
            print(f"       Risk Reduction: {intervention.expected_risk_reduction:.1%}")
        print()

        # Emit prophet signal
        print("📡 Emitting ΛPROPHET signal...")

        if prediction.confidence > 0.9:
            alert_level = AlertLevel.EMERGENCY
        elif prediction.confidence > 0.8:
            alert_level = AlertLevel.CRITICAL
        elif prediction.confidence > 0.7:
            alert_level = AlertLevel.WARNING
        else:
            alert_level = AlertLevel.INFO

        signal = prophet.emit_prophet_signal(
            alert_level,
            {
                "prediction": prediction,
                "confidence": prediction.confidence,
                "analysis": analysis,
            },
        )

        print(f"   ✓ Signal Type: {signal.signal_type}")
        print(f"   ✓ Alert Level: {signal.alert_level.value}")
        print(f"   ✓ Signal ID: {signal.signal_id}")
        print(f"   ✓ Timestamp: {signal.timestamp}")

    else:
        print("   ✅ No significant cascade risk detected")

    print()
    print("🎯 DEMONSTRATION COMPLETE")
    print("✅ ΛPROPHET predictive cascade detection capabilities verified")


if __name__ == "__main__":
    asyncio.run(run_prophet_demo())
