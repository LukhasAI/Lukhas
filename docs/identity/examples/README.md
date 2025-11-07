# WebAuthn Examples

Complete, runnable examples of WebAuthn registration and authentication flows for LUKHAS AI.

**Framework**: Constellation Framework - Identity ⚛️ pillar
**Specification**: W3C WebAuthn Level 2

## Contents

- `webauthn_registration.py` - Complete Python backend implementation of registration flow
- `webauthn_authentication.py` - Complete Python backend implementation of authentication flow
- `webauthn_frontend.ts` - Complete TypeScript frontend implementation of both flows
- `README.md` - This file

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 14+ (for TypeScript/frontend)
- Modern browser with WebAuthn support (Chrome 67+, Firefox 60+, Safari 13+, Edge 18+)
- HTTPS or localhost (WebAuthn requires HTTPS in production)

### Backend Setup

#### 1. Install Python Dependencies

```bash
pip install fastapi uvicorn webauthn python-jose pydantic
```

#### 2. Run Registration Service

```bash
cd docs/identity/examples
python webauthn_registration.py
```

This starts a FastAPI server on `http://localhost:5000` with these endpoints:
- `POST /api/auth/webauthn/register/begin` - Start registration
- `POST /api/auth/webauthn/register/complete` - Complete registration
- `GET /api/auth/webauthn/credentials` - List credentials
- `DELETE /api/auth/webauthn/credentials/{credential_id}` - Delete credential

#### 3. Run Authentication Service (in another terminal)

```bash
python webauthn_authentication.py
```

This starts a FastAPI server with these endpoints:
- `POST /api/auth/webauthn/authenticate/begin` - Start authentication
- `POST /api/auth/webauthn/authenticate/complete` - Complete authentication
- `GET /api/auth/webauthn/credentials` - List credentials
- `DELETE /api/auth/webauthn/credentials/{credential_id}` - Revoke credential

### Frontend Setup

#### 1. Copy TypeScript Files

```bash
# Copy webauthn_frontend.ts to your frontend project
cp webauthn_frontend.ts /path/to/your/frontend/src/
```

#### 2. Use in React Component

```typescript
import {
    handleRegistration,
    handleAuthentication,
    isWebAuthnSupported
} from './webauthn_frontend';

// Check if WebAuthn is supported
if (isWebAuthnSupported()) {
    console.log('WebAuthn is supported!');
}

// Registration
await handleRegistration(
    userId='user123',
    username='user@example.com',
    displayName='John Doe',
    deviceName='Security Key'
);

// Authentication
const result = await handleAuthentication('user@example.com');
console.log('Session token:', result.session_token);
```

#### 3. Use with HTML/Vanilla JavaScript

```html
<script src="webauthn_frontend.ts"></script>

<button onclick="handleRegistration('user123', 'user@example.com', 'John', 'My Key')">
    Register
</button>

<button onclick="handleAuthentication('user@example.com')">
    Sign In
</button>
```

## Testing the Examples

### 1. Test Registration Flow

```bash
# Terminal 1: Start registration service
python webauthn_registration.py

# Terminal 2: Make registration request
curl -X POST http://localhost:5000/api/auth/webauthn/register/begin \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "username": "user@example.com",
    "display_name": "Test User"
  }'

# Response will contain registration options (challenge, etc)
# In browser, call: navigator.credentials.create(options)
# Then send result to: POST /api/auth/webauthn/register/complete
```

### 2. Test Authentication Flow

```bash
# Terminal 1: Start authentication service
python webauthn_authentication.py

# Terminal 2: Make authentication request
curl -X POST http://localhost:5000/api/auth/webauthn/authenticate/begin \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com"}'

# Response will contain authentication options (challenge, etc)
# In browser, call: navigator.credentials.get(options)
# Then send result to: POST /api/auth/webauthn/authenticate/complete
```

### 3. Test with Simulator

For testing without a physical authenticator:

```bash
# Use Chrome WebAuthn Simulator extension
# 1. Install from Chrome Web Store: "WebAuthn Testing"
# 2. Open browser DevTools (F12)
# 3. Create test authenticators
# 4. Run registration/authentication flows
```

Or use the official WebAuthn.io testing site:
- https://webauthn.io/ - Test any WebAuthn implementation
- https://webauthn.me/ - Test with your actual authenticators

