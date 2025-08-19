# 🔐 LUKHAS AI Authentication Protocol Documentation
*Current Login, Onboarding, and User ID Assignment System*

⚛️🧠🛡️ **Trinity Framework Authentication** | **Tier-Based Access Control** | **Symbolic Identity System**

---

## 📚 Table of Contents
- [Current Authentication Flow](#-current-authentication-flow)
- [User Onboarding Process](#-user-onboarding-process)
- [User ID Assignment](#-user-id-assignment)
- [Access Tier System](#-access-tier-system)
- [Token Structure](#-token-structure)
- [Security Validation](#-security-validation)
- [Frontend Integration](#-frontend-integration)
- [API Endpoints](#-api-endpoints)

---

## 🔑 Current Authentication Flow

### **Login Process (`identity/login.py`)**

```python
def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Current login implementation:
    1. Validates password strength
    2. Validates email format
    3. Generates user_id from email
    4. Creates authentication token
    5. Returns user session data
    """
    
    # Password validation requirements:
    # - Minimum 8 characters
    # - At least 1 uppercase letter
    # - At least 1 lowercase letter
    # - At least 1 number
    # - At least 1 special character
    # - No common weak patterns
    
    # User ID generation:
    user_id = email.split("@")[0].replace(".", "_").lower()
    
    # Token creation with metadata:
    metadata = {
        "email": email,
        "consent": True,
        "trinity_score": 0.5,
        "drift_score": 0.0,
        "password_validated": True,
        "security_level": "enhanced" if CRYPTO_AVAILABLE else "basic"
    }
    
    # Returns:
    {
        "success": True,
        "token": "LUKHAS-T2-<random>",
        "user_id": user_id,
        "tier": "T2",
        "glyphs": ["⚛️", "✨"]  # Identity glyphs
    }
```

### **Registration Process (`identity/registration.py`)**

```python
def register_user(email: str, password: str, requested_tier: Optional[str] = None):
    """
    Current registration implementation:
    1. Validates email format
    2. Generates user_id from email
    3. Assigns access tier (default T2)
    4. Creates initial user metadata
    5. Generates authentication token
    """
    
    # User ID generation:
    user_id = email.split("@")[0].replace(".", "_").lower()
    
    # Initial metadata:
    metadata = {
        "email": email,
        "consent": True,
        "trinity_score": 0.3,  # Starting score
        "drift_score": 0.0,
        "cultural_profile": "universal",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Default tier assignment:
    tier = AccessTier.T2  # Creator level by default
```

---

## 🎭 User Onboarding Process

### **Web Interface Onboarding (`lukhas_website/components/proteus-onboarding.tsx`)**

The frontend provides a 5-step onboarding flow for new users:

1. **Welcome Screen**
   - Introduction to PR0T3US consciousness visualization
   - Explains quantum-inspired and bio-adaptive features

2. **Microphone Access**
   - Request permission for voice-reactive features
   - Provides voice command examples:
     - "Show me consciousness"
     - "Transform to cube"
     - "Increase energy"

3. **Interactive Controls**
   - Mouse interaction tutorial:
     - Left Click + Drag: Rotate view
     - Right Click + Drag: Pan camera
     - Scroll: Zoom
     - Double Click: Reset view

4. **Consciousness States**
   - Explains visual feedback for different states:
     - Calm: Smooth, flowing particles (blue)
     - Focused: Organized patterns (purple)
     - Energetic: Rapid movement (orange)

5. **Configuration**
   - API integration settings:
     - OpenAI GPT-4
     - Anthropic Claude
     - Google Gemini
     - Local Models
   - Settings persistence (localStorage)

### **Onboarding State Management**

```typescript
interface ProteusOnboardingProps {
  onComplete: () => void
  isFirstVisit?: boolean  // Tracks if user is new
}

// Progress tracking:
- Progress bar shows completion percentage
- Step indicators for navigation
- Skip option for returning users
- Settings saved locally for persistence
```

---

## 🆔 User ID Assignment

### **Current Implementation**

```python
# User ID Generation Logic (identity_core.py):

def generate_user_id(email: str) -> str:
    """
    Current user ID generation:
    - Takes email prefix (before @)
    - Replaces dots with underscores
    - Converts to lowercase
    
    Example:
    john.doe@example.com -> john_doe
    """
    user_id = email.split("@")[0].replace(".", "_").lower()
    return user_id
```

### **User ID Characteristics**
- **Format**: `lowercase_with_underscores`
- **Source**: Email prefix
- **Uniqueness**: Not enforced (TODO)
- **Storage**: In-memory token store (development)
- **Production TODO**: Implement proper database storage

---

## 🎖️ Access Tier System

### **Five-Tier Hierarchy (`identity/identity_core.py`)**

```python
class AccessTier(Enum):
    T1 = "T1"  # Basic - Public viewing only
    T2 = "T2"  # Creator - Content creation + API access
    T3 = "T3"  # Advanced - Consciousness, emotion, dream modules
    T4 = "T4"  # Quantum - Full system except admin
    T5 = "T5"  # Admin - Complete system access + Guardian
```

### **Tier Permissions Matrix**

| Permission | T1 | T2 | T3 | T4 | T5 |
|------------|----|----|----|----|-----|
| View Public | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create Content | ❌ | ✅ | ✅ | ✅ | ✅ |
| API Access | ❌ | ✅ | ✅ | ✅ | ✅ |
| Consciousness | ❌ | ❌ | ✅ | ✅ | ✅ |
| Emotion | ❌ | ❌ | ✅ | ✅ | ✅ |
| Dream | ❌ | ❌ | ✅ | ✅ | ✅ |
| Quantum | ❌ | ❌ | ❌ | ✅ | ✅ |
| Guardian | ❌ | ❌ | ❌ | ❌ | ✅ |
| Admin | ❌ | ❌ | ❌ | ❌ | ✅ |

### **Tier Glyphs (Visual Indicators)**

```python
TIER_GLYPHS = {
    T1: ["⚛️"],                           # Identity only
    T2: ["⚛️", "✨"],                     # + Creation
    T3: ["⚛️", "🧠", "💭"],              # + Consciousness
    T4: ["⚛️", "🧠", "💭", "🔮"],        # + Quantum
    T5: ["⚛️", "🧠", "💭", "🔮", "🛡️"]  # + Guardian
}
```

---

## 🎫 Token Structure

### **Token Format**
```
LUKHAS-<TIER>-<RANDOM_STRING>
```

### **Example Tokens**
- `LUKHAS-T2-a3b5c7d9e1f3g5h7`
- `LUKHAS-T5-x9y8z7w6v5u4t3s2`

### **Token Metadata**
```python
{
    "user_id": "john_doe",
    "tier": "T2",
    "email": "john.doe@example.com",
    "created_at": "2025-08-19T10:30:00Z",
    "expires_at": "2025-08-20T10:30:00Z",  # 24hr expiry
    "consent": True,
    "trinity_score": 0.5,
    "drift_score": 0.0,
    "glyphs": ["⚛️", "✨"],
    "permissions": {...}
}
```

---

## 🛡️ Security Validation

### **Password Requirements**
```python
def validate_password(password: str):
    """
    Requirements:
    - Minimum 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains number
    - Contains special character
    - No weak patterns (password, 123456, etc.)
    """
```

### **Email Validation**
```python
def validate_email(email: str):
    """
    Requirements:
    - Contains @ symbol
    - Contains domain (.)
    - Valid format: user@domain.com
    """
```

### **Token Validation**
```python
def validate_symbolic_token(token: str):
    """
    Validation steps:
    1. Check token format (LUKHAS-TIER-RANDOM)
    2. Validate tier exists
    3. Check token store
    4. Verify expiration
    5. Validate symbolic integrity
    6. Alert Guardian on breach
    """
```

---

## 💻 Frontend Integration

### **Login Component Structure**
```typescript
// Expected login flow:
1. User enters email/password
2. Frontend validates input format
3. POST to /api/auth/login
4. Receive token and user data
5. Store token in localStorage/sessionStorage
6. Redirect to dashboard

// Session management:
- Token stored in browser storage
- Auto-refresh before expiry
- Logout clears all session data
```

### **Protected Routes**
```typescript
// Route protection based on tier:
if (userTier < requiredTier) {
  redirect('/upgrade')
}

// API calls include token:
headers: {
  'Authorization': `Bearer ${token}`,
  'X-LUKHAS-Tier': userTier
}
```

---

## 🔌 API Endpoints

### **Authentication Endpoints**

```python
# Login
POST /api/auth/login
Body: { "email": "user@example.com", "password": "SecurePass123!" }
Response: { "token": "LUKHAS-T2-xxx", "user_id": "user", "tier": "T2" }

# Register
POST /api/auth/register
Body: { "email": "user@example.com", "password": "SecurePass123!", "tier": "T2" }
Response: { "token": "LUKHAS-T2-xxx", "user_id": "user", "success": true }

# Logout
POST /api/auth/logout
Headers: { "Authorization": "Bearer LUKHAS-T2-xxx" }
Response: { "success": true }

# Validate Token
GET /api/auth/validate
Headers: { "Authorization": "Bearer LUKHAS-T2-xxx" }
Response: { "valid": true, "tier": "T2", "user_id": "user" }
```

---

## 🚧 Current Limitations & TODOs

### **Security Improvements Needed**
- [ ] Implement proper password hashing (bcrypt/argon2)
- [ ] Add rate limiting for login attempts
- [ ] Implement 2FA/MFA support
- [ ] Add OAuth providers (Google, GitHub)
- [ ] Implement WebAuthn/Passkeys

### **Storage & Persistence**
- [ ] Replace in-memory token store with Redis/database
- [ ] Implement user profile storage
- [ ] Add session management
- [ ] Create audit trail for authentication events

### **User Management**
- [ ] Implement unique user ID validation
- [ ] Add user profile management
- [ ] Create tier upgrade/downgrade system
- [ ] Implement user deletion/GDPR compliance

### **Token Management**
- [ ] Add refresh token mechanism
- [ ] Implement token rotation
- [ ] Add device-specific tokens
- [ ] Create token revocation list

---

## 🔄 Migration Path

### **Recommended Improvements**

1. **Database Integration**
   ```python
   # Add PostgreSQL/MongoDB for user storage
   users_collection = {
       "_id": "unique_user_id",
       "email": "user@example.com",
       "password_hash": "hashed_password",
       "tier": "T2",
       "created_at": datetime,
       "metadata": {...}
   }
   ```

2. **JWT Implementation**
   ```python
   # Replace custom tokens with JWT
   import jwt
   
   token = jwt.encode({
       "user_id": user_id,
       "tier": tier,
       "exp": expiration
   }, SECRET_KEY, algorithm="HS256")
   ```

3. **OAuth Integration**
   ```python
   # Add social login providers
   from authlib.integrations import oauth2
   
   oauth.register(
       name='google',
       client_id=GOOGLE_CLIENT_ID,
       client_secret=GOOGLE_CLIENT_SECRET,
       ...
   )
   ```

---

*Last Updated: 2025-08-19 | Version: 1.0.0 | LUKHAS AI Authentication System*