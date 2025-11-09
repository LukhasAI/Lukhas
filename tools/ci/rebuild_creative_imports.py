#!/usr/bin/env python3
"""Quick script to rebuild creative_q_expression.py import map from grep."""

import json

# The 47 undefined class names from previous analysis
UNDEFINED_CLASSES = [
    "AcetylcholineLearningBridge",
    "CollaborativeSessionRequest",
    "CreativeBlockchain",
    "CreativeConflictHarmonizer",
    "CreativeEvolutionEngine",
    "CreativeRequest",
    "CreativityMeshNetwork",
    "CreativityMonitor",
    "CreativityStyleEvolver",
    "CrossCulturalSynthesizer",
    "CulturalQIMemory",
    "CulturalResonanceTuner",
    "CulturalScaleQuantumLibrary",
    "DopamineCreativityModulator",
    "DopamineRewardSystem",
    "EmergenceDetector",
    "EmotionImageryQuantumMapper",
    "EmotionalMelodyWeaver",
    "EmotionalPreferenceLearner",
    "HarmonicQuantumInspiredProcessor",
    "KirejiQuantumSelector",
    "NeuralCreativityNetwork",
    "NeuralOscillator",
    "NorepinephrineFocusEnhancer",
    "PersonalizedCreation",
    "PhoneticHarmonyAnalyzer",
    "QIAestheticProfiler",
    "QIChoreographer",
    "QICodePoet",
    "QIEmotionEncoder",
    "QIIdeaSynthesizer",
    "QIImaginationProcessor",
    "QIStoryWeaver",
    "QISyllableCounter",
    "QIVisualArtist",
    "QIWatermarkEmbedder",
    "Quantum3DSculptor",
    "REMDreamSynthesizer",
    "RhythmPatternSuperposer",
    "SeasonalReferenceEncoder",
    "SemanticEntangler",
    "SerotoninMoodHarmonizer",
    "SwarmCreativityOrchestrator",
    "SynapticInspirationPool",
    "SynapticPlasticityEngine",
    "UserSession",
    "ZeroKnowledgeCreativityValidator",
]

# Heuristic: Most classes are in labs.consciousness.creativity.qi_creative_types
# Only Quantum3DSculptor is unique
import_map = {}

# Simple mapping based on previous analysis
for cls in UNDEFINED_CLASSES:
    if cls == "Quantum3DSculptor":
        import_map[cls] = (
            "products.content.poetica.creativity_engines.qi_creative_types"
        )
    else:
        import_map[cls] = "labs.consciousness.creativity.qi_creative_types"

# Save to /tmp
output_path = "/tmp/creative_import_map_resolved.json"
with open(output_path, "w") as f:
    json.dump(import_map, f, indent=2)

print(f"✅ Regenerated import map: {len(import_map)} classes")
print(f"✅ Saved to: {output_path}")
print("\nPreview:")
print(
    f"  - labs.consciousness: {sum(1 for m in import_map.values() if 'labs.consciousness' in m)} classes"
)
print(
    f"  - products.content: {sum(1 for m in import_map.values() if 'products.content' in m)} classes"
)