## Environment Configuration

### Change RP ID and Origin

Edit the configuration variables in each Python file:

**webauthn_registration.py**:
```python
RP_ID = "example.com"              # Your domain
RP_NAME = "My Application"         # Your app name
ORIGIN = "https://example.com"     # Your HTTPS domain
TIMEOUT_MS = 60000                 # 60 seconds
```

**webauthn_authentication.py**:
```python
RP_ID = "example.com"
ORIGIN = "https://example.com"
TIMEOUT_MS = 60000
```

### Change Supported Algorithms

Edit the `pub_key_cred_params` in `generate_registration_options()`:

```python
pub_key_cred_params: List[PublicKeyCredentialParameters] = [
    {"type": "public-key", "alg": -7},     # ES256 (Recommended)
    {"type": "public-key", "alg": -257},   # RS256 (Fallback)
    {"type": "public-key", "alg": -8},     # EdDSA (Fallback)
]
```

## Browser Support Testing

### Chrome / Edge / Brave
- Full WebAuthn Level 2 support
- Platform authenticators (Windows Hello)
- Security keys (USB, NFC, BLE, hybrid)

**Test**:
```bash
# Open DevTools > Console
isWebAuthnSupported()  # Should return true
```

### Firefox
- Full WebAuthn Level 2 support
- Security keys (USB, NFC)
- Note: Platform authenticators vary by OS

**Note**: Some algorithms may not be supported. Provide fallback algorithms:
```python
pub_key_cred_params = [
    {"type": "public-key", "alg": -7},     # Try ES256
    {"type": "public-key", "alg": -257},   # Fallback to RS256
]
```

### Safari (macOS/iOS)
- Full WebAuthn support (13+)
- Touch ID and Face ID
- Security keys (requires iOS 14.5+)

**Test on macOS**:
```bash
# Safari 13+ on macOS 10.15+
# Visit http://localhost:5000
# Use Touch ID for registration/authentication
```

### Mobile Browsers
- Chrome Android: Full support (90+)
- Firefox Android: Full support (68+)
- Safari iOS: Full support (14.5+)
- Samsung Internet: Full support (14+)

## HTTPS Requirement

WebAuthn requires HTTPS in production (except for localhost/127.0.0.1).

### Development with HTTPS

**Option 1: Self-signed certificate**
```bash
# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use with FastAPI
uvicorn webauthn_registration:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

**Option 2: mkcert**
```bash
# Install: https://github.com/FiloSottile/mkcert
mkcert localhost 127.0.0.1

# This creates localhost.pem and localhost-key.pem
uvicorn webauthn_registration:app --ssl-keyfile=localhost-key.pem --ssl-certfile=localhost.pem
```

**Option 3: ngrok reverse proxy**
```bash
# Install: https://ngrok.com
ngrok http 5000

# This provides HTTPS tunnel: https://abc123.ngrok.io
# Update ORIGIN in examples
```

## Troubleshooting

### "NotAllowedError: The operation either timed out or was not allowed"

**Causes**:
- User cancelled the operation
- Authenticator doesn't support the requested algorithm
- Timeout expired before user completed operation
- HTTPS certificate issues

**Solutions**:
1. Ensure HTTPS is used (or localhost for testing)
2. Provide fallback algorithms
3. Increase timeout
4. Check authenticator compatibility

### "InvalidStateError: An attempt was made to use an object that is not, or is no longer, usable"

**Causes**:
- Credential already exists for this user on this authenticator
- Trying to re-register with same device

**Solutions**:
1. Always populate `excludeCredentials` with existing credentials
2. Use different security key or platform authenticator
3. Delete and re-register if needed

### "SecurityError: The operation is insecure and should not be performed"

**Causes**:
- HTTPS not used (except localhost)
- Invalid TLS certificate
- Cross-origin request issues

**Solutions**:
1. Use HTTPS in production
2. Use `http://localhost` for development
3. Check certificate validity
4. Configure CORS properly

### Registration works but authentication fails

**Causes**:
- Different RP_ID between registration and authentication
- Sign counter validation failed
- Credential deleted or expired

**Solutions**:
1. Ensure RP_ID matches exactly
2. Check that credential still exists: `GET /api/auth/webauthn/credentials?user_id=...`
3. Verify sign counter logic in backend

