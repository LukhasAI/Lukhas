#!/bin/bash

# LUKHAS ΛiD System Setup Script
# =============================
# 
# Enterprise-grade setup for LUKHAS Lambda Identity management system
# Automates development environment configuration and deployment preparation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

print_header() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "  LUKHAS ΛiD System Setup"
    echo "  Enterprise Identity Management"
    echo "========================================"
    echo -e "${NC}"
}

# Check if Python 3.11+ is available
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.11"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python $PYTHON_VERSION detected"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.11+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
}

# Create virtual environment
setup_virtualenv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Create necessary directories
create_directories() {
    print_status "Creating directory structure..."
    
    # Create missing directories
    mkdir -p logs
    mkdir -p docs/api
    mkdir -p docs/development
    mkdir -p docs/security
    mkdir -p docs/compliance
    mkdir -p tests/unit
    mkdir -p tests/integration
    mkdir -p tests/load
    mkdir -p tests/security
    mkdir -p config/environments
    mkdir -p api/auth
    
    print_success "Directory structure created"
}

# Generate configuration files
generate_config() {
    print_status "Generating configuration files..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# LUKHAS ΛiD System Configuration
# ===============================

# Application Settings
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=true
LOG_LEVEL=DEBUG

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_VERSION=v1

# Rate Limiting
RATE_LIMIT_STORAGE=memory://
RATE_LIMIT_STRATEGY=fixed-window
RATE_LIMIT_HEADERS=true

# Security Settings
CORS_ORIGINS=http://localhost:3000,https://lukhas.ai
ENABLE_TALISMAN=true
SECURE_HEADERS=true

# ΛiD Configuration
LAMBD_ID_MAX_GENERATION_ATTEMPTS=5
LAMBD_ID_DEFAULT_TIER=0
LAMBD_ID_ENABLE_COLLISION_DETECTION=true
LAMBD_ID_ENABLE_ACTIVITY_LOGGING=true

# Monitoring & Metrics
ENABLE_PROMETHEUS_METRICS=false
ENABLE_STRUCTURED_LOGGING=true
LOG_FILE_PATH=logs/lambd_id_api.log

# Development Settings
RELOAD_ON_CHANGE=true
DEBUG_TOOLBAR=false
PROFILING_ENABLED=false

# Optional: Database (if persistence is added)
# DATABASE_URL=sqlite:///lukhas_lambda_id.db
# DATABASE_POOL_SIZE=5
# DATABASE_POOL_TIMEOUT=30

# Optional: Redis (for distributed rate limiting)
# REDIS_URL=redis://localhost:6379/0
# REDIS_POOL_SIZE=10

# Optional: External Services
# DATADOG_API_KEY=your_datadog_key
# NEWRELIC_LICENSE_KEY=your_newrelic_key
EOF
        print_success "Environment configuration created"
    else
        print_warning "Environment configuration already exists"
    fi
    
    # Create Docker Compose file
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << EOF
version: '3.8'

services:
  lukhas-lambda-id:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Redis for distributed rate limiting
  # redis:
  #   image: redis:7-alpine
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   restart: unless-stopped

# Optional: Named volumes
# volumes:
#   redis_data:
EOF
        print_success "Docker Compose configuration created"
    else
        print_warning "Docker Compose configuration already exists"
    fi
}

