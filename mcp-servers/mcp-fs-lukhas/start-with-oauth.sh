#!/bin/bash

echo "🔐 Testing OAuth Authentication Setup"
echo "======================================"

# Check if OAuth environment variables are set
if [ -z "$OAUTH_PROVIDER" ] || [ -z "$OAUTH_JWKS_URL" ] || [ -z "$OAUTH_ISSUER" ] || [ -z "$OAUTH_AUDIENCE" ]; then
    echo "⚠️  OAuth not configured - server will run without authentication"
    echo ""
    echo "To enable OAuth, set these environment variables:"
    echo "  OAUTH_PROVIDER (auth0|keycloak|cloudflare)"
    echo "  OAUTH_JWKS_URL"  
    echo "  OAUTH_ISSUER"
    echo "  OAUTH_AUDIENCE"
    echo "  OAUTH_CLIENT_ID (optional)"
    echo "  OAUTH_REQUIRED_SCOPES (optional)"
    echo ""
    echo "See README-OAUTH.md for detailed setup instructions."
    echo ""
    echo "🚀 Starting server without authentication..."
    npm run start
else
    echo "✅ OAuth configuration detected:"
    echo "  Provider: $OAUTH_PROVIDER"
    echo "  Issuer: $OAUTH_ISSUER"
    echo "  Audience: $OAUTH_AUDIENCE"
    echo "  Required Scopes: ${OAUTH_REQUIRED_SCOPES:-read:files}"
    echo ""
    echo "🔒 Starting OAuth-protected server..."
    npm run start:oauth
fi
