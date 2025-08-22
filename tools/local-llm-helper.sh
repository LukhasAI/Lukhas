#!/bin/bash
# Local LLM Helper Script for Claude Code
# Location: /Users/agi_dev/LOCAL-REPOS/Lukhas/tools/local-llm-helper.sh

echo "🤖 LUKHAS Local LLM Helper"
echo "=========================="
echo

case "$1" in
    "status")
        echo "📊 Current LLM Status:"
        echo
        ollama list
        echo
        echo "💾 Storage Location: ~/.ollama/models/"
        echo "🔧 Ollama Binary: /opt/homebrew/bin/ollama"
        ;;
    "code")
        echo "🔧 Starting DeepSeek Coder (3.8GB) for coding tasks..."
        ollama run deepseek-coder:6.7b
        ;;
    "chat")
        echo "💬 Starting Llama 3.2 (1.3GB) for quick conversations..."
        ollama run llama3.2:1b
        ;;
    "serve")
        echo "🌐 Starting Ollama API server on localhost:11434..."
        ollama serve
        ;;
    "test")
        echo "🧪 Testing local LLM connection..."
        curl -s http://localhost:11434/api/generate -d '{
            "model": "llama3.2:1b",
            "prompt": "Say hello and confirm you are running locally",
            "stream": false
        }' | jq -r '.response' 2>/dev/null || echo "API not running. Start with: ollama serve"
        ;;
    *)
        echo "Usage: $0 {status|code|chat|serve|test}"
        echo
        echo "Commands:"
        echo "  status  - Show available models and system info"
        echo "  code    - Start DeepSeek Coder for coding tasks"
        echo "  chat    - Start Llama 3.2 for quick conversations"
        echo "  serve   - Start API server for programmatic access"
        echo "  test    - Test API connection"
        echo
        echo "Current Models:"
        ollama list | tail -n +2
        ;;
esac
