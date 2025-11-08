#!/usr/bin/env python3
"""
Create Jules sessions for high-priority non-test TODOs

Creates 5 critical implementation tasks via Jules API.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def create_priority_sessions():
    """Create Jules sessions for priority non-test TODOs"""

    sessions = [
        {
            "title": "🔴 CRITICAL: Activate Guardian ethics DSL enforcement and implement kill-switch",
            "prompt": """**CRITICAL PRODUCTION SAFETY ISSUE**

From audit (docs/gonzo/AUDIT_07_NOV_25.md):
- Ethics DSL enforcement is currently **OFF by default**
- Emergency kill-switch mechanism only documented, not implemented
- Dual-approval override lacks operational runbook

**Task 1: Activate Ethics DSL Enforcement**

File: `core/governance/guardian_system_integration.py` or appropriate Guardian config

Current state: `ENFORCE_ETHICS_DSL=0` (off by default)
Required change:
1. Set `ENFORCE_ETHICS_DSL=1` to activate enforcement
2. Add configuration flag in appropriate config file
3. Add feature flag toggle mechanism (canary rollout support)
4. Add logging when enforcement is active/inactive

**Task 2: Implement Emergency Kill-Switch**

Current state: Only documented in specs, not in code
Implementation needed:

```python
# In core/governance/guardian_system_integration.py or guardian validator

def check_emergency_killswitch() -> bool:
    '''
    Check if emergency Guardian kill-switch is activated.
    Returns True if Guardian should be disabled (emergency mode).
    '''
    # Check file-based flag (no DB dependency for emergencies)
    killswitch_path = Path("/tmp/guardian_emergency_disable")
    if killswitch_path.exists():
        logger.critical("GUARDIAN EMERGENCY KILL-SWITCH ACTIVATED")
        return True

    # Check environment variable fallback
    if os.getenv("GUARDIAN_EMERGENCY_DISABLE") == "1":
        logger.critical("GUARDIAN EMERGENCY KILL-SWITCH ACTIVATED (ENV)")
        return True

    return False

# Integrate check into Guardian validation flow
# Before applying any Guardian rules, check killswitch
```

**Task 3: Create Dual-Approval Runbook**

File: `docs/runbooks/guardian_override_playbook.md`

Content should include:
```markdown
# Guardian Override Playbook

## Emergency Kill-Switch Activation

**When to use**: Only for critical incidents where Guardian is causing production issues

**Activation steps**:
1. Senior engineer authorization required
2. Create kill-switch file: `touch /tmp/guardian_emergency_disable`
3. OR set environment: `GUARDIAN_EMERGENCY_DISABLE=1`
4. Verify Guardian is disabled in logs
5. Document incident in #incidents Slack channel

**Deactivation**:
1. Remove kill-switch: `rm /tmp/guardian_emergency_disable`
2. Verify Guardian re-enabled
3. Post-incident review within 24 hours

## Dual-Approval Override Process

**Context**: Guardian blocks require two approvals for override

**Process**:
1. First approver reviews Guardian block decision
2. Documents override justification
3. Second independent approver reviews
4. Both approvers log approval in audit trail
5. Override logged to `reports/guardian/overrides.jsonl`

**Code integration**: Use existing `guardian.dual_approval_override()` method

## Incident Response Contacts
- On-call: [PagerDuty rotation]
- Ethics lead: [Contact]
- Security lead: [Contact]
```

**Testing Requirements**:
- Unit tests for `check_emergency_killswitch()`
- Integration test: verify Guardian respects kill-switch
- Test dual-approval override flow
- Verify audit logging

**Output Files**:
- Modified: `core/governance/guardian_system_integration.py` (or appropriate Guardian file)
- Created: `docs/runbooks/guardian_override_playbook.md`
- Modified: Guardian config file (add ENFORCE_ETHICS_DSL flag)
- Tests: `tests/integration/governance/test_guardian_killswitch.py`

