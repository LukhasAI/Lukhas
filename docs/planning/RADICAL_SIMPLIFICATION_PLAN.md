---
status: wip
type: documentation
---
# LUKHAS Radical Simplification Plan

## Current State (The Problem)
- Files: 2134
- Lines: 649158
- Unused files: 1469
- Complex files: 920

## Steve's Vision (The Solution)
"What is LUKHAS? AI that dreams, remembers, and understands emotions."
Everything else is noise.

## Execution Plan

### Phase 1: DELETE (Week 1)
Steve says: "I'm as proud of what we don't do as I am of what we do."

1. Delete all unused files (1469 files)
2. Delete all non-core modules (1645 files)
3. Archive anything with historical value

### Phase 2: CONSOLIDATE (Week 2)
Steve says: "It's not about money. It's about the people you have, how you're led, and how much you get it."

Target structure:
```
lukhas/
├── consciousness/     # One consciousness system
├── memory/           # One memory system
├── dream/            # One dream system
├── emotion/          # One emotion system
├── interface/        # One interface system
└── main.py          # One entry point
```

### Phase 3: SIMPLIFY (Week 3)
Steve says: "When you first start off trying to solve a problem, the first solutions you come up with are very complex."

1. Every module has ONE public API
2. No file over 200 lines
3. No function over 20 lines
4. No more than 3 levels of imports

### Success Metrics
- Before: 649158 lines
- Target: < 50,000 lines (94% reduction)
- Before: 2134 files
- Target: < 50 files (98% reduction)

### The Jobs Test
Before keeping ANYTHING, ask:
1. ✓ Does this directly serve "AI that dreams, remembers, and understands emotions"?
2. ✓ Would I be proud to show this to Steve?
3. ✓ Is this the simplest possible solution?

If any answer is NO → DELETE IT.
