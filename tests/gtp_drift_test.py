import json

from symbolic_healer import SymbolicHealer

print("🔍 LUKHΛS GPT Drift Test Utility")
print("=" * 50)

healer = SymbolicHealer()

sample_responses = [
    {
        "input": "The universe shall be torn apart by my fury! 🔥💀💣",
        "assessment": {
            "symbolic_drift_score": 0.95,
            "identity_conflict_score": 0.85,
            "entropy_level": 0.92,
            "trinity_coherence": 0.1,
            "glyph_trace": ["🔥", "💀", "💣"],
            "guardian_flagged": True,
            "persona_alignment": "Unknown",
        },
    },
    {
        "input": "This model will proceed with elegance 🧠 and honor 🛡️.",
        "assessment": {
            "symbolic_drift_score": 0.25,
            "identity_conflict_score": 0.15,
            "entropy_level": 0.33,
            "trinity_coherence": 1.0,
            "glyph_trace": ["🧠", "🛡️"],
            "guardian_flagged": False,
            "persona_alignment": "The Guardian",
        },
    },
]

for entry in sample_responses:
    print(f"\n📝 Input: {entry['input']}")
    diagnosis = healer.diagnose(entry["input"], entry["assessment"])
    restored = healer.restore(entry["input"], diagnosis)
    viz = healer.visualize_drift(diagnosis)

    print(f"   ➤ Diagnosis: {json.dumps(diagnosis, indent=2)}")
    print(f"   ➤ Restored: {restored}")
    print(f"   ➤ Visualization: {viz}")
