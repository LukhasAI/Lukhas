#!/usr/bin/env python3
"""
Integration test for the complete LUKHAS Guardian System.
Tests the full workflow from issue detection to sub-agent coordination.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_remediator_agent_basic():
    """Test basic RemediatorAgent functionality."""

    from orchestration.monitoring.remediator_agent import (
        RemediatorAgent,
    )

    print("\n🎯 Testing RemediatorAgent Basic Functionality...")

    # Create RemediatorAgent
    remediation = RemediatorAgent()

    # Validate initialization
    assert remediation.agent_id is not None, "Should have agent ID"
    assert len(remediation.spawned_agents) == 0, "Should start with no spawned agents"
    assert len(remediation.remediation_history) == 0, "Should start with empty history"

    print(f"   ✅ RemediatorAgent created: {remediation.agent_id}")

    return remediation


def test_ethical_issue_remediation():
    """Test remediation of ethical issues."""

    from orchestration.monitoring.remediator_agent import RemediatorAgent

    print("\n🏛️ Testing Ethical Issue Remediation...")

    remediation = RemediatorAgent()

    # Define ethical issue
    ethical_issue = {
        "type": "ethical_violation",
        "severity": "high",
        "description": "Detected bias in decision-making algorithm",
        "indicators": ["bias_detected", "unfair_treatment", "autonomy_violation"],
        "decision_context": {
            "type": "automated_hiring",
            "informed_consent": False,
            "potential_bias": True,
            "affects_vulnerable": True,
            "explainable": False,
            "risks": ["discrimination", "unfair_treatment"],
            "consequence_severity": 0.8,
        },
    }

    # Execute remediation
    session = remediation.detect_and_remediate(ethical_issue)

    # Validate session
    assert session["status"] == "completed", "Session should be completed"
    assert len(session["spawned_agents"]) > 0, "Should spawn at least one agent"
    assert "results" in session, "Should have results"

    # Check for EthicsGuardian
    ethics_agent = None
    for agent_info in session["spawned_agents"]:
        if agent_info["agent_type"] == "EthicsGuardian":
            ethics_agent = agent_info
            break

    assert ethics_agent is not None, "Should spawn EthicsGuardian for ethical issue"

    # Validate results
    results = session["results"]
    agent_results = results["agent_results"]
    ethics_result = agent_results[ethics_agent["agent_id"]]

    assert "assessment" in ethics_result, "Should have ethical assessment"
    assert "recommendations" in ethics_result, "Should have recommendations"

    assessment = ethics_result["assessment"]
    assert assessment["overall_score"] is not None, "Should have overall score"
    assert len(assessment["violations_detected"]) > 0, "Should detect violations"

    print("   ✅ Ethical remediation completed")
    print(f"   - Session ID: {session['session_id']}")
    print(f"   - Ethics score: {assessment['overall_score']:.3f}")
    print(f"   - Violations: {len(assessment['violations_detected'])}")
    print(f"   - Recommendations: {len(assessment['recommendations'])}")

    return session


def test_memory_issue_remediation():
    """Test remediation of memory issues."""

    from orchestration.monitoring.remediator_agent import RemediatorAgent

    print("\n🧹 Testing Memory Issue Remediation...")

    remediation = RemediatorAgent()

    # Define memory issue
    memory_issue = {
        "type": "memory_fragmentation",
        "severity": "medium",
        "description": "High memory fragmentation detected",
        "indicators": ["memory_fragmentation", "performance_degradation"],
        "memory_stats": {
            "fragmentation_level": 0.8,
            "available_memory": "40%",
            "optimization_needed": True,
        },
    }

    # Execute remediation
    session = remediation.detect_and_remediate(memory_issue)

    # Validate session
    assert session["status"] == "completed", "Session should be completed"
    assert len(session["spawned_agents"]) > 0, "Should spawn at least one agent"

    # Check for MemoryCleaner
    memory_agent = None
    for agent_info in session["spawned_agents"]:
        if agent_info["agent_type"] == "MemoryCleaner":
            memory_agent = agent_info
            break

    assert memory_agent is not None, "Should spawn MemoryCleaner for memory issue"

    # Validate results
    results = session["results"]
    agent_results = results["agent_results"]
    memory_result = agent_results[memory_agent["agent_id"]]

    assert "analysis" in memory_result, "Should have memory analysis"
    assert "recommendations" in memory_result, "Should have recommendations"

    analysis = memory_result["analysis"]
    assert (
        analysis["fragmentation_level"] is not None
    ), "Should have fragmentation level"
    assert "optimization_potential" in analysis, "Should have optimization potential"

    print("   ✅ Memory remediation completed")
    print(f"   - Session ID: {session['session_id']}")
    print(f"   - Fragmentation: {analysis['fragmentation_level']:.1%}")
    print(f"   - Cleanup performed: {memory_result['cleanup_performed']}")
    print(f"   - Dream optimization: {memory_result['dream_optimization']}")

    return session


def test_multi_domain_remediation():
    """Test remediation of complex multi-domain issues."""

    from orchestration.monitoring.remediator_agent import RemediatorAgent

    print("\n🔄 Testing Multi-Domain Issue Remediation...")

    remediation = RemediatorAgent()

    # Define complex issue with both ethical and memory concerns
    complex_issue = {
        "type": "system_degradation",
        "severity": "critical",
        "description": "System showing both ethical drift and memory issues",
        "indicators": [
            "bias_detected",
            "memory_fragmentation",
            "performance_degradation",
            "ethical_violations",
            "unfair_outcomes",
        ],
        "decision_context": {
            "type": "recommendation_system",
            "potential_bias": True,
            "explainable": False,
            "affects_vulnerable": True,
        },
        "memory_stats": {"fragmentation_level": 0.9, "corruption_detected": True},
    }

    # Execute remediation
    session = remediation.detect_and_remediate(complex_issue)

    # Validate session
    assert session["status"] == "completed", "Session should be completed"
    assert (
        len(session["spawned_agents"]) >= 2
    ), "Should spawn multiple agents for complex issue"

    # Check for both agent types
    has_ethics = False
    has_memory = False

    for agent_info in session["spawned_agents"]:
        if agent_info["agent_type"] == "EthicsGuardian":
            has_ethics = True
        elif agent_info["agent_type"] == "MemoryCleaner":
            has_memory = True

    assert has_ethics, "Should spawn EthicsGuardian for complex issue"
    assert has_memory, "Should spawn MemoryCleaner for complex issue"

    # Validate comprehensive results
    results = session["results"]
    assert (
        len(results["agent_results"]) >= 2
    ), "Should have results from multiple agents"
    assert len(results["recommendations"]) > 0, "Should have aggregated recommendations"

    print("   ✅ Multi-domain remediation completed")
    print(f"   - Session ID: {session['session_id']}")
    print(f"   - Agents spawned: {len(session['spawned_agents'])}")
    print(f"   - Total recommendations: {len(results['recommendations'])}")

    return session


def test_manual_agent_spawning():
    """Test manual spawning of specific agents."""

    from orchestration.monitoring.remediator_agent import RemediatorAgent

    print("\n🎮 Testing Manual Agent Spawning...")

    remediation = RemediatorAgent()

    # Manually spawn EthicsGuardian
    ethics_task = {
        "violation_type": "transparency_concern",
        "severity": "medium",
        "context": "manual_review",
    }

    ethics_agent_id = remediation.spawn_ethics_guardian(ethics_task)
    assert ethics_agent_id is not None, "Should return agent ID"

    # Manually spawn MemoryCleaner
    memory_task = {
        "memory_issue": "routine_maintenance",
        "severity": "low",
        "context": "scheduled_cleanup",
    }

    memory_agent_id = remediation.spawn_memory_cleaner(memory_task)
    assert memory_agent_id is not None, "Should return agent ID"

    # Verify agents are tracked
    assert len(remediation.spawned_agents) == 2, "Should track both spawned agents"

    ethics_status = remediation.get_agent_status(ethics_agent_id)
    memory_status = remediation.get_agent_status(memory_agent_id)

    assert ethics_status is not None, "Should have ethics agent status"
    assert memory_status is not None, "Should have memory agent status"
    assert ethics_status["agent_type"] == "EthicsGuardian", "Should be EthicsGuardian"
    assert memory_status["agent_type"] == "MemoryCleaner", "Should be MemoryCleaner"

    print("   ✅ Manual spawning completed")
    print(f"   - EthicsGuardian: {ethics_agent_id}")
    print(f"   - MemoryCleaner: {memory_agent_id}")

    return remediation


def test_system_monitoring_integration():
    """Test integration with monitoring system."""

    from orchestration.monitoring.remediator_agent import RemediatorAgent

    print("\n📊 Testing System Monitoring Integration...")

    remediation = RemediatorAgent()

    # Simulate multiple remediation sessions
    issues = [
        {
            "type": "ethical_concern",
            "severity": "medium",
            "indicators": ["bias_potential"],
        },
        {
            "type": "memory_optimization",
            "severity": "low",
            "indicators": ["fragmentation"],
        },
    ]

    sessions = []
    for issue in issues:
        session = remediation.detect_and_remediate(issue)
        sessions.append(session)

    # Test monitoring capabilities
    active_sessions = remediation.get_active_sessions()
    history = remediation.get_remediation_history()

    # Validate monitoring data
    assert len(history) == 2, "Should have 2 sessions in history"
    assert len(active_sessions) == 0, "Should have no active sessions (all completed)"

    # Validate session data quality
    for session in history:
        assert "session_id" in session, "Should have session ID"
        assert "start_time" in session, "Should have start time"
        assert "end_time" in session, "Should have end time"
        assert "status" in session, "Should have status"
        assert "results" in session, "Should have results"

    print("   ✅ Monitoring integration verified")
    print(f"   - Sessions completed: {len(history)}")
    print(f"   - Active sessions: {len(active_sessions)}")

    return remediation


def test_full_guardian_system_pipeline():
    """Test the complete guardian system pipeline."""

    print("\n🔄 Testing Full Guardian System Pipeline...")

    # Import the complete monitoring system
    try:
        from orchestration.monitoring import (
            EthicsGuardian,
            MemoryCleaner,
            RemediatorAgent,
        )

        print("   ✅ All monitoring components imported successfully")
    except ImportError as e:
        print(f"   ⚠️ Import warning: {e}")
        # Fall back to direct imports
        from orchestration.monitoring.remediator_agent import RemediatorAgent

    # Create comprehensive test scenario
    remediation = RemediatorAgent("INTEGRATION_TEST")

    # Complex system issue
    system_issue = {
        "type": "comprehensive_system_audit",
        "severity": "high",
        "description": "Full system health check and remediation",
        "indicators": [
            "ethical_drift_detected",
            "memory_fragmentation_high",
            "performance_degradation",
            "compliance_concerns",
        ],
        "decision_context": {
            "type": "ai_system_operation",
            "informed_consent": False,
            "potential_bias": True,
            "affects_vulnerable": True,
            "explainable": False,
            "risks": ["bias", "discrimination", "privacy_breach"],
            "consequence_severity": 0.9,
        },
        "memory_stats": {
            "fragmentation_level": 0.85,
            "corruption_detected": True,
            "optimization_needed": True,
        },
    }

    # Execute comprehensive remediation
    session = remediation.detect_and_remediate(system_issue)

    # Comprehensive validation
    assert session["status"] == "completed", "Pipeline should complete successfully"
    assert (
        len(session["spawned_agents"]) >= 2
    ), "Should spawn multiple specialized agents"

    # Validate agent coordination
    results = session["results"]
    assert results["overall_success"], "Pipeline should succeed overall"
    assert (
        len(results["recommendations"]) > 0
    ), "Should provide actionable recommendations"

    # Validate individual agent performance
    for agent_id, agent_result in results["agent_results"].items():
        assert (
            agent_result["status"] == "completed"
        ), f"Agent {agent_id} should complete successfully"

    # Calculate pipeline metrics
    duration = (session["end_time"] - session["start_time"]).total_seconds()
    agent_count = len(session["spawned_agents"])
    recommendation_count = len(results["recommendations"])

    print("   ✅ Full pipeline completed successfully")
    print(f"   - Duration: {duration:.2f} seconds")
    print(f"   - Agents deployed: {agent_count}")
    print(f"   - Recommendations generated: {recommendation_count}")
    print(f"   - Overall success: {results['overall_success']}")

    return {
        "session": session,
        "duration": duration,
        "agent_count": agent_count,
        "recommendation_count": recommendation_count,
        "success": results["overall_success"],
    }


if __name__ == "__main__":
    try:
        print("🚀 Starting LUKHAS Guardian System Integration Tests...")

        # Run all integration tests
        remediation_basic = test_remediator_agent_basic()
        ethical_session = test_ethical_issue_remediation()
        memory_session = test_memory_issue_remediation()
        multi_domain_session = test_multi_domain_remediation()
        manual_agents = test_manual_agent_spawning()
        monitoring_integration = test_system_monitoring_integration()
        pipeline_result = test_full_guardian_system_pipeline()

        print("\n" + "=" * 60)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n📋 Test Summary:")
        print("   - Basic functionality: ✅")
        print("   - Ethical remediation: ✅")
        print("   - Memory remediation: ✅")
        print("   - Multi-domain handling: ✅")
        print("   - Manual agent spawning: ✅")
        print("   - Monitoring integration: ✅")
        print("   - Full pipeline: ✅")

        print("\n🏆 Pipeline Performance:")
        print(f"   - Total duration: {pipeline_result['duration']:.2f}s")
        print(f"   - Agents deployed: {pipeline_result['agent_count']}")
        print(f"   - Recommendations: {pipeline_result['recommendation_count']}")
        print("   - Success rate: 100%")

        print("\n✨ LUKHAS Guardian System is fully integrated and operational!")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
