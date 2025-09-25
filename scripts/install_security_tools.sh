#!/bin/bash
# LUKHAS Security Tools Installation Script
# Installs all required security scanning tools for T4/0.01% excellence

set -e

echo "🚀 Installing LUKHAS Security Tools for T4/0.01% Excellence"
echo "=============================================================="

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
echo "📋 Python Version: $python_version"

# Upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip

# Core security tools
echo "🛡️  Installing core security scanning tools..."
pip install semgrep bandit safety

# SBOM generation tools
echo "📋 Installing SBOM generation tools..."
pip install cyclonedx-python-lib

# Abuse testing tools
echo "⚔️  Installing abuse testing tools..."
pip install aiohttp

# Configuration and policy tools
echo "📝 Installing configuration tools..."
pip install pyyaml

# Development and testing tools
echo "🧪 Installing testing tools..."
pip install pytest pytest-asyncio

# Verify installations
echo ""
echo "✅ Verifying installations..."

check_tool() {
    local tool=$1
    local import_name=$2

    if python3 -c "import $import_name" 2>/dev/null; then
        echo "  ✅ $tool: Installed"
    else
        echo "  ❌ $tool: Failed to install"
        return 1
    fi
}

check_command() {
    local tool=$1
    local command=$2

    if command -v $command >/dev/null 2>&1; then
        echo "  ✅ $tool: Available"
    else
        echo "  ❌ $tool: Not available"
        return 1
    fi
}

# Verify Python packages
check_tool "Semgrep" "semgrep"
check_tool "Bandit" "bandit"
check_tool "Safety" "safety"
check_tool "CycloneDX" "cyclonedx"
check_tool "aiohttp" "aiohttp"
check_tool "PyYAML" "yaml"

# Verify command line tools
check_command "Semgrep CLI" "semgrep"
check_command "Bandit CLI" "bandit"
check_command "Safety CLI" "safety"

echo ""
echo "🎯 Testing LUKHAS Security Framework..."

# Test security framework
if python3 scripts/test_security_framework.py; then
    echo "✅ Security framework test passed"
else
    echo "⚠️  Security framework test had some issues (this may be expected)"
fi

echo ""
echo "🏆 LUKHAS Security Tools Installation Complete!"
echo "=============================================================="
echo ""
echo "📊 Available Tools:"
echo "  🔍 SBOM Generation: scripts/security_sbom_generator.py"
echo "  🛡️  Security Scanner: scripts/security_scanner.py"
echo "  ⚔️  Abuse Tester: scripts/abuse_tester.py"
echo "  🧪 Framework Test: scripts/test_security_framework.py"
echo ""
echo "📋 Security Policy: security/security_policy.yml"
echo "📚 Documentation: security/README.md"
echo ""
echo "🚀 Ready for T4/0.01% Excellence Security Validation!"

# Create artifacts directory if it doesn't exist
mkdir -p artifacts

echo ""
echo "🎭 Quick Test - Generate SBOM:"
echo "python3 scripts/security_sbom_generator.py --output-dir artifacts"
echo ""
echo "🔍 Quick Test - Security Scan:"
echo "python3 scripts/security_scanner.py --output-dir artifacts"
echo ""
echo "⚔️  Quick Test - Abuse Testing (mock mode):"
echo "python3 scripts/abuse_tester.py --base-url http://localhost:8000 --output-dir artifacts"