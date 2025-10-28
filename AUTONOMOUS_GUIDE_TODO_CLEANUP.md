# Autonomous Guide: TODO Cleanup Campaign (Reduce 6,876 to <1,000)

**Goal:** Systematically reduce TODO/FIXME debt from 7,568 items to under 1,000
**Priority:** Medium (Ongoing effort)
**Estimated Time:** 10-15 hours over multiple sessions
**Compatible With:** Claude Code, Codex, GitHub Copilot, Manual Execution

---

## 📋 Current Status

- **TODO Comments:** 6,876
- **FIXME Comments:** 692
- **Total Debt:** 7,568 items
- **Target:** <1,000 items (87% reduction)

---

## 🎯 Phase 1: Categorize and Prioritize (30 minutes)

### Step 1.1: Generate Full TODO Inventory
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Generate TODO inventory
grep -r "TODO" --include="*.py" . 2>/dev/null | \
  grep -v ".git" | grep -v "__pycache__" | grep -v ".venv" \
  > /tmp/todo_inventory.txt

# Generate FIXME inventory
grep -r "FIXME" --include="*.py" . 2>/dev/null | \
  grep -v ".git" | grep -v "__pycache__" | grep -v ".venv" \
  > /tmp/fixme_inventory.txt

wc -l /tmp/todo_inventory.txt /tmp/fixme_inventory.txt
```

### Step 1.2: Categorize by Lane
```bash
# Production lane (lukhas/)
grep "lukhas/" /tmp/todo_inventory.txt | wc -l

# Integration lane (core/)
grep "core/" /tmp/todo_inventory.txt | wc -l

# Development lane (candidate/)
grep "candidate/" /tmp/todo_inventory.txt | wc -l

# Other locations
grep -v "lukhas/" /tmp/todo_inventory.txt | \
  grep -v "core/" | grep -v "candidate/" | wc -l
```

### Step 1.3: Categorize by Priority Tags
```bash
# High priority
grep -i "TODO-HIGH\|TODO:HIGH\|FIXME:CRITICAL" /tmp/todo_inventory.txt | wc -l

# Medium priority
grep -i "TODO-MED\|TODO:MED\|FIXME" /tmp/todo_inventory.txt | wc -l

# Low priority / No tag
grep -v "TODO-HIGH\|TODO-MED\|FIXME" /tmp/todo_inventory.txt | wc -l
```

### Step 1.4: Categorize by Type
```bash
# Create categorization script
cat > /tmp/categorize_todos.py << 'EOF'
import sys
import re

categories = {
    'implementation': 0,
    'documentation': 0,
    'testing': 0,
    'refactor': 0,
    'cleanup': 0,
    'bug': 0,
    'performance': 0,
    'security': 0,
    'other': 0
}

keywords = {
    'implementation': ['implement', 'add', 'create', 'build'],
    'documentation': ['document', 'docstring', 'comment', 'explain'],
    'testing': ['test', 'coverage', 'validation', 'verify'],
    'refactor': ['refactor', 'clean', 'simplify', 'improve'],
    'cleanup': ['remove', 'delete', 'unused', 'deprecated'],
    'bug': ['fix', 'bug', 'issue', 'error'],
    'performance': ['optimize', 'performance', 'speed', 'cache'],
    'security': ['security', 'auth', 'permission', 'secret']
}

for line in sys.stdin:
    line_lower = line.lower()
    categorized = False
    for category, kws in keywords.items():
        if any(kw in line_lower for kw in kws):
            categories[category] += 1
            categorized = True
            break
    if not categorized:
        categories['other'] += 1

for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"{cat:15s}: {count:5d}")
EOF

cat /tmp/todo_inventory.txt | python3 /tmp/categorize_todos.py
```

---

## 🚀 Phase 2: Execute Cleanup by Strategy (Multiple Sessions)

### Strategy A: Delete Obsolete TODOs (High Impact, Low Effort)

**Target:** ~30% reduction (2,000+ items)

**Step 2A.1: Identify Obsolete TODOs**
```bash
# TODOs in files that don't exist
grep "TODO.*deprecat\|TODO.*old\|TODO.*legacy" /tmp/todo_inventory.txt > /tmp/obsolete_todos.txt

# TODOs already implemented
grep "TODO.*implement" /tmp/todo_inventory.txt | head -20
# Manually verify if already done, mark for deletion
```

**Step 2A.2: Create Cleanup Branch**
```bash
git checkout -b cleanup/obsolete-todos-$(date +%Y-%m-%d)
```

**Step 2A.3: Delete Obsolete TODOs**
```python
# Create deletion script
cat > /tmp/delete_obsolete_todos.py << 'EOF'
#!/usr/bin/env python3
"""Delete obsolete TODO comments from Python files."""

import re
import sys
from pathlib import Path

