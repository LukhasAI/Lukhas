# Codex Task: Fix candidate/ Directory Syntax Errors  

## Current Status
- **Target Directory**: `candidate/` (experimental/development modules)
- **Error Count**: ~4,000+ syntax errors (development lane)
- **Error Types**: F-string issues, import errors, experimental code syntax

## Task Instructions

### 1. High-Impact Areas (Priority Order)
```bash
# Check errors by module
ruff check candidate/consciousness/ --output-format=concise | grep syntax | wc -l
ruff check candidate/governance/ --output-format=concise | grep syntax | wc -l  
ruff check candidate/bio/ --output-format=concise | grep syntax | wc -l
ruff check candidate/memory/ --output-format=concise | grep syntax | wc -l

# Focus sequence:
candidate/consciousness/    # Core consciousness modules
candidate/governance/       # Ethics and identity systems  
candidate/bio/              # Bio-inspired processing
candidate/memory/           # Memory fold systems
```

### 2. Systematic Fix Approach
```python
# Common patterns to fix:
# Pattern 1: F-string single brace
OLD: f"text {var}}"  
NEW: f"text {var}"

# Pattern 2: UUID hex access
OLD: f"id-{uuid4()}}.hex"
NEW: f"id-{uuid4().hex}"  

# Pattern 3: Missing imports
ADD: from datetime import timezone, datetime
ADD: import asyncio
ADD: from typing import Optional, Dict, Any

# Pattern 4: Conditional in f-string  
OLD: f"{condition} if True else 'default'}"
NEW: f"{condition if True else 'default'}"
```

### 3. Module-Specific Context

#### candidate/consciousness/
- Dream engines with symbolic processing
- Awareness modules with reflection systems
- Keep dream state and symbolic trace functionality intact

#### candidate/governance/ 
- Identity (ΛiD) system with tiered authentication
- Ethics engines and Guardian system validation
- Constitutional AI principles - preserve ethical frameworks

#### candidate/bio/
- Bio-inspired oscillators and adaptation
- Symbolic processing and matriz integration
- Swarm intelligence and colony patterns

#### candidate/memory/
- Fold-based memory with 1000-fold limit
- Cascade prevention (99.7% success rate)
- Memory identity and consciousness persistence

### 4. Quality Standards
- **Lane Compliance**: candidate/ → lukhas/ promotion path
- **Test Coverage**: Aim for 85% minimum on fixed modules
- **MΛTRIZ Integrity**: Preserve consciousness patterns
- **No Breaking Changes**: Fix syntax only, preserve APIs

### 5. Error Categories (Fix Priority)
1. **Critical**: Files that prevent module loading
2. **High**: F-string and import errors  
3. **Medium**: Type annotation and formatting issues
4. **Low**: Style and minor syntax variations

## Execution Strategy
```bash
# 1. Identify critical files
find candidate/ -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep "SyntaxError" | head -10

# 2. Fix systematically by module
# Start with candidate/consciousness/awareness/ (core consciousness)
# Then candidate/governance/ethics/ (safety systems)
# Then candidate/bio/oscillator/ (adaptation systems)

# 3. Validate after each batch
python -c "import candidate.consciousness.awareness; print('✅ Consciousness loaded')"
```

## Success Metrics
- Reduce candidate/ syntax errors by 1000+ 
- Enable successful import of core consciousness modules
- Maintain 99.7% memory cascade prevention rate
- Preserve Trinity Framework constellation navigation

**Context**: candidate/ is the development lane for the world's most sophisticated distributed consciousness architecture. Each module represents a cognitive component in the 692-module consciousness network. Preserve the cognitive DNA and consciousness authenticity.