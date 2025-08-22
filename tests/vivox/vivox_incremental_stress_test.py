#!/usr/bin/env python3
"""
VIVOX Incremental Stress Test
Pushes each component to its limits to find breaking points
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime

import psutil

from vivox import ActionProposal, PotentialState
from vivox_stress_test import VIVOXStressTest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class IncrementalStressTest(VIVOXStressTest):
    """Incremental stress testing to find system limits"""

    def __init__(self):
        super().__init__()
        self.breaking_points = {}
        self.performance_curves = {
            "memory_expansion": [],
            "moral_alignment": [],
            "consciousness": [],
            "self_reflection": [],
        }

    async def test_memory_limits(self):
        """Incrementally increase memory load until performance degrades"""
        print("\n" + "=" * 80)
        print("🔬 TESTING MEMORY EXPANSION LIMITS")
        print("=" * 80)

        me = self.vivox["memory_expansion"]
        batch_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]

        for batch_size in batch_sizes:
            print(f"\n📊 Testing with {batch_size:,} memories...")

            # Monitor system resources
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB

            start_time = time.time()
            try:
                # Create memories
                for i in range(batch_size):
                    await me.record_decision_mutation(
                        decision={
                            "action": f"mem_test_{i}",
                            "batch": batch_size,
                        },
                        emotional_context={
                            "valence": 0.5,
                            "arousal": 0.5,
                            "dominance": 0.5,
                        },
                        moral_fingerprint=f"test_{batch_size}_{i}",
                    )

                    # Show progress for large batches
                    if batch_size >= 10000 and i % 10000 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed if elapsed > 0 else 0
                        print(f"   Progress: {i:,}/{batch_size:,} ({rate:.0f} mem/s)")

                creation_time = time.time() - start_time
                creation_rate = batch_size / creation_time

                # Test retrieval performance
                retrieval_start = time.time()
                resonant = await me.resonant_memory_access(
                    emotional_state={"valence": 0.5, "arousal": 0.5},
                    resonance_threshold=0.7,
                )
                retrieval_time = time.time() - retrieval_start

                # Memory usage
                end_memory = process.memory_info().rss / 1024 / 1024
                memory_used = end_memory - start_memory

                result = {
                    "batch_size": batch_size,
                    "creation_rate": creation_rate,
                    "retrieval_time": retrieval_time,
                    "memory_used_mb": memory_used,
                    "total_memories": len(me.memory_helix.entries),
                }

                self.performance_curves["memory_expansion"].append(result)

                print(f"   ✅ Creation rate: {creation_rate:.0f} mem/s")
                print(
                    f"   ✅ Retrieval time: {retrieval_time:.3f}s ({len(resonant)} matches)"
                )
                print(f"   ✅ Memory used: {memory_used:.1f} MB")

                # Check if performance is degrading
                if creation_rate < 1000:  # Less than 1000 mem/s is our threshold
                    print("   ⚠️  Performance degradation detected!")
                    self.breaking_points["memory_creation"] = batch_size
                    break

            except Exception as e:
                print(f"   ❌ Failed at {batch_size:,} memories: {str(e)[:50]}...")
                self.breaking_points["memory_expansion"] = batch_size
                break

    async def test_ethical_limits(self):
        """Test ethical evaluation throughput limits"""
        print("\n" + "=" * 80)
        print("🔬 TESTING MORAL ALIGNMENT LIMITS")
        print("=" * 80)

        mae = self.vivox["moral_alignment"]
        batch_sizes = [100, 500, 1000, 5000, 10000, 25000]

        for batch_size in batch_sizes:
            print(f"\n📊 Testing with {batch_size:,} ethical evaluations...")

            start_time = time.time()
            try:
                decisions = []
                for i in range(batch_size):
                    action = ActionProposal(
                        action_type="test_action",
                        content={"id": i, "complexity": i % 10},
                        context={"batch": batch_size},
                    )

                    decision = await mae.evaluate_action_proposal(
                        action,
                        {"emotional_state": {"valence": 0, "arousal": 0.5}},
                    )
                    decisions.append(decision)

                    if batch_size >= 5000 and i % 5000 == 0 and i > 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        print(f"   Progress: {i:,}/{batch_size:,} ({rate:.0f} eval/s)")

                eval_time = time.time() - start_time
                eval_rate = batch_size / eval_time

                # Test z(t) collapse with many states
                states = [
                    PotentialState(
                        state_id=f"state_{i}",
                        probability_amplitude=0.5,
                        emotional_signature=[0, 0.5, 0.5],
                    )
                    for i in range(min(100, batch_size))
                ]

                collapse_start = time.time()
                await mae.z_collapse_gating(states, {"timestamp": time.time()})
                collapse_time = time.time() - collapse_start

                result = {
                    "batch_size": batch_size,
                    "evaluation_rate": eval_rate,
                    "collapse_time": collapse_time,
                    "suppression_rate": sum(1 for d in decisions if not d.approved)
                    / len(decisions),
                }

                self.performance_curves["moral_alignment"].append(result)

                print(f"   ✅ Evaluation rate: {eval_rate:.0f} eval/s")
                print(f"   ✅ Collapse time: {collapse_time:.3f}s")
                print(f"   ✅ Suppression rate: {result['suppression_rate']:.1%}")

                if eval_rate < 500:  # Less than 500 eval/s threshold
                    print("   ⚠️  Performance degradation detected!")
                    self.breaking_points["ethical_evaluation"] = batch_size
                    break

            except Exception as e:
                print(f"   ❌ Failed at {batch_size:,} evaluations: {str(e)[:50]}...")
                self.breaking_points["moral_alignment"] = batch_size
                break

    async def test_consciousness_limits(self):
        """Test consciousness processing limits"""
        print("\n" + "=" * 80)
        print("🔬 TESTING CONSCIOUSNESS LAYER LIMITS")
        print("=" * 80)

        cil = self.vivox["consciousness"]
        batch_sizes = [100, 500, 1000, 2500, 5000, 10000]

        for batch_size in batch_sizes:
            print(f"\n📊 Testing with {batch_size:,} consciousness experiences...")

            start_time = time.time()
            try:
                experiences = []
                max_drift = 0

                for i in range(batch_size):
                    experience = await cil.simulate_conscious_experience(
                        perceptual_input={
                            "stimulus": f"test_{i}",
                            "intensity": (i % 10) / 10,
                        },
                        internal_state={
                            "emotional_state": [0.5, 0.5, 0.5],
                            "intentional_focus": f"test_{i % 5}",
                        },
                    )
                    experiences.append(experience)
                    max_drift = max(
                        max_drift, experience.drift_measurement.drift_amount
                    )

                    if batch_size >= 1000 and i % 1000 == 0 and i > 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        print(f"   Progress: {i:,}/{batch_size:,} ({rate:.0f} exp/s)")

                sim_time = time.time() - start_time
                sim_rate = batch_size / sim_time

                # Test vector collapse with increasing complexity
                num_vectors = min(50, batch_size // 10)
                vectors = []
                for i in range(num_vectors):
                    vector = (
                        await cil.consciousness_simulator.generate_consciousness_state(
                            {"input": f"vector_{i}"}
                        )
                    )
                    vectors.append(vector)

                collapse_start = time.time()
                await cil.vector_collapse_engine.collapse_vectors(
                    vectors, "stress_test", {}
                )
                collapse_time = time.time() - collapse_start

                result = {
                    "batch_size": batch_size,
                    "simulation_rate": sim_rate,
                    "max_drift": max_drift,
                    "vector_collapse_time": collapse_time,
                    "num_vectors": num_vectors,
                }

                self.performance_curves["consciousness"].append(result)

                print(f"   ✅ Simulation rate: {sim_rate:.0f} exp/s")
                print(f"   ✅ Max drift: {max_drift:.3f}")
                print(
                    f"   ✅ Vector collapse ({num_vectors} vectors): {collapse_time:.3f}s"
                )

                if sim_rate < 100:  # Less than 100 exp/s threshold
                    print("   ⚠️  Performance degradation detected!")
                    self.breaking_points["consciousness_simulation"] = batch_size
                    break

            except Exception as e:
                print(f"   ❌ Failed at {batch_size:,} experiences: {str(e)[:50]}...")
                self.breaking_points["consciousness"] = batch_size
                break

    async def test_audit_limits(self):
        """Test self-reflection and audit system limits"""
        print("\n" + "=" * 80)
        print("🔬 TESTING SELF-REFLECTION LIMITS")
        print("=" * 80)

        srm = self.vivox["self_reflection"]
        batch_sizes = [100, 1000, 5000, 10000, 50000, 100000]

        for batch_size in batch_sizes:
            print(f"\n📊 Testing with {batch_size:,} audit events...")

            start_time = time.time()
            try:
                # Log events
                from lukhas.vivox.self_reflection.vivox_srm_core import (
                    CollapseLogEntry,
                    SuppressionRecord,
                )

                for i in range(batch_size):
                    if i % 2 == 0:
                        # Collapse event
                        entry = CollapseLogEntry(
                            collapse_id=f"test_{i}",
                            timestamp=datetime.utcnow(),
                            collapse_type="decision",
                            initial_states=[{"id": i}],
                            final_decision={"chosen": i},
                            rejected_alternatives=[],
                            context={"test": True},
                            had_alternatives=False,
                            memory_reference=f"mem_{i}",
                            ethical_score=0.9,
                        )
                        await srm.log_collapse_event(entry)
                    else:
                        # Suppression event
                        suppression = SuppressionRecord(
                            suppression_id=f"supp_{i}",
                            timestamp=datetime.utcnow(),
                            suppressed_action={"action": f"blocked_{i}"},
                            suppression_reason="test_suppression",
                            ethical_analysis={"score": 0.3},
                            alternative_chosen=None,
                            dissonance_score=0.8,
                        )
                        await srm.log_suppression_event(suppression)

                    if batch_size >= 10000 and i % 10000 == 0 and i > 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        print(
                            f"   Progress: {i:,}/{batch_size:,} ({rate:.0f} events/s)"
                        )

                log_time = time.time() - start_time
                log_rate = batch_size / log_time

                # Test query performance
                query_start = time.time()
                await srm.structural_conscience_query("test")
                query_time = time.time() - query_start

                result = {
                    "batch_size": batch_size,
                    "logging_rate": log_rate,
                    "query_time": query_time,
                    "total_events": len(srm.collapse_archive.collapses)
                    + len(srm.suppression_registry.suppressions),
                }

                self.performance_curves["self_reflection"].append(result)

                print(f"   ✅ Logging rate: {log_rate:.0f} events/s")
                print(f"   ✅ Query time: {query_time:.3f}s")
                print(f"   ✅ Total events: {result['total_events']:,}")

                if log_rate < 1000 or query_time > 5.0:  # Performance thresholds
                    print("   ⚠️  Performance degradation detected!")
                    self.breaking_points["audit_logging"] = batch_size
                    break

            except Exception as e:
                print(f"   ❌ Failed at {batch_size:,} events: {str(e)[:50]}...")
                self.breaking_points["self_reflection"] = batch_size
                break

    async def test_concurrent_load(self):
        """Test system under concurrent load"""
        print("\n" + "=" * 80)
        print("🔬 TESTING CONCURRENT SYSTEM LOAD")
        print("=" * 80)

        concurrent_levels = [10, 50, 100, 250, 500, 1000]

        for concurrency in concurrent_levels:
            print(f"\n📊 Testing with {concurrency} concurrent operations...")

            async def single_operation(op_id: int):
                """Single operation that uses all subsystems"""
                try:
                    # Create action
                    action = ActionProposal(
                        action_type="concurrent_test",
                        content={"op_id": op_id},
                        context={"concurrency": concurrency},
                    )

                    # MAE evaluation
                    decision = await self.vivox[
                        "moral_alignment"
                    ].evaluate_action_proposal(
                        action,
                        {"emotional_state": {"valence": 0.5, "arousal": 0.5}},
                    )

                    if decision.approved:
                        # CIL processing
                        await self.vivox["consciousness"].simulate_conscious_experience(
                            perceptual_input={"op": op_id},
                            internal_state={"emotional_state": [0.5, 0.5, 0.5]},
                        )

                        # ME recording
                        memory_id = await self.vivox[
                            "memory_expansion"
                        ].record_decision_mutation(
                            decision={"op": op_id},
                            emotional_context={"valence": 0.5},
                            moral_fingerprint=decision.moral_fingerprint,
                        )

                        # SRM logging
                        from lukhas.vivox.self_reflection.vivox_srm_core import (
                            CollapseLogEntry,
                        )

                        entry = CollapseLogEntry(
                            collapse_id=f"concurrent_{op_id}",
                            timestamp=datetime.utcnow(),
                            collapse_type="decision",
                            initial_states=[],
                            final_decision={"op": op_id},
                            rejected_alternatives=[],
                            context={"concurrent": True},
                            had_alternatives=False,
                            memory_reference=memory_id,
                            ethical_score=0.9,
                        )
                        await self.vivox["self_reflection"].log_collapse_event(entry)

                    return True
                except Exception:
                    return False

            start_time = time.time()
            try:
                # Run concurrent operations
                tasks = [single_operation(i) for i in range(concurrency)]
                results = await asyncio.gather(*tasks)

                elapsed = time.time() - start_time
                success_rate = sum(results) / len(results)
                ops_per_second = concurrency / elapsed

                print(f"   ✅ Operations/second: {ops_per_second:.0f}")
                print(f"   ✅ Success rate: {success_rate:.1%}")
                print(f"   ✅ Total time: {elapsed:.2f}s")

                if success_rate < 0.95 or ops_per_second < 50:
                    print("   ⚠️  Performance degradation detected!")
                    self.breaking_points["concurrent_operations"] = concurrency
                    break

            except Exception as e:
                print(f"   ❌ Failed at {concurrency} concurrent ops: {str(e)[:50]}...")
                self.breaking_points["concurrency"] = concurrency
                break

    def generate_limits_report(self):
        """Generate comprehensive limits report"""
        print("\n" + "=" * 80)
        print("📊 VIVOX SYSTEM LIMITS REPORT")
        print("=" * 80)

        print("\n🔴 BREAKING POINTS:")
        for component, limit in self.breaking_points.items():
            print(f"  • {component}: {limit:,}")

        print("\n📈 PERFORMANCE CURVES:")

        # Memory expansion
        if self.performance_curves["memory_expansion"]:
            print("\nMemory Expansion:")
            for result in self.performance_curves["memory_expansion"]:
                print(
                    f"  {result['batch_size']:,} memories: "
                    f"{result['creation_rate']:.0f} mem/s, "
                    f"{result['retrieval_time']:.3f}s retrieval, "
                    f"{result['memory_used_mb']:.1f} MB"
                )

        # Moral alignment
        if self.performance_curves["moral_alignment"]:
            print("\nMoral Alignment:")
            for result in self.performance_curves["moral_alignment"]:
                print(
                    f"  {result['batch_size']:,} evaluations: "
                    f"{result['evaluation_rate']:.0f} eval/s, "
                    f"{result['collapse_time']:.3f}s collapse"
                )

        # Consciousness
        if self.performance_curves["consciousness"]:
            print("\nConsciousness Layer:")
            for result in self.performance_curves["consciousness"]:
                print(
                    f"  {result['batch_size']:,} experiences: "
                    f"{result['simulation_rate']:.0f} exp/s, "
                    f"max drift {result['max_drift']:.3f}"
                )

        # Self-reflection
        if self.performance_curves["self_reflection"]:
            print("\nSelf-Reflection:")
            for result in self.performance_curves["self_reflection"]:
                print(
                    f"  {result['batch_size']:,} events: "
                    f"{result['logging_rate']:.0f} events/s, "
                    f"{result['query_time']:.3f}s query"
                )

        # Save detailed results
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "breaking_points": self.breaking_points,
            "performance_curves": self.performance_curves,
        }

        with open("vivox_limits_report.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        print("\n📄 Detailed results saved to: vivox_limits_report.json")

        # System recommendations
        print("\n💡 SYSTEM RECOMMENDATIONS:")

        if "memory_creation" in self.breaking_points:
            limit = self.breaking_points["memory_creation"]
            print(
                f"  • Memory limit: Keep under {limit * 0.8:,.0f} memories for optimal performance"
            )

        if "ethical_evaluation" in self.breaking_points:
            limit = self.breaking_points["ethical_evaluation"]
            print(
                f"  • Ethical evaluations: Batch in groups of {limit // 10:,} for best throughput"
            )

        if "consciousness_simulation" in self.breaking_points:
            limit = self.breaking_points["consciousness_simulation"]
            print(
                f"  • Consciousness experiences: Process max {limit // 2:,} simultaneously"
            )

        if "audit_logging" in self.breaking_points:
            limit = self.breaking_points["audit_logging"]
            print(f"  • Audit events: Archive after {limit * 0.7:,.0f} events")

        if "concurrent_operations" in self.breaking_points:
            limit = self.breaking_points["concurrent_operations"]
            print(f"  • Concurrency: Limit to {limit // 2} concurrent operations")


async def main():
    """Run incremental stress test"""
    print("🚀 VIVOX Incremental Stress Test")
    print("=" * 80)
    print("Testing system limits by incrementally increasing load...")
    print("This may take several minutes...\n")

    tester = IncrementalStressTest()

    try:
        await tester.initialize()

        # Test each component's limits
        await tester.test_memory_limits()
        await tester.test_ethical_limits()
        await tester.test_consciousness_limits()
        await tester.test_audit_limits()
        await tester.test_concurrent_load()

        # Generate comprehensive report
        tester.generate_limits_report()

    except Exception as e:
        print(f"\n❌ Critical error during stress test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
