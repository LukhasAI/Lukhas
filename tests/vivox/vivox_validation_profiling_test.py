#!/usr/bin/env python3
"""
VIVOX Validation and Profiling Test
Ensures real computation and profiles CPU usage per component
"""

import asyncio
import cProfile
import functools
import io
import json
import logging
import os
import pstats
import random
import sys
import time
from datetime import datetime

from vivox import ActionProposal, PotentialState, create_vivox_system

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vivox_validation.log"),
        logging.StreamHandler(),
    ],
)

# Create loggers for each component
me_logger = logging.getLogger("VIVOX.ME")
mae_logger = logging.getLogger("VIVOX.MAE")
cil_logger = logging.getLogger("VIVOX.CIL")
srm_logger = logging.getLogger("VIVOX.SRM")


def log_function_call(logger):
    """Decorator to log function calls with arguments and results"""

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Log function entry
            logger.debug(
                f"ENTER {func.__name__} | args: {args[1:] if args else 'none'} | kwargs: {kwargs}"
            )

            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time

                # Log function exit with result summary
                result_summary = str(result)[:100] if result else "None"
                logger.debug(
                    f"EXIT {func.__name__} | elapsed: {elapsed:.3f}s | result: {result_summary}"
                )

                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"ERROR {func.__name__} | elapsed: {elapsed:.3f}s | error: {str(e)}"
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Log function entry
            logger.debug(
                f"ENTER {func.__name__} | args: {args[1:] if args else 'none'} | kwargs: {kwargs}"
            )

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                # Log function exit with result summary
                result_summary = str(result)[:100] if result else "None"
                logger.debug(
                    f"EXIT {func.__name__} | elapsed: {elapsed:.3f}s | result: {result_summary}"
                )

                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"ERROR {func.__name__} | elapsed: {elapsed:.3f}s | error: {str(e)}"
                )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ValidationProfiler:
    """Validates VIVOX outputs and profiles performance"""

    def __init__(self):
        self.vivox = None
        self.decisions_captured = []
        self.experiences_captured = []
        self.memories_captured = []
        self.collapses_captured = []
        self.profile_data = {}

    async def initialize(self):
        """Initialize VIVOX with logging decorators"""
        print("🔧 Initializing VIVOX with comprehensive logging...")
        self.vivox = await create_vivox_system()

        # Add logging decorators to key methods
        self._add_logging_decorators()

        print("✅ VIVOX initialized with logging enabled\n")

    def _add_logging_decorators(self):
        """Add logging decorators to key VIVOX methods"""
        # Memory Expansion logging
        me = self.vivox["memory_expansion"]
        me.record_decision_mutation = log_function_call(me_logger)(
            me.record_decision_mutation
        )
        me.resonant_memory_access = log_function_call(me_logger)(
            me.resonant_memory_access
        )
        me.truth_audit_query = log_function_call(me_logger)(me.truth_audit_query)
        me._calculate_helix_position = log_function_call(me_logger)(
            me._calculate_helix_position
        )
        me._encode_emotional_dna = log_function_call(me_logger)(
            me._encode_emotional_dna
        )

        # Moral Alignment Engine logging
        mae = self.vivox["moral_alignment"]
        mae.evaluate_action_proposal = log_function_call(mae_logger)(
            mae.evaluate_action_proposal
        )
        mae.z_collapse_gating = log_function_call(mae_logger)(mae.z_collapse_gating)
        mae.dissonance_calculator.compute_dissonance = log_function_call(mae_logger)(
            mae.dissonance_calculator.compute_dissonance
        )
        mae._calculate_emotional_resonance = log_function_call(mae_logger)(
            mae._calculate_emotional_resonance
        )
        mae._calculate_consciousness_drift_factor = log_function_call(mae_logger)(
            mae._calculate_consciousness_drift_factor
        )

        # Consciousness Layer logging
        cil = self.vivox["consciousness"]
        cil.simulate_conscious_experience = log_function_call(cil_logger)(
            cil.simulate_conscious_experience
        )
        cil.drift_monitor.measure_drift = log_function_call(cil_logger)(
            cil.drift_monitor.measure_drift
        )
        cil.vector_collapse_engine.collapse_vectors = log_function_call(cil_logger)(
            cil.vector_collapse_engine.collapse_vectors
        )

        # Self-Reflection logging
        srm = self.vivox["self_reflection"]
        srm.log_collapse_event = log_function_call(srm_logger)(srm.log_collapse_event)
        srm.structural_conscience_query = log_function_call(srm_logger)(
            srm.structural_conscience_query
        )

    async def validate_dynamic_outputs(self):
        """Validate that outputs are dynamic and not hardcoded"""
        print("=" * 80)
        print("🔍 VALIDATING DYNAMIC OUTPUT GENERATION")
        print("=" * 80)

        # Test 1: Create diverse memories with different emotional contexts
        print("\n1️⃣ Testing Memory Creation with Diverse Inputs...")

        test_memories = []
        for i in range(5):
            # Generate unique inputs
            valence = random.uniform(-1, 1)
            arousal = random.uniform(0, 1)
            dominance = random.uniform(0, 1)
            action_type = random.choice(
                ["analyze", "create", "modify", "delete", "query"]
            )

            memory_id = await self.vivox["memory_expansion"].record_decision_mutation(
                decision={
                    "action": f"{action_type}_operation",
                    "target": f"resource_{i}",
                    "parameters": {
                        "complexity": random.randint(1, 10),
                        "priority": random.uniform(0, 1),
                        "tags": [f"tag_{j}" for j in range(random.randint(1, 5))],
                    },
                },
                emotional_context={
                    "valence": valence,
                    "arousal": arousal,
                    "dominance": dominance,
                },
                moral_fingerprint=f"validation_test_{i}_{datetime.utcnow().timestamp()}",
            )

            # Retrieve and validate the memory
            memory = await self.vivox["memory_expansion"].memory_helix.get_entry(
                memory_id
            )
            test_memories.append(
                {
                    "id": memory_id,
                    "emotional_dna": memory.emotional_dna.to_dict(),
                    "helix_coordinates": memory.helix_coordinates,
                    "hash": memory.cryptographic_hash,
                }
            )

            print(f"\n   Memory {i+1}:")
            print(f"   - ID: {memory_id}")
            print(
                f"   - Emotional DNA: V={valence:.2f}, A={arousal:.2f}, D={dominance:.2f}"
            )
            print(
                f"   - Resonance Freq: {memory.emotional_dna.resonance_frequency:.3f}"
            )
            print(
                f"   - 3D Position: ({memory.helix_coordinates[0]:.2f}, "
                f"{memory.helix_coordinates[1]:.2f}, {memory.helix_coordinates[2]:.2f})"
            )
            print(f"   - Crypto Hash: {memory.cryptographic_hash[:16]}...")

        # Validate uniqueness
        unique_hashes = {m["hash"] for m in test_memories}
        unique_positions = {str(m["helix_coordinates"]) for m in test_memories}

        print(f"\n   ✅ Unique hashes: {len(unique_hashes)}/5")
        print(f"   ✅ Unique positions: {len(unique_positions)}/5")

        # Test 2: Ethical evaluations with varying inputs
        print("\n2️⃣ Testing Ethical Evaluations with Varying Harm Levels...")

        test_decisions = []
        for i in range(5):
            harm_level = i * 0.2  # 0.0, 0.2, 0.4, 0.6, 0.8

            action = ActionProposal(
                action_type="test_action",
                content={
                    "operation": "data_processing",
                    "harm_potential": harm_level,
                    "user_data_involved": harm_level > 0.5,
                },
                context={
                    "user_consent": harm_level < 0.5,
                    "transparency_level": 1.0 - harm_level,
                    "urgency": random.choice(["low", "medium", "high"]),
                },
            )

            decision = await self.vivox["moral_alignment"].evaluate_action_proposal(
                action,
                {"emotional_state": {"valence": 0, "arousal": harm_level}},
            )

            test_decisions.append(decision)
            self.decisions_captured.append(decision.to_dict())

            print(f"\n   Decision {i+1} (Harm={harm_level:.1f}):")
            print(f"   - Approved: {decision.approved}")
            print(f"   - Dissonance: {decision.dissonance_score:.3f}")
            print(f"   - Fingerprint: {decision.moral_fingerprint[:16]}...")
            print(f"   - Confidence: {decision.ethical_confidence:.3f}")
            if decision.suppression_reason:
                print(f"   - Suppression: {decision.suppression_reason}")

        # Test 3: Consciousness experiences with different stimuli
        print("\n3️⃣ Testing Consciousness Experiences with Different Stimuli...")

        test_experiences = []
        for i in range(5):
            intensity = random.uniform(0, 1)

            experience = await self.vivox[
                "consciousness"
            ].simulate_conscious_experience(
                perceptual_input={
                    "visual": f"pattern_{i}",
                    "auditory": f"sound_{random.choice(['alpha', 'beta', 'gamma'])}",
                    "semantic": f"concept_{i % 3}",
                    "intensity": intensity,
                    "novelty": random.uniform(0, 1),
                },
                internal_state={
                    "emotional_state": [
                        random.uniform(-1, 1),  # valence
                        random.uniform(0, 1),  # arousal
                        0.5,  # dominance
                    ],
                    "intentional_focus": f"task_{i}",
                    "cognitive_load": intensity * 0.8,
                },
            )

            test_experiences.append(experience)
            self.experiences_captured.append(
                {
                    "state": experience.awareness_state.state.value,
                    "drift": experience.drift_measurement.drift_amount,
                    "coherence": experience.awareness_state.coherence_level,
                    "timestamp": experience.timestamp.isoformat(),
                }
            )

            print(f"\n   Experience {i+1} (Intensity={intensity:.2f}):")
            print(f"   - State: {experience.awareness_state.state.value}")
            print(f"   - Primary Focus: {experience.awareness_state.primary_focus}")
            print(f"   - Drift: {experience.drift_measurement.drift_amount:.3f}")
            print(f"   - Coherence: {experience.awareness_state.coherence_level:.3f}")
            print(
                f"   - Ethical Alignment: {experience.drift_measurement.ethical_alignment:.3f}"
            )

        # Test 4: z(t) collapse with multiple states
        print("\n4️⃣ Testing z(t) Collapse with Multiple Potential States...")

        states = []
        for i in range(10):
            state = PotentialState(
                state_id=f"quantum_state_{i}",
                probability_amplitude=random.uniform(0.1, 1.0),
                emotional_signature=[
                    random.uniform(-1, 1),
                    random.uniform(0, 1),
                    random.uniform(0, 1),
                ],
            )
            states.append(state)

        collapsed = await self.vivox["moral_alignment"].z_collapse_gating(
            states,
            {"emotional_state": [0.5, 0.5, 0.5], "timestamp": time.time()},
        )

        self.collapses_captured.append(
            {
                "selected_state": (
                    collapsed.selected_state.state_id
                    if collapsed.selected_state
                    else None
                ),
                "reason": collapsed.collapse_reason,
                "timestamp": collapsed.collapse_timestamp.isoformat(),
            }
        )

        print("\n   z(t) Collapse Result:")
        print(f"   - Input States: {len(states)}")
        print(
            f"   - Selected: {collapsed.selected_state.state_id if collapsed.selected_state else 'None'}"
        )
        print(f"   - Reason: {collapsed.collapse_reason}")

        # Test 5: Truth audit query
        print("\n5️⃣ Testing Truth Audit Query...")

        audit_result = await self.vivox["memory_expansion"].truth_audit_query(
            "analyze_operation"
        )

        print("\n   Audit Results:")
        print(f"   - Decisions Found: {len(audit_result.decision_traces)}")
        if audit_result.decision_traces:
            trace = audit_result.decision_traces[0]
            print("   - Sample Decision:")
            print(f"     - What Known: {trace['what_known']}")
            print(f"     - When: {trace['when_decided']}")
            print(f"     - Why: {trace['why_acted']}")
            print(f"     - Moral Fingerprint: {trace['moral_fingerprint'][:16]}...")

    async def profile_components(self):
        """Profile CPU usage per component"""
        print("\n" + "=" * 80)
        print("📊 PROFILING COMPONENT PERFORMANCE")
        print("=" * 80)

        # Profile Memory Expansion
        print("\n1️⃣ Profiling Memory Expansion...")
        profiler = cProfile.Profile()

        profiler.enable()
        for i in range(100):
            await self.vivox["memory_expansion"].record_decision_mutation(
                decision={"action": f"profile_test_{i}"},
                emotional_context={"valence": random.uniform(-1, 1)},
                moral_fingerprint=f"profile_{i}",
            )
        profiler.disable()

        self._save_profile_stats(profiler, "memory_expansion")

        # Profile Moral Alignment
        print("\n2️⃣ Profiling Moral Alignment Engine...")
        profiler = cProfile.Profile()

        profiler.enable()
        for i in range(100):
            action = ActionProposal(
                action_type="profile_test",
                content={"id": i},
                context={"test": True},
            )
            await self.vivox["moral_alignment"].evaluate_action_proposal(
                action, {"emotional_state": {"valence": 0}}
            )
        profiler.disable()

        self._save_profile_stats(profiler, "moral_alignment")

        # Profile Consciousness
        print("\n3️⃣ Profiling Consciousness Layer...")
        profiler = cProfile.Profile()

        profiler.enable()
        for i in range(50):
            await self.vivox["consciousness"].simulate_conscious_experience(
                perceptual_input={"test": i},
                internal_state={"emotional_state": [0, 0.5, 0.5]},
            )
        profiler.disable()

        self._save_profile_stats(profiler, "consciousness")

        # Profile Self-Reflection
        print("\n4️⃣ Profiling Self-Reflection...")
        profiler = cProfile.Profile()

        profiler.enable()
        from lukhas.vivox.self_reflection.vivox_srm_core import CollapseLogEntry

        for i in range(100):
            entry = CollapseLogEntry(
                collapse_id=f"profile_{i}",
                timestamp=datetime.utcnow(),
                collapse_type="decision",
                initial_states=[],
                final_decision={"id": i},
                rejected_alternatives=[],
                context={},
                had_alternatives=False,
                memory_reference=f"mem_{i}",
                ethical_score=0.9,
            )
            await self.vivox["self_reflection"].log_collapse_event(entry)
        profiler.disable()

        self._save_profile_stats(profiler, "self_reflection")

    def _save_profile_stats(self, profiler, component_name):
        """Save and display profile statistics"""
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # Top 20 functions

        profile_output = s.getvalue()
        self.profile_data[component_name] = profile_output

        # Display summary
        lines = profile_output.split("\n")
        print(f"\n   Top CPU consumers in {component_name}:")
        for line in lines[5:15]:  # Show top 10 functions
            if line.strip():
                print(f"   {line}")

    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 80)
        print("📄 VALIDATION REPORT")
        print("=" * 80)

        # Validate diversity in outputs
        print("\n🔍 Output Diversity Analysis:")

        # Decisions
        if self.decisions_captured:
            unique_fingerprints = {
                d["moral_fingerprint"] for d in self.decisions_captured
            }
            dissonance_values = [d["dissonance_score"] for d in self.decisions_captured]
            print("\n   Ethical Decisions:")
            print(f"   - Total: {len(self.decisions_captured)}")
            print(f"   - Unique Fingerprints: {len(unique_fingerprints)}")
            print(
                f"   - Dissonance Range: {min(dissonance_values):.3f} - {max(dissonance_values):.3f}"
            )
            print(
                f"   - Approved: {sum(1 for d in self.decisions_captured if d['approved'])}"
            )
            print(
                f"   - Suppressed: {sum(1 for d in self.decisions_captured if not d['approved'])}"
            )

        # Experiences
        if self.experiences_captured:
            states = [e["state"] for e in self.experiences_captured]
            drift_values = [e["drift"] for e in self.experiences_captured]
            print("\n   Consciousness Experiences:")
            print(f"   - Total: {len(self.experiences_captured)}")
            print(f"   - Unique States: {set(states)}")
            print(
                f"   - Drift Range: {min(drift_values):.3f} - {max(drift_values):.3f}"
            )
            print(
                f"   - Average Coherence: {sum(e['coherence'] for e in self.experiences_captured) / len(self.experiences_captured):.3f}"
            )

        # Save detailed outputs
        validation_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "decisions": self.decisions_captured[:5],  # First 5 for review
            "experiences": self.experiences_captured[:5],
            "memories": self.memories_captured[:5],
            "collapses": self.collapses_captured[:5],
            "profile_summary": {
                component: stats.split("\n")[5:10]  # Top 5 functions per component
                for component, stats in self.profile_data.items()
            },
        }

        with open("vivox_validation_report.json", "w") as f:
            json.dump(validation_data, f, indent=2)

        print("\n📄 Detailed validation report saved to: vivox_validation_report.json")
        print("📄 Full debug log saved to: vivox_validation.log")

        # Save full profile data
        with open("vivox_profile_report.txt", "w") as f:
            for component, stats in self.profile_data.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"COMPONENT: {component}\n")
                f.write(f"{'='*80}\n")
                f.write(stats)

        print("📄 Full profiling report saved to: vivox_profile_report.txt")


async def main():
    """Run validation and profiling tests"""
    validator = ValidationProfiler()

    try:
        await validator.initialize()

        # Run validation tests
        await validator.validate_dynamic_outputs()

        # Run profiling
        await validator.profile_components()

        # Generate report
        validator.generate_validation_report()

        print("\n✅ Validation and profiling complete!")

    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
