# JWT Examples and Configuration

**Part of BATCH-COPILOT-2025-10-08-01**  
**TaskID**: ASSIST-LOW-EXAMPLES-JWT-q9r0s1t2

## JWT Configuration Examples

### Development Environment

```yaml
# config/jwt_dev.yaml
jwt:
  algorithm: "HS256"
  secret_key: "dev-secret-key-change-in-production"
  expiration: 3600  # 1 hour
  refresh_expiration: 604800  # 7 days
  issuer: "lukhas.ai"
  audience: "lukhas-api"
  
  # Token validation
  verify_signature: true
  verify_exp: true
  verify_nbf: true
  verify_iat: true
  require_exp: true
  require_iat: true
```

### Production Environment

```yaml
# config/jwt_prod.yaml
jwt:
  algorithm: "RS256"  # Asymmetric for production
  private_key_path: "/secure/keys/private.pem"
  public_key_path: "/secure/keys/public.pem"
  expiration: 900  # 15 minutes (shorter for security)
  refresh_expiration: 2592000  # 30 days
  issuer: "lukhas.ai"
  audience: "lukhas-api"
  
  # Enhanced validation
  verify_signature: true
  verify_exp: true
  verify_nbf: true
  verify_iat: true
  verify_iss: true
  verify_aud: true
  require_exp: true
  require_iat: true
  require_jti: true  # Unique token ID
  
  # Security
  leeway: 10  # 10 seconds clock skew tolerance
  blacklist_enabled: true
```

## Public Key Management

### Generating RSA Key Pair

```bash
# Generate private key
openssl genrsa -out private.pem 2048

# Generate public key
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

### Storing Keys Securely

```python
from pathlib import Path

# Load keys
private_key = Path("/secure/keys/private.pem").read_text()
public_key = Path("/secure/keys/public.pem").read_text()

# Configure JWT adapter
from candidate.bridge.api.jwt_adapter import JWTAdapter

jwt_adapter = JWTAdapter(
    algorithm="RS256",
    private_key=private_key,
    public_key=public_key
)
```

### Key Rotation

```python
# Rotate keys periodically (e.g., every 90 days)
from datetime import datetime, timedelta

class JWTKeyManager:
    def __init__(self):
        self.current_key = self.load_key("current")
        self.next_key = self.load_key("next")
        self.previous_key = self.load_key("previous")
    
    def rotate_keys(self):
        """Rotate keys: next → current → previous."""
        self.previous_key = self.current_key
        self.current_key = self.next_key
        self.next_key = self.generate_new_key()
        self.save_keys()
```

## Token Validation Examples

### Basic Token Validation

```python
from candidate.bridge.api.jwt_adapter import JWTAdapter

adapter = JWTAdapter(algorithm="HS256", secret="your-secret")

try:
    # Decode and validate token
    payload = adapter.verify(token)
    
    user_id = payload["user_id"]
    tier = payload["tier"]
    
    print(f"Valid token for user: {user_id} (tier: {tier})")
    
except jwt.ExpiredSignatureError:
    print("Token expired")
except jwt.InvalidTokenError as e:
    print(f"Invalid token: {e}")
```

### Advanced Validation with Claims

```python
# Validate specific claims
payload = adapter.verify(
    token,
    required_claims=["user_id", "tier", "lambda_id"],
    audience="lukhas-api",
    issuer="lukhas.ai"
)

# Check custom claims
if payload.get("tier") not in ["free", "pro", "enterprise"]:
    raise ValueError("Invalid tier")

if payload.get("lambda_id", "").startswith("λ_"):
    print(f"Lambda ID verified: {payload['lambda_id']}")
```

### Token Refresh Flow

```python
def refresh_access_token(refresh_token: str) -> dict:
    """Refresh access token using refresh token."""
    
    # Verify refresh token
    refresh_payload = adapter.verify(refresh_token)
    
    if refresh_payload.get("type") != "refresh":
        raise ValueError("Not a refresh token")
    
    # Issue new access token
    new_token = adapter.create_token(
        {
            "user_id": refresh_payload["user_id"],
            "tier": refresh_payload["tier"],
            "lambda_id": refresh_payload["lambda_id"],
            "type": "access"
        },
        expiration=900  # 15 minutes
    )
    
    return {
        "access_token": new_token,
        "expires_in": 900
    }
