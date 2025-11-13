# T4 Agent Onboarding Runbook

## Overview
Onboard an automated agent to the T4 Intent Platform. Agents must use `tools/t4/policy_client.py` to register intents and perform pre-PR checks. All LLM calls must use `tools/ci/llm_policy.py`.

## Steps

### 1. Request an API key (admin)
```bash
export T4_ADMIN_TOKEN="<<admin-token>>"
python3 tools/ci/create_api_key_admin.py --agent_id "claude-agent-1" --owner "platform" --expires_days 365 --daily_limit 100.0
# copy the printed key and store in agent's secret store
```

### 2. Configure the agent
```bash
export T4_INTENT_API="https://intent-api.internal:8001"
export T4_API_KEY="<agent-key>"
```

### 3. Run the certification test
```bash
python3 - <<'PY'
from tools.t4.policy_client import pre_pr_check
print(pre_pr_check(["lukhas/core/foo.py"], ["F821"]))
PY
```

The test creates reserved placeholders for missing intents (if enabled) and returns missing file list.

### 4. Policy requirements
- Always call `pre_pr_check(files, critical_codes)` prior to PR creation.
- If any critical intent is missing, either:
  - Create a reserved intent placeholder and open a draft PR, or
  - Block the PR and require human assignment.
- All LLM calls must use `tools/ci/llm_policy.py`.
- Record agent id in intent creation.

### 5. Security
- Store `T4_API_KEY` securely and rotate periodically.
- Admin token used to create keys must be kept in vault and not committed.

### 6. Troubleshooting
- Check `GET /health` on the intent API.
- Examine audit log via admin endpoints if actions are unexpected.

## Production Deployment

### Start Intent API
```bash
export T4_ADMIN_TOKEN="<strong-secret>"
export T4_RATE_REDIS="redis://localhost:6379"  # optional
uvicorn tools.ci.intent_api:APP --host 0.0.0.0 --port 8001 --workers 2
```

### Create Admin Key (first time)
```bash
curl -X POST "http://127.0.0.1:8001/admin/api_keys?admin_token=<admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"admin-user","owner":"platform","scopes":"intents:*","expires_in_days":365,"daily_limit":1000.0}'
```

### Create Agent Keys
```bash
python3 tools/ci/create_api_key_admin.py --agent_id "agent-name" --owner "team" --expires_days 365 --daily_limit 100.0
```

### Health Check
```bash
curl http://127.0.0.1:8001/health
```

## API Endpoints

### Public (requires API key)
- `GET /health` - Health check
- `POST /intents` - Create intent
- `GET /intents/stale?days=30` - List stale intents
- `GET /intents/by_owner/{owner}` - Intents by owner
- `GET /intents/by_file?file=path` - Intents by file
- `GET /intents/{intent_id}` - Get single intent
- `PATCH /intents/{intent_id}` - Update intent
- `GET /metrics/summary` - Aggregate metrics

### Admin (requires admin token)
- `POST /admin/api_keys?admin_token=X` - Create API key
- `DELETE /admin/api_keys/{key}?admin_token=X` - Revoke API key
- `GET /admin/api_keys?admin_token=X` - List all API keys
- `DELETE /intents/{intent_id}?admin_token=X` - Delete intent

## Example Workflows

### Agent Pre-PR Check
```python
from tools.t4.policy_client import pre_pr_check

files = ["lukhas/core/foo.py", "lukhas/api/bar.py"]
critical_codes = ["F821", "F401"]
missing = pre_pr_check(files, critical_codes, auto_create_reserved=True)

if missing:
    print(f"Missing intents for: {missing}")
    # Open draft PR or block merge
```

### LLM Call with Quota
```python
from tools.ci.llm_policy import call_openai_chat

result = call_openai_chat(
    prompt="Explain this code",
    model="gpt-4o-mini",
    max_completion_tokens=1024,
    agent_api_key=os.environ["T4_API_KEY"],
    agent_id="my-agent"
)
print(result["text"])
print(f"Cost: ${result['cost']:.4f}")
```

## Monitoring

### Check Agent Usage
```bash
sqlite3 reports/todos/intent_registry.db "SELECT agent_id, SUM(est_cost) as total_cost FROM llm_usage GROUP BY agent_id"
```

### Check API Key Status
```bash
curl -H "X-T4-API-KEY: <admin-key>" http://127.0.0.1:8001/admin/api_keys?admin_token=<token>
```

### Audit Log
```bash
sqlite3 reports/todos/intent_registry.db "SELECT * FROM audit_log WHERE agent_id='my-agent' ORDER BY timestamp DESC LIMIT 10"
```

## Rate Limiting

- Default: 120 requests/minute per API key
- In-process fallback if Redis not configured
- Returns 429 status code when exceeded

## Security Best Practices

1. **Never commit secrets**: Use environment variables or vault
2. **Rotate keys annually**: Set `expires_in_days` when creating keys
3. **Limit daily quotas**: Set appropriate `daily_limit` for LLM costs
4. **Monitor audit logs**: Review agent actions regularly
5. **Use TLS in production**: Deploy behind HTTPS proxy

## Rollback

If you need to disable enforcement:
```bash
# Revoke all agent keys
sqlite3 reports/todos/intent_registry.db "UPDATE api_keys SET revoked=1"

# Stop intent API
pkill -f "uvicorn tools.ci.intent_api"
```

## Support

For issues or questions:
- Check audit logs for failed requests
- Review `GET /health` endpoint status
- Contact platform team for admin token issues
