#!/bin/bash

# GPT-OSS Integration Installation Script
# Installs and configures GPT-OSS integration for LUKHAS ecosystem

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/.gpt-oss"
MODELS_DIR="$INSTALL_DIR/models"
LOGS_DIR="$INSTALL_DIR/logs"
CONFIG_DIR="$INSTALL_DIR/config"
CACHE_DIR="$INSTALL_DIR/cache"

# Default model variant
DEFAULT_MODEL="gpt-oss-20b"
SELECTED_MODEL=""

# Installation options
INSTALL_VSCODE_EXT=false
INSTALL_BRAIN_MODULE=false
INSTALL_LAMBDA_ADAPTERS=false
INSTALL_OLLAMA=false
SKIP_DEPENDENCIES=false

print_header() {
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════╗"
    echo "║           GPT-OSS Integration Setup           ║"
    echo "║              LUKHAS Ecosystem                 ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

show_help() {
    echo "GPT-OSS Integration Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -m, --model MODEL       Model variant to install (gpt-oss-20b, gpt-oss-120b)"
    echo "  -v, --vscode            Install VSCode extension integration"
    echo "  -b, --brain             Install brain module integration"
    echo "  -l, --lambda            Install Lambda Products adapters"
    echo "  -o, --ollama            Install and configure Ollama"
    echo "  -a, --all               Install all components"
    echo "  -s, --skip-deps         Skip dependency installation"
    echo "  --uninstall             Uninstall GPT-OSS integration"
    echo ""
    echo "Examples:"
    echo "  $0 --all                Install everything with default model"
    echo "  $0 -m gpt-oss-120b -v   Install VSCode integration with 120B model"
    echo "  $0 -b -l                Install brain module and Lambda adapters only"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -m|--model)
                SELECTED_MODEL="$2"
                shift 2
                ;;
            -v|--vscode)
                INSTALL_VSCODE_EXT=true
                shift
                ;;
            -b|--brain)
                INSTALL_BRAIN_MODULE=true
                shift
                ;;
            -l|--lambda)
                INSTALL_LAMBDA_ADAPTERS=true
                shift
                ;;
            -o|--ollama)
                INSTALL_OLLAMA=true
                shift
                ;;
            -a|--all)
                INSTALL_VSCODE_EXT=true
                INSTALL_BRAIN_MODULE=true
                INSTALL_LAMBDA_ADAPTERS=true
                INSTALL_OLLAMA=true
                shift
                ;;
            -s|--skip-deps)
                SKIP_DEPENDENCIES=true
                shift
                ;;
            --uninstall)
                uninstall_gpt_oss
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

check_system_requirements() {
    print_step "Checking system requirements..."

    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" && "$ARCH" != "arm64" ]]; then
        print_error "Unsupported architecture: $ARCH"
        exit 1
    fi

    # Check available memory for model selection
    if [[ "$OS" == "macos" ]]; then
        TOTAL_MEM=$(sysctl -n hw.memsize)
        TOTAL_MEM_GB=$((TOTAL_MEM / 1024 / 1024 / 1024))
    else
        TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        TOTAL_MEM_GB=$((TOTAL_MEM_KB / 1024 / 1024))
    fi

    print_info "System: $OS ($ARCH)"
    print_info "Total Memory: ${TOTAL_MEM_GB}GB"

    # Recommend model based on memory
    if [[ $TOTAL_MEM_GB -lt 16 ]]; then
        print_warning "Less than 16GB RAM detected. GPT-OSS-20b may run slowly."
        if [[ -z "$SELECTED_MODEL" ]]; then
            SELECTED_MODEL="gpt-oss-20b"
        fi
    elif [[ $TOTAL_MEM_GB -lt 80 ]]; then
        print_info "Sufficient memory for GPT-OSS-20b model."
        if [[ -z "$SELECTED_MODEL" ]]; then
            SELECTED_MODEL="gpt-oss-20b"
        fi
    else
        print_info "High memory system detected. GPT-OSS-120b is available."
        if [[ -z "$SELECTED_MODEL" ]]; then
            # Ask user for model preference
            echo -e "\n${YELLOW}Select GPT-OSS model variant:${NC}"
            echo "1) gpt-oss-20b (16GB+ RAM required)"
            echo "2) gpt-oss-120b (80GB+ RAM required)"
            read -p "Choice [1]: " model_choice

            case $model_choice in
                2)
                    SELECTED_MODEL="gpt-oss-120b"
                    ;;
                *)
                    SELECTED_MODEL="gpt-oss-20b"
                    ;;
            esac
        fi
    fi

    print_info "Selected model: $SELECTED_MODEL"
}

