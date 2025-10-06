---
status: wip
type: documentation
---
# LUKHAS AI ChatGPT Integration - REST API Setup

🎉 **FIXED!** The URL now works with ChatGPT Custom GPT Actions.

## ✅ **Working URL for ChatGPT**

**Base URL**: `https://lukhas-mcp-production.up.railway.app`

The issue was that ChatGPT Custom GPT Actions expect **REST API endpoints**, not raw MCP JSON-RPC protocol. We've created a REST wrapper that converts between the two.

## 🔧 **ChatGPT Custom GPT Configuration**

### **Step 1: Create Custom GPT**
1. Go to: https://chatgpt.com/gpts/editor
2. Click "Create" in top right
3. Switch to "Configure" tab

### **Step 2: Basic Information**
- **Name**: `LUKHAS AI Assistant`
- **Description**: `Access LUKHAS AI Platform through the Constellation Framework ⚛️🧠🛡️`
- **Instructions**:
```
You are connected to the LUKHAS AI Platform through REST API. You can:

1. Get system information about LUKHAS AI
2. List directories and files safely
3. Read file contents with security controls
4. Access Constellation Framework capabilities (⚛️🧠🛡️)

Always start by checking the system health, then explore available capabilities.
Use the Constellation Framework context in your responses: Identity, Consciousness, Guardian.
```

### **Step 3: Add Actions**
1. Click "Create new action"
2. **Import Schema**: Copy the entire contents of `chatgpt_rest_openapi.yaml`
3. **Or configure manually**:
   - **Authentication**: None
   - **Schema**: Paste the OpenAPI YAML content

### **Step 4: Available Endpoints**

#### **Health Check**
```
GET https://lukhas-mcp-production.up.railway.app/health
```

#### **System Information**
```
GET https://lukhas-mcp-production.up.railway.app/info
```

#### **List Directory**
```
GET https://lukhas-mcp-production.up.railway.app/list-directory?path=/tmp
```

#### **Read File**
```
GET https://lukhas-mcp-production.up.railway.app/read-file?path=/tmp/example.txt&max_lines=100
```

## 🧪 **Test Commands for ChatGPT**

Once configured, try these commands in your Custom GPT:

1. **"Check LUKHAS AI system health"**
2. **"Get information about the LUKHAS AI Platform"**
3. **"List files in the /tmp directory"**
4. **"Explain the Constellation Framework"**

## 📋 **Expected Responses**

### **Health Check Response**
```json
{
  "status": "healthy",
  "server": "LUKHAS MCP REST Wrapper for ChatGPT",
  "version": "1.0.0",
  "constellation_framework": "⚛️🧠🛡️",
  "session_id": "uuid-here"
}
```

### **System Info Response**
```json
{
  "lukhas_ai": {
    "name": "LUKHAS AI Platform",
    "description": "Consciousness-Aware AI Development Platform",
    "constellation_framework": {
      "symbol": "⚛️🧠🛡️",
      "components": {
        "⚛️ Identity": "Lambda ID system, authentication, symbolic self-representation",
        "🧠 Consciousness": "692-module cognitive processing, memory systems, awareness",
        "🛡️ Guardian": "Constitutional AI, ethical frameworks, drift detection"
      }
    }
  }
}
```

## 🔒 **Security Features**

- ✅ **Path Sandboxing**: Only `/tmp` and `/var/tmp` directories allowed
- ✅ **File Size Limits**: Maximum 1MB per file
- ✅ **Input Validation**: All parameters validated
- ✅ **CORS Enabled**: Works with ChatGPT's cross-origin requests
- ✅ **Error Handling**: Safe error responses without information leakage

## 🎯 **Why This Works Now**

1. **REST API**: ChatGPT expects REST endpoints, not MCP protocol
2. **CORS Headers**: Added for cross-origin requests from ChatGPT
3. **JSON Responses**: Proper JSON format instead of JSON-RPC
4. **OpenAPI Schema**: Complete API documentation for ChatGPT
5. **GET/POST Methods**: Both supported for flexibility

## 🚀 **Quick Verification**

Test the endpoints manually:

```bash
# Health check
curl https://lukhas-mcp-production.up.railway.app/health

# System info
curl https://lukhas-mcp-production.up.railway.app/info

# List directory
curl "https://lukhas-mcp-production.up.railway.app/list-directory?path=/tmp"
```

## ⚛️🧠🛡️ **Constellation Framework Integration**

Your ChatGPT will now have access to:
- **⚛️ Identity**: Secure file system access with session management
- **🧠 Consciousness**: Intelligent content analysis and exploration
- **🛡️ Guardian**: Security controls and safe operations

**The URL is now working with ChatGPT!** 🎉