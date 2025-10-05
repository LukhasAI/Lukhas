# 🔌 LUKHAS-MCP ChatGPT Connector Configuration

## ✅ **WORKING PUBLIC ENDPOINT**
**Base URL:** `https://acb519bafa80.ngrok-free.app`
**MCP Endpoint:** `https://acb519bafa80.ngrok-free.app/mcp`
**Health Check:** `https://acb519bafa80.ngrok-free.app/health`

---

## 🛠️ **ChatGPT Configuration Steps**

### **Step 1: Open ChatGPT Settings**
1. Go to **Settings** → **Connectors**
2. Click **+ Add Connector** or find **LUKHAS-MCP** if already added

### **Step 2: Configure LUKHAS-MCP Connector**

```json
{
  "name": "LUKHAS-MCP",
  "endpoint": "https://acb519bafa80.ngrok-free.app/mcp",
  "transport": "HTTP",
  "authentication": {
    "type": "none"
  },
  "headers": {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }
}
```

### **Step 3: Copy-Paste Values**

**Field Mapping:**
- **Connector Name:** `LUKHAS-MCP`
- **Endpoint/Host:** `https://acb519bafa80.ngrok-free.app/mcp`
- **Transport:** `HTTP` (not WebSocket or stdio)
- **Authentication:** `None` (no API key required)
- **Required Headers:** 
  - `Content-Type: application/json`
  - `Accept: application/json`

### **Step 4: Test Connection**
After saving, ChatGPT should automatically test the connection. You should see:
- ✅ **Connection successful**
- ✅ **27 tools discovered** (including WHY, file operations, canary management)

---

## 🚨 **Common Issues & Quick Fixes**

### **Issue: Toggle Still Disabled**
**Cause:** Org policy or plan restrictions
**Fix:** Ask your admin to enable **Custom MCP Connectors** in workspace settings

### **Issue: "Connection Failed"**
**Cause:** ngrok tunnel might have expired
**Fix:** Check if URL is still active:
```bash
curl -s https://acb519bafa80.ngrok-free.app/health
```

### **Issue: "Transport Mismatch"**
**Cause:** Wrong transport type selected
**Fix:** Ensure **HTTP** is selected, NOT WebSocket or stdio

### **Issue: "Authentication Required"**
**Cause:** Wrong auth settings
**Fix:** Set authentication to **None** (our server doesn't require auth)

---

## 🎛️ **Verify Working Connection**

Once enabled, test in ChatGPT:
```
/ Use Connectors → LUKHAS-MCP

Ask: "List the available LUKHAS development tools"
```

You should see all 27 tools including:
- **search/fetch** (LUKHAS knowledge)
- **why/why_math** (audit narratives)
- **file operations** (create_file, write_file, etc.)
- **canary management** (start_canary, canary_status)
- **evaluation tools** (run_eval, status)

---

## 🔄 **If ngrok URL Changes**

The ngrok URL `https://acb519bafa80.ngrok-free.app` will change when restarted. 

**To get new URL:**
```bash
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

**Then update ChatGPT connector endpoint accordingly.**

---

## 🎉 **Success Indicators**

✅ **Toggle enabled** (no longer grayed out)
✅ **Green status** in connector list  
✅ **Tools work** when using `/` in ChatGPT
✅ **WHY button** works in cockpit: https://acb519bafa80.ngrok-free.app/cockpit.html

**You're ready for Matriz rollout!** 🚀