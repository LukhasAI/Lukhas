# LUKHΛS LucasID: Enterprise & OAuth User ID Examples

## 🔑 What is LucasID (ΛID)?

LucasID (written as **ΛID**) is the **canonical user handle** in the LUKHΛS ecosystem. All other identifiers (Google, Apple, enterprise SSO, phone, etc.) are *federated aliases* that can be linked to a single ΛID. Users may choose parts of their ΛID during signup, while enterprises can reserve **namespaces** (e.g., `openai/`, `stanford/`).

**Design goals**
- One canonical ΛID per person (stable handle)
- Optional **provider alias** (Google/Apple/etc.) during login for convenience
- **Namespace** support for enterprises, schools, guilds, gyms, private groups
- Privacy-first: email/phone/GovID **not required** as the username; can be verified privately
- Human-legible, machine-parseable, and easy to type

## 🧩 ΛID Format

**Canonical handle (no PII):**
```
`#ΛID {namespace?}:{username} [@{provider?}] [~{locale?}] [{emoji?}]`
```

Where:
- `{namespace?}` optional org/community namespace (e.g., `openai`, `stanford`, `acme`)
- `{username}` user-chosen handle (letters, digits, `_` and `-`), 3–32 chars
- `@{provider?}` optional **login alias** (e.g., `@google`, `@apple`, `@github`)
- `~{locale?}` optional location code (ISO country/city slug or 3-word code)
- `{emoji?}` optional single emoji/sigil for personalization (stored as metadata)

**Examples**
- `#ΛID openai:reviewer @apple`
- `#ΛID stanford:alice_smith @google ~us-sf 🦉`
- `#ΛID gonzo @lukhas` (no namespace; first-party LUKHΛS login)

> Note: The `#` and `ΛID` prefix are UI affordances; the **canonical stored form** is `openai:reviewer` with separate metadata fields for provider/locale/emoji.

## 🧾 ABNF (Grammar) & Regex

**ABNF**
```
LUCASID = [NAMESPACE ":"] USERNAME [SP PROVIDER] [SP LOCALE] [SP EMOJI]
NAMESPACE = 1*(ALPHA / DIGIT / "-" / "_")
USERNAME  = 3*32(ALPHA / DIGIT / "-" / "_")
PROVIDER  = "@" ("google" / "apple" / "github" / "lukhas" / 1*ALPHA )
LOCALE    = "~" 1*(ALPHA / DIGIT / "-" )
EMOJI     = %x1F300-1FAD6 / %x2600-26FF ; stored as UTF-8 codepoint
SP        = 1*WSP
```

**Validation Regex (canonical core)**
```
^(?:(?<namespace>[a-z0-9_-]{1,48}):)?(?<username>[a-z0-9_-]{3,32})$ 
```

## 🧭 Login Flow: Provider Dropdown + Username-Only

### UX
1) User selects a provider from a dropdown **(optional)**: Google / Apple / GitHub / LUKHΛS
2) User types **only the username part** (e.g., `alice.smith` for Google; no `@gmail.com`)
3) System resolves final identifier and launches the OAuth flow or first‑party login

### Resolution Rules
- If provider is chosen: build alias `@provider` and map to that OAuth journey
- If no provider: default to first‑party LUKHΛS login (`@lukhas`)
- Namespace typed? Route under that namespace; else global

### Example API
```http
POST /identity/resolve-login
{
  "input": "stanford:alice_smith",
  "provider": "google"    // optional; if omitted → "lukhas"
}

→ 200 OK
{
  "canonical_lid": "stanford:alice_smith",
  "provider": "google",
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "csrf_nonce"
}
```

## 🏛️ Namespaces & Monetization

- **Reserved namespaces** for verified orgs (OpenAI, Stanford, ACME). Paid or verified.
- **Community namespaces** for clubs/crews/schools/gyms (reviewed on request).
- **Personal namespaces** (e.g., `gonzo:`) are allowed if globally unique.
- Squatting rules + grace periods + dispute policy recommended.

## 🔒 Privacy & PII Policy (Important)

