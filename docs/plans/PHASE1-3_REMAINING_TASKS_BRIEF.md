---
title: Phase 1-3 Remaining Tasks Brief
date: 2025-10-18
status: ready-for-parallel-agent
priority: medium
branch: feat/phase1-3-completion
source: EXECUTION_PLAN.md
---

# Phase 1-3 Remaining Tasks Brief

## Mission
Complete remaining documentation and artifact enhancement tasks from Phases 1-3 of the EXECUTION_PLAN.md. These are low-risk, parallel-safe tasks that improve code quality, discoverability, and developer experience.

## Context

### What's Already Done ✅
- ✅ Enhanced `docs/CONSTELLATION_TOP.md` (v2.0)
- ✅ Regenerated 780 manifests with star assignments
- ✅ Updated Constellation summary dashboard
- ✅ API manifest tiering (partial)
- ✅ Contracts registry validation
- ✅ Phase 5B directory flattening complete

### Current Repository State
```bash
Branch: main
Manifests: 780 modules with star assignments
Structure: Flattened (lukhas/ removed, all at root/labs)
Star Distribution: 856 promoted stars across 8 categories
Quality Tiers: T1-T4 assigned to all modules
```

### Reference Documents
- Main plan: `/Users/agi_dev/LOCAL-REPOS/Lukhas/EXECUTION_PLAN.md`
- Constellation stats: `docs/dashboards/CONSTELLATION_STATS.md`
- Manifest schema: `configs/schemas/module_manifest.schema.json`

## Tasks to Complete

### 📋 Phase 1: Documentation Enhancement

#### Task 1.1: Enhance `docs/lukhas_context/*.md` Files
**Priority**: Medium
**Time Estimate**: 2-3 hours
**Complexity**: Low

**Objective**: Standardize all context markdown files with YAML front matter, cross-links, and contract references.

**Files to Update** (42 context files):
```bash
# Find all context files
find docs/lukhas_context -name "*.md" -type f
```

**For each context file, add:**

1. **YAML Front Matter** (if missing):
```yaml
---
domain: [consciousness|memory|governance|etc.]
stars: [list of relevant stars]
tier: [T1|T2|T3|T4]
contracts: [list of contract IDs if applicable]
updated: 2025-10-18
status: active
---
```

2. **Contract Links Section** (if module has contracts):
```markdown
## 📜 Contracts

This module implements the following contracts:
- [CONTRACT_ID_001](../../contracts/CONTRACT_ID_001.md) - Description
- [CONTRACT_ID_002](../../contracts/CONTRACT_ID_002.md) - Description
```

3. **Cross-References Section**:
```markdown
## 🔗 Related Modules

- [Related Module](./related_module_context.md) - How they interact
- [Another Module](./another_context.md) - Dependencies
```

4. **Constellation Alignment** (if not present):
```markdown
## ⭐ Constellation Stars

This module aligns with:
- **Flow (Consciousness)**: [explanation]
- **Trail (Memory)**: [explanation]
```

**Success Criteria**:
- All 42 context files have YAML front matter
- Contract links present where applicable
- Cross-references between related modules
- No broken links

**Validation**:
```bash
# Check all context files have front matter
for f in docs/lukhas_context/*.md; do
  head -1 "$f" | grep -q "^---$" || echo "Missing front matter: $f"
done
```

---

#### Task 1.2: Add Schema Field Docstrings
**Priority**: Low
**Time Estimate**: 1-2 hours
**Complexity**: Low

**Objective**: Add descriptions to all required fields in the manifest schema to improve validator error messages.

**File**: `configs/schemas/module_manifest.schema.json`

**Current State**: Schema exists but many fields lack `"description"` properties

**Action Items**:

1. **Add descriptions to all required fields**:
```json
{
  "module": {
    "type": "object",
    "description": "Core module metadata including name, path, and quality tier",
    "properties": {
      "name": {
        "type": "string",
        "description": "Human-readable module name (e.g., 'Consciousness Engine')"
      },
      "path": {
        "type": "string",
        "description": "Relative path from repository root (e.g., 'consciousness/core')"
      },
      "tier": {
        "type": "string",
        "enum": ["T1", "T2", "T3", "T4"],
        "description": "Quality tier: T1=Critical, T2=Important, T3=Standard, T4=Experimental"
      }
    }
  }
}
```

