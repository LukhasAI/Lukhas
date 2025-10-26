Title: Wire core WebAuthn adapter into identity flows with minimal public routes

Objective
- Introduce minimal WebAuthn endpoints backed by the core adapter scaffold at `core/identity/adapters/webauthn_adapter.py:1` without violating lane boundaries.

Context
- Adapter provides:
  - `start_challenge(user_id, rp_id, origin) -> dict`
  - `verify_response(response, expected_challenge=None) -> dict`
- This is a deterministic stub (no crypto) suitable for smoke and UI prototyping.

Deliverables
- New FastAPI router `lukhas/identity/webauthn_api.py` (or `serve/webauthn_routes.py` if identity package not present) with endpoints:
  - `POST /id/webauthn/challenge`: body `{ user_id, rp_id, origin }` → returns PublicKey credential options
  - `POST /id/webauthn/verify`: body `{ response, expected_challenge? }` → returns `{ ok: bool, user_verified: bool }`
- Conditional include in `serve/main.py:1` guarded by env `LUKHAS_WEBAUTHN=1`.
- Basic tests exercising both endpoints and happy-path.

Constraints
- Keep endpoints under non-OpenAI namespace (`/id/webauthn/*`).
- No lane violations; use the adapter only from `core/identity/adapters/...`.
- Keep cryptographic verification out-of-scope; adapter is intentionally stubbed.

Suggested Steps
1) Create router module (one file, small, typed) importing `core.identity.adapters.webauthn_adapter as wa`.
2) Add pydantic models for request bodies; strict validation.
3) Update `serve/main.py:1` to include this router when `LUKHAS_WEBAUTHN=1`.
4) Tests in `tests/unit/test_webauthn_routes.py` covering challenge + verify roundtrip.

Verification
- `make codex-bootcheck`
- `pytest -q tests/unit/test_webauthn_routes.py`
- Manual curl:
  - `curl -X POST :8000/id/webauthn/challenge -d '{"user_id":"u1","rp_id":"lukhas.ai","origin":"https://lukhas.ai"}' -H 'Content-Type: application/json'`

Acceptance Criteria
- Endpoints present only when `LUKHAS_WEBAUTHN=1`.
- Roundtrip works and returns `ok: true`.
- Tests pass.

Commit (T4)
feat(identity): expose minimal WebAuthn routes backed by core adapter

