# RFC-0009 — Guardian Policy (PEP/PDP)

**Problem:** unify scope checks with rich policy (ABAC) while keeping OpenAI-compatible errors.
**Design:**

* **Model:** Subject(org_id, user_id, scopes), Action(route, verb), Resource(model, collection, sensitivity), Context(ip, time, plan).
* **Policy file:** `configs/policy/guardian_policies.yaml`
* **PDP:** pure-python matcher; first-applicable; default-deny.
* **PEP:** FastAPI dependencies `require_scope`, `require_policy(resource)`.
