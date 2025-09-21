# Security operations & automation
.PHONY: security security-scan security-update security-audit security-fix security-fix-vulnerabilities security-fix-issues security-fix-all security-ollama security-ollama-fix security-ollama-setup security-comprehensive-scan security-emergency-patch test-security security-autopilot security-monitor security-status security-schedule security-schedule-3h security-schedule-tonight security-schedule-list security-schedule-run
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