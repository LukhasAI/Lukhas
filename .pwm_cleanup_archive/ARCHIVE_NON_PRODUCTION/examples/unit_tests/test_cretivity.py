"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: test_cretivity.py
Advanced: test_cretivity.py
Integration Date: 2025-05-31T07:55:28.152388
"""

# Test code
from creativity.advanced_haiku_generator import (
    AdvancedHaikuGenerator as NeuroHaikuGenerator,
)

if __name__ == "__main__":
    # Mock symbolic database with example words
    mock_db = {
        "fragment_concepts": ["nature", "time", "moment"],
        "phrase_concepts": ["action", "reflection", "journey"],
        "nature_words": ["tree", "wind", "sun", "moon", "rain", "cloud"],
        "time_words": ["dawn", "dusk", "now", "then", "soon", "night"],
        "moment_words": ["pause", "breath", "glimpse", "flash", "instant"],
        "action_words": ["walk", "run", "leap", "dance", "sing", "dream"],
        "reflection_words": ["think", "wonder", "ponder", "recall", "remember"],
        "journey_words": ["path", "road", "trail", "voyage", "quest"],
        "sensory_words": ["bright", "soft", "loud", "sweet", "bitter"],
        "emotion_words": ["happy", "sad", "calm", "fierce", "gentle"],
        "contrast_words": ["still", "bright", "dark", "silent", "loud"],
    }

    # Mock federated model
    class MockFederatedModel:
        def get_parameters(self):
            return {"style_weights": {"nature": 0.8, "tech": 0.2}}

        def predict_expansion_type(self, line):
            # Simple mock to rotate through different expansion types
            if "tree" in line.lower():
                return "imagery"
            elif "path" in line.lower():
                return "emotion"
            else:
                return "contrast"

    # Create haiku generator
    haiku_gen = NeuroHaikuGenerator(mock_db, MockFederatedModel())

    # Generate and print a haiku (using legacy neural method for sync compatibility)
    print("Generated Haiku:")
    print(haiku_gen.generate_neural_haiku())

    # Try with different expansion depth
    print("\nWith more expansion:")
    print(haiku_gen.generate_neural_haiku(expansion_depth=3))
