#!/usr/bin/env python3
"""
Module: debug_pls.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""


"""Debug PLS threat extraction"""

from aka_qualia.pls import PLS

# Create PLS instance
pls = PLS(random_seed=123, enable_stochasticity=False)

# Test signals from failing test
signals = {"text": "extreme danger panic threat alarm crisis", "emotion": {"valence": -0.9, "arousal": 0.95}}

print("Input signals:", signals)

# Extract latent representation
latent = pls.encode(signals, memory_ctx={"similarity_scores": [0.2]})

print("Extracted latent:")
print(f"  threat_level: {latent.threat_level:.3f}")
print(f"  soothing_level: {latent.soothing_level:.3f}")
print(f"  complexity: {latent.complexity:.3f}")
print(f"  familiarity: {latent.familiarity:.3f}")
print(f"  temporal_pressure: {latent.temporal_pressure:.3f}")
print(f"  agency_signals: {latent.agency_signals:.3f}")

# Decode to proto-qualia
proto = pls.decode_protoqualia(latent, temperature=0.4)

print("Generated proto-qualia:")
print(f"  tone: {proto.tone:.3f}")
print(f"  arousal: {proto.arousal:.3f}")
print(f"  clarity: {proto.clarity:.3f}")
print(f"  embodiment: {proto.embodiment:.3f}")
print(f"  colorfield: {proto.colorfield}")
print(f"  narrative_gravity: {proto.narrative_gravity:.3f}")

# Debug threat extraction specifically
threat = pls._extract_threat_signals(signals)
print(f"Raw threat extraction: {threat:.3f}")

# Count text keywords
text = signals["text"].lower()
threat_keywords = ["danger", "threat", "fear", "anxiety", "panic", "alarm", "risk"]
found_keywords = [word for word in threat_keywords if word in text]
print(f"Found threat keywords: {found_keywords}")

# Check emotion processing
emotion = signals["emotion"]
if "valence" in emotion:
    valence = emotion["valence"]
    if valence < 0:
        emotion_threat = abs(valence) * 0.3
        print(f"Emotion threat (|{valence}| * 0.3): {emotion_threat:.3f}")
