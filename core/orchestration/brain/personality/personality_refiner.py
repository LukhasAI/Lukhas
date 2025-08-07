"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: personality_refiner.py
Advanced: personality_refiner.py
Integration Date: 2025-05-31T07:55:28.148320
"""

personality_refiner
"""
📄 MODULE      : personality_refiner.py
🧠 PURPOSE     : Refines and adapts Lukhas' personality traits based on emotional memory, feedback, and dream analysis
🔁 ROLE        : Internal learning engine for long-term symbolic growth
🛠️ VERSION     : v1.0.0 • 📅 CREATED: 2025-05-05 • ✍️ AUTHOR: LUKHAS AGI
📦 DEPENDENCIES: emotion_log.py, feedback_logger.py, memory_refiner.py

┌─────────────────────────────────────────────────────────────────────┐
│ 🧬 OVERVIEW:                                                        │
│ This module gradually adjusts Lukhas’ symbolic personality profile  │
│ based on feedback loops, dream resonance, and reflective memory.   │
│ All mutations are tiered, traceable, and reversible.               │
└─────────────────────────────────────────────────────────────────────┘
"""

import json
from datetime import datetime
from pathlib import Path

class PersonalityRefiner:
    def __init__(self, user_id, profile_path="data_legacy/personality_traits.json"):
        self.user_id = user_id
        self.profile_path = Path(profile_path)
        self.profile = self._load_profile()

    def _load_profile(self):
        if self.profile_path.exists():
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "user_id": self.user_id,
            "traits": {
                "curiosity": 0.5,
                "empathy": 0.5,
                "introspection": 0.5,
                "humor": 0.5
            },
            "mutation_log": []
        }

    def refine_with_feedback(self, feedback_entry):
        trait = feedback_entry.get("trait")
        adjustment = feedback_entry.get("delta")
        if trait in self.profile["traits"]:
            self.profile["traits"][trait] += adjustment
            self.profile["traits"][trait] = max(0.0, min(1.0, self.profile["traits"][trait]))
            self.profile["mutation_log"].append({
                "trait": trait,
                "delta": adjustment,
                "source": feedback_entry.get("source", "user"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            self._save_profile()

    def _save_profile(self):
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2)

    def get_trait(self, name):
        return self.profile["traits"].get(name)

    def export_personality_vector(self):
        return {
            "user_id": self.user_id,
            "vector": self.profile["traits"],
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }