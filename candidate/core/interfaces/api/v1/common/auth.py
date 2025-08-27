# ΛTAG: api_auth

import hashlib
import hmac
import os
import secrets
import time
from typing import Dict, Optional

from fastapi import Header, HTTPException, Request
import structlog

# Initialize ΛTRACE logger for security events
logger = structlog.get_logger("ΛTRACE.api_auth")

# Security configuration
API_KEY_MIN_LENGTH = 32
API_KEY_MAX_LENGTH = 128
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
HMAC_SECRET = os.getenv("LUKHAS_ID_SECRET", "default-unsafe-secret-change-in-production")

# Rate limiting storage (in production, use Redis)
_rate_limit_store: Dict[str, list] = {}


class SecurityValidationError(Exception):
    """Custom exception for security validation failures."""
    pass


def _validate_key_format(api_key: str) -> bool:
    """
    Validate API key format and structure.
    
    LUKHAS API keys follow the format: luk_<env>_<32-char-hex>
    Example: luk_prod_a1b2c3d4e5f6789012345678901234567890abcd
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Check length bounds
    if len(api_key) < API_KEY_MIN_LENGTH or len(api_key) > API_KEY_MAX_LENGTH:
        return False
    
    # Check LUKHAS prefix format
    if not api_key.startswith("luk_"):
        return False
    
    parts = api_key.split("_")
    if len(parts) != 3:
        return False
    
    prefix, env, key_part = parts
    
    # Validate environment
    if env not in ["dev", "test", "prod", "staging"]:
        return False
    
    # Validate key part (should be hex)
    if len(key_part) < 32:
        return False
    
    try:
        int(key_part, 16)  # Validate hex format
    except ValueError:
        return False
    
    return True


def _verify_key_signature(api_key: str) -> bool:
    """
    Verify API key cryptographic signature using HMAC.
    This prevents key forgery and ensures authenticity.
    """
    try:
        # Extract components
        parts = api_key.split("_")
        if len(parts) != 3:
            return False
        
        prefix, env, key_part = parts
        
        # For generated keys, the signature is embedded in the key_part
        # Key format: base_key (32 chars) + signature (16 chars) = 48 chars total
        if len(key_part) < 48:
            return False
        
        base_key = key_part[:32]  # First 32 chars
        provided_sig = key_part[32:48]  # Next 16 chars as signature
        
        # Create expected signature from base components
        message = f"{prefix}_{env}_{base_key}"
        expected_sig = hmac.new(
            HMAC_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return hmac.compare_digest(expected_sig, provided_sig)
    except Exception as e:
        logger.warning("Key signature verification failed", error=str(e))
        return False


def _check_rate_limit(api_key: str) -> bool:
    """
    Implement rate limiting to prevent API abuse.
    """
    current_time = time.time()
    
    if api_key not in _rate_limit_store:
        _rate_limit_store[api_key] = []
    
    # Clean old requests outside the window
    _rate_limit_store[api_key] = [
        req_time for req_time in _rate_limit_store[api_key]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check if under limit
    if len(_rate_limit_store[api_key]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    _rate_limit_store[api_key].append(current_time)
    return True


def _audit_auth_attempt(api_key: str, success: bool, request: Optional[Request] = None) -> None:
    """
    Log authentication attempts for security monitoring.
    """
    # Mask key for logging (show only first 8 chars)
    masked_key = api_key[:12] + "*" * (len(api_key) - 12) if len(api_key) > 12 else "*" * len(api_key)
    
    log_data = {
        "masked_api_key": masked_key,
        "success": success,
        "timestamp": time.time(),
        "ip_address": getattr(request, "client", {}).get("host") if request else "unknown"
    }
    
    if success:
        logger.info("API key authentication successful", **log_data)
    else:
        logger.warning("API key authentication failed", **log_data)


async def verify_api_key(x_api_key: str = Header(...), request: Request = None) -> None:
    """
    Comprehensive API key verification with security checks.
    
    Implements:
    - Format validation
    - Cryptographic signature verification  
    - Rate limiting
    - Audit logging
    - Input sanitization
    """
    try:
        # Input validation
        if not x_api_key:
            _audit_auth_attempt("", False, request)
            raise HTTPException(status_code=401, detail="Missing API Key")
        
        # Sanitize input
        api_key = x_api_key.strip()
        
        # Format validation
        if not _validate_key_format(api_key):
            _audit_auth_attempt(api_key, False, request)
            raise HTTPException(status_code=401, detail="Invalid API Key Format")
        
        # Rate limiting check
        if not _check_rate_limit(api_key):
            _audit_auth_attempt(api_key, False, request)
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Cryptographic verification
        if not _verify_key_signature(api_key):
            _audit_auth_attempt(api_key, False, request)
            raise HTTPException(status_code=401, detail="Invalid API Key")
        
        # Log successful authentication
        _audit_auth_attempt(api_key, True, request)
        
        logger.info("API key validation successful", 
                   key_prefix=api_key[:12],
                   client_ip=getattr(request, "client", {}).get("host") if request else "unknown")
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error("Unexpected error in API key validation", error=str(e))
        _audit_auth_attempt(api_key if 'api_key' in locals() else "", False, request)
        raise HTTPException(status_code=500, detail="Authentication service error")


def generate_api_key(environment: str = "dev") -> str:
    """
    Generate a new LUKHAS API key with cryptographic signature.
    
    Args:
        environment: The environment (dev, test, staging, prod)
    
    Returns:
        A properly formatted and signed API key
    """
    if environment not in ["dev", "test", "staging", "prod"]:
        raise ValueError("Invalid environment. Must be one of: dev, test, staging, prod")
    
    # Generate random key part (32 hex chars)
    key_base = secrets.token_hex(16)
    
    # Create message for signing
    message = f"luk_{environment}_{key_base}"
    
    # Generate signature
    signature = hmac.new(
        HMAC_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    
    # Combine into final key
    api_key = f"luk_{environment}_{key_base}{signature}"
    
    logger.info("Generated new API key", 
               environment=environment,
               key_prefix=api_key[:12])
    
    return api_key
