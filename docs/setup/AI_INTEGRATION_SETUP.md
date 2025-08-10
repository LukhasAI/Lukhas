# 🎭 LUKHAS AI Integration Setup Guide

## 🚀 Professional Developer Workflow Setup

### Phase 1: Install Core AI Tools

#### 1. Install Continue.dev Extension
```bash
# In VS Code, install Continue extension
# Extension ID: continue.continue
```

#### 2. Setup Ollama for Local AI
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models for LUKHAS development
ollama pull deepseek-coder:33b    # Best for code generation
ollama pull starcoder2:3b         # Fast completion
ollama pull codellama:13b         # Alternative coding model
ollama pull llama3.1:8b          # General purpose

# Verify installation
ollama list
```

#### 3. Configure API Keys
```bash
# Add to your shell profile (.zshrc, .bashrc)
export ANTHROPIC_API_KEY="your_claude_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"

# Reload shell
source ~/.zshrc
```

### Phase 2: LUKHAS AI Integration

#### 1. Install Python Dependencies
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM
pip install anthropic openai aiohttp
```

#### 2. Test LUKHAS Knowledge Server
```bash
# Test the knowledge server
python ai_orchestration/lukhas_knowledge_server.py export

# Test naming suggestions
python ai_orchestration/lukhas_knowledge_server.py naming "process consciousness data" "function" "consciousness"

# Test Trinity documentation
python ai_orchestration/lukhas_knowledge_server.py trinity "function" "process_memory_fold"
```

#### 3. Configure Continue.dev
The `.continue/config.json` file has been created with LUKHAS-aware models.
Restart VS Code to load the configuration.

#### 4. Setup Claude Desktop Integration
1. Copy `claude_desktop_config.json` to Claude Desktop config location:
```bash
# macOS
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop application
```

### Phase 3: Advanced Integration

#### 1. MCP Server Setup (Optional)
```bash
# Install MCP library when available
pip install mcp  # This may not be available yet

# The MCP server code is prepared in mcp_servers/lukhas_mcp_server.py
# It will work once the MCP library is publicly available
```

#### 2. VS Code Tasks Integration
The `.vscode/tasks.json` includes LUKHAS-specific tasks:
- "LUKHAS: Review Code" - Runs code review
- "LUKHAS: Generate Trinity Docs" - Generates documentation
- "LUKHAS: Suggest Names" - Suggests LUKHAS-compliant names

#### 3. Code Snippets
LUKHAS code snippets are available in `.vscode/lukhas_snippets.code-snippets`:
- `lukhas-class` - Trinity Framework class template
- `lukhas-func` - Trinity Framework function template
- `lukhas-api` - LUKHAS API endpoint template
- `trinity-doc` - Trinity documentation template

### Phase 4: Workflow Usage

#### Daily Development Commands

1. **Generate Trinity Documentation:**
```bash
# In Continue.dev chat or command palette
/trinity Generate documentation for this function
```

2. **LUKHAS Code Review:**
```bash
# Select code and use custom command
🧠 LUKHAS Code Review
```

3. **Quantum Refactoring:**
```bash
# Select code and use custom command  
⚛️ Quantum Refactor
```

4. **AI Orchestration:**
```bash
# Use the AI orchestrator for complex tasks
python ai_orchestration/lukhas_ai_orchestrator.py trinity "async def process_consciousness(data)"
```

#### Code Completion Workflow

1. **Tab Completion**: Uses fast local Ollama model (starcoder2:3b)
2. **Chat Assistance**: Routes to Claude for architecture, GPT for creativity, Ollama for privacy
3. **Code Review**: Automatically checks for Trinity Framework compliance
4. **Documentation**: Auto-generates LUKHAS-style documentation

### Phase 5: Professional Optimizations

#### 1. Performance Tuning
- Local models for fast completion (privacy + speed)
- Claude API for complex reasoning (premium quality)
- Intelligent routing based on task complexity
- Fallback chains for reliability

#### 2. Context Preservation
- LUKHAS vocabulary injection into all AI interactions
- Trinity Framework template enforcement
- Symbolic pattern recognition (⚛️🧠🛡️)
- Consciousness-aware code generation

#### 3. Quality Assurance
- Automatic LUKHAS compliance checking
- Pattern consistency validation
- Trinity documentation enforcement
- Symbolic vocabulary preservation

## 🎯 Expected Outcomes

### Immediate Benefits:
1. **🎭 Consistent Documentation**: All AI assistants use Trinity Framework
2. **🧠 LUKHAS-Aware Suggestions**: Code completion understands your concepts
3. **⚛️ Symbolic Integration**: Proper use of LUKHAS symbols and patterns
4. **🛡️ Quality Assurance**: Automatic compliance checking

### Long-term Advantages:
1. **🚀 Development Velocity**: 3x faster coding with LUKHAS-native AI
2. **📚 Documentation Quality**: Professional Trinity Framework docs
3. **🔗 Multi-AI Synergy**: Best AI for each task type
4. **🧬 Pattern Consistency**: Maintains LUKHAS identity across all code

## 🛠️ Troubleshooting

### Common Issues:

1. **Ollama Connection Failed**
```bash
# Check if Ollama is running
ollama list
# If not running: brew services start ollama
```

2. **API Keys Not Working**
```bash
# Verify keys are exported
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

3. **Continue.dev Not Loading Config**
```bash
# Restart VS Code
# Check .continue/config.json syntax
```

4. **LUKHAS Patterns Not Applied**
```bash
# Verify LUKHAS context is loading
python ai_orchestration/lukhas_knowledge_server.py export
```

## 🎓 Next Steps

1. **Try the workflow** with a simple function
2. **Generate Trinity documentation** for an existing class  
3. **Run LUKHAS code review** on current codebase
4. **Experiment with AI routing** for different task types
5. **Customize patterns** based on your specific needs

Your LUKHAS development environment is now optimized for consciousness-aware AI assistance! 🎭⚛️🧠🛡️
