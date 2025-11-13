"""
Glyph Verifier
"""
import base64
import json
import time


class GlyphVerifier:
    """
    Simulates a JWE-like token verification.
    The "token" is a base64-encoded JSON string containing user_id and expiry.
    """

    async def verify(self, token: str, user_id: str) -> bool:
        """
        Verifies the glyph token by decoding it, checking the user ID,
        and ensuring it has not expired.
        """
        if not token or not user_id:
            return False

        try:
            # Decode the token
            decoded_str = base64.b64decode(token).decode('utf-8')
            token_data = json.loads(decoded_str)

            # Verify the contents
            if token_data.get("user_id") != user_id:
                return False

            return not time.time() > token_data.get("expires_at", 0)

        except (TypeError, ValueError, base64.binascii.Error, json.JSONDecodeError):
            # If any decoding or parsing error occurs, the token is invalid.
            return False

    @staticmethod
    def _generate_test_token(user_id: str, expires_in_seconds: int = 60) -> str:
        """Helper to generate a valid token for testing."""
        payload = {
            "user_id": user_id,
            "expires_at": time.time() + expires_in_seconds,
        }
        token_bytes = json.dumps(payload).encode('utf-8')
        return base64.b64encode(token_bytes).decode('utf-8')
