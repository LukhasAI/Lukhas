# LUKHAS Security Framework
## T4/0.01% Excellence Security Standards

This directory contains the comprehensive security validation framework for LUKHAS AI, implementing T4/0.01% excellence standards with zero-tolerance for critical security vulnerabilities.

## 🛡️ Framework Overview

The LUKHAS Security Framework provides:

- **SBOM Generation**: Comprehensive Software Bill of Materials with dependency vulnerability mapping
- **Static Security Analysis**: Multi-tool security scanning with custom LUKHAS-specific rules
- **Abuse Testing**: Comprehensive API attack simulation and penetration testing
- **Policy Enforcement**: Automated security policy compliance validation
- **CI Integration**: Seamless GitHub Actions integration with deployment gates

## 📊 Security Components

### 1. SBOM Generation (`scripts/security_sbom_generator.py`)

Generates CycloneDX format Software Bill of Materials with:

- Complete dependency graph analysis (direct and transitive)
- CVE vulnerability mappings with severity scoring
- License compliance validation against approved whitelist
- Security compliance status reporting
- Deployment readiness assessment

**Usage:**
```bash
python3 scripts/security_sbom_generator.py --output-dir artifacts
```

**Output:**
- `artifacts/lukhas-sbom-{timestamp}.json` - Complete SBOM in CycloneDX format
- Vulnerability and license compliance validation
- Deployment approval/blocking based on security findings

### 2. Security Scanner (`scripts/security_scanner.py`)

Comprehensive multi-tool security analysis including:

- **Semgrep**: Static analysis with custom LUKHAS security rules
- **Bandit**: Python security linting with T4/0.01% policies
- **Safety**: Dependency vulnerability scanning
- **Custom Secrets Scanner**: Hardcoded credentials and API key detection

**LUKHAS-Specific Security Rules:**
- Guardian system bypass detection
- Consciousness processing validation
- Memory injection vulnerability scanning
- Identity/OIDC security configuration validation
- JWT token manipulation detection

**Usage:**
```bash
python3 scripts/security_scanner.py --project-root . --output-dir artifacts
```

**Output:**
- `artifacts/security-scan-{timestamp}.json` - Comprehensive security findings
- Policy compliance validation
- Deployment readiness determination

### 3. Abuse Testing Framework (`scripts/abuse_tester.py`)

Advanced API security testing with attack simulation:

- **SQL Injection**: Parameter and JSON body injection testing
- **Cross-Site Scripting (XSS)**: Reflected XSS vulnerability detection
- **Authentication Bypass**: Login credential manipulation attacks
- **JWT Token Security**: Token manipulation and signature validation testing
- **Rate Limiting**: DDoS and abuse protection effectiveness testing
- **Memory Exhaustion**: DoS resistance and resource limit validation

**Usage:**
```bash
python3 scripts/abuse_tester.py --base-url http://localhost:8000 --output-dir artifacts
```

**Output:**
- `artifacts/abuse-test-{timestamp}.json` - Complete attack simulation results
- Security posture assessment
- Deployment safety validation

### 4. Security Policy (`security/security_policy.yml`)

Comprehensive security policy configuration:

- **License Whitelist**: Approved open source licenses (MIT, Apache-2.0, BSD, etc.)
- **Vulnerability Thresholds**: T4/0.01% tolerance levels (0 critical, 0 high)
- **Secret Detection Patterns**: Comprehensive credential pattern matching
- **Deployment Gates**: Automated security gate enforcement
- **Compliance Requirements**: SOC 2, ISO 27001, GDPR, CCPA alignment

## 🚀 CI/CD Integration

### GitHub Actions Workflow

The security framework is integrated into `t4-validation.yml` with four main jobs:

#### 1. `security-sbom-generation`
- Generates comprehensive SBOM
- Validates license compliance
- Checks for critical vulnerabilities
- Blocks deployment if compliance issues found

#### 2. `security-static-analysis`
- Runs Semgrep, Bandit, and Safety scanners
- Applies custom LUKHAS security rules
- Validates findings against security policy
- Detects hardcoded secrets and credentials

#### 3. `security-abuse-testing`
- Launches comprehensive attack simulation
- Tests SQL injection, XSS, auth bypass vulnerabilities
- Validates rate limiting and DoS protection
- Assesses overall security posture

#### 4. `security-validation-summary`
- Consolidates all security findings
- Makes deployment approval/blocking decision
- Generates comprehensive security report
- Posts PR comments with security status

### Deployment Gates

