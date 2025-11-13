"""
Golden fixtures for smoke tests.

Provides unified authentication tokens and test data to eliminate flaky 401/403 errors.
All tokens use consistent scopes, org, and project IDs.

**Stability Contract**:
- All tokens are pre-validated against identity/tier_system
- Same org/project/scope across all tests
- No external dependencies (fully mocked)
- Deterministic behavior for CI/CD

**Token Format**: sk-lukhas-{tier}-{unique_id}
- Tier 0 (basic): Limited access, rate limits
- Tier 1 (standard): Standard access
- Tier 2 (premium): Enhanced access
- Tier 3 (enterprise): Full access

**Usage**:
```python
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS, GOLDEN_ORG_TOKEN

def test_my_feature(client: TestClient) -> None:
    r = client.post("/v1/responses", headers=GOLDEN_AUTH_HEADERS, json=payload)
    assert r.status_code == 200
```

Phase 3: Added for test reliability polish (Task 6).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

# =============================================================================
# Golden Authentication Tokens
# =============================================================================

# Primary token for most smoke tests (Tier 1 - Standard)
GOLDEN_TOKEN = "sk-lukhas-standard-1234567890abcdef"

# Alternative tokens for multi-org or tier-specific tests
GOLDEN_TOKEN_TIER0 = "sk-lukhas-basic-0000000000000000"
GOLDEN_TOKEN_TIER1 = "sk-lukhas-standard-1234567890abcdef"  # Same as GOLDEN_TOKEN
GOLDEN_TOKEN_TIER2 = "sk-lukhas-premium-9876543210fedcba"
GOLDEN_TOKEN_TIER3 = "sk-lukhas-enterprise-abcdef1234567890"

# Org-specific tokens for isolation tests
GOLDEN_ORG1_TOKEN = "sk-lukhas-org1-aaaaaaaaaaaaaaaa"
GOLDEN_ORG2_TOKEN = "sk-lukhas-org2-bbbbbbbbbbbbbbbb"

# Invalid tokens for negative testing
INVALID_TOKEN_SHORT = "short"  # Too short (< 8 chars)
INVALID_TOKEN_MALFORMED = "not-a-valid-token"
INVALID_TOKEN_WRONG_PREFIX = "sk-openai-wrong-prefix-12345678"

# =============================================================================
# Header Builders
# =============================================================================

def golden_auth_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Build auth headers with golden token.

    Args:
        extra: Optional extra headers to merge (e.g., Idempotency-Key, X-Custom-Header)

    Returns:
        Headers dict with Authorization + any extras

    Example:
        headers = golden_auth_headers({"Idempotency-Key": "test-123"})
    """
    headers = {"Authorization": f"Bearer {GOLDEN_TOKEN}"}
    if extra:
        headers.update(extra)
    return headers


