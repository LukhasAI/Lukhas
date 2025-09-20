# LUKHAS AI Connector Access Guide

Guide for AI assistants and automated systems accessing the LUKHAS repository.

## Authentication & Permissions

### GitHub Access Requirements

#### Minimum Required Scopes
- **`repo:read`** - Read repository content and metadata
- **`issues:read`** - Read issues for context and history
- **`pull_requests:read`** - Access PR discussions and code reviews
- **`actions:read`** - Read CI/CD status and workflow results

#### Optional Enhanced Scopes
- **`discussions:read`** - Access GitHub Discussions for broader context
- **`wiki:read`** - Read repository wiki content
- **`packages:read`** - Access published packages and containers

### Authentication Methods

#### GitHub App (Recommended)
```yaml
# Preferred for organizational access
permissions:
  contents: read
  issues: read
  pull_requests: read
  actions: read
  metadata: read
```

#### Personal Access Token (PAT)
```bash
# For individual developer use
export GITHUB_TOKEN="ghp_your_token_here"

# Verify access
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/LukhasAI/Lukhas
```

## Repository Structure for AI Connectors

### Entry Points (Start Here)
```
LUKHAS/
├── README.md                    # Project overview and quick start
├── ARCHITECTURE.md              # System architecture and design
├── SEARCH_MAP.md               # Search patterns and navigation guide
├── ENV_VARS.md                 # Environment variables catalog
└── docs/CONNECTOR_ACCESS.md    # This file
```

### Core Production Code
```
lukhas/                         # Production-ready modules
├── core/                      # GLYPH engine, Constellation Framework
├── identity/                  # Authentication and authorization
├── memory/                    # Memory systems and persistence
├── orchestration/             # Brain Hub coordination
└── trace/                     # Distributed tracing
```

### Experimental & Research
```
candidate/                      # Experimental features
├── consciousness/             # Consciousness research
├── memory/                    # Advanced memory systems
├── governance/                # Governance frameworks
└── core/                      # Core system experiments
```

### Configuration & Operations
```
.env.example                   # Environment template
pyproject.toml                 # Python configuration
requirements.txt               # Pinned dependencies
monitoring/                    # Prometheus config and alerts
samples/                       # Sample logs and data
```

## Key Files for Understanding System

### Essential Reading (Priority 1)
1. **`README.md`** - Project overview and Constellation Framework
2. **`ARCHITECTURE.md`** - Complete system architecture
3. **`SEARCH_MAP.md`** - How to find specific functionality
4. **`ENV_VARS.md`** - All configuration options

### System Behavior (Priority 2)
1. **`samples/logs/`** - Real system behavior examples
2. **`monitoring/alert-rules.yml`** - What the system monitors
3. **`tests/smoke/test_entrypoints.py`** - Core API validation
4. **`.github/CODEOWNERS`** - Domain expertise mapping

### Code Organization (Priority 3)
1. **`lukhas/core/__init__.py`** - Core module exports
2. **`MATRIZ/__init__.py`** - Symbolic processing system
3. **`candidate/core/ethics/`** - Guardian system implementation
4. **`pyproject.toml`** - Dependencies and tool configuration

## Common Connector Use Cases

### Code Analysis & Review
```bash
# Find all Guardian/ethics related code
rg -n "guardian|ethics|safety" --type py

# Find API endpoints
rg -n "@app\.|@router\." --type py

# Find test patterns
find tests/ -name "test_*.py" | head -10
```

### Understanding System Health
```bash
# Check recent commits
git log --oneline -10

# Check CI status
gh run list --limit 5

# View configuration
cat pyproject.toml | grep -A 10 "\[tool\."
```

### Finding Specific Functionality
```bash
# Use the search map
grep -A 5 "Guardian" SEARCH_MAP.md
grep -A 5 "MATRIZ" SEARCH_MAP.md

# Find modules by pattern
find . -name "*consciousness*" -type f
find . -name "*identity*" -type f
```

## Rate Limits & Best Practices

### GitHub API Rate Limits
- **Authenticated**: 5,000 requests/hour
- **Search API**: 30 requests/minute
- **GraphQL**: 5,000 points/hour

### Connector Best Practices