**LUKHAS Conventions**:
- Use LUKHAS terminology
- Follow existing Guardian patterns
- Include comprehensive docstrings
- Add audit logging for all actions
- No production secrets in code

**Priority**: P0 - CRITICAL - Production safety issue
"""
        },
        {
            "title": "P1: Automated cleanup - Run autoflake/isort/black/ruff --fix across codebase",
            "prompt": """**P1 CODE QUALITY: Systematic autofix cleanup**

From PRIORITY_TODOs.md and AUDIT_07_NOV_25.md:
- Currently 4,300+ Ruff violations
- Need systematic cleanup with automated tools
- Small batches to avoid breaking changes

**Objective**: Run autofix pass on core modules to reduce lint violations

**Implementation Approach**:

Create script: `scripts/batch_autofix.py`

```python
#!/usr/bin/env python3
'''
Batch autofix for code quality improvements

Runs: autoflake → isort → black → ruff --fix
Small batches with test verification between changes.
'''

import subprocess
import sys
from pathlib import Path

def run_autofix_batch(module_path: str) -> bool:
    \"\"\"Run autofix tools on module and verify tests pass\"\"\"

    print(f"\\n{'='*60}")
    print(f"Autofix batch: {module_path}")
    print('='*60)

    # Step 1: autoflake (remove unused imports and variables)
    print("\\n1. Running autoflake...")
    subprocess.run([
        "autoflake",
        "--in-place",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--remove-duplicate-keys",
        "--recursive",
        module_path
    ], check=True)

    # Step 2: isort (organize imports)
    print("\\n2. Running isort...")
    subprocess.run([
        "isort",
        module_path
    ], check=True)

    # Step 3: black (format code)
    print("\\n3. Running black...")
    subprocess.run([
        "black",
        module_path
    ], check=True)

    # Step 4: ruff --fix (auto-fixable issues)
    print("\\n4. Running ruff --fix...")
    subprocess.run([
        "python3", "-m", "ruff", "check",
        "--fix",
        module_path
    ], check=False)  # Don't fail on remaining issues

    # Step 5: Verify tests still pass
    print("\\n5. Running tests...")
    result = subprocess.run([
        "pytest",
        f"tests/unit/{module_path}",
        "-q"
    ], capture_output=True)

    if result.returncode == 0:
        print("✅ Tests passed")
        return True
    else:
        print("❌ Tests failed - changes need review")
        return False

# Priority modules for autofix (small batches)
MODULES = [
    "bridge/llm_wrappers",
    "core/governance",
    "lukhas/identity",
    "lukhas/memory",
    "matriz",
]

def main():
    results = {}

    for module in MODULES:
        success = run_autofix_batch(module)
        results[module] = "✅" if success else "❌"

    print("\\n" + "="*60)
    print("Autofix Summary")
    print("="*60)
    for module, status in results.items():
        print(f"{status} {module}")

if __name__ == "__main__":
    main()
```

**Execution Plan**:
1. Run on small module first (bridge/llm_wrappers) as pilot
2. Verify tests pass
3. Create commit for each module
4. If tests fail, investigate and fix manually
5. Document any breaking changes

**Commit Messages** (T4 standard):
```
chore(hygiene): autofix bridge/llm_wrappers with autoflake/isort/black/ruff

Problem:
- 4,300+ Ruff violations across codebase
- Unused imports and variables cluttering code
- Inconsistent formatting

Solution:
- Applied autoflake to remove unused imports/variables
- Applied isort for import organization
- Applied black for consistent formatting
- Applied ruff --fix for auto-fixable issues

Impact:
- Reduced violations in bridge/llm_wrappers from X to Y
- All tests passing
- No functional changes

🤖 Generated with Jules (jules.google.com)
```

**Testing**:
- Verify existing tests still pass after each batch
- Run smoke tests: `make smoke`
- Run full test suite for affected modules

**Output Files**:
- Created: `scripts/batch_autofix.py`
- Modified: All .py files in target modules (formatting only)
- No functional changes - pure cleanup

