#!/usr/bin/env python3
"""
Jules Batch 5 - Architecture & Infrastructure
Focus: System design, CI/CD, DevOps, Infrastructure
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


BATCH5_SESSIONS = [
    {
        "title": "🏗️ P1: Implement Proper Logging Infrastructure",
        "prompt": """**HIGH PRIORITY: Replace print() with Structured Logging**

**Objective**: Replace all print() statements with proper structured logging

**Current State**: Many files use print() for debugging/output
**Target**: Structured logging with levels, contexts, and log aggregation

**Implementation**:

```python
import logging
import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger(__name__)

# Usage
logger.info("processing_request", request_id=req_id, user_id=user_id)
logger.error("operation_failed", error=str(e), traceback=tb)
logger.debug("cache_hit", key=cache_key, ttl=ttl_remaining)
```

**Replace Patterns**:

```python
# Before:
print(f"Processing request {req_id}")
print(f"Error: {e}")

# After:
logger.info("processing_request", request_id=req_id)
logger.error("request_failed", error=str(e), exc_info=True)
```

**Log Levels**:
- DEBUG: Detailed diagnostic info
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error events
- CRITICAL: Critical failures

**Add Context**:
```python
# Add request context
with logger.bind(request_id=req_id, user_id=user_id):
    logger.info("starting_operation")
    # ... operation ...
    logger.info("operation_complete")
```

**Expected Output**:
- All print() replaced with logging
- JSON-formatted logs
- Proper log levels
- Context preservation
- Log aggregation ready

**Commit Message**:
```
feat(logging): implement structured logging infrastructure

Problem:
- print() statements scattered everywhere
- No log levels or structured data
- Hard to aggregate and analyze
- No context preservation

Solution:
- Configured structlog for structured logging
- Replaced all print() with proper logging
- JSON output format
- Context binding
- Log levels throughout

Impact:
- Production-ready logging
- Aggregation-friendly format
- Better debugging
- ELK/Datadog compatible

Files: 100+ files updated
```

**Priority**: P1 - Production requirement
""",
    },
    {
        "title": "🏗️ P1: Create Makefile Targets for Common Tasks",
        "prompt": """**HIGH PRIORITY: Comprehensive Makefile for Developer Experience**

**Objective**: Create complete Makefile with all common development tasks

**Implementation**:

