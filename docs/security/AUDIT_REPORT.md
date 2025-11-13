# Security Audit Report - November 2025

## 1. Executive Summary

This report details the findings and remediations of a security audit conducted on the LUKHAS AI Platform. The audit identified two key vulnerabilities: one critical vulnerability related to an insecure authentication fallback mechanism, and one high-severity vulnerability in the multi-tenant memory system of the `/v1/embeddings` endpoint.

Both vulnerabilities have been addressed, and security-focused tests have been added to prevent regressions. This report provides a detailed breakdown of the identified issues and the corrective actions taken.

## 2. Vulnerabilities Identified

### 2.1. Critical Vulnerability: Insecure Authentication Fallback

**- Vulnerability:** The authentication system in `labs/core/security/auth.py` was designed with a mock JWT implementation that would be used if the `PyJWT` library was not installed. This mock implementation provided no actual security and would have allowed the application to run in an insecure state, creating a significant security risk.

**- Impact:** If the `PyJWT` dependency was accidentally missed during deployment, the authentication system would fail open, allowing unauthenticated access to protected endpoints.

**- Recommendation:** Remove the insecure mock JWT implementation and instead raise an `ImportError` if the `PyJWT` library is not available. This ensures that the application will fail safely rather than running in an insecure state.

### 2.2. High-Severity Vulnerability: Improper Tenant Isolation in `/v1/embeddings`

**- Vulnerability:** The `/v1/embeddings` endpoint in `serve/main.py` was using the raw `Authorization` header as the `tenant_id` for the multi-tenant memory system. This was a direct use of user-supplied data without proper validation.

**- Impact:** This vulnerability could have been exploited to access or poison the memory indexes of other tenants. An attacker could have potentially specified another user's `user_id` in the `Authorization` header, leading to a full bypass of tenant isolation.

**- Recommendation:** Modify the endpoint to use the `user_id` from the validated JWT payload as the `tenant_id`. This ensures that the tenant ID is always a validated and authenticated user identifier, preventing any possibility of tenant-hopping attacks.

## 3. Remediations

### 3.1. Hardening the Authentication System

- The insecure mock JWT implementation in `labs/core/security/auth.py` has been removed. The system now raises an `ImportError` if the `PyJWT` library is not installed, preventing the application from starting in an insecure state.
- The `/v1/embeddings` endpoint has been modified to use the `user_id` from the validated JWT payload as the `tenant_id`. This ensures that the multi-tenant memory system is always correctly scoped to the authenticated user.
- The `StrictAuthMiddleware` in `serve/main.py` has been updated to attach the validated JWT payload to the request state, making the authenticated user's information securely available to downstream endpoints.

### 3.2. Security-Focused Testing

- A unit test has been added to `tests/unit/labs/core/security/test_auth.py` to verify that an `ImportError` is raised if the `PyJWT` library is not installed.
- An integration test has been added to `tests/integration/api/test_embeddings_auth.py` to ensure that the `/v1/embeddings` endpoint correctly uses the `user_id` from the JWT payload as the `tenant_id`.

## 4. Conclusion

The vulnerabilities identified in this audit have been successfully remediated, and the overall security posture of the LUKHAS AI Platform has been significantly improved. The addition of security-focused tests will help to prevent similar vulnerabilities from being introduced in the future.
