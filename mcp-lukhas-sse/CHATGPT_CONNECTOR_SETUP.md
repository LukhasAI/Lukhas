---
status: wip
type: documentation
---
# 🤖 ChatGPT Connector Setup for LUKHAS AI

## ⚡ Quick Setup

### 1. Add Connector to ChatGPT
1. Go to ChatGPT Settings → Beta Features → **Connectors**
2. Click "Add Connector" or "Create Connector"
3. Enter the following details:

**Base URL:** `https://lukhas-mcp-production.up.railway.app`

**OpenAPI Schema:** 
- **Option 1 (Recommended):** Auto-discovery URL: `https://lukhas-mcp-production.up.railway.app/openapi.json`
- **Option 2:** Copy/paste the schema from `chatgpt_rest_openapi.yaml`

**Authentication:** No Authentication (public API)

**Name:** LUKHAS AI Platform
**Description:** Access the LUKHAS AI Constellation Framework (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum) for consciousness-aware AI capabilities

### 2. Test the Connection
Once the connector is added and enabled, you can test with these example prompts in ChatGPT:

**Health Check:**
```
"Check if LUKHAS AI is healthy"
```
→ Will call `/health` endpoint and show server status

**System Information:**
```
"Tell me about the LUKHAS AI system and Constellation Framework"
```
→ Will call `/info` endpoint and explain the platform architecture

**Directory Operations:**
```
"What files are in the /tmp directory?"
"List the contents of /var/tmp"
```
→ Will call `/list-directory` endpoint with specified paths

**File Reading:**
```
"Read the contents of /tmp/test.txt"
"Show me the first 50 lines of /tmp/log.txt"
```
→ Will call `/read-file` endpoint with optional line limits

### 3. Verify OpenAPI Discovery
ChatGPT Connectors can auto-discover our API specification:
```
curl https://lukhas-mcp-production.up.railway.app/openapi.json
```

## 🛡️ Available Endpoints

### Health Check
- **GET** `/health`
- **Purpose:** Check if LUKHAS AI server is operational
- **Response:** Server status, version, Constellation Framework symbol

### System Information  
- **GET** `/info`
- **Purpose:** Get detailed LUKHAS AI platform information
- **Response:** Full Constellation Framework details, capabilities, architecture

### Directory Listing
- **GET** `/list-directory?path={path}`
- **POST** `/list-directory` with JSON body
- **Purpose:** List files and directories (security-restricted paths)
- **Security:** Only allowed in `/tmp`, `/var/tmp` directories

### File Reading
- **GET** `/read-file?path={path}&max_lines={limit}`
- **POST** `/read-file` with JSON body  
- **Purpose:** Read text file contents (security-restricted)
- **Security:** Max 1MB files, safe directories only

## ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum Constellation Framework Access

Once connected, ChatGPT will have access to:

- **⚛️ Identity**: System identification and authentication info
- **🧠 Consciousness**: Platform architecture and cognitive processing details  
- **🛡️ Guardian**: Security controls and ethical frameworks

## 🔧 Technical Details

**Base URL:** https://lukhas-mcp-production.up.railway.app
**Protocol:** REST API with JSON responses
**CORS:** Enabled for cross-origin requests
**Rate Limiting:** Standard Railway limits apply
**Uptime:** 99.9% via Railway hosting
**Security:** Path sandboxing, file size limits, input validation

## 🚀 What You Can Do

Ask ChatGPT to:
- "Check LUKHAS AI system health"
- "Get information about the Constellation Framework"
- "List available files in safe directories"
- "Read configuration or log files"
- "Monitor system status and capabilities"

## 🛠️ Advanced Usage

ChatGPT can combine multiple API calls:
- Check health, then get system info
- List directory, then read specific files
- Monitor system status over time
- Extract and analyze LUKHAS AI configurations

---

**Status:** ✅ PRODUCTION READY  
**Last Updated:** September 18, 2025  
**Railway URL:** https://lukhas-mcp-production.up.railway.app  
**Constellation Framework:** ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum LUKHAS AI Platform