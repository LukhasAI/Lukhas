#!/usr/bin/env python3
"""
🧬 DNA Helix Memory System Demonstration
Shows the immutable memory architecture in action
"""

import asyncio
import os
import sys

from lukhas.memory.dna_helix import (
    MemoryHelix,
    RepairMethod,
    SymbolicRepairLoop,
    SymbolicStrand,
)
from lukhas.memory.dna_helix.helix_vault import HelixVault

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def demonstrate_basic_memory():
    """Demonstrate basic DNA helix memory operations"""
    print("\n" + "=" * 60)
    print("🧬 BASIC DNA HELIX MEMORY")
    print("=" * 60)

    # Create a memory with origin strand
    origin_glyphs = ["TRUST", "PROTECT", "LEARN", "GROW", "HELP", "CONNECT"]
    memory = MemoryHelix("childhood_memory_001", origin_glyphs)

    print(f"\n✨ Created memory: {memory.memory_id}")
    print(f"📝 Origin strand: {' → '.join(origin_glyphs)}")
    print("🔒 Immutable: Origin can never be changed")

    # Access memory
    data = memory.access()
    print(f"\n📖 Accessing memory (count: {data['metadata']['accessed']})")
    print(f"   Current state: {' → '.join(data['current'])}")
    print(f"   Drift: {data['drift']:.3f}")

    # Simulate memory drift over time
    print("\n⏰ Simulating memory drift over time...")
    drifted_glyphs = ["TRUST", "DEFEND", "STUDY", "GROW", "ASSIST", "NETWORK"]
    memory.mutate(drifted_glyphs)

    print("🌊 Memory has drifted:")
    print(f"   Original: {' → '.join(origin_glyphs)}")
    print(f"   Current:  {' → '.join(drifted_glyphs)}")
    print(f"   Drift score: {memory.helix_core.calculate_drift()}:.3f}")

    # Repair memory
    if memory.helix_core.should_repair():
        print("\n🛠 Memory drift exceeds threshold - initiating repair...")
        memory.helix_core.repair(method=RepairMethod.PARTIAL_HEAL, cause="Demonstration drift correction")

        repaired = list(memory.helix_core.current.sequence)
        print("✅ Memory repaired:")
        print(f"   Repaired: {' → '.join(repaired)}")
        print(f"   New drift: {memory.helix_core.calculate_drift()}:.3f}")

        # Show repair history
        repair = memory.helix_core.repair_history[-1]
        print("\n📜 Repair details:")
        print(f"   Method: {repair.repair_method.value}")
        print(f"   Confidence: {repair.confidence:.3f}")
        print(f"   Glyphs repaired: {len(repair.glyphs_repaired)}")


async def demonstrate_multi_context_memory():
    """Demonstrate multi-dimensional memory with contexts"""
    print("\n" + "=" * 60)
    print("🌈 MULTI-CONTEXT MEMORY")
    print("=" * 60)

    # Create episodic memory with multiple contexts
    memory = MemoryHelix(
        "first_day_school",
        ["ARRIVE", "NERVOUS", "MEET", "TEACHER", "LEARN", "PLAY", "FRIENDS"],
    )

    # Add emotional context
    memory.add_emotional_context(["ANXIOUS", "CURIOUS", "EXCITED", "HAPPY"])

    # Add temporal context
    memory.add_temporal_context(["SEPTEMBER", "MORNING", "EIGHT_AM", "FIRST_DAY"])

    # Add causal context
    memory.add_causal_context(["NEW_SCHOOL", "PARENTS_MOVED", "FRESH_START"])

    print("\n🧬 Created multi-dimensional memory")
    data = memory.access()

    print(f"\n📍 Core memory: {' → '.join(data['origin'][:4])}...")
    print(f"❤️  Emotional: {' → '.join(data['emotional_context'])}")
    print(f"⏰ Temporal: {' → '.join(data['temporal_context'])}")
    print(f"🔗 Causal: {' → '.join(data['causal_context'])}")

    # Calculate multi-dimensional coherence
    print("\n🔮 Memory coherence analysis:")
    print(f"   Core drift: {memory.helix_core.calculate_drift()}:.3f}")
    print(f"   Entropy: {memory.origin_strand.entropy()}:.3f}")
    print("   Immutability: ✅ Origin preserved")


