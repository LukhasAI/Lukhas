"""Oneiric configuration with reproducibility support."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class OneiricConfig:
    """Configuration for Oneiric dream generation system."""

    # Reproducibility
    seed_lock: Optional[int] = None
    """
    Optional seed lock for reproducible dream generation.
    When set, freezes randomness to enable deterministic runs for testing.
    """

    # Generation parameters
    max_dream_length: int = 1000
    intensity_range: tuple[float, float] = (0.0, 1.0)
    enable_regret_signatures: bool = True

    # Storage
    persist_dreams: bool = True
    link_to_memory_folds: bool = True
    link_to_wavec: bool = True

    def is_reproducible(self) -> bool:
        """Check if configuration enables reproducible generation."""
        return self.seed_lock is not None

    def get_seed(self) -> Optional[int]:
        """Get the current seed lock value."""
        return self.seed_lock

    def set_seed(self, seed: int) -> None:
        """
        Set seed lock for reproducible generation.

        Args:
            seed: Random seed value
        """
        self.seed_lock = seed

    def clear_seed(self) -> None:
        """Clear seed lock, returning to non-deterministic generation."""
        self.seed_lock = None


# Default configuration instance
default_config = OneiricConfig()


if __name__ == "__main__":
    # Demonstration
    print("=== Oneiric Config with Seed Lock Demo ===\n")

    config = OneiricConfig()
    print(f"Initial config - reproducible: {config.is_reproducible()}")
    print(f"Seed: {config.get_seed()}\n")

    # Enable reproducibility
    config.set_seed(42)
    print("After setting seed=42:")
    print(f"  Reproducible: {config.is_reproducible()}")
    print(f"  Seed: {config.get_seed()}\n")

    # Create config with seed at initialization
    reproducible_config = OneiricConfig(seed_lock=12345)
    print("Config with seed_lock=12345:")
    print(f"  Reproducible: {reproducible_config.is_reproducible()}")
    print(f"  Seed: {reproducible_config.get_seed()}\n")

    # Clear seed
    config.clear_seed()
    print("After clearing seed:")
    print(f"  Reproducible: {config.is_reproducible()}")
    print(f"  Seed: {config.get_seed()}")
