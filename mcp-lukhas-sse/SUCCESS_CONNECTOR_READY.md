---
status: wip
type: documentation
---
# ✅ ChatGPT Connector - READY FOR USE!

## 🎉 Status: OPERATIONAL

Your LUKHAS AI REST API is now **fully deployed** and **ChatGPT Connector ready**!

### 🔗 Live Endpoints

**Base URL:** https://lukhas-mcp-production.up.railway.app

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/health` | Health check | Server status and Constellation Framework |
| `/info` | System info | Complete LUKHAS AI platform details |
| `/list-directory?path=/tmp` | List files | Secure directory browsing |
| `/read-file?path=/tmp/file.txt` | Read files | Secure file reading (max 1MB) |
| `/openapi.json` | API Schema | Auto-discovery for ChatGPT Connectors |

### 🤖 ChatGPT Connector Setup

**In ChatGPT:**
1. Settings → Beta Features → **Connectors**
2. Add Connector with:
   - **Base URL:** `https://lukhas-mcp-production.up.railway.app`
   - **OpenAPI:** `https://lukhas-mcp-production.up.railway.app/openapi.json`
   - **Auth:** No Authentication

### 🧪 Test Commands

**Health Check:**
```bash
curl https://lukhas-mcp-production.up.railway.app/health
# ✅ {"status":"healthy","constellation_framework":"⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum",...}
```

**Constellation Framework Info:**
```bash
curl https://lukhas-mcp-production.up.railway.app/info | jq .lukhas_ai.constellation_framework
# ✅ Shows ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian details
```

**OpenAPI Discovery:**
```bash
curl https://lukhas-mcp-production.up.railway.app/openapi.json | jq .info.title
# ✅ "LUKHAS AI REST API"
```

### 🎯 What ChatGPT Can Do

Once connected, ChatGPT can:
- ✅ Check LUKHAS AI system health
- ✅ Get Constellation Framework information (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum)
- ✅ Browse safe directories (`/tmp`, `/var/tmp`)
- ✅ Read text files securely (max 1MB)
- ✅ Access full platform architecture details
- ✅ Monitor system status and capabilities

### 🛡️ Security Features

- **Path Sandboxing:** Only `/tmp` and `/var/tmp` allowed
- **File Size Limits:** Maximum 1MB per file
- **Input Validation:** All parameters sanitized
- **CORS Enabled:** Cross-origin requests supported
- **Error Handling:** Safe error messages

### 🚀 What's Next

1. **Add the connector in ChatGPT** using the setup above
2. **Test with simple prompts** like "Check LUKHAS AI health"
3. **Explore the Constellation Framework** through ChatGPT conversations
4. **Monitor usage** via Railway dashboard

### 📊 System Status

- **Deployment Platform:** Railway (99.9% uptime)
- **Server Status:** ✅ HEALTHY
- **Constellation Framework:** ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum ACTIVE
- **Security:** ✅ ENABLED
- **CORS:** ✅ CONFIGURED
- **OpenAPI:** ✅ AVAILABLE

---

**🎉 You're all set! ChatGPT can now connect to your LUKHAS AI platform!**

*Constellation Framework: ⚛️ Identity • 🧠 Consciousness • 🛡️ Guardian*