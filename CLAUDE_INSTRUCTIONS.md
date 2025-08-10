

CLAUDE INSTRUCTIONS

⸻

0) System-wide guardrails (run first)

Prompt to Claude

Act as principal engineer. Apply these non-negotiable guardrails across all work you do in this repo:
	1.	Canonical identity is ΛID = {namespace?}:{username}; no raw PII (email/phone/passport/SSN/DNI) as usernames. These may be verification claims only, never stored raw (store hashed/attested).
	2.	Primary auth = Passkeys/WebAuthn. OAuth aliases (Google/Apple/GitHub/Microsoft) are optional convenience. GTΨ (gesture token) is an optional consent/MFA factor for sensitive actions.
	3.	Data minimization: default “metadata-only” reads; escalate to content only when the user explicitly consents per item.
	4.	Capability tokens: use short-lived, least-privilege JWT/macaroons with caveats (service, scope, resource IDs, TTL, audience). Refresh tokens live in an enclave/KMS.
	5.	Edge first for gesture recognition; store only hashed kinematic features.
	6.	Everything must have: logs, audit trail, and revocation paths.
Reply “ACK GUARDRAILS” when applied.

⸻

1) ΛID Resolver + OIDC Provider (you are the IdP)

Prompt to Claude

Create a minimal ΛID Resolver + OIDC Provider service in identity/:
	•	Endpoints:
	•	POST /identity/resolve-login → input { "input": "namespace:username", "provider":"google|apple|lukhas|…" }, output canonical lid, normalized provider, and redirect auth_url if alias provider is chosen.
	•	GET /.well-known/openid-configuration and JWKS for OIDC Provider (“Sign in with LUKHΛS”).
	•	Storage: Postgres schema identity with tables: users(namespace, username, created_at), unique (namespace, username); aliases(lid, provider, hint, verified); mfa(lid, type, enabled).
	•	Add WebAuthn/Passkeys bootstrap for first-party login (@lukhas).
	•	ABNF parser for ΛID (use the ABNF we drafted) + strict regex.
	•	Unit tests with pytest.
	•	CLI seeding script: create gonzo and sample namespaces openai, stanford.
Acceptance: docker compose up boots OIDC endpoints; tests pass; p95 parse < 2ms.

⸻

2) Consent Fabric + Unified Consent Graph (UCG)

Prompt to Claude

Implement a Consent Fabric and Unified Consent Graph:
Files: consent/ucg_schema.sql, consent/service.py, consent/api.py
	•	Graph entities: lid, service, resource, scope, token (capability), purpose, edges GRANTED, USES, EXPIRES_AT, REVOKED.
	•	API:
	•	POST /consent/grant → { lid, service, scopes:[…], purpose, ttl } → issues capability token (macaroon w/ caveats).
	•	POST /consent/revoke → revoke by token id or by (lid, service, scope).
	•	GET /consent/ledger?lid=… → returns human-readable ledger for Studio.
	•	Logic: metadata-only scopes by default (email.read.headers, cloud.list.metadata). Escalations must create a new capability with narrower resource IDs and short TTL (≤30m).
	•	Add audit log table; every grant/revoke logged with reason and client IP/fingerprint.
Acceptance: unit tests for grant/escalate/revoke; example macaroons; ledger renders readable.

⸻

3) Service Adapters (Gmail headers, Drive/Dropbox list)

Prompt to Claude

Create adapters under adapters/ with a common interface (list, get, put, move, search, watch) and no direct vendor calls from the orchestrator:
	•	adapters/gmail_headers/ → list headers only (from, to, subject, date, labels).
	•	adapters/drive/ + adapters/dropbox/ → list files (name, size, mime, last_access, sharing).
	•	Each adapter must accept a capability token and verify its caveats; deny if scope/resource/TTL invalid.
	•	Provide “dry-run” plan API for file consolidation: POST /cloud/plan (diff: duplicates, old archives, projected savings).
Acceptance: smoke tests for list endpoints with fake vendors; deny on missing/expired capability.

⸻

4) GTΨ gesture factor (edge model + consent prompts)

Prompt to Claude

Add GTΨ as optional MFA/consent:
	•	gtpsi/edge/ a tiny on-device recognizer (gesture→hashed features). Simulate with a library or stub if needed.
	•	gtpsi/server/verify.py verifies { lid, gesture_hash, nonce, timestamp }; bind result to an approval record for the exact action (e.g., “send email”, “move files”, “grant scope”).
	•	Add a “sign with stroke” UI hook to Studio that requests GTΨ for high-risk actions and time-locks approval (≤60s).
	•	Store only hashed kinematic features + salt in a per-user enclave; never raw strokes.
