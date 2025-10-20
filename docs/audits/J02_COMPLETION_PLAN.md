# Jules J-02 Completion Plan

**Created**: 2025-10-20
**Status**: In Progress
**Branch**: `feat/jules-j02-finish`
**Goal**: Add function-level docstrings (Args/Returns/Raises/Examples) to 33 remaining functions

---

## Functions Needing Work (33 total)

### Priority 1: Manifest Scripts (Phase 4 Critical) - 13 functions

**scripts/generate_module_manifests.py** (9 functions):
- [ ] `validate_star(star: str) -> bool` - Add Args/Returns
- [ ] `guess_colony(path: str) -> str` - Add full docstring
- [ ] `infer_capabilities(...)` - Add Args
- [ ] `map_priority_to_quality_tier(...)` - Add Args
- [ ] `decide_quality_tier(...)` - Add Args
- [ ] `discover_tests(...)` - Add Args
- [ ] `build_testing_block(...)` - Add Args
- [ ] `now_iso() -> str` - Add full docstring
- [ ] `make_context_md(...) -> str` - Add full docstring

**scripts/validate_module_manifests.py** (4 functions):
- [ ] `__init__(self, schema_path: Path)` - Add docstring
- [ ] `find_lukhas_modules(...) -> List[Path]` - Add Args
- [ ] `validate_all_modules(...)` - Add Args
- [ ] `generate_summary_report(...) -> str` - Add Args

### Priority 2: Migration & Sync Scripts - 13 functions

**scripts/context_coverage_bot.py** (3 functions):
- [ ] `has_front_matter(text: str) -> bool` - Add full docstring
- [ ] `is_archived(path: Path) -> bool` - Add full docstring
- [ ] `main()` - Add full docstring

**scripts/migrate_context_front_matter.py** (7 functions):
- [ ] `has_front_matter(...) -> bool`
- [ ] `read_manifest(...) -> dict`
- [ ] `parse_legacy_header(...) -> dict` - Add Args
- [ ] `sanitize_nodes(...) -> list`
- [ ] `to_front_matter(...) -> str`
- [ ] `remove_legacy_header(...) -> str` - Add Args
- [ ] `main()`

**scripts/sync_t12_manifest_owners.py** (3 functions):
- [ ] `is_archived(path: Path) -> bool`
- [ ] `now_iso() -> str`
- [ ] `main()`

### Priority 3: T1/T2 Owner Fix - 4 functions

**scripts/fix_t12_context_owners.py**:
- [ ] `find_front_matter_bounds(...) -> tuple`
- [ ] `patch_owner_in_fm(...) -> str`
- [ ] `get_tier_and_owner(...) -> tuple`
- [ ] Plus 1 more (from "and 3 more")

### Priority 4: CI/Quality Scripts - 3 functions

Already partially done, but need completion verification.

---

## Docstring Template (Copy-Paste Ready)

```python
def function_name(arg1: str, arg2: int = 0) -> bool:
    """Short imperative summary (<80 chars).

    Extended description explaining algorithm, design decisions,
    or important context (optional but recommended for complex logic).

    Args:
        arg1: Description with units/constraints/format.
        arg2: Description with default behavior. Defaults to 0.

    Returns:
        bool: What True means, what False means (observable effect).

    Raises:
        ValueError: When arg1 is empty or malformed.
        FileNotFoundError: When required config file missing.

    Example:
        >>> function_name("test", 42)
        True
        >>> function_name("")
        Traceback (most recent call last):
        ValueError: arg1 cannot be empty
    """
```

---

## Execution Strategy

### Fast Track (Recommended)

Use AI-assisted editing to batch-process similar functions:

1. **Group 1**: Simple predicates (`has_front_matter`, `is_archived`, `now_iso`)
   - Pattern: No args or simple boolean returns
   - Time: 5 minutes for all

2. **Group 2**: Parser/builder functions (`parse_legacy_header`, `to_front_matter`, `make_context_md`)
   - Pattern: String manipulation, dict building
   - Time: 10 minutes

3. **Group 3**: Main orchestrators (`main`, `validate_all_modules`)
   - Pattern: Complex workflows, multiple steps
   - Time: 15 minutes

4. **Group 4**: Inference/decision functions (`infer_capabilities`, `decide_quality_tier`)
   - Pattern: Multi-arg logic, weighted scoring
   - Time: 15 minutes

**Total Estimated Time**: 45-60 minutes for all 33 functions

---

## Validation Commands

```bash
# After editing each script, verify:
python3 -m py_compile scripts/generate_module_manifests.py
python3 -m py_compile scripts/validate_module_manifests.py
# ... etc

# Check docstring style
pydocstyle scripts/generate_module_manifests.py || true

# Final validation
python3 - <<'PY'
import ast
from pathlib import Path

scripts = [
    "scripts/generate_module_manifests.py",
    "scripts/validate_module_manifests.py",
    "scripts/context_coverage_bot.py",
    "scripts/migrate_context_front_matter.py",
    "scripts/sync_t12_manifest_owners.py",
    "scripts/fix_t12_context_owners.py",
]

missing = 0
for script in scripts:
    tree = ast.parse(Path(script).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            if not doc or ("Args:" not in doc and node.args.args):
                print(f"❌ {script}:{node.name} - incomplete docstring")
                missing += 1

if missing == 0:
    print("✅ All 33 functions have complete docstrings!")
else:
    print(f"⚠️  {missing} functions still need work")
PY
```

---

## Commit Strategy

After completing each priority group:

```bash
git add scripts/<modified_script>.py
git commit -m "docs(jules-j02): add function docstrings to <script_name>

- Added Args/Returns/Raises/Examples to X functions
- Functions: list_of_function_names
- Validated with pydocstyle and py_compile"
```

Final commit:
```bash
git add -A
git commit -m "docs(jules): complete J-02 function docstrings (33 functions across 6 critical scripts)

Problem:
- 33 functions in critical infrastructure scripts lacked complete docstrings
- Missing Args, Returns, Raises, and Examples sections
- Blocked 85%+ coverage target

Solution:
- Added Google-style docstrings to all 33 functions
- Organized by priority: manifests > migration > quality
- Validated with pydocstyle and ast parsing

Impact:
- Complete documentation for Phase 4 manifest generation
- Foundation for 85%+ interrogate coverage
- All critical scripts ready for production use

Related: #445 (J-06 completion tracker)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Notes

- Focus on **Priority 1** (manifest scripts) first - these are Phase 4 critical
- Use the template consistently for style uniformity
- Don't over-engineer - pragmatic, clear docs > perfect prose
- Examples are optional for simple functions but recommended for complex ones
