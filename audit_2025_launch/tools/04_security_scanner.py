#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_REPORTS_DIR = ROOT_DIR / "audit_2025_launch" / "reports"
EXCLUDE = ["__pycache__", ".venv", ".git", "node_modules"]

def should_exclude(p): return any(x in str(p) for x in EXCLUDE)

PATTERNS = {
    "email": (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', "medium"),
    "api_key": (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "critical"),
    "password": (r'(?i)(password|passwd)\s*[:=]\s*["\'](?!\{)([^"\']{8,})["\']', "critical"),
    "token": (r'(?i)(token|auth_token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "critical"),
}

print("=" * 80)
print("LUKHAS PRE-LAUNCH AUDIT - PHASE 4: SECURITY & SENSITIVITY SCAN")
print("=" * 80)

findings = []
for py_file in list(ROOT_DIR.rglob("*.py"))[:500]:  # Limit for speed
    if should_exclude(py_file): continue
    try:
        with open(py_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for name, (pattern, severity) in PATTERNS.items():
                for match in re.finditer(pattern, content):
                    findings.append({"file": str(py_file.relative_to(ROOT_DIR)), "type": name, "severity": severity, "line": content[:match.start()].count('\n')+1})
    except (OSError, UnicodeDecodeError): pass

by_severity = {"critical": len([f for f in findings if f["severity"]=="critical"]), "high": 0, "medium": len([f for f in findings if f["severity"]=="medium"]), "low": 0}

report = {"timestamp": datetime.now().isoformat(), "summary": by_severity, "findings_by_severity": {"critical": [f for f in findings if f["severity"]=="critical"][:20], "medium": [f for f in findings if f["severity"]=="medium"][:20]}}

with open(AUDIT_REPORTS_DIR / "security_findings.json", "w") as f: json.dump(report, f, indent=2)
print(f"✓ Security scan: {by_severity['critical']} critical, {by_severity['medium']} medium findings")
print("=" * 80)