2. **Enhance validator error messages** in `scripts/validate_module_manifests.py`:
```python
# Current: "Validation error"
# Enhanced: "Validation error in consciousness/core/module.manifest.json:
#            Field 'tier' must be one of [T1, T2, T3, T4], got 'T5'"
```

3. **Add field examples** to schema where helpful:
```json
{
  "contracts": {
    "type": "array",
    "description": "List of contract IDs this module implements",
    "examples": [["CON-001-MEMORY", "CON-002-STORAGE"]]
  }
}
```

**Success Criteria**:
- All required fields have `"description"` properties
- Validator shows helpful error messages with field context
- Schema examples added for complex fields

**Validation**:
```bash
# Check schema completeness
python3 - <<PY
import json
schema = json.load(open("configs/schemas/module_manifest.schema.json"))
missing = []
def check_descriptions(obj, path=""):
    if isinstance(obj, dict):
        if "properties" in obj:
            for key, val in obj["properties"].items():
                if "description" not in val:
                    missing.append(f"{path}.{key}")
                check_descriptions(val, f"{path}.{key}")
check_descriptions(schema)
print(f"Fields missing descriptions: {len(missing)}")
for m in missing[:10]:
    print(f"  - {m}")
PY
```

---

#### Task 1.3: Artifact Audit - 99% Coverage Push
**Priority**: High
**Time Estimate**: 2-3 hours
**Complexity**: Medium

**Objective**: Scan for orphan modules (no manifest) and generate missing manifests to achieve 99%+ coverage.

**Current Coverage**: 780 manifests generated

**Action Items**:

1. **Scan for Python packages without manifests**:
```bash
# Find all Python package directories
find . -type f -name "__init__.py" -not -path "*/.*" -not -path "*/venv/*" \
  -not -path "*/node_modules/*" -not -path "*/quarantine/*" | \
  xargs -I {} dirname {} | sort -u > /tmp/all_packages.txt

# Find all manifest directories
find manifests -name "module.manifest.json" | \
  xargs -I {} dirname {} | \
  sed 's|manifests/||' | sort -u > /tmp/manifested_packages.txt

# Find orphans
comm -23 /tmp/all_packages.txt /tmp/manifested_packages.txt > /tmp/orphan_packages.txt
```

2. **Generate manifests for orphans**:
```bash
# For each orphan, generate manifest
while read pkg; do
  echo "Generating manifest for: $pkg"
  python3 scripts/generate_module_manifests.py \
    --module-path "$pkg" \
    --star-from-rules \
    --write-context \
    --validate
done < /tmp/orphan_packages.txt
```

3. **Create audit report**:
```markdown
# Artifact Audit Report

**Date**: 2025-10-18
**Coverage Before**: 780 manifests
**Coverage After**: [N] manifests

## Orphans Found
- [List of orphan modules]

## Manifests Generated
- [List of generated manifests with star assignments]

## Coverage Metrics
- Total Python packages: [N]
- Manifested packages: [N]
- Coverage: [N]%
- Orphans remaining: [N] (quarantine, archive, etc.)
```

**Save to**: `docs/audits/artifact_coverage_audit_2025-10-18.md`

**Success Criteria**:
- 99%+ manifest coverage (excluding quarantine, archive, tests)
- All orphan modules identified
- Audit report generated
- New manifests validated

---

### 📋 Phase 2: Contract Validation & API Documentation

#### Task 2.1: Public API Documentation Scaffolding (OpenAPI Stubs)
**Priority**: Medium
**Time Estimate**: 2-3 hours
**Complexity**: Medium

**Objective**: Create OpenAPI 3.1 schema templates for LUKHAS public APIs and map manifests to API specs.

**Background**:
- We have `docs/openapi/lukhas-openai.json` from PR #431
- Need to expand this to cover full LUKHAS API surface

**Action Items**:

1. **Create OpenAPI stub for each major API surface**:

Create these files in `docs/openapi/`:
- `lukhas-memory-api.json` - Memory system APIs
- `lukhas-consciousness-api.json` - Consciousness APIs
- `lukhas-governance-api.json` - Guardian/Ethics APIs
- `lukhas-dream-api.json` - Dream system APIs
- `lukhas-identity-api.json` - ΛiD authentication APIs

