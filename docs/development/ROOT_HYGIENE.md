# Root Directory Hygiene System

Automated enforcement to keep the repository root clean and organized.

## Problem

Over time, documentation files, session notes, status reports, and temporary files accumulate at the repository root, making it difficult to:
- Navigate the repository
- Find important files
- Maintain consistent organization
- Onboard new developers

## Solution

Three-layer automated hygiene system:

### 1. `.root-allowlist` - Configuration File

Defines exactly what's allowed at repository root:
- Essential project files (README.md, SECURITY.md, etc.)
- AI agent context files (gemini.md, lukhas_context.md)
- Project structure directories (docs/, tests/, lukhas/, etc.)
- Build/config files (Makefile, pyproject.toml, etc.)

**Location**: `.root-allowlist`

### 2. Validation Scripts

#### `scripts/validate_root_hygiene.py`
- **Purpose**: Checks all files/directories at root against allowlist
- **Strictness**: Permissive (allows legitimate project structure)
- **Usage**: `python3 scripts/validate_root_hygiene.py`

#### `scripts/validate_root_docs.py`
- **Purpose**: Blocks NEW documentation files from root
- **Strictness**: Strict (only allows essential docs)
- **Usage**: `python3 scripts/validate_root_docs.py`
- **Allowed docs**:
  - README.md
  - SECURITY.md
  - LICENSE / LICENSE.md
  - CHANGELOG.md
  - CONTRIBUTING.md
  - gemini.md (AI context)
  - lukhas_context.md (AI context)
  - claude.me (AI context)

### 3. Enforcement

#### Pre-Commit Hook
Automatically runs on every commit to block unauthorized files:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-root-docs
      name: Validate root documentation hygiene
      entry: python3 scripts/validate_root_docs.py
      language: system
      pass_filenames: false
      always_run: true
      stages: [commit]
```

#### Makefile Targets
```bash
make validate-root           # Check all root files
make validate-root-docs      # Check documentation files (strict)
make validate-root-all       # Run both validators
```

## Documentation Organization

When the validator rejects a file, move it to the appropriate subdirectory:

| File Type | Destination Directory | Examples |
|-----------|----------------------|----------|
| Agent guides | `docs/agents/` | AGENTS.md, AGENT_TASK_TEMPLATE.md |
| Session notes | `docs/sessions/` | SESSION_*.md |
| Status reports | `docs/project_status/` | *_STATUS.md, *_SUMMARY.md |
| Test docs | `docs/testing/` | TEST_*.md, SMOKE_*.md |
| Security docs | `docs/security/` | SECURITY_*.md |
| MATRIZ docs | `docs/matriz/` | MATRIZ_*.md |
| Bridge docs | `docs/bridge/` | BRIDGE_*.md |
| Codex docs | `docs/codex/` | CODEX_*.md |
| Audit reports | `docs/audits/` | AUDIT_*.md, *_AUDIT.md |
| General docs | `docs/` | *.md (general documentation) |

## Common Workflows

### For AI Agents

When creating new documentation:
```bash
# ❌ DON'T: Create at root
cat > AGENT_NEW_FEATURE.md <<EOF
...
EOF

# ✅ DO: Create in appropriate subdirectory
cat > docs/agents/AGENT_NEW_FEATURE.md <<EOF
...
EOF
```

### For Developers

If pre-commit blocks your commit:
```bash
# 1. Check what file was rejected
python3 scripts/validate_root_docs.py

# 2. Move file to appropriate directory
git mv <rejected-file> docs/<appropriate-subdir>/

# 3. Update any links/references if needed

# 4. Retry commit
git commit
```

### Adding Exceptions

If a file legitimately needs to be at root:

1. Edit `.root-allowlist`
2. Add the filename or pattern
3. Add comment explaining why it's at root
4. Test: `make validate-root-all`
5. Commit the allowlist change

Example:
```
# Essential project metadata
zenodo.metadata.json  # DOI registration metadata

# New essential file
NEW_ESSENTIAL_FILE.md  # Brief reason why it's at root
```

## Maintenance

### Review Periodically

```bash
# Check what's currently allowed
cat .root-allowlist

# Check what's actually at root
ls -la | grep -v "^d" | wc -l
```

### Tighten Over Time

As the project matures, you can:
1. Remove temporary patterns from allowlist
2. Move grandfathered files to proper locations
3. Update the allowlist to be more restrictive

### Monitoring

Track root directory size over time:
```bash
# Count files at root (excluding directories)
find . -maxdepth 1 -type f | wc -l

# Should trend downward over time
```

## Benefits

1. **Prevents Clutter**: Blocks new documentation at root before it accumulates
2. **Maintains Organization**: Forces consistent structure
3. **Improves Discoverability**: Related files grouped together
4. **Git History**: Uses `git mv` to preserve file history
5. **Automated**: No manual policing needed
6. **Self-Documenting**: Clear error messages guide developers

## Troubleshooting

### "Why was my commit blocked?"
The pre-commit hook detected an unauthorized documentation file at root.
Run `python3 scripts/validate_root_docs.py` to see which file.

### "How do I bypass for an emergency?"
```bash
git commit --no-verify -m "emergency fix"
```
Then immediately file an issue to properly organize the file.

### "Can I add a legitimate file to root?"
Yes, but only if it's truly essential (like a new LICENSE variant or official project metadata). Edit `.root-allowlist` and add a comment explaining why.

## Related

- [Documentation Structure](../README.md)
- [Development Workflow](README.md)
- [Pre-Commit Hooks](../../.pre-commit-config.yaml)
- [Root Allowlist](../../.root-allowlist)