- **Never use raw PII as a username** (email, phone, passport/DNI/SSN). 
- If a user prefers phone/passport/DNI for login, treat it as a **verification factor** only.
- Store **hashed, salted, and tokenized** proofs or third‑party attestations (e.g., Stripe Identity, Passkeys/WebAuthn). Do not persist raw numbers.
- Recommend **Passkeys/WebAuthn** as the default strong login; provider aliases remain for convenience.
- Support **2FA** (TOTP, WebAuthn, or GTΨ gesture token) for high‑risk actions.

## 🔐 Security Options (AuthN/AuthZ)

- First‑party login: **Passkeys/WebAuthn** (preferred), email+magic link (fallback)
- Federated login: Google/Apple/GitHub via OAuth/OIDC (username‑only UX)
- Phone verification: SMS/WhatsApp OTP → verified claim, not username
- Government ID: third‑party verification → store attestation token only
- Gesture Token (GTΨ): optional high‑entropy factor for consent/approvals

**Example: linked aliases on a single ΛID**
```json
{
  "lid": "openai:reviewer",
  "aliases": [
    { "provider": "lukhas",  "verified": true },
    { "provider": "google",  "username_hint": "reviewer", "verified": true },
    { "provider": "apple",   "username_hint": "reviewer", "verified": false },
    { "provider": "phone",   "e164_hash": "h:sha256:…",   "verified": true }
  ],
  "mfa": ["webauthn", "totp", "gtpsi"],
  "tier": "T3"
}
```

## 🧪 Validation Matrix (SWOT‑ready)

| Vector | What to test | KPIs |
|---|---|---|
| GTΨ gesture factor | Spoofing, replay, kinesthetic variance | FAR/FRR, entropy/bitrate |
| Runtime grammar | Parser determinism, perf | p50/p95 parse time, error rate |
| Namespace policy | Squatting, dispute | time‑to‑resolution, abuse reports |
| Privacy | PII handling, data retention | 0 raw PII stored, DPIA pass |

## 🏢 Enterprise User ID System

**Note:** All enterprise handles are just **namespaced ΛIDs**. The canonical form is `namespace:username`. Provider aliases (e.g., `@google`) are optional at login time and do not change the canonical ΛID.

### User ID Format Examples

| Organization | Email | Generated User ID | Format Template |
|--------------|-------|-------------------|-----------------|
| **OpenAI** | reviewer@openai.com | `openai-reviewer` | `{org_id}-{username}` |
| **Stanford** | alice.smith@stanford.edu | `stanford-alice_smith` | `{org_id}-{username}` |
| **MIT** | john.doe@mit.edu | `mit-john_doe` | `{org_id}-{username}` |
| **Google** | dev@google.com | `google-dev` | `{org_id}-{username}` |
| **Microsoft** | engineer@microsoft.com | `msft-engineer` | `{org_id}-{username}` |

### Custom Enterprise Formats

Organizations can configure custom user ID formats:

```json
{
  "acme_corp": {
    "organization_id": "acme",
    "domain_pattern": "*.acme.com",
    "user_id_format": "acme:{department}-{username}",
    "default_tier": "T2"
  }
}
```

**Result**: `acme_engineering_johndoe`

## 🔐 OAuth Provider Integration

### 1. **Apple Sign-In Flow**

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Apple
    participant LUKHAS
    
    User->>App: Tap "Sign in with Apple"
    App->>LUKHAS: GET /identity/oauth/login/apple
    LUKHAS->>App: Return Apple Auth URL
    App->>Apple: Redirect to Apple Auth
    User->>Apple: Authorize app
    Apple->>App: Redirect with auth code
    App->>LUKHAS: POST /identity/oauth/callback
    LUKHAS->>Apple: Exchange code for token
    Apple->>LUKHAS: Return user info
    LUKHAS->>App: Return LUKHAS token + user_id
```

**User ID Allocation:**
- **Standard**: `john_doe` (from email john.doe@icloud.com)
- **Enterprise**: `apple-john_doe` (if john.doe@apple.com)
- **Fallback**: `apple_A1B2C3D4` (if username taken)

### 2. **Google OAuth Flow**

**API Request:**
```bash
# Step 1: Get Google Auth URL
POST /identity/oauth/login
{
  "provider": "google",
  "redirect_uri": "https://yourapp.com/oauth/callback"
}

