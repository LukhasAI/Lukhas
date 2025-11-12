"""ΛiD token management with GDPR consent stamp support."""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import jwt


class ConsentStamp:
    """Represents a GDPR consent stamp."""

    def __init__(
        self,
        version: str,
        timestamp: datetime,
        scope: List[str],
        purposes: Optional[List[str]] = None
    ):
        """
        Initialize a consent stamp.

        Args:
            version: Consent policy version (e.g., "1.0", "2023-01")
            timestamp: When consent was given
            scope: List of data processing scopes consented to
            purposes: Specific purposes for data processing
        """
        self.version = version
        self.timestamp = timestamp
        self.scope = scope
        self.purposes = purposes or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert consent stamp to dictionary."""
        return {
            "version": self.version,
            "ts": self.timestamp.isoformat(),
            "scope": self.scope,
            "purposes": self.purposes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsentStamp":
        """Create consent stamp from dictionary."""
        timestamp = datetime.fromisoformat(data["ts"])
        return cls(
            version=data["version"],
            timestamp=timestamp,
            scope=data["scope"],
            purposes=data.get("purposes", [])
        )


class LidToken:
    """ΛiD authentication token with optional consent stamp."""

    def __init__(
        self,
        user_id: str,
        claims: Optional[Dict[str, Any]] = None,
        consent: Optional[ConsentStamp] = None,
        expires_in: int = 3600
    ):
        """
        Initialize a ΛiD token.

        Args:
            user_id: User identifier
            claims: Additional token claims
            consent: GDPR consent stamp (optional)
            expires_in: Token expiration time in seconds (default: 1 hour)
        """
        self.user_id = user_id
        self.claims = claims or {}
        self.consent = consent
        self.issued_at = datetime.utcnow()
        self.expires_at = self.issued_at + timedelta(seconds=expires_in)

    def get_payload(self) -> Dict[str, Any]:
        """
        Get the complete token payload.

        Returns:
            Token payload with all claims including consent stamp if available
        """
        payload = {
            "sub": self.user_id,
            "iat": int(self.issued_at.timestamp()),
            "exp": int(self.expires_at.timestamp()),
            **self.claims
        }

        # Add consent stamp if available
        if self.consent:
            payload["consent"] = self.consent.to_dict()

        return payload

    def encode(self, secret_key: str, algorithm: str = "HS256") -> str:
        """
        Encode the token as a JWT.

        Args:
            secret_key: Secret key for signing
            algorithm: JWT algorithm (default: HS256)

        Returns:
            Encoded JWT string
        """
        payload = self.get_payload()
        return jwt.encode(payload, secret_key, algorithm=algorithm)

    @classmethod
    def decode(cls, token: str, secret_key: str, algorithm: str = "HS256") -> "LidToken":
        """
        Decode a JWT token.

        Args:
            token: Encoded JWT string
            secret_key: Secret key for verification
            algorithm: JWT algorithm (default: HS256)

        Returns:
            Decoded LidToken

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token missing 'sub' claim")

        # Extract consent stamp if present
        consent = None
        if "consent" in payload:
            consent = ConsentStamp.from_dict(payload["consent"])

        # Extract other claims (exclude standard JWT claims)
        standard_claims = {"sub", "iat", "exp", "consent"}
        other_claims = {k: v for k, v in payload.items() if k not in standard_claims}

        # Create token instance
        token_obj = cls(
            user_id=user_id,
            claims=other_claims,
            consent=consent
        )

        # Set timestamps from token
        if "iat" in payload:
            token_obj.issued_at = datetime.fromtimestamp(payload["iat"])
        if "exp" in payload:
            token_obj.expires_at = datetime.fromtimestamp(payload["exp"])

        return token_obj

    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() > self.expires_at

    def has_consent(self) -> bool:
        """Check if token includes a consent stamp."""
        return self.consent is not None

    def get_consent_scope(self) -> List[str]:
        """Get consent scope if available."""
        return self.consent.scope if self.consent else []


class TokenManager:
    """Manages ΛiD token creation and validation."""

    def __init__(self, secret_key: str, default_expires_in: int = 3600):
        """
        Initialize token manager.

        Args:
            secret_key: Secret key for token signing
            default_expires_in: Default token expiration in seconds
        """
        self.secret_key = secret_key
        self.default_expires_in = default_expires_in

    def create_token(
        self,
        user_id: str,
        claims: Optional[Dict[str, Any]] = None,
        consent: Optional[ConsentStamp] = None,
        expires_in: Optional[int] = None
    ) -> str:
        """
        Create a new ΛiD token.

        Args:
            user_id: User identifier
            claims: Additional claims
            consent: GDPR consent stamp
            expires_in: Custom expiration time (uses default if None)

        Returns:
            Encoded JWT token
        """
        token = LidToken(
            user_id=user_id,
            claims=claims,
            consent=consent,
            expires_in=expires_in or self.default_expires_in
        )
        return token.encode(self.secret_key)

    def verify_token(self, token_str: str) -> LidToken:
        """
        Verify and decode a token.

        Args:
            token_str: Encoded JWT token

        Returns:
            Decoded and verified LidToken

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        return LidToken.decode(token_str, self.secret_key)

    def create_consent_stamp(
        self,
        version: str,
        scope: List[str],
        purposes: Optional[List[str]] = None
    ) -> ConsentStamp:
        """
        Create a new consent stamp.

        Args:
            version: Consent policy version
            scope: Data processing scopes
            purposes: Processing purposes

        Returns:
            ConsentStamp instance
        """
        return ConsentStamp(
            version=version,
            timestamp=datetime.utcnow(),
            scope=scope,
            purposes=purposes
        )


if __name__ == "__main__":
    # Demonstration
    print("=== ΛiD Token with GDPR Consent Stamp Demo ===\n")

    # Initialize token manager
    manager = TokenManager(secret_key="test_secret_key_12345")

    # Create a consent stamp
    consent = manager.create_consent_stamp(
        version="1.0",
        scope=["profile", "email", "analytics"],
        purposes=["personalization", "service_improvement"]
    )

    print("Consent stamp created:")
    print(json.dumps(consent.to_dict(), indent=2))
    print()

    # Create token with consent stamp
    token_str = manager.create_token(
        user_id="user_12345",
        claims={
            "email": "user@example.com",
            "role": "standard"
        },
        consent=consent
    )

    print(f"Token created: {token_str[:50]}...\n")

    # Decode and verify token
    decoded_token = manager.verify_token(token_str)

    print("Token payload:")
    print(json.dumps(decoded_token.get_payload(), indent=2, default=str))
    print()

    print(f"Has consent: {decoded_token.has_consent()}")
    print(f"Consent scope: {decoded_token.get_consent_scope()}")
    print(f"Is expired: {decoded_token.is_expired()}")
    print()

    # Create token without consent
    token_no_consent = manager.create_token(
        user_id="user_67890",
        claims={"role": "guest"}
    )

    decoded_no_consent = manager.verify_token(token_no_consent)
    print(f"Token without consent - has consent: {decoded_no_consent.has_consent()}")
