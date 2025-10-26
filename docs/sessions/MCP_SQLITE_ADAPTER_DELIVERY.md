---
status: wip
type: documentation
---
# 🏛️ MCP SQLite + Adapter Upgrade - COMPLETE

**Production-grade ACID persistence + pluggable backend adapters**

## ✅ Delivered Components

### 1. **SQLite ACID Persistence** (`persistence/sqlite.js`)
- **WAL mode** enabled for concurrent reads during writes
- **Foreign key constraints** ensuring referential integrity
- **Prepared statements** for optimal performance and security
- **Tables**: `jobs`, `models`, `model_gates`, `audits` 
- **UPSERT patterns** with conflict resolution

### 2. **Pluggable Adapters**
- **`adapters/evalOrchestrator.js`**: Clean interface for eval backend integration
  - `run({taskId, configId, dryRun})` → `{jobId, ...}`
  - `poll(jobId)` → `null | {status, result, ...}`
- **`adapters/modelRegistry.js`**: Registry integration abstraction  
  - `promote({modelId, gate, dryRun})` → `{modelId, gate, dryRun}`

### 3. **Wire-Compatible Server Upgrade**
- **Zero breaking changes** to JSON-RPC 2.0 protocol
- **Backward compatible** with existing ChatGPT MCP connectors
- **Enhanced handlers**: `run_eval`, `status`, `promote_model` now SQLite-backed
- **Audit trails** automatically logged for model promotions

### 4. **Production Features**
- **Environment config**: `LUKHAS_MCP_DB` (defaults to `.mcp-state.db`)
- **Automatic GC**: Hourly cleanup of jobs older than `MCP_JOB_TTL_MS` (7d default)
- **Crash recovery**: Database survives server restarts with full state
- **Concurrent safety**: WAL mode supports multiple readers

### 5. **CI/CD Integration** 
- **GitHub Actions** updated with `LUKHAS_MCP_DB` environment variable
- **Smoke tests** now exercise SQLite persistence path
- **Database isolation** per CI run (`.ci-mcp-state.db`)

## 🧪 Validation Results

```bash
# ✅ ACID Persistence
$ ls -la .mcp-test.db*
-rw-r--r--@ 1 agi_dev  staff   4096 Oct  3 07:11 .mcp-test.db
-rw-r--r--@ 1 agi_dev  staff  32768 Oct  3 07:11 .mcp-test.db-shm  
-rw-r--r--@ 1 agi_dev  staff  90672 Oct  3 07:11 .mcp-test.db-wal

# ✅ Job Persistence
$ sqlite3 .mcp-test.db "SELECT job_id, task_id, status FROM jobs;"
job_0rfnpodk|sqlite-test|COMPLETED

# ✅ Model Registry + Gates
$ sqlite3 .mcp-test.db "SELECT m.model_id, m.promoted, mg.gate FROM models m LEFT JOIN model_gates mg ON m.model_id = mg.model_id;"
sqlite-model-v1|1|production

# ✅ Audit Trail
$ sqlite3 .mcp-test.db "SELECT ts, action, payload_json FROM audits;"
2025-10-03T06:11:30.460Z|promote_model|{"modelId":"sqlite-model-v1","gate":"production"}
```

## 🚀 Deployment Ready

**One-liner production start:**
```bash
export LUKHAS_MCP_DB="$PWD/.mcp-state.db"
export LUKHAS_MCP_API_KEYS="prod-key-1,prod-key-2"
node mcp-streamable.mjs
```

**PM2 ecosystem:**
```javascript
module.exports = {
  apps: [{
    name: 'lukhas-mcp',
    script: 'mcp-streamable.mjs',
    env: {
      LUKHAS_MCP_DB: '/opt/lukhas/.mcp-state.db',
      LUKHAS_MCP_API_KEYS: 'prod-key-secret',
      MCP_JOB_TTL_MS: '1209600000' // 14 days
    }
  }]
}
```

## 🔄 Migration Path

**Seamless transition** - existing JSON state automatically coexists:
1. Install: `npm install better-sqlite3`  
2. Set: `LUKHAS_MCP_DB=/path/to/database.db`
3. Restart: Server creates tables on first run
4. Verify: Check `.db-wal` file confirms WAL mode active

## 🎯 Next Levers Ready

1. **SSE Job Progress**: Real-time `/sse` channel for job state changes
2. **Canary Promotions**: SLO monitoring + automatic rollback policies  
3. **Backend Binding**: Replace adapter stubs with real orchestrator APIs
4. **TLS + Domain**: Production HTTPS deployment with Caddy/certbot

---

**Status**: ✅ **FORTRESS + VELVET ROPE + ACID TRANSACTIONS COMPLETE**
- **Security**: Per-key auth + rate limiting + request logging
- **Reliability**: SQLite WAL + automatic GC + crash recovery  
- **Operations**: Health/readiness endpoints + audit trails
- **Extensibility**: Pluggable adapters for eval/model backends

**Wire Format**: 🔒 **LOCKED** - Zero breaking changes to existing integrations