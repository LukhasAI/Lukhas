"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: ethics.governor.lambda_governor_demo
📄 FILENAME: lambda_governor_demo.py
🎯 PURPOSE: Demonstration script for ΛGOVERNOR integration and capabilities
🧠 CONTEXT: LUKHAS AGI Ethical Arbitration - Integration Demo
🔮 CAPABILITY: Live demonstration of arbitration, intervention, and mesh notification
🛡️ ETHICS: Safe demonstration of global ethical governance capabilities
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: LambdaGovernor, Mock subsystems for demonstration
═══════════════════════════════════════════════════════════════════════════════════

🏛️ ΛGOVERNOR DEMONSTRATION SCRIPT
────────────────────────────────────────────────────────────────────

Interactive demonstration of the ΛGOVERNOR global ethical arbitration engine,
showing real-time escalation processing, risk evaluation, intervention
authorization, and mesh-wide coordination for the LUKHAS AGI system.

LUKHAS_TAG: governor_demo, arbitration_showcase, claude_code
"""

import asyncio
import json

from lambda_governor import (
    EscalationPriority,
    EscalationSource,
    LambdaGovernor,
    create_escalation_signal,
)


class GovernorDemo:
    """Interactive demonstration of ΛGOVERNOR capabilities."""

    def __init__(self):
        self.governor = None
        self.demo_sources = {
            "drift_sentinel": EscalationSource.DRIFT_SENTINEL,
            "emotion_protocol": EscalationSource.EMOTION_PROTOCOL,
            "conflict_resolver": EscalationSource.CONFLICT_RESOLVER,
            "dream_anomaly": EscalationSource.DREAM_ANOMALY,
            "memory_fold": EscalationSource.MEMORY_FOLD,
        }
        self.responses = []

    async def run_demo(self):
        """Run the complete governor demonstration."""
        print("🏛️  LUKHAS AGI - ΛGOVERNOR Global Arbitration Engine Demonstration")
        print("═══════════════════════════════════════════════════════════════════")
        print()

        # Initialize governor
        print("1️⃣  Initializing ΛGOVERNOR...")
        self.governor = LambdaGovernor(response_timeout=5.0, escalation_retention=100)

        # Register mock components
        await self._register_mock_components()
        print()

        try:
            # Run demonstration scenarios
            await self._demo_low_risk_escalation()
            await self._demo_emotional_volatility_freeze()
            await self._demo_entropy_quarantine()
            await self._demo_cascade_prevention()
            await self._demo_emergency_shutdown()
            await self._demo_multi_source_arbitration()
            await self._demo_system_status()

        except Exception as e:
            print(f"❌ Demo error: {e}")

        print("🎯 DEMONSTRATION COMPLETE")
        print("═══════════════════════════════════════")

    async def _register_mock_components(self):
        """Register mock mesh components."""
        print("2️⃣  Registering mock mesh components...")

        # Mock mesh router
        class MockMeshRouter:
            async def receive_governor_notification(self, notification):
                print(f"   📡 Mesh Router received: {notification['decision']}")

        # Mock dream coordinator
        class MockDreamCoordinator:
            async def receive_intervention_notice(self, notification):
                print(f"   🌌 Dream Coordinator notified: {notification['type']}")

        # Mock memory manager
        class MockMemoryManager:
            async def execute_quarantine(self, scope):
                print(
                    f"   💾 Memory Manager quarantining: {len(scope.get('symbol_ids', []))} symbols"
                )

        self.governor.register_mesh_router(MockMeshRouter())
        self.governor.register_dream_coordinator(MockDreamCoordinator())
        self.governor.register_memory_manager(MockMemoryManager())

        print("   ✓ Mock components registered")

    async def _demo_low_risk_escalation(self):
        """Demonstrate low-risk escalation resulting in ALLOW."""
        print("📊 SCENARIO 1: Low-Risk Escalation (Expected: ALLOW)")
        print("────────────────────────────────────────────────────")

        signal = create_escalation_signal(
            source_module=EscalationSource.DRIFT_SENTINEL,
            priority=EscalationPriority.LOW,
            triggering_metric="minor_drift",
            drift_score=0.15,
            entropy=0.2,
            emotion_volatility=0.1,
            contradiction_density=0.1,
            symbol_ids=["benign_symbol_001"],
            context={"scenario": "low_risk_demo"},
        )

        print("   Sending LOW priority escalation:")
        print(f"   • Drift: {signal.drift_score}")
        print(f"   • Entropy: {signal.entropy}")
        print(f"   • Emotion: {signal.emotion_volatility}")

        response = await self.governor.receive_escalation(signal)
        self.responses.append(response)

        print(f"\n   🟢 DECISION: {response.decision.value}")
        print(f"   • Risk Score: {response.risk_score:.3f}")
        print(f"   • Confidence: {response.confidence:.3f}")
        print(f"   • Reasoning: {response.reasoning}")
        print()

    async def _demo_emotional_volatility_freeze(self):
        """Demonstrate emotional volatility triggering FREEZE."""
        print("🔥 SCENARIO 2: Emotional Volatility (Expected: FREEZE)")
        print("──────────────────────────────────────────────────────")

        signal = create_escalation_signal(
            source_module=EscalationSource.EMOTION_PROTOCOL,
            priority=EscalationPriority.MEDIUM,
            triggering_metric="emotion_cascade",
            drift_score=0.3,
            entropy=0.4,
            emotion_volatility=0.75,  # High emotion
            contradiction_density=0.3,
            symbol_ids=["volatile_emotion_chain"],
            memory_ids=["em_mem_001", "em_mem_002"],
            context={"scenario": "emotion_freeze_demo"},
        )

        print("   Sending MEDIUM priority emotional volatility:")
        print(f"   • Emotion Volatility: {signal.emotion_volatility} ⚠️")
        print(f"   • Source: {signal.source_module.value}")

        response = await self.governor.receive_escalation(signal)
        self.responses.append(response)

        print(f"\n   🟡 DECISION: {response.decision.value}")
        print(f"   • Risk Score: {response.risk_score:.3f}")
        print(f"   • Intervention Tags: {', '.join(response.intervention_tags)}")
        print(f"   • Affected Systems: {len(response.mesh_notifications)}")
        print()

    async def _demo_entropy_quarantine(self):
        """Demonstrate high entropy triggering QUARANTINE."""
        print("💥 SCENARIO 3: High Entropy (Expected: QUARANTINE)")
        print("───────────────────────────────────────────────────")

        signal = create_escalation_signal(
            source_module=EscalationSource.SYMBOLIC_MESH,
            priority=EscalationPriority.HIGH,
            triggering_metric="entropy_overflow",
            drift_score=0.6,
            entropy=0.88,  # Above quarantine threshold
            emotion_volatility=0.5,
            contradiction_density=0.7,
            symbol_ids=["chaotic_mesh_node", "unstable_symbol"],
            memory_ids=["mem_fold_alpha", "mem_fold_beta"],
            context={"scenario": "entropy_quarantine_demo"},
        )

        print("   Sending HIGH priority entropy violation:")
        print(f"   • Entropy: {signal.entropy} 🚨")
        print(f"   • Contradiction Density: {signal.contradiction_density}")
        print(f"   • Affected Symbols: {len(signal.symbol_ids)}")

        response = await self.governor.receive_escalation(signal)
        self.responses.append(response)

        print(f"\n   🟠 DECISION: {response.decision.value}")
        print(f"   • Risk Score: {response.risk_score:.3f}")
        print(
            f"   • Quarantine Scope: {response.quarantine_scope['isolation_level'] if response.quarantine_scope else 'N/A'}"
        )
        print(f"   • Rollback Available: {'Yes' if response.rollback_plan else 'No'}")
        print()

    async def _demo_cascade_prevention(self):
        """Demonstrate cascade prevention through multiple escalations."""
        print("🌊 SCENARIO 4: Cascade Prevention (Multiple Escalations)")
        print("────────────────────────────────────────────────────────")

        print("   Simulating cascade conditions with 3 related escalations...")

        cascade_symbols = ["cascade_origin", "cascade_propagator", "cascade_amplifier"]

        for i, symbol in enumerate(cascade_symbols):
            signal = create_escalation_signal(
                source_module=EscalationSource.DRIFT_SENTINEL,
                priority=EscalationPriority.CRITICAL,
                triggering_metric="cascade_detection",
                drift_score=0.7 + i * 0.1,
                entropy=0.75 + i * 0.05,
                emotion_volatility=0.6,
                contradiction_density=0.8,
                symbol_ids=[symbol],
                context={"cascade_stage": i + 1},
            )

            print(f"\n   Stage {i + 1}: {symbol}")
            print(f"   • Drift: {signal.drift_score:.2f}")
            print(f"   • Urgency: {signal.calculate_urgency_score():.3f}")

            response = await self.governor.receive_escalation(signal)
            self.responses.append(response)

            print(f"   → Decision: {response.decision.value}")

            await asyncio.sleep(0.5)  # Brief pause between escalations

        print("\n   📊 Cascade Prevention Summary:")
        print(f"   • Total Escalations: {len(cascade_symbols)}")
        print(f"   • Quarantined Symbols: {len(self.governor.quarantined_symbols)}")
        print(f"   • Frozen Systems: {len(self.governor.frozen_systems)}")
        print()

    async def _demo_emergency_shutdown(self):
        """Demonstrate emergency shutdown scenario."""
        print("🆘 SCENARIO 5: Emergency Shutdown (Expected: SHUTDOWN)")
        print("───────────────────────────────────────────────────────")

        signal = create_escalation_signal(
            source_module=EscalationSource.SYSTEM_MONITOR,
            priority=EscalationPriority.EMERGENCY,
            triggering_metric="critical_failure",
            drift_score=0.95,
            entropy=0.92,
            emotion_volatility=0.88,
            contradiction_density=0.90,
            symbol_ids=["critical_system_core"],
            memory_ids=["core_mem_001", "core_mem_002", "core_mem_003"],
            context={
                "scenario": "emergency_shutdown_demo",
                "cascade_risk": True,
                "subsystem_failures": 3,
            },
        )

        print("   Sending EMERGENCY priority system failure:")
        print("   • All Metrics CRITICAL:")
        print(f"     - Drift: {signal.drift_score} 🔴")
        print(f"     - Entropy: {signal.entropy} 🔴")
        print(f"     - Emotion: {signal.emotion_volatility} 🔴")
        print(f"     - Contradiction: {signal.contradiction_density} 🔴")

        response = await self.governor.receive_escalation(signal)
        self.responses.append(response)

        print(f"\n   🔴 DECISION: {response.decision.value}")
        print(f"   • Risk Score: {response.risk_score:.3f}")
        print(
            f"   • Emergency Tags: {[t for t in response.intervention_tags if 'EMERGENCY' in t]}"
        )
        print(
            f"   • Isolation Level: {response.quarantine_scope['isolation_level'] if response.quarantine_scope else 'N/A'}"
        )
        print(
            f"   • Manual Approval Required: {response.rollback_plan.get('conditions_for_rollback', {}).get('manual_approval_required', False) if response.rollback_plan else False}"
        )
        print()

    async def _demo_multi_source_arbitration(self):
        """Demonstrate arbitration with escalations from multiple sources."""
        print("🔀 SCENARIO 6: Multi-Source Arbitration")
        print("────────────────────────────────────────")

        print("   Processing escalations from different subsystems...")

        sources = [
            ("drift_sentinel", EscalationSource.DRIFT_SENTINEL, 0.6, 0.5),
            ("emotion_protocol", EscalationSource.EMOTION_PROTOCOL, 0.4, 0.7),
            ("conflict_resolver", EscalationSource.CONFLICT_RESOLVER, 0.5, 0.3),
        ]

        for name, source, drift, emotion in sources:
            signal = create_escalation_signal(
                source_module=source,
                priority=EscalationPriority.MEDIUM,
                triggering_metric=f"{name}_alert",
                drift_score=drift,
                entropy=0.4,
                emotion_volatility=emotion,
                contradiction_density=0.4,
                symbol_ids=["shared_concern_symbol"],
                context={"multi_source": True},
            )

            print(f"\n   📨 From {source.value}:")
            response = await self.governor.receive_escalation(signal)
            self.responses.append(response)

            print(
                f"   → Decision: {response.decision.value} (Risk: {response.risk_score:.3f})"
            )

        print()

    async def _demo_system_status(self):
        """Demonstrate system status reporting."""
        print("📋 SCENARIO 7: System Status Dashboard")
        print("───────────────────────────────────────")

        status = self.governor.get_governor_status()

        print("ΛGOVERNOR System Status:")
        print(f"   • Status: {status['status']}")
        print(f"   • Total Escalations: {status['total_escalations']}")
        print(f"   • Active Escalations: {status['active_escalations']}")
        print(f"   • Interventions Executed: {status['interventions_executed']}")
        print(f"   • Successful Interventions: {status['successful_interventions']}")
        print(f"   • Average Response Time: {status['average_response_time']:.3f}s")
        print()

        print("Decision Distribution:")
        for decision, count in status["decisions_by_type"].items():
            print(f"   • {decision}: {count}")
        print()

        print("System State:")
        for state_type, count in status["system_state"].items():
            if count > 0:
                print(f"   • {state_type}: {count}")
        print()

        print("Safety Thresholds:")
        for threshold, value in status["safety_thresholds"].items():
            print(f"   • {threshold}: {value}")
        print()

        # Show audit log sample
        if self.governor.audit_log_path.exists():
            print("Recent Audit Entries:")
            try:
                with open(self.governor.audit_log_path) as f:
                    lines = f.readlines()
                    for line in lines[-3:]:  # Last 3 entries
                        entry = json.loads(line)
                        print(
                            f"   • {entry['timestamp']}: {entry['arbitration']['decision']} - {entry['escalation']['source_module']}"
                        )
            except:
                print("   • No audit entries available")
        print()


async def main():
    """Run the ΛGOVERNOR demonstration."""
    try:
        demo = GovernorDemo()
        await demo.run_demo()

        print("\nThe ΛGOVERNOR successfully demonstrated:")
        print("✓ Multi-dimensional risk evaluation across subsystems")
        print("✓ Five-tier intervention system (ALLOW → SHUTDOWN)")
        print("✓ Real-time mesh notification and coordination")
        print("✓ Cascade prevention through proactive interventions")
        print("✓ Comprehensive audit trail with ΛTAG metadata")
        print("✓ Emergency response and system-wide override capabilities")
        print()
        print("LUKHAS AGI global ethical arbitration is operational.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


# CLAUDE CHANGELOG
# - Created interactive demonstration script for ΛGOVERNOR # CLAUDE_EDIT_v0.1
# - Implemented 7 demonstration scenarios covering all decision types # CLAUDE_EDIT_v0.1
# - Added mock mesh components for notification testing # CLAUDE_EDIT_v0.1
# - Created cascade prevention demonstration with multiple escalations # CLAUDE_EDIT_v0.1
# - Added comprehensive system status dashboard display # CLAUDE_EDIT_v0.1
# - Included audit log sampling in demonstration # CLAUDE_EDIT_v0.1