check_dependencies() {
    if [[ "$SKIP_DEPENDENCIES" == "true" ]]; then
        print_info "Skipping dependency check as requested"
        return
    fi

    print_step "Checking dependencies..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $PYTHON_VERSION"

    # Check Node.js for VSCode extension
    if [[ "$INSTALL_VSCODE_EXT" == "true" ]]; then
        if ! command -v node &> /dev/null; then
            print_error "Node.js is required for VSCode extension but not installed"
            exit 1
        fi

        NODE_VERSION=$(node --version)
        print_info "Node.js version: $NODE_VERSION"
    fi

    # Check VS Code if installing extension
    if [[ "$INSTALL_VSCODE_EXT" == "true" ]]; then
        if ! command -v code &> /dev/null; then
            print_warning "VS Code command 'code' not found in PATH"
            print_info "You may need to install VS Code or add it to PATH"
        fi
    fi

    print_success "Dependencies check completed"
}

create_directories() {
    print_step "Creating installation directories..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$MODELS_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$CACHE_DIR"

    print_success "Created directories in $INSTALL_DIR"
}

install_python_dependencies() {
    print_step "Installing Python dependencies..."

    # Create requirements file
    cat > "$INSTALL_DIR/requirements.txt" << EOF
# GPT-OSS Integration Requirements
torch>=2.0.0
transformers>=4.25.0
numpy>=1.24.0
asyncio>=3.4.3
aiohttp>=3.8.0
msgpack>=1.0.0
cryptography>=3.4.8
ollama>=0.1.0
psutil>=5.9.0
pynvml>=11.4.0
EOF

    # Install dependencies
    if command -v pip3 &> /dev/null; then
        pip3 install -r "$INSTALL_DIR/requirements.txt"
    elif command -v pip &> /dev/null; then
        pip install -r "$INSTALL_DIR/requirements.txt"
    else
        print_error "Neither pip3 nor pip found"
        exit 1
    fi

    print_success "Python dependencies installed"
}

install_ollama() {
    if [[ "$INSTALL_OLLAMA" != "true" ]]; then
        return
    fi

    print_step "Installing Ollama..."

    if command -v ollama &> /dev/null; then
        print_info "Ollama already installed"
    else
        # Install Ollama
        if [[ "$OS" == "macos" ]]; then
            curl -fsSL https://ollama.ai/install.sh | sh
        else
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    fi

    # Wait for Ollama service to start
    print_info "Starting Ollama service..."
    ollama serve &
    sleep 5

    # Pull the selected model
    print_step "Pulling $SELECTED_MODEL model..."
    if ! ollama pull "$SELECTED_MODEL"; then
        print_warning "Failed to pull $SELECTED_MODEL from Ollama registry"
        print_info "You may need to manually install the model later"
    fi

    print_success "Ollama installation completed"
}