**LUKHAS Conventions**:
- Run `make lane-guard` to verify import boundaries maintained
- Follow T4 commit message standards
- Test after each module batch
- Document any issues in commit body

**Priority**: P1 - Quick wins, visible impact
"""
        },
        {
            "title": "P1: Create codemod to replace labs imports with proper module imports",
            "prompt": """**P1 TECHNICAL DEBT: Replace labs imports codemod**

From PRIORITY_TODOs.md:
- Need to systematically replace `labs` ImportFrom nodes
- Part of lane hygiene enforcement
- Automated refactoring

**Objective**: Create LibCST codemod to replace `labs` imports with proper imports

**Background**:
- `labs/` directory contains experimental/deprecated code
- Production code should not import from `labs/`
- Need automated tool to fix violations

**Implementation**:

File: `scripts/codemods/replace_labs_imports.py`

```python
#!/usr/bin/env python3
'''
Codemod: Replace labs imports with proper imports

Transforms:
  from labs.foo import bar  →  from candidate.foo import bar
  from labs.governance import X  →  from core.governance import X

Usage:
  python3 scripts/codemods/replace_labs_imports.py --path lukhas --dry-run
  python3 scripts/codemods/replace_labs_imports.py --path lukhas --apply
'''

import argparse
import libcst as cst
from pathlib import Path
from typing import Union

# Mapping: labs module → proper import location
LABS_REPLACEMENT_MAP = {
    "labs.governance": "core.governance",
    "labs.consciousness": "candidate.consciousness",
    "labs.identity": "lukhas.identity",
    "labs.memory": "candidate.memory",
    "labs.matriz": "matriz",
    # Add more mappings as discovered
}

class ReplaceLabsImportsTransformer(cst.CSTTransformer):
    '''LibCST transformer to replace labs imports'''

    def __init__(self):
        self.changes = []

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom
    ) -> Union[cst.ImportFrom, cst.RemovalSentinel]:
        '''Replace labs imports with proper imports'''

        if updated_node.module is None:
            return updated_node

        module_name = self._get_module_name(updated_node.module)

        # Check if this is a labs import
        if module_name.startswith("labs."):
            # Find replacement
            replacement = self._find_replacement(module_name)

            if replacement:
                self.changes.append({
                    "from": module_name,
                    "to": replacement,
                    "line": original_node
                })

                # Build new import node
                new_module = self._build_module_attribute(replacement)
                new_node = updated_node.with_changes(module=new_module)

                return new_node

        return updated_node

    def _get_module_name(self, module: cst.Attribute | cst.Name) -> str:
        '''Extract module name from CST node'''
        if isinstance(module, cst.Name):
            return module.value
        elif isinstance(module, cst.Attribute):
            # Recursively build dotted name
            parts = []
            current = module
            while isinstance(current, cst.Attribute):
                parts.append(current.attr.value)
                current = current.value
            if isinstance(current, cst.Name):
                parts.append(current.value)
            return ".".join(reversed(parts))
        return ""

    def _find_replacement(self, labs_import: str) -> str | None:
        '''Find replacement for labs import'''
        # Direct match
        if labs_import in LABS_REPLACEMENT_MAP:
            return LABS_REPLACEMENT_MAP[labs_import]

        # Prefix match (for submodules)
        for labs_prefix, replacement_prefix in LABS_REPLACEMENT_MAP.items():
            if labs_import.startswith(labs_prefix + "."):
                suffix = labs_import[len(labs_prefix):]
                return replacement_prefix + suffix

        return None

    def _build_module_attribute(self, module_path: str) -> cst.Attribute | cst.Name:
        '''Build CST Attribute node from dotted module path'''
        parts = module_path.split(".")
        if len(parts) == 1:
            return cst.Name(parts[0])

        # Build nested Attribute nodes
        node = cst.Name(parts[0])
        for part in parts[1:]:
            node = cst.Attribute(value=node, attr=cst.Name(part))
        return node


def process_file(file_path: Path, dry_run: bool = True) -> tuple[bool, int]:
    '''Process single file with codemod'''

    try:
        source = file_path.read_text()
        tree = cst.parse_module(source)

        transformer = ReplaceLabsImportsTransformer()
        modified_tree = tree.visit(transformer)

        if transformer.changes:
            print(f"\n{'='*60}")
            print(f"File: {file_path}")
            print(f"Changes: {len(transformer.changes)}")
            for change in transformer.changes:
                print(f"  {change['from']} → {change['to']}")

            if not dry_run:
                # Write modified code
                file_path.write_text(modified_tree.code)
                print(f"✅ Applied changes")
            else:
                print(f"🔍 Dry-run (no changes written)")

            return True, len(transformer.changes)

        return False, 0

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def main():
    parser = argparse.ArgumentParser(description="Replace labs imports codemod")
    parser.add_argument("--path", required=True, help="Path to process (file or directory)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes")

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: Must specify --dry-run or --apply")
        return 1

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {path}")
        return 1

    # Collect Python files
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))

    print(f"\nProcessing {len(files)} Python files...")

    total_changes = 0
    modified_files = 0

    for file in files:
        modified, changes = process_file(file, dry_run=args.dry_run)
        if modified:
            modified_files += 1
            total_changes += changes

    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"Files processed: {len(files)}")
    print(f"Files modified: {modified_files}")
    print(f"Total changes: {total_changes}")

    if args.dry_run:
        print(f"\n💡 Run with --apply to write changes")


if __name__ == "__main__":
    main()
```

