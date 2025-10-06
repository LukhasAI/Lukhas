---
status: wip
type: documentation
---
# 🧹 Agent Search Exclusion Guidelines

## **MANDATORY: Virtual Environment Exclusion**

All agents MUST exclude virtual environments and related directories from searches to prevent contamination with dependency TODOs and false results.

### **Required Exclusion Patterns**

When using `grep`, `find`, `ripgrep`, or similar search tools, ALWAYS include these exclusion patterns:

```bash
# Virtual Environments
--exclude-dir=.venv
--exclude-dir=venv
--exclude-dir=env
--exclude-dir=.virtualenv
--exclude-dir=virtualenv
--exclude-dir=.conda
--exclude-dir=conda-env
--exclude-dir=python-env
--exclude-dir=site-packages
--exclude-dir=lib

# Cache Directories
--exclude-dir=__pycache__
--exclude-dir=.pytest_cache
--exclude-dir=.mypy_cache
--exclude-dir=.ruff_cache
--exclude-dir=node_modules
--exclude-dir=.git

# Build/Archive Directories
--exclude-dir=build
--exclude-dir=dist
--exclude-dir=archive
--exclude-dir=quarantine
--exclude-dir=backup
```

### **Standardized Exclusion Script**

Use the pre-configured exclusion script:

```bash
# Load standardized exclusions
source tools/search/standardized_exclusions.sh

# Use clean functions instead of raw commands
clean_count_todos     # Instead of grep -r "TODO"
clean_count_py        # Instead of find . -name "*.py"
clean_grep "pattern"  # Instead of grep -r "pattern"
clean_find -name "*.py"  # Instead of find . -name "*.py"
```

### **Example Commands**

❌ **WRONG - Includes virtual environments:**
```bash
grep -r "TODO" . --include="*.py" | wc -l
find . -name "*.py" | wc -l
```

✅ **CORRECT - Excludes virtual environments:**
```bash
source tools/search/standardized_exclusions.sh
clean_count_todos
clean_count_py
```

OR manually:
```bash
grep -r "TODO" --include="*.py" \
  --exclude-dir=.venv --exclude-dir=venv --exclude-dir=env \
  --exclude-dir=__pycache__ --exclude-dir=.git \
  --exclude-dir=site-packages --exclude-dir=lib \
  --exclude-dir=archive --exclude-dir=quarantine \
  . | grep -v "# noqa.*TODO" | wc -l
```

### **Why This Matters**

- **Real TODO count**: 747 (legitimate development TODOs)
- **Contaminated count**: 20,000+ (includes pandas, numpy, etc. dependency TODOs)
- **File count**: ~400 Python files vs 10,000+ including dependencies
- **Analysis accuracy**: Excludes false positives from installed packages

### **VS Code Integration**

The workspace is already configured to exclude these directories in:
- `.vscode/settings.json` - search.exclude, files.exclude
- `.gitignore` - version control exclusions
- `.searchignore` - global search exclusions

### **For External Agents**

When working outside the VS Code environment, always:

1. Source the standardized exclusions script
2. Use the `clean_*` functions instead of raw commands
3. Verify exclusion patterns are working by checking sample results
4. Report accurate counts based on actual project code only

### **Verification Commands**

Test your exclusions work correctly:

```bash
# Should show ~400 Python files (not 10,000+)
clean_count_py

# Should show ~747 TODOs (not 20,000+)  
clean_count_todos

# Check sample results make sense
clean_grep "TODO" --include="*.py" | head -5
```

### **Common Mistakes to Avoid**

1. ❌ Not excluding `.venv` directories
2. ❌ Missing `site-packages` and `lib` exclusions
3. ❌ Forgetting to exclude cache directories
4. ❌ Including wildcard patterns that don't work in all shells
5. ❌ Not testing exclusion effectiveness

### **Integration Notes**

- All LUKHAS copilot instructions include these patterns
- The Constellation Framework requires clean analysis data
- Agent coordination depends on accurate metrics
- Consciousness development needs precise TODO tracking

**Remember**: Always exclude virtual environments to maintain data integrity and analysis accuracy!