#### Efficient Repository Access
```python
# Good: Use specific file paths
files_to_read = [
    "ARCHITECTURE.md",
    "SEARCH_MAP.md",
    "lukhas/core/__init__.py",
    "tests/smoke/test_entrypoints.py"
]

# Avoid: Reading entire directory trees
# Don't recursively read all files
```

#### Respect Repository Boundaries
```python
# Read-only operations only
operations = [
    "read_file",
    "search_code",
    "list_directory",
    "get_git_info"
]

# Avoid write operations without explicit permission
avoid = [
    "create_file",
    "modify_file",
    "create_pr",
    "push_commits"
]
```

### Caching Recommendations
```python
# Cache these for 1 hour
cache_1h = [
    "ARCHITECTURE.md",
    "README.md",
    "ENV_VARS.md"
]

# Cache these for 15 minutes
cache_15m = [
    "git log",
    "file listings",
    "module exports"
]

# Don't cache (always fresh)
no_cache = [
    "CI status",
    "recent commits",
    "active PRs"
]
```

## Security Considerations

### Sensitive Areas (Handle with Care)
- **`/ethics/`** - Guardian system code
- **`/identity/`** - Authentication systems
- **`/governance/`** - Policy and compliance
- **`.env.example`** - Environment templates (safe)
- **`monitoring/`** - System observability

### Never Access
- **`.env`** - Actual environment files (if present)
- **`secrets/`** - Any secrets directories
- **`*.key`** - Private key files
- **`credentials.*`** - Credential files

### Safe Patterns
```bash
# Safe: Read configuration templates
cat .env.example

# Safe: Read documentation
cat docs/architecture/SECURITY_ARCHITECTURE.md

# Safe: Read sample logs (already redacted)
cat samples/logs/guardian_decisions.jsonl
```

## Error Handling & Fallbacks

### Common Issues & Solutions

#### File Not Found
```python
# Graceful handling for missing files
try:
    content = read_file("optional_file.md")
except FileNotFoundError:
    # Check alternative locations
    alternatives = [
        "docs/optional_file.md",
        "README.md",  # Fallback to main docs
    ]
```

#### Rate Limit Exceeded
```python
# Implement exponential backoff
import time

def api_call_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** i
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

#### Large Repository Handling
```python
# Use targeted searches instead of full scans
patterns = [
    "*.py",     # Python files only
    "*.md",     # Documentation only
    "*.yml",    # Configuration only
]

# Avoid scanning these
exclude = [
    ".git/",
    "__pycache__/",
    ".venv/",
    "node_modules/",
    "htmlcov/"
]
```

## Integration Examples

### Read System Architecture
```python
def understand_lukhas_system():
    # Start with overview
    readme = read_file("README.md")
    architecture = read_file("ARCHITECTURE.md")

    # Understand search patterns
    search_map = read_file("SEARCH_MAP.md")

    # Check environment options
    env_vars = read_file("ENV_VARS.md")

    return {
        "overview": readme,
        "architecture": architecture,
        "search_patterns": search_map,
        "configuration": env_vars
    }
```

### Find Specific Functionality
```python
def find_guardian_system():
    # Use search map first
    search_map = read_file("SEARCH_MAP.md")
    guardian_pattern = extract_pattern(search_map, "Guardian")

    # Then search specific locations
    guardian_files = search_files(
        pattern="guardian|ethics",
        paths=["candidate/core/ethics/", "lukhas/"]
    )

    return guardian_files
```

### Check System Health
```python
def check_system_status():
    # Recent commits
    commits = git_log(limit=5)

    # CI status
    ci_status = get_workflow_status()

    # Configuration health
    config = read_file("pyproject.toml")

    return {
        "recent_activity": commits,
        "ci_status": ci_status,
        "configuration": config
    }
```

## Support & Contact

### Documentation Issues
- File issues with label `area:documentation`
- Tag `@architecture-team` for structural questions

### Access Issues
- File issues with label `area:infrastructure`
- Tag `@platform-team` for access problems

### System Understanding
- Use `SEARCH_MAP.md` patterns first
- Check `samples/logs/` for behavior examples
- Review `ARCHITECTURE.md` for design decisions

---

*This guide ensures AI connectors can effectively understand and interact with the LUKHAS repository while respecting security boundaries and rate limits.*