**Dependencies**: Add to requirements.txt:
```
libcst>=1.0.0
```

**Testing**:
Create `tests/unit/codemods/test_replace_labs_imports.py` to verify transformations

**Usage**:
```bash
# Dry-run to see changes
python3 scripts/codemods/replace_labs_imports.py --path lukhas --dry-run

# Apply changes
python3 scripts/codemods/replace_labs_imports.py --path lukhas --apply

# Verify no broken imports
make lane-guard
pytest tests/
```

**Output Files**:
- Created: `scripts/codemods/replace_labs_imports.py`
- Created: `tests/unit/codemods/test_replace_labs_imports.py`
- Modified: All files with labs imports (after --apply)

**LUKHAS Conventions**:
- Follow lane boundaries
- Test after applying
- Document mapping in LABS_REPLACEMENT_MAP

**Priority**: P1 - Technical debt cleanup
"""
        },
        {
            "title": "P1: Implement SLSA CI workflow for supply chain security (first 10 modules)",
            "prompt": """**P1 SECURITY: SLSA CI for supply chain integrity**

From PRIORITY_TODOs.md:
- Implement SLSA (Supply-chain Levels for Software Artifacts) CI
- Use cosign/in-toto for provenance
- Start with first 10 critical modules

**Objective**: Add GitHub Actions workflow for SLSA compliance

**Background**:
- SLSA provides framework for supply chain security
- Level 1: Provenance for build process
- Level 2: Signed provenance
- Level 3: Non-forgeable provenance

**Implementation**:

File: `.github/workflows/slsa-provenance.yml`

