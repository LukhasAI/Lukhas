#!/usr/bin/env python3
"""
Create GitHub issues for all 786 bridge gaps, grouped by directory.
"""
import subprocess
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(".")

def get_bridge_gaps():
    """Run find_bridge_gaps.py and parse output."""
    result = subprocess.run(
        ["python3", "scripts/find_bridge_gaps.py"],
        capture_output=True,
        text=True
    )

    gaps_by_dir = defaultdict(list)
    current_dir = None

    for line in result.stdout.splitlines():
        if "/ needs these modules:" in line:
            current_dir = line.split("/")[0].strip()
        elif line.strip().startswith("- "):
            module = line.strip()[2:]
            if current_dir:
                gaps_by_dir[current_dir].append(module)

    return gaps_by_dir

def create_issue(title, body, dry_run=False):
    """Create a GitHub issue."""
    if dry_run:
        print(f"[DRY RUN] Would create: {title}")
        print(f"  Modules: {body[:100]}...")
        return None

    cmd = [
        "gh", "issue", "create",
        "--repo", "LukhasAI/Lukhas",
        "--title", title,
        "--body", body
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        issue_url = result.stdout.strip()
        print(f"✅ Created: {issue_url}")

        # Tag @codex
        issue_num = issue_url.split("/")[-1]
        subprocess.run([
            "gh", "issue", "comment", issue_num,
            "--repo", "LukhasAI/Lukhas",
            "--body", "@codex Please review and implement bridge exports for these modules."
        ])
        return issue_url
    else:
        print(f"❌ Failed: {result.stderr}")
        return None

def create_batch_issue(dir_name, modules, batch_num=None):
    """Create issue for a batch of modules in a directory."""
    batch_suffix = f" (Batch {batch_num})" if batch_num else ""
    title = f"Bridge Gap: {dir_name}/* modules{batch_suffix}"

    body = f"""# Bridge Export Gap: {dir_name}/* modules

**Directory:** `{dir_name}/`
**Modules needing bridge exports:** {len(modules)}
**Part of:** MATRIZ Flattening Audit & Bridge Remediation Campaign (#880)

---

## Modules to Export

"""

    for module in sorted(modules):
        # Check if module file exists
        module_path = ROOT / "labs" / dir_name / f"{module}.py"
        exists = "✅" if module_path.exists() else "⚠️"
        body += f"- {exists} `{module}`\n"

    body += f"""
---

## Implementation Pattern

For each module, add to `{dir_name}/__init__.py`:

```python
# Bridge export for {dir_name}.MODULE_NAME
try:
    from labs.{dir_name} import MODULE_NAME
except ImportError:
    def MODULE_NAME(*args, **kwargs):
        '''Stub for MODULE_NAME.'''
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "MODULE_NAME" not in __all__:
    __all__.append("MODULE_NAME")
```

---

## Verification

After adding exports:

```bash
# Compile check
python3 -m py_compile {dir_name}/__init__.py

# Test import
python3 -c "from {dir_name} import MODULE_NAME; print('✅ Import successful')"

# Re-run smoke tests
pytest --collect-only -m "smoke" 2>&1 | grep "ERROR" | wc -l
```

---

## Acceptance Criteria

- [ ] All modules exported in `{dir_name}/__init__.py`
- [ ] Bridge file compiles without errors
- [ ] Imports work from test files
- [ ] Collection error count reduced

---

**Reference:**
- Root cause: `BRIDGE_GAP_ANALYSIS.md`
- Example pattern: `consciousness/dream/expand/__init__.py` (lines 90-144)
- Gap finder: `scripts/find_bridge_gaps.py`
"""

    return title, body

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Don't actually create issues")
    parser.add_argument("--limit", type=int, help="Limit number of issues created")
    parser.add_argument("--batch-size", type=int, default=50, help="Max modules per issue")
    args = parser.parse_args()

    print("🔍 Finding bridge gaps...")
    gaps_by_dir = get_bridge_gaps()

    print(f"📊 Found gaps in {len(gaps_by_dir)} directories")
    print(f"📦 Total modules: {sum(len(m) for m in gaps_by_dir.values())}")
    print()

    issues_created = []
    total_count = 0

    for dir_name, modules in sorted(gaps_by_dir.items()):
        # Split large directories into batches
        if len(modules) > args.batch_size:
            batches = [modules[i:i+args.batch_size] for i in range(0, len(modules), args.batch_size)]
            for batch_num, batch in enumerate(batches, 1):
                title, body = create_batch_issue(dir_name, batch, batch_num)
                issue_url = create_issue(title, body, args.dry_run)
                if issue_url:
                    issues_created.append((title, issue_url))

                total_count += 1
                if args.limit and total_count >= args.limit:
                    break
        else:
            title, body = create_batch_issue(dir_name, modules)
            issue_url = create_issue(title, body, args.dry_run)
            if issue_url:
                issues_created.append((title, issue_url))

            total_count += 1
            if args.limit and total_count >= args.limit:
                break

        if args.limit and total_count >= args.limit:
            break

    print()
    print(f"✅ Created {len(issues_created)} issues")

    # Write summary
    summary_file = ROOT / "BRIDGE_ISSUES_CREATED.md"
    with summary_file.open("w") as f:
        f.write("# Bridge Gap Issues Created\n\n")
        f.write(f"**Total:** {len(issues_created)} issues\n\n")
        for title, url in issues_created:
            f.write(f"- [{title}]({url})\n")

    print(f"📝 Summary written to {summary_file}")

if __name__ == "__main__":
    main()
