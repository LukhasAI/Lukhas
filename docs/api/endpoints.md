# LUKHAS API Endpoints

This document provides a comprehensive overview of the LUKHAS API endpoints. For detailed information about each endpoint, please refer to the OpenAPI specification.

## OpenAI Compatible Endpoints

These endpoints are designed to be compatible with the OpenAI API.

-   `POST /v1/chat/completions`: Generate a chat completion.
-   `POST /v1/embeddings`: Create deterministic embeddings for a given input.
-   `GET /v1/models`: List the available models.
-   `POST /v1/responses`: Create a response.

## Dreams API

-   `POST /v1/dreams`: Create a new dream sequence.

## Consciousness API

-   `POST /api/v1/consciousness/query`: Query the current consciousness state.
-   `POST /api/v1/consciousness/dream`: Initiate a dream sequence.
-   `GET /api/v1/consciousness/memory`: Get the consciousness memory state.

## Feedback API

-   `POST /feedback/capture`: Capture user feedback for an AI action.
-   `POST /feedback/batch`: Capture multiple feedback cards at once.
-   `GET /feedback/report/{user_id}`: Get a learning report for a specific user.
-   `GET /feedback/metrics`: Get overall feedback system metrics.
-   `POST /feedback/trigger-learning`: Manually trigger the learning cycle.
-   `GET /feedback/health`: Health check for the feedback system.

## Guardian API

-   `POST /api/v1/guardian/validate`: Validate an action against the guardian policies.
-   `GET /api/v1/guardian/audit`: Retrieve the guardian audit log.
-   `GET /api/v1/guardian/drift-check`: Check for policy drift.

## Identity API

-   `POST /api/v1/identity/authenticate`: Authenticate a user.
-   `GET /api/v1/identity/verify`: Verify a user.
-   `GET /api/v1/identity/tier-check`: Check the user's tier.
