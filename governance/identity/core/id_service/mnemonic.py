"""
Minimal mnemonic module stub for testing purposes.
This is a placeholder for the actual mnemonic library.
"""

class Mnemonic:
    """Mock Mnemonic class for BIP39 functionality."""

    def __init__(self, language="english"):
        self.language = language
        self.wordlist = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid"
        ]

    def generate(self, strength=128):
        """Generate a mock mnemonic phrase."""
        # Mock implementation - returns a simple phrase
        word_count = strength // 11  # Approximate word count
        return " ".join(self.wordlist[:min(word_count, len(self.wordlist))])

    def to_seed(self, mnemonic, passphrase=""):
        """Convert mnemonic to seed (mock implementation)."""
        # Mock implementation - returns a fake seed
        return b"mock_seed_" + mnemonic.encode()[:32]