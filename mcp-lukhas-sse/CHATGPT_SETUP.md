---
status: wip
type: documentation
---
# 🤖 ChatGPT MCP Server Setup

## 🚨 **IMPORTANT: ChatGPT Can't Access Localhost**

ChatGPT runs on OpenAI's servers and **cannot access `http://localhost:8080`**. You need to expose your server to the internet.

## 🔧 **Solution Options**

### **Option 1: Use ngrok (Recommended)**
```bash
# Install ngrok first: https://ngrok.com/download
# Sign up and get authtoken: https://dashboard.ngrok.com/get-started/your-authtoken

# Expose your server
ngrok http 8080

# This will give you a public URL like: https://abc123.ngrok.io
```

### **Option 2: No-Auth Mode for Testing**
Your server now supports **no authentication** for testing:

**Current Server Settings:**
- URL: `http://localhost:8080/sse` (localhost only)
- Authentication: **DISABLED** (ALLOW_NO_AUTH=true)
- Available without any token

### **Option 3: Multiple Auth Methods**
Your server now supports:

1. **Bearer Token (Standard)**:
   ```
   Authorization: Bearer YOUR_TOKEN
   ```

2. **API Key Header** (ChatGPT might prefer this):
   ```
   X-API-Key: YOUR_TOKEN
   ```

3. **Query Parameter** (for testing):
   ```
   http://localhost:8080/sse?token=YOUR_TOKEN
   ```

## 🧪 **Your Working Server Details**

**Health Check:** `http://localhost:8080/health`
**MCP Endpoint:** `http://localhost:8080/sse`

**Your JWT Token:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Rlc3QtaXNzdWVyLmxvY2FsIiwiYXVkIjoiYXBpOi8vbHVraGFzLW1jcCIsInN1YiI6InRlc3QtdXNlci0xMjMiLCJpYXQiOjE3NTgxNTA5NjEsImV4cCI6MTc1ODE1NDU2MSwic2NvcGUiOiJyZWFkOmZpbGVzIHdyaXRlOmZpbGVzIn0.u1_MC0yAYVoEAu4tiztGb_Vuz9uTvzi2UDKVDTxUJww
```

## 🌐 **For ChatGPT Integration**

### **Step 1: Expose with ngrok**
```bash
# In terminal 1 - keep your server running
cd /Users/cognitive_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse
ALLOWED_ROOTS="/Users/cognitive_dev/LOCAL-REPOS/Lukhas" ALLOW_NO_AUTH=true python3 chatgpt_server.py

# In terminal 2 - expose to internet
ngrok http 8080
```

### **Step 2: Use ngrok URL in ChatGPT**
When ngrok gives you a URL like `https://abc123.ngrok.io`, use:

**For ChatGPT Custom GPT:**
- **API Endpoint:** `https://abc123.ngrok.io/sse`
- **Authentication:** None (no-auth mode) OR X-API-Key with your token
- **Schema:** OpenAPI/Custom actions

## ⚡ **Quick Test Commands**

```bash
# Test without auth (should work)
curl http://localhost:8080/sse

# Test with X-API-Key (ChatGPT style)
curl -H "X-API-Key: YOUR_TOKEN" http://localhost:8080/sse

# Test with Bearer token (standard)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/sse

# Test with query param
curl "http://localhost:8080/sse?token=YOUR_TOKEN"
```

## 🔒 **Security Notes**

- **No-auth mode** is enabled for testing - disable for production
- **ngrok URLs** are publicly accessible - anyone can reach them
- Use **real OAuth** providers for production (Auth0, Clerk, Firebase)

## 🛠️ **Server Management**

**Start Server:**
```bash
cd /Users/cognitive_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse
ALLOWED_ROOTS="/Users/cognitive_dev/LOCAL-REPOS/Lukhas" ALLOW_NO_AUTH=true python3 chatgpt_server.py &
```

**Stop Server:**
```bash
pkill -f chatgpt_server
```

**Check Status:**
```bash
curl http://localhost:8080/health
```