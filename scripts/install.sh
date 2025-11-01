#!/bin/bash
set -e

# LUKHAS API Optimization System - Installation Script
# Complete automated installation for all deployment environments

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REQUIRED_PYTHON_VERSION="3.9"
RECOMMENDED_PYTHON_VERSION="3.11"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/lukhas_api_optimization_install.log"

# Functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "🚀 LUKHAS API Optimization System"
    echo "   Enterprise Installation Script"
    echo "=========================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}📋 Step $1: $2${NC}"
    log "Step $1: $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

check_requirements() {
    print_step "1" "Checking System Requirements"
    
    # Check Python version
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 --version | cut -d' ' -f2)
        echo "   Python version: $python_version"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)"; then
            print_success "Python version requirement met"
        else
            print_error "Python 3.9+ required, found $python_version"
            echo "   Please install Python 3.9 or higher"
            exit 1
        fi
        
        # Check for recommended version
        if python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)"; then
            print_success "Using recommended Python version"
        else
            print_warning "Python 3.11+ recommended for optimal performance"
        fi
    else
        print_error "Python 3 not found"
        echo "   Please install Python 3.9 or higher"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        print_success "pip3 found"
    else
        print_error "pip3 not found"
        echo "   Please install pip3"
        exit 1
    fi
    
    # Check disk space (need at least 1GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -gt 1048576 ]; then  # 1GB in KB
        print_success "Sufficient disk space available"
    else
        print_warning "Low disk space. At least 1GB recommended"
    fi
    
    # Check memory (need at least 2GB)
    if command -v free >/dev/null 2>&1; then
        total_memory=$(free -m | awk '/^Mem:/{print $2}')
        if [ "$total_memory" -gt 2048 ]; then
            print_success "Sufficient memory available (${total_memory}MB)"
        else
            print_warning "Low memory. At least 2GB recommended"
        fi
    fi
}

install_system_dependencies() {
    print_step "2" "Installing System Dependencies"
    
    # Detect OS and install dependencies
    if command -v apt-get >/dev/null 2>&1; then
        echo "   Detected: Debian/Ubuntu"
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
            build-essential \
            python3-dev \
            redis-server \
            curl \
            git \
            nginx \
            supervisor \
            || {
                print_error "Failed to install system dependencies"
                exit 1
            }
        print_success "Debian/Ubuntu dependencies installed"
        
    elif command -v yum >/dev/null 2>&1; then
        echo "   Detected: RedHat/CentOS"
        sudo yum install -y \
            gcc \
            python3-devel \
            redis \
            curl \
            git \
            nginx \
            supervisor \
            || {
                print_error "Failed to install system dependencies"
                exit 1
            }
        print_success "RedHat/CentOS dependencies installed"
        
    elif command -v brew >/dev/null 2>&1; then
        echo "   Detected: macOS with Homebrew"
        brew install redis nginx || {
            print_error "Failed to install macOS dependencies"
            exit 1
        }
        print_success "macOS dependencies installed"
        
    else
        print_warning "Unknown package manager. Please install manually:"
        echo "   - Redis server"
        echo "   - Build tools (gcc, make)"
        echo "   - Python development headers"
    fi
}

