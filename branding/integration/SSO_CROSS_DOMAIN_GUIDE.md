# LUKHAS Single Sign-On (SSO) Cross-Domain Integration Guide
## Unified Authentication via ΛiD Across the LUKHAS Ecosystem

---

## Overview

**ΛiD (Lambda ID)** serves as the central authentication system for all LUKHAS domains. This guide specifies how SSO flows work across the ecosystem, ensuring seamless user experience while maintaining security.

**Version**: 1.0
**Created**: 2025-11-06
**Status**: Active - Critical Infrastructure

---

## Architecture

### Central Identity Provider

**Provider**: `lukhas.id`
**Protocol**: OAuth 2.0 / OpenID Connect
**Session Management**: JWT tokens with refresh capability

### Participating Domains

All LUKHAS domains integrate with ΛiD SSO:
- lukhas.ai (flagship)
- lukhas.dev (developers)
- lukhas.team (collaboration)
- lukhas.store (marketplace)
- lukhas.io (infrastructure console)
- lukhas.cloud (cloud console)
- lukhas.com (corporate)
- lukhas.xyz (experimental)
- lukhas.eu, lukhas.us (compliance portals)

---

## User Journey: First-Time Sign-In

### Scenario: User visits lukhas.ai for the first time

1. **User Action**: Clicks "Sign In" on lukhas.ai
2. **lukhas.ai**: Redirects to `lukhas.id/login` with OAuth params
   ```
   https://lukhas.id/login?
     response_type=code&
     client_id=lukhas.ai&
     redirect_uri=https://lukhas.ai/auth/callback&
     scope=openid profile email&
     state=random_state_token
   ```

3. **lukhas.id**: Presents login interface
   - Email/password input
   - OR biometric authentication (if supported)
   - OR social login options (Google, GitHub, etc.)

4. **User**: Enters credentials / authenticates

5. **lukhas.id**:
   - Creates ΛiD if new user
   - Generates unique consciousness signature
   - Sets up session with MFA if enabled
   - Generates authorization code

6. **lukhas.id**: Redirects back to lukhas.ai
   ```
   https://lukhas.ai/auth/callback?
     code=authorization_code&
     state=random_state_token
   ```

7. **lukhas.ai**: Exchanges code for tokens
   ```javascript
   POST https://lukhas.id/oauth/token
   {
     grant_type: 'authorization_code',
     code: 'authorization_code',
     client_id: 'lukhas.ai',
     client_secret: 'client_secret',
     redirect_uri: 'https://lukhas.ai/auth/callback'
   }
   ```

8. **lukhas.id**: Returns tokens
   ```json
   {
     "access_token": "eyJhbGc...",
     "refresh_token": "eyJhbGc...",
     "id_token": "eyJhbGc...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```

9. **lukhas.ai**:
   - Validates tokens
   - Creates local session
   - Stores user info
   - **User is now logged in to lukhas.ai**

---

## User Journey: Cross-Domain SSO (Already Logged In)

### Scenario: User logged into lukhas.ai, now visits lukhas.dev

1. **User Action**: Clicks "Sign In" on lukhas.dev (or auto-triggered)

2. **lukhas.dev**: Redirects to `lukhas.id/login` (same OAuth flow)

3. **lukhas.id**:
   - **Detects existing session** (session cookie from previous login)
   - **No login UI shown** (user already authenticated)
   - Immediately generates authorization code
   - Redirects back to lukhas.dev

4. **lukhas.dev**: Exchanges code for tokens (same as above)

5. **lukhas.dev**: **User is now logged in—seamless experience**

**User Experience**: User never saw a login screen on lukhas.dev; they were automatically signed in because ΛiD recognized their existing session.

---

## Technical Implementation

### OAuth 2.0 Endpoints (lukhas.id)

```yaml
authorization_endpoint: https://lukhas.id/oauth/authorize
token_endpoint: https://lukhas.id/oauth/token
userinfo_endpoint: https://lukhas.id/oauth/userinfo
jwks_uri: https://lukhas.id/.well-known/jwks.json
```

### Scopes

```yaml
openid: Required - OIDC identifier
profile: User profile info (name, avatar, etc.)
email: User email address
lukhas:platform: Access to LUKHAS platform features
lukhas:developer: Developer API access
lukhas:team: Team collaboration features
lukhas:store: Marketplace purchases
lukhas:admin: Administrative functions
```

### Token Structure

#### Access Token (JWT)
```json
{
  "sub": "lid_abc123...",  // ΛiD (subject)
  "iss": "https://lukhas.id",
  "aud": ["lukhas.ai", "lukhas.dev"],
  "exp": 1635724800,
  "iat": 1635721200,
  "scope": "openid profile email lukhas:platform",
  "consciousness_signature": "sig_xyz789..."
}
```

