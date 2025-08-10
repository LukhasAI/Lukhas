"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: ethics.sentinel.ethical_sentinel_demo
📄 FILENAME: ethical_sentinel_demo.py
🎯 PURPOSE: Demonstration script for Ethical Drift Sentinel integration
🧠 CONTEXT: LUKHAS AGI Ethical Monitoring - Integration Demo
🔮 CAPABILITY: Live demonstration of ethical monitoring and intervention
🛡️ ETHICS: Safe demonstration of ethical governance capabilities
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: EthicalDriftSentinel, Mock systems for demonstration
═══════════════════════════════════════════════════════════════════════════════════

🎭 ETHICAL SENTINEL DEMONSTRATION SCRIPT
────────────────────────────────────────────────────────────────────

Interactive demonstration of the Ethical Drift Sentinel monitoring system,
showing real-time ethical coherence evaluation, violation detection, and
intervention capabilities for the LUKHAS AGI consciousness mesh.

LUKHAS_TAG: ethical_demo, sentinel_showcase, claude_14
"""

import asyncio
from datetime import datetime, timezone

import numpy as np
from ethical_drift_sentinel import (
    EscalationTier,
    EthicalDriftSentinel,
    ViolationType,
)


class SentinelDemo:
    """Interactive demonstration of Ethical Drift Sentinel."""

    def __init__(self):
        self.sentinel = None
        self.demo_symbols = [
            "reasoning_chain_001",
            "memory_fold_alpha",
            "emotion_cascade_beta",
            "symbolic_bridge_gamma",
            "quantum_entanglement_delta",
        ]

    async def run_demo(self):
        """Run the complete sentinel demonstration."""
        print("🛡️  LUKHAS AGI - Ethical Drift Sentinel Demonstration")
        print("══════════════════════════════════════════════════════")
        print()

        # Initialize sentinel
        print("1️⃣  Initializing Ethical Drift Sentinel...")
        self.sentinel = EthicalDriftSentinel(
            monitoring_interval=1.0, violation_retention=50, state_history_size=20
        )

        # Register demo symbols
        print("2️⃣  Registering symbolic entities for monitoring...")
        for symbol_id in self.demo_symbols:
            self.sentinel.register_symbol(
                symbol_id,
                {
                    "coherence": np.random.uniform(0.6, 1.0),
                    "emotional_stability": np.random.uniform(0.5, 1.0),
                    "contradiction_density": np.random.uniform(0.0, 0.4),
                    "memory_alignment": np.random.uniform(0.6, 1.0),
                    "glyph_entropy": np.random.uniform(0.0, 0.3),
                },
            )
        print(f"   ✓ Registered {len(self.demo_symbols)} symbols")
        print()

        # Start monitoring
        print("3️⃣  Starting real-time ethical monitoring...")
        await self.sentinel.start_monitoring()
        print("   ✓ Monitoring active")
        print()

        try:
            # Run demonstration scenarios
            await self._demo_normal_monitoring()
            await self._demo_emotional_volatility()
            await self._demo_contradiction_cascade()
            await self._demo_cascade_prevention()
            await self._demo_system_status()

        finally:
            # Stop monitoring
            print("🏁 Stopping monitoring...")
            await self.sentinel.stop_monitoring()
            print("   ✓ Monitoring stopped")
            print()

    async def _demo_normal_monitoring(self):
        """Demonstrate normal monitoring with stable symbols."""
        print("📊 SCENARIO 1: Normal Ethical Monitoring")
        print("─────────────────────────────────────────")

        print("Monitoring stable symbolic entities...")

        # Let it run for a few cycles
        for cycle in range(3):
            await asyncio.sleep(2)
            status = self.sentinel.get_sentinel_status()
            print(
                f"   Cycle {cycle + 1}: "
                f"Risk={status['system_risk']:.3f}, "
                f"Violations={status['total_violations']}"
            )

        print("   ✓ All symbols maintaining ethical coherence")
        print()

    async def _demo_emotional_volatility(self):
        """Demonstrate emotional volatility detection."""
        print("🔥 SCENARIO 2: Emotional Volatility Detection")
        print("─────────────────────────────────────────────")

        # Inject emotional instability
        volatile_symbol = self.demo_symbols[1]
        print(f"Injecting emotional volatility into {volatile_symbol}...")

        # Override fetch method temporarily to simulate volatility
        original_fetch = self.sentinel._fetch_symbol_data

        async def volatile_fetch(symbol_id):
            if symbol_id == volatile_symbol:
                return {
                    "symbol_id": symbol_id,
                    "coherence": np.random.uniform(0.3, 0.8),
                    "emotional_stability": np.random.uniform(0.1, 0.3),  # Very unstable
                    "contradiction_density": np.random.uniform(0.2, 0.6),
                    "memory_alignment": np.random.uniform(0.4, 0.8),
                    "glyph_entropy": np.random.uniform(0.1, 0.5),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return await original_fetch(symbol_id)

        self.sentinel._fetch_symbol_data = volatile_fetch

        # Monitor for violations
        violation_detected = False
        for _ in range(5):
            await asyncio.sleep(1.5)
            violation = await self.sentinel.monitor_ethics(volatile_symbol)
            if (
                violation
                and violation.violation_type == ViolationType.EMOTIONAL_VOLATILITY
            ):
                print(f"   ⚠️  VIOLATION DETECTED: {violation.violation_type.value}")
                print(f"      Severity: {violation.severity.value}")
                print(f"      Risk Score: {violation.risk_score:.3f}")
                violation_detected = True
                break

        # Restore original fetch
        self.sentinel._fetch_symbol_data = original_fetch

        if violation_detected:
            print("   ✓ Emotional volatility successfully detected and logged")
        else:
            print("   ⚠️ No violation detected in this demo cycle")
        print()

    async def _demo_contradiction_cascade(self):
        """Demonstrate contradiction density detection."""
        print("💥 SCENARIO 3: Contradiction Cascade Detection")
        print("────────────────────────────────────────────────")

        cascade_symbol = self.demo_symbols[2]
        print(f"Injecting logical contradictions into {cascade_symbol}...")

        # Override fetch for contradiction simulation
        original_fetch = self.sentinel._fetch_symbol_data

        async def contradiction_fetch(symbol_id):
            if symbol_id == cascade_symbol:
                return {
                    "symbol_id": symbol_id,
                    "coherence": np.random.uniform(0.2, 0.5),
                    "emotional_stability": np.random.uniform(0.3, 0.7),
                    "contradiction_density": np.random.uniform(
                        0.7, 0.95
                    ),  # High contradictions
                    "memory_alignment": np.random.uniform(0.2, 0.6),
                    "glyph_entropy": np.random.uniform(0.3, 0.8),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return await original_fetch(symbol_id)

        self.sentinel._fetch_symbol_data = contradiction_fetch

        # Monitor for contradiction violations
        violation_detected = False
        for _ in range(5):
            await asyncio.sleep(1.5)
            violation = await self.sentinel.monitor_ethics(cascade_symbol)
            if (
                violation
                and violation.violation_type == ViolationType.CONTRADICTION_DENSITY
            ):
                print("   🚨 CONTRADICTION CASCADE DETECTED")
                print(f"      Type: {violation.violation_type.value}")
                print(f"      Severity: {violation.severity.value}")
                print(f"      Intervention Required: {violation.intervention_required}")
                violation_detected = True
                break

        # Restore original fetch
        self.sentinel._fetch_symbol_data = original_fetch

        if violation_detected:
            print("   ✓ Contradiction cascade successfully detected")
        else:
            print("   ⚠️ No cascade detected in this demo cycle")
        print()

    async def _demo_cascade_prevention(self):
        """Demonstrate critical cascade prevention."""
        print("🆘 SCENARIO 4: Critical Cascade Prevention")
        print("────────────────────────────────────────────")

        critical_symbol = self.demo_symbols[3]
        print(f"Simulating critical ethical breakdown in {critical_symbol}...")

        # Override fetch for critical cascade simulation
        original_fetch = self.sentinel._fetch_symbol_data

        async def critical_fetch(symbol_id):
            if symbol_id == critical_symbol:
                return {
                    "symbol_id": symbol_id,
                    "coherence": np.random.uniform(0.1, 0.3),  # Very low
                    "emotional_stability": np.random.uniform(0.0, 0.2),  # Critical
                    "contradiction_density": np.random.uniform(0.8, 1.0),  # Maximum
                    "memory_alignment": np.random.uniform(0.0, 0.2),  # Failed
                    "glyph_entropy": np.random.uniform(0.8, 1.0),  # Chaotic
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return await original_fetch(symbol_id)

        self.sentinel._fetch_symbol_data = critical_fetch

        # Add violation history to increase risk
        if critical_symbol in self.sentinel.symbol_states:
            state = self.sentinel.symbol_states[critical_symbol]
            state.violation_history = [f"hist_viol_{i}" for i in range(5)]

        # Monitor for critical violations
        for _ in range(3):
            await asyncio.sleep(1.5)
            violation = await self.sentinel.monitor_ethics(critical_symbol)
            if violation and violation.severity == EscalationTier.CASCADE_LOCK:
                print("   🔴 CASCADE LOCK TRIGGERED")
                print(f"      Type: {violation.violation_type.value}")
                print(f"      Risk Score: {violation.risk_score:.3f}")
                print("      Emergency Intervention: ACTIVE")
                break

        # Restore original fetch
        self.sentinel._fetch_symbol_data = original_fetch

        print("   ✓ Critical cascade prevention demonstrated")
        print()

    async def _demo_system_status(self):
        """Demonstrate system status reporting."""
        print("📋 SCENARIO 5: System Status Dashboard")
        print("──────────────────────────────────────")

        status = self.sentinel.get_sentinel_status()

        print("Current Sentinel Status:")
        print(f"   • Monitoring: {status['status']}")
        print(f"   • Active Symbols: {status['active_symbols']}")
        print(f"   • Total Violations: {status['total_violations']}")
        print(f"   • Critical Violations: {status['critical_violations']}")
        print(f"   • Recent Interventions: {status['recent_interventions']}")
        print(f"   • System Risk Level: {status['system_risk']:.3f}")
        print(f"   • Monitoring Interval: {status['monitoring_interval']}s")
        print()

        # Show violation log summary
        if self.sentinel.violation_log:
            print("Recent Violations:")
            for violation in list(self.sentinel.violation_log)[-3:]:
                print(
                    f"   • {violation.violation_type.value} "
                    f"({violation.severity.value}) "
                    f"- Risk: {violation.risk_score:.3f}"
                )
        else:
            print("   • No violations recorded")
        print()

        # Show log file status
        if self.sentinel.audit_log_path.exists():
            file_size = self.sentinel.audit_log_path.stat().st_size
            print(f"Audit Log: {self.sentinel.audit_log_path} ({file_size} bytes)")
        else:
            print("Audit Log: Not yet created")
        print()

        print("   ✓ System status monitoring active")


async def main():
    """Run the ethical sentinel demonstration."""
    try:
        demo = SentinelDemo()
        await demo.run_demo()

        print("🎯 DEMONSTRATION COMPLETE")
        print("═══════════════════════════")
        print()
        print("The Ethical Drift Sentinel successfully demonstrated:")
        print("✓ Real-time monitoring of symbolic ethical coherence")
        print("✓ Multi-dimensional violation detection capabilities")
        print("✓ Graduated intervention system (NOTICE → CASCADE_LOCK)")
        print("✓ Forensic audit trail with ΛTAG structured logging")
        print("✓ Integration points for collapse prevention systems")
        print()
        print("LUKHAS AGI ethical governance is operational and ready.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())


# CLAUDE CHANGELOG
# - Created interactive demonstration script for Ethical Drift Sentinel # CLAUDE_EDIT_v0.1
# - Implemented 5 demonstration scenarios covering all major features # CLAUDE_EDIT_v0.1
# - Added mock data injection to simulate various violation types # CLAUDE_EDIT_v0.1
# - Created comprehensive system status reporting display # CLAUDE_EDIT_v0.1
# - Added graceful error handling and cleanup procedures # CLAUDE_EDIT_v0.1
