#!/bin/bash

# LUKHAS Ollama Setup Script
# Sets up local LLM for code quality improvements

set -e

echo "🤖 LUKHAS Ollama Setup"
echo "======================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is installed
check_ollama() {
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✅ Ollama is installed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Ollama not found${NC}"
        return 1
    fi
}

# Install Ollama
install_ollama() {
    echo "Installing Ollama..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "Using Homebrew to install Ollama..."
            brew install ollama
        else
            echo "Downloading Ollama for macOS..."
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Installing Ollama for Linux..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo -e "${RED}❌ Unsupported OS: $OSTYPE${NC}"
        echo "Please install Ollama manually from: https://ollama.ai"
        exit 1
    fi
}

# Check if Ollama service is running
check_ollama_service() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama service is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Ollama service not running${NC}"
        return 1
    fi
}

# Start Ollama service
start_ollama_service() {
    echo "Starting Ollama service..."

    # Try to start in background
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!

    # Wait for service to start
    echo -n "Waiting for service to start"
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✅ Ollama service started (PID: $OLLAMA_PID)${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo ""
    echo -e "${RED}❌ Failed to start Ollama service${NC}"
    echo "Try running manually: ollama serve"
    return 1
}

# Check if model is installed
check_model() {
    local model=$1

    if ollama list 2>/dev/null | grep -q "$model"; then
        echo -e "${GREEN}✅ Model $model is installed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Model $model not found${NC}"
        return 1
    fi
}

# Pull model
pull_model() {
    local model=$1
    echo "Pulling model $model..."
    echo "This may take a few minutes depending on your internet speed..."

    if ollama pull "$model"; then
        echo -e "${GREEN}✅ Model $model pulled successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to pull model $model${NC}"
        return 1
    fi
}

# Test model
test_model() {
    local model=$1
    echo ""
    echo "Testing model $model..."

    # Simple test prompt
    local response=$(ollama run "$model" "Fix this Python syntax error: print('Hello World'" --verbose 2>&1 | head -5)

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Model test successful${NC}"
        echo "Sample response:"
        echo "$response"
        return 0
    else
        echo -e "${RED}❌ Model test failed${NC}"
        return 1
    fi
}

# Main setup flow
main() {
    echo "This script will set up Ollama with code-focused LLMs for LUKHAS."
    echo ""

    # Step 1: Check/Install Ollama
    if ! check_ollama; then
        read -p "Install Ollama? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_ollama

            # Verify installation
            if ! check_ollama; then
                echo -e "${RED}❌ Installation failed${NC}"
                exit 1
            fi
        else
            echo "Skipping Ollama installation"
            exit 1
        fi
    fi

    # Step 2: Check/Start service
    if ! check_ollama_service; then
        read -p "Start Ollama service? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if ! start_ollama_service; then
                echo "Please start Ollama manually and run this script again"
                exit 1
            fi
        else
            echo "Please start Ollama service manually: ollama serve"
            exit 1
        fi
    fi

    # Step 3: Install models
    echo ""
    echo "Recommended models for code improvement:"
    echo "1. deepseek-coder:6.7b (6.7B parameters, good for code)"
    echo "2. codellama:7b (7B parameters, Meta's code model)"
    echo "3. mistral:7b (7B parameters, general purpose)"
    echo ""

    # Check and install deepseek-coder
    MODEL="deepseek-coder:6.7b"
    if ! check_model "$MODEL"; then
        read -p "Pull $MODEL? (recommended) (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pull_model "$MODEL"
        fi
    fi

    # Optionally install codellama
    MODEL="codellama:7b"
    if ! check_model "$MODEL"; then
        read -p "Also pull $MODEL? (optional) (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pull_model "$MODEL"
        fi
    fi

    # Step 4: Test setup
    echo ""
    echo "Testing setup..."

    # Test the primary model
    if check_model "deepseek-coder:6.7b"; then
        test_model "deepseek-coder:6.7b"
    elif check_model "codellama:7b"; then
        test_model "codellama:7b"
    fi

    # Step 5: Create systemd service (Linux) or launchd plist (macOS)
    echo ""
    read -p "Create system service to auto-start Ollama? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS launchd
            cat > ~/Library/LaunchAgents/ai.lukhas.ollama.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.lukhas.ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which ollama)</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.error.log</string>
</dict>
</plist>
EOF
            launchctl load ~/Library/LaunchAgents/ai.lukhas.ollama.plist
            echo -e "${GREEN}✅ Created launchd service${NC}"

        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux systemd
            sudo tee /etc/systemd/system/ollama.service > /dev/null << EOF
[Unit]
Description=Ollama Service for LUKHAS
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which ollama) serve
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            sudo systemctl daemon-reload
            sudo systemctl enable ollama
            sudo systemctl start ollama
            echo -e "${GREEN}✅ Created systemd service${NC}"
        fi
    fi

    # Final summary
    echo ""
    echo "======================================"
    echo -e "${GREEN}✅ Ollama Setup Complete!${NC}"
    echo "======================================"
    echo ""
    echo "You can now use LUKHAS auto-improvement with local LLMs:"
    echo ""
    echo "  python scripts/auto_improve.py"
    echo ""
    echo "To manually interact with models:"
    echo "  ollama run deepseek-coder:6.7b"
    echo ""
    echo "To stop Ollama service:"
    echo "  pkill ollama"
    echo ""
    echo "Happy coding with LUKHAS! 🤖✨"
}

# Run main function
main