**Template for each file**:
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "LUKHAS [Domain] API",
    "version": "0.1.0",
    "description": "API for LUKHAS [domain] system",
    "contact": {
      "name": "LUKHAS AI",
      "url": "https://lukhas.ai"
    }
  },
  "servers": [
    {
      "url": "https://api.lukhas.ai/v1",
      "description": "Production API"
    },
    {
      "url": "http://localhost:8000",
      "description": "Local development"
    }
  ],
  "paths": {
    "/[domain]/health": {
      "get": {
        "summary": "Health check for [domain] system",
        "operationId": "get[Domain]Health",
        "responses": {
          "200": {
            "description": "System healthy"
          }
        }
      }
    }
  },
  "components": {
    "schemas": {},
    "securitySchemes": {
      "BearerAuth": {
        "type": "http",
        "scheme": "bearer"
      }
    }
  }
}
```

2. **Map manifests to API specs**:

Create `docs/openapi/manifest_api_mapping.json`:
```json
{
  "mapping": [
    {
      "manifest": "memory/core/module.manifest.json",
      "api_spec": "lukhas-memory-api.json",
      "endpoints": ["/memory/store", "/memory/recall"]
    },
    {
      "manifest": "consciousness/core/module.manifest.json",
      "api_spec": "lukhas-consciousness-api.json",
      "endpoints": ["/consciousness/process", "/consciousness/reflect"]
    }
  ]
}
```

3. **Create API documentation README**:

Create `docs/openapi/README.md`:
```markdown
# LUKHAS OpenAPI Specifications

This directory contains OpenAPI 3.1 specifications for LUKHAS public APIs.

## Available APIs

- **Memory API** (`lukhas-memory-api.json`) - Memory storage and recall
- **Consciousness API** (`lukhas-consciousness-api.json`) - Cognitive processing
- **Governance API** (`lukhas-governance-api.json`) - Ethics and safety
- **Dream API** (`lukhas-dream-api.json`) - Dream synthesis
- **Identity API** (`lukhas-identity-api.json`) - Authentication (ΛiD)
- **OpenAI Compatibility** (`lukhas-openai.json`) - OpenAI-compatible facade

## Viewing Specifications

