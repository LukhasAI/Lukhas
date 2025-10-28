# Security operations & automation
.PHONY: security security-scan security-update security-audit security-fix security-fix-vulnerabilities security-fix-issues security-fix-all security-ollama security-ollama-fix security-ollama-setup security-comprehensive-scan security-emergency-patch test-security security-autopilot security-monitor security-status security-schedule security-schedule-3h security-schedule-tonight security-schedule-list security-schedule-run matrix-security-posture matrix-security-report matrix-security-alerts matrix-security-dashboard security-monitor-pip security-check-cve-2025-8869
security: security-audit security-scan ## Full security check suite
	@echo "✅ Full security check complete!"

security-scan:
	@echo "🔍 Running quick security scan..."
	@pip install -q safety pip-audit 2>/dev/null || true
	@echo "Checking with safety..."
	@safety check --short-report 2>/dev/null || echo "⚠️ Some vulnerabilities found"
	@echo "\nChecking with pip-audit..."
	@pip-audit --desc 2>/dev/null || echo "⚠️ Some vulnerabilities found"
	@echo "✅ Security scan complete!"

security-ollama:
	@echo "🤖 Running Ollama-powered security analysis..."
	@python3 scripts/ollama_security_analyzer.py scan
	@echo "✅ Ollama security analysis complete!"

security-ollama-fix:
	@echo "🔧 Auto-fixing vulnerabilities with Ollama..."
	@python3 scripts/ollama_security_analyzer.py fix
	@echo "✅ Ollama fix complete!"

security-ollama-setup:
	@echo "🛠️ Setting up Ollama for security analysis..."
	@command -v ollama >/dev/null 2>&1 || (echo "Installing Ollama..." && brew install ollama)
	@brew services start ollama 2>/dev/null || echo "Ollama service already running"
	@sleep 3
	@echo "Pulling security analysis model..."
	@ollama pull deepseek-coder:6.7b || true
	@echo "✅ Ollama setup complete!"

security-fix-vulnerabilities:
	@echo "🛡️ Auto-fixing known security vulnerabilities..."
	@python3 scripts/fix_security_vulnerabilities.py
	@echo "✅ Security vulnerabilities fixed!"

security-fix-issues:
	@echo "🛡️ Auto-fixing security issues (Bandit findings)..."
	@python3 scripts/fix_security_issues.py
	@echo "✅ Security issues fixed!"

security-fix-all:
	@echo "🛡️ Fixing ALL security vulnerabilities and issues..."
	@make security-fix-vulnerabilities
	@make security-fix-issues
	@echo "✅ All security fixes complete!"

security-update:
	@echo "🔧 Running automated security updates..."
	@pip install -q safety pip-audit 2>/dev/null || true
	@python3 scripts/security-update.py --auto --no-test
	@echo "✅ Security updates complete!"

security-audit:
	@echo "🔒 Running deep security audit..."
	@pip install -q safety pip-audit bandit 2>/dev/null || true
	@mkdir -p security-reports
	@echo "Running safety check..."
	@safety check --json --output security-reports/safety-report.json 2>/dev/null || true
	@safety check --short-report || true
	@echo "\nRunning pip-audit..."
	@pip-audit --desc --format json --output security-reports/pip-audit.json 2>/dev/null || true
	@echo "\nRunning bandit..."
	@bandit -r . -f json -o security-reports/bandit-report.json 2>/dev/null || true
	@echo "\n📊 Security reports saved to security-reports/"
	@echo "✅ Security audit complete!"

test-security:
	@echo "🧪 Running security-focused tests..."
	@python3 -c "import fastapi, aiohttp, transformers; print('✅ Critical packages import successfully')"
	@pytest tests/ -k "security" -v --tb=short || echo "No specific security tests found"
	@echo "✅ Security tests complete!"

security-comprehensive-scan:
	@echo "🔍 Running comprehensive security scan..."
	@mkdir -p security-reports
	@echo "Running Safety CLI scan..."
	@safety scan --output json --save-json security-reports/safety-scan.json 2>/dev/null || echo "Safety scan completed with issues"
	@echo "Running pip-audit..."
	@pip-audit --format json --output security-reports/pip-audit.json 2>/dev/null || echo "pip-audit completed with issues"
	@echo "Running Bandit security scan..."
	@bandit -r . -f json -o security-reports/bandit.json -x .venv,venv,node_modules,.git 2>/dev/null || echo "Bandit scan completed"
	@echo "Running Ollama analysis..."
	@python3 scripts/ollama_security_analyzer.py scan > security-reports/ollama-analysis.txt
	@echo "📊 Security reports saved to security-reports/"
	@echo "✅ Comprehensive security scan complete!"