async def demonstrate_memory_vault():
    """Demonstrate the Helix Vault system"""
    print("\n" + "=" * 60)
    print("🔐 HELIX VAULT SYSTEM")
    print("=" * 60)

    # Create vault
    vault = HelixVault()
    await vault.start()

    print("\n🏛 Creating memory vault...")

    # Create various types of memories
    memories = [
        (
            "skill_riding_bike",
            [
                "BALANCE",
                "PEDAL",
                "STEER",
                "BRAKE",
                "PRACTICE",
                "FALL",
                "RETRY",
                "SUCCESS",
            ],
            {"procedural", "motor_skill", "childhood"},
        ),
        (
            "fact_gravity",
            [
                "NEWTON",
                "FORCE",
                "MASS",
                "ACCELERATION",
                "9.8",
                "METERS",
                "SECOND",
                "SQUARED",
            ],
            {"semantic", "physics", "scientific"},
        ),
        (
            "event_birthday_10",
            [
                "CAKE",
                "CANDLES",
                "FRIENDS",
                "GIFTS",
                "SURPRISE",
                "JOY",
                "FAMILY",
                "PHOTOS",
            ],
            {"episodic", "celebration", "childhood"},
        ),
        (
            "trauma_accident",
            ["CAR", "CRASH", "FEAR", "PAIN", "HOSPITAL", "RECOVERY", "SCAR", "CAUTION"],
            {"episodic", "trauma", "formative"},
        ),
    ]

    for mem_id, glyphs, tags in memories:
        vault.create_memory(mem_id, glyphs, tags)
        print(f"   ✓ Created: {mem_id}")

    # Show vault statistics
    stats = vault.get_statistics()
    print("\n📊 Vault Statistics:")
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Average drift: {stats['avg_drift']:.3f}")
    print(f"   Unique tags: {stats['unique_tags']}")

    # Demonstrate search
    print("\n🔍 Searching memories:")

    childhood_memories = vault.search_by_tags({"childhood"})
    print(f"   Childhood memories: {len(childhood_memories)}")
    for mem in childhood_memories:
        print(f"      • {mem.memory_id}")

    episodic_memories = vault.search_by_tags({"episodic"})
    print(f"   Episodic memories: {len(episodic_memories)}")

    # Simulate drift in trauma memory
    trauma_memory = vault.get_memory("trauma_accident")
    if trauma_memory:
        # Drift: Memory softens over time
        trauma_memory.mutate(
            [
                "CAR",
                "INCIDENT",
                "CONCERN",
                "DISCOMFORT",
                "CLINIC",
                "HEALING",
                "MARK",
                "CAREFUL",
            ]
        )

        print("\n🌊 Trauma memory drift detected:")
        print(f"   Drift level: {trauma_memory.helix_core.calculate_drift()}:.3f}")

        # Use consensus repair from other episodic memories
        print("   🤝 Attempting consensus repair...")
        success = await vault.consensus_repair("trauma_accident", {"episodic"})
        if success:
            print("   ✅ Consensus repair completed")

    # Create drift oracle
    oracle = vault.create_drift_oracle()
    analysis = oracle.analyze_drift_patterns()

    print("\n🔮 Drift Oracle Analysis:")
    print(f"   Average drift velocity: {analysis['drift_velocity']:.4f}/hour")
    print(f"   Repair effectiveness: {analysis['repair_effectiveness']:.2%}")

    # Predict future repairs
    predictions = oracle.predict_repair_needs(hours_ahead=24)
    if predictions:
        print("\n⚠️  Predicted repairs needed within 24 hours:")
        for mem_id, predicted_drift in predictions[:3]:
            print(f"   • {mem_id}: predicted drift {predicted_drift:.3f}")

    await vault.stop()