```makefile
.PHONY: help install dev test lint format clean docker

# Default target
help: ## Show this help message
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = \":.*?## \"}; {printf \"\\033[36m%-20s\\033[0m %s\\n\", $$1, $$2}'

# Development
install: ## Install dependencies
\tpip install -r requirements.txt
\tpip install -r requirements-dev.txt

dev: ## Start development environment
\tuvicorn serve.main:app --reload --host 0.0.0.0 --port 8000

shell: ## Start Python shell with LUKHAS loaded
\tipython -i -c "from lukhas import *"

# Testing
test: ## Run all tests
\tpytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-fast: ## Run fast tests only
\tpytest tests/unit tests/smoke -v -x

test-integration: ## Run integration tests
\tpytest tests/integration -v

test-e2e: ## Run end-to-end tests
\tpytest tests/e2e -v

test-watch: ## Run tests in watch mode
\tptw -- tests/

# Code Quality
lint: ## Run all linters
\truff check .
\tmypy .
\tbandit -r . -ll

lint-fix: ## Auto-fix linting issues
\truff check --fix .
\tblack .

format: ## Format code
\tblack .
\tisort .

type-check: ## Type checking only
\tmypy . --pretty

# Security
security: ## Run security checks
\tbandit -r . -ll -f json -o security-report.json
\tpip-audit
\tgitleaks detect

# Database
db-migrate: ## Run database migrations
\talembic upgrade head

db-reset: ## Reset database
\talembic downgrade base
\talembic upgrade head

db-seed: ## Seed database with test data
\tpython scripts/seed_database.py

# Docker
docker-build: ## Build Docker image
\tdocker build -t lukhas:latest .

docker-run: ## Run Docker container
\tdocker run -p 8000:8000 lukhas:latest

docker-compose-up: ## Start all services
\tdocker-compose up -d

docker-compose-down: ## Stop all services
\tdocker-compose down

# CI/CD
ci: lint test security ## Run CI pipeline locally

release: ## Create release
\tpython scripts/create_release.py

# Documentation
docs-build: ## Build documentation
\tcd docs && make html

docs-serve: ## Serve documentation locally
\tcd docs/_build/html && python -m http.server 8001

docs-api: ## Generate API documentation
\tpdoc --html --output-dir docs/api lukhas

# Cleanup
clean: ## Clean build artifacts
\tfind . -type d -name \"__pycache__\" -exec rm -rf {} +
\tfind . -type f -name \"*.pyc\" -delete
\trm -rf .pytest_cache .mypy_cache .ruff_cache
\trm -rf htmlcov coverage.xml .coverage
\trm -rf dist build *.egg-info

clean-deep: clean ## Deep clean including venv
\trm -rf .venv node_modules

# Utilities
count-lines: ## Count lines of code
\tfind . -name \"*.py\" -not -path \"./.venv/*\" -not -path \"./tests/*\" | xargs wc -l | tail -1

check-todos: ## List all TODO comments
\tgrep -r \"TODO\\|FIXME\\|XXX\" --include=\"*.py\" --exclude-dir=.venv | wc -l

check-coverage: ## Check test coverage percentage
\tpytest --cov=. --cov-report=term-missing | grep TOTAL

# Git hooks
setup-hooks: ## Setup git pre-commit hooks
\tpre-commit install
\tpre-commit run --all-files
```

**Additional Targets for LUKHAS Specific**:

```makefile
# LUKHAS Specific
matriz-test: ## Test MATRIZ cognitive engine
\tpytest tests/matriz -v -m \"not slow\"

guardian-test: ## Test Guardian system
\tpytest tests/governance -v

memory-test: ## Test memory system
\tpytest tests/memory -v

smoke: ## Run smoke tests
\tpytest tests/smoke -v -x

lane-guard: ## Validate lane boundaries
\tpython scripts/validate_lane_boundaries.py

# Performance
bench: ## Run benchmarks
\tpytest tests/performance --benchmark-only

profile: ## Profile application
\tpython -m cProfile -o profile.stats main.py
\tpython -m pstats profile.stats
```

**Expected Output**:
- Complete Makefile
- 40+ useful targets
- Good help documentation
- All common tasks covered

**Commit Message**:
```
feat(dev): comprehensive Makefile for developer experience

Problem:
- No standardized way to run common tasks
- New developers don't know commands
- Inconsistent testing/linting
- Manual CI/CD steps

Solution:
- Created 40+ Makefile targets
- Documented all commands
- Standardized workflows
- Easy onboarding

Impact:
- One-command operations
- Better developer experience
- Consistent CI/CD
- Easy for new contributors

Usage: make help
```

**Priority**: P1 - Developer experience
""",
    },
    {
        "title": "🔄 P1: Implement CI/CD Pipeline Improvements",
        "prompt": """**HIGH PRIORITY: Enhanced GitHub Actions CI/CD**

**Objective**: Improve CI/CD pipeline with comprehensive checks

**Implementation**:

**.github/workflows/ci.yml**:
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install ruff mypy black isort
      - name: Run ruff
        run: ruff check .
      - name: Run mypy
        run: mypy . --install-types --non-interactive
      - name: Check formatting
        run: |
          black --check .
          isort --check .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r . -ll -f json -o bandit-report.json
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2

  build:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t lukhas:${{ github.sha }} .
      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo \"${{ secrets.DOCKER_PASSWORD }}\" | docker login -u \"${{ secrets.DOCKER_USERNAME }}\" --password-stdin
          docker tag lukhas:${{ github.sha }} lukhasai/lukhas:latest
          docker push lukhasai/lukhas:latest
