---
status: wip
type: documentation
---
# 🎯 MCP Ops Kit - HARDENED DELIVERY ✅

**Production-ready MCP server with auth, persistence, and rate limiting**

## ✅ Complete Hardening Applied

### **🔐 Security Layer**
- ✅ **API Key Authentication** - `LUKHAS_MCP_API_KEYS` env var protection
- ✅ **Rate Limiting** - Token bucket per IP (configurable limits)
- ✅ **Request Logging** - JSON structured logs with IP, UA, status
- ✅ **SSE Auth** - Header + query param support for streaming
- ✅ **401/429 Responses** - Proper error codes for unauthorized/rate-limited requests

### **💾 Persistence Layer**
- ✅ **JSON State Storage** - `.mcp-state.json` for JOBS/MODELS
- ✅ **Graceful Recovery** - Survives process restarts
- ✅ **Auto-save** - Every 3 seconds when dirty
- ✅ **Atomic Writes** - Temp file + rename for safety
- ✅ **markDirty()** - Added to all eval runner mutations

### **🔧 Operational Features**
- ✅ **Health Endpoint** - `HEAD /healthz` for monitoring
- ✅ **Environment Config** - `LUKHAS_REPO_ROOT`, `MCP_STATE_PATH`, rate limit tuning
- ✅ **CI Integration** - GitHub Actions updated with auth headers
- ✅ **Documentation** - Security & persistence guide added

## 🧪 Validation Results

### **Auth Protection Working**
```bash
# With key: ✅ 23 tools
curl -H 'X-API-Key: test-key-123' → 23 tools

# Without key: ✅ Rejected  
curl (no auth) → "Unauthorized"
```

### **Persistence Working**
```bash
# Job creation persisted
run_eval → job_27ta0pfj created
ls .mcp-state.json → 976 bytes, 2 jobs stored
```

### **Health Check Working**
```bash
curl -I /healthz → HTTP/1.1 200 OK
```

## 🚀 Production Deployment Ready

### **Environment Variables**
```bash
# Required for production
export LUKHAS_REPO_ROOT="/path/to/lukhas"
export LUKHAS_MCP_API_KEYS="prod-key-1,backup-key-2"

# Optional tuning
export MCP_RL_WINDOW_MS=10000  # Rate limit window
export MCP_RL_BUCKET=60        # Requests per window
export MCP_STATE_PATH="/var/lib/lukhas/.mcp-state.json"
```

### **Production Checklist**
- ✅ **Security**: API keys configured, rate limits active
- ✅ **Reliability**: Persistence working, health checks enabled  
- ✅ **Monitoring**: Structured logging, request tracing
- ✅ **CI/CD**: Auth integrated in GitHub Actions
- ✅ **Documentation**: Security guide and examples provided

### **Backend Integration Path**
```javascript
// Current: In-memory with JSON persistence
const JOBS = new Map();           // → Persisted to .mcp-state.json
const MODELS = new Map();         // → Survives restarts

// Next: Real backend integration (wire format unchanged!)
const JOBS = evalOrchestrator;    // → Real eval orchestrator API
const MODELS = modelRegistry;     // → Real model registry API
```

## 🎯 Mission Accomplished

**Zero downtime migration**: Existing ChatGPT connectors continue working unchanged while gaining enterprise-grade security and reliability. 

**Matriz-ready**: No more "what ifs" - auth, persistence, monitoring, and CI all locked in for production deployment.

---

**🔒 Security**: API-key protected, rate-limited, logged  
**💾 Persistence**: JSON state storage, restart-safe  
**🔧 Operations**: Health checks, monitoring, CI integration  
**📋 Documentation**: Complete security & persistence guide  

**Wire Contract Status**: 🔒 **LOCKED** - Zero breaking changes to existing integrations!