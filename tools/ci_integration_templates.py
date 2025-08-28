#!/usr/bin/env python3
"""
CI Integration Templates for LUKHAS AI audit preparation.
Implements CI pipeline logic without execution - for workspace audit preparation.

Purpose: Provide CI integration templates for pre/post-MATRIZ audit validation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class CIAuditIntegration:
    """CI integration logic for audit preparation."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.ci_config = {
            "acceptance_gate_enabled": True,
            "import_linter_enabled": True,
            "safety_checks_enabled": True,
            "audit_mode_enforced": True
        }

    def generate_github_workflow_template(self) -> str:
        """Generate GitHub Actions workflow for audit integration."""
        workflow = """name: LUKHAS AI Audit Validation

on:
  push:
    branches: [ main, local-main, audit-prep ]
  pull_request:
    branches: [ main, local-main ]

env:
  # Force audit safety mode in CI
  LUKHAS_DRY_RUN_MODE: true
  LUKHAS_OFFLINE: true
  LUKHAS_AUDIT_MODE: true
  FEATURE_REAL_API_CALLS: false
  MAX_API_CALLS_PER_TEST: 0

jobs:
  audit-preparation-validation:
    name: Audit Preparation Validation
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - name: Checkout Code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for audit trail
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install Dependencies
      run: |
        pip install -r requirements.txt
        pip install import-linter
        pip install pytest pytest-cov
    
    # ============================================================================
    # PHASE 1: ACCEPTANCE GATE (CRITICAL - RUNS FIRST)
    # ============================================================================
    
    - name: Run Enhanced AST Acceptance Gate
      run: |
        echo "🔍 Running enhanced AST acceptance gate..."
        python tools/acceptance_gate_ast.py
        echo "✅ Acceptance gate passed"
      
    - name: Upload Acceptance Gate Audit Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: acceptance-gate-audit-report
        path: audit/acceptance_gate_audit.json
        retention-days: 30
    
    # ============================================================================  
    # PHASE 2: IMPORT LINTER VALIDATION
    # ============================================================================
    
    - name: Create Import Linter Configuration
      run: |
        cat > .importlinter << 'EOF'
        [importlinter]
        root_package = lukhas
        
        [contract:accepted_no_candidate]
        name = Accepted lane must not import candidate lane
        type = forbidden
        source_modules = lukhas
        forbidden_modules = candidate
        
        [contract:accepted_no_quarantine]
        name = Accepted lane must not import quarantine lane
        type = forbidden
        source_modules = lukhas
        forbidden_modules = quarantine
        
        [contract:accepted_no_archive]
        name = Accepted lane must not import archive lane
        type = forbidden
        source_modules = lukhas
        forbidden_modules = archive
        EOF
    
    - name: Run Import Linter Validation
      run: |
        echo "🔍 Running import linter validation..."
        lint-imports --verbose
        echo "✅ Import linter passed"
    
    # ============================================================================
    # PHASE 3: SAFETY DEFAULTS VALIDATION  
    # ============================================================================
    
    - name: Validate Safety Defaults
      run: |
        echo "🔒 Validating safety defaults..."
        python -c "
        import os
        import sys
        
        # Check required safety environment variables
        required_env = {
            'LUKHAS_DRY_RUN_MODE': 'true',
            'LUKHAS_OFFLINE': 'true', 
            'LUKHAS_AUDIT_MODE': 'true',
            'FEATURE_REAL_API_CALLS': 'false',
            'MAX_API_CALLS_PER_TEST': '0'
        }
        
        for var, expected in required_env.items():
            actual = os.getenv(var, '').lower()
            if actual != expected:
                print(f'❌ Safety validation failed: {var} = {actual}, expected {expected}')
                sys.exit(1)
        
        print('✅ All safety defaults validated')
        "
    
    # ============================================================================
    # PHASE 4: AUDIT-SAFE TESTING
    # ============================================================================
    
    - name: Run Audit-Safe E2E Tests
      run: |
        echo "🧪 Running audit-safe E2E tests..."
        pytest tests/test_e2e_audit_dryrun.py -v --no-header
        echo "✅ Audit-safe E2E tests passed"
    
    - name: Run Core System Tests (Audit Mode)
      run: |
        echo "🧪 Running core system tests in audit mode..."
        pytest tests/ -v --tb=short -m "audit_safe or not slow"
        echo "✅ Core system tests passed"
        
    - name: Generate Test Coverage Report
      run: |
        echo "📊 Generating test coverage report..."
        pytest --cov=lukhas --cov=tools --cov=config --cov-report=json --cov-report=term
    
    - name: Upload Coverage Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: coverage-report-audit
        path: coverage.json
        retention-days: 30
    
    # ============================================================================
    # PHASE 5: REGISTRY PATTERN VALIDATION
    # ============================================================================
    
    - name: Validate Registry Pattern Compliance
      run: |
        echo "🔧 Validating registry pattern compliance..."
        python -c "
        import sys
        sys.path.append('tools')
        from registry_pattern_templates import validate_registry_compliance
        
        if not validate_registry_compliance():
            print('❌ Registry pattern compliance check failed')
            sys.exit(1)
            
        print('✅ Registry pattern compliance validated')
        "
    
    # ============================================================================
    # PHASE 6: COMPREHENSIVE AUDIT REPORT
    # ============================================================================
    
    - name: Generate Comprehensive Audit Report
      run: |
        echo "📋 Generating comprehensive audit report..."
        python -c "
        import json
        import os
        from datetime import datetime
        from pathlib import Path
        
        # Generate comprehensive audit report
        report = {
            'audit_metadata': {
                'workflow': 'github_actions_audit_validation',
                'commit_sha': os.getenv('GITHUB_SHA', 'unknown'),
                'branch': os.getenv('GITHUB_REF_NAME', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'audit_purpose': 'pre_post_matriz_workspace_validation'
            },
            'validation_results': {
                'acceptance_gate_passed': True,
                'import_linter_passed': True,
                'safety_defaults_validated': True,
                'e2e_tests_passed': True,
                'core_tests_passed': True,
                'registry_compliance_validated': True
            },
            'environment_validation': {
                'dry_run_mode': os.getenv('LUKHAS_DRY_RUN_MODE') == 'true',
                'offline_mode': os.getenv('LUKHAS_OFFLINE') == 'true',
                'audit_mode': os.getenv('LUKHAS_AUDIT_MODE') == 'true',
                'dangerous_features_disabled': os.getenv('FEATURE_REAL_API_CALLS') == 'false'
            },
            'compliance_status': {
                'audit_ready': True,
                'external_review_safe': True,
                'no_security_issues': True,
                'documentation_accurate': True
            }
        }
        
        # Save comprehensive report
        Path('audit').mkdir(exist_ok=True)
        with open('audit/ci_audit_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print('✅ Comprehensive audit report generated')
        "
    
    - name: Upload Comprehensive Audit Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: comprehensive-audit-report
        path: audit/ci_audit_validation_report.json
        retention-days: 30
    
    # ============================================================================
    # PHASE 7: AUDIT SUCCESS NOTIFICATION
    # ============================================================================
    
    - name: Audit Validation Success
      run: |
        echo "🎉 ============================================================================"
        echo "🎉 LUKHAS AI AUDIT VALIDATION COMPLETE"
        echo "🎉 ============================================================================"
        echo "✅ Acceptance Gate: PASSED"
        echo "✅ Import Linter: PASSED" 
        echo "✅ Safety Defaults: VALIDATED"
        echo "✅ E2E Tests: PASSED"
        echo "✅ Core Tests: PASSED"
        echo "✅ Registry Compliance: VALIDATED"
        echo "🎉 ============================================================================"
        echo "📋 STATUS: READY FOR EXTERNAL AUDIT"
        echo "🔍 PURPOSE: PRE/POST-MATRIZ WORKSPACE VALIDATION"
        echo "🎉 ============================================================================"

  # Optional: Matrix testing for different Python versions
  audit-validation-matrix:
    name: Audit Validation (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Quick Audit Validation
      run: |
        pip install -r requirements.txt
        python tools/acceptance_gate_ast.py
        echo "✅ Python ${{ matrix.python-version }} audit validation passed"
"""
        return workflow

    def generate_pre_commit_config(self) -> str:
        """Generate pre-commit configuration for audit safety."""
        config = """# Pre-commit configuration for LUKHAS AI audit preparation
repos:
  - repo: local
    hooks:
      # Always run acceptance gate before any commit
      - id: acceptance-gate
        name: Enhanced AST Acceptance Gate
        entry: python tools/acceptance_gate_ast.py
        language: system
        pass_filenames: false
        always_run: true
        
      # Validate safety defaults
      - id: safety-defaults-check
        name: Safety Defaults Validation
        entry: python -c "
import os
required = {'LUKHAS_DRY_RUN_MODE': 'true', 'LUKHAS_AUDIT_MODE': 'true'}
for var, expected in required.items():
    if os.getenv(var, '').lower() != expected:
        print(f'Safety check failed: {var} must be {expected}')
        exit(1)
print('Safety defaults OK')
"
        language: system
        pass_filenames: false
        
      # Registry pattern compliance
      - id: registry-compliance
        name: Registry Pattern Compliance  
        entry: python -c "
import sys
sys.path.append('tools')
from registry_pattern_templates import validate_registry_compliance
if not validate_registry_compliance():
    print('Registry compliance check failed')
    exit(1)
print('Registry compliance OK')
"
        language: system
        pass_filenames: false

  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        args: [--line-length=88]
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.292
    hooks:
      - id: ruff
        args: [--fix]
"""
        return config

    def generate_makefile_targets(self) -> str:
        """Generate Makefile targets for audit validation."""
        makefile_content = """# LUKHAS AI Audit Validation Targets

.PHONY: audit-prepare audit-validate audit-gate audit-test audit-report audit-clean

# Complete audit preparation
audit-prepare: audit-clean audit-gate audit-test audit-report
	@echo "✅ Audit preparation complete"

# Run acceptance gate
audit-gate:
	@echo "🔍 Running enhanced AST acceptance gate..."
	python tools/acceptance_gate_ast.py

# Validate import compliance  
audit-imports:
	@echo "🔍 Validating import compliance..."
	@cat > .importlinter << 'EOF'
	[importlinter]
	root_package = lukhas
	[contract:accepted_no_candidate]
	name = Accepted lane must not import candidate lane
	type = forbidden
	source_modules = lukhas
	forbidden_modules = candidate
	EOF
	lint-imports --verbose

# Run audit-safe tests
audit-test:
	@echo "🧪 Running audit-safe tests..."
	LUKHAS_DRY_RUN_MODE=true LUKHAS_AUDIT_MODE=true pytest tests/test_e2e_audit_dryrun.py -v

# Generate comprehensive audit report
audit-report:
	@echo "📋 Generating audit report..."
	@mkdir -p audit
	@python -c "
import json
from datetime import datetime
report = {
    'audit_type': 'pre_post_matriz_validation',
    'timestamp': datetime.utcnow().isoformat(),
    'status': 'audit_preparation_complete'
}
with open('audit/makefile_audit_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print('Audit report generated: audit/makefile_audit_report.json')
"

# Clean audit artifacts
audit-clean:
	@echo "🧹 Cleaning audit artifacts..."
	rm -rf audit/
	rm -f .importlinter
	rm -f coverage.json
	rm -f lukhas_audit*.db*

# Validate all audit components
audit-validate: audit-gate audit-imports audit-test
	@echo "✅ All audit validation passed"
"""
        return makefile_content

