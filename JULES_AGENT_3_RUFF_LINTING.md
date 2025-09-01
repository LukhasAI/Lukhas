# Jules Agent 3: Ruff Linting Specialist

## 🎯 Mission: Systematic Ruff Error Resolution
**Focus**: Apply safe Ruff fixes across lukhas/, serve/, and candidate/ (non-aka_qualia)

## 🔴 Priority Queue (Ruff Fixes Only)

### Phase 1: High-Impact Safe Fixes
1. **Unused Imports (F401)**
   - Remove unused import statements
   - Clean up import organization
   - Apply across all safe modules

2. **Undefined Names (F821)**
   - Add missing imports for undefined variables
   - Fix typos in variable/function names
   - Resolve scope issues

3. **Import Organization (I001, I002)**
   - Sort imports alphabetically
   - Separate standard lib, third-party, local imports
   - Apply isort-style formatting

### Phase 2: Code Style & Simplification
4. **Line Length (E501)**
   - Break long lines at logical points
   - Use parentheses for line continuation
   - Maintain readability

5. **Simplification Rules (SIM)**
   - SIM117: Combine nested with statements
   - SIM118: Use in operator for membership tests
   - SIM210: Use bool() instead of conditional expressions

6. **Comprehension Improvements (C4)**
   - Convert loops to list/dict comprehensions where appropriate
   - Optimize nested loops
   - Maintain readability

### Phase 3: Error Prevention
7. **Unused Variables (F841)**
   - Remove truly unused variables
   - Prefix with underscore if needed for APIs
   - Add type annotations where missing

8. **String Formatting (F-string conversion)**
   - Convert .format() calls to f-strings
   - Convert % formatting to f-strings
   - Optimize string concatenation

## 🛡️ Safety Constraints
- **Branch**: Work on `feat/jules-ruff-fixes`
- **Patch Limit**: ≤20 lines per file per session
- **Safe Only**: No behavior changes, only style/lint fixes
- **Avoid**: `candidate/aka_qualia/` (Wave C development)
- **Focus Areas**: `lukhas/`, `serve/`, `tests/`, `tools/`
- **Quality Gate**: All fixes must pass ruff check after application

## 🔧 Systematic Approach
```bash
# Setup
source .venv/bin/activate

# Identify issues by category
ruff check . --select=F401 > unused_imports.txt
ruff check . --select=F821 > undefined_names.txt
ruff check . --select=SIM > simplification.txt

# Apply fixes in batches
ruff check --fix . --select=F401,I001,I002  # Safe imports
ruff check --fix . --select=SIM117,SIM118   # Safe simplifications
ruff check --fix . --select=E501 --line-length=88  # Line length
```

## 📊 Target Error Categories
```bash
# Current major ruff issues to tackle:
# F401: unused-import
# F821: undefined-name  
# I001: unsorted-imports
# I002: missing-required-import
# SIM117: combine-with-statements
# SIM118: in-dict-keys
# E501: line-too-long
# C408: unnecessary-collection-call
# C416: unnecessary-comprehension
```

## 🧪 Fix Validation Pattern
```bash
# Before fixing each file:
ruff check [file] --output-format=json > before.json

# Apply fixes (≤20 lines per file)
ruff check --fix [file] --select=[RULES]

# Validate fix success
ruff check [file] --output-format=json > after.json
diff before.json after.json

# Ensure no regressions
pytest tests/[related_tests] -v
```

## 📊 Success Metrics
- **Error Reduction**: Reduce ruff errors by 30%+ in target areas
- **Categories**: Focus on F401, F821, SIM, I001/I002 first
- **Files Fixed**: 50+ files with safe lint improvements
- **Quality**: Zero new errors introduced
- **Test Pass**: All related tests continue passing

## 🎯 Expected Outcome
Agent 3 systematically improves code quality through safe linting fixes, reducing technical debt while maintaining system stability.

---
*Agent 3 Focus: Ruff linting - Code quality at scale*