def remove_todo_line(file_path, line_number):
    """Remove a single TODO line from file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Remove the line (1-indexed to 0-indexed)
    if 0 <= line_number - 1 < len(lines):
        del lines[line_number - 1]

    with open(file_path, 'w') as f:
        f.writelines(lines)

if __name__ == '__main__':
    # Read obsolete_todos.txt
    # Format: filepath:line_number:TODO text
    with open('/tmp/obsolete_todos.txt') as f:
        for line in f:
            parts = line.split(':', 2)
            if len(parts) >= 2:
                filepath = parts[0]
                try:
                    line_num = int(parts[1])
                    remove_todo_line(filepath, line_num)
                    print(f"Removed TODO from {filepath}:{line_num}")
                except (ValueError, FileNotFoundError) as e:
                    print(f"Error: {e}")
EOF

python3 /tmp/delete_obsolete_todos.py
```

**Step 2A.4: Validate and Commit**
```bash
# Run smoke tests
make smoke  # Must pass 10/10

# Commit
git add .
git commit -m "chore(cleanup): remove obsolete TODO comments

Removed ~$(git diff --cached | grep -c "^-.*TODO") obsolete TODO comments that were:
- Referring to already-implemented features
- In deprecated/legacy code paths
- Marked as obsolete

Impact: TODO count reduced from 6,876 to $(grep -r "TODO" --include="*.py" . | wc -l)

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin cleanup/obsolete-todos-$(date +%Y-%m-%d)
gh pr create --title "chore(cleanup): remove obsolete TODOs" --body "..."
```

---

### Strategy B: Convert TODOs to GitHub Issues (Medium Impact, Medium Effort)

**Target:** ~25% reduction (1,500+ items)

**Step 2B.1: Extract High-Value TODOs**
```bash
# Get TODO-HIGH items
grep -i "TODO-HIGH" /tmp/todo_inventory.txt > /tmp/high_priority_todos.txt

# Get complex implementation TODOs
grep -i "TODO.*implement.*feature\|TODO.*add.*system" /tmp/todo_inventory.txt \
  > /tmp/complex_todos.txt
```

**Step 2B.2: Create GitHub Issues**
```bash
# For each high-priority TODO, create an issue
while IFS= read -r line; do
  file=$(echo "$line" | cut -d':' -f1)
  linenum=$(echo "$line" | cut -d':' -f2)
  todo_text=$(echo "$line" | cut -d':' -f3-)

  # Create issue
  gh issue create \
    --title "$(echo "$todo_text" | sed 's/TODO://g' | sed 's/^ *//g' | head -c 80)" \
    --body "**Source:** $file:$linenum

$todo_text

**Context:** Migrated from inline TODO comment during cleanup campaign.
**Priority:** High
**Lane:** $(echo "$file" | cut -d'/' -f1)" \
    --label "todo-migration,enhancement"

  # Replace TODO with issue reference
  # (Script to update file with issue link)

done < /tmp/high_priority_todos.txt
```

**Step 2B.3: Replace TODOs with Issue Links**
```python
# Create replacement script
cat > /tmp/replace_todo_with_issue.py << 'EOF'
#!/usr/bin/env python3
"""Replace TODO comments with GitHub issue references."""

import re
import subprocess

def replace_todo_with_issue(file_path, line_number, issue_number):
    """Replace TODO line with GitHub issue reference."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    if 0 <= line_number - 1 < len(lines):
        # Replace TODO with issue link
        old_line = lines[line_number - 1]
        indent = len(old_line) - len(old_line.lstrip())
        new_line = ' ' * indent + f"# See: https://github.com/LukhasAI/Lukhas/issues/{issue_number}\n"
        lines[line_number - 1] = new_line

    with open(file_path, 'w') as f:
        f.writelines(lines)

# Usage: Called by parent script with file, line, issue number
EOF
```

---

### Strategy C: Fix Simple TODOs (Low Impact, High Effort)

**Target:** ~15% reduction (1,000+ items)

**Step 2C.1: Identify Simple TODOs**
```bash
# TODOs that are simple docstring additions
grep "TODO.*docstring\|TODO.*add comment" /tmp/todo_inventory.txt \
  > /tmp/simple_docstring_todos.txt

# TODOs that are simple type hint additions
grep "TODO.*type.*hint\|TODO.*typing" /tmp/todo_inventory.txt \
  > /tmp/simple_typing_todos.txt
```

**Step 2C.2: Fix in Batches**
```bash
git checkout -b cleanup/simple-docstrings-$(date +%Y-%m-%d)

# For each simple TODO, implement the fix
# Example: Add docstring
# Before:
#   def foo():
#       # TODO: add docstring
#       pass
# After:
#   def foo():
#       """Brief description of foo."""
#       pass

# Commit in small batches (10-20 files at a time)
git add <files>
git commit -m "docs: add docstrings to resolve TODO comments in <module>"
```

---

### Strategy D: Archive candidate/ TODOs (High Impact, Low Effort)

**Target:** ~20% reduction (1,500+ items)

**Rationale:** candidate/ lane is experimental - TODOs there are expected and don't count against production health.

**Step 2D.1: Tag candidate/ TODOs**
```bash
# Find all TODOs in candidate/
grep "candidate/" /tmp/todo_inventory.txt > /tmp/candidate_todos.txt
wc -l /tmp/candidate_todos.txt