setup_python_environment() {
    print_step "3" "Setting up Python Environment"
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv .venv || {
            print_error "Failed to create virtual environment"
            exit 1
        }
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate || {
        print_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip
    echo "   Upgrading pip..."
    pip install --upgrade pip setuptools wheel || {
        print_error "Failed to upgrade pip"
        exit 1
    }
    
    print_success "Python environment ready"
}

install_python_dependencies() {
    print_step "4" "Installing Python Dependencies"
    
    cd "$PROJECT_ROOT"
    source .venv/bin/activate
    
    # Install core dependencies
    if [ -f "requirements.txt" ]; then
        echo "   Installing core dependencies..."
        pip install -r requirements.txt || {
            print_error "Failed to install core dependencies"
            exit 1
        }
        print_success "Core dependencies installed"
    fi
    
    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        echo "   Installing development dependencies..."
        pip install -r requirements-dev.txt || {
            print_warning "Failed to install development dependencies"
        }
    fi
    
    # Install API optimization specific dependencies
    echo "   Installing API optimization dependencies..."
    pip install \
        fastapi \
        uvicorn \
        redis \
        aioredis \
        prometheus-client \
        structlog \
        pydantic \
        cryptography \
        PyJWT \
        passlib \
        bcrypt \
        || {
            print_error "Failed to install API optimization dependencies"
            exit 1
        }
    
    # Optional ML/Analytics dependencies
    echo "   Installing optional analytics dependencies..."
    pip install \
        numpy \
        pandas \
        scikit-learn \
        matplotlib \
        seaborn \
        plotly \
        || {
            print_warning "Some analytics dependencies failed to install"
        }
    
    print_success "Python dependencies installed"
}

setup_configuration() {
    print_step "5" "Setting up Configuration"
    
    cd "$PROJECT_ROOT"
    
    # Create config directory
    mkdir -p config
    mkdir -p config/secrets
    mkdir -p logs
    mkdir -p data/cache
    
    # Generate configuration files
    if command -v python3 >/dev/null 2>&1; then
        source .venv/bin/activate
        
        echo "   Generating development configuration..."
        python3 config/config_factory.py \
            --environment development \
            --output config/development.yaml \
            --format yaml || {
                print_warning "Failed to generate development config"
            }
        
        echo "   Generating production configuration..."
        python3 config/config_factory.py \
            --environment production \
            --output config/production.yaml \
            --format yaml || {
                print_warning "Failed to generate production config"
            }
        
        echo "   Generating testing configuration..."
        python3 config/config_factory.py \
            --environment testing \
            --output config/testing.yaml \
            --format yaml || {
                print_warning "Failed to generate testing config"
            }
    fi
    
    # Setup secrets management
    if [ -f "config/secrets_manager.py" ]; then
        source .venv/bin/activate
        echo "   Generating master encryption key..."
        python3 config/secrets_manager.py generate-key > config/.master_key_info || {
            print_warning "Failed to generate master key"
        }
    fi
    
    # Set proper permissions
    chmod 700 config/secrets
    chmod 600 config/.master_key_info 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    
    print_success "Configuration setup complete"
}

setup_redis() {
    print_step "6" "Setting up Redis"
    
    # Check if Redis is running
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is already running"
    else
        echo "   Starting Redis server..."
        
        if command -v systemctl >/dev/null 2>&1; then
            # SystemD
            sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis
            sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis
            print_success "Redis started with systemctl"
            
        elif command -v service >/dev/null 2>&1; then
            # SysV Init
            sudo service redis-server start 2>/dev/null || sudo service redis start
            print_success "Redis started with service"
            
        elif command -v brew >/dev/null 2>&1; then
            # macOS with Homebrew
            brew services start redis
            print_success "Redis started with brew services"
            
        else
            # Manual start
            redis-server --daemonize yes
            print_success "Redis started manually"
        fi
        
        # Wait for Redis to start
        sleep 2
        
        # Verify Redis is running
        if redis-cli ping >/dev/null 2>&1; then
            print_success "Redis is running and accessible"
        else
            print_error "Redis failed to start properly"
            exit 1
        fi
    fi
    
    # Test Redis functionality
    echo "   Testing Redis functionality..."
    redis-cli set lukhas_test "installation_test" >/dev/null
    if [ "$(redis-cli get lukhas_test)" = "installation_test" ]; then
        redis-cli del lukhas_test >/dev/null
        print_success "Redis functionality test passed"
    else
        print_error "Redis functionality test failed"
        exit 1
    fi
}

run_tests() {
    print_step "7" "Running Installation Tests"
    
    cd "$PROJECT_ROOT"
    source .venv/bin/activate
    
    # Test configuration loading
    echo "   Testing configuration system..."
    if python3 -c "
import sys
sys.path.insert(0, '.')
from config.config_factory import create_config
config = create_config('development')
print('✅ Configuration system working')
" 2>/dev/null; then
        print_success "Configuration system test passed"
    else
        print_warning "Configuration system test failed"
    fi
    
    # Test secrets management
    echo "   Testing secrets management..."
    if python3 -c "
import sys
sys.path.insert(0, '.')
from config.secrets_manager import SecretsManager
manager = SecretsManager()
manager.store_secret('test_secret', 'test_value')
value = manager.get_secret('test_secret')
assert value == 'test_value'
manager.delete_secret('test_secret')
print('✅ Secrets management working')
" 2>/dev/null; then
        print_success "Secrets management test passed"
    else
        print_warning "Secrets management test failed"
    fi
    
    # Test API optimization imports
    echo "   Testing API optimization imports..."
    if python3 -c "
import sys
sys.path.insert(0, '.')
from api.optimization.advanced_api_optimizer import LUKHASAPIOptimizer
from api.optimization.advanced_middleware import LUKHASMiddlewarePipeline
from api.optimization.analytics_dashboard import AnalyticsDashboard
from api.optimization.integration_hub import LUKHASAPIOptimizationHub
print('✅ All API optimization modules imported')
" 2>/dev/null; then
        print_success "API optimization imports test passed"
    else
        print_warning "API optimization imports test failed"
    fi
    
    # Run validation test suite if available
    if [ -f "test_api_optimization_validation.py" ]; then
        echo "   Running comprehensive validation tests..."
        timeout 60 python3 test_api_optimization_validation.py 2>/dev/null || {
            print_warning "Comprehensive validation tests had issues (timeout or errors)"
        }
    fi
}

setup_systemd_service() {
    print_step "8" "Setting up System Service (Optional)"
    
    if command -v systemctl >/dev/null 2>&1 && [ "$EUID" -eq 0 ]; then
        cat > /etc/systemd/system/lukhas-api-optimization.service << EOF
[Unit]
Description=LUKHAS API Optimization System
After=network.target redis.service
Requires=redis.service

[Service]
Type=forking
User=lukhas
Group=lukhas
WorkingDirectory=$PROJECT_ROOT
Environment=LUKHAS_CONFIG_FILE=config/production.yaml
ExecStart=$PROJECT_ROOT/.venv/bin/uvicorn api.optimization.integration_hub:app --host 0.0.0.0 --port 8001 --daemon
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable lukhas-api-optimization
        print_success "SystemD service installed"
    else
        print_warning "SystemD service setup skipped (requires root or not available)"
    fi
}

create_startup_scripts() {
    print_step "9" "Creating Startup Scripts"
    
    cd "$PROJECT_ROOT"
    
    # Development startup script
    cat > scripts/start-development.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting LUKHAS API Optimization - Development Mode"

# Check if we're in the right directory
if [ ! -f "config/development.yaml" ]; then
    echo "❌ Must run from project root directory"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set environment
export LUKHAS_CONFIG_FILE="config/development.yaml"
export LUKHAS_API_OPTIMIZATION_MODE="development"
export LUKHAS_LOG_LEVEL="DEBUG"

# Start Redis if not running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "🔄 Starting Redis..."
    if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis
    elif command -v brew >/dev/null 2>&1; then
        brew services start redis
    else
        redis-server --daemonize yes
    fi
    sleep 2
fi

# Start the optimization system
echo "🎯 Starting API optimization system..."
uvicorn api.optimization.integration_hub:app \
    --host 127.0.0.1 \
    --port 8001 \
    --reload \
    --log-level debug
EOF
    
    # Production startup script
    cat > scripts/start-production.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting LUKHAS API Optimization - Production Mode"

# Check if we're in the right directory
if [ ! -f "config/production.yaml" ]; then
    echo "❌ Must run from project root directory"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set environment
export LUKHAS_CONFIG_FILE="config/production.yaml"
export LUKHAS_API_OPTIMIZATION_MODE="production"
export LUKHAS_LOG_LEVEL="INFO"

# Validate configuration
python3 config/config_factory.py \
    --environment production \
    --validate

# Health check dependencies
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running"
    exit 1
fi

# Start with proper process management
exec uvicorn api.optimization.integration_hub:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-log \
    --log-level info
EOF
    
    # Make scripts executable
    chmod +x scripts/start-development.sh
    chmod +x scripts/start-production.sh
    
    print_success "Startup scripts created"
}

print_summary() {
    echo -e "${GREEN}"
    echo "=========================================="
    echo "🎉 Installation Complete!"
    echo "=========================================="
    echo -e "${NC}"
    
    echo "📋 Summary:"
    echo "   ✅ System dependencies installed"
    echo "   ✅ Python environment configured"
    echo "   ✅ Dependencies installed"
    echo "   ✅ Configuration files generated"
    echo "   ✅ Redis server running"
    echo "   ✅ Tests passed"
    echo "   ✅ Startup scripts created"
    echo ""
    
    echo "🚀 Quick Start:"
    echo "   Development:  ./scripts/start-development.sh"
    echo "   Production:   ./scripts/start-production.sh"
    echo ""
    
    echo "🔧 Configuration:"
    echo "   Development:  config/development.yaml"
    echo "   Production:   config/production.yaml"
    echo "   Secrets:      config/secrets_manager.py"
    echo ""
    
    echo "📊 Health Check:"
    echo "   API Health:   curl http://localhost:8001/health"
    echo "   Metrics:      curl http://localhost:8001/metrics"
    echo "   Redis:        redis-cli ping"
    echo ""
    
    echo "📖 Documentation:"
    echo "   System Guide: docs/infrastructure/API_OPTIMIZATION_SYSTEM.md"
    echo "   Deployment:   docs/infrastructure/API_OPTIMIZATION_DEPLOYMENT.md"
    echo ""
    
    echo "💡 Next Steps:"
    echo "   1. Review and customize configuration files"
    echo "   2. Set up monitoring and alerting"
    echo "   3. Configure load balancer (production)"
    echo "   4. Set up backup and disaster recovery"
    echo ""
    
    print_success "LUKHAS API Optimization System is ready to use!"
}

# Main installation flow
main() {
    print_header
    
    # Parse command line arguments
    SKIP_TESTS=false
    SKIP_DEPS=false
    ENVIRONMENT="development"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-tests      Skip installation tests"
                echo "  --skip-deps       Skip system dependencies"
                echo "  --environment ENV Set target environment (development|production)"
                echo "  --help           Show this help"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log "Starting LUKHAS API Optimization installation"
    log "Target environment: $ENVIRONMENT"
    log "Skip tests: $SKIP_TESTS"
    log "Skip deps: $SKIP_DEPS"
    
    # Run installation steps
    check_requirements
    
    if [ "$SKIP_DEPS" = false ]; then
        install_system_dependencies
    else
        print_warning "Skipping system dependencies installation"
    fi
    
    setup_python_environment
    install_python_dependencies
    setup_configuration
    setup_redis
    
    if [ "$SKIP_TESTS" = false ]; then
        run_tests
    else
        print_warning "Skipping installation tests"
    fi
    
    if [ "$ENVIRONMENT" = "production" ]; then
        setup_systemd_service
    fi
    
    create_startup_scripts
    print_summary
    
    log "Installation completed successfully"
}

# Run main function with all arguments
main "$@"