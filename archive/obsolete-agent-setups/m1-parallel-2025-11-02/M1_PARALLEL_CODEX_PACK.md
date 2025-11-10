# M1 Parallel Codex Pack - Codemod Automation

**Target**: M1 Branch Laptop (Primary Codex Work)  
**Branch Base**: `origin/M1`  
**Timeline**: 1-2 hours  
**Safety Level**: T4-Safe (dry-run only, no auto-apply)

---

## 🎯 Mission Overview

Run automated codemod in dry-run mode, filter for conservative patches, and produce safe batch archive for human review. This is CPU/light IO work that produces artifacts for the main machine to review and apply.

## ⚡ Quick Start Commands

```bash
# Step 0: Checkout M1 branch
git fetch origin
git checkout --track -B M1 origin/M1
git pull --ff origin M1

# Step 1: Setup environment
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip setuptools wheel libcst

# Step 2: Run codemod dry-run
mkdir -p /tmp/codmod_patches
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
ls -1 /tmp/codmod_patches | wc -l

# Step 3: Filter safe patches
chmod +x scripts/automation/filter_safe_patches.sh
scripts/automation/filter_safe_patches.sh --patch-dir /tmp/codmod_patches --out-dir /tmp/codmod_batches/batch1.safe

# Step 4: Create archive
tar -czf /tmp/codemod_batch1_patches.tgz -C /tmp/codmod_batches batch1.safe
ls -1 /tmp/codmod_batches/batch1.safe | wc -l
```

## 🤖 Codex Agent Prompt

```
Task: Run LUKHAS codemod dry-run and produce safe first batch.

Steps:
1) Run: python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
2) Filter conservative patches: scripts/automation/filter_safe_patches.sh --patch-dir /tmp/codmod_patches --out-dir /tmp/codmod_batches/batch1.safe  
3) Archive the safe batch: tar -czf /tmp/codemod_batch1_patches.tgz -C /tmp/codmod_batches batch1.safe
4) Upload or print the archive path and produce a JSON report with counts (total patches, safe patches, flagged patches).

Constraints: 
- Do NOT apply any patches automatically
- Provide archive for human review only
- Generate summary report of filtered results

Output: Archive path + JSON summary report
```

## 🔍 Filter Logic (Conservative)

The filter keeps only patches that:
- ✅ Include `importlib` or `_importlib` 
- ✅ Include `getattr(_mod,...)` pattern
- ✅ Don't delete function/class headers
- ✅ Have minimal non-import deletions
- ✅ Follow try/except pattern with fallback

## 📦 Expected Deliverables

1. **Archive**: `/tmp/codemod_batch1_patches.tgz`
2. **Summary Report**: JSON with counts (total, safe, flagged)
3. **Upload Location**: PR comment or shared location
4. **Coordination Note**: "Batch-1 ready for main machine review"

## 🛡️ Safety Checks

- ✅ Dry-run only (no files modified)
- ✅ Conservative filtering applied
- ✅ Human review required before apply
- ✅ No changes to `.importlinter` or `.venv`
- ✅ Artifacts uploaded for review

## 🔄 Validation Commands

```bash
# Quick sanity check
for p in /tmp/codmod_batches/batch1.safe/*.patch; do
  echo "---- $p ----"
  sed -n '1,120p' "$p"
  echo
done | head -n 200

# Count verification
echo "Total patches: $(ls -1 /tmp/codmod_patches | wc -l)"
echo "Safe patches: $(ls -1 /tmp/codmod_batches/batch1.safe | wc -l)"
```

## 📋 Coordination Rules

1. **No Auto-Apply**: Archive only, no patches applied
2. **Upload Required**: Share archive for main machine review
3. **Label PRs**: Use `agent:codex-M1` label
4. **File Lock**: Coordinate with main machine on file conflicts
5. **Human Gate**: Main team reviews before applying any patches

---

**Status**: Ready for Codex execution  
**Next**: Upload archive → Main machine review → Apply safe patches