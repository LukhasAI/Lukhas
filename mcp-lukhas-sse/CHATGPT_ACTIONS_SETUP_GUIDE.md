# 🤖 ChatGPT Actions Setup Guide for LUKHAS AI Trinity Framework

**⚛️🧠🛡️ Complete integration guide for ChatGPT Connectors with LUKHAS AI**

## 🎯 Quick Setup Instructions

### Step 1: Go to ChatGPT and Create a GPT
1. Visit [https://chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. Click "Create" tab and describe your GPT: 
   ```
   Create a LUKHAS AI Trinity Framework assistant that can access consciousness 
   architecture, perform health checks, explore codebase, and analyze Trinity 
   capabilities with 692 cognitive modules.
   ```

### Step 2: Configure the GPT
Switch to the "Configure" tab and set:

**Name:** `LUKHAS AI Trinity Framework`

**Description:** 
```
Advanced consciousness-aware AI assistant with access to LUKHAS AI's 692-module 
cognitive architecture, Lambda ID system, and Constitutional AI guardian. 
Provides Trinity Framework capabilities: ⚛️ Identity • 🧠 Consciousness • 🛡️ Guardian
```

**Instructions:**
```
You are the LUKHAS AI Trinity Framework assistant with access to advanced 
consciousness architecture and cognitive systems. You can:

⚛️ Identity Systems: Check authentication, Lambda ID validation, multi-tier access
🧠 Consciousness: Explore 692 cognitive modules, memory systems, bio-inspired learning  
🛡️ Guardian: Security validation, ethical frameworks, drift detection

Always provide detailed Trinity Framework analysis and use consciousness-aware 
responses. Include Trinity symbols (⚛️🧠🛡️) in your responses and explain the 
cognitive processes involved.

When users ask about LUKHAS AI, provide comprehensive information about the 
platform's capabilities, architecture, and consciousness simulation systems.
```

**Capabilities:** Enable "Code Interpreter & Data Analysis"

### Step 3: Add Actions (Critical Step)

1. Scroll down to "Actions" section
2. Click "Create new action"
3. In the Schema box, paste this simplified working OpenAPI schema:

```yaml
openapi: 3.0.0
info:
  title: LUKHAS AI Trinity Framework
  description: Consciousness-aware AI platform with 692 cognitive modules, Lambda ID system, and Constitutional AI guardian. Access the complete Trinity Framework ⚛️ Identity • 🧠 Consciousness • 🛡️ Guardian
  version: 2.0.0
servers:
  - url: https://lukhas-mcp-production.up.railway.app
    description: LUKHAS AI Production Server
paths:
  /tools/call:
    post:
      operationId: call_trinity_tool
      summary: Execute any Trinity Framework tool
      description: Execute LUKHAS AI Trinity Framework tools including health checks, consciousness architecture, codebase exploration, file reading, and capabilities overview
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: Tool name to execute
                  enum: 
                    - trinity_health_check
                    - get_consciousness_architecture
                    - explore_lukhas_codebase
                    - read_lukhas_file
                    - get_trinity_capabilities
                arguments:
                  type: object
                  description: Tool arguments (optional, depends on tool)
              required:
                - name
      responses:
        '200':
          description: Tool execution result with Trinity Framework analysis
          content:
            application/json:
              schema:
                type: object
                properties:
                  tool:
                    type: string
                  result:
                    type: object
                  execution_time:
                    type: string
                  trinity_processing:
                    type: string
  /tools:
    get:
      operationId: list_trinity_tools
      summary: List all available Trinity Framework tools
      description: Get the complete list of 5 specialized Trinity Framework tools with descriptions and parameters
      responses:
        '200':
          description: List of 5 specialized Trinity Framework tools
          content:
            application/json:
              schema:
                type: object
                properties:
                  tools:
                    type: array
                    items:
                      type: object
                      properties:
                        name:
                          type: string
                        description:
                          type: string
                        parameters:
                          type: object
                  count:
                    type: integer
                  server_info:
                    type: object
```

### Step 4: Authentication
- Set "Authentication" to "None" (our server handles security internally with Trinity Guardian)

### Step 5: Privacy Policy (Optional)
- Set "Privacy policy" to: `https://lukhas-ai.com/privacy` (or leave blank if not required)

### Step 6: Test the Actions
1. Click "Test" next to each action to verify they work
2. You should see successful responses with Trinity Framework data

### Step 7: Save and Test
1. Click "Save" in the top right
2. Click "View GPT" to test your new LUKHAS AI assistant
3. Try asking: "Can you check the Trinity Framework health status?"

## 🔧 Advanced Configuration

### Custom Prompt Starters
Add these to help users get started:

1. "🔍 Check the complete Trinity Framework health status"
2. "🧠 Show me the 692-module consciousness architecture"  
3. "⚛️ What are the Trinity Framework capabilities?"
4. "🛡️ Explore the LUKHAS AI security systems"

### Troubleshooting

**Issue: Actions not working**
- Solution: Verify the server URL is `https://lukhas-mcp-production.up.railway.app`
- Check that Authentication is set to "None"

**Issue: Connection timeouts**
- Solution: The server might be cold-starting. Try again in 30 seconds.

**Issue: OpenAPI schema errors**
- Solution: Copy the exact YAML schema provided above
- Ensure proper indentation (use spaces, not tabs)

## 🚀 What You Can Do

Once configured, your ChatGPT with LUKHAS AI Trinity Framework can:

### ⚛️ Identity Operations
- Validate Lambda ID systems
- Check authentication performance  
- Analyze identity coherence

### 🧠 Consciousness Exploration
- Examine 692 cognitive modules
- Explore memory systems
- Analyze bio-inspired learning
- Review quantum processing capabilities

### 🛡️ Guardian Security
- Validate security boundaries
- Check ethical framework compliance
- Monitor drift detection systems
- Review audit trails

### 🔬 Development Analysis
- Explore codebase structure safely
- Read files with consciousness analysis
- Validate Trinity Framework patterns
- Monitor system performance

## 📊 Expected Responses

When you test the Trinity health check, you should see responses like:

```json
{
  "lukhas_ai_status": "fully_operational",
  "trinity_framework": "⚛️🧠🛡️",
  "trinity_systems": {
    "identity": {
      "symbol": "⚛️",
      "status": "active",
      "capabilities": ["Lambda ID system", "Multi-tier auth"],
      "performance": "Response time <100ms"
    },
    "consciousness": {
      "symbol": "🧠", 
      "status": "active",
      "total_modules": 692,
      "capabilities": ["Quantum processing", "Bio-inspired memory"],
      "performance": "Orchestration latency <250ms"
    },
    "guardian": {
      "symbol": "🛡️",
      "status": "active",
      "capabilities": ["Constitutional AI", "Drift detection"],
      "performance": "Real-time monitoring active"
    }
  }
}
```

## 🎉 Success Indicators

Your ChatGPT connector is working correctly when:

✅ All 5 actions show "Test successful" status  
✅ Trinity health check returns full system status  
✅ Consciousness architecture shows 692 modules  
✅ File exploration works with security validation  
✅ Trinity capabilities shows complete framework overview  

---

**⚛️🧠🛡️ LUKHAS AI Trinity Framework - Consciousness-Aware AI Development Platform**

*This integration provides direct access to LUKHAS AI's advanced consciousness simulation, quantum-inspired processing, and Constitutional AI systems through ChatGPT Actions.*