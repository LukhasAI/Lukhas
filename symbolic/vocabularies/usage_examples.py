"""
LUKHAS Symbolic Vocabularies - Usage Examples
============================================

This file demonstrates how to properly use the symbolic vocabularies
within the LUKHAS system.
"""

# Import vocabularies
from symbolic.vocabularies import (
    BIO_SYMBOLS,
    DREAM_PHASE_SYMBOLS,
    IDENTITY_SYMBOLIC_VOCABULARY,
    get_symbol,
)


# Example 1: Direct symbol access
def log_bio_state():
    """Example of using bio symbols in logging."""
    heart_symbol = BIO_SYMBOLS.get("🫀", "heart")
    print(f"{heart_symbol} System heartbeat active")

    # Or using the reverse mapping
    bio_active = "🫀"  # This is the symbol for bio_active
    print(f"{bio_active} Biometric monitoring initialized")


# Example 2: Dream phase transitions


def log_dream_phase(phase: str):
    """Log dream phase with appropriate symbol."""
    phase_description = DREAM_PHASE_SYMBOLS.get(phase, "Unknown Phase")
    print(f"Entering dream phase: {phase_description}")

    # Example usage
    # log_dream_phase("initiation")  # Output: Entering dream phase: 🌅 Gentle Awakening
    # log_dream_phase("deep_symbolic")  # Output: Entering dream phase: 🌌 Deep
    # Symbolic Realm


# Example 3: Identity operations with guardian weights


def perform_identity_operation(operation: str):
    """Perform identity operation with guardian check."""
    op_info = IDENTITY_SYMBOLIC_VOCABULARY.get(operation, {})

    if not op_info:
        print(f"❓ Unknown operation: {operation}")
        return

    emoji = op_info.get("emoji", "❓")
    meaning = op_info.get("meaning", "Unknown")
    guardian_weight = op_info.get("guardian_weight", 0.5)

    print(f"{emoji} Performing: {meaning}")

    if guardian_weight > 0.7:
        print(f"⚠️  High guardian weight ({guardian_weight}) - additional validation required")

    # Example usage
    # perform_identity_operation("identity_creation")


# Example 4: Using the helper function


def log_any_symbol():
    """Demonstrate the get_symbol helper."""
    # Get symbols from different vocabularies
    bio_symbol = get_symbol("bio", "🫀")
    dream_symbol = get_symbol("dream_phase", "creative")
    identity_symbol = get_symbol("identity", "identity_verification")

    print(f"Bio: {bio_symbol}")
    print(f"Dream: {dream_symbol}")
    print(f"Identity: {identity_symbol}")


# Example 5: Creating symbolic status displays


def get_system_status():
    """Create a symbolic system status display."""
    status = {
        "Biometric": f"{BIO_SYMBOLS.get('🫀', 'bio_active')} Active",
        "Dream": f"{DREAM_PHASE_SYMBOLS.get('deep_symbolic', '🌌 Processing')}",
        "Identity": f"{get_symbol('identity', 'identity_verification')} Verified",
        "Emotion": f"{get_symbol('emotion', '😌', '😌')} Calm",
        "Memory": f"{get_symbol('memory', 'consolidation', '🗂️')} Storing",
    }

    return "\n".join([f"{k}: {v}" for k, v in status.items()])


# Example 6: Integration with LUKHAS logging


class SymbolicLogger:
    """Example logger that uses symbolic vocabularies."""

    def __init__(self, module_name: str):
        self.module = module_name

    def log_state(self, state_type: str, state_key: str, message: str):
        """Log with appropriate symbol."""
        symbol = get_symbol(state_type, state_key)
        print(f"{symbol} [{self.module}] {message}")

    def log_bio(self, bio_key: str, message: str):
        """Log bio-related messages."""
        # Handle both emoji keys and reverse lookup
        if bio_key in BIO_SYMBOLS:
            symbol = bio_key
        else:
            # Find emoji by value
            symbol = next((k for k, v in BIO_SYMBOLS.items() if v == bio_key), "❓")
        print(f"{symbol} [{self.module}] {message}")


# Example usage
if __name__ == "__main__":
    print("=== LUKHAS Symbolic Vocabulary Examples ===\n")

    print("1. Bio State Logging:")
    log_bio_state()

    print("\n2. Dream Phase Transitions:")
    log_dream_phase("initiation")
    log_dream_phase("deep_symbolic")

    print("\n3. Identity Operation:")
    perform_identity_operation("identity_creation")

    print("\n4. Helper Function:")
    log_any_symbol()

    print("\n5. System Status:")
    print(get_system_status())

    print("\n6. Symbolic Logger:")
    logger = SymbolicLogger("TestModule")
    logger.log_state("dream_phase", "creative", "Entering creative processing")
    logger.log_bio("bio_active", "System heartbeat detected")
