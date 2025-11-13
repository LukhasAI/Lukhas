"""Endocrine API with mood-to-tags export."""

from .hormone_system import HormoneSystem


class EndocrineAPI:
    """Public API for endocrine system."""

    def __init__(self, hormone_system: HormoneSystem):
        self.system = hormone_system

    def to_tags(self) -> List[str]:
        """
        Convert current mood/hormone state to tag bundle.

        Returns:
            List of tags representing hormones and derived emotions
        """
        tags = []
        state = self.system.state

        # Hormone tags
        tags.append(f"#TAG:hormone/cortisol:{state.cortisol:.2f}")
        tags.append(f"#TAG:hormone/beta_endorphin:{state.beta_endorphin:.2f}")
        tags.append(f"#TAG:hormone/dopamine:{state.dopamine:.2f}")
        tags.append(f"#TAG:hormone/serotonin:{state.serotonin:.2f}")

        # Derived emotion tags
        if state.cortisol > 0.7:
            tags.append("#TAG:emotion/stressed")
        if state.beta_endorphin > 0.7:
            tags.append("#TAG:emotion/relaxed")
        if state.dopamine > 0.7:
            tags.append("#TAG:emotion/motivated")
        if state.serotonin > 0.7:
            tags.append("#TAG:emotion/stable")
        if state.cortisol < 0.3 and state.serotonin > 0.6:
            tags.append("#TAG:emotion/calm")

        return tags


if __name__ == "__main__":
    print("=== Endocrine Mood→Tags Demo ===\n")

    system = HormoneSystem()
    api = EndocrineAPI(system)

    print("Initial tags:")
    for tag in api.to_tags():
        print(f"  {tag}")

    print("\nAfter stress trigger:")
    system.trigger_stress(0.8)
    for tag in api.to_tags():
        print(f"  {tag}")