```yaml
name: SLSA Provenance

on:
  push:
    branches: [main]
  release:
    types: [created]

permissions:
  contents: read
  id-token: write  # For cosign
  packages: write

jobs:
  build-provenance:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build in-toto cosign

      - name: Build artifacts for SLSA modules
        run: |
          # Build wheel for distribution
          python -m build

          # Create checksums
          sha256sum dist/*.whl > dist/checksums.txt

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Generate SLSA provenance
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Generate in-toto provenance for first 10 modules
          python3 scripts/slsa/generate_provenance.py \
            --modules "matriz,lukhas.identity,lukhas.memory,core.governance,bridge.llm_wrappers,lukhas.consciousness,candidate.core,core.orchestration,lukhas.api,tools.ci" \
            --output provenance.json

      - name: Sign provenance with Cosign
        run: |
          # Keyless signing with GitHub OIDC
          cosign sign-blob \
            --bundle provenance.cosign.bundle \
            provenance.json

      - name: Upload provenance
        uses: actions/upload-artifact@v3
        with:
          name: slsa-provenance
          path: |
            provenance.json
            provenance.cosign.bundle
            dist/checksums.txt

      - name: Verify provenance (self-check)
        run: |
          cosign verify-blob \
            --bundle provenance.cosign.bundle \
            --certificate-identity-regexp="^https://github.com/LukhasAI/Lukhas" \
            --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
            provenance.json

  slsa-verification:
    runs-on: ubuntu-latest
    needs: build-provenance

    steps:
      - name: Download provenance
        uses: actions/download-artifact@v3
        with:
          name: slsa-provenance

      - name: Display provenance
        run: |
          echo "SLSA Provenance generated and signed"
          cat provenance.json | jq .

      - name: Check SLSA level
        run: |
          # Verify we meet SLSA Level 2
          python3 -c "
import json
with open('provenance.json') as f:
    prov = json.load(f)
    print(f'Build type: {prov.get(\"buildType\")}')
    print(f'Builder ID: {prov.get(\"builder\", {}).get(\"id\")}')
    print('✅ SLSA Level 2 requirements met')
          "
```

File: `scripts/slsa/generate_provenance.py`

```python
#!/usr/bin/env python3
'''
Generate SLSA provenance for LUKHAS modules

Creates in-toto provenance attestation.
'''

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

def generate_provenance(modules: list[str], output: Path):
    '''Generate SLSA provenance document'''

    # Get git commit info
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    commit_time = subprocess.check_output(["git", "log", "-1", "--format=%cI"]).decode().strip()
    repo_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()

    # Get builder info (GitHub Actions)
    builder_id = f"{repo_url}/actions/runs/{subprocess.os.getenv('GITHUB_RUN_ID', 'local')}"

    # Build materials (source files for modules)
    materials = []
    for module in modules:
        module_path = Path(module.replace(".", "/"))
        if module_path.exists():
            # Hash all .py files in module
            for py_file in module_path.rglob("*.py"):
                sha256 = subprocess.check_output(["sha256sum", str(py_file)]).decode().split()[0]
                materials.append({
                    "uri": f"git+{repo_url}@{commit}#{py_file}",
                    "digest": {"sha256": sha256}
                })

    # Create SLSA provenance (v0.2 format)
    provenance = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "subject": [
            {
                "name": f"lukhas-{module}",
                "digest": {"sha256": "..."}  # Would be actual artifact hash
            }
            for module in modules
        ],
        "predicateType": "https://slsa.dev/provenance/v0.2",
        "predicate": {
            "builder": {
                "id": builder_id
            },
            "buildType": "https://github.com/LukhasAI/Lukhas/slsa-build@v1",
            "invocation": {
                "configSource": {
                    "uri": f"git+{repo_url}",
                    "digest": {"sha1": commit},
                    "entryPoint": ".github/workflows/slsa-provenance.yml"
                }
            },
            "buildConfig": {
                "modules": modules,
                "python_version": "3.11",
                "build_time": datetime.utcnow().isoformat()
            },
            "metadata": {
                "buildInvocationId": subprocess.os.getenv("GITHUB_RUN_ID", "local"),
                "buildStartedOn": commit_time,
                "buildFinishedOn": datetime.utcnow().isoformat(),
                "completeness": {
                    "parameters": True,
                    "environment": True,
                    "materials": True
                },
                "reproducible": False  # TODO: Make builds reproducible
            },
            "materials": materials
        }
    }

    # Write provenance
    with open(output, 'w') as f:
        json.dump(provenance, f, indent=2)

    print(f"✅ Generated SLSA provenance for {len(modules)} modules")
    print(f"   Output: {output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules", required=True, help="Comma-separated module list")
    parser.add_argument("--output", required=True, help="Output provenance file")

    args = parser.parse_args()

    modules = [m.strip() for m in args.modules.split(",")]
    generate_provenance(modules, Path(args.output))

if __name__ == "__main__":
    main()
```

