---
status: wip
type: documentation
---
# 🔧 SURGICAL Corruption Fix Strategy

**Mission**: Preserve logic, state & organization while eliminating corruption

## 📊 Corruption Analysis Results

- **Total Files**: 4,898 Python files
- **Clean Files**: 4,419 (90.2%) - ready for automated fixes
- **Corrupted Files**: 479 (9.8%) - need surgical repair
- **Critical Issues**: Only 1 file with null bytes

## 🎯 Three-Phase Surgical Approach

### Phase 0: Critical Triage (Immediate)
```bash
# 1. Quarantine the 1 null-byte file
mkdir -p quarantine/critical
mv products/communication/abas/archived_specs/override_logic.py quarantine/critical/

# 2. Create surgical repair workspace
git checkout pre-matriz-freeze-20250911T044009Z
git switch -c surgical-corruption-fix-phase0
```

### Phase 1: Surgical Indentation Repair (High Priority)
**Target**: 3 files with severe indentation corruption
```
- candidate/core/safety/predictive_harm_prevention.py
- candidate/memory/systems/dream_memory_manager.py  
- tools/scripts/enhance_all_modules.py
```

**Surgical Technique**: Remove excessive whitespace padding while preserving logic

### Phase 2: F-String Pattern Repair (Medium Priority)
**Target**: 5 files with malformed f-strings
```
- candidate/bridge/adapters/api_documentation_generator.py
- candidate/bridge/api/direct_ai_router.py
- candidate/api/audit.py
- tools/module_dependency_visualizer.py
- products/communication/nias/vendor_portal_backup.py
```

**Surgical Technique**: Fix bracket matching and escape sequences

### Phase 3: Standard Syntax Cleanup (Automated)
**Target**: 470 files with standard syntax errors
- Most are f-string bracket mismatches
- Can use automated tools AFTER corruption is surgically repaired

## 🛠️ Surgical Tools

### Tool 1: Indentation Repair
```python
def surgical_indent_repair(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    repaired_lines = []
    for line in lines:
        # Remove excessive whitespace corruption while preserving structure
        if '                                                   ' in line:
            # This is the corruption signature - repair it
            cleaned = line.replace('                                                   ', '    ')
            repaired_lines.append(cleaned)
        else:
            repaired_lines.append(line)
    
    return ''.join(repaired_lines)
```

### Tool 2: F-String Repair
```python
def surgical_fstring_repair(content):
    # Fix common f-string corruption patterns
    # Preserve logic while fixing syntax
    patterns = {
        'f"{': 'f"{',  # Basic validation
        '}}"': '}"',   # Remove double closing
        # Add more patterns as discovered
    }
    return content
```

## 🎯 Success Metrics

### Phase 0 Success
- [x] 1 critical file quarantined
- [ ] Clean baseline established
- [ ] No data loss

### Phase 1 Success
- [ ] 3 indentation files surgically repaired
- [ ] Files parse without syntax errors
- [ ] Logic and organization preserved

### Phase 2 Success  
- [ ] 5 f-string files surgically repaired
- [ ] All f-strings properly formed
- [ ] Functionality maintained

### Phase 3 Success
- [ ] Corrupted file count: 479 → <50
- [ ] Ready for automated ruff fixes
- [ ] All tagged commit logic preserved

## 🚀 Execution Plan

**Immediate Next Steps**:
1. Create surgical repair branch from clean baseline
2. Quarantine the 1 critical file
3. Apply surgical fixes to the 8 high/medium priority files
4. Validate repairs preserve logic
5. Execute automated fixes on clean foundation

**Timeline**: 
- Phase 0: 15 minutes
- Phase 1: 30 minutes (3 files)
- Phase 2: 30 minutes (5 files)  
- Phase 3: Automated (10 minutes)

**Total Estimated Time**: ~1.5 hours to clean foundation

---
*This strategy preserves all your tagged commit logic while surgically removing corruption*