def tier_auth_headers(tier: int, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Build auth headers for specific tier.

    Args:
        tier: Tier level (0-3)
        extra: Optional extra headers

    Returns:
        Headers dict with tier-specific token

    Example:
        headers = tier_auth_headers(3)  # Enterprise tier
    """
    token_map = {
        0: GOLDEN_TOKEN_TIER0,
        1: GOLDEN_TOKEN_TIER1,
        2: GOLDEN_TOKEN_TIER2,
        3: GOLDEN_TOKEN_TIER3,
    }
    token = token_map.get(tier, GOLDEN_TOKEN)
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def org_auth_headers(org_id: int, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Build auth headers for specific org.

    Args:
        org_id: Organization ID (1 or 2)
        extra: Optional extra headers

    Returns:
        Headers dict with org-specific token

    Example:
        headers = org_auth_headers(1)  # Org 1
    """
    token_map = {
        1: GOLDEN_ORG1_TOKEN,
        2: GOLDEN_ORG2_TOKEN,
    }
    token = token_map.get(org_id, GOLDEN_TOKEN)
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def invalid_auth_headers(token_type: str = "short") -> Dict[str, str]:
    """
    Build headers with intentionally invalid token for negative testing.

    Args:
        token_type: Type of invalid token ('short', 'malformed', 'wrong_prefix')

    Returns:
        Headers dict with invalid token

    Example:
        headers = invalid_auth_headers("short")
        r = client.post("/v1/responses", headers=headers, json=payload)
        assert r.status_code == 401
    """
    token_map = {
        "short": INVALID_TOKEN_SHORT,
        "malformed": INVALID_TOKEN_MALFORMED,
        "wrong_prefix": INVALID_TOKEN_WRONG_PREFIX,
    }
    token = token_map.get(token_type, INVALID_TOKEN_MALFORMED)
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# Convenience Exports (Backward Compatibility)
# =============================================================================

# Most tests should use these
GOLDEN_AUTH_HEADERS = golden_auth_headers()
GOLDEN_ORG_TOKEN = GOLDEN_TOKEN

# Legacy aliases for gradual migration
AUTH_HEADERS = GOLDEN_AUTH_HEADERS
VALID_TOKEN = GOLDEN_TOKEN

# =============================================================================
# Golden Test Data
# =============================================================================

def golden_embed_payload(input_text: str = "hello world") -> Dict[str, Any]:
    """
    Build standard embeddings payload.

    Args:
        input_text: Text to embed (default: "hello world")

    Returns:
        Embeddings API payload dict

    Example:
        payload = golden_embed_payload("test input")
        r = client.post("/v1/embeddings", headers=GOLDEN_AUTH_HEADERS, json=payload)
    """
    return {
        "model": "lukhas-embed",
        "input": input_text,
    }


def golden_response_payload(
    input_text: str = "hi",
    stream: bool = False,
    model: str = "lukhas-response"
) -> Dict[str, Any]:
    """
    Build standard responses payload.

    Args:
        input_text: Input text (default: "hi")
        stream: Enable streaming (default: False)
        model: Model name (default: "lukhas-response")

    Returns:
        Responses API payload dict

    Example:
        payload = golden_response_payload("test", stream=True)
        r = client.post("/v1/responses", headers=GOLDEN_AUTH_HEADERS, json=payload)
    """
    return {
        "model": model,
        "input": input_text,
        "stream": stream,
    }


def golden_dream_payload(prompt: str = "test dream") -> Dict[str, Any]:
    """
    Build standard dreams payload.

    Args:
        prompt: Dream prompt (default: "test dream")

    Returns:
        Dreams API payload dict

    Example:
        payload = golden_dream_payload("lucid dream test")
        r = client.post("/v1/dreams", headers=GOLDEN_AUTH_HEADERS, json=payload)
    """
    return {
        "prompt": prompt,
        "model": "lukhas-dream",
    }


# =============================================================================
# Test Isolation Helpers
# =============================================================================

def unique_idempotency_key(test_name: str, iteration: int = 0) -> str:
    """
    Generate unique idempotency key for test.

    Args:
        test_name: Name of test (e.g., "test_replay_cache")
        iteration: Optional iteration counter for multi-call tests

    Returns:
        Unique idempotency key string

    Example:
        key = unique_idempotency_key("test_cache_hit")
        headers = golden_auth_headers({"Idempotency-Key": key})
    """
    import hashlib
    import time

    # Include timestamp to ensure uniqueness across test runs
    data = f"{test_name}-{iteration}-{time.time()}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def golden_trace_header(test_name: str) -> Dict[str, str]:
    """
    Generate consistent trace header for test.

    Args:
        test_name: Name of test

    Returns:
        Headers dict with X-Trace-Id

    Example:
        headers = {**GOLDEN_AUTH_HEADERS, **golden_trace_header("test_tracing")}
    """
    import hashlib

    trace_id = hashlib.md5(test_name.encode()).hexdigest()
    return {"X-Trace-Id": trace_id}
