---
status: wip
type: documentation
owner: unknown
module: makefile
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# LUKHAS Makefile Examples & Best Practices

## Fragment Development Examples

### Creating a New Fragment

When adding functionality to the LUKHAS build system, organize related targets into domain-specific fragments:

```makefile
# mk/deployment.mk - Example deployment fragment
.PHONY: deploy deploy-staging deploy-prod deploy-rollback

deploy: deploy-staging ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@kubectl apply -f k8s/staging/
	@echo "✅ Staging deployment complete"

deploy-prod: ## Deploy to production (requires confirmation)
	@echo "🚨 Production deployment requires confirmation"
	@read -p "Deploy to production? (y/N): " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		kubectl apply -f k8s/production/; \
		echo "✅ Production deployment complete"; \
	else \
		echo "❌ Production deployment cancelled"; \
	fi

deploy-rollback: ## Rollback last deployment
	@echo "🔄 Rolling back deployment..."
	@kubectl rollout undo deployment/lukhas-api
	@echo "✅ Rollback complete"
```

### Target Documentation Patterns

**Simple Targets:**
```makefile
clean: ## Remove build artifacts and cache files
	rm -rf build/ dist/ *.egg-info

lint: ## Run code quality checks
	ruff check . --quiet
	mypy . --ignore-missing-imports
```

**Complex Targets with Dependencies:**
```makefile
release: test lint security-scan ## Create production release (full validation)
	@echo "🏗️ Building production release..."
	python -m build
	twine check dist/*
	@echo "✅ Release ready for deployment"
```

**Conditional Targets:**
```makefile
test-gpu: ## Run GPU-accelerated tests (requires CUDA)
	@command -v nvidia-smi >/dev/null || (echo "❌ CUDA not available"; exit 1)
	CUDA_VISIBLE_DEVICES=0 pytest tests/gpu/ -v
```

## Common Workflow Patterns

### Development Workflow

```bash
# Start new development session
make bootstrap          # Setup environment
make doctor            # Verify system health
make dev               # Start development server

# During development
make quick             # Fix issues and test
make test-tier1-matriz # Fast validation
make lint              # Code quality check

# Before committing
make test-cov          # Full test suite with coverage
make security-scan     # Security validation
make doctor-strict     # Strict health check
```

### CI/CD Integration

```bash
# Local CI simulation
make ci-local          # Full CI pipeline locally
make audit-scan        # Compliance validation
make api-spec          # Generate API documentation

# Pre-deployment checks
make security-audit    # Deep security analysis
make test-advanced     # Advanced testing suite
make policy           # Policy compliance
```

### Security Maintenance

```bash
# Regular security maintenance
make security-scan     # Quick vulnerability check
make security-update   # Update vulnerable packages
make test-security     # Security-focused tests

# Emergency response
make security-emergency-patch  # Critical vulnerability fixes
make security-comprehensive-scan  # Full security audit

# Scheduled maintenance
make security-schedule-tonight  # Schedule evening maintenance
make security-monitor  # Continuous monitoring
```

## Advanced Usage Patterns

### Parameterized Targets

```makefile
# mk/deployment.mk
deploy-env: ## Deploy to specified environment (ENV=staging|prod)
	@if [ -z "$(ENV)" ]; then \
		echo "Usage: make deploy-env ENV=staging|prod"; \
		exit 1; \
	fi
	@echo "🚀 Deploying to $(ENV)..."
	kubectl apply -f k8s/$(ENV)/
```

Usage:
```bash
make deploy-env ENV=staging
make deploy-env ENV=prod
```

### Conditional Execution

```makefile
# mk/tests.mk
test-with-coverage: ## Run tests with coverage (CI=true for XML output)
	@if [ "$(CI)" = "true" ]; then \
		pytest --cov=lukhas --cov-report=xml --cov-report=term; \
	else \
		pytest --cov=lukhas --cov-report=html --cov-report=term; \
	fi
```

### Multi-Stage Targets

```makefile
# mk/release.mk
release-candidate: ## Create release candidate with full validation
	@echo "🔍 Stage 1: Validation"
	@$(MAKE) test-advanced
	@$(MAKE) security-audit
	@$(MAKE) policy
	@echo "🏗️ Stage 2: Build"
	@$(MAKE) build-artifacts
	@echo "📊 Stage 3: Quality Gates"
	@$(MAKE) performance-benchmark
	@echo "✅ Release candidate ready"
```

## Error Handling Patterns

### Graceful Degradation

```makefile
# mk/optional.mk
optional-feature: ## Optional feature (gracefully handles missing deps)
	@if command -v special-tool >/dev/null 2>&1; then \
		echo "✅ Running with special-tool"; \
		special-tool --analyze; \
	else \
		echo "⚠️ special-tool not available, using fallback"; \
		python scripts/fallback_analysis.py; \
	fi
```

### Dependency Validation

```makefile
# mk/validation.mk
check-deps: ## Validate required dependencies
	@echo "🔍 Checking dependencies..."
	@missing=0; \
	for cmd in python3 git ruff pytest; do \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			echo "❌ Missing: $$cmd"; \
			missing=1; \
		fi; \
	done; \
	if [ $$missing -eq 1 ]; then \
		echo "💡 Install missing dependencies and retry"; \
		exit 1; \
	fi
	@echo "✅ All dependencies available"
```

### Recovery Suggestions

```makefile
# mk/troubleshooting.mk
doctor-fix: ## Auto-fix common doctor issues
	@echo "🔧 Auto-fixing common issues..."
	@if [ ! -d ".venv" ]; then \
		echo "📦 Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@if [ ! -f ".venv/bin/pytest" ]; then \
		echo "📦 Installing test dependencies..."; \
		.venv/bin/pip install pytest pytest-cov; \
	fi
	@echo "✅ Common issues resolved"
```

