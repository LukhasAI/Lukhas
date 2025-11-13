# TODO Inbox

> **Quick-drop zone for unorganized TODOs**
>
> Drop tasks here when you're in the middle of work and don't have time to organize them properly.
> They'll be processed and moved to the appropriate location in the next review cycle.

---

## How to Use

### 1. Quick Drop (Human or AI)

When you encounter a TODO mid-work:

```bash
# Option 1: Quick text file
echo "Fix the memory leak in matriz/core/node.py" > TODO/inbox/YYYY-MM-DD-memory-leak.txt

# Option 2: Use the template
cp TODO/inbox/_TEMPLATE.md TODO/inbox/2025-11-11-my-task.md
# Edit with your task details
```

### 2. Naming Convention

**Format**: `YYYY-MM-DD-short-description.{md|txt}`

**Examples**:
- `2025-11-11-guardian-veto-bug.md`
- `2025-11-11-add-metrics.txt`
- `2025-11-11-refactor-consciousness.md`

### 3. What Happens Next

**Daily Review** (automated or human):
1. Process inbox items
2. Assign priority (P0-P3)
3. Generate task ID
4. Add to MASTER_LOG.md
5. Move processed file to `active/` or `archive/`

### 4. Template Usage

Copy `_TEMPLATE.md` for structured tasks:

```bash
cp TODO/inbox/_TEMPLATE.md TODO/inbox/$(date +%Y-%m-%d)-my-task.md
```

Fill in:
- **Title**: Brief description
- **Context**: Why is this needed?
- **Details**: What needs to be done?
- **Files**: Which files are affected?
- **Effort**: S/M/L guess
- **Priority**: Your best guess (reviewer may adjust)

---

## Processing Script

```bash
# Process all inbox items (moves to MASTER_LOG.md)
python scripts/todo/process_inbox.py

# Process and assign to specific agent
python scripts/todo/process_inbox.py --agent=jules

# Dry run (preview what would happen)
python scripts/todo/process_inbox.py --dry-run
```

---

## Rules

### ✅ DO:
- Drop tasks anytime during work
- Use simple text for quick notes
- Use template for complex tasks
- Include file paths when relevant
- Add context (why is this important?)

### ❌ DON'T:
- Leave tasks in inbox >7 days
- Drop duplicate tasks (check MASTER_LOG first if possible)
- Use inbox for conversations (use GitHub Issues)
- Include secrets or PII

---

## Inbox Status

**Auto-generated stats** (updated by process_inbox.py):

- **Inbox count**: 0 items
- **Oldest item**: N/A
- **Last processed**: Never
- **Average processing time**: N/A

**Inbox health**: 🟢 Healthy (0 items)

Thresholds:
- 🟢 Healthy: 0-5 items
- 🟡 Warning: 6-15 items
- 🔴 Critical: 16+ items (process immediately!)

---

## Integration with MASTER_LOG

When processed, inbox items become:

1. **Task ID assigned**: `T20251111001`
2. **Priority determined**: Based on T4 criteria
3. **Added to MASTER_LOG.md**: Appropriate priority section
4. **Detail file created**: If complex (in `active/`)
5. **Inbox file archived**: Moved to `processed/YYYY-MM-DD/`

---

**Last Updated**: 2025-11-11
