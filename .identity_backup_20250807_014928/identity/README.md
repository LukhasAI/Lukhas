# 🛡️ LUKHΛS Identity System (ΛiD)

Complete identity management system with Trinity Framework integration for secure, tier-based access control.

## 🌟 Features

- **User Registration** with email capture and consent logging
- **Secure Authentication** with token-based sessions
- **5-Tier Access Control** (T1-T5) with progressive permissions
- **Symbolic Tracking** with GLYPH-based user representation
- **GDPR Compliance** with consent logging and audit trails
- **Trinity Framework Integration** (⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian)

## 🚀 Quick Start

### Demo Account

A pre-configured demo account is available for testing:

```
Email: reviewer@openai.com
Password: demo_password
Tier: T5 (Full Guardian access)
```

### Basic Usage

```python
from identity import identity_router, get_current_user, AuthContext

# Add to your FastAPI app
app.include_router(identity_router)

# Protect a route
@app.get("/protected")
async def protected_route(user: AuthContext = Depends(get_current_user)):
    return {"user": user.email, "tier": user.tier}
```

## 📁 System Components

### Core Files

- **`user_db.py`** - User database with file-based storage
- **`registration.py`** - User registration endpoints
- **`login.py`** - Authentication and session management
- **`verify.py`** - Token verification and permissions
- **`middleware.py`** - Authentication middleware and decorators
- **`api.py`** - Combined API router

### Data Storage

- **`data/users.json`** - User database
- **`data/consent_log.jsonl`** - GDPR consent audit log

## 🔐 Authentication Tiers

### T1 - Observer
- **Glyphs**: ⚛️
- **Access**: Basic public content
- **Trinity Score**: 0.3

### T2 - Participant  
- **Glyphs**: ⚛️ 🔐
- **Access**: Content creation, basic API
- **Trinity Score**: 0.5

### T3 - Contributor
- **Glyphs**: ⚛️ 🔐 🧠
- **Access**: Consciousness, emotion, dream modules
- **Trinity Score**: 0.7

### T4 - Architect
- **Glyphs**: ⚛️ 🔐 🧠 🌍
- **Access**: Quantum processing, system design
- **Trinity Score**: 0.9

### T5 - Guardian
- **Glyphs**: 🛡️ ⚛️ 🧠
- **Access**: Full system control, admin tools
- **Trinity Score**: 1.0

## 🌐 API Endpoints

### Registration
- `POST /identity/register` - Register new user
- `GET /identity/register/check-email/{email}` - Check email availability
- `GET /identity/register/tiers` - Get tier information

### Authentication
- `POST /identity/login` - Login with email/password or token
- `POST /identity/logout` - Logout and invalidate token
- `GET /identity/profile` - Get current user profile

### Verification
- `POST /identity/verify` - Verify token and get permissions
- `GET /identity/verify/quick` - Quick token validation
- `GET /identity/verify/permissions/{resource}` - Check resource access

## 🛠️ Middleware & Decorators

### Dependencies

```python
# Get current user
user: AuthContext = Depends(get_current_user)

# Require specific tier
user: AuthContext = Depends(require_t3_or_above)
```

### Decorators

```python
# Require minimum tier
@require_tier("T3")
async def advanced_feature(user: AuthContext = Depends(get_current_user)):
    pass

# Require specific permission
@require_permission("can_use_quantum")
async def quantum_feature(user: AuthContext = Depends(get_current_user)):
    pass

# Require Trinity active
@require_trinity_active()
async def trinity_feature(user: AuthContext = Depends(get_current_user)):
    pass
```

## 📊 Permissions Matrix

| Permission | T1 | T2 | T3 | T4 | T5 |
|------------|----|----|----|----|-----|
| can_view_public | ✅ | ✅ | ✅ | ✅ | ✅ |
| can_create_content | ❌ | ✅ | ✅ | ✅ | ✅ |
| can_access_api | ❌ | ✅ | ✅ | ✅ | ✅ |
| can_use_consciousness | ❌ | ❌ | ✅ | ✅ | ✅ |
| can_use_emotion | ❌ | ❌ | ✅ | ✅ | ✅ |
| can_use_dream | ❌ | ❌ | ✅ | ✅ | ✅ |
| can_use_quantum | ❌ | ❌ | ❌ | ✅ | ✅ |
| can_access_guardian | ❌ | ❌ | ❌ | ❌ | ✅ |
| can_admin | ❌ | ❌ | ❌ | ❌ | ✅ |

## 🧪 Testing

Run the test script to verify the system:

```bash
cd identity
python3 test_identity.py
```

## 🔗 Integration Example

See `example_integration.py` for a complete FastAPI application with identity integration.

```bash
python3 example_integration.py
# Visit http://localhost:8000/docs for API documentation
```

## 🔒 Security Features

- **Password Hashing** - Secure password storage (SHA256 for demo, use bcrypt/argon2 in production)
- **Token-Based Auth** - Stateless authentication with secure tokens
- **Session Management** - Multiple active sessions per user
- **Audit Logging** - Complete consent and action tracking
- **GDPR Compliance** - Consent management and data protection

## 📝 Future Enhancements

- [ ] Database backend (PostgreSQL/MongoDB)
- [ ] Email verification
- [ ] Multi-factor authentication
- [ ] Biometric integration
- [ ] OAuth2/OIDC support
- [ ] Rate limiting
- [ ] Password reset flow
- [ ] Account recovery

## 🛡️ Trinity Framework

The identity system is fully integrated with the LUKHΛS Trinity Framework:

- **⚛️ Identity**: Core authentication and user management
- **🧠 Consciousness**: User state and awareness tracking
- **🛡️ Guardian**: Security validation and ethical oversight

---

**LUKHΛS Identity System v1.0.0** - Secure, Symbolic, Sovereign