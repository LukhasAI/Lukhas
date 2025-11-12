"""ΛiD configuration with FaceID toggle."""
from dataclasses import dataclass


@dataclass
class LidConfig:
    """Configuration for ΛiD identity system."""

    require_faceid: bool = False
    """Whether to require FaceID for login (default: disabled)"""

    enable_seed_phrase: bool = True
    """Allow seed phrase authentication"""

    enable_webauthn: bool = True
    """Allow WebAuthn authentication"""

    session_timeout_seconds: int = 3600
    """Session timeout in seconds"""

    def is_faceid_required(self) -> bool:
        """Check if FaceID is required for login."""
        return self.require_faceid

    def check_login_flow(self, method: str) -> bool:
        """
        Check if login method is allowed given current config.

        Args:
            method: Login method name

        Returns:
            True if method is allowed
        """
        if method == "faceid":
            return True  # FaceID always allowed if supported

        # If FaceID is required, other methods are not allowed
        if self.require_faceid:
            return False

        # Check other methods
        if method == "seed_phrase":
            return self.enable_seed_phrase
        elif method == "webauthn":
            return self.enable_webauthn

        return False


if __name__ == "__main__":
    print("=== ΛiD Config with FaceID Toggle Demo ===\n")

    # Default config (FaceID not required)
    config = LidConfig()
    print(f"Default config:")
    print(f"  FaceID required: {config.is_faceid_required()}")
    print(f"  Seed phrase allowed: {config.check_login_flow('seed_phrase')}")
    print(f"  WebAuthn allowed: {config.check_login_flow('webauthn')}\n")

    # FaceID required
    strict_config = LidConfig(require_faceid=True)
    print(f"FaceID required config:")
    print(f"  FaceID required: {strict_config.is_faceid_required()}")
    print(f"  Seed phrase allowed: {strict_config.check_login_flow('seed_phrase')}")
    print(f"  FaceID allowed: {strict_config.check_login_flow('faceid')}")
