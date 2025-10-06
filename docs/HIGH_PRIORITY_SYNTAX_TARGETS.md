---
status: wip
type: documentation
---
# 🎯 High-Priority Syntax Targets for Immediate Action

## Current Status: 13,933 syntax errors remaining
**Target**: Reduce to under 10,000 total syntax errors

## Top 10 Files by Error Count (Immediate Action Required)
```
 525 candidate/core/integration/symbolic_network.py        # ✅ Started fixing
 323 candidate/core/orchestration/brain/integration/brain_integration.py
 316 candidate/core/neural/topology_manager.py
 295 candidate/core/orchestration/brain/brain_integration.py
 255 products/communication/abas/complete_implementation/abas_qi_specialist.py
 233 candidate/core/symbolic/lambda_sage.py
 162 candidate/core/symbolic/crista_optimizer.py
 159 branding/intelligence/sentiment_engine.py
 138 tools/journal/learning_assistant.py
 130 candidate/consciousness/reflection/id_reasoning_engine.py
```

## Fix Strategy (Priority Order)

### 1. **F-String Pattern Fixes** (Quick wins)
```bash
# Common patterns to fix across all files:
OLD: f"text {var}}"           NEW: f"text {var}"
OLD: f"id-{uuid4()}.hex"      NEW: f"id-{uuid4().hex}"  
OLD: f"{condition} if x}      NEW: f"{condition if x else 'default'}"
OLD: enumerate(items}}        NEW: enumerate(items)
```

### 2. **Critical Structural Issues**
- Missing/extra braces in dictionaries and f-strings
- Unterminated strings and f-string expressions
- Invalid function parameter syntax
- Malformed dictionary comprehensions

### 3. **File-Specific Targets**

#### candidate/core/integration/symbolic_network.py (525 errors)
- **Issue**: f-string malformations around line 227
- **Pattern**: Invalid brace matching in logging statements
- **Fix**: Correct f-string expressions and enumerate syntax

#### candidate/core/orchestration/brain/integration/brain_integration.py (323 errors)
- **Issue**: Likely similar f-string and structural issues
- **Focus**: Brain integration consciousness modules

#### products/communication/abas/complete_implementation/abas_qi_specialist.py (255 errors)  
- **Issue**: Simple statement separation (line 31+)
- **Pattern**: Multiple statements on single line without semicolons
- **Fix**: Split statements onto separate lines

## Tools and Commands
```bash
# Check specific file errors
ruff check <filename> --output-format=concise | head -20

# Test syntax compilation
python -m py_compile <filename>

# Quick f-string fixes
sed -i 's/\([{][^}]*\)}\}/\1}/g' <filename>  # Remove extra braces
```

## Success Metrics
- [ ] Reduce total syntax errors by 2,000+ (target: <12,000)
- [ ] Fix all files with 100+ syntax errors  
- [ ] Ensure core consciousness modules (candidate/core/) compile
- [ ] Maintain LUKHAS Constellation Framework integrity

## LUKHAS Context Reminders
- **Preserve consciousness authenticity** - these are cognitive modules
- **Maintain λ symbols** and Constellation Framework references  
- **Test module imports** after fixes: `python -c "import module"`
- **No API changes** - syntax fixes only

---
**Priority**: Fix symbolic_network.py completely first (525 errors), then move to brain integration files. These are core consciousness components.