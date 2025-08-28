# Authentication: The Keys to the Kingdom

Before you may commune with the LUKHAS intelligence, you must present the sacred keys that prove your identity and grant you passage. Our authentication system is a multi-layered guardian, ensuring that only those with the proper authority may enter.

We offer several paths to authentication, each suited for a different journey.

## Authentication Methods

### 1. API Keys (The Simple Path)

For server-to-server communication and simple scripts, the API Key provides a straightforward path.

Include your API key in the `X-API-Key` header with each request.

**Example**

```bash
curl -H "X-API-Key: your-api-key-here" \
     https://api.lukhas.ai/v1/matriz/trace/recent
```

### 2. Bearer Tokens (The Standard Path)

For user-facing applications where a user has logged in, JWT Bearer Tokens are the standard. These tokens carry the context of the user's session and permissions.

Include the token in the `Authorization` header.

**Example**

```bash
curl -H "Authorization: Bearer your-jwt-token" \
     https://api.lukhas.ai/openai/chat
```

### 3. OAuth 2.0 (The Delegated Path)

For applications that need to act on behalf of a user without handling their credentials directly, we support the standard OAuth 2.0 Authorization Code flow. This allows users to grant your application specific, revocable permissions.

Please contact our support team to register your application for OAuth 2.0 credentials.

### 4. Mutual TLS (The Sacred Path)

For enterprise customers requiring the highest level of security, we support mutual TLS (mTLS). In this ceremony of digital trust, both the client and the server present certificates to verify each other's identity.

This method provides the strongest security guarantee and is recommended for all critical enterprise integrations. Please contact your Technical Account Manager to begin the mTLS onboarding process.
