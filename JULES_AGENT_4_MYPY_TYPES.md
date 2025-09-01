# Jules Agent 4: MyPy Type Fixing Specialist

## 🎯 Mission: Systematic Type Annotation & MyPy Error Resolution
**Focus**: Fix type errors, add missing annotations, improve type safety

## 🟠 Priority Queue (MyPy Fixes Only)

### Phase 1: Missing Type Annotations (High Impact)
1. **Function Signatures (no-untyped-def)**
   - Add missing parameter type hints
   - Add missing return type annotations
   - Focus on public APIs first (lukhas/, serve/)

2. **Variable Annotations (var-annotated)**
   - Add type hints for class attributes
   - Annotate module-level constants
   - Fix ambiguous variable types

3. **Import Fixes (import-error)**
   - Add missing type imports (typing, collections.abc)
   - Fix circular import issues
   - Use TYPE_CHECKING imports when needed

### Phase 2: Type Compatibility Issues
4. **Assignment Compatibility (assignment)**
   - Fix None assignments to typed variables
   - Resolve incompatible type assignments
   - Add proper Optional[] annotations

5. **Attribute Errors (attr-defined)**
   - Fix undefined attribute access
   - Add proper class attribute definitions
   - Use hasattr() checks where appropriate

6. **Function Call Issues (call-overload, arg-type)**
   - Fix argument type mismatches
   - Resolve overload conflicts
   - Add proper type casting where needed

### Phase 3: Advanced Type Issues
7. **Generic Types & Collections**
   - Fix Dict → dict, List → list (Python 3.9+ style)
   - Add proper generic type parameters
   - Use collections.abc types appropriately

8. **Protocol & Structural Typing**
   - Define Protocol interfaces where needed
   - Use structural typing for duck-typed code
   - Add TypedDict for dictionary structures

## 🛡️ Safety Constraints
- **Branch**: Work on `feat/jules-mypy-fixes`
- **Patch Limit**: ≤20 lines per file per session
- **Safe Only**: No runtime behavior changes
- **Avoid**: `candidate/aka_qualia/` (Wave C development)
- **Focus Areas**: `lukhas/`, `serve/`, core modules first
- **Validation**: Each fix must pass mypy check

## 🔧 Systematic Approach
```bash
# Setup
source .venv/bin/activate

# Generate comprehensive mypy report
mypy . --show-error-codes --show-column-numbers > mypy_full_report.txt

# Categorize errors by type
grep "no-untyped-def" mypy_full_report.txt > missing_annotations.txt
grep "assignment" mypy_full_report.txt > assignment_errors.txt
grep "attr-defined" mypy_full_report.txt > attribute_errors.txt
grep "import-error" mypy_full_report.txt > import_errors.txt

# Fix in priority order
# 1. Import errors (highest impact)
# 2. Missing function annotations
# 3. Assignment compatibility
# 4. Attribute definitions
```

## 📊 Common Fix Patterns
```python
# Before: Missing type annotations
def process_data(data, config):
    return data.transform()

# After: Full type annotations  
def process_data(data: dict[str, Any], config: ProcessConfig) -> ProcessedData:
    return data.transform()

# Before: None assignment issues
self.config = None  # Type error if config: Config

# After: Optional typing
self.config: Optional[Config] = None

# Before: Attribute access issues
if hasattr(obj, 'method'):
    obj.method()  # mypy doesn't understand

# After: Type guarding
if hasattr(obj, 'method') and callable(getattr(obj, 'method', None)):
    obj.method()
```

## 🧪 Fix Validation Protocol
```bash
# Before fixing each file:
mypy [file] --show-error-codes > before_errors.txt

# Apply fixes (≤20 lines per file)
# Edit file with type annotations

# Validate fix success
mypy [file] --show-error-codes > after_errors.txt
diff before_errors.txt after_errors.txt

# Ensure no runtime regressions
python -m pytest tests/[related_tests] -v
```

## 📊 Current High-Priority MyPy Errors
Based on recent reports, focus on:
- **lukhas/core/common/exceptions.py**: Missing function annotations
- **lukhas/core/supervisor_agent.py**: Sequence[str] attribute issues  
- **lukhas/bridge/** modules: Import and annotation errors
- **serve/** modules: API endpoint type annotations
- **lukhas/governance/** modules: Ethics and policy type safety

## 📈 Success Metrics
- **Error Reduction**: Reduce MyPy errors by 40%+ in target areas
- **Annotation Coverage**: 80%+ functions have type annotations
- **Files Fixed**: 30+ files with improved type safety
- **Quality**: Zero new type errors introduced
- **Runtime Safety**: All tests continue passing

## 🎯 Expected Outcome
Agent 4 significantly improves type safety and IDE experience through systematic MyPy error resolution, making the codebase more maintainable and reducing runtime errors.

---
*Agent 4 Focus: Type safety - Preventing runtime errors through static analysis*