```

## Token Creation Examples

### Creating Access Tokens

```python
# Create standard access token
access_token = adapter.create_token(
    payload={
        "user_id": "user_123",
        "email": "user@example.com",
        "tier": "pro",
        "lambda_id": "λ_user_123",
        "roles": ["user", "api_consumer"]
    },
    expiration=3600  # 1 hour
)
```

### Creating Refresh Tokens

```python
# Create refresh token (longer expiration)
refresh_token = adapter.create_token(
    payload={
        "user_id": "user_123",
        "tier": "pro",
        "type": "refresh"
    },
    expiration=604800  # 7 days
)
```

### Creating Special-Purpose Tokens

```python
# Email verification token
verification_token = adapter.create_token(
    payload={
        "user_id": "user_123",
        "email": "user@example.com",
        "type": "email_verification",
        "purpose": "verify_email"
    },
    expiration=3600  # 1 hour, short expiration
)

# Password reset token
reset_token = adapter.create_token(
    payload={
        "user_id": "user_123",
        "type": "password_reset",
        "nonce": "unique_nonce_123"
    },
    expiration=1800  # 30 minutes
)
```

## Integration with ΛID System

```python
def create_authenticated_session(lambda_id: str, tier: str) -> dict:
    """Create authenticated session with Lambda ID."""
    
    access_token = adapter.create_token(
        payload={
            "lambda_id": lambda_id,
            "tier": tier,
            "consciousness_state": "active",
            "guardian_approved": True
        },
        expiration=900
    )
    
    refresh_token = adapter.create_token(
        payload={
            "lambda_id": lambda_id,
            "tier": tier,
            "type": "refresh"
        },
        expiration=2592000  # 30 days
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "lambda_id": lambda_id,
        "expires_in": 900
    }
```

## Middleware Integration

### FastAPI Middleware

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """FastAPI dependency for JWT verification."""
    
    token = credentials.credentials
    
    try:
        payload = adapter.verify(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Use in routes
@app.get("/protected")
async def protected_route(payload: dict = Depends(verify_jwt_token)):
    return {"user_id": payload["user_id"], "tier": payload["tier"]}
```

### Flask Middleware

```python
from flask import request, jsonify
from functools import wraps

def jwt_required(f):
    """Flask decorator for JWT authentication."""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(" ")[1]
        
        try:
            payload = adapter.verify(token)
            request.jwt_payload = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    
    return decorated_function

# Use in routes
@app.route("/protected")
@jwt_required
def protected_route():
    payload = request.jwt_payload
    return jsonify({"user_id": payload["user_id"]})
```

## Token Blacklisting

### Redis-Based Blacklist

```python
import redis

class JWTBlacklist:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def blacklist_token(self, jti: str, exp: int):
        """Add token to blacklist until expiration."""
        ttl = exp - int(datetime.utcnow().timestamp())
        if ttl > 0:
            self.redis.setex(f"blacklist:{jti}", ttl, "1")
    
    def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted."""
        return self.redis.exists(f"blacklist:{jti}") > 0

# Usage
blacklist = JWTBlacklist(redis_client)

# Blacklist on logout
def logout(token: str):
    payload = adapter.decode(token)  # Don't verify, just decode
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    if jti and exp:
        blacklist.blacklist_token(jti, exp)
```

## Testing

### Unit Tests

```python
import pytest
from datetime import datetime, timedelta

def test_jwt_creation_and_verification():
    """Test JWT creation and verification."""
    adapter = JWTAdapter(algorithm="HS256", secret="test-secret")
    
    payload = {"user_id": "test_123", "tier": "pro"}
    token = adapter.create_token(payload, expiration=3600)
    
    verified = adapter.verify(token)
    assert verified["user_id"] == "test_123"
    assert verified["tier"] == "pro"

def test_jwt_expiration():
    """Test JWT expiration handling."""
    adapter = JWTAdapter(algorithm="HS256", secret="test-secret")
    
    # Create token that expires in 1 second
    token = adapter.create_token({"user_id": "test"}, expiration=1)
    
    # Wait for expiration
    import time
    time.sleep(2)
    
    # Should raise ExpiredSignatureError
    with pytest.raises(jwt.ExpiredSignatureError):
        adapter.verify(token)
```

## Best Practices

1. **Use RS256 in production** (asymmetric signing)
2. **Short access token expiration** (15 minutes or less)
3. **Longer refresh token expiration** (30 days)
4. **Always verify signature** in production
5. **Implement token blacklisting** for logout
6. **Rotate keys periodically** (every 90 days)
7. **Use HTTPS only** for token transmission
8. **Store tokens securely** (httpOnly cookies or secure storage)
9. **Include jti claim** for unique token identification
10. **Monitor failed verification attempts**

---

**⚛️🧠🛡️ LUKHAS AI Platform - Secure JWT Authentication**
