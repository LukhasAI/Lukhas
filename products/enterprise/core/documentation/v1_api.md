---
status: wip
type: documentation
---
# V1 Endpoints: Identity, Consciousness, and Guardian

This document outlines the v1 API endpoints for core LUKHAS functionalities. These endpoints are designed for high-performance, system-level integrations and may be served by a different application than the core chat and feedback APIs.

**Note:** These endpoints were not present in the `openapi.json` generated from the `serve.main:app` server. This documentation is based on the specifications provided for load testing and enterprise integration.

## Identity API

Endpoints for managing user identity, authentication, and access tiers.

### POST /api/v1/identity/authenticate

Authenticate a user and receive a session token.

### GET /api/v1/identity/verify

Verify the validity of a session token.

### GET /api/v1/identity/tier-check

Check the access tier for a given user or token.

## Consciousness API

Endpoints for direct interaction with the consciousness module.

### POST /api/v1/consciousness/query

Submit a query to the consciousness module for a direct, unfiltered response.

### POST /api/v1/consciousness/dream

Initiate a dream sequence with a given seed.

### GET /api/v1/consciousness/memory

Retrieve a memory snapshot from the consciousness module.

## Guardian API

Endpoints for interacting with the Guardian safety and alignment system.

### POST /api/v1/guardian/validate

Request validation of a proposed action or content against the Guardian's principles.

### GET /api/v1/guardian/audit

Retrieve an audit trail of Guardian validation decisions.

### GET /api/v1/guardian/drift-check

Check the current constitutional drift score of the system.