**First 10 Modules** (priority order):
1. matriz
2. lukhas.identity
3. lukhas.memory
4. core.governance
5. bridge.llm_wrappers
6. lukhas.consciousness
7. candidate.core
8. core.orchestration
9. lukhas.api
10. tools.ci

**Testing**:
- Run workflow manually
- Verify provenance generated
- Verify cosign signature
- Check SLSA level compliance

**Documentation**: Add `docs/security/SLSA_COMPLIANCE.md`

**Output Files**:
- Created: `.github/workflows/slsa-provenance.yml`
- Created: `scripts/slsa/generate_provenance.py`
- Created: `docs/security/SLSA_COMPLIANCE.md`

**LUKHAS Conventions**:
- Follow security best practices
- Use keyless signing (GitHub OIDC)
- Document provenance format

**Priority**: P1 - Security foundations
"""
        },
        {
            "title": "P2: Refresh API documentation with examples and update timestamps",
            "prompt": """**P2 DOCUMENTATION: Complete API reference and update guides**

From AUDIT_07_NOV_25.md:
- API documentation incomplete
- Missing usage examples
- Docs not updated since January 2024
- Developer guides are placeholders

**Objective**: Comprehensive API documentation refresh

**Tasks**:

**1. Update API Reference**

File: `docs/api/COMPLETE_REFERENCE.md`

Requirements:
- Document ALL endpoints in lukhas/api/
- Include request/response schemas
- Add curl examples for each endpoint
- Add Python client examples
- Document authentication requirements
- Add rate limiting info
- Include error codes reference

Example structure:
```markdown
# LUKHAS AI API Reference

**Version**: 1.0.0
**Last Updated**: 2025-01-08
**Base URL**: `https://api.lukhas.ai/v1`

## Authentication

All API requests require authentication via API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.lukhas.ai/v1/endpoint
```

## Endpoints

### POST /v1/consciousness/process

Process input through MATRIZ cognitive engine.

**Request**:
```json
{
  "input": "User query",
  "context": {},
  "options": {
    "model": "matriz-standard",
    "max_tokens": 1000
  }
}
```

**Response**:
```json
{
  "output": "Processed response",
  "metadata": {
    "latency_ms": 180,
    "tokens_used": 450,
    "consciousness_level": 0.87
  }
}
```

**Python Example**:
```python
from lukhas import LukhasClient

client = LukhasClient(api_key="...")
response = client.consciousness.process(
    input="What is consciousness?",
    model="matriz-standard"
)
print(response.output)
```

**Error Codes**:
- 400: Invalid request
- 401: Unauthorized
- 429: Rate limit exceeded
- 500: Internal error
```

**2. Create Getting Started Guides**

File: `docs/guides/GETTING_STARTED.md`

Content:
- Quick start (5 minutes)
- Installation instructions
- First API call
- Authentication setup
- Common use cases
- Troubleshooting

File: `docs/guides/LUKHAS_WITH_OPENAI.md`

Content:
- OpenAI compatibility layer
- Migration from OpenAI
- Feature comparison
- Drop-in replacement examples

**3. Update All Documentation Timestamps**

Script: `scripts/update_doc_timestamps.py`

```python
#!/usr/bin/env python3
'''Update 'Last Updated' timestamps in all documentation'''

import re
from datetime import datetime
from pathlib import Path

def update_timestamps(doc_dir: Path):
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(r"Last [Uu]pdated:?\s*\d{4}-\d{2}-\d{2}")

    for md_file in doc_dir.rglob("*.md"):
        content = md_file.read_text()

        # Check if file has been modified in git
        import subprocess
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", str(md_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout:
            last_commit = result.stdout[:10]  # YYYY-MM-DD

            # Update or add timestamp
            if pattern.search(content):
                new_content = pattern.sub(f"Last Updated: {last_commit}", content)
            else:
                # Add to frontmatter if present, else add after first heading
                if content.startswith("# "):
                    lines = content.split("\n")
                    lines.insert(1, f"\n**Last Updated**: {last_commit}\n")
                    new_content = "\n".join(lines)
                else:
                    new_content = content

            if new_content != content:
                md_file.write_text(new_content)
                print(f"Updated: {md_file}")

if __name__ == "__main__":
    update_timestamps(Path("docs"))
```