# Response:
{
  "provider": "google",
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?client_id=...",
  "state": "random_csrf_token"
}
```

**User Authorization → Callback:**
```bash
# Step 2: Handle callback after user authorizes
POST /identity/oauth/callback
{
  "provider": "google",
  "code": "4/P7q7W91a-oMsCeLvIaQm6bTrgtp7",
  "redirect_uri": "https://yourapp.com/oauth/callback"
}

# Response:
{
  "success": true,
  "user_id": "john_doe",
  "display_name": "John Doe",
  "email": "john.doe@gmail.com",
  "token": "lukhas_jwt_token_here",
  "tier": "T2",
  "glyphs": ["⚛️", "✨"],
  "provider": "google",
  "is_new_user": true,
  "federated": true
}
```

## 🏢 Enterprise Configuration Examples

### OpenAI Configuration
```python
EnterpriseConfig(
    organization_id="openai",
    domain_pattern="*.openai.com",
    display_name="OpenAI",
    default_tier=AccessTier.T5,  # Full access for OpenAI reviewers
    auto_verify=True,
    user_id_format="openai-{username}"
)
```

**Results:**
- `reviewer@openai.com` → `openai-reviewer` (Tier T5)
- `researcher@openai.com` → `openai-researcher` (Tier T5)
- Auto-verified, full system access

### Stanford University Configuration
```python
EnterpriseConfig(
    organization_id="stanford",
    domain_pattern="*.stanford.edu",
    display_name="Stanford University",
    default_tier=AccessTier.T3,  # Advanced academic access
    auto_verify=True,
    user_id_format="stanford-{username}"
)
```

**Results:**
- `alice.smith@cs.stanford.edu` → `stanford-alice_smith` (Tier T3)
- `prof.johnson@stanford.edu` → `stanford-prof_johnson` (Tier T3)
- Access to consciousness, emotion, dream modules

### Corporate Enterprise Configuration
```python
EnterpriseConfig(
    organization_id="acme",
    domain_pattern="*.acme.com",
    display_name="ACME Corporation",
    default_tier=AccessTier.T2,
    auto_verify=False,  # Manual verification required
    sso_required=True,  # Require SSO login
    user_id_format="acme-{username}"
)
```

## 📱 Mobile App Integration

### iOS App (Swift)
```swift
// 1. Initiate Apple Sign-In
func startAppleSignIn() {
    let provider = ASAuthorizationAppleIDProvider()
    let request = provider.createRequest()
    request.requestedScopes = [.fullName, .email]
    
    let controller = ASAuthorizationController(authorizationRequests: [request])
    controller.delegate = self
    controller.presentationContextProvider = self
    controller.performRequests()
}

// 2. Handle Apple response
func authorizationController(controller: ASAuthorizationController, 
                           didCompleteWithAuthorization authorization: ASAuthorization) {
    if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
        let code = String(data: appleIDCredential.authorizationCode!, encoding: .utf8)!
        
        // Send to LUKHAS
        sendToLUKHAS(provider: "apple", code: code)
    }
}

// 3. Send to LUKHAS API
func sendToLUKHAS(provider: String, code: String) {
    let request = [
        "provider": provider,
        "code": code,
        "redirect_uri": "https://yourapp.com/oauth/callback"
    ]
    
    APIClient.post("/identity/oauth/callback", data: request) { response in
        // Save LUKHAS token and user info
        UserDefaults.standard.set(response.token, forKey: "lukhas_token")
        UserDefaults.standard.set(response.user_id, forKey: "lukhas_user_id")
    }
}
```

### Android App (Kotlin)
```kotlin
// 1. Google Sign-In
private fun startGoogleSignIn() {
    val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
        .requestEmail()
        .requestIdToken(getString(R.string.google_client_id))
        .build()
        
    val client = GoogleSignIn.getClient(this, gso)
    val signInIntent = client.signInIntent
    startActivityForResult(signInIntent, RC_SIGN_IN)
}