## Performance Optimization Examples

### Parallel Execution

```makefile
# mk/parallel.mk
test-parallel: ## Run tests in parallel with optimal worker count
	@workers=$$(python3 -c "import os; print(min(8, os.cpu_count()))"); \
	echo "🧪 Running tests with $$workers workers"; \
	pytest -n $$workers tests/

lint-parallel: ## Run linting tools in parallel
	@echo "🔍 Running parallel linting..."
	@$(MAKE) -j4 lint-ruff lint-mypy lint-bandit lint-imports

lint-ruff:
	@ruff check . --quiet

lint-mypy:
	@mypy . --ignore-missing-imports

lint-bandit:
	@bandit -r . -ll

lint-imports:
	@python tools/ci/check_imports.py
```

### Caching Strategies

```makefile
# mk/cache.mk
.cache/%.analyzed: %.py ## Cache analysis results
	@mkdir -p .cache
	@echo "🔍 Analyzing $<..."
	@python tools/analyze.py $< > $@

analyze-cached: $(patsubst %.py,.cache/%.analyzed,$(wildcard src/*.py)) ## Cached analysis
	@echo "✅ Analysis complete (cached)"
```

### Resource Management

```makefile
# mk/resources.mk
heavy-task: ## Resource-intensive task with memory management
	@echo "🧠 Checking available memory..."
	@free_mb=$$(free -m | awk 'NR==2{print $$7}'); \
	if [ $$free_mb -lt 4000 ]; then \
		echo "⚠️ Low memory ($$free_mb MB), running in conservative mode"; \
		python scripts/heavy_task.py --memory-limit 2G; \
	else \
		echo "✅ Sufficient memory ($$free_mb MB), running optimized"; \
		python scripts/heavy_task.py --memory-limit 8G; \
	fi
```

## Integration Examples

### Docker Integration

```makefile
# mk/docker.mk
docker-build: ## Build Docker image with caching
	@echo "🐳 Building Docker image..."
	docker build --cache-from lukhas:latest -t lukhas:dev .

docker-test: ## Run tests in Docker environment
	@echo "🧪 Testing in Docker..."
	docker run --rm -v $(PWD):/app lukhas:dev make test

docker-clean: ## Clean Docker artifacts
	@echo "🧹 Cleaning Docker..."
	docker system prune -f
	docker volume prune -f
```

### Git Integration

```makefile
# mk/git.mk
git-hooks: ## Install Git hooks
	@echo "🔗 Installing Git hooks..."
	@cp tools/git-hooks/* .git/hooks/
	@chmod +x .git/hooks/*
	@echo "✅ Git hooks installed"

release-tag: ## Create release tag (VERSION=x.y.z required)
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release-tag VERSION=1.2.3"; \
		exit 1; \
	fi
	@git tag -a v$(VERSION) -m "Release version $(VERSION)"
	@git push origin v$(VERSION)
	@echo "✅ Tagged release v$(VERSION)"
```

### External Tool Integration

```makefile
# mk/tools.mk
format-all: ## Format code with multiple tools
	@echo "🎨 Formatting Python..."
	@black --line-length 88 .
	@isort --profile black .
	@echo "🎨 Formatting JavaScript..."
	@if [ -d "frontend/" ]; then \
		cd frontend && npm run format; \
	fi
	@echo "🎨 Formatting YAML..."
	@find . -name "*.yml" -o -name "*.yaml" | xargs yamlfmt
```

## Testing Strategy Examples

### Test Matrix

```makefile
# mk/test-matrix.mk
test-matrix: ## Run tests across Python versions
	@for py in python3.8 python3.9 python3.10 python3.11; do \
		if command -v $$py >/dev/null 2>&1; then \
			echo "🧪 Testing with $$py"; \
			$$py -m pytest tests/ --tb=short; \
		else \
			echo "⚠️ $$py not available"; \
		fi; \
	done
```

### Environment-Specific Testing

```makefile
# mk/env-tests.mk
test-dev: ## Run development environment tests
	@ENVIRONMENT=development pytest tests/ -m "not prod"

test-staging: ## Run staging environment tests  
	@ENVIRONMENT=staging pytest tests/ -m "staging or not prod"

test-prod: ## Run production-safe tests only
	@ENVIRONMENT=production pytest tests/ -m "prod" --no-cov
```

## Best Practices Summary

### Target Naming Conventions

- Use kebab-case: `test-tier1-matriz`, not `test_tier1_matriz`
- Be descriptive: `security-comprehensive-scan`, not `sec-scan`
- Group related targets: `docker-build`, `docker-test`, `docker-clean`
- Use consistent prefixes: `test-*`, `security-*`, `doctor-*`

### Documentation Standards

- Always include `## Description` for user-facing targets
- Keep descriptions concise but informative (< 60 characters)
- Use consistent terminology across descriptions
- Document required parameters in descriptions

### Error Handling

- Provide clear error messages with actionable suggestions
- Use exit codes appropriately (0 = success, non-zero = failure)
- Implement graceful degradation for optional features
- Include recovery instructions in error messages

### Performance Considerations

- Minimize shell command invocations in hot paths
- Use Make's built-in functions when possible
- Cache expensive computations
- Design targets for parallel execution when appropriate

### Maintenance Guidelines

- Keep fragments focused on single domains
- Regularly review and consolidate duplicate functionality
- Update documentation when behavior changes
- Test target interactions across fragments

These examples provide a foundation for extending the LUKHAS Makefile system while maintaining consistency, reliability, and usability across all build automation workflows.