# These don't need cleanup - they're part of experimental development
```

**Step 2D.2: Update Metrics to Exclude candidate/**
```bash
# Create filtered TODO count script
cat > /tmp/count_production_todos.sh << 'EOF'
#!/bin/bash
# Count TODOs excluding candidate/ lane
grep -r "TODO" --include="*.py" . 2>/dev/null | \
  grep -v ".git" | grep -v "__pycache__" | grep -v ".venv" | \
  grep -v "candidate/" | wc -l
EOF

chmod +x /tmp/count_production_todos.sh
/tmp/count_production_todos.sh
```

**Production TODO Count (excluding candidate/):** Expected ~3,000-4,000

---

## ✅ Phase 3: Verification (15 minutes)

### Step 3.1: Count Remaining TODOs
```bash
# Total count
grep -r "TODO" --include="*.py" . | grep -v ".git" | wc -l

# Production count (excluding candidate/)
grep -r "TODO" --include="*.py" . | grep -v ".git" | \
  grep -v "candidate/" | wc -l

# Target: <1,000 in production code
```

### Step 3.2: Generate Final Report
```bash
cat > /tmp/todo_cleanup_report.md << EOF
# TODO Cleanup Campaign Report

## Before
- Total TODOs: 6,876
- FIXMEs: 692
- Total Debt: 7,568

## After
- Total TODOs: $(grep -r "TODO" --include="*.py" . | grep -v ".git" | wc -l)
- FIXMEs: $(grep -r "FIXME" --include="*.py" . | grep -v ".git" | wc -l)
- Production TODOs: $(grep -r "TODO" --include="*.py" . | grep -v ".git" | grep -v "candidate/" | wc -l)

## Reduction
- Absolute: $((6876 - $(grep -r "TODO" --include="*.py" . | grep -v ".git" | wc -l)))
- Percentage: $(echo "scale=1; (6876 - $(grep -r "TODO" --include="*.py" . | grep -v ".git" | wc -l)) * 100 / 6876" | bc)%

## Strategies Used
- Deleted obsolete TODOs: XXX items
- Converted to GitHub issues: XXX items
- Fixed simple TODOs: XXX items
- Excluded candidate/ lane: XXX items
EOF

cat /tmp/todo_cleanup_report.md
```

---

## 📋 Execution Checklist

```
Phase 1: Categorization
[ ] Generate TODO/FIXME inventory
[ ] Categorize by lane (lukhas/, core/, candidate/)
[ ] Categorize by priority (HIGH, MED, LOW)
[ ] Categorize by type (implementation, docs, etc.)

Phase 2: Cleanup Strategies
[ ] Strategy A: Delete obsolete TODOs (~2,000 items)
[ ] Strategy B: Convert to GitHub issues (~1,500 items)
[ ] Strategy C: Fix simple TODOs (~1,000 items)
[ ] Strategy D: Exclude candidate/ (~1,500 items)

Phase 3: Verification
[ ] Count remaining TODOs
[ ] Verify target met (<1,000 in production)
[ ] Generate cleanup report
[ ] Update documentation
```

---

## 🎯 Success Criteria

### Must Achieve
- ✅ Production TODO count <1,000 (excluding candidate/)
- ✅ No TODO-HIGH items unaddressed
- ✅ Smoke tests 10/10 PASS
- ✅ All cleanup PRs documented

### Should Achieve
- ✅ GitHub issues created for complex TODOs
- ✅ Simple TODOs resolved
- ✅ Cleanup report generated

---

## ⚠️ Important Notes

### What NOT to Delete
- ❌ TODOs with active work-in-progress
- ❌ TODOs referencing known bugs with workarounds
- ❌ TODOs in candidate/ (expected experimental work)
- ❌ Security-related TODOs (convert to issues instead)

### Best Practices
1. **Batch commits:** Group 10-20 similar TODO fixes per commit
2. **Test between batches:** Run smoke tests after each batch
3. **Document decisions:** Note why TODOs were deleted/converted
4. **Create issues for complex work:** Don't delete, migrate to tracking system

---

## 📊 Expected Timeline

- **Phase 1:** 30 minutes (categorization)
- **Strategy A:** 2 hours (delete obsolete)
- **Strategy B:** 4 hours (convert to issues)
- **Strategy C:** 6 hours (fix simple)
- **Strategy D:** 1 hour (exclude candidate/)
- **Phase 3:** 30 minutes (verification)

**Total:** ~14 hours over 3-4 sessions

---

## 🤖 Autonomous Execution Notes

**For AI Agents (Claude Code, Codex, Copilot):**

1. **Start with Strategy A** - Highest impact, lowest risk
2. **Validate frequently** - Smoke tests after each batch
3. **Conservative deletions** - When in doubt, create an issue
4. **Report progress** - Update user after each strategy
5. **Emergency stop** - If smoke tests fail, stop and rollback

**Success Signal:** Production TODO count <1,000 and smoke tests passing

---

**Last Updated:** 2025-10-28
**Status:** Ready for Autonomous Execution
**Difficulty:** Medium-High (requires judgment)
**Risk:** Low (if validated frequently)