create_config_files() {
    print_step "Creating configuration files..."

    # Main GPT-OSS config
    cat > "$CONFIG_DIR/gpt_oss_config.json" << EOF
{
  "model": {
    "variant": "$SELECTED_MODEL",
    "backend": "ollama",
    "model_path": "$MODELS_DIR",
    "context_window": 8192,
    "max_tokens": 2048,
    "temperature": 0.7
  },
  "cache": {
    "enabled": true,
    "max_size": 1000,
    "ttl_seconds": 3600,
    "cache_dir": "$CACHE_DIR"
  },
  "performance": {
    "batch_size": 8,
    "max_concurrent": 4,
    "timeout_seconds": 30
  },
  "logging": {
    "level": "INFO",
    "log_dir": "$LOGS_DIR",
    "max_log_files": 10
  },
  "integration": {
    "vscode_enabled": $INSTALL_VSCODE_EXT,
    "brain_module_enabled": $INSTALL_BRAIN_MODULE,
    "lambda_products_enabled": $INSTALL_LAMBDA_ADAPTERS
  }
}
EOF

    # VSCode extension config
    if [[ "$INSTALL_VSCODE_EXT" == "true" ]]; then
        mkdir -p "$CONFIG_DIR/vscode"
        cat > "$CONFIG_DIR/vscode/settings.json" << EOF
{
  "gpt-oss.model.variant": "$SELECTED_MODEL",
  "gpt-oss.completion.enabled": true,
  "gpt-oss.completion.maxTokens": 500,
  "gpt-oss.completion.temperature": 0.7,
  "gpt-oss.lukhas.patternsEnabled": true,
  "gpt-oss.shadow.enabled": true,
  "gpt-oss.cache.enabled": true
}
EOF
    fi

    # Brain module config
    if [[ "$INSTALL_BRAIN_MODULE" == "true" ]]; then
        mkdir -p "$CONFIG_DIR/brain-module"
        cat > "$CONFIG_DIR/brain-module/settings.json" << EOF
{
  "brain": {
    "frequency": 30.0,
    "context_window_size": 10,
    "cache_size": 100,
    "reasoning_depth": "comprehensive"
  },
  "symphony_integration": {
    "enabled": true,
    "sync_with_other_brains": true,
    "bio_rhythmic_sync": true
  },
  "performance": {
    "monitoring_enabled": true,
    "metrics_collection": true,
    "auto_optimization": true
  }
}
EOF
    fi

    # Lambda Products config
    if [[ "$INSTALL_LAMBDA_ADAPTERS" == "true" ]]; then
        mkdir -p "$CONFIG_DIR/lambda-products"
        cat > "$CONFIG_DIR/lambda-products/settings.json" << EOF
{
  "qrg": {
    "enabled": true,
    "quality_threshold": 0.7,
    "reasoning_depth": "comprehensive"
  },
  "nias": {
    "enabled": true,
    "intelligence_analysis": true,
    "behavioral_modeling": true
  },
  "abas": {
    "enabled": true,
    "business_analysis": true,
    "strategic_planning": true
  },
  "dast": {
    "enabled": true,
    "data_analytics": true,
    "predictive_modeling": true
  }
}
EOF
    fi

    print_success "Configuration files created"
}

install_vscode_extension() {
    if [[ "$INSTALL_VSCODE_EXT" != "true" ]]; then
        return
    fi

    print_step "Setting up VSCode extension integration..."

    # Copy VSCode extension files to workspace
    VSCODE_EXT_DIR="$(pwd)/gpt-oss-integration/vscode-extension"
    if [[ -d "$VSCODE_EXT_DIR" ]]; then
        print_info "Installing GPT-OSS completion provider..."

        # Install Node.js dependencies
        cd "$VSCODE_EXT_DIR"
        if [[ -f "package.json" ]]; then
            npm install
        fi

        cd - > /dev/null

        # Create symlink for easy access
        ln -sf "$VSCODE_EXT_DIR" "$CONFIG_DIR/vscode-extension"

        print_info "To complete VSCode integration, add this to your workspace settings:"
        print_info "  \"gpt-oss.configPath\": \"$CONFIG_DIR/gpt_oss_config.json\""

    else
        print_warning "VSCode extension directory not found. Integration may be incomplete."
    fi

    print_success "VSCode extension setup completed"
}

install_brain_module() {
    if [[ "$INSTALL_BRAIN_MODULE" != "true" ]]; then
        return
    fi

    print_step "Setting up brain module integration..."

    # Copy brain module to installation directory
    BRAIN_MODULE_DIR="$(pwd)/gpt-oss-integration/agi-integration/brain-modules"
    if [[ -d "$BRAIN_MODULE_DIR" ]]; then
        cp -r "$BRAIN_MODULE_DIR" "$INSTALL_DIR/"

        # Make module importable
        export PYTHONPATH="$INSTALL_DIR/brain-modules:$PYTHONPATH"

        print_info "Brain module installed to: $INSTALL_DIR/brain-modules"
        print_info "Add to your PYTHONPATH: export PYTHONPATH=\"$INSTALL_DIR/brain-modules:\$PYTHONPATH\""

    else
        print_warning "Brain module directory not found. Integration may be incomplete."
    fi

    print_success "Brain module setup completed"
}

install_lambda_adapters() {
    if [[ "$INSTALL_LAMBDA_ADAPTERS" != "true" ]]; then
        return
    fi

    print_step "Setting up Lambda Products adapters..."

    # Copy Lambda Products adapters
    ADAPTERS_DIR="$(pwd)/gpt-oss-integration/lambda-products/adapters"
    if [[ -d "$ADAPTERS_DIR" ]]; then
        cp -r "$ADAPTERS_DIR" "$INSTALL_DIR/lambda-products/"

        print_info "Lambda Products adapters installed to: $INSTALL_DIR/lambda-products"

    else
        print_warning "Lambda Products adapters directory not found. Integration may be incomplete."
    fi

    print_success "Lambda Products adapters setup completed"
}