```

**.github/workflows/release.yml**:
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

**Expected Output**:
- Comprehensive CI/CD
- Multi-version testing
- Security scanning
- Auto-deployment
- Release automation

**Commit Message**:
```
ci: comprehensive GitHub Actions CI/CD pipeline

Problem:
- Basic CI pipeline
- No multi-version testing
- Missing security scans
- Manual deployments
- No release automation

Solution:
- Added lint, test, security jobs
- Multi-version Python testing (3.9-3.11)
- Integrated bandit, pip-audit, gitleaks
- Auto-deploy to Docker Hub
- Release workflow

Impact:
- Comprehensive CI checks
- Better code quality gates
- Security scanning on every PR
- Automated deployments
- Professional release process

CI: All checks passing
```

**Priority**: P1 - Infrastructure
""",
    },
    {
        "title": "📊 P2: Implement Prometheus Metrics Exporter",
        "prompt": """**MEDIUM PRIORITY: Complete Prometheus Metrics Integration**

**Objective**: Export comprehensive metrics for monitoring

**Implementation**:

```python
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

matriz_operations_total = Counter(
    'matriz_operations_total',
    'Total MATRIZ cognitive operations',
    ['operation_type', 'status']
)

matriz_operation_duration_ms = Histogram(
    'matriz_operation_duration_milliseconds',
    'MATRIZ operation latency',
    ['operation_type'],
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000]
)

active_thoughts = Gauge(
    'matriz_active_thoughts',
    'Number of active thoughts in MATRIZ'
)

memory_entries = Gauge(
    'memory_system_entries_total',
    'Total entries in memory system'
)

cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

system_info = Info(
    'lukhas_system',
    'LUKHAS system information'
)

system_info.info({
    'version': '1.0.0',
    'python_version': sys.version,
    'deployment': 'production'
})

# Middleware for automatic HTTP metrics
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    duration = time.time() - start_time
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# Metrics endpoint
@app.get('/metrics')
async def metrics():
    '''Prometheus metrics endpoint'''
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

**Custom Collectors**:

```python
from prometheus_client.core import GaugeMetricFamily
from prometheus_client import REGISTRY

class LUKHASCollector:
    '''Custom collector for LUKHAS metrics'''

    def collect(self):
        # Memory metrics
        yield GaugeMetricFamily(
            'lukhas_memory_bytes',
            'Memory usage in bytes',
            value=self.get_memory_usage()
        )

        # Active sessions
        yield GaugeMetricFamily(
            'lukhas_active_sessions',
            'Number of active sessions',
            value=self.get_active_sessions()
        )

REGISTRY.register(LUKHASCollector())
```

**Expected Output**:
- Complete metrics exporter
- /metrics endpoint
- Grafana-ready
- Custom collectors

**Commit Message**:
```
feat(monitoring): comprehensive Prometheus metrics

Problem:
- No metrics export
- Can't monitor system health
- No Grafana dashboards
- Missing observability

Solution:
- Implemented Prometheus exporter
- HTTP request metrics
- MATRIZ operation metrics
- Memory and cache metrics
- Custom collectors
- /metrics endpoint

Impact:
- Full observability
- Grafana dashboard ready
- Production monitoring
- Performance insights

Metrics: 15+ metrics exported
```

**Priority**: P2 - Observability
""",
    },
    {
        "title": "🐳 P2: Create Production Docker Compose Setup",
        "prompt": """**MEDIUM PRIORITY: Production-Ready Docker Compose**

**Objective**: Complete Docker Compose for full LUKHAS stack