#### ID Token (JWT)
```json
{
  "sub": "lid_abc123...",
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "email_verified": true,
  "avatar_url": "https://cdn.lukhas.id/avatars/lid_abc123.jpg",
  "consciousness_signature": "sig_xyz789...",
  "iss": "https://lukhas.id",
  "aud": "lukhas.ai",
  "exp": 1635724800,
  "iat": 1635721200
}
```

---

## Session Management

### Session Duration

```yaml
access_token_lifetime: 1 hour
refresh_token_lifetime: 30 days
id_token_lifetime: 1 hour
session_cookie_lifetime: 7 days (remember me) or session (no checkbox)
```

### Token Refresh

When access token expires, clients should use refresh token:

```javascript
POST https://lukhas.id/oauth/token
{
  grant_type: 'refresh_token',
  refresh_token: 'eyJhbGc...',
  client_id: 'lukhas.ai',
  client_secret: 'client_secret'
}
```

### Logout

#### Single Domain Logout
```javascript
// Logs out from current domain only
lukhas.ai.logout()
// Clears local session
// Redirects to lukhas.ai homepage
```

#### Global Logout (All Domains)
```javascript
// Logs out from ALL LUKHAS domains
window.location = 'https://lukhas.id/logout?redirect=https://lukhas.ai'
```

**lukhas.id** revokes session and all tokens, user logged out everywhere.

---

## Visual Consistency During Auth Flow

### Branding During Redirect

When user is redirected to `lukhas.id`, they should **immediately recognize** they're still in the LUKHAS ecosystem.

#### lukhas.id Login Page Elements

```html
<div class="auth-page">
  <header class="lukhas-header">
    <img src="/logos/lukhas-lambda.svg" alt="LUKHAS ΛiD" />
    <nav>
      <a href="https://lukhas.ai">← Back to LUKHAS.AI</a>
    </nav>
  </header>

  <main class="auth-container">
    <div class="biometric-signature" data-domain="lukhas.ai">
      <!-- Unique particle pattern -->
    </div>

    <h1>Sign in with ΛiD</h1>
    <p>Signing in to <strong>LUKHAS.AI</strong></p>

    <!-- Login form -->
    <form class="auth-form">
      <input type="email" placeholder="Email" />
      <input type="password" placeholder="Password" />
      <button type="submit">Sign In</button>
    </form>

    <div class="auth-alternatives">
      <button class="biometric-auth">Use Biometric</button>
      <a href="/signup">Create ΛiD</a>
    </div>
  </main>

  <footer class="lukhas-footer">
    <!-- Constellation links -->
  </footer>
</div>
```

**Key Elements**:
- LUKHAS branding prominent
- Shows which domain user is signing into ("Signing in to LUKHAS.AI")
- Consistent color scheme (security purple)
- Biometric signature visualization
- Clear CTAs

### Loading States

```html
<!-- During redirect -->
<div class="auth-redirect-loading">
  <div class="loading-biometric">
    <div class="scan-line"></div>
  </div>
  <p>Authenticating with ΛiD...</p>
</div>
```

### Success Confirmation

```html
<!-- After successful auth, before redirect back -->
<div class="auth-success">
  <div class="success-animation">
    <!-- Particle burst -->
  </div>
  <h2>Welcome back, Ada!</h2>
  <p>Returning to LUKHAS.AI...</p>
  <!-- Auto-redirect in 1s -->
</div>
```

---

## Security Considerations

### PKCE (Proof Key for Code Exchange)

For public clients (SPAs, mobile apps), use PKCE:

```javascript
// Generate code verifier
const codeVerifier = generateRandomString(128);
// Generate code challenge
const codeChallenge = base64UrlEncode(sha256(codeVerifier));

// Authorization request includes:
{
  code_challenge: codeChallenge,
  code_challenge_method: 'S256'
}

// Token exchange includes:
{
  code_verifier: codeVerifier
}
```

### State Parameter

Always include and validate `state` parameter to prevent CSRF:

```javascript
const state = generateRandomString(32);
sessionStorage.setItem('oauth_state', state);

// Include in authorization URL
// Validate on callback
if (callbackState !== sessionStorage.getItem('oauth_state')) {
  throw new Error('Invalid state');
}
```

### Token Storage

```javascript
// Access Token: Memory only (don't persist)
let accessToken = null;

// Refresh Token: HttpOnly cookie (backend sets)
// Never expose to JavaScript

// ID Token: Can be stored in sessionStorage for user info
sessionStorage.setItem('id_token', idToken);
```

### HTTPS Only

**All** OAuth flows MUST use HTTPS. No exceptions.

---

## Error Handling

### Common Error Scenarios

#### User Cancels Login
```
https://lukhas.ai/auth/callback?
  error=access_denied&
  error_description=User cancelled login
```

