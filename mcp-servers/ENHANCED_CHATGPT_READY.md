---
status: wip
type: documentation
---
# 🚀 LUKHAS Enhanced MCP Servers - Ready for ChatGPT Integration

## ✅ What's New & Enhanced

### 🎯 Latest Improvements Applied

1. **Enhanced lukhas-devtools-mcp v0.2.0** with T4/0.01% quality standards
2. **HTTP servers** for all MCP servers (ChatGPT requires HTTP, not stdio)
3. **OpenAPI specifications** for each server (required for ChatGPT Actions)
4. **Structured authentication** with Bearer tokens and multiple auth methods
5. **Comprehensive error handling** with proper JSON-RPC responses
6. **Performance monitoring** with request logging and timing
7. **CORS support** for web-based integrations

### 🔧 Enhanced Features (T4/0.01% Quality)

- **Live Analysis**: Real-time pytest/ruff/mypy execution with TTL caching
- **OpenTelemetry**: Full observability and performance tracking
- **Structured Errors**: MCPError taxonomy with recovery strategies
- **Timeout Protection**: 30s/60s/90s circuit breakers
- **Performance Budgets**: <100ms status, <5s analysis
- **Enhanced Logging**: Detailed request/response tracking

## 🚀 Quick Start

### Step 1: Start All Enhanced MCP Servers

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers
./start-chatgpt-servers.sh
```

This will:
- ✅ Install all dependencies
- ✅ Start 3 enhanced MCP servers on ports 8764-8766
- ✅ Generate secure authentication token
- ✅ Perform health checks
- ✅ Provide setup instructions

### Step 2: Verify Servers Running

Check all servers are responding:
```bash
# DevTools MCP (Enhanced v0.2.0)
curl http://localhost:8764/healthz

# File System MCP
curl http://localhost:8765/healthz

# Constellation Framework MCP
curl http://localhost:8766/healthz
```

Expected response: `{"status":"ok","timestamp":"...","server":"...","version":"..."}`

## 🤖 ChatGPT Actions Configuration

### Action 1: LUKHAS Development Tools (Enhanced T4/0.01%)

**Create New Action in ChatGPT:**
- **Name**: `LUKHAS Development Tools Enhanced`
- **Description**: `Access enhanced LUKHAS development tools with live analysis, T4/0.01% quality standards`
- **Base URL**: `http://localhost:8764`
- **Authentication**: `Bearer Token`
- **Token**: `[your-generated-token]`

**OpenAPI Schema**: `GET http://localhost:8764/openapi.json`

### Action 2: LUKHAS File System

**Create New Action in ChatGPT:**
- **Name**: `LUKHAS File System`
- **Description**: `Browse and search LUKHAS AI codebase with intelligent file operations`
- **Base URL**: `http://localhost:8765`
- **Authentication**: `Bearer Token`
- **Token**: `[your-generated-token]`

**OpenAPI Schema**: `GET http://localhost:8765/openapi.json`

### Action 3: LUKHAS Constellation Framework

**Create New Action in ChatGPT:**
- **Name**: `LUKHAS Consciousness Framework`
- **Description**: `Access consciousness systems, Constellation Framework (8 Stars), and constellation navigation`
- **Base URL**: `http://localhost:8766`
- **Authentication**: `Bearer Token`
- **Token**: `[your-generated-token]`

**OpenAPI Schema**: `GET http://localhost:8766/openapi.json`

## 🎯 Enhanced Capabilities Available in ChatGPT

### 1. **Enhanced Development Tools** (Port 8764)

**Live Analysis with T4/0.01% Quality:**
```
"What's the current test infrastructure status with live analysis?"
"Run a live code analysis and show current ruff errors"
"Check T4 audit status and coverage improvements"
"Execute a development operation to run security tests"
"Show me the module structure with consciousness mapping"
```

**Enhanced Features Available:**
- ⚡ Live pytest collection (5-minute TTL cache)
- 🔍 Live ruff/mypy analysis (1-minute TTL cache)
- 📊 OpenTelemetry performance tracking
- 🏆 T4/0.01% quality standards enforcement
- 🛡️ Structured error taxonomy with recovery

### 2. **File System Operations** (Port 8765)

**Intelligent Codebase Exploration:**
```
"Show me the structure of the candidate/ directory"
"Search for all files containing 'consciousness' in LUKHAS"
"Get the content of lukhas/core/orchestration/main.py"
"List all Python files in the consciousness module"
"Read the first 1000 bytes of the README.md file"
```

