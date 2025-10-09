"""
API Framework JWT Adapter

Provides JWT verification and token lifecycle management with ΛID integration.

Trinity Framework:
- ⚛️ Identity: ΛID-based JWT verification
- 🛡️ Guardian: Token validation, expiration enforcement
- 🧠 Consciousness: Audit trail integration

TaskIDs:
- TODO-HIGH-BRIDGE-ADAPTER-i3j4k5l6: JWT verification implementation

#TAG:bridge
#TAG:adapters
#TAG:authentication
#TAG:trinity
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import jwt
import hashlib
import json

logger = logging.getLogger(__name__)


class JWTAlgorithm(Enum):
    """Supported JWT algorithms"""
    RS256 = "RS256"  # RSA with SHA-256
    HS256 = "HS256"  # HMAC with SHA-256
    RS512 = "RS512"  # RSA with SHA-512
    ES256 = "ES256"  # ECDSA with SHA-256


class TokenType(Enum):
    """JWT token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"
    IDENTITY = "identity"  # ΛID tokens


@dataclass
class TokenClaims:
    """JWT token claims with ΛID integration"""
    
    # Standard JWT claims
    sub: str  # Subject (user/system ID)
    iss: str  # Issuer
    aud: Union[str, List[str]]  # Audience
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    nbf: Optional[int] = None  # Not before timestamp
    jti: Optional[str] = None  # JWT ID
    
    # ΛID-specific claims
    lambda_id: Optional[str] = None  # ΛID identifier
    identity_tier: Optional[str] = None  # alpha|beta|gamma|delta
    consciousness_level: Optional[str] = None  # Consciousness state
    
    # Custom claims
    token_type: str = "access"
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert claims to JWT payload dict"""
        payload = {
            "sub": self.sub,
            "iss": self.iss,
            "aud": self.aud,
            "exp": self.exp,
            "iat": self.iat,
            "token_type": self.token_type,
        }
        
        if self.nbf is not None:
            payload["nbf"] = self.nbf
        if self.jti:
            payload["jti"] = self.jti
        if self.lambda_id:
            payload["lambda_id"] = self.lambda_id
        if self.identity_tier:
            payload["identity_tier"] = self.identity_tier
        if self.consciousness_level:
            payload["consciousness_level"] = self.consciousness_level
        if self.scopes:
            payload["scopes"] = self.scopes
        if self.metadata:
            payload["metadata"] = self.metadata
            
        return payload
    
    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TokenClaims":
        """Create claims from JWT payload"""
        return cls(
            sub=payload["sub"],
            iss=payload["iss"],
            aud=payload["aud"],
            exp=payload["exp"],
            iat=payload["iat"],
            nbf=payload.get("nbf"),
            jti=payload.get("jti"),
            lambda_id=payload.get("lambda_id"),
            identity_tier=payload.get("identity_tier"),
            consciousness_level=payload.get("consciousness_level"),
            token_type=payload.get("token_type", "access"),
            scopes=payload.get("scopes", []),
            metadata=payload.get("metadata", {}),
        )


@dataclass
class TokenValidationResult:
    """Result of token validation"""
    valid: bool
    claims: Optional[TokenClaims] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Audit information
    validation_metadata: Dict[str, Any] = field(default_factory=dict)


class JWTAdapter:
    """
    JWT verification and token lifecycle management adapter
    
    Features:
    - RS256/HS256/RS512/ES256 algorithm support
    - Token validation with comprehensive checks
    - ΛID integration for identity tokens
    - Token lifecycle management (issue, refresh, revoke)
    - Audit trail for Guardian integration
    - Configurable expiration and leeway
    
    TaskID: TODO-HIGH-BRIDGE-ADAPTER-i3j4k5l6
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        algorithm: JWTAlgorithm = JWTAlgorithm.HS256,
        issuer: str = "lukhas-api",
        audience: Union[str, List[str]] = "lukhas-platform",
        access_token_ttl: int = 3600,  # 1 hour
        refresh_token_ttl: int = 86400 * 30,  # 30 days
        leeway: int = 60,  # Clock skew tolerance
        lambda_id_integration: bool = True,
    ):
        """
        Initialize JWT adapter
        
        Args:
            secret_key: HMAC secret key (for HS256)
            public_key: RSA/ECDSA public key (for RS256/ES256 verification)
            private_key: RSA/ECDSA private key (for RS256/ES256 signing)
            algorithm: JWT algorithm to use
            issuer: Token issuer identifier
            audience: Expected audience(s)
            access_token_ttl: Access token TTL in seconds
            refresh_token_ttl: Refresh token TTL in seconds
            leeway: Clock skew tolerance in seconds
            lambda_id_integration: Enable ΛID integration
        """
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl
        self.leeway = leeway
        self.lambda_id_integration = lambda_id_integration
        
        # Key management
        if algorithm == JWTAlgorithm.HS256:
            if not secret_key:
                raise ValueError("HS256 requires secret_key")
            self.secret_key = secret_key
            self.public_key = None
            self.private_key = None
        else:  # RS256, RS512, ES256
            if not public_key:
                raise ValueError(f"{algorithm.value} requires public_key")
            self.secret_key = None
            self.public_key = public_key
            self.private_key = private_key
        
        # Revocation tracking (in-memory, use Redis/DB in production)
        self._revoked_tokens: set = set()
        
        logger.info(
            f"JWTAdapter initialized: algorithm={algorithm.value}, "
            f"issuer={issuer}, lambda_id={lambda_id_integration}"
        )
    
    def create_token(
        self,
        subject: str,
        token_type: TokenType = TokenType.ACCESS,
        scopes: Optional[List[str]] = None,
        lambda_id: Optional[str] = None,
        identity_tier: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        custom_ttl: Optional[int] = None,
    ) -> str:
        """
        Create a new JWT token
        
        Args:
            subject: Token subject (user/system ID)
            token_type: Type of token
            scopes: Permission scopes
            lambda_id: ΛID identifier
            identity_tier: Identity tier (alpha|beta|gamma|delta)
            metadata: Additional metadata
            custom_ttl: Custom TTL in seconds (overrides defaults)
        
        Returns:
            Encoded JWT token string
        """
        now = datetime.utcnow()
        
        # Determine TTL
        if custom_ttl:
            ttl = custom_ttl
        elif token_type == TokenType.REFRESH:
            ttl = self.refresh_token_ttl
        else:
            ttl = self.access_token_ttl
        
        # Generate JTI (JWT ID)
        jti_data = f"{subject}:{token_type.value}:{now.timestamp()}"
        jti = hashlib.sha256(jti_data.encode()).hexdigest()[:16]
        
        # Create claims
        claims = TokenClaims(
            sub=subject,
            iss=self.issuer,
            aud=self.audience,
            exp=int((now + timedelta(seconds=ttl)).timestamp()),
            iat=int(now.timestamp()),
            nbf=int(now.timestamp()),
            jti=jti,
            lambda_id=lambda_id if self.lambda_id_integration else None,
            identity_tier=identity_tier,
            token_type=token_type.value,
            scopes=scopes or [],
            metadata=metadata or {},
        )
        
        # Encode token
        key = self.secret_key if self.algorithm == JWTAlgorithm.HS256 else self.private_key
        if not key:
            raise ValueError("Cannot create token: no signing key configured")
        
        token = jwt.encode(
            claims.to_dict(),
            key,
            algorithm=self.algorithm.value,
        )
        
        logger.info(
            f"Token created: type={token_type.value}, subject={subject}, "
            f"lambda_id={lambda_id}, expires={claims.exp}"
        )
        
        return token
    
    def verify_token(
        self,
        token: str,
        expected_type: Optional[TokenType] = None,
        required_scopes: Optional[List[str]] = None,
        verify_lambda_id: bool = True,
    ) -> TokenValidationResult:
        """
        Verify JWT token with comprehensive validation
        
        Args:
            token: JWT token string
            expected_type: Expected token type (if specified)
            required_scopes: Required permission scopes
            verify_lambda_id: Whether to verify ΛID presence
        
        Returns:
            TokenValidationResult with validation status and claims
        """
        try:
            # Decode token
            key = self.secret_key if self.algorithm == JWTAlgorithm.HS256 else self.public_key
            
            payload = jwt.decode(
                token,
                key,
                algorithms=[self.algorithm.value],
                issuer=self.issuer,
                audience=self.audience,
                leeway=self.leeway,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                }
            )
            
            # Parse claims
            claims = TokenClaims.from_dict(payload)
            
            # Check revocation
            if claims.jti and claims.jti in self._revoked_tokens:
                return TokenValidationResult(
                    valid=False,
                    error="Token has been revoked",
                    error_code="TOKEN_REVOKED",
                )
            
            # Verify token type
            if expected_type and claims.token_type != expected_type.value:
                return TokenValidationResult(
                    valid=False,
                    error=f"Invalid token type: expected {expected_type.value}, got {claims.token_type}",
                    error_code="INVALID_TOKEN_TYPE",
                )
            
            # Verify required scopes
            if required_scopes:
                missing_scopes = set(required_scopes) - set(claims.scopes)
                if missing_scopes:
                    return TokenValidationResult(
                        valid=False,
                        error=f"Missing required scopes: {missing_scopes}",
                        error_code="INSUFFICIENT_SCOPES",
                    )
            
            # Verify ΛID presence (if required)
            if verify_lambda_id and self.lambda_id_integration and not claims.lambda_id:
                logger.warning(f"Token missing ΛID: subject={claims.sub}")
            
            # Successful validation
            return TokenValidationResult(
                valid=True,
                claims=claims,
                validation_metadata={
                    "algorithm": self.algorithm.value,
                    "issuer": self.issuer,
                    "lambda_id_verified": bool(claims.lambda_id),
                }
            )
            
        except jwt.ExpiredSignatureError:
            return TokenValidationResult(
                valid=False,
                error="Token has expired",
                error_code="TOKEN_EXPIRED",
            )
        except jwt.InvalidAudienceError:
            return TokenValidationResult(
                valid=False,
                error="Invalid audience",
                error_code="INVALID_AUDIENCE",
            )
        except jwt.InvalidIssuerError:
            return TokenValidationResult(
                valid=False,
                error="Invalid issuer",
                error_code="INVALID_ISSUER",
            )
        except jwt.InvalidSignatureError:
            return TokenValidationResult(
                valid=False,
                error="Invalid signature",
                error_code="INVALID_SIGNATURE",
            )
        except jwt.DecodeError as e:
            return TokenValidationResult(
                valid=False,
                error=f"Token decode error: {str(e)}",
                error_code="DECODE_ERROR",
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}", exc_info=True)
            return TokenValidationResult(
                valid=False,
                error=f"Verification error: {str(e)}",
                error_code="VERIFICATION_ERROR",
            )
    
    def refresh_token(
        self,
        refresh_token: str,
        new_scopes: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token: Valid refresh token
            new_scopes: Updated scopes (optional)
        
        Returns:
            New access token, or None if refresh failed
        """
        # Verify refresh token
        result = self.verify_token(
            refresh_token,
            expected_type=TokenType.REFRESH,
        )
        
        if not result.valid or not result.claims:
            logger.warning(f"Token refresh failed: {result.error}")
            return None
        
        # Create new access token
        access_token = self.create_token(
            subject=result.claims.sub,
            token_type=TokenType.ACCESS,
            scopes=new_scopes or result.claims.scopes,
            lambda_id=result.claims.lambda_id,
            identity_tier=result.claims.identity_tier,
            metadata=result.claims.metadata,
        )
        
        logger.info(f"Token refreshed: subject={result.claims.sub}")
        return access_token
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (add to revocation list)
        
        Args:
            token: Token to revoke
        
        Returns:
            True if successfully revoked
        """
        try:
            # Decode without verification (to get JTI)
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
            )
            
            jti = payload.get("jti")
            if not jti:
                logger.warning("Token missing JTI, cannot revoke")
                return False
            
            self._revoked_tokens.add(jti)
            logger.info(f"Token revoked: jti={jti}")
            return True
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def decode_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging/logging)
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload dict, or None if decode fails
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
            )
            return payload
        except Exception as e:
            logger.error(f"Token decode failed: {e}")
            return None
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get token information without full verification
        
        Args:
            token: JWT token string
        
        Returns:
            Dict with token metadata
        """
        payload = self.decode_without_verification(token)
        if not payload:
            return {"error": "Invalid token format"}
        
        exp = payload.get("exp")
        now = datetime.utcnow().timestamp()
        
        return {
            "subject": payload.get("sub"),
            "issuer": payload.get("iss"),
            "audience": payload.get("aud"),
            "token_type": payload.get("token_type"),
            "lambda_id": payload.get("lambda_id"),
            "identity_tier": payload.get("identity_tier"),
            "scopes": payload.get("scopes", []),
            "issued_at": datetime.fromtimestamp(payload.get("iat", 0)).isoformat() if payload.get("iat") else None,
            "expires_at": datetime.fromtimestamp(exp).isoformat() if exp else None,
            "expired": exp < now if exp else None,
            "jti": payload.get("jti"),
        }


# Convenience functions for common patterns

def create_identity_token(
    adapter: JWTAdapter,
    lambda_id: str,
    identity_tier: str,
    scopes: Optional[List[str]] = None,
) -> str:
    """
    Create ΛID-based identity token
    
    Args:
        adapter: JWTAdapter instance
        lambda_id: ΛID identifier
        identity_tier: Identity tier (alpha|beta|gamma|delta)
        scopes: Permission scopes
    
    Returns:
        Identity token
    """
    return adapter.create_token(
        subject=lambda_id,
        token_type=TokenType.IDENTITY,
        lambda_id=lambda_id,
        identity_tier=identity_tier,
        scopes=scopes or ["identity:read"],
    )


def verify_identity_token(
    adapter: JWTAdapter,
    token: str,
    required_tier: Optional[str] = None,
) -> TokenValidationResult:
    """
    Verify ΛID identity token
    
    Args:
        adapter: JWTAdapter instance
        token: Identity token
        required_tier: Required minimum tier (if specified)
    
    Returns:
        TokenValidationResult
    """
    result = adapter.verify_token(
        token,
        expected_type=TokenType.IDENTITY,
        verify_lambda_id=True,
    )
    
    # Verify tier if specified
    if result.valid and required_tier and result.claims:
        tier_order = ["alpha", "beta", "gamma", "delta"]
        user_tier_idx = tier_order.index(result.claims.identity_tier) if result.claims.identity_tier in tier_order else -1
        required_tier_idx = tier_order.index(required_tier) if required_tier in tier_order else -1
        
        if user_tier_idx < required_tier_idx:
            result.valid = False
            result.error = f"Insufficient identity tier: required {required_tier}, got {result.claims.identity_tier}"
            result.error_code = "INSUFFICIENT_TIER"
    
    return result
