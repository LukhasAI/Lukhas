# 📁 Artifacts Location Reference

**Repository:** LukhasAI/Lukhas  
**Last Updated:** 2025-10-28  
**Purpose:** Quick reference for all pre-generated artifacts

---

## 🎯 TODO Replacement Artifacts

### Primary Mapping File
```
artifacts/todo_to_issue_map.json
```
**Size:** ~15 KB  
**Entries:** 78 mappings  
**Format:** JSON  
**Content:** Maps `file:line` → GitHub issue number  

**Sample Entry:**
```json
{
  ".semgrep/lukhas-security.yaml:547": {
    "issue": 552,
    "title": "implement authentication",
    "repo": "LukhasAI/Lukhas"
  }
}
```

**Usage:**
```bash
# View mappings
cat artifacts/todo_to_issue_map.json | python3 -m json.tool | head -40

# Count entries
cat artifacts/todo_to_issue_map.json | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"

# Find specific file
cat artifacts/todo_to_issue_map.json | python3 -m json.tool | grep "lukhas_website"
```

---

### Replacement Log
```
artifacts/replace_todos_log.json
```
**Size:** ~3 KB  
**Entries:** 38 files  
**Format:** JSON  
**Content:** Dry-run results with file paths and issue numbers  

**Sample Entry:**
```json
{
  "file": ".semgrep/lukhas-security.yaml",
  "line": 547,
  "issue": 552,
  "repo": "LukhasAI/Lukhas",
  "applied": false
}
```

**Usage:**
```bash
# View affected files
cat artifacts/replace_todos_log.json | python3 -m json.tool | grep '"file"' | sort

# Count files
cat artifacts/replace_todos_log.json | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"
```

---

## 📊 MATRIZ Migration Artifacts