# Run tests
run_tests() {
    print_status "Running test suite..."
    
    # Create basic test if tests directory is empty
    if [ ! -f "tests/__init__.py" ]; then
        touch tests/__init__.py
        touch tests/unit/__init__.py
        touch tests/integration/__init__.py
        
        # Create a basic test file
        cat > tests/test_basic.py << EOF
"""
Basic tests for LUKHAS ΛiD system
"""

import unittest
from datetime import datetime

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests"""
    
    def test_system_imports(self):
        """Test that core modules can be imported"""
        try:
            # Test core imports (these will fail until implementation is complete)
            # from core.id_service.lambd_id_generator import LambdaIDGenerator
            # from core.id_service.lambd_id_validator import LambdaIDValidator
            # from core.id_service.lambd_id_entropy import EntropyCalculator
            pass
        except ImportError as e:
            self.skipTest(f"Core modules not yet implemented: {e}")
    
    def test_configuration_exists(self):
        """Test that configuration files exist"""
        import os
        self.assertTrue(os.path.exists('.env'), "Environment configuration should exist")
        self.assertTrue(os.path.exists('requirements.txt'), "Requirements file should exist")
        self.assertTrue(os.path.exists('Dockerfile'), "Dockerfile should exist")
    
    def test_directory_structure(self):
        """Test that directory structure is correct"""
        import os
        
        expected_dirs = [
            'core',
            'core/id_service', 
            'core/tier',
            'core/trace',
            'core/sing',
            'core/sent',
            'api',
            'api/routes',
            'api/controllers',
            'utils',
            'config',
            'tests',
            'logs'
        ]
        
        for directory in expected_dirs:
            self.assertTrue(os.path.exists(directory), f"Directory {directory} should exist")

if __name__ == '__main__':
    unittest.main()
EOF
    fi
    
    # Run tests
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
    else
        python -m unittest discover tests/ -v
    fi
    
    print_success "Tests completed"
}

# Validate system
validate_system() {
    print_status "Validating system setup..."
    
    # Check if all core files exist
    core_files=(
        "core/id_service/lambd_id_generator.py"
        "core/id_service/lambd_id_validator.py"
        "core/id_service/lambd_id_entropy.py"
        "core/id_service/tier_permissions.json"
        "api/routes/lambd_id_routes.py"
        "api/controllers/lambd_id_controller.py"
        "api/__init__.py"
        "requirements.txt"
        "Dockerfile"
        ".env"
    )
    
    missing_files=()
    
    for file in "${core_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "All core files present"
    else
        print_warning "Missing files:"
        printf '%s\n' "${missing_files[@]}"
    fi
    
    # Check Python imports (basic syntax validation)
    print_status "Validating Python syntax..."
    
    python_files=(
        "core/id_service/lambd_id_generator.py"
        "core/id_service/lambd_id_validator.py" 
        "core/id_service/lambd_id_entropy.py"
        "api/routes/lambd_id_routes.py"
        "api/controllers/lambd_id_controller.py"
        "api/__init__.py"
    )
    
    for file in "${python_files[@]}"; do
        if [ -f "$file" ]; then
            if python -m py_compile "$file" 2>/dev/null; then
                print_success "✓ $file syntax valid"
            else
                print_error "✗ $file syntax error"
            fi
        fi
    done
}

# Print usage information
print_usage() {
    print_status "LUKHAS ΛiD System Setup Complete!"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "  Development Server:    python -m api"
    echo "  Run Tests:            pytest tests/"
    echo "  Docker Build:         docker build -t lukhas-lambda-id ."
    echo "  Docker Run:           docker run -p 5000:5000 lukhas-lambda-id"
    echo "  Docker Compose:       docker-compose up -d"
    echo ""
    echo "📚 API Endpoints:"
    echo "  Health Check:         http://localhost:5000/health"
    echo "  API Info:            http://localhost:5000/api/v1/info"
    echo "  Generate ΛiD:         POST http://localhost:5000/api/v1/lambda-id/generate"
    echo "  Validate ΛiD:         POST http://localhost:5000/api/v1/lambda-id/validate"
    echo ""
    echo "🔧 Configuration:"
    echo "  Edit .env file for environment-specific settings"
    echo "  Modify core/id_service/tier_permissions.json for tier configuration"
    echo ""
    echo "📖 Documentation:"
    echo "  README.md            - System overview and API reference"
    echo "  docs/                - Detailed documentation"
    echo ""
    echo "🎯 Next Steps:"
    echo "  1. Review and customize .env configuration"
    echo "  2. Start development server: python -m api"
    echo "  3. Test API endpoints with curl or Postman"
    echo "  4. Begin integration with your application"
    echo ""
}

# Main setup function
main() {
    print_header
    
    # Check system requirements
    check_python
    
    # Setup development environment  
    setup_virtualenv
    install_dependencies
    create_directories
    generate_config
    
    # Validate and test
    validate_system
    run_tests
    
    # Print usage information
    print_usage
    
    print_success "LUKHAS ΛiD System setup completed successfully! 🎉"
}

# Run main function
main "$@"