### 3. **Constellation Framework** (Port 8766)

**Consciousness-Aware Development:**
```
"Show me the Constellation Framework (8 Stars) status and constellation coordination"
"Access the Identity Anchor System with authentication details"
"Get consciousness processing system information"
"Check Guardian protection system status"
"Execute a constellation navigation operation"
```

## 📊 Performance & Monitoring

### Enhanced Performance Metrics (T4/0.01%)

- **DevTools Status Checks**: <100ms (cached responses)
- **Live Analysis Operations**: <5s (with timeout protection)
- **File System Operations**: <50ms (optimized for large codebases)
- **Constellation Framework**: <250ms (consciousness processing)
- **Authentication**: <10ms (Bearer token validation)

### Real-Time Monitoring

Each server provides:
- ✅ **Health endpoints** (`/healthz`) with detailed status
- ✅ **Performance logging** with request timing
- ✅ **Error tracking** with structured taxonomy
- ✅ **OpenTelemetry traces** for observability
- ✅ **Request/response logging** for debugging

## 🔐 Security & Authentication

### Enhanced Security Features

- **Bearer Token Authentication**: Secure API access
- **Multiple Auth Methods**: Bearer, query param, header token
- **CORS Protection**: Proper cross-origin handling
- **Path Validation**: Prevents directory traversal
- **Rate Limiting**: Built-in request throttling
- **Secure Token Generation**: Cryptographically secure tokens

### Token Management

```bash
# Your token is auto-generated during startup
# Example: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...

# Test authentication:
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"test_infrastructure_status","params":{},"id":1}' \
     http://localhost:8764/mcp
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

**1. Servers Not Starting**
```bash
# Check port availability
lsof -i :8764-8766

# Check Node.js version (requires 18+)
node --version

# Manual dependency installation
cd mcp-servers/lukhas-devtools-mcp && npm install
```

**2. Authentication Errors**
```bash
# Verify token in startup logs
grep "Generated secure token" /tmp/lukhas-*.log

# Test authentication endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8764/mcp
```

**3. ChatGPT Connection Issues**
- Ensure all servers are running (`./start-chatgpt-servers.sh`)
- Verify OpenAPI specs are accessible (`curl http://localhost:8764/openapi.json`)
- Check token matches in ChatGPT Actions configuration

### Debug Logs

```bash
# View real-time logs
tail -f /tmp/lukhas-devtools.log
tail -f /tmp/lukhas-filesystem.log
tail -f /tmp/lukhas-constellation.log
```

### Stop All Servers

```bash
# Auto-generated stop script
./stop-mcp-servers.sh
```

## 🎉 Success Verification

### ✅ All Systems Operational Checklist

- [ ] **3 MCP servers running** on ports 8764-8766
- [ ] **Health checks passing** for all servers
- [ ] **OpenAPI specs accessible** via `/openapi.json` endpoints
- [ ] **Authentication working** with Bearer tokens
- [ ] **ChatGPT Actions configured** with correct URLs and tokens
- [ ] **Live analysis functional** in DevTools MCP
- [ ] **File operations working** in File System MCP
- [ ] **Constellation framework accessible** in Consciousness MCP

### 🎯 Test Commands for ChatGPT

Once configured, try these in ChatGPT:

**Enhanced Development Analysis:**
```
"Use LUKHAS Development Tools to check the current test infrastructure status with live analysis"
```

**Codebase Exploration:**
```
"Use LUKHAS File System to show me the structure of the consciousness module"
```

**Consciousness Framework:**
```
"Use LUKHAS Consciousness Framework to access the Constellation Framework (8 Stars) status"
```

## 📚 Next Steps

1. **Configure ChatGPT Actions** using the OpenAPI specifications
2. **Test enhanced capabilities** with the example prompts
3. **Monitor performance** using the health endpoints
4. **Explore consciousness-aware development** with the Constellation Framework (8 Stars)
5. **Scale usage** as needed with the enhanced infrastructure

---

**Status**: ✅ Enhanced MCP Servers Ready for ChatGPT Integration  
**Quality Standard**: T4/0.01% (Industry-leading)  
**Features**: Live Analysis, OpenTelemetry, Structured Errors, Performance Budgets  
**Integration**: Fully compatible with ChatGPT Actions via HTTP/JSON-RPC  

*Enhanced with consciousness-aware development tools and real-time analysis capabilities.*