### Migration Manifest
```
artifacts/matriz_manifest.json
```
**Content:** MATRIZ import migration tracking  
**Status:** ✅ Complete (PR #540 merged)

---

## 📋 Documentation Artifacts

### TODO Analysis Report
```
TODO_CONVERSION_SUMMARY.md
```
**Size:** 199 lines  
**Content:**
- Original inventory: 215 TODOs
- Filtered inventory: 78 TODOs (HIGH priority)
- Exclusion criteria (archives, backups, build artifacts)
- Security concentration: 93.6%
- Distribution by directory

---

### Parallel Workflow Guide
```
PARALLEL_TODO_WORK.md
```
**Size:** 120 lines  
**Content:**
- Quick start for GitHub Copilot
- Quick start for Claude Code
- Quick start for Cursor
- Conflict avoidance strategies
- Example commands

---

### Codex Setup Guide
```
CODEX_PARALLEL_SETUP.md
```
**Size:** 160 lines  
**Content:**
- Codex primary assignments (MATRIZ ✅, Import Org 🔄)
- Codex secondary roles (TODO, Tests, Candidate)
- Option A: Import Organization (E402 fixes)
- Option B: TODO Replacement (recommended)
- Cost-conscious execution strategy

---

### Codex Initiation Prompt
```
CODEX_INITIATION_PROMPT.md
```
**Size:** 450+ lines  
**Content:**
- Complete mission briefing
- Step-by-step execution instructions (9 steps)
- Artifact locations and formats
- Safety guardrails
- Troubleshooting guide
- Success criteria

---

### Quick Start Card
```
CODEX_QUICK_START.txt
```
**Size:** 28 lines  
**Format:** ASCII box  
**Content:** One-page command reference for Codex

---

## 🔧 Scripts

### TODO Inventory Generator
```
scripts/todo_migration/generate_todo_inventory.py
```
**Size:** 248 lines  
**Functionality:**
- Scans codebase for TODOs
- Multi-format parsing (Python/JS/C)
- Priority detection
- Security keyword detection (15 keywords)
- CSV output with metadata

**Usage:**
```bash
python3 scripts/todo_migration/generate_todo_inventory.py \
  --output todo_inventory.csv \
  --priority HIGH \
  --root /Users/agi_dev/LOCAL-REPOS/Lukhas
```

---

### TODO Replacement Script
```
scripts/todo_migration/replace_todos_with_issues.py
```
**Size:** 5.1 KB  
**Functionality:**
- Reads mapping JSON
- Replaces TODOs with GitHub issue links
- Dry-run mode (default)
- Apply mode (--apply flag)
- Generates replacement log

**Usage:**
```bash
# Dry-run (default)
python3 scripts/todo_migration/replace_todos_with_issues.py \
  --map artifacts/todo_to_issue_map.json

# Apply changes
python3 scripts/todo_migration/replace_todos_with_issues.py \
  --map artifacts/todo_to_issue_map.json \
  --apply
```

---

### MATRIZ Import Rewriter
```
scripts/consolidation/rewrite_matriz_imports.py
```
**Functionality:**
- AST-based import rewriting
- Case standardization (matriz → MATRIZ)
- E402 linting fixes
- Dry-run and apply modes

**Usage:**
```bash
# Check what would change
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --path lukhas core serve \
  --dry-run --verbose

# Apply changes
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --path lukhas core serve \
  --git-apply
```

---

## 📂 Directory Structure

```
/Users/agi_dev/LOCAL-REPOS/Lukhas/
├── artifacts/
│   ├── todo_to_issue_map.json          ← 78 TODO→issue mappings
│   ├── replace_todos_log.json          ← Dry-run results (38 files)
│   └── matriz_manifest.json            ← MATRIZ migration tracking
│
├── scripts/
│   ├── todo_migration/
│   │   ├── generate_todo_inventory.py  ← TODO scanner
│   │   └── replace_todos_with_issues.py ← TODO replacer
│   └── consolidation/
│       └── rewrite_matriz_imports.py   ← Import rewriter
│
├── docs/
│   ├── TODO_CONVERSION_SUMMARY.md      ← Analysis report
│   └── PARALLEL_TODO_WORK.md           ← Workflow guide
│
├── CODEX_PARALLEL_SETUP.md             ← Codex assignments
├── CODEX_INITIATION_PROMPT.md          ← Mission briefing
├── CODEX_QUICK_START.txt               ← Command reference
└── ARTIFACTS_LOCATIONS.md              ← This file
```

---

## 🚀 Quick Access Commands

### View All TODO Artifacts
```bash
ls -lh artifacts/todo* artifacts/replace*
```

### Validate All Artifacts
```bash
# Check JSON syntax
python3 -c "import json; json.load(open('artifacts/todo_to_issue_map.json')); print('✅ Mapping valid')"
python3 -c "import json; json.load(open('artifacts/replace_todos_log.json')); print('✅ Log valid')"

# Check file counts
echo "Mappings: $(cat artifacts/todo_to_issue_map.json | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')"
echo "Files to update: $(cat artifacts/replace_todos_log.json | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')"
```

### View All Documentation
```bash
ls -lh *.md | grep -E "CODEX|TODO|PARALLEL|ARTIFACTS"
```

### Check Script Availability
```bash
ls -lh scripts/todo_migration/*.py
ls -lh scripts/consolidation/*.py
```

---

## 📊 Artifact Statistics

| Artifact | Size | Type | Entries | Status |
|----------|------|------|---------|--------|
| `todo_to_issue_map.json` | ~15 KB | JSON | 78 | ✅ Ready |
| `replace_todos_log.json` | ~3 KB | JSON | 38 | ✅ Ready |
| `matriz_manifest.json` | ~10 KB | JSON | 17 | ✅ Complete |
| `TODO_CONVERSION_SUMMARY.md` | 199 lines | MD | N/A | ✅ Ready |
| `PARALLEL_TODO_WORK.md` | 120 lines | MD | N/A | ✅ Ready |
| `CODEX_PARALLEL_SETUP.md` | 160 lines | MD | N/A | ✅ Ready |
| `CODEX_INITIATION_PROMPT.md` | 450+ lines | MD | N/A | ✅ Ready |

---

## 🔍 Search Helpers

### Find Specific Issue in Mapping
```bash
# Find which file has issue #581
cat artifacts/todo_to_issue_map.json | python3 -c "import sys,json; m=json.load(sys.stdin); print([k for k,v in m.items() if v['issue']==581])"
```

### Find All Issues in a Directory
```bash
# Find all lukhas_website issues
cat artifacts/todo_to_issue_map.json | python3 -m json.tool | grep -B2 "lukhas_website"
```

### Count Issues by Priority
```bash
# From original summary
grep "security-related" TODO_CONVERSION_SUMMARY.md
```

---

## 💾 Backup Locations

**Original Files:** Git history (pre-TODO replacement)  
**Backup Branch:** `main` (before replacement PR)  
**Rollback:** `git revert <commit>` if needed

---

## 🆘 Emergency Recovery

If artifacts are lost or corrupted:

```bash
# Regenerate mapping from GitHub issues
gh issue list --limit 100 --json number,title,body | \
  python3 -c "import sys,json; ..." > artifacts/todo_to_issue_map_regenerated.json

# Or restore from git history
git show HEAD~N:artifacts/todo_to_issue_map.json > artifacts/todo_to_issue_map.json
```

---

**Last Verified:** 2025-10-28 17:30 PST  
**All Artifacts:** ✅ Present and validated  
**Ready for Codex Execution:** ✅ YES
