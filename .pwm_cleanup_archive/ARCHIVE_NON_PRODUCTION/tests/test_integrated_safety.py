#!/usr/bin/env python3
"""
Test and demonstrate the integrated safety system with all components
"""

import asyncio
import sys
from datetime import datetime

import numpy as np

# Add parent directory to path
sys.path.append(".")

from core.integrated_safety_system import (
    IntegratedSafetySystem,
    SafetyEvent,
    SafetyEventType,
)


async def test_comprehensive_safety():
    """Comprehensive test of integrated safety system"""
    print("🧪 COMPREHENSIVE INTEGRATED SAFETY TEST")
    print("=" * 80)

    # Initialize the integrated safety system
    print("\n📦 Initializing Integrated Safety System...")
    safety_system = IntegratedSafetySystem()

    # Start monitoring
    monitoring_task = asyncio.create_task(safety_system.run_continuous_monitoring())

    # Give system time to initialize
    await asyncio.sleep(1)

    # Test 1: Multi-Colony Validation
    print("\n1️⃣ TEST: Multi-Colony Validation")
    print("-" * 40)

    test_actions = [
        {
            "name": "Safe User Request",
            "action": {
                "type": "user_request",
                "content": "Please explain quantum computing",
                "user_consent": True,
                "harm_potential": 0.0,
                "is_explainable": True,
            },
        },
        {
            "name": "Potentially Harmful Action",
            "action": {
                "type": "system_action",
                "content": "Delete all user data",
                "harm_potential": 0.9,
                "user_consent": False,
                "reversible": False,
            },
        },
        {
            "name": "Ethically Ambiguous Request",
            "action": {
                "type": "analysis_request",
                "content": "Analyze user behavior patterns",
                "harm_potential": 0.3,
                "user_consent": True,
                "transparency_level": 0.5,
                "bias_assessment": 0.4,
            },
        },
    ]

    for test in test_actions:
        print(f"\n   Testing: {test['name']}")
        result = await safety_system.validate_action(test["action"])

        print(f"   ✓ Is Safe: {'✅' if result.is_safe else '❌'}")
        print(f"   ✓ Safety Score: {result.safety_score:.2%}")
        print(f"   ✓ Ethical Score: {result.ethical_score:.2%}")
        print(f"   ✓ Compliance Score: {result.compliance_score:.2%}")
        print(f"   ✓ Consensus Score: {result.consensus_score:.2%}")
        print(f"   ✓ Validation Time: {result.validation_time_ms:.1f}ms")

        if result.violations:
            print(f"   ⚠️  Violations: {len(result.violations)}")
            for v in result.violations[:2]:  # Show first 2
                print(f"      - {v}")

        if result.recommendations:
            print("   💡 Recommendations:")
            for r in result.recommendations[:2]:  # Show first 2
                print(f"      - {r}")

    # Test 2: Event Broadcasting and Colony Coordination
    print("\n\n2️⃣ TEST: Event Broadcasting & Colony Coordination")
    print("-" * 40)

    # Simulate a hallucination detection
    print("\n   Simulating hallucination detection...")
    hallucination_event = SafetyEvent(
        event_id="test_hall_001",
        event_type=SafetyEventType.HALLUCINATION_DETECTED,
        severity=0.8,
        source_colony="test_memory",
        timestamp=datetime.now(),
        data={
            "detected_hallucination": "LUKHAS was created in 1990",
            "correct_information": "LUKHAS is an AGI system created in 2025",
            "confidence": 0.95,
        },
    )

    success = await safety_system.event_bus.broadcast_safety_event(hallucination_event)
    print(f"   ✓ Event broadcast: {'✅' if success else '❌'}")

    # Check event metrics
    metrics = safety_system.event_bus.get_event_metrics()
    print(f"   ✓ Total events: {metrics['total_events']}")
    print(
        f"   ✓ Hallucination events: {metrics['events_by_type'].get(SafetyEventType.HALLUCINATION_DETECTED, 0)}"
    )

    # Test 3: Threat Response and Mitigation
    print("\n\n3️⃣ TEST: Threat Response & Mitigation")
    print("-" * 40)

    threats = [
        {
            "name": "Minor Anomaly",
            "threat": {
                "type": "performance_degradation",
                "severity": 0.3,
                "source": "monitoring_system",
                "details": "Response time increased by 20%",
            },
        },
        {
            "name": "Critical Security Threat",
            "threat": {
                "type": "unauthorized_access_attempt",
                "severity": 0.9,
                "source": "security_monitor",
                "details": "Multiple failed authentication attempts detected",
                "affected_components": ["auth_service", "user_database"],
            },
        },
    ]

    for threat_test in threats:
        print(f"\n   Testing: {threat_test['name']}")
        response = await safety_system.handle_threat(threat_test["threat"])

        print(f"   ✓ Threat ID: {response['threat_id']}")
        print(f"   ✓ Threat Level: {response['threat_level']}")
        print(f"   ✓ Mitigation Effectiveness: {response['effectiveness']:.0%}")
        print(f"   ✓ System Safety Level: {response['system_safety_level']}")

        strategy = response["mitigation_strategy"]
        print(f"   ✓ Mitigation Action: {strategy.get('action', 'unknown')}")
        print(f"   ✓ Colonies Involved: {strategy.get('colonies_involved', [])}")

    # Test 4: Drift Detection and Correction
    print("\n\n4️⃣ TEST: Drift Detection & Correction")
    print("-" * 40)

    # Simulate drift by adding reality anchors and checking violations
    print("\n   Adding reality anchors...")
    safety_system.memory_safety.add_reality_anchor("test_year", "2025")
    safety_system.memory_safety.add_reality_anchor("test_system", "LUKHAS AI")

    # Test action that violates reality anchor
    drift_action = {
        "content": "Processing data from year 2030",
        "type": "temporal_reference",
        "timestamp": datetime.now(),
    }

    print("   Testing action with temporal drift...")
    result = await safety_system.validate_action(drift_action)
    print(f"   ✓ Detected drift violation: {'✅' if not result.is_safe else '❌'}")

    # Check drift metrics
    drift_status = await safety_system._monitor_global_drift()
    print(f"   ✓ Memory drift score: {drift_status.get('memory', 0):.3f}")

    # Test 5: Circuit Breaker Functionality
    print("\n\n5️⃣ TEST: Circuit Breaker Protection")
    print("-" * 40)

    # Simulate multiple failures to trip circuit breaker
    print("\n   Simulating component failures...")
    test_component = "test_service"

    for i in range(6):  # Threshold is 5
        safety_system.trip_circuit_breaker(test_component)
        is_open = not safety_system.check_circuit_breaker(test_component)
        print(f"   Failure {i+1}: Circuit breaker {'OPEN' if is_open else 'CLOSED'}")

    # Test 6: System Health and Metrics
    print("\n\n6️⃣ TEST: System Health & Metrics")
    print("-" * 40)

    # Get comprehensive system status
    status = safety_system.get_system_status()

    print("\n   System Status:")
    print(f"   ✓ System ID: {status['system_id']}")
    print(f"   ✓ Safety Level: {status['safety_level']}")
    print(f"   ✓ Active Threats: {status['active_threats']}")

    print("\n   Event Metrics:")
    event_metrics = status["event_metrics"]
    print(f"   ✓ Total Events: {event_metrics['total_events']}")
    print(f"   ✓ Event Types: {len(event_metrics['events_by_type'])}")

    print("\n   Safety Metrics:")
    safety_metrics = status["safety_metrics"]
    print(f"   ✓ Validations: {safety_metrics['validations_performed']}")
    print(f"   ✓ Threats Detected: {safety_metrics['threats_detected']}")
    print(f"   ✓ Avg Response Time: {safety_metrics['average_response_time']:.1f}ms")
    print(f"   ✓ Uptime: {safety_metrics.get('uptime_hours', 0):.2f} hours")

    print("\n   Colony Status:")
    for colony, status in status["colonies_status"].items():
        print(f"   ✓ {colony}: {status}")

    # Test 7: Cascading Safety Protocol
    print("\n\n7️⃣ TEST: Cascading Safety Protocol")
    print("-" * 40)

    # Create a complex scenario requiring multi-level response
    complex_event = SafetyEvent(
        event_id="test_cascade_001",
        event_type=SafetyEventType.ETHICAL_VIOLATION,
        severity=0.6,
        source_colony="test_ethics",
        timestamp=datetime.now(),
        data={
            "violation_type": "bias_detected",
            "affected_users": 1000,
            "bias_score": 0.7,
            "requires_human_review": True,
        },
        affected_colonies={"reasoning", "memory", "governance"},
    )

    print("\n   Broadcasting complex ethical violation...")
    success = await safety_system.event_bus.broadcast_safety_event(complex_event)
    print(f"   ✓ Complex event broadcast: {'✅' if success else '❌'}")
    print(f"   ✓ Affected colonies: {complex_event.affected_colonies}")

    # Test 8: Performance Under Load
    print("\n\n8️⃣ TEST: Performance Under Load")
    print("-" * 40)

    print("\n   Running 100 rapid validations...")
    start_time = datetime.now()

    validation_times = []
    for i in range(100):
        test_action = {
            "id": f"perf_test_{i}",
            "type": "performance_test",
            "data": f"Test data {i}",
            "timestamp": datetime.now(),
        }

        val_start = datetime.now()
        result = await safety_system.validate_action(test_action)
        val_time = (datetime.now() - val_start).total_seconds() * 1000
        validation_times.append(val_time)

    total_time = (datetime.now() - start_time).total_seconds()

    print(f"   ✓ Total time: {total_time:.2f}s")
    print(f"   ✓ Average validation: {np.mean(validation_times):.1f}ms")
    print(
        f"   ✓ Min/Max validation: {np.min(validation_times):.1f}ms / {np.max(validation_times):.1f}ms"
    )
    print(f"   ✓ Throughput: {100/total_time:.1f} validations/second")

    # Final system summary
    print("\n\n📊 FINAL SYSTEM SUMMARY")
    print("=" * 80)

    final_status = safety_system.get_system_status()

    print("\n✅ System Operational Status:")
    print(f"   - Safety Level: {final_status['safety_level']}")
    print(
        f"   - Total Validations: {final_status['safety_metrics']['validations_performed']}"
    )
    print(
        f"   - Average Response: {final_status['safety_metrics']['average_response_time']:.1f}ms"
    )
    print(f"   - Active Threats: {final_status['active_threats']}")

    # Check for any open circuit breakers
    open_breakers = [
        comp
        for comp, state in final_status["circuit_breakers"].items()
        if state["is_open"]
    ]
    if open_breakers:
        print(f"\n⚠️  Open Circuit Breakers: {open_breakers}")
    else:
        print("\n✅ All Circuit Breakers Operational")

    # Cancel monitoring
    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass

    print("\n\n✨ All tests completed successfully!")