### "TypeError: Cannot read property 'create' of undefined"

**Cause**:
- Browser doesn't support WebAuthn

**Solution**:
```typescript
if (!isWebAuthnSupported()) {
    console.log('This browser does not support WebAuthn');
    // Fall back to password or other auth method
}
```

## Integration with LUKHAS

To use these examples with LUKHAS AI:

### 1. Add LUKHAS Imports

```python
from lukhas.identity.webauthn_credential import WebAuthnCredentialStore
from lukhas_website.lukhas.identity.webauthn_types import (
    CredentialCreationOptions,
    PublicKeyCredentialCreation,
    CredentialRequestOptions,
    PublicKeyCredentialAssertion
)
```

### 2. Replace Credential Store

Instead of in-memory storage, use LUKHAS credential store or your database:

```python
# Instead of:
credential_store = WebAuthnCredentialStore()

# Use LUKHAS or your database:
from lukhas.identity.webauthn_credential import WebAuthnCredentialStore
credential_store = WebAuthnCredentialStore()

# Or implement your own:
class MyCredentialStore:
    def store_credential(self, user_id: str, credential: dict) -> None:
        # Store in database
        pass

    def get_credential(self, credential_id: str) -> dict:
        # Retrieve from database
        pass

    # ... etc
```

### 3. Integrate with LUKHAS API

Add these endpoints to your LUKHAS API module:

```python
# lukhas/api/identity.py
from lukhas.identity.webauthn_credential import WebAuthnCredentialStore

credential_store = WebAuthnCredentialStore()

@app.post("/api/auth/webauthn/register/begin")
async def register_begin(...):
    # Your implementation here
    pass

@app.post("/api/auth/webauthn/register/complete")
async def register_complete(...):
    # Your implementation here
    pass

# ... etc
```

## Production Deployment

### Security Checklist

- [ ] Use HTTPS with valid certificate
- [ ] Store credentials in encrypted database
- [ ] Use cryptographically secure challenge generation
- [ ] Implement rate limiting on registration/authentication endpoints
- [ ] Monitor sign counter validation for replay attacks
- [ ] Store audit logs of registration/authentication events
- [ ] Implement credential expiration if needed
- [ ] Use hardware security module (HSM) for key storage if possible
- [ ] Implement backup codes for account recovery
- [ ] Test with real authenticators before launch

### Database Schema

**credentials table**:
```sql
CREATE TABLE webauthn_credentials (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    credential_id VARCHAR(255) NOT NULL UNIQUE,
    public_key TEXT NOT NULL,
    counter INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    device_name VARCHAR(255),
    aaguid VARCHAR(36),
    transports JSON,
    backup_eligible BOOLEAN DEFAULT FALSE,
    backup_state BOOLEAN DEFAULT FALSE,
    metadata JSON,
    INDEX (user_id),
    INDEX (credential_id)
);
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/webauthn/register/begin")
@limiter.limit("5/minute")
async def register_begin(request: Request, ...):
    # Registration limited to 5 requests per minute per IP
    pass
```

### Monitoring

Log all registration and authentication events:

```python
import logging

logger = logging.getLogger(__name__)

def log_registration_event(user_id: str, device_name: str, success: bool):
    logger.info(
        f"WebAuthn registration",
        extra={
            "event": "webauthn_registration",
            "user_id": user_id,
            "device_name": device_name,
            "success": success
        }
    )

def log_authentication_event(user_id: str, success: bool, error: str = None):
    logger.info(
        f"WebAuthn authentication",
        extra={
            "event": "webauthn_authentication",
            "user_id": user_id,
            "success": success,
            "error": error
        }
    )
```

## Additional Resources

- **W3C WebAuthn Level 2**: https://www.w3.org/TR/webauthn-2/
- **WebAuthn.io**: https://webauthn.io/ - Test your implementation
- **FIDO2 Specifications**: https://fidoalliance.org/
- **Yubico Developer Guide**: https://developers.yubico.com/WebAuthn/
- **MDN WebAuthn**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API
- **OWASP Authentication Cheat Sheet**: https://cheatsheetseries.owasp.org/

## License

These examples are part of LUKHAS AI and follow the same license as the main repository.

---

**Last Updated**: November 2, 2024
**LUKHAS AI - Constellation Framework - Identity ⚛️ Pillar**