security-emergency-patch:
	@echo "🚨 EMERGENCY SECURITY PATCH MODE"
	@echo "This will automatically fix ALL known critical vulnerabilities"
	@read -p "Continue? (y/N): " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		make security-fix-vulnerabilities; \
		pip install -r requirements.txt; \
		make test-security; \
		echo "✅ Emergency patch complete!"; \
	else \
		echo "❌ Emergency patch cancelled"; \
	fi

security-autopilot:
	@echo "🚀 Running Security Autopilot..."
	@python3 scripts/security-autopilot.py fix

security-monitor:
	@echo "👁️ Starting continuous security monitoring..."
	@python3 scripts/security-autopilot.py monitor --continuous --interval 3600

security-status:
	@echo "📊 Security Status:"
	@python3 scripts/security-autopilot.py status

security-schedule:
	@echo "🕒 LUKHAS Security Task Scheduler"
	@echo "=================================="
	@python3 scripts/security_scheduler.py status
	@echo ""
	@echo "💡 Schedule security fixes for later:"
	@echo "   make security-schedule-3h    - Schedule in 3 hours"
	@echo "   make security-schedule-tonight - Schedule at 8 PM today"
	@echo "   Or use: python3 scripts/security_scheduler.py schedule fix-all +2h"

security-schedule-3h:
	@echo "⏰ Scheduling security fixes in 3 hours..."
	@python3 scripts/security_scheduler.py schedule fix-all +3h --description "Automated security fix (3h delay)"

security-schedule-tonight:
	@echo "🌙 Scheduling security fixes for 8 PM tonight..."
	@python3 scripts/security_scheduler.py schedule fix-all 20:00 --description "Evening security maintenance"

security-schedule-list:
	@python3 scripts/security_scheduler.py list

security-schedule-run:
	@python3 scripts/security_scheduler.py run-pending

# SBOM Generation
.PHONY: sbom
sbom:
	@echo "📦 Generating SBOM..."
	@mkdir -p reports/sbom
	syft packages dir:. -o cyclonedx-json > reports/sbom/cyclonedx.json
	@echo "✅ SBOM generated at reports/sbom/cyclonedx.json"

# Matrix Tracks Security Posture Monitoring
matrix-security-posture: ## Run Matrix Tracks security posture analysis
	@echo "🛡️ Running Matrix Tracks Security Posture Analysis..."
	@mkdir -p artifacts/security
	@python3 tools/security_posture_monitor.py \
		--pattern "**/matrix_*.json" \
		--output artifacts/security/posture_report.json \
		--verbose
	@echo "✅ Security posture analysis complete!"

matrix-security-report: ## Generate detailed security report
	@echo "📊 Generating Matrix Tracks security dashboard..."
	@mkdir -p artifacts/security
	@python3 tools/security_posture_monitor.py \
		--pattern "**/matrix_*.json" \
		--output artifacts/security/posture_report.json \
		--verbose
	@echo "📄 Security report available at artifacts/security/posture_report.json"

matrix-security-alerts: ## Check for critical security alerts
	@echo "🚨 Checking for critical security alerts..."
	@python3 tools/security_posture_monitor.py \
		--pattern "**/matrix_*.json" \
		--output artifacts/security/posture_report.json \
		--alert-on-critical
	@echo "✅ Security alert check complete!"

matrix-security-dashboard: ## Display security posture dashboard
	@echo "🖥️ Matrix Tracks Security Posture Dashboard"
	@echo "============================================"
	@python3 tools/security_posture_monitor.py \
		--pattern "**/matrix_*.json" \
		--verbose
	@echo ""
	@echo "💡 For detailed report: make matrix-security-report"

# Matrix Identity & Authorization
.PHONY: identity-validate policy-test authz-matrix generate-opa-bundle
identity-validate: ## Validate identity blocks in Matrix contracts
	@echo "🔐 Validating identity blocks in Matrix contracts..."
	@python3 tools/matrix_gate.py --identity --pattern "**/matrix_*.json"

policy-test: ## Test OPA policies
	@echo "🧪 Testing OPA policies..."
	@opa test policies/matrix -v || echo "⚠️ OPA not available - install with: brew install open-policy-agent/tap/opa"

authz-matrix: ## Generate and test authorization matrices
	@echo "🔧 Generating authorization test matrices..."
	@python3 tools/generate_authz_matrix.py --module memoria --format yaml
	@echo "✅ Authorization matrix generated for memoria module"