// 2. Handle Google response
override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    super.onActivityResult(requestCode, resultCode, data)
    
    if (requestCode == RC_SIGN_IN) {
        val task = GoogleSignIn.getSignedInAccountFromIntent(data)
        val account = task.getResult(ApiException::class.java)
        
        // Send auth code to LUKHAS
        sendAuthCodeToLUKHAS("google", account.serverAuthCode)
    }
}

// 3. API call to LUKHAS
private fun sendAuthCodeToLUKHAS(provider: String, code: String?) {
    val request = mapOf(
        "provider" to provider,
        "code" to code,
        "redirect_uri" to "https://yourapp.com/oauth/callback"
    )
    
    apiService.oauthCallback(request).enqueue(object : Callback<LoginResponse> {
        override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
            // Save LUKHAS credentials
            prefs.edit()
                .putString("lukhas_token", response.body()?.token)
                .putString("lukhas_user_id", response.body()?.user_id)
                .apply()
        }
    })
}
```

## 🔄 Account Linking Examples

### Link Multiple Providers
```bash
# User logs in with Google first
POST /identity/oauth/callback
{
  "provider": "google",
  "code": "google_auth_code"
}
# Returns: user_id = "john_doe"

# Later, link Apple account
POST /identity/oauth/link-account
{
  "primary_user_id": "john_doe",
  "secondary_provider": "apple", 
  "secondary_code": "apple_auth_code",
  "redirect_uri": "https://yourapp.com/oauth/callback"
}
# Result: Can now sign in with either Google or Apple
```

### Migration from Email to OAuth
```bash
# User originally registered with email
# user_id = "john_doe" (from john.doe@gmail.com)

# Now wants to add Google OAuth
POST /identity/oauth/callback
{
  "provider": "google",
  "code": "google_code"
}
# System detects matching email and links automatically
# Still user_id = "john_doe", but can now use OAuth
```

## 🏗️ Temporary User System

### Temporary User Allocation
```python
# When OAuth fails or is incomplete
temp_user_id = oauth_federation.create_temporary_user(
    provider=OAuthProvider.APPLE,
    email="incomplete@example.com"
)
# Returns: "temp_a1b2c3d4"

# Temporary user expires in 1 hour
# Can be converted to permanent user when OAuth completes
```

### Use Cases for Temporary Users:
1. **OAuth Interruption**: User closes app during OAuth flow
2. **Network Issues**: OAuth provider temporarily unavailable  
3. **Partial Data**: Provider returns limited user information
4. **Testing**: Development and testing scenarios

## 📊 User ID Statistics

### User ID Distribution Example:
```
Total Users: 10,000
├── Standard: 7,500 (75%)
│   ├── john_doe: 2,500
│   ├── alice_smith: 2,000
│   └── other patterns: 3,000
├── Enterprise: 2,000 (20%)
│   ├── openai-*: 500
│   ├── stanford-*: 400
│   ├── mit-*: 300
│   └── other orgs: 800
├── Federated: 400 (4%)
│   ├── google_*: 200
│   ├── apple_*: 150
│   └── github_*: 50
└── Temporary: 100 (1%)
    └── temp_*: 100
```

### Tier Distribution by Source:
```
OAuth Users:
├── T5 (Guardian): 15% (enterprise domains)
├── T4 (Quantum): 5% (verified researchers)  
├── T3 (Advanced): 25% (academic domains)
├── T2 (Creator): 50% (standard users)
└── T1 (Observer): 5% (unverified)
```

This system provides **flexible, secure, and scalable** user identity management that works across consumer OAuth, enterprise SSO, and institutional access patterns! 🚀

## 📚 Developer Notes

- Store canonical ΛID as two columns: `namespace` (nullable) and `username`.
- Enforce uniqueness on `(namespace, username)`.
- Keep provider alias, locale, emoji in separate columns (or JSONB) and **do not** include them in uniqueness.
- Provide a `/identity/resolve-login` endpoint (see above) and keep provider‑specific logic isolated in adapters.