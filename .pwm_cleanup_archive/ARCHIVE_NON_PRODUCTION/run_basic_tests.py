#!/usr/bin/env python3
"""
Basic Integration Tests for LUKHAS Identity System

This script runs core tests with proper error handling for missing dependencies.
"""

import asyncio
import hashlib
import json
import logging
import os
import sys
from datetime import datetime

import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("IDENTITY_TEST")


async def test_biometric_colony():
    """Test biometric verification colony."""
    logger.info("\n=== Testing Biometric Verification Colony ===")

    try:
        from identity.core.colonies.biometric_verification_colony import (
            BiometricSample,
            BiometricType,
            BiometricVerificationColony,
        )

        # Initialize colony
        colony = BiometricVerificationColony("test_biometric")
        await colony.initialize()

        # Test data
        lambda_id = "test_user_001"

        # Create biometric samples
        samples = []
        for bio_type in ["fingerprint", "facial"]:
            sample = BiometricSample(
                sample_id=f"sample_{bio_type}_001",
                biometric_type=BiometricType(bio_type),
                raw_data=np.random.bytes(1024),
                quality_score=0.85,
                capture_timestamp=datetime.utcnow(),
                device_id="test_device",
                environmental_factors={"lighting": "good"},
                preprocessing_applied=["normalization"],
            )
            samples.append(sample)

        # Reference template
        reference = hashlib.sha256(b"test_reference").digest()

        # Perform verification
        result = await colony.verify_biometric_identity(
            lambda_id=lambda_id,
            biometric_samples=samples,
            reference_template=reference,
            tier_level=2,
            session_id="test_session_001",
        )

        # Report results
        logger.info(f"Verification Result: {result.verified}")
        logger.info(f"Confidence: {result.confidence_score:.3f}")
        logger.info(f"Agents Involved: {result.agents_involved}")

        # Get colony health
        health = colony.get_colony_health_status()
        logger.info(f"Colony Health: {health['health_score']:.3f}")
        logger.info(f"Total Agents: {health['total_agents']}")

        return {
            "test": "biometric_colony",
            "success": True,
            "verified": result.verified,
            "confidence": result.confidence_score,
            "health_score": health["health_score"],
            "agent_count": health["total_agents"],
        }

    except Exception as e:
        logger.error(f"Biometric colony test failed: {e}")
        import traceback

        traceback.print_exc()
        return {"test": "biometric_colony", "success": False, "error": str(e)}


async def test_consciousness_colony():
    """Test consciousness verification colony."""
    logger.info("\n=== Testing Consciousness Verification Colony ===")

    try:
        from identity.core.colonies.consciousness_verification_colony import (
            ConsciousnessVerificationColony,
        )

        # Initialize colony
        colony = ConsciousnessVerificationColony("test_consciousness")
        await colony.initialize()

        # Test data
        lambda_id = "test_user_002"

        # Mock consciousness data
        consciousness_data = {
            "brainwave_patterns": {
                "alpha": np.random.random(100) * 30,
                "beta": np.random.random(100) * 50,
                "gamma": np.random.random(100) * 100,
                "theta": np.random.random(100) * 10,
                "delta": np.random.random(100) * 5,
            },
            "coherence_score": 0.75,
            "emotional_state": {"valence": 0.5, "arousal": 0.6, "dominance": 0.7},
            "meditation_depth": 0.4,
            "focus_level": 0.8,
        }

        # Perform verification
        result = await colony.verify_consciousness_state(
            lambda_id=lambda_id,
            consciousness_data=consciousness_data,
            tier_level=3,
            session_id="test_session_002",
        )

        # Report results
        logger.info(f"Consciousness Verification: {result.verified}")
        logger.info(f"Confidence: {result.confidence_score:.3f}")
        logger.info(f"Analysis Methods: {result.agents_involved}")

        # Get emergent patterns
        patterns = colony.get_emergent_patterns()
        logger.info(f"Emergent Patterns Found: {len(patterns)}")

        return {
            "test": "consciousness_colony",
            "success": True,
            "verified": result.verified,
            "confidence": result.confidence_score,
            "emergent_patterns": len(patterns),
        }

    except Exception as e:
        logger.error(f"Consciousness colony test failed: {e}")
        return {"test": "consciousness_colony", "success": False, "error": str(e)}