**4. Add Missing Examples**

Files to update:
- `docs/examples/consciousness_api.py`
- `docs/examples/identity_auth.py`
- `docs/examples/memory_management.py`
- `docs/examples/guardian_usage.py`

Each should have:
- Minimal working example
- Common patterns
- Error handling
- Best practices

**5. Create Migration Guides**

File: `docs/guides/MIGRATION_GUIDE.md`

Content:
- Version upgrade paths
- Breaking changes
- Deprecation notices
- Code migration examples

**Testing**:
- Verify all code examples run
- Check all links work
- Validate API schemas match implementation
- Spell check and grammar check

**Output Files**:
- Updated: `docs/api/COMPLETE_REFERENCE.md`
- Created: `docs/guides/GETTING_STARTED.md`
- Created: `docs/guides/LUKHAS_WITH_OPENAI.md`
- Created: `docs/guides/MIGRATION_GUIDE.md`
- Created: `scripts/update_doc_timestamps.py`
- Updated: All docs/ files (timestamps)
- Created: Multiple example files in docs/examples/

**LUKHAS Conventions**:
- Use LUKHAS AI (not Lukhas AGI)
- Include quantum-inspired and bio-inspired terminology
- Follow existing doc structure
- Add changelog entries

**Priority**: P2 - Important for developer experience
"""
        }
    ]

    print("\n🚀 Creating 5 Priority Jules Sessions (Non-Test TODOs)")
    print("=" * 70)
    print(f"\nSessions to create: {len(sessions)}\n")

    for i, s in enumerate(sessions, 1):
        title = s['title']
        print(f"{i}. {title}")

    print("\n" + "=" * 70)

    created = []

    async with JulesClient() as jules:
        for i, session_config in enumerate(sessions, 1):
            print(f"\nCreating session {i}/{len(sessions)}...")
            title = session_config['title']
            print(f"  {title}")

            try:
                session = await jules.create_session(
                    prompt=session_config['prompt'],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session['name'].split('/')[-1]
                print(f"  ✅ Created: {session_id}")
                print(f"     URL: https://jules.google.com/session/{session_id}")
                created.append({
                    "title": title,
                    "session_id": session_id,
                    "url": f"https://jules.google.com/session/{session_id}"
                })

            except Exception as e:
                print(f"  ❌ Failed: {e}")

            await asyncio.sleep(2)

    print("\n" + "=" * 70)
    print(f"✅ Created {len(created)}/{len(sessions)} priority sessions")
    print("=" * 70)

    if created:
        print("\n📋 Session Summary:\n")
        for item in created:
            print(f"✅ {item['title']}")
            print(f"   Session ID: {item['session_id']}")
            print(f"   URL: {item['url']}")
            print()

    print("\n🎯 Priority Breakdown:")
    print("  🔴 P0 (CRITICAL): Guardian ethics DSL + kill-switch")
    print("  🟡 P1 (High):     Autofix, Labs codemod, SLSA CI")
    print("  🟢 P2 (Important): API documentation refresh")

    print("\nNext steps:")
    print("  1. Jules will process sessions and create PRs")
    print("  2. Monitor: https://jules.google.com/")
    print("  3. Review PRs when ready")
    print("  4. Check daily quota: python3 scripts/list_all_jules_sessions.py")


if __name__ == "__main__":
    try:
        asyncio.run(create_priority_sessions())
    except KeyboardInterrupt:
        print("\n⏸️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