Use [Swagger Editor](https://editor.swagger.io/) or:
```bash
npm install -g @redocly/cli
redocly preview-docs docs/openapi/lukhas-memory-api.json
```

## Manifest Mapping

See `manifest_api_mapping.json` for the relationship between module manifests
and API specifications.
```

**Success Criteria**:
- 5+ OpenAPI stub files created
- Manifest-to-API mapping document exists
- OpenAPI README with usage instructions
- All specs validate against OpenAPI 3.1 schema

**Validation**:
```bash
# Validate OpenAPI specs (requires npm install -g @apidevtools/swagger-cli)
for spec in docs/openapi/*.json; do
  swagger-cli validate "$spec" && echo "✅ $spec" || echo "❌ $spec"
done
```

---

#### Task 2.2: `check_contract_refs.py` Robustness Pass
**Priority**: Medium
**Time Estimate**: 1-2 hours
**Complexity**: Low

**Objective**: Enhance contract validation script with better error handling, edge cases, and caching.

**File**: `scripts/validate_contract_refs.py`

**Current Issues**:
- Basic error messages
- No caching for repeated validations
- Doesn't handle all edge cases

**Enhancements to Add**:

1. **Better Error Reporting**:
```python
# Current
print(f"Unknown contract: {contract_id}")

# Enhanced
print(f"❌ Unknown contract: {contract_id}")
print(f"   Referenced in: {manifest_path}")
print(f"   Line: {line_number}")
print(f"   Available contracts: {', '.join(known_contracts[:5])}")
```

2. **Add Caching**:
```python
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_FILE = ".contract_validation_cache.json"
CACHE_TTL = timedelta(hours=1)

def load_cache():
    if Path(CACHE_FILE).exists():
        cache = json.loads(Path(CACHE_FILE).read_text())
        if datetime.fromisoformat(cache['timestamp']) > datetime.now() - CACHE_TTL:
            return cache['data']
    return None

def save_cache(data):
    cache = {'timestamp': datetime.now().isoformat(), 'data': data}
    Path(CACHE_FILE).write_text(json.dumps(cache, indent=2))
```

3. **Handle Edge Cases**:
```python
# Empty contracts list
if not contracts:
    # Don't error, just skip validation
    return

# Malformed contract IDs
if not re.match(r'^CON-\d{3}-[A-Z]+$', contract_id):
    warnings.append(f"Malformed contract ID: {contract_id}")

# Circular contract dependencies
visited = set()
def check_circular(contract_id, path=[]):
    if contract_id in path:
        errors.append(f"Circular dependency: {' -> '.join(path + [contract_id])}")
    # ... recursion
```

4. **Add Summary Statistics**:
```python
print("\n📊 Validation Summary:")
print(f"  Manifests checked: {total_manifests}")
print(f"  Contract references: {total_refs}")
print(f"  Unique contracts: {len(unique_contracts)}")
print(f"  Errors: {len(errors)}")
print(f"  Warnings: {len(warnings)}")
```

**Success Criteria**:
- Enhanced error messages with context
- Caching implemented (1 hour TTL)
- Edge cases handled gracefully
- Summary statistics printed
- No regressions in existing validation

**Validation**:
```bash
# Run with cache
python3 scripts/validate_contract_refs.py  # First run (slow)
python3 scripts/validate_contract_refs.py  # Second run (fast, cached)

# Test edge cases
python3 scripts/validate_contract_refs.py --test-malformed
python3 scripts/validate_contract_refs.py --test-circular
```

---

### 📋 Phase 3: Script Documentation

#### Task 3.1: Add Docstrings to All Scripts
**Priority**: Low
**Time Estimate**: 2-3 hours
**Complexity**: Low

**Objective**: Document all CLI tools and helper scripts with comprehensive docstrings and --help output.

**Files to Document** (scripts/):
```bash
# List all Python scripts
ls -1 scripts/*.py
```

**For each script, add**:

1. **Module-level docstring**:
```python
#!/usr/bin/env python3
"""
Generate module manifests for LUKHAS components.

This script scans the repository for Python modules and generates
standardized manifest files containing metadata, dependencies, contracts,
and constellation star assignments.

Usage:
    python3 scripts/generate_module_manifests.py --all
    python3 scripts/generate_module_manifests.py --module-path core/memory
    python3 scripts/generate_module_manifests.py --star-from-rules --write-context

Examples:
    # Generate all manifests with star promotion
    python3 scripts/generate_module_manifests.py --all --star-from-rules

    # Regenerate single module
    python3 scripts/generate_module_manifests.py --module-path consciousness/core

    # Validate only (no writes)
    python3 scripts/generate_module_manifests.py --all --validate-only

Exit Codes:
    0: Success
    1: Validation errors found
    2: File I/O errors

See Also:
    - configs/schemas/module_manifest.schema.json - Manifest schema
    - docs/dashboards/CONSTELLATION_STATS.md - Star statistics
"""
```

2. **Function docstrings**:
```python
def generate_manifest(module_path: str, star_from_rules: bool = False) -> dict:
    """
    Generate a manifest dictionary for the given module.

    Args:
        module_path: Relative path to module from repo root (e.g., 'core/memory')
        star_from_rules: If True, assign stars based on configs/star_rules.json

    Returns:
        Dictionary containing manifest data conforming to module_manifest.schema.json

    Raises:
        FileNotFoundError: If module_path doesn't exist
        ValidationError: If generated manifest doesn't pass schema validation

    Example:
        >>> manifest = generate_manifest('consciousness/core', star_from_rules=True)
        >>> manifest['module']['name']
        'Consciousness Core'
    """
```

3. **Argument descriptions** (argparse):
```python
parser.add_argument(
    '--star-from-rules',
    action='store_true',
    help='Assign constellation stars based on configs/star_rules.json (requires confidence >= 0.70)'
)

parser.add_argument(
    '--module-path',
    type=str,
    metavar='PATH',
    help='Path to specific module (relative to repo root, e.g., "consciousness/core")'
)
```

**Scripts to prioritize**:
1. `scripts/generate_module_manifests.py` - Main manifest generator
2. `scripts/validate_contract_refs.py` - Contract validator
3. `scripts/validate_module_manifests.py` - Manifest validator
4. `scripts/sync_t12_manifest_owners.py` - Owner sync tool
5. `scripts/dependency_scanner.py` - Dependency analysis
6. `scripts/normalize_imports.py` - Import normalization

**Success Criteria**:
- All scripts have module-level docstrings
- All functions have docstrings with Args/Returns/Raises
- All argparse arguments have help text
- `--help` output is comprehensive and helpful

**Validation**:
```bash
# Check all scripts have help
for script in scripts/*.py; do
  python3 "$script" --help 2>&1 | grep -q "usage:" || echo "Missing --help: $script"
done

# Check docstring coverage
python3 - <<PY
import ast
import sys
missing = []
for script in Path("scripts").glob("*.py"):
    tree = ast.parse(script.read_text())
    if not ast.get_docstring(tree):
        missing.append(script)
print(f"Scripts missing docstrings: {len(missing)}")
for m in missing:
    print(f"  - {m}")
PY
```

---

## Deliverables

When all tasks complete, you should have:

1. **Enhanced Documentation**:
   - [ ] 42 context files with YAML front matter, contract links, cross-references
   - [ ] Schema with comprehensive field descriptions
   - [ ] Audit report showing 99%+ manifest coverage

2. **API Foundation**:
   - [ ] 5+ OpenAPI specification stubs
   - [ ] Manifest-to-API mapping document
   - [ ] OpenAPI README with usage guide

3. **Improved Tooling**:
   - [ ] Enhanced contract validator with caching and better errors
   - [ ] Fully documented scripts with --help and docstrings

4. **Audit Reports**:
   - [ ] Artifact coverage audit (saved to docs/audits/)
   - [ ] Documentation enhancement summary

## Success Criteria

- ✅ All 42 context files enhanced with front matter
- ✅ Schema descriptions added to all required fields
- ✅ 99%+ manifest coverage achieved
- ✅ OpenAPI stubs created and validated
- ✅ Contract validator enhanced with caching
- ✅ All scripts fully documented
- ✅ No broken links in documentation
- ✅ All changes committed with T4 standard messages

## Commit Message Templates

### For documentation enhancements:
```
docs(context): enhance lukhas_context files with YAML front matter

**Problem**
- Context files lacked standardized metadata
- No contract links or cross-references
- Difficult to discover related modules

**Solution**
- Added YAML front matter to 42 context files
- Linked contract references where applicable
- Added cross-references between related modules
- Included constellation star alignments

**Impact**
- ✅ Improved discoverability
- ✅ Better module relationship visibility
- ✅ Standardized context file format

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### For schema enhancements:
```
feat(schema): add field descriptions to manifest schema

**Problem**
- Validator error messages lacked context
- Schema fields had no descriptions
- Developers unsure of field purposes

**Solution**
- Added descriptions to all required fields
- Enhanced validator error messages with field context
- Added examples for complex fields

**Impact**
- ✅ Helpful validation errors
- ✅ Self-documenting schema
- ✅ Better developer experience

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### For artifact audit:
```
docs(audit): achieve 99% manifest coverage - artifact audit complete

**Problem**
- [N] orphan modules lacked manifests
- Incomplete artifact coverage
- No systematic audit process

**Solution**
- Scanned for all Python packages
- Generated manifests for [N] orphan modules
- Created comprehensive audit report
- Validated all new manifests

**Impact**
- ✅ Coverage: 780 → [N] manifests (99%+)
- ✅ All production modules manifested
- ✅ Audit report: docs/audits/artifact_coverage_audit_2025-10-18.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Branch Strategy

Create branch from main:
```bash
git checkout main
git pull origin main
git checkout -b feat/phase1-3-completion
```

Work in this branch, commit regularly, then create PR when complete.

## Questions/Blockers

If you encounter issues:

1. **Missing contract files**: Some contract IDs in manifests may reference non-existent contracts - document these and skip validation
2. **Orphan modules in quarantine**: Don't generate manifests for quarantine/ - these are intentionally unmaintained
3. **OpenAPI validation requires tools**: If swagger-cli not available, document the specs but skip validation

## Time Estimate

**Total**: 12-15 hours

- Task 1.1: Context files (2-3h)
- Task 1.2: Schema docstrings (1-2h)
- Task 1.3: Artifact audit (2-3h)
- Task 2.1: OpenAPI stubs (2-3h)
- Task 2.2: Contract validator (1-2h)
- Task 3.1: Script docs (2-3h)
- Testing & commit (1-2h)

## Getting Started

1. Read this brief thoroughly
2. Create branch `feat/phase1-3-completion`
3. Start with Task 1.3 (Artifact Audit) - highest priority
4. Work through tasks in order
5. Commit after each task completion
6. Create PR when all tasks complete

Good luck! 🚀