Acceptance: tests show GTΨ approval is required and verified for: send_email, cloud.move.files, share_link_public.

⸻

5) Universal Language (UL) entropy factor

Prompt to Claude

Implement Universal Language (UL) as a local secure mapping between personal symbols (strokes, emojis, words, sounds) and Λ-meanings:
	•	ul/local_map.enc sealed store per device; CRUD via ul/service.py.
	•	API: POST /ul/bind → { symbol: any, meaning: ΛID or UNL token, salt } (stored only locally); POST /ul/challenge → server sends a random challenge asking for a composition (e.g., “compose ⟨calm + collapse⟩”), client returns UL-signature; server only receives a proof, not raw symbol data.
	•	Integrate UL as an additional entropy source during high-risk approvals; if present, combine GTΨ + UL proof.
Acceptance: E2E flow where a user binds two personal symbols and later passes a challenge without the server learning the raw forms.

⸻

6) Re-auth, fallback & safety playbooks

Prompt to Claude

Add fallbacks and re-auth flows:
	•	Token expiry UX: adapters return reauth_required; Studio shows a minimal scope re-auth card with purpose and TTL; never request more than was previously granted unless the user escalates.
	•	Periodic auto-revoke schedules (e.g., every 30 days) with one-click re-grant.
	•	Degraded mode: if a service is down/denied, show metadata cached view with clear banners and “retry later” job queue.
	•	Recovery: passkey recovery codes (one-time printable), social recovery (2 trusted contacts), and a manual support path; all audited.
	•	Fraud/duress: a “shadow gesture” cancels actions and triggers silent lock.
Acceptance: integration tests simulate expired tokens → reauth; service outage → degraded mode; duress gesture → lock + alert.

⸻

7) Compliance & privacy (GDPR/SOC2-style)

Prompt to Claude

Create a compliance kit:
	•	compliance/data_map.md (systems, data types, retention, lawful basis).
	•	compliance/dpia.md (privacy impact, mitigations, UL/GTΨ specifics).
	•	compliance/log_retention.yaml (per-table TTL; default 30–90 days for access logs).
	•	Add “Download/Delete my data” endpoints and background jobs.
	•	Document: no raw PII as usernames; gov IDs are attested by third parties only; phone/email are verification claims.
Acceptance: build a make compliance-check that lints presence of these docs/files and prints a summary.

⸻

8) Studio UX scaffolding (unified inbox, cloud optimizer)

Prompt to Claude

Ship the minimum Studio:
	•	Unified Inbox page (headers-only by default). When a thread is clicked, escalate scope for that thread only.
	•	Cloud Optimizer page: shows size/duplication across drive/dropbox/icloud; proposes a dry-run move plan with savings; requires GTΨ to execute.
	•	Connections page: provider cards (Google/Apple/GitHub/Microsoft/Dropbox/Drive/iCloud), granted scopes, last used, revoke button, and activity log.
	•	Legend HUD: live translation of Λ-traces to human sentences (UNL) as actions flow.
Acceptance: UI works with fake adapters; performs grant/escalate/revoke; shows audit log entries.

⸻

9) Performance & cost gates

Prompt to Claude

Add basic perf budgets and dashboards:
	•	Goals: p95 /identity/resolve-login < 30ms, p95 parser < 2ms, p95 adapter list < 150ms, Studio TTI < 2s.
	•	Prometheus/OpenTelemetry for: parse time, consent grants, adapter latency, reauth events, GTΨ verification time.
	•	Grafana panels + alerts for spikes or abnormal revoke rates.
Acceptance: dashboards render with mock load; alerts fire on induced latency.

⸻

10) Threat model & red-team drills

Prompt to Claude

Produce a threat model and tests:
	•	Scenarios: replay, shoulder-surf, video forgery, malware reading screen, stolen device, OAuth token exfil, gesture forgery with GAN, ritual poisoning (malicious symbol semantics), namespace squatting.
	•	Add chaos tests: expired tokens mid-action, adapter outage, partial consent graph corruption, clock skew.
	•	Output security/threat_model.md and tests/security/ with runnable scripts.
Acceptance: “red team” test suite runs and reports PASS/FAIL with mitigations linked.