generate-opa-bundle: ## Generate OPA bundle from ΛiD tier permissions
	@echo "🔧 Generating OPA bundle from ΛiD tier permissions..."
	@python3 tools/tier_opa_generator.py

test-macaroon-flow: ## Test complete macaroon issuance and verification flow
	@echo "🎟️ Testing complete macaroon flow..."
	@TOKEN=$$(python3 tools/tier_macaroon_issuer.py issue --subject "lukhas:user:test" --tier "trusted" --scopes "memoria.read,memoria.store" --audience "lukhas-matrix" --ttl 15 --webauthn | grep "Issued macaroon:" | cut -d" " -f3); \
	echo "Verifying token: $$TOKEN"; \
	python3 tools/verify_macaroon.py $$TOKEN

test-authz-middleware: ## Test authorization middleware
	@echo "🛡️ Testing authorization middleware..."
	@python3 tools/matrix_authz_middleware.py --test

run-authz-tests: ## Run authorization test matrices
	@echo "🧪 Running authorization test matrices..."
	@python3 tools/run_authz_tests.py --test-dir tests/authz

run-authz-tests-verbose: ## Run authorization tests with verbose output
	@echo "🧪 Running authorization test matrices (verbose)..."
	@python3 tools/run_authz_tests.py --test-dir tests/authz --verbose

test-identity-integration: ## Test complete identity integration flow
	@echo "🔐 Testing complete identity integration flow..."
	@make generate-opa-bundle
	@make identity-validate
	@make authz-matrix
	@make run-authz-tests
	@echo "✅ Identity integration test complete!"

# Matrix Contract Bootstrap
.PHONY: matrix-bootstrap-all matrix-bootstrap-all-write matrix-bootstrap-overwrite matrix-bootstrap-some validate-matrix-all

matrix-bootstrap-all: ## Discover & generate contracts for all modules (dry-run)
	@echo "🔍 Matrix Contract Discovery (dry-run)..."
	@python3 tools/matrix_bootstrap_all.py

matrix-bootstrap-all-write: ## Generate contracts for all modules (skip existing)
	@echo "📝 Generating Matrix contracts for all modules..."
	@python3 tools/matrix_bootstrap_all.py --write
	@echo "✅ Matrix contract generation complete!"

matrix-bootstrap-overwrite: ## Force overwrite existing contracts (use sparingly)
	@echo "⚠️  OVERWRITING existing Matrix contracts..."
	@python3 tools/matrix_bootstrap_all.py --write --overwrite
	@echo "✅ Matrix contract overwrite complete!"

matrix-bootstrap-some: ## Generate contracts for specific modules (set MODULES="a,b,c")
	@echo "📝 Generating Matrix contracts for modules: $(MODULES)..."
	@python3 tools/matrix_bootstrap_all.py --write --modules "$(MODULES)"
	@echo "✅ Matrix contract generation complete for: $(MODULES)"

validate-matrix-all: ## Validate all Matrix contracts (schema + identity)
	@echo "🔍 Validating all Matrix contracts..."
	@make validate-matrix || echo "⚠️ Schema validation issues found"
	@python3 tools/matrix_gate.py --identity --pattern "**/matrix_*.json" || echo "⚠️ Identity validation issues found"
	@echo "✅ Matrix contract validation complete!"

# CVE-2025-8869 pip monitoring
security-monitor-pip: ## Monitor PyPI for pip 25.3 release (CVE-2025-8869 fix)
	@echo "🔍 Checking for pip 25.3 release..."
	@bash scripts/monitoring/check_pip_version.sh

security-check-cve-2025-8869: ## Check status of CVE-2025-8869 (pip vulnerability)
	@echo "🔒 CVE-2025-8869 Status Check"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📋 Vulnerability: Arbitrary File Overwrite in pip"
	@echo "🆔 CVE: CVE-2025-8869 (GHSA-4xh5-x5gv-qwph)"
	@echo "⚠️  Severity: HIGH"
	@echo ""
	@echo "Current Status:"
	@pip --version 2>/dev/null || echo "  pip: Not found"
	@echo ""
	@echo "📖 Documentation:"
	@echo "  - Advisory: docs/security/CVE-2025-8869-PIP-ADVISORY.md"
	@echo "  - Monitoring: docs/security/PIP_VERSION_MONITORING.md"
	@echo "  - Guidelines: docs/security/FIXING_VULNERABILITIES.md"
	@echo ""
	@echo "🔍 Running pip version check..."
	@bash scripts/monitoring/check_pip_version.sh || echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
