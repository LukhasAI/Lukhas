---
status: wip
type: documentation
---
# LUKHAS MCP Server - Official Specification Compliant

This is an **official MCP v2025-06-18 specification compliant** server for the LUKHAS AI Platform, implementing the Model Context Protocol as defined by OpenAI.

## 🎯 Specification Compliance

This server fully implements the **Streamable HTTP transport** as specified in the official MCP documentation:

- ✅ **JSON-RPC 2.0** message format
- ✅ **MCP-Protocol-Version: 2025-06-18** header support
- ✅ **Server-Sent Events (SSE)** for bidirectional communication
- ✅ **Session management** with secure session IDs
- ✅ **Standard MCP methods**: `initialize`, `tools/list`, `tools/call`
- ✅ **Security**: Path validation and sandboxing
- ✅ **Error handling**: Proper JSON-RPC error responses

## 🚀 Deployment

**Production URL**: https://lukhas-mcp-production.up.railway.app

### Railway Deployment

```bash
# Deploy to Railway
railway up
```

### Local Development

```bash
# Install dependencies
pip install starlette uvicorn

# Set environment variables
export PORT=8080
export ALLOWED_ROOTS="/tmp,/var/tmp"

# Run the server
python mcp_official_server.py
```

## 🔗 Endpoints

### Health Check
```
GET /health
```

### MCP Protocol Endpoint
```
POST /mcp          # Send JSON-RPC messages to server
GET /mcp           # Receive SSE stream from server  
DELETE /mcp        # Terminate session
```

### Required Headers

```http
MCP-Protocol-Version: 2025-06-18
Content-Type: application/json
Accept: text/event-stream  # For SSE responses
Mcp-Session-Id: <session-id>  # After initialization
```

## 🛠️ Available Tools

### 1. list_directory
Lists files and directories in a given path.

**Input Schema:**
```json
{
  "path": "string (required)"
}
```

### 2. read_file
Reads the contents of a text file.

**Input Schema:**
```json
{
  "path": "string (required)",
  "max_lines": "integer (optional, default: 100)"
}
```

## 🔒 Security Features

- **Path sandboxing**: Only allows access to configured allowed roots
- **Session validation**: Secure session ID generation and validation
- **Input validation**: JSON schema validation for all tool inputs
- **Error handling**: Safe error responses without information leakage

## 📋 MCP Protocol Flow

1. **Initialization**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "initialize",
     "params": {
       "protocolVersion": "2025-06-18",
       "clientInfo": {"name": "ChatGPT", "version": "1.0"},
       "capabilities": {}
     }
   }
   ```

2. **Tool Discovery**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "tools/list"
   }
   ```

3. **Tool Execution**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 3,
     "method": "tools/call",
     "params": {
       "name": "list_directory",
       "arguments": {"path": "/tmp"}
     }
   }
   ```

## 🧪 Testing

### Health Check
```bash
curl https://lukhas-mcp-production.up.railway.app/health
```

### MCP Initialization
```bash
curl -X POST https://lukhas-mcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "clientInfo": {"name": "test", "version": "1.0"},
      "capabilities": {}
    }
  }'
```

### Tool List
```bash
curl -X POST https://lukhas-mcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

## ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum LUKHAS AI Integration

This MCP server provides ChatGPT with access to LUKHAS AI Platform capabilities:

- **⚛️ Identity**: Secure session management and authentication
- **🧠 Consciousness**: File system exploration and content analysis  
- **🛡️ Guardian**: Security validation and path sandboxing

For more information about LUKHAS AI, visit: https://github.com/LUKHAS-AI/LUKHAS

---

**Protocol Version**: 2025-06-18  
**Transport**: Streamable HTTP with SSE  
**Compliance**: Official OpenAI MCP Specification