**Implementation**:

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  lukhas-api:
    build: .
    image: lukhas:latest
    container_name: lukhas-api
    ports:
      - \"8000:8000\"
    environment:
      - DATABASE_URL=postgresql://lukhas:password@postgres:5432/lukhas
      - REDIS_URL=redis://redis:6379/0
      - PROMETHEUS_PORT=9090
    depends_on:
      - postgres
      - redis
      - prometheus
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8000/health\"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: lukhas-postgres
    environment:
      - POSTGRES_DB=lukhas
      - POSTGRES_USER=lukhas
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - \"5432:5432\"
    healthcheck:
      test: [\"CMD-SHELL\", \"pg_isready -U lukhas\"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: lukhas-redis
    ports:
      - \"6379:6379\"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: [\"CMD\", \"redis-cli\", \"ping\"]
      interval: 10s
      timeout: 3s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: lukhas-prometheus
    ports:
      - \"9090:9090\"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    container_name: lukhas-grafana
    ports:
      - \"3000:3000\"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus

  nginx:
    image: nginx:alpine
    container_name: lukhas-nginx
    ports:
      - \"80:80\"
      - \"443:443\"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - lukhas-api

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  default:
    name: lukhas-network
```

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lukhas'
    static_configs:
      - targets: ['lukhas-api:8000']
    metrics_path: '/metrics'
```

**nginx.conf**:
```nginx
upstream lukhas_backend {
    least_conn;
    server lukhas-api:8000;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://lukhas_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /metrics {
        deny all;
    }
}
```

**Expected Output**:
- Complete Docker Compose
- All services configured
- Health checks
- Monitoring integrated
- Production-ready

**Commit Message**:
```
feat(docker): production-ready Docker Compose setup

Problem:
- No complete Docker setup
- Manual service configuration
- No monitoring stack
- Missing reverse proxy

Solution:
- Created complete Docker Compose
- All services: API, Postgres, Redis
- Integrated Prometheus + Grafana
- Added Nginx reverse proxy
- Health checks configured
- Volume persistence

Impact:
- One-command deployment
- Complete stack
- Monitoring included
- Production-ready setup

Usage: docker-compose up -d
```

**Priority**: P2 - Deployment
""",
    },
    {
        "title": "📝 P2: Create CONTRIBUTING.md Guide",
        "prompt": """**MEDIUM PRIORITY: Comprehensive Contribution Guide**

**Objective**: Create detailed CONTRIBUTING.md for open source contributors

**Implementation**:

**CONTRIBUTING.md**:
```markdown
# Contributing to LUKHAS AI

Thank you for your interest in contributing to LUKHAS! This guide will help you get started.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

Please be respectful, inclusive, and professional in all interactions.

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- Docker (optional)

### Setup
\```bash
# Clone repository
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
make install

# Run tests
make test
\```

## Development Workflow

### 1. Create a Branch
\```bash
git checkout -b feature/your-feature-name
\```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test additions

### 2. Make Changes
- Follow coding standards (see below)
- Add tests for new features
- Update documentation

### 3. Run Quality Checks
\```bash
make lint        # Run all linters
make test        # Run all tests
make security    # Security checks
\```

### 4. Commit Changes
Follow our commit message format (see below).

### 5. Push and Create PR
\```bash
git push origin feature/your-feature-name
gh pr create
\```

## Coding Standards

### Python Style
- Follow PEP 8
- Use Black for formatting
- Type hints required
- Docstrings for public APIs

\```python
def process_data(input_data: Dict[str, Any]) -> ProcessedResult:
    '''
    Process input data and return structured result.

    Args:
        input_data: Dictionary containing input parameters

    Returns:
        ProcessedResult object with processed data

    Raises:
        ValueError: If input_data is invalid
    '''
    # Implementation
\```

### Import Organization
\```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import pandas as pd
import numpy as np

# Local imports
from lukhas.core import BaseComponent
from lukhas.memory import MemorySystem
\```

### Lane Boundaries
- `lukhas/` - Production code only
- `core/` - Tested integration components
- `candidate/` - Experimental features
- Never import from `candidate/` in `lukhas/`

## Testing Requirements

### Test Coverage
- Minimum 80% coverage for new code
- All public APIs must have tests
- Integration tests for cross-module features

### Test Structure
\```python
import pytest

class TestMyFeature:
    '''Tests for MyFeature'''

    @pytest.fixture
    def feature(self):
        return MyFeature()

    def test_basic_functionality(self, feature):
        result = feature.process("input")
        assert result == "expected"

    def test_error_handling(self, feature):
        with pytest.raises(ValueError):
            feature.process(None)
\```

### Running Tests
\```bash
# All tests
make test

# Specific tests
pytest tests/unit/test_myfeature.py -v

# With coverage
pytest --cov=lukhas tests/
\```

## Commit Messages

Format:
\```
<type>(<scope>): <subject>

<optional body>

<optional footer>
\```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Maintenance

Example:
\```
feat(memory): add vector similarity search

- Implemented cosine similarity
- Added batch processing
- Optimized for large datasets

Closes #123
\```

## Pull Request Process

### 1. Ensure Quality
- [ ] All tests pass
- [ ] Linting passes
- [ ] Security checks pass
- [ ] Documentation updated

### 2. Write PR Description
- Describe what changed
- Explain why
- Link related issues
- Add screenshots if UI changes

### 3. Request Review
Tag maintainers for review.

### 4. Address Feedback
Respond to comments and update PR.

### 5. Merge
Squash and merge when approved.

## Need Help?

- Open an issue for questions
- Join our Discord
- Check documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
\```

**Expected Output**:
- Complete CONTRIBUTING.md
- Clear guidelines
- Easy onboarding
- Professional standards

**Commit Message**:
```
docs: add comprehensive CONTRIBUTING.md guide

Problem:
- No contribution guidelines
- Unclear how to contribute
- New contributors confused
- No standards documented

Solution:
- Created comprehensive CONTRIBUTING.md
- Detailed development workflow
- Coding standards explained
- Testing requirements clear
- Commit message format
- PR process documented

Impact:
- Better open source readiness
- Clear contributor path
- Professional standards
- Easier onboarding

Ready for: Open source launch
```

**Priority**: P2 - Open source readiness
""",
    },
]


async def create_batch5():
    """Create Batch 5: Architecture & Infrastructure"""

    print("\n" + "="*80)
    print("🚀 JULES BATCH 5: ARCHITECTURE & INFRASTRUCTURE")
    print("="*80)
    print(f"\nCreating {len(BATCH5_SESSIONS)} sessions:")
    print("  🏗️ Infrastructure: 3 sessions")
    print("  📊 Monitoring: 1 session")
    print("  🐳 Docker: 1 session")
    print("  📝 Documentation: 1 session")
    print(f"\n  TOTAL: {len(BATCH5_SESSIONS)} sessions")
    print("="*80 + "\n")

    created = []
    failed = []

    async with JulesClient() as jules:
        for i, session_config in enumerate(BATCH5_SESSIONS, 1):
            try:
                print(f"\n[{i}/{len(BATCH5_SESSIONS)}] Creating: {session_config['title']}")

                session = await jules.create_session(
                    prompt=session_config['prompt'],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session['name'].split('/')[-1]
                created.append({
                    'title': session_config['title'],
                    'session_id': session_id
                })

                print(f"✅ Created: {session_id}")

            except Exception as e:
                if "429" in str(e):
                    print(f"⏸️  Rate limit - stopping")
                    failed.append(session_config)
                    break
                print(f"❌ Failed: {e}")
                failed.append(session_config)
                continue

            await asyncio.sleep(1)

    # Summary
    print("\n" + "="*80)
    print("📊 BATCH 5 SUMMARY")
    print("="*80)
    print(f"\n✅ Created: {len(created)}/{len(BATCH5_SESSIONS)}")

    if created:
        for s in created:
            print(f"\n• {s['title']}")
            print(f"  ID: {s['session_id']}")

    print(f"\n🎯 Total Today: {34 + len(created)}/100")
    print("="*80 + "\n")

    return created


if __name__ == "__main__":
    asyncio.run(create_batch5())
