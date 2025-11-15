# Security Issue 3: Fix Shell Injection Vulnerabilities (HIGH)

## Priority: P1 - HIGH Security Pattern
## Estimated Effort: 20 days
## Target: Fix all 66 shell injection patterns

---

## 🎯 Objective

Fix all 66 shell injection vulnerabilities from subprocess and os.system calls. Shell injection occurs when untrusted input is passed to shell commands, allowing attackers to execute arbitrary system commands.

## 📊 Current State

- **subprocess with shell=True**: 27 occurrences
- **os.system calls**: 39 occurrences
- **Total**: 66 shell injection risks
- **Risk Level**: HIGH
- **Security Impact**: Remote command execution, system compromise

## 🔍 Background

Shell injection allows attackers to:
- Execute arbitrary system commands
- Access sensitive files
- Modify system configuration
- Launch denial of service attacks
- Pivot to other systems

## 📋 Deliverables

### 1. Remediation for subprocess.run

**Standard Fix** (shell=False):
```python
# ❌ BEFORE (HIGH RISK - Shell Injection)
import subprocess
result = subprocess.run(f"ls {user_path}", shell=True)

# ✅ AFTER (SAFE - No Shell)
import subprocess
from pathlib import Path
from typing import List

def safe_list_directory(user_path: str) -> List[str]:
    """Safely list directory without shell injection."""
    # Validate path
    path = Path(user_path).resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid directory")
    
    # Use array form (no shell=True)
    result = subprocess.run(
        ["ls", str(path)],  # Array - no shell interpretation
        capture_output=True,
        text=True,
        check=True,
        timeout=5
    )
    return result.stdout.splitlines()
```

### 2. Remediation for os.system

**Replace with subprocess**:
```python
# ❌ BEFORE (HIGH RISK)
import os
os.system(f"rm {filename}")

# ✅ AFTER (SAFE)
import subprocess
from pathlib import Path

def safe_remove_file(filename: str) -> None:
    """Safely remove file."""
    path = Path(filename)
    if not path.exists():
        raise ValueError("File does not exist")
    
    subprocess.run(
        ["rm", str(path)],
        check=True,
        timeout=5
    )
```

### 3. Input Validation
- [ ] Validate all user inputs before subprocess calls
- [ ] Use Path objects for file operations
- [ ] Whitelist allowed commands
- [ ] Add timeout for all subprocess calls

### 4. Security Testing
```python
def test_shell_injection_prevented():
    """Ensure shell injection is prevented."""
    malicious_inputs = [
        "; rm -rf /",
        "| cat /etc/passwd",
        "&& whoami",
        "$(malicious command)",
    ]
    
    for malicious in malicious_inputs:
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            safe_list_directory(malicious)
```

### 5. Documentation
- [ ] Create `docs/security/SHELL_INJECTION_FIX_REPORT.md`
- [ ] Update subprocess usage guidelines

## ✅ Acceptance Criteria

- [ ] All 66 shell injection patterns fixed
- [ ] All subprocess calls use array form (no shell=True)
- [ ] All os.system replaced with subprocess
- [ ] Input validation in place
- [ ] Security tests pass
- [ ] Complete documentation

## 🏷️ Labels: `security`, `high`, `p1`, `shell-injection`

---

**Estimated Days**: 20 days | **Phase**: Security Phase 1
