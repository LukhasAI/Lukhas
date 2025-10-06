---
status: wip
type: documentation
---
# 🚀 LUKHAS DevTools API for ChatGPT (Simple REST Approach)

## ✅ **SOLUTION: Regular ChatGPT Action (Not MCP)**

The MCP connector was causing timeouts. This is a **simple REST API** that ChatGPT can use as a regular "Action" instead.

---

## 🎯 **ChatGPT Action Configuration**

### **Action Name:**
```
LUKHAS DevTools
```

### **Description:**
```
Access LUKHAS development infrastructure status, code analysis, utilities, and architecture information. Get real-time insights into a T4/0.01% quality consciousness system with 775+ tests and 692 cognitive modules.
```

### **Schema (Import URL):**
```
https://fd743631a261.ngrok-free.app/openapi.json
```

### **Authentication:**
```
None
```

---

## 📊 **Available API Endpoints**

Once configured, ChatGPT can access these endpoints:

### 🏗️ **Infrastructure Status**
- **GET** `/infrastructure` - Testing infrastructure status (775+ tests)
- Returns: operational status, test counts, stability metrics

### 📈 **Code Analysis** 
- **GET** `/analysis` - Codebase health metrics and quality scores
- Returns: health score, metrics, recent improvements

### 🛠️ **Development Utilities**
- **GET** `/utilities` - Available development tools and utilities  
- Returns: testing tools, linting, security scanning, performance monitoring

### 🏛️ **Module Structure**
- **GET** `/structure` - LUKHAS architecture and module information
- Returns: 692 cognitive modules, consciousness architecture, domains

### ❤️ **Health Check**
- **GET** `/health` - Simple health check endpoint
- Returns: server status and timestamp

---

## 🧪 **Test the API**

You can test these endpoints directly:

```bash
# Infrastructure status
curl https://fd743631a261.ngrok-free.app/infrastructure

# Code analysis
curl https://fd743631a261.ngrok-free.app/analysis

# Development utilities
curl https://fd743631a261.ngrok-free.app/utilities

# Module structure  
curl https://fd743631a261.ngrok-free.app/structure

# Health check
curl https://fd743631a261.ngrok-free.app/health
```

---

## 🔧 **Why This Works Better**

### ❌ **MCP Issues:**
- Complex protocol that ChatGPT had trouble validating
- Timeout during connector creation process
- Authentication complexities

### ✅ **REST API Benefits:**
- Simple HTTP GET requests
- Standard OpenAPI specification
- Fast response times (~100ms)
- No complex protocol negotiations
- Direct ChatGPT Actions compatibility

---

## 📋 **Setup Instructions**

### Step 1: Go to ChatGPT Settings
1. Settings → Features → Actions
2. Create new Action

### Step 2: Configure the Action
- **Name**: `LUKHAS DevTools`
- **Import from URL**: `https://fd743631a261.ngrok-free.app/openapi.json`
- **Authentication**: None
- **Privacy**: Not required for personal use

### Step 3: Test
Ask ChatGPT: "What's the LUKHAS infrastructure status?" or "Analyze the LUKHAS codebase"

---

## 🎉 **Expected Results**

ChatGPT will be able to:
- ✅ Check LUKHAS testing infrastructure (775+ tests)
- ✅ Get code quality metrics and health scores
- ✅ Access development utilities information
- ✅ Explore the consciousness architecture (692 modules)
- ✅ Monitor system health and performance

---

## 🌟 **Sample Questions for ChatGPT**

Once configured, try asking:

- "What's the current LUKHAS infrastructure status?"
- "How is the LUKHAS codebase health?"
- "What development tools are available in LUKHAS?"
- "Tell me about the LUKHAS module structure"
- "Is the LUKHAS system healthy?"

---

## 🔧 **Technical Details**

- **Server**: Node.js REST API
- **Port**: 8765 (tunneled through ngrok)
- **Tunnel**: `https://fd743631a261.ngrok-free.app`
- **Response Time**: ~100ms
- **Format**: JSON responses
- **CORS**: Enabled for ChatGPT access
- **Quality**: T4/0.01% excellence standards

---

*This simple REST approach should resolve the timeout issues and provide reliable access to LUKHAS development tools through ChatGPT!* 🚀