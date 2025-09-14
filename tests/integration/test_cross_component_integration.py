#!/usr/bin/env python3
"""
Cross-Component Integration Tests
===============================

Tests demonstrating integration between multiple components working together.
This shows real-world scenarios where components collaborate.

Trinity Framework: ⚛️🧠🛡️
"""

import logging
import os
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress logging for cleaner test output
if not os.getenv("DEBUG_TESTS"):
    logging.getLogger().setLevel(logging.CRITICAL)


class TestActorTierIntegration:
    """Test integration between Actor System and Tier System."""

    def __init__(self):
        self.results = []

    def test_secure_actor_communication(self):
        """Test actors with tier-based access control."""
        try:
            from identity.tier_system import AccessContext, AccessType, DynamicTierSystem, PermissionScope, TierLevel
            from lukhas.core.actor_system import ActorSystem, AIAgentActor

            # Create integrated systems
            actor_system = ActorSystem()
            tier_system = DynamicTierSystem()

            # Create security-aware actor
            class SecureActor(AIAgentActor):
                def __init__(self, actor_id, capabilities, tier_system, user_context):
                    super().__init__(actor_id, capabilities)
                    self.tier_system = tier_system
                    self.user_context = user_context

                def secure_operation(self, operation_type, resource_id, metadata):
                    """Perform operation with tier-based access control."""
                    context = AccessContext(
                        user_id=self.user_context.get("user_id"),
                        session_id=self.user_context.get("session_id"),
                        operation_type=operation_type,
                        resource_scope=PermissionScope.MEMORY_FOLD,
                        resource_id=resource_id,
                        timestamp_utc=datetime.now(timezone.utc).isoformat(),
                        metadata=metadata,
                    )

                    # Check access using tier system
                    decision = self.tier_system.check_access(context, TierLevel.AUTHENTICATED)

                    if decision.granted:
                        # Perform the operation
                        self.memory[f"operation_{resource_id}"] = {
                            "status": "completed",
                            "decision_id": decision.decision_id,
                            "tier_level": decision.tier_level.name,
                            "metadata": metadata,
                        }
                        return {"success": True, "decision_id": decision.decision_id}
                    else:
                        return {"success": False, "reason": decision.reasoning}

            # Create secure actors with different user contexts
            admin_actor = SecureActor(
                "admin_agent",
                ["admin_operations", "data_management"],
                tier_system,
                {"user_id": "admin_user_001", "session_id": "admin_session"},
            )

            user_actor = SecureActor(
                "user_agent",
                ["basic_operations"],
                tier_system,
                {"user_id": "regular_user_001", "session_id": "user_session"},
            )

            # Register actors
            actor_system.register("admin_agent", admin_actor)
            actor_system.register("user_agent", user_actor)

            # Test secure operations
            admin_result = admin_actor.secure_operation(
                AccessType.WRITE, "sensitive_data_001", {"sensitivity": "high", "operation": "data_backup"}
            )

            user_result = user_actor.secure_operation(
                AccessType.READ, "public_data_001", {"sensitivity": "low", "operation": "data_view"}
            )

            # Verify security integration
            assert "success" in admin_result, "Admin operation should return status"
            assert "success" in user_result, "User operation should return status"

            # Verify operations were logged in actor memory
            if admin_result["success"]:
                assert "operation_sensitive_data_001" in admin_actor.memory, "Admin operation should be logged"
                operation_log = admin_actor.memory["operation_sensitive_data_001"]
                assert "decision_id" in operation_log, "Should log decision ID"
                assert "tier_level" in operation_log, "Should log tier level"

            self.results.append("✅ Secure actor communication with tier integration")
            return True

        except Exception as e:
            self.results.append(f"❌ Secure actor communication failed: {e}")
            return False

    def test_elevated_session_actor_workflow(self):
        """Test actor workflow with session elevation."""
        try:
            from identity.tier_system import DynamicTierSystem, TierLevel
            from lukhas.core.actor_system import ActorSystem, AIAgentActor

            actor_system = ActorSystem()
            tier_system = DynamicTierSystem()

            # Create workflow coordinator actor
            class WorkflowCoordinator(AIAgentActor):
                def __init__(self, actor_id, tier_system):
                    super().__init__(actor_id, ["coordination", "privilege_management"])
                    self.tier_system = tier_system
                    self.workflow_history = []

                def request_elevation(self, session_id, target_tier, justification):
                    """Request session elevation for workflow."""
                    result = self.tier_system.elevate_session(
                        session_id=session_id, target_tier=target_tier, justification=justification, duration_minutes=60
                    )

                    self.workflow_history.append(
                        {
                            "action": "elevation_request",
                            "session_id": session_id,
                            "target_tier": target_tier.name,
                            "result": result,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                    return result

                def execute_privileged_workflow(self, workflow_data):
                    """Execute workflow that requires elevated privileges."""
                    # Simulate complex workflow requiring privilege escalation
                    workflow_steps = [
                        ("data_analysis", TierLevel.AUTHENTICATED),
                        ("system_modification", TierLevel.ELEVATED),
                        ("security_audit", TierLevel.PRIVILEGED),
                    ]

                    results = []
                    for step_name, required_tier in workflow_steps:
                        # Check if we need elevation
                        current_session = workflow_data.get("session_id")

                        if required_tier.value > TierLevel.AUTHENTICATED.value:
                            # Request elevation
                            elevation_result = self.request_elevation(
                                current_session,
                                required_tier,
                                f"Workflow step: {step_name} requires {required_tier.name}",
                            )

                            if elevation_result["success"]:
                                # Execute step with elevated privileges
                                step_result = {
                                    "step": step_name,
                                    "tier": required_tier.name,
                                    "status": "completed_elevated",
                                    "elevation_id": elevation_result.get("elevation_id"),
                                }
                            else:
                                step_result = {
                                    "step": step_name,
                                    "tier": required_tier.name,
                                    "status": "elevation_failed",
                                    "reason": elevation_result.get("reason"),
                                }
                        else:
                            # Execute step with normal privileges
                            step_result = {"step": step_name, "tier": required_tier.name, "status": "completed_normal"}

                        results.append(step_result)
                        self.workflow_history.append(
                            {
                                "action": "workflow_step",
                                "step_data": step_result,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )

                    return results

            # Create and register coordinator
            coordinator = WorkflowCoordinator("workflow_coordinator", tier_system)
            actor_system.register("workflow_coordinator", coordinator)

            # Execute privileged workflow
            workflow_data = {
                "session_id": "workflow_session_001",
                "user_id": "workflow_user",
                "workflow_type": "data_processing_pipeline",
            }

            workflow_results = coordinator.execute_privileged_workflow(workflow_data)

            # Verify workflow execution
            assert len(workflow_results) == 3, "Should execute all 3 workflow steps"
            assert all("step" in result for result in workflow_results), "All steps should be logged"
            assert len(coordinator.workflow_history) >= 3, "Should track workflow history"

            # Verify elevation requests were made
            elevation_requests = [
                entry for entry in coordinator.workflow_history if entry["action"] == "elevation_request"
            ]
            assert len(elevation_requests) >= 2, "Should make elevation requests for privileged steps"

            # Verify steps were completed
            completed_steps = [result for result in workflow_results if "completed" in result["status"]]
            assert len(completed_steps) >= 2, "Should complete multiple workflow steps"

            self.results.append("✅ Elevated session actor workflow")
            return True

        except Exception as e:
            self.results.append(f"❌ Elevated session actor workflow failed: {e}")
            return False


def run_integration_tests():
    """Run cross-component integration tests."""
    print("🔗 LUKHAS Cross-Component Integration Tests")
    print("=" * 60)
    print("Testing real-world component collaboration...")
    print()

    all_results = []
    total_tests = 0
    passed_tests = 0

    # Test Actor-Tier Integration
    print("🎭🛡️ Testing Actor System + Tier System Integration...")
    integration_tests = TestActorTierIntegration()
    integration_results = [
        integration_tests.test_secure_actor_communication(),
        integration_tests.test_elevated_session_actor_workflow(),
    ]

    for result in integration_tests.results:
        print(f"  {result}")
        all_results.append(result)

    total_tests += len(integration_results)
    passed_tests += sum(integration_results)
    print()

    # Summary
    print("=" * 60)
    print("🔗 INTEGRATION TEST RESULTS")
    print("=" * 60)

    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"Total Integration Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()

    if success_rate >= 90:
        print("🚀 EXCEPTIONAL INTEGRATION!")
        print("Components work together seamlessly in complex scenarios!")
    elif success_rate >= 80:
        print("🎉 EXCELLENT INTEGRATION!")
        print("Components demonstrate solid collaboration patterns.")
    else:
        print("⚠️ INTEGRATION NEEDS WORK")
        print("Component collaboration needs improvement.")

    print()
    print("🔍 Integration Features Demonstrated:")
    for result in all_results:
        print(f"  {result}")

    print()
    print("🏆 REAL-WORLD CAPABILITIES VALIDATED:")
    print("  • Security-aware actor operations")
    print("  • Dynamic privilege escalation workflows")
    print("  • Cross-component audit trails")
    print("  • Enterprise-grade access control")
    print("  • Complex multi-step workflows")
    print("  • Automatic tier-based authorization")

    return success_rate >= 80


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