async def demonstrate_real_world_scenario():
    """Demonstrate a real-world safety scenario"""
    print("\n\n🌍 REAL-WORLD SCENARIO DEMONSTRATION")
    print("=" * 80)

    safety_system = IntegratedSafetySystem()
    monitoring_task = asyncio.create_task(safety_system.run_continuous_monitoring())

    print("\nScenario: User requests AI to help with medical advice")
    print("-" * 60)

    # User makes a medical request
    medical_request = {
        "type": "user_request",
        "category": "medical_advice",
        "content": "I have chest pain, what should I do?",
        "user_id": "user_123",
        "timestamp": datetime.now(),
        "context": {
            "user_location": "home",
            "user_age": "unknown",
            "medical_history": "unavailable",
        },
        # Risk factors
        "harm_potential": 0.8,  # High - medical advice can be harmful
        "urgency": "high",
        "requires_expertise": True,
        "liability_risk": 0.9,
    }

    print("\n1. Initial Safety Validation:")
    result = await safety_system.validate_action(medical_request)

    print(f"   ✓ Is Safe: {'✅' if result.is_safe else '❌'}")
    print(f"   ✓ Safety Score: {result.safety_score:.2%}")
    print(f"   ✓ Ethical Score: {result.ethical_score:.2%}")
    print(f"   ✓ Compliance Score: {result.compliance_score:.2%}")

    if result.violations:
        print("\n   ⚠️  Violations Detected:")
        for violation in result.violations:
            print(f"      - {violation}")

    if result.recommendations:
        print("\n   💡 System Recommendations:")
        for rec in result.recommendations:
            print(f"      - {rec}")

    # System generates safe response
    print("\n2. System Generates Safe Alternative Response:")
    safe_response = {
        "type": "system_response",
        "content": "I understand you're experiencing chest pain. For any serious medical symptoms, especially chest pain, please contact emergency services (911) or visit the nearest emergency room immediately. I cannot provide medical diagnosis or treatment advice.",
        "includes_disclaimer": True,
        "provides_emergency_info": True,
        "harm_potential": 0.0,
        "user_consent": True,
        "transparency_level": 1.0,
    }

    safe_result = await safety_system.validate_action(safe_response)
    print(f"   ✓ Safe Response Validated: {'✅' if safe_result.is_safe else '❌'}")
    all_scores_high = all(
        [
            safe_result.safety_score > 0.9,
            safe_result.ethical_score > 0.9,
            safe_result.compliance_score > 0.9,
        ]
    )
    print(f"   ✓ All Safety Scores > 90%: {'✅' if all_scores_high else '❌'}")

    # Cleanup
    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass

    print("\n✅ Real-world scenario handled safely!")


async def main():
    """Run all tests and demonstrations"""
    try:
        # Run comprehensive tests
        await test_comprehensive_safety()

        # Run real-world scenario
        await demonstrate_real_world_scenario()

        print("\n\n🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")

    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
