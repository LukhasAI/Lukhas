# LUKHAS AI API Migration Guide

This guide provides instructions for migrating to new versions of the LUKHAS AI API.

## Versioning

The LUKHAS AI API follows Semantic Versioning. Breaking changes will only be introduced in major version updates.

## Migrating from v1 to v2

Version 2 of the LUKHAS AI API is currently in development. This section will be updated with detailed migration instructions as the release date approaches.

### Key Changes in v2

*   **Authentication:** API keys will be replaced with OAuth 2.0 access tokens.
*   **Rate Limiting:** Rate limits will be more granular, with different limits for different endpoints.
*   **Error Handling:** Error responses will be more detailed and will include a unique error code for each type of error.

## Deprecation Notices

### v1 Endpoints

*   The `/v1/status` endpoint in the Consciousness Chat API is deprecated and will be removed in v2. Please use the `/health` endpoint instead.
*   The `/v1/identity/auth/token` endpoint is deprecated and will be removed in v2. Please use the new OAuth 2.0 flow to obtain an access token.
