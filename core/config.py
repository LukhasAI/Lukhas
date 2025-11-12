"""Core system configuration."""
import os
from dataclasses import dataclass


@dataclass
class CoreConfig:
    """Core LUKHAS configuration."""

    LOG_ONLY: bool = False
    """
    Global LOG_ONLY toggle for risky paths.
    When enabled, guardian/router will log decisions without acting.
    Read from environment variable LUKHAS_LOG_ONLY.
    """

    DEBUG: bool = False
    """Enable debug mode"""

    ENVIRONMENT: str = "development"
    """Deployment environment"""

    @classmethod
    def from_env(cls) -> "CoreConfig":
        """Load configuration from environment variables."""
        return cls(
            LOG_ONLY=os.getenv("LUKHAS_LOG_ONLY", "false").lower() == "true",
            DEBUG=os.getenv("LUKHAS_DEBUG", "false").lower() == "true",
            ENVIRONMENT=os.getenv("LUKHAS_ENV", "development")
        )


# Global config instance
config = CoreConfig.from_env()


if __name__ == "__main__":
    print("=== Core Config Demo ===\n")

    cfg = CoreConfig.from_env()
    print(f"LOG_ONLY: {cfg.LOG_ONLY}")
    print(f"DEBUG: {cfg.DEBUG}")
    print(f"ENVIRONMENT: {cfg.ENVIRONMENT}")

    print("\nSet LUKHAS_LOG_ONLY=true to enable log-only mode")
