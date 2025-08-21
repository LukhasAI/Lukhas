# Developer Guide

## Getting Started

This guide helps developers set up their environment for Health Advisor Plugin development.

## Prerequisites

1. **Development Environment**
   - Python 3.9+
   - Node.js 16+
   - Git
   - Docker

2. **Access Requirements**
   - GitHub access
   - Development API keys
   - Test provider credentials

## Initial Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/lucas-systems/health-advisor-plugin.git
   cd health-advisor-plugin
   ```

2. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configuration**
   ```bash
   # Copy configuration templates
   cp config/settings.template.yaml config/settings.yaml
   cp config/secrets.template.yaml config/secrets.yaml
   
   # Edit configurations with your settings
   vim config/settings.yaml
   vim config/secrets.yaml
   ```

## Development Workflow

1. **Branch Management**
   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name
   
   # Regular updates
   git fetch origin
   git rebase origin/main
   ```

2. **Testing**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test categories
   pytest tests/unit
   pytest tests/integration
   pytest tests/compliance
   ```

3. **Code Quality**
   ```bash
   # Run linters
   flake8 src tests
   black src tests
   isort src tests
   
   # Type checking
   mypy src
   ```

## Provider Development

1. **Creating New Provider**
   - Copy provider template
   - Implement required interfaces
   - Add configuration
   - Write tests

2. **Testing Provider**
   - Unit tests
   - Integration tests
   - Compliance validation
   - Performance testing

## Compliance Development

1. **Adding Compliance Rules**
   - Define requirements
   - Implement validations
   - Add audit logging
   - Test compliance

2. **Testing Compliance**
   - Regulation tests
   - Data protection
   - Audit trails
   - Security checks

## Documentation

1. **Code Documentation**
   - Docstrings
   - Type hints
   - Comments
   - Examples

2. **Project Documentation**
   - README updates
   - API documentation
   - Integration guides
   - Deployment guides

## Building & Packaging

1. **Local Build**
   ```bash
   # Build package
   python setup.py build
   
   # Create distribution
   python setup.py sdist bdist_wheel
   ```

2. **Docker Build**
   ```bash
   # Build container
   docker build -t health-advisor-plugin .
   
   # Run container
   docker run -p 8000:8000 health-advisor-plugin
   ```

## Debugging

1. **Local Debugging**
   - VS Code configuration
   - PyCharm setup
   - Debug logging
   - Error tracking

2. **Remote Debugging**
   - SSH tunneling
   - Remote debugger
   - Log access
   - Metrics viewing

## Deployment

1. **Staging Deployment**
   - Environment setup
   - Configuration
   - Testing
   - Monitoring

2. **Production Deployment**
   - Security review
   - Performance testing
   - Backup verification
   - Rollback plan

## Support

### Development Support
- GitHub Issues
- Developer Chat
- Documentation
- Code Reviews

### Security Support
- Security Advisories
- Vulnerability Reports
- Patch Management
- Security Reviews