**Client Handling**: Show message, redirect to homepage

#### Invalid Credentials
lukhas.id shows error on login page, user retries.

#### Expired Session
Access token expired, refresh fails.

**Client Handling**: Redirect to login, preserve intended destination.

#### Network Issues
**Client Handling**: Retry with exponential backoff, show friendly error.

---

## Implementation Checklist for New Domains

When adding a new domain to LUKHAS SSO:

### Backend Setup
- [ ] Register OAuth client with lukhas.id
- [ ] Obtain `client_id` and `client_secret`
- [ ] Configure redirect URIs (e.g., `https://new-domain.lukhas.ai/auth/callback`)
- [ ] Implement OAuth authorization code flow
- [ ] Implement token exchange endpoint handler
- [ ] Implement token refresh logic
- [ ] Store tokens securely (refresh in HttpOnly cookie)
- [ ] Validate ID token JWT signature

### Frontend Setup
- [ ] Add "Sign In with ΛiD" button
- [ ] Implement redirect to lukhas.id/login
- [ ] Handle OAuth callback
- [ ] Extract and validate state parameter
- [ ] Display user info from ID token
- [ ] Implement logout (local and global options)
- [ ] Handle session expiry gracefully

### Visual Integration
- [ ] Use consistent ΛiD branding for auth buttons
- [ ] Show loading state during redirects
- [ ] Display user avatar and name (from ID token)
- [ ] Implement biometric particle signature (optional)

### Testing
- [ ] Test first-time sign-in
- [ ] Test cross-domain SSO (already logged in)
- [ ] Test logout (local and global)
- [ ] Test token refresh
- [ ] Test error scenarios (cancel, invalid creds, network errors)
- [ ] Test mobile and desktop
- [ ] Test with screen readers

---

## Domain-Specific Customizations

### lukhas.dev: API Key Access

After SSO, developers need API keys:

```javascript
// After successful auth
const accessToken = getAccessToken();

// Fetch API keys from developer console
fetch('https://lukhas.id/api/developer/keys', {
  headers: {
    Authorization: `Bearer ${accessToken}`
  }
});
```

### lukhas.store: Purchase History

```javascript
// After SSO, load user's purchased apps
fetch('https://lukhas.store/api/purchases', {
  headers: {
    Authorization: `Bearer ${accessToken}`
  }
});
```

### lukhas.team: Team Membership

```javascript
// After SSO, load user's teams
fetch('https://lukhas.team/api/teams', {
  headers: {
    Authorization: `Bearer ${accessToken}`
  }
});
```

---

## Monitoring & Analytics

### Key Metrics

```yaml
sso_success_rate: >98%  # Target
avg_auth_time: <2s       # Time from click to logged in
cross_domain_success: >99%  # SSO without re-login
token_refresh_success: >99.5%
```

### Logging

```javascript
// Log all auth events
log.info('SSO_INITIATED', {
  source_domain: 'lukhas.ai',
  user_id: null,  // Not yet authenticated
  timestamp: new Date()
});

log.info('SSO_SUCCESS', {
  source_domain: 'lukhas.ai',
  user_id: 'lid_abc123',
  auth_time: '1.2s',
  timestamp: new Date()
});

log.error('SSO_FAILURE', {
  source_domain: 'lukhas.ai',
  error: 'invalid_grant',
  timestamp: new Date()
});
```

---

## Troubleshooting

### Issue: User sees login screen on every domain

**Cause**: Session cookie from lukhas.id not being set or shared
**Solution**:
- Verify `SameSite=None; Secure` on session cookie
- Ensure all domains use HTTPS
- Check cookie domain is set to `.lukhas.id`

### Issue: Token refresh fails

**Cause**: Refresh token expired or revoked
**Solution**: Redirect user to login, preserve destination URL

### Issue: CORS errors during token exchange

**Cause**: Token exchange should be backend-to-backend
**Solution**: Never call `/oauth/token` from frontend; use backend proxy

---

## Future Enhancements

- [ ] Biometric WebAuthn support
- [ ] Social login (Google, GitHub, Apple)
- [ ] Multi-factor authentication (MFA) during SSO
- [ ] Passwordless magic links
- [ ] Device trust and remember device
- [ ] Session management dashboard (see all active sessions)

---

## Version & Metadata

**Version**: 1.0
**Created**: 2025-11-06
**Last Updated**: 2025-11-06
**Next Review**: 2026-02-06
**Maintained By**: LUKHAS Identity Team

**Contact**:
- Technical Issues: identity-dev@lukhas.id
- Security Issues: security@lukhas.id
- General Support: support@lukhas.id

**Based On**:
- OAuth 2.0 RFC 6749
- OpenID Connect Core 1.0
- PKCE RFC 7636
- LUKHAS Multi-Domain Strategy
