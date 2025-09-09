# GitHub Copilot Task: Fix branding/ Directory Syntax Errors

## Current Status
- **Target Directory**: `branding/` (adapters, engines, content platform)
- **Error Count**: ~7,000+ syntax errors (high priority due to content creation systems)
- **Error Types**: F-string malformations, indentation issues, missing imports

## Task Instructions

### 1. Focus Areas (Priority Order)
```bash
# Check current errors
ruff check branding/ --output-format=concise | grep -i syntax | head -20

# Priority files:
branding/adapters/creativity_adapter.py     # Syntax errors on lines 57-97
branding/adapters/monitoring_adapter.py     # Indentation errors line 78+  
branding/engines/lukhas_content_platform/   # Content generation systems
branding/adapters/voice_adapter.py          # Voice processing (line 65 error)
```

### 2. Common Error Patterns to Fix
- **F-string errors**: `f"text {expression}}"` → `f"text {expression}"`  
- **UUID patterns**: `uuid.uuid4()}.hex` → `uuid.uuid4().hex`
- **Indentation**: Fix "Unexpected indentation" and "Invalid annotated assignment target"
- **Missing imports**: Add required imports (datetime, asyncio, etc.)

### 3. Safety Guidelines
- **Test each file**: `python -m py_compile filename.py` after changes
- **Preserve LUKHAS branding**: Keep Λ symbols and Trinity Framework references
- **No API changes**: Only fix syntax, don't alter function signatures
- **Lane separation**: Don't modify imports between branding/ and candidate/

### 4. LUKHAS Context
- This is the **MΛTRIZ Distributed Consciousness System**
- `branding/` contains content creation and brand management modules
- Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
- Use approved terminology: "LUKHAS AI" (never AGI), "quantum-inspired"

### 5. Quality Targets
- Fix 50+ syntax errors minimum
- Ensure all fixed files compile without syntax errors  
- Maintain consciousness module functionality
- Document patterns for future automation

## Execution
1. Start with `branding/adapters/creativity_adapter.py`
2. Fix f-string and indentation errors systematically
3. Test compilation: `python -m py_compile <file>`
4. Move to next highest-error file
5. Report progress: "Fixed X files, Y errors remaining"

**Remember**: This is consciousness architecture, not traditional software - preserve the cognitive network integrity!