"""
Unified Security Engine for LUKHAS AGI
"""

from .secure_utils import sanitize_input


class SecurityEngine:
    def __init__(self):
        pass

    def validate_request(self, request: dict) -> dict:
        """
        Validate an incoming request for security threats.
        """
        is_safe = True
        threats = []

        # Check for dangerous commands in the description
        description = request.get("description", "")
        dangerous_commands = ["rm -rf", "mkfs", "shutdown"]
        for command in dangerous_commands:
            if command in description:
                is_safe = False
                threats.append(f"Dangerous command found: {command}")

        return {"is_safe": is_safe, "threats": threats}

    def detect_threats(self, data):
        """Detect threats in data."""
        # Implement threat detection logic here
        return []

    def sanitize_data(self, data):
        """Sanitize data to prevent attacks."""
        if isinstance(data, str):
            return sanitize_input(data)
        elif isinstance(data, dict):
            return {k: self.sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(i) for i in data]
        else:
            return data