async def test_swarm_hub():
    """Test tier-aware swarm hub."""
    logger.info("\n=== Testing Tier-Aware Swarm Hub ===")

    try:
        from identity.core.swarm.tier_aware_swarm_hub import TierAwareSwarmHub

        # Initialize hub
        hub = TierAwareSwarmHub("test_hub")
        await hub.initialize()

        # Test task submission
        lambda_id = "test_user_003"

        task_id = await hub.submit_identity_verification_task(
            lambda_id=lambda_id,
            tier_level=2,
            verification_type="standard",
            session_id="test_session_003",
            auth_data={
                "biometric_data": {
                    "samples": [{"type": "fingerprint", "data": "mock"}],
                    "template": b"mock_template",
                }
            },
        )

        logger.info(f"Task Submitted: {task_id[:30]}...")

        # Get hub stats
        stats = hub.get_hub_statistics()
        logger.info(f"Active Orchestrations: {stats['active_orchestrations']}")
        logger.info(f"Colony Health: {len(stats['colony_health'])} colonies")

        # Get tier performance
        performance = hub.get_tier_performance_report()
        logger.info(f"Performance Report: {len(performance)} tiers tracked")

        return {
            "test": "swarm_hub",
            "success": True,
            "task_id": task_id,
            "active_orchestrations": stats["active_orchestrations"],
            "colonies_registered": len(stats["colony_health"]),
        }

    except Exception as e:
        logger.error(f"Swarm hub test failed: {e}")
        return {"test": "swarm_hub", "success": False, "error": str(e)}


async def test_tag_resolver():
    """Test identity tag resolver with trust networks."""
    logger.info("\n=== Testing Identity Tag Resolver ===")

    try:
        from identity.core.tagging.identity_tag_resolver import (
            IdentityTagResolver,
            IdentityTagType,
            TrustLevel,
        )

        # Initialize resolver
        resolver = IdentityTagResolver("test_resolver")
        await resolver.initialize()

        # Create test identities
        user1 = "test_user_004"
        user2 = "test_user_005"

        # Establish trust
        await resolver.establish_trust_relationship(
            from_identity=user1, to_identity=user2, initial_trust=TrustLevel.MEDIUM
        )

        logger.info(f"Trust established: {user1} -> {user2}")

        # Assign tag
        tag_id = await resolver.assign_identity_tag(
            lambda_id=user1,
            tag_type=IdentityTagType.CAPABILITY,
            tag_value="test_capability",
            tier_level=2,
            metadata={"test": True},
        )

        logger.info(f"Tag assigned: {tag_id}")

        # Get reputation
        reputation = resolver.get_identity_reputation(user1)
        logger.info(f"Reputation Score: {reputation['overall_reputation']:.3f}")

        # Get stats
        stats = resolver.get_resolver_statistics()
        logger.info(f"Trust Relationships: {stats['trust_relationships']}")
        logger.info(f"Total Tags: {stats['total_tags']}")

        return {
            "test": "tag_resolver",
            "success": True,
            "trust_relationships": stats["trust_relationships"],
            "total_tags": stats["total_tags"],
            "reputation_score": reputation["overall_reputation"],
        }

    except Exception as e:
        logger.error(f"Tag resolver test failed: {e}")
        return {"test": "tag_resolver", "success": False, "error": str(e)}


async def test_health_monitor():
    """Test health monitoring system."""
    logger.info("\n=== Testing Health Monitor ===")

    try:
        from identity.core.health.identity_health_monitor import (
            ComponentType,
            HealthMetric,
            IdentityHealthMonitor,
        )

        # Initialize monitor
        monitor = IdentityHealthMonitor("test_monitor")
        await monitor.initialize()

        # Register component
        await monitor.register_component(
            "test_component", ComponentType.COLONY, tier_level=2
        )

        logger.info("Component registered")

        # Report healthy metrics
        await monitor.report_component_metrics(
            "test_component",
            {
                HealthMetric.SUCCESS_RATE: 0.95,
                HealthMetric.ERROR_RATE: 0.05,
                HealthMetric.RESPONSE_TIME: 150,
            },
            tier_level=2,
        )

        # Get system health
        health = monitor.get_system_health_report()
        logger.info(f"System Health: {health['overall_health']:.3f}")
        logger.info(f"Components: {health['component_count']}")
        logger.info(f"Active Healing: {health['active_healing_plans']}")

        return {
            "test": "health_monitor",
            "success": True,
            "overall_health": health["overall_health"],
            "component_count": health["component_count"],
            "active_healing": health["active_healing_plans"],
        }

    except Exception as e:
        logger.error(f"Health monitor test failed: {e}")
        return {"test": "health_monitor", "success": False, "error": str(e)}


