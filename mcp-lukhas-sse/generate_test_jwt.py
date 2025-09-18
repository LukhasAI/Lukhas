#!/usr/bin/env python3
"""Generate test JWT tokens for local development."""

import json
import time
from jose import jwt

def generate_test_jwt():
    """Generate a test JWT token for local development."""
    
    # Simple test signing secret (DO NOT use in production!)
    test_secret = "test-secret-key-for-local-development-only-do-not-use-in-production"
    
    # Test payload
    payload = {
        "iss": "https://test-issuer.local",
        "aud": "api://lukhas-mcp",
        "sub": "test-user-123",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour
        "scope": "read:files write:files"
    }
    
    # Generate JWT with symmetric key (easier for testing)
    token = jwt.encode(payload, test_secret, algorithm='HS256')
    
    return token, test_secret

def create_test_jwks():
    """Create test JWKS for local validation."""
    
    # For symmetric key testing, we'll just return a simple response
    # In real scenarios, this would be asymmetric keys
    jwks = {
        "keys": [
            {
                "kty": "oct",
                "use": "sig", 
                "kid": "test-key-1",
                "k": "dGVzdC1zZWNyZXQta2V5LWZvci1sb2NhbC1kZXZlbG9wbWVudC1vbmx5LWRvLW5vdC11c2UtaW4tcHJvZHVjdGlvbg"
            }
        ]
    }
    
    return jwks

if __name__ == "__main__":
    print("🧪 Local JWT Token Generator")
    print("=" * 40)
    
    # Generate test token
    token, _ = generate_test_jwt()
    
    print("✅ Test JWT Token:")
    print(token)
    print()
    
    print("🔧 Test this with your server:")
    print(f"curl -H 'Authorization: Bearer {token}' http://localhost:8080/sse/")
    print()
    
    print("⚠️  Note: This is for LOCAL TESTING ONLY!")
    print("   Do not use these keys in production!")
    
    # Save token to file for easy access
    with open("test-jwt-token.txt", "w") as f:
        f.write(token)
    
    print(f"💾 Token saved to: test-jwt-token.txt")