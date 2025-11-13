# Pylance-Ruff Alignment Configuration Summary

## ✅ Configuration Applied

### **VS Code Settings Changes**
- **Ruff**: Removed aggressive `--select=ALL` override, now uses `pyproject.toml` config
- **Pylance**: Changed from `strict` to `basic` mode with focused include/exclude paths
- **Scope**: Changed from `openFilesOnly` to `workspace` for comprehensive coverage
- **Indexing**: Enabled for better performance and accuracy

### **New Files Created**
- **`pyrightconfig.json`**: Workspace-specific Pylance configuration aligned with MyPy

## 🎯 Path-Based Error Filtering

### **Strict Checking** (Pylance + MyPy focused)
- `lukhas/` - Production integration layer
- `MATRIZ/` - Cognitive DNA engine

### **Basic Checking** (Pylance warnings only)
- `candidate/` - Development workspace 
- `archive/`, `quarantine/` - Historical code
- `tests/`, `tools/` - Utility code

### **Excluded Entirely** (No checking)
- `labs/`, `examples/`, `docs/` - Documentation/examples
- `products/` - Deployment code (excluded per pyproject.toml)
- Build/cache directories

## 📊 Expected Error Count Alignment

### **Before Alignment**
- **Pylance**: ~1,000 errors (checking everything in strict mode)
- **Ruff**: Unknown (was using different rule set)

### **After Alignment** 
- **Ruff**: 4,263 errors (per `ruff check --statistics`)
- **Pylance**: Should be ~200-500 errors (focused on lukhas/ + MATRIZ/ only)

## 🔧 Diagnostic Severity Mapping

| Error Type | Ruff | Pylance | Rationale |
|------------|------|---------|-----------|
| Import errors | Error | Warning | Allow development flexibility |
| Type stubs missing | N/A | Information | External libraries |
| Unknown types | N/A | Information | Gradual typing approach |
| General type issues | N/A | Information | Match MyPy exclude behavior |

## 🚀 Live Error Monitoring

You should now see:

1. **Ruff errors**: 4,263 total across all checked files
2. **Pylance errors**: Much fewer, focused on production paths only
3. **Consistent rule enforcement** between tools
4. **No duplicate errors** from overlapping configurations

## 🎯 Getting Live Numbers

To get live error counts:

```bash
# Ruff errors (total)
ruff check --statistics

# Ruff errors (by file)
ruff check --output-format=github

# Pylance errors (via VS Code)
# Check Problems panel -> Filter by "Pylance"
```

## 🔄 Re-alignment Commands

If you need to re-sync the tools:

```bash
# Reload VS Code settings
# Command Palette -> "Developer: Reload Window"

# Force Pylance restart  
# Command Palette -> "Python: Restart Language Server"

# Validate Ruff config
ruff check --config pyproject.toml --dry-run
```

The configuration is now aligned - Pylance should show significantly fewer errors focused on your production code paths!