create_activation_script() {
    print_step "Creating activation script..."

    cat > "$INSTALL_DIR/activate_gpt_oss.sh" << EOF
#!/bin/bash
# GPT-OSS Integration Activation Script

export GPT_OSS_HOME="$INSTALL_DIR"
export GPT_OSS_CONFIG="\$GPT_OSS_HOME/config/gpt_oss_config.json"
export GPT_OSS_MODEL="$SELECTED_MODEL"
export PYTHONPATH="\$GPT_OSS_HOME/brain-modules:\$PYTHONPATH"

# Start Ollama service if installed
if command -v ollama &> /dev/null; then
    if ! pgrep -f "ollama serve" > /dev/null; then
        echo "Starting Ollama service..."
        ollama serve &
        sleep 3
    fi
fi

echo "GPT-OSS Integration environment activated"
echo "Config: \$GPT_OSS_CONFIG"
echo "Model: \$GPT_OSS_MODEL"
echo ""
echo "Available commands:"
echo "  gpt-oss-test     - Test GPT-OSS integration"
echo "  gpt-oss-status   - Show system status"
echo "  gpt-oss-logs     - View logs"
EOF

    chmod +x "$INSTALL_DIR/activate_gpt_oss.sh"

    # Create convenience scripts
    cat > "$INSTALL_DIR/gpt-oss-test" << 'EOF'
#!/usr/bin/env python3
"""Test GPT-OSS integration"""

import sys
import os
sys.path.insert(0, os.path.join(os.environ['GPT_OSS_HOME'], 'brain-modules'))

async def test_integration():
    try:
        from gpt_oss_brain import test_gpt_oss_brain
        await test_gpt_oss_brain()
    except ImportError as e:
        print(f"❌ Failed to import GPT-OSS brain: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_integration())
EOF

    chmod +x "$INSTALL_DIR/gpt-oss-test"

    cat > "$INSTALL_DIR/gpt-oss-status" << 'EOF'
#!/bin/bash
"""Show GPT-OSS system status"""

echo "🔍 GPT-OSS Integration Status"
echo "============================="
echo "Home: $GPT_OSS_HOME"
echo "Config: $GPT_OSS_CONFIG"
echo "Model: $GPT_OSS_MODEL"
echo ""

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "🤖 Ollama Status:"
    if pgrep -f "ollama serve" > /dev/null; then
        echo "  ✅ Service running"
        ollama list 2>/dev/null | head -5
    else
        echo "  ❌ Service not running"
    fi
else
    echo "  ❌ Ollama not installed"
fi

echo ""

# Check disk usage
echo "💾 Disk Usage:"
du -sh "$GPT_OSS_HOME" 2>/dev/null || echo "  Unable to check disk usage"

echo ""

# Check logs
if [[ -d "$GPT_OSS_HOME/logs" ]]; then
    echo "📄 Recent Logs:"
    find "$GPT_OSS_HOME/logs" -name "*.log" -mtime -1 | head -3
fi
EOF

    chmod +x "$INSTALL_DIR/gpt-oss-status"

    cat > "$INSTALL_DIR/gpt-oss-logs" << 'EOF'
#!/bin/bash
"""View GPT-OSS logs"""

LOG_DIR="$GPT_OSS_HOME/logs"
if [[ -d "$LOG_DIR" ]]; then
    echo "📄 Available log files:"
    ls -la "$LOG_DIR"
    echo ""

    # Show most recent log
    LATEST_LOG=$(find "$LOG_DIR" -name "*.log" -type f -exec ls -t {} + | head -1)
    if [[ -n "$LATEST_LOG" ]]; then
        echo "📄 Latest log: $LATEST_LOG"
        tail -50 "$LATEST_LOG"
    fi
else
    echo "❌ No logs directory found"
fi
EOF

    chmod +x "$INSTALL_DIR/gpt-oss-logs"

    print_success "Activation script and utilities created"
}

create_uninstall_script() {
    print_step "Creating uninstall script..."

    cat > "$INSTALL_DIR/uninstall_gpt_oss.sh" << EOF
#!/bin/bash
# GPT-OSS Integration Uninstall Script

echo "🗑️  GPT-OSS Integration Uninstall"
echo "================================="
echo ""

read -p "Are you sure you want to uninstall GPT-OSS integration? [y/N]: " confirm
if [[ \$confirm != [yY] && \$confirm != [yY][eE][sS] ]]; then
    echo "Uninstall cancelled"
    exit 0
fi

echo "Stopping Ollama service..."
pkill -f "ollama serve" 2>/dev/null || true

echo "Removing installation directory..."
rm -rf "$INSTALL_DIR"

echo "Cleaning up environment variables..."
# Note: User needs to manually remove from their shell profile

echo ""
echo "✅ GPT-OSS integration has been uninstalled"
echo "Note: You may want to remove these from your shell profile:"
echo "  export GPT_OSS_HOME=\"$INSTALL_DIR\""
echo "  export PYTHONPATH=\"$INSTALL_DIR/brain-modules:\\\$PYTHONPATH\""
EOF

    chmod +x "$INSTALL_DIR/uninstall_gpt_oss.sh"

    print_success "Uninstall script created"
}

show_completion_message() {
    print_success "GPT-OSS Integration installation completed!"
    echo ""
    echo -e "${GREEN}📋 Installation Summary:${NC}"
    echo "  • Installation directory: $INSTALL_DIR"
    echo "  • Model variant: $SELECTED_MODEL"
    echo "  • VSCode integration: $([ "$INSTALL_VSCODE_EXT" = true ] && echo "✅ Installed" || echo "❌ Skipped")"
    echo "  • Brain module: $([ "$INSTALL_BRAIN_MODULE" = true ] && echo "✅ Installed" || echo "❌ Skipped")"
    echo "  • Lambda adapters: $([ "$INSTALL_LAMBDA_ADAPTERS" = true ] && echo "✅ Installed" || echo "❌ Skipped")"
    echo "  • Ollama backend: $([ "$INSTALL_OLLAMA" = true ] && echo "✅ Installed" || echo "❌ Skipped")"
    echo ""
    echo -e "${BLUE}🚀 Next Steps:${NC}"
    echo "1. Activate the environment:"
    echo "   source $INSTALL_DIR/activate_gpt_oss.sh"
    echo ""
    echo "2. Test the installation:"
    echo "   $INSTALL_DIR/gpt-oss-test"
    echo ""
    echo "3. Check system status:"
    echo "   $INSTALL_DIR/gpt-oss-status"
    echo ""
    echo "4. Add to your shell profile for persistent activation:"
    echo "   echo 'source $INSTALL_DIR/activate_gpt_oss.sh' >> ~/.bashrc"
    echo ""
    echo -e "${YELLOW}⚠️  Important Notes:${NC}"
    if [[ "$INSTALL_VSCODE_EXT" == "true" ]]; then
        echo "• Configure VSCode workspace with GPT-OSS settings"
    fi
    if [[ "$INSTALL_OLLAMA" == "true" ]]; then
        echo "• Ensure Ollama service is running before using GPT-OSS"
    fi
    echo "• Review feature flags in config/feature_flags.json to enable components"
    echo ""
    echo -e "${GREEN}Happy coding with GPT-OSS! 🎉${NC}"
}

uninstall_gpt_oss() {
    print_step "Uninstalling GPT-OSS integration..."

    if [[ -d "$INSTALL_DIR" ]]; then
        # Run uninstall script if it exists
        if [[ -f "$INSTALL_DIR/uninstall_gpt_oss.sh" ]]; then
            "$INSTALL_DIR/uninstall_gpt_oss.sh"
        else
            rm -rf "$INSTALL_DIR"
            print_success "GPT-OSS integration uninstalled"
        fi
    else
        print_info "GPT-OSS integration not found or already uninstalled"
    fi
}

main() {
    print_header

    parse_args "$@"

    # If no components selected, show help
    if [[ "$INSTALL_VSCODE_EXT" != "true" && "$INSTALL_BRAIN_MODULE" != "true" && "$INSTALL_LAMBDA_ADAPTERS" != "true" && "$INSTALL_OLLAMA" != "true" ]]; then
        echo -e "${YELLOW}No components selected for installation.${NC}"
        echo "Use --all to install everything, or select specific components."
        echo ""
        show_help
        exit 1
    fi

    check_system_requirements
    check_dependencies
    create_directories
    install_python_dependencies
    install_ollama
    create_config_files
    install_vscode_extension
    install_brain_module
    install_lambda_adapters
    create_activation_script
    create_uninstall_script
    show_completion_message
}

# Run main function with all arguments
main "$@"
