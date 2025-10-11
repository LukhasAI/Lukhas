# Contracts Reference Checks — Troubleshooting

This guide helps resolve CI failures from:
- `scripts/validate_contract_refs.py`
- `docs/check_links.py` (when linking to contracts in docs)

## Contract IDs: Naming Rules

- Format: **`<topic>@v<major>`**
- Allowed chars in `<topic>`: `[a-z0-9_.:-]+`
- Examples:
  - `memory.write@v1`
  - `guardian.policy.violation@v1`
  - `identity.oauth.callback@v2`

## Typical Failure Messages

- **`invalid contract id: X`**
  - The ID doesn't match `<topic>@v<major>`.
  - ✅ Fix: Rename to `something.meaningful@v1`.

- **`unknown contract: X`**
  - A manifest references a contract not found in `contracts/`.
  - ✅ Fix: Create `contracts/<ID>.json` with a JSON Schema for the payload.

- **Anchor mismatch (`[FAIL missing anchor]`)**
  - A Markdown link uses `#heading` that doesn't exist in the target file.
  - ✅ Fix: Ensure the target page has a `# Heading` that slugifies to that anchor.

## How to Add a New Contract

1. Pick an ID:
   - `my.feature.event@v1`
2. Create schema:
   - `contracts/my.feature.event@v1.json`
3. Update manifests that publish/subscribe:
   - `observability.events.publishes/subscribes` list must include the exact ID.
4. Validate locally:
   ```bash
   python scripts/validate_contract_refs.py
   python docs/check_links.py --root .
```

## Versioning Guidance

* Backward-compatible changes: expand schema in place (still `@v1`).
* Breaking changes: bump to `@v2` and keep both schemas side-by-side until migration completes.

## Quick Checklist

* [ ] IDs conform to `<topic>@v<major>`
* [ ] Schema exists under `contracts/`
* [ ] Manifests reference existing IDs
* [ ] Docs link to the right files/anchors
* [ ] CI green: contract validator & link checker
