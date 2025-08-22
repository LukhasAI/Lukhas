# 🤖 Local LLM Setup Guide for Claude Code

**Date**: August 22, 2025  
**System**: M4 MacBook Air  
**Project**: LUKHAS AI Development

## 🎯 Available Local Models

After cleanup and optimization, we have **2 models** perfectly sized for M4 MacBook Air:

### 1. **DeepSeek Coder 6.7B** (Primary Coding Model)
- **Size**: 3.8GB
- **Purpose**: Code generation, debugging, refactoring, technical documentation
- **Strengths**: Excellent for Python, JavaScript, TypeScript, system architecture
- **Command**: `ollama run deepseek-coder:6.7b`
- **API**: `http://localhost:11434/api/generate` (when running)

### 2. **Llama 3.2 1B** (Lightweight Assistant)
- **Size**: 1.3GB  
- **Purpose**: Quick responses, lightweight tasks, testing, conversations
- **Strengths**: Fast inference, low memory usage, general assistance
- **Command**: `ollama run llama3.2:1b`
- **API**: `http://localhost:11434/api/generate` (when running)

## 🛠️ Technical Setup

### Ollama Installation
- **Binary Location**: `/opt/homebrew/bin/ollama`
- **Models Storage**: `~/.ollama/models/`
- **Status Check**: `ollama list`
- **Service**: `ollama serve` (starts API server on localhost:11434)

### Integration Commands

```bash
# List available models
ollama list

# Start a model interactively
ollama run deepseek-coder:6.7b
ollama run llama3.2:1b

# Start API server (background)
ollama serve &

# Test API connection
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder:6.7b",
  "prompt": "Write a Python function to calculate fibonacci",
  "stream": false
}'
```

## 🚀 Recommended Usage for LUKHAS Development

### For Code Tasks (Use DeepSeek Coder):
- Python module development
- FastAPI endpoint creation
- Consciousness framework code
- Trinity Framework implementation
- Error debugging and optimization
- Documentation generation

### For Quick Tasks (Use Llama 3.2):
- Planning and brainstorming
- Code comments and explanations
- Quick consultations
- Testing simple logic
- Lightweight conversations

## 🔧 Claude Code Integration

### Method 1: Direct Terminal Commands
When Claude Code needs local LLM assistance:
```bash
# For coding tasks
ollama run deepseek-coder:6.7b "Optimize this Python function: [paste code]"

# For quick questions  
ollama run llama3.2:1b "Explain this concept briefly"
```

### Method 2: API Integration
If building tools that need programmatic access:
```python
import requests

def query_local_llm(prompt, model="deepseek-coder:6.7b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
```

## 📊 Performance Notes

- **DeepSeek Coder**: ~2-4GB RAM usage, excellent for complex coding tasks
- **Llama 3.2 1B**: ~1-2GB RAM usage, very fast responses
- **Both models**: Optimized for M4 MacBook Air efficiency
- **Total Storage**: Only 5.1GB (down from 67GB after cleanup!)

## 🎯 Best Practices

1. **Use DeepSeek Coder for**:
   - LUKHAS consciousness module development
   - Complex Python/TypeScript tasks
   - Architecture decisions
   - Code reviews and optimizations

2. **Use Llama 3.2 for**:
   - Quick clarifications
   - Planning sessions  
   - Simple explanations
   - Testing ideas

3. **Performance Tips**:
   - Run one model at a time to optimize memory
   - Use `ollama serve` for API access if building integrations
   - Models auto-unload after inactivity to free memory

---

*This setup provides Claude Code with powerful local LLM capabilities while maintaining optimal performance on M4 MacBook Air hardware.*
