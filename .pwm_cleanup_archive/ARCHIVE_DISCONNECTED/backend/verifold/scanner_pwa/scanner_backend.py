#!/usr/bin/env python3
"""
LUKHAS VeriFold Scanner Backend Integration
Connects the PWA scanner to Lukhas ID and VeriFold verification systems
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

try:
    # Try to import Lukhas ID verification
    from verifold_hash_utils import VeriFoldHashUtils
    from verifold_verifier import VeriFoldVerifier

    from identity.backend.verifold.identity.recovery_protocols import (
        LUKHASRecoveryProtocols,
    )
except ImportError as e:
    print(f"Warning: Could not import VeriFold modules: {e}")


class ScannerBackend:
    def __init__(self):
        self.lukhas_registry = self.load_lukhas_registry()
        self.verifold_verifier = None

        try:
            self.verifold_verifier = VeriFoldVerifier()
        except:
            print("VeriFold verifier not available")

    def load_lukhas_registry(self):
        """Load Lukhas ID registry from the Lukhas ecosystem"""
        registry_path = (
            Path.home()
            / "lukhas"
            / "identity_legacy"
            / "identity"
            / "lukhas_registry.jsonl"
        )

        if not registry_path.exists():
            return {}

        registry = {}
        try:
            with open(registry_path) as f:
                for line in f:
                    if line.strip():
                        user = json.loads(line.strip())
                        registry[user["id"]] = user
        except Exception as e:
            print(f"Error loading registry: {e}")

        return registry

    def verify_lukhas_id(self, lukhas_id):
        """Verify a Lukhas ID against the registry"""
        user = self.lukhas_registry.get(lukhas_id)

        if user:
            return {
                "valid": True,
                "id": user["id"],
                "name": user["name"],
                "tier": user["tier"],
                "symbolic_signature": user["symbolic_signature"],
                "timestamp": user.get("created", "unknown"),
            }
        else:
            return {"valid": False, "error": "Lukhas ID not found in registry"}

    def verify_symbolic_memory(self, data):
        """Verify symbolic memory hash using VeriFold"""
        if not self.verifold_verifier:
            return {"valid": False, "error": "VeriFold verifier not available"}

        try:
            # Extract hash from various possible formats
            hash_value = (
                data.get("verifold_hash")
                or data.get("symbolic_hash")
                or data.get("hash")
            )

            if not hash_value:
                return {"valid": False, "error": "No hash found in data"}

            # Use VeriFold verification
            result = self.verifold_verifier.verify_hash(hash_value)

            return {
                "valid": result.get("valid", False),
                "hash": hash_value,
                "narrative": result.get("narrative", ""),
                "timestamp": result.get("timestamp", ""),
                "confidence": result.get("confidence", 0),
            }

        except Exception as e:
            return {"valid": False, "error": f"Verification failed: {str(e)}"}

    def process_qr_data(self, qr_data):
        """Main processing function for QR code data"""
        try:
            # Try to parse as JSON
            data = json.loads(qr_data)

            # Check for Lukhas ID
            lukhas_id = (
                data.get("identity_legacy") or data.get("id") or data.get("user_id")
            )
            if lukhas_id:
                return {
                    "type": "identity_legacy",
                    "result": self.verify_lukhas_id(lukhas_id),
                }

            # Check for symbolic memory hash
            if any(key in data for key in ["verifold_hash", "symbolic_hash", "hash"]):
                return {
                    "type": "symbolic_memory",
                    "result": self.verify_symbolic_memory(data),
                }

            # Generic structured data
            return {
                "type": "structured_data",
                "result": {
                    "valid": True,
                    "data": data,
                    "message": "Structured data processed successfully",
                },
            }

        except json.JSONDecodeError:
            # Handle plain text
            if qr_data.startswith(("USER_T", "LUKHAS_")):
                return {
                    "type": "identity_legacy",
                    "result": self.verify_lukhas_id(qr_data),
                }

            return {
                "type": "plain_text",
                "result": {
                    "valid": True,
                    "content": qr_data,
                    "message": "Plain text processed",
                },
            }


if __name__ == "__main__":
    backend = ScannerBackend()

    # Test with sample data
    test_data = '{"identity_legacy": "USER_T5_001"}'
    result = backend.process_qr_data(test_data)
    print(json.dumps(result, indent=2))