async def test_glyph_generation():
    """Test distributed GLYPH generation."""
    logger.info("\n=== Testing GLYPH Generation ===")

    try:
        from identity.core.glyph.distributed_glyph_generation import (
            DistributedGLYPHColony,
            GLYPHType,
        )

        # Initialize colony
        colony = DistributedGLYPHColony("test_glyph")
        await colony.initialize()

        # Test data
        lambda_id = "test_user_006"

        # Generate GLYPH
        glyph = await colony.generate_identity_glyph(
            lambda_id=lambda_id,
            glyph_type=GLYPHType.AUTHENTICATION,
            tier_level=2,
            identity_data={"lambda_id": lambda_id, "tier": 2, "test": True},
            session_id="test_session_006",
        )

        logger.info(f"GLYPH Generated: {glyph.glyph_id[:30]}...")
        logger.info(
            f"Quality Score: {glyph.quality_metrics.get('overall_quality', 0):.3f}"
        )
        logger.info(f"Fragments Used: {len(glyph.fragments_used)}")
        logger.info(f"Image Size: {glyph.image_data.shape}")

        # Get colony stats
        stats = colony.get_colony_statistics()
        logger.info(f"Total GLYPHs Generated: {stats['total_glyphs_generated']}")

        return {
            "test": "glyph_generation",
            "success": True,
            "glyph_id": glyph.glyph_id,
            "quality_score": glyph.quality_metrics.get("overall_quality", 0),
            "fragments": len(glyph.fragments_used),
            "image_shape": str(glyph.image_data.shape),
        }

    except Exception as e:
        logger.error(f"GLYPH generation test failed: {e}")
        return {"test": "glyph_generation", "success": False, "error": str(e)}


async def test_colony_connectivity():
    """Test basic colony connectivity."""
    logger.info("\n=== Testing Colony Connectivity ===")

    try:
        from identity.core.colonies import BiometricVerificationColony
        from identity.core.events import (
            IdentityEventType,
            get_identity_event_publisher,
        )

        # Initialize colony
        colony = BiometricVerificationColony("connectivity_test")
        await colony.initialize()

        # Get event publisher
        publisher = await get_identity_event_publisher()

        # Test event publishing
        event_id = await publisher.publish_colony_event(
            IdentityEventType.COLONY_HEALTH_CHECK,
            lambda_id="system",
            tier_level=0,
            colony_id=colony.colony_id,
            consensus_data={"test": True},
        )

        logger.info(f"Event Published: {event_id}")

        # Check colony agents
        agent_count = len(colony.agents)
        active_agents = sum(
            1
            for agent in colony.agents.values()
            if str(agent.state) in ["AgentState.IDLE", "AgentState.WORKING"]
        )

        logger.info(f"Total Agents: {agent_count}")
        logger.info(f"Active Agents: {active_agents}")

        # Get event stats
        event_stats = publisher.get_event_statistics()
        logger.info(f"Total Events: {event_stats['total_events']}")

        return {
            "test": "colony_connectivity",
            "success": True,
            "agent_count": agent_count,
            "active_agents": active_agents,
            "event_published": bool(event_id),
            "total_events": event_stats["total_events"],
        }

    except Exception as e:
        logger.error(f"Colony connectivity test failed: {e}")
        return {"test": "colony_connectivity", "success": False, "error": str(e)}


async def run_all_tests():
    """Run all basic tests."""
    print("\n" + "=" * 60)
    print("LUKHAS IDENTITY SYSTEM - BASIC INTEGRATION TESTS")
    print("=" * 60)
    print(f"Start Time: {datetime.utcnow().isoformat()}")
    print("=" * 60 + "\n")

    # Define tests
    tests = [
        test_biometric_colony,
        test_consciousness_colony,
        test_swarm_hub,
        test_tag_resolver,
        test_health_monitor,
        test_glyph_generation,
        test_colony_connectivity,
    ]

    results = []

    # Run each test
    for test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test_func.__name__} crashed: {e}")
            results.append(
                {
                    "test": test_func.__name__,
                    "success": False,
                    "error": f"Crash: {str(e)}",
                }
            )

    # Generate summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get("success", False))
    failed = len(results) - passed

    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")

    print("\nDetailed Results:")
    for result in results:
        status = "✓" if result.get("success", False) else "✗"
        test_name = result.get("test", "unknown")
        if result.get("success", False):
            print(f"  {status} {test_name}")
            for key, value in result.items():
                if key not in ["test", "success"]:
                    print(f"      {key}: {value}")
        else:
            print(f"  {status} {test_name}: {result.get('error', 'Unknown error')}")

    # Save results
    os.makedirs("identity/tests/results", exist_ok=True)

    timestamp = int(datetime.utcnow().timestamp())

    # Save detailed results
    with open(f"identity/tests/results/basic_test_results_{timestamp}.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "total_tests": len(results),
                "passed": passed,
                "failed": failed,
                "success_rate": passed / len(results) if results else 0,
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )

    # Save summary
    with open("identity/tests/results/test_summary_latest.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "test_type": "basic_integration",
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "tests": [r.get("test", "unknown") for r in results],
            },
            f,
            indent=2,
        )

    print("\nResults saved to: identity/tests/results/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
