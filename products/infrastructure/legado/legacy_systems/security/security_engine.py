"""
Unified Security Engine for LUKHAS AGI
"""

import html
import re


def sanitize_input(text: str) -> str:
    """Basic input sanitization function."""
    if not isinstance(text, str):
        return str(text)

    # HTML escape
    sanitized = html.escape(text)

    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"eval\s*\(",
        r"exec\s*\(",
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    return sanitized


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