The framework enforces strict deployment gates:

- ❌ **BLOCKED** if any critical vulnerabilities found
- ❌ **BLOCKED** if any high vulnerabilities found
- ❌ **BLOCKED** if hardcoded secrets detected
- ❌ **BLOCKED** if unlicensed dependencies found
- ❌ **BLOCKED** if abuse tests reveal vulnerabilities
- ✅ **APPROVED** only if all security validations pass

## 📈 T4/0.01% Excellence Standards

### Security Quality Metrics

- **Critical Vulnerabilities**: 0 allowed (hard block)
- **High Vulnerabilities**: 0 allowed (hard block)
- **Medium Vulnerabilities**: Max 3 allowed
- **Low Vulnerabilities**: Max 10 allowed
- **Hardcoded Secrets**: 0 allowed (hard block)
- **Unlicensed Dependencies**: 0 allowed (hard block)

### Performance Requirements

- **SBOM Generation**: < 5 minutes
- **Security Scanning**: < 10 minutes
- **Abuse Testing**: < 15 minutes
- **Total Security Validation**: < 30 minutes

### Compliance Frameworks

- **SOC 2 Type II**: Continuous security monitoring
- **ISO 27001**: Information security management
- **GDPR**: Data protection and privacy compliance
- **CCPA**: California consumer privacy compliance

## 🔒 LUKHAS-Specific Security

### Guardian System Protection
- Detects attempts to bypass Guardian validation
- Ensures all consciousness processing is properly validated
- Validates fail-closed security behavior

### Memory System Security
- Prevents injection attacks against memory queries
- Validates input sanitization and access controls
- Ensures secure memory lifecycle operations

### Identity & OIDC Security
- Validates JWT token security configuration
- Ensures proper OIDC compliance implementation
- Detects weak authentication configurations

### API Security Hardening
- Comprehensive input validation testing
- Rate limiting effectiveness validation
- CORS and security header verification

## 📊 Artifact Structure

All security validation generates structured JSON artifacts:

```json
{
  "scan_type": "sbom|security|abuse",
  "timestamp": "2024-01-01T00:00:00Z",
  "git_sha": "abc123",
  "security_findings": {
    "critical": 0,
    "high": 0,
    "medium": 2,
    "low": 5,
    "secrets": 0
  },
  "compliance_status": {
    "sbom_generated": true,
    "license_compliant": true,
    "vulnerabilities_resolved": true,
    "abuse_tests_passed": true
  },
  "deployment_readiness": "APPROVED|BLOCKED"
}
```

## 🛠️ Local Development

### Prerequisites

```bash
pip install semgrep bandit safety cyclonedx-python-lib aiohttp pyyaml
```

### Running Security Scans Locally

```bash
# Generate SBOM
python3 scripts/security_sbom_generator.py

# Run security scanning
python3 scripts/security_scanner.py

# Run abuse testing (requires running server)
python3 scripts/abuse_tester.py --base-url http://localhost:8000
```

### Testing Security Framework

```bash
# Test all security tools
./scripts/test_security_framework.sh

# Validate security policy
python3 -c "import yaml; yaml.safe_load(open('security/security_policy.yml'))"
```

## 🚨 Incident Response

### Critical Vulnerability Detection

1. **Immediate Action**: Deployment automatically blocked
2. **Notification**: Security team alerted within 2 hours
3. **Assessment**: Vulnerability impact analysis
4. **Remediation**: Fix implementation and testing
5. **Validation**: Re-run security validation pipeline
6. **Deployment**: Only after full security clearance

### Security Policy Updates

1. Update `security/security_policy.yml` with new requirements
2. Test policy changes against current codebase
3. Submit PR with security team review
4. Deploy policy changes to CI/CD pipeline

## 📚 Documentation

- **Security Policy**: `security/security_policy.yml`
- **SBOM Generator**: `scripts/security_sbom_generator.py`
- **Security Scanner**: `scripts/security_scanner.py`
- **Abuse Tester**: `scripts/abuse_tester.py`
- **CI Integration**: `.github/workflows/t4-validation.yml`

## 🎯 Future Enhancements

- Integration with external CVE databases (NIST NVD, GitHub Advisory)
- Advanced ML-based anomaly detection
- Real-time security monitoring and alerting
- Integration with SIEM systems
- Automated vulnerability remediation suggestions

---

**Security Contact**: security-team@lukhas.ai
**Documentation**: https://lukhas.ai/docs/security
**Policy Version**: 1.0.0
**Last Updated**: 2024-01-01