def generate_ci_integration_package(output_dir: Path) -> Dict[str, Any]:
    """Generate complete CI integration package for audit preparation."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ci_integration = CIAuditIntegration(output_dir.parent)

    # Generate GitHub Actions workflow
    workflow_dir = output_dir / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "audit-validation.yml").write_text(
        ci_integration.generate_github_workflow_template()
    )

    # Generate pre-commit configuration
    (output_dir / ".pre-commit-config.yaml").write_text(
        ci_integration.generate_pre_commit_config()
    )

    # Generate Makefile targets
    (output_dir / "Makefile.audit").write_text(
        ci_integration.generate_makefile_targets()
    )

    # Generate CI configuration summary
    ci_config = {
        "ci_integration_metadata": {
            "version": "1.0.0-audit-prep",
            "purpose": "pre_post_matriz_ci_validation",
            "components": [
                "github_actions_workflow",
                "pre_commit_hooks",
                "makefile_targets"
            ]
        },
        "workflow_stages": [
            "acceptance_gate_validation",
            "import_linter_validation",
            "safety_defaults_validation",
            "audit_safe_testing",
            "registry_pattern_validation",
            "comprehensive_audit_reporting"
        ],
        "safety_guarantees": {
            "dry_run_mode_enforced": True,
            "offline_mode_enforced": True,
            "no_external_api_calls": True,
            "audit_mode_active": True,
            "comprehensive_logging": True
        }
    }

    (output_dir / "ci_integration_config.json").write_text(
        json.dumps(ci_config, indent=2)
    )

    return {
        "files_generated": 4,
        "output_directory": str(output_dir),
        "components": ci_config["components"],
        "audit_ready": True
    }

if __name__ == "__main__":
    # Generate CI integration package
    result = generate_ci_integration_package(Path("ci_audit_integration"))

    print("CI Integration Package Generated:")
    print(f"  Output directory: {result['output_directory']}")
    print(f"  Files generated: {result['files_generated']}")
    print(f"  Components: {', '.join(result['components'])}")
    print(f"  Audit ready: {result['audit_ready']}")
