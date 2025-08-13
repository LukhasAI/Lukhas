# LUKHAS  Identity Integration Automation Tools

## Overview

This suite of automation tools helps fix identity integration issues across the LUKHAS  codebase. The tools automatically add authentication, tier protection, and user ID tracking where needed.

## 🚀 Quick Start

```bash
# Preview all changes (recommended first)
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --dry-run

# Apply all fixes
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --fix-all

# Validate current state
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --validate
```

## 🛠️ Individual Tools

### 1. Identity Automation Suite
**File:** `IDENTITY_AUTOMATION_SUITE.py`  
**Purpose:** Master coordinator for all identity tools  

```bash
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --dry-run
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --fix-all
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --validate
```

### 2. Auto Identity Fixer  
**File:** `AUTO_IDENTITY_FIXER.py`  
**Purpose:** Automatically adds authentication to API endpoints and module protection  

```bash
python3 tools/scripts/AUTO_IDENTITY_FIXER.py --dry-run
python3 tools/scripts/AUTO_IDENTITY_FIXER.py  # Live mode
```

**What it fixes:**
- ✅ Adds `AuthContext` parameters to API endpoints
- ✅ Adds identity imports to files
- ✅ Adds tier protection to module `__init__.py` files
- ✅ Injects user context into function signatures

### 3. User ID Injector
**File:** `USER_ID_INJECTOR.py`  
**Purpose:** Adds user ID tracking to data operations and logging  

```bash
python3 tools/scripts/USER_ID_INJECTOR.py --dry-run consciousness quantum
python3 tools/scripts/USER_ID_INJECTOR.py consciousness quantum dream emotion
```

**What it adds:**
- ✅ `user_id` fields to data dictionaries
- ✅ User context to log messages  
- ✅ User tracking to database operations
- ✅ User parameters to function signatures

### 4. Identity Guard
**File:** `IDENTITY_GUARD.py`  
**Purpose:** Validates files for identity compliance (pre-commit hook)  

```bash
python3 tools/scripts/IDENTITY_GUARD.py api/consciousness_chat_api.py
python3 tools/scripts/IDENTITY_GUARD.py --pre-commit  # As pre-commit hook
```

**What it validates:**
- ❌ Unprotected API endpoints
- ⚠️ Sensitive modules without tier protection
- ⚠️ Data operations without user tracking

### 5. Identity Integration Audit
**File:** `tools/analysis/IDENTITY_INTEGRATION_AUDIT.py`  
**Purpose:** Comprehensive analysis of identity integration status  

```bash
python3 tools/analysis/IDENTITY_INTEGRATION_AUDIT.py
```

**Reports:**
- 📊 Protection statistics by module
- 📁 Unprotected files and endpoints
- 🔗 User linking analysis
- 💡 Specific recommendations

## 📋 Templates

### Protected API Template
**File:** `tools/templates/protected_api_template.py`  
**Purpose:** Complete template for creating tier-protected API endpoints  

Copy this template when creating new APIs to ensure proper authentication from the start.

**Features:**
- ✅ T1-T5 tier protection examples
- ✅ Proper error handling
- ✅ User context injection
- ✅ Permission-based access control
- ✅ Request/response models with user tracking

## 🔄 Workflow

### Initial Setup (One-time)
```bash
# 1. Run full audit to understand current state
python3 tools/analysis/IDENTITY_INTEGRATION_AUDIT.py

# 2. Preview all fixes
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --dry-run

# 3. Apply fixes
python3 tools/scripts/IDENTITY_AUTOMATION_SUITE.py --fix-all

# 4. Review changes and test
git diff
pytest tests/
```

### Daily Development
```bash
# Before committing new API code
python3 tools/scripts/IDENTITY_GUARD.py path/to/new_file.py

# Auto-fix any issues found
python3 tools/scripts/AUTO_IDENTITY_FIXER.py --dry-run
```

### Pre-Commit Hook Setup
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
python3 tools/scripts/IDENTITY_GUARD.py --pre-commit
```

## 🎯 What Gets Fixed

### API Endpoints (BEFORE)
```python
@app.post("/consciousness/chat")
async def chat_endpoint(message: ChatMessage):
    # Anyone can access - SECURITY RISK
    return await process_consciousness(message)
```

### API Endpoints (AFTER)  
```python
from identity.middleware import AuthContext, require_t3_or_above

@app.post("/consciousness/chat")
async def chat_endpoint(
    message: ChatMessage,
    user: AuthContext = Depends(require_t3_or_above)  # ✅ PROTECTED
):
    # Add user tracking
    message_data = message.dict()
    message_data["user_id"] = user.user_id
    
    return await process_consciousness(message_data, user=user)
```

### Data Operations (BEFORE)
```python
def save_dream(dream_content: str):
    data = {
        "content": dream_content,
        "timestamp": datetime.now()
    }
    # No user tracking - can't tell whose dream this is
    database.save(data)
```

### Data Operations (AFTER)
```python
def save_dream(dream_content: str, user: Optional[AuthContext] = None):
    data = {
        "content": dream_content,
        "timestamp": datetime.now(),
        "user_id": getattr(user, "user_id", "anonymous")  # ✅ USER TRACKING
    }
    database.save(data, user_id=user.user_id if user else None)
```

## 🔐 Security Levels

| Tier | Access Level | Modules | API Endpoints |
|------|-------------|---------|---------------|  
| **T1** | Basic viewing | Public content | Health, status |
| **T2** | Content creation | API access | Create, upload |
| **T3** | Advanced features | Consciousness, emotion, dream | Chat, analysis |
| **T4** | Quantum processing | Quantum modules | Quantum APIs |
| **T5** | Admin/Guardian | Governance, admin | System management |

## 📊 Success Metrics

After running the automation tools, you should achieve:

- ✅ **100% API Protection** (currently 0/82 protected)
- ✅ **Module Tier Enforcement** (currently 2/5 modules protected)  
- ✅ **User ID Tracking** (currently 26/191 modules)
- ✅ **Identity Imports** (automatically added where needed)

Run the audit again to verify improvements:
```bash
python3 tools/analysis/IDENTITY_INTEGRATION_AUDIT.py
```

## 🚨 Safety Features

All tools include safety features:

- 🔄 **Automatic backups** before modifying files
- 🧪 **Dry-run mode** to preview changes  
- 🛡️ **Error handling** with detailed reporting
- 📝 **Change logging** for audit trails
- ⚡ **Rollback support** via git history

## 💡 Tips

1. **Always run dry-run first** to preview changes
2. **Test after applying fixes** - authentication changes affect functionality
3. **Review backups** if something goes wrong
4. **Use templates** for new code to start with proper protection
5. **Run validation** before committing code changes

---

**Need help?** Check the individual tool help:
```bash
python3 tools/scripts/AUTO_IDENTITY_FIXER.py --help
python3 tools/scripts/IDENTITY_GUARD.py --help
```