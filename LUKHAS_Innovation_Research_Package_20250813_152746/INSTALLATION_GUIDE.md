# LUKHAS Innovation System - Installation & Testing Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Running Tests](#running-tests)
5. [Troubleshooting](#troubleshooting)
6. [API Configuration](#api-configuration)
7. [Docker Deployment](#docker-deployment)

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM
- **Storage**: 500MB free space
- **Network**: Internet connection for API calls

### Required Software
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check pip
pip3 --version

# Check git (optional)
git --version
```

## Quick Start

### 1. One-Line Installation
```bash
# Clone or extract package, then:
make setup && make test
```

### 2. Manual Quick Start
```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...

# Run quick test
python3 src/test_innovation_quick_baseline.py
```

## Detailed Installation

### Step 1: Environment Setup

#### Option A: Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### Option B: Conda Environment
```bash
# Create conda environment
conda create -n lukhas python=3.10

# Activate environment
conda activate lukhas
```

### Step 2: Install Dependencies

```bash
# Core dependencies only
pip install -r requirements.txt

# Or install as package with all extras
pip install -e ".[full]"

# For development
pip install -e ".[dev]"
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Required configuration:
```env
# Minimum required
OPENAI_API_KEY=your-key-here

# Optional but recommended
GUARDIAN_DRIFT_THRESHOLD=0.15
LOG_LEVEL=INFO
```

### Step 4: Verify Installation

```bash
# Check system readiness
make check

# Or manually verify
python3 -c "import openai; print('OpenAI: OK')"
python3 -c "import numpy; print('NumPy: OK')"
python3 -c "from src.core.common import get_logger; print('Core: OK')"
```

## Running Tests

### Basic Test Execution

#### Quick Test (7 scenarios, ~1 minute)
```bash
# Using make
make test

# Direct execution
python3 src/test_innovation_quick_baseline.py

# With custom threshold
GUARDIAN_DRIFT_THRESHOLD=0.14 python3 src/test_innovation_quick_baseline.py
```

#### Comprehensive Test (60 scenarios, ~15 minutes)
```bash
# Using make
make full-test

# Direct execution
python3 src/test_innovation_research_baseline.py

# With progress monitoring
python3 -u src/test_innovation_research_baseline.py | tee test_log.txt
```

### Analysis and Reporting

```bash
# Analyze results
make analyze

# Or run analysis directly
python3 src/analyze_pass_rate_factors.py

# Generate comprehensive report
python3 src/generate_report.py  # If available
```

### Test Output Locations

- **Test Results**: `test_results/`
- **Data Files**: `data/`
- **Logs**: `logs/`
- **Research Data**: `research_data/`

## Troubleshooting

### Common Issues and Solutions

#### 1. OpenAI API Key Issues
```bash
# Error: "OpenAI API key not found"
# Solution: Ensure .env file exists and contains valid key
echo "OPENAI_API_KEY=sk-your-key" > .env

# Test API key
python3 -c "import os; from openai import OpenAI; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('API key valid')"
```

#### 2. Import Errors
```bash
# Error: "ModuleNotFoundError: No module named 'openai'"
# Solution: Install missing dependencies
pip install openai

# Or reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### 3. Permission Errors
```bash
# Error: "Permission denied"
# Solution: Set correct permissions
chmod +x setup.py
chmod 755 src/*.py
```

#### 4. Path Issues
```bash
# Error: "No module named 'src'"
# Solution: Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from package root
cd LUKHAS_Innovation_Research_Package_*
python3 -m src.test_innovation_quick_baseline
```

#### 5. API Rate Limiting
```bash
# Error: "Rate limit exceeded"
# Solution: Add delays or reduce batch size
API_RATE_LIMIT_PER_MINUTE=10 python3 src/test_innovation_quick_baseline.py
```

## API Configuration

### OpenAI Configuration
```env
# Required
OPENAI_API_KEY=sk-proj-...

# Optional
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=600
```

### Using Different Models
```bash
# GPT-3.5 (faster, cheaper)
OPENAI_MODEL=gpt-3.5-turbo python3 src/test_innovation_quick_baseline.py

# GPT-4 (better quality)
OPENAI_MODEL=gpt-4 python3 src/test_innovation_quick_baseline.py
```

### Fallback Mode (No API)
```bash
# Use fallback generation without API
USE_MOCK_DATA=true python3 src/test_innovation_quick_baseline.py

# Or remove API key to trigger fallback
unset OPENAI_API_KEY
python3 src/test_innovation_quick_baseline.py
```

## Docker Deployment

### Build and Run with Docker

```bash
# Build image
docker build -t lukhas-innovation:latest .

# Run with environment file
docker run --env-file .env lukhas-innovation:latest

# Run with inline environment
docker run -e OPENAI_API_KEY=sk-... lukhas-innovation:latest

# Interactive mode
docker run -it --env-file .env lukhas-innovation:latest /bin/bash

# Mount local directory for results
docker run -v $(pwd)/test_results:/app/test_results --env-file .env lukhas-innovation:latest
```

### Docker Compose (if docker-compose.yml exists)
```bash
# Start services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Advanced Usage

### Custom Test Scenarios

Create a custom test file:
```python
# my_test.py
from src.test_innovation_research_baseline import InnovationResearchTester

async def run_custom_test():
    tester = InnovationResearchTester(use_api=True)
    # Add custom logic here
    
import asyncio
asyncio.run(run_custom_test())
```

### Batch Processing
```bash
# Run multiple tests with different thresholds
for threshold in 0.10 0.15 0.20; do
    GUARDIAN_DRIFT_THRESHOLD=$threshold python3 src/test_innovation_quick_baseline.py
    mv test_results/latest.json test_results/threshold_${threshold}.json
done
```

### Performance Monitoring
```bash
# Time execution
time make test

# Monitor resource usage
python3 -m cProfile -o profile.stats src/test_innovation_quick_baseline.py

# Memory profiling (requires memory_profiler)
python3 -m memory_profiler src/test_innovation_quick_baseline.py
```

## Support

### Getting Help

1. **Check Documentation**: Review README.md and this guide
2. **Examine Logs**: Check `logs/` directory for error details
3. **Test Connection**: Verify API connectivity
4. **Minimal Test**: Try fallback mode first

### Contact Information

- **Technical Support**: support@lukhas.ai
- **Research Questions**: research@lukhas.ai
- **Bug Reports**: Create issue in project repository

## Next Steps

After successful installation:

1. ✅ Run quick baseline test
2. 📊 Analyze results with `make analyze`
3. 🔬 Review findings in `test_results/`
4. 🚀 Deploy to production environment
5. 📈 Monitor and optimize thresholds

---

*Last Updated: August 13, 2025*
*Version: 1.0.0*