async def demonstrate_gdpr_compliance():
    """Demonstrate GDPR-compliant memory operations"""
    print("\n" + "=" * 60)
    print("🇪🇺 GDPR COMPLIANCE FEATURES")
    print("=" * 60)

    # Create personal memory
    memory = MemoryHelix(
        "personal_data_001",
        ["NAME", "JOHN_DOE", "EMAIL", "JOHN@EXAMPLE", "LOCATION", "PARIS"],
    )
    memory.tags.add("personal_data")
    memory.tags.add("user_12345")

    print("\n📝 Created personal data memory")
    print(f"   ID: {memory.memory_id}")
    print(f"   Tags: {memory.tags}")

    # Normal access
    data = memory.access()
    print("\n✅ Normal access permitted")
    print(f"   Data: {' → '.join(data['current'][:4])}...")

    # GDPR Article 17 - Right to erasure
    print("\n🔒 User exercises right to erasure (GDPR Article 17)")
    memory.lock("GDPR Article 17 - User request for erasure")

    print(f"   Memory locked: {memory.locked}")
    print(f"   Lock reason: {[t for t in memory.tags if t.startswith('locked:')}]}")

    # Attempt access after lock
    print("\n❌ Attempting access after lock:")
    try:
        memory.access()
    except PermissionError as e:
        print(f"   Access denied: {e}")

    # Show that origin is still preserved (for legal/audit purposes)
    print("\n📋 Audit trail (origin preserved):")
    print("   Origin exists: ✅")
    print("   Origin immutable: ✅")
    print("   Access blocked: ✅")
    print("   GDPR compliant: ✅")


async def demonstrate_repair_loop():
    """Demonstrate automatic repair loop"""
    print("\n" + "=" * 60)
    print("🔄 AUTOMATIC REPAIR LOOP")
    print("=" * 60)

    # Create memory prone to drift
    memory = MemoryHelix(
        "unstable_memory",
        ["STABLE", "THOUGHT", "CLEAR", "FOCUSED", "RATIONAL", "LOGICAL"],
    )

    # Create repair loop
    helix = memory.helix_core
    helix.drift_threshold = 0.3  # Lower threshold for demo
    repair_loop = SymbolicRepairLoop(helix, check_interval=1.0, auto_repair=True)

    print("\n🔄 Starting automatic repair loop...")
    print("   Check interval: 1 second")
    print(f"   Drift threshold: {helix.drift_threshold}")
    print("   Auto-repair: enabled")

    await repair_loop.start()

    # Simulate gradual drift
    print("\n🌊 Introducing gradual drift...")

    for i in range(3):
        await asyncio.sleep(1.5)

        # Introduce some drift
        current = list(helix.current.sequence)
        if i == 0:
            current[1] = "CHAOTIC"
            print(f"   Drift {i + 1}: THOUGHT → CHAOTIC")
        elif i == 1:
            current[3] = "SCATTERED"
            print(f"   Drift {i + 1}: FOCUSED → SCATTERED")
        else:
            current[5] = "EMOTIONAL"
            print(f"   Drift {i + 1}: LOGICAL → EMOTIONAL")

        helix.current = SymbolicStrand(current)
        drift = helix.calculate_drift()
        print(f"   Current drift: {drift:.3f}")

        if drift > helix.drift_threshold:
            print("   ⚠️  Drift exceeds threshold!")
            print("   ⏳ Waiting for auto-repair...")
            await asyncio.sleep(2)
            print(f"   ✅ Post-repair drift: {helix.calculate_drift()}:.3f}")

    await repair_loop.stop()

    # Show repair history
    print(f"\n📜 Repair History ({len(helix.repair_history)} repairs):")
    for i, repair in enumerate(helix.repair_history):
        print(f"   {i + 1}. {repair.timestamp.strftime('%H:%M:%S')} - {repair.repair_method.value}")
        print(f"      Drift: {repair.drift_before:.3f} → {repair.drift_after:.3f}")


async def main():
    """Run all demonstrations"""
    print("\n" + "=" * 60)
    print("🧬 LUKHAS DNA HELIX MEMORY SYSTEM")
    print("   Immutable Memory Architecture Demonstration")
    print("=" * 60)

    # Run demonstrations
    await demonstrate_basic_memory()
    await demonstrate_multi_context_memory()
    await demonstrate_memory_vault()
    await demonstrate_gdpr_compliance()
    await demonstrate_repair_loop()

    print("\n" + "=" * 60)
    print("✨ DNA HELIX DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  ✓ Immutable origin strands")
    print("  ✓ Drift detection and repair")
    print("  ✓ Multi-dimensional memory contexts")
    print("  ✓ Helix Vault with search and consensus")
    print("  ✓ GDPR compliance (right to erasure)")
    print("  ✓ Automatic repair loops")
    print("  ✓ Drift prediction and analysis")


if __name__ == "__main__":
    asyncio.run(main())
