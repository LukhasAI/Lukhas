#!/usr/bin/env python3
"""
Create Batch 2 of Jules sessions - Priority organized
Covers: Critical (P0), High (P1), Medium (P2), Low (P3) tasks
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient

# Session definitions organized by priority
SESSIONS = {
    "CRITICAL": [
        {
            "title": "🔴 P0: Fix RUF012 Mutable Class Defaults (119 violations)",
            "prompt": """**CRITICAL CODE QUALITY: Fix RUF012 Mutable Class Attribute Defaults**

**Objective**: Eliminate all 119 instances of mutable class attribute defaults, a common source of subtle bugs.

**Issue**: GitHub Issue #860
- **Priority**: P0/P1
- **Error Code**: RUF012
- **Count**: 119 violations
- **Risk**: High - can cause state leakage between instances

**Problem Pattern**:
```python
class MyClass:
    items = []  # WRONG: Shared across all instances!
    config = {}  # WRONG: Shared mutable dict!
```

**Correct Pattern**:
```python
from dataclasses import dataclass, field

@dataclass
class MyClass:
    items: list = field(default_factory=list)
    config: dict = field(default_factory=dict)

# OR using __init__:
class MyClass:
    def __init__(self):
        self.items = []
        self.config = {}
```

**Task**:
1. Run `python3 -m ruff check --select RUF012 . --output-format=json > /tmp/ruf012_violations.json`
2. Analyze all 119 violations
3. For each violation:
   - If class uses dataclasses: Convert to `field(default_factory=...)`
   - If regular class: Move initialization to `__init__`
   - If class constant: Add type hint and document as class-level constant
4. Verify no behavioral changes with tests
5. Run full test suite to ensure no regressions

**Safety Requirements**:
- Run pytest on modified files
- Check for any tests that depend on shared state
- Verify all instances get independent default values
- Document any intentional class-level constants

**Expected Output**:
- All 119 RUF012 violations eliminated
- All tests passing
- Git commit with detailed explanation
- PR ready for review

**Commit Message**:
```
fix(hygiene): eliminate 119 RUF012 mutable class attribute defaults

Problem:
- 119 classes using mutable default arguments
- Risk of state leakage between instances
- Common source of subtle bugs in production

Solution:
- Convert dataclasses to use field(default_factory=...)
- Move list/dict initialization to __init__ for regular classes
- Document intentional class constants with type hints

Impact:
- Eliminates entire class of potential bugs
- More predictable instance initialization
- Follows Python best practices

Safety: All tests pass, no behavioral changes
```

**Priority**: P0 - Critical code quality issue
""",
        },
        {
            "title": "🔴 P0: Fix CVE-2025-8869 pip Security Vulnerability",
            "prompt": """**CRITICAL SECURITY: Address CVE-2025-8869 pip Arbitrary File Overwrite**

**Objective**: Mitigate CVE-2025-8869 security vulnerability in pip

**Issue**: GitHub Issue #399
- **CVE**: CVE-2025-8869
- **Severity**: Critical
- **Impact**: Arbitrary file overwrite vulnerability
- **Status**: Open since 2025-10-15

**Task**:
1. Research CVE-2025-8869 details and affected pip versions
2. Check current pip version: `pip --version`
3. Identify remediation steps:
   - Upgrade pip to safe version
   - Update requirements.txt constraints
   - Check for any workarounds needed
4. Test upgrade in isolated environment
5. Update CI/CD to enforce safe pip version
6. Document the vulnerability and mitigation

**Verification**:
- Run `pip-audit` after upgrade
- Verify no regression in package installations
- Check that all requirements still install correctly
- Update security documentation

**Deliverables**:
- Upgraded pip to safe version
- Updated requirements files with version constraints
- CI/CD pipeline updated
- Security advisory documented in docs/security/
- PR with detailed security impact explanation

**Commit Message**:
```
security(deps): upgrade pip to fix CVE-2025-8869

Security Impact:
- CVE-2025-8869: Arbitrary file overwrite vulnerability
- Severity: Critical
- Affected: pip versions <X.Y.Z

Solution:
- Upgraded pip to version X.Y.Z
- Added version constraint in requirements
- Updated CI to enforce safe version

Verification:
✅ pip-audit clean
✅ All requirements install correctly
✅ No regressions in CI/CD
```

**Priority**: P0 - Critical security vulnerability
""",
        },
        {
            "title": "🔴 P0: Resolve PR #805 M1 Branch Conflicts",
            "prompt": """**CRITICAL CI: Resolve PR #805 M1 Branch Conflicts**

**Objective**: Unblock PR #805 which has merge conflicts preventing CI/CD

**Issue**: GitHub Issue #859
- **Priority**: P1
- **PR**: #805
- **Status**: Blocked by branch conflicts
- **Created**: 2025-11-02

**Task**:
1. Fetch latest main branch changes
2. Review PR #805 to understand the changes
3. Identify conflicting files
4. Resolve conflicts carefully:
   - Preserve PR #805 intent
   - Integrate main branch changes
   - Test conflict resolution
5. Update PR with resolved conflicts
6. Verify CI passes

**Steps**:
```bash
# Check out PR branch
gh pr checkout 805

# Fetch latest main
git fetch origin main

# Attempt merge
git merge origin/main

# Resolve conflicts in each file
# (Review carefully - preserve both sets of changes where applicable)

# Test locally
make test
make lint

# Push resolution
git push
```

**Verification**:
- All conflicts resolved
- CI passes (lint, type check, tests)
- PR ready for review
- No regressions from main branch

**Deliverables**:
- PR #805 updated with conflict resolution
- All CI checks passing
- Comment on PR explaining resolution approach

**Priority**: P0 - Blocking CI/CD pipeline
""",
        },
    ],
    "HIGH": [
        {
            "title": "🟠 P1: Quick Wins - Small Error Types Cleanup (Issue #946)",
            "prompt": """**HIGH PRIORITY: Quick Wins Lint Cleanup**

**Objective**: Fix small, low-risk linter violations for quick code quality improvement

**Issue**: GitHub Issue #946
- **Priority**: P1
- **Type**: Quick wins / Low-hanging fruit
- **Labels**: good first issue, codex, lint, hygiene

**Task**: Address simple, mechanical linting violations that can be auto-fixed:
1. Run `ruff check --select E,W,F --output-format=json . > /tmp/quick_wins.json`
2. Focus on auto-fixable issues:
   - E501: Line too long (can often auto-format)
   - F841: Unused variables
   - E402: Module level import not at top
   - W291, W293: Whitespace issues
3. Apply fixes in batches by error code
4. Verify no behavioral changes

**Approach**:
```bash
# Auto-fix safe violations
ruff check --fix --select E501,F841,W291,W293 .

# Format code
ruff format .

# Verify
make test
```

**Safety**:
- Only fix mechanical violations
- No logic changes
- Run tests after each batch
- Commit by error code for easy review

**Expected Output**:
- 50-100+ violations fixed
- All tests passing
- Clean git commits by error type

**Commit Message Template**:
```
chore(lint): fix E501 line length violations in X files

- Applied ruff auto-fix for line length
- No logic changes, formatting only
- Tests pass
```

**Priority**: P1 - Quick code quality improvement
""",
        },
        {
            "title": "🟠 P1: Implement ProviderRegistry Infrastructure (Issue #821)",
            "prompt": """**HIGH PRIORITY: Create ProviderRegistry Infrastructure**

**Objective**: Build ProviderRegistry to enable dynamic component loading and decouple lanes

**Issue**: GitHub Issue #821
- **Priority**: High
- **Status**: Blocks Copilot Task 01
- **Labels**: infrastructure, blocks-tasks

**Background**:
The codebase needs a registry pattern to:
- Enable lane isolation (candidate/ vs lukhas/ vs core/)
- Allow optional feature loading
- Support plugin architecture
- Prevent circular import issues

**Task**:
1. Design ProviderRegistry interface:
```python
class ProviderRegistry:
    '''Central registry for optional providers and components'''

    def register(self, name: str, provider: Any, namespace: Optional[str] = None) -> None:
        '''Register a provider'''

    def get(self, name: str, namespace: Optional[str] = None, default: Any = None) -> Any:
        '''Get provider with fallback'''

    def has(self, name: str, namespace: Optional[str] = None) -> bool:
        '''Check if provider exists'''

    def list_providers(self, namespace: Optional[str] = None) -> list[str]:
        '''List all registered providers'''
```

2. Implement thread-safe registry
3. Add namespace support for lane isolation
4. Create registration decorators
5. Add comprehensive tests
6. Document usage patterns

**File Structure**:
```
core/providers/
├── __init__.py
├── registry.py          # Main ProviderRegistry
├── decorators.py        # @register_provider, etc.
└── tests/
    ├── test_registry.py
    └── test_decorators.py
```

**Usage Example**:
```python
from core.providers import registry

# Register provider
@registry.register_provider('openai', namespace='llm')
class OpenAIProvider:
    pass

# Use with fallback
provider = registry.get('openai', namespace='llm', default=FallbackProvider())
```

**Testing**:
- Test registration and retrieval
- Test namespace isolation
- Test thread safety
- Test fallback behavior
- Test decorator patterns

**Expected Output**:
- Complete ProviderRegistry implementation
- 90%+ test coverage
- Documentation with examples
- Unblocks Issue #821 dependent tasks

**Commit Message**:
```
feat(core): implement ProviderRegistry infrastructure

Problem:
- Need dynamic component loading
- Lane isolation requires registry pattern
- Circular imports from direct coupling

Solution:
- Thread-safe ProviderRegistry with namespaces
- Registration decorators for easy use
- Fallback support for optional providers

Impact:
- Enables lane boundary enforcement
- Supports plugin architecture
- Reduces coupling between modules

Tests: 90%+ coverage, all tests pass
Unblocks: Issue #821, Copilot Task 01
```

**Priority**: P1 - Blocks multiple tasks
""",
        },
        {
            "title": "🟠 P1: Fix Import Organization E402 and UP035 (Issue #945)",
            "prompt": """**HIGH PRIORITY: Phase 2 Import Organization**

**Objective**: Fix E402 (module import not at top) and UP035 (deprecated typing) violations

**Issue**: GitHub Issue #945
- **Priority**: P1
- **Type**: Lint cleanup, import organization
- **Labels**: codex, lint, hygiene

**E402 Pattern (Module import not at top)**:
```python
# WRONG
import sys
sys.path.insert(0, '...')
import some_module  # E402: import not at top

# CORRECT
import sys
import some_module  # Put at top
sys.path.insert(0, '...')  # Runtime manipulation after imports
```

**UP035 Pattern (Deprecated typing imports)**:
```python
# WRONG (Python 3.9+)
from typing import List, Dict, Tuple

def process(items: List[str]) -> Dict[str, int]:
    pass

# CORRECT (Python 3.9+)
def process(items: list[str]) -> dict[str, int]:
    pass
```

**Task**:
1. Run `ruff check --select E402,UP035 --output-format=json .`
2. Count violations and prioritize high-impact files
3. Fix E402 violations:
   - Move imports to top of file
   - Keep sys.path manipulation AFTER imports if needed
   - Use importlib for dynamic imports instead of sys.path
4. Fix UP035 violations:
   - Replace typing.List → list
   - Replace typing.Dict → dict
   - Replace typing.Tuple → tuple
   - Replace typing.Set → set
   - Keep typing.Optional, typing.Union (still needed)

**Automated Approach**:
```bash
# Fix UP035 automatically
ruff check --fix --select UP035 .

# Fix E402 requires manual review (can affect behavior)
ruff check --select E402 --output-format=grouped .
# Then fix each file carefully
```

**Safety**:
- Test after each file change
- E402 fixes may affect runtime behavior
- UP035 is safe (just type hint modernization)

**Expected Output**:
- All E402 violations fixed
- All UP035 violations fixed
- Tests passing
- Modern Python 3.9+ type hints throughout

**Commit Messages**:
```
refactor(imports): modernize type hints (UP035)

- Replace typing.List/Dict/Tuple with builtin equivalents
- Python 3.9+ supports builtin generic types
- No runtime changes, type hints only

Files changed: ~50+
```

```
fix(imports): move module imports to top (E402)

- Reorganized imports to follow PEP 8
- Moved sys.path manipulation after imports where safe
- Replaced runtime path manipulation with importlib where applicable

Safety: All tests pass, no behavioral changes
```

**Priority**: P1 - Code organization and modernization
""",
        },
        {
            "title": "🟠 P1: Implement Security TODOs - Authentication and Validation",
            "prompt": """**HIGH PRIORITY: Implement Critical Security TODOs**

**Objective**: Address open security-related TODO items from migration

**Issues**: #552, #581, #582, #584, #600, #611, #619, #623, #627, #629
- **Priority**: P1
- **Type**: Security implementation
- **Created**: 2025-10-28 (TODO migration)

**Key Security TODOs to Address**:

1. **#552, #584: Implement Authentication**
   - Location: Security modules, admin endpoints
   - Task: Add proper authentication layer
   - Use: JWT, API keys, or WebAuthn

2. **#581: Real Authentication Challenge (WebAuthn/Device Key)**
   - Implement WebAuthn for passwordless auth
   - Add device key registration
   - Create challenge-response flow

3. **#582: Audit Λ-trace for Security Logging**
   - Review Lambda-trace logging for security events
   - Ensure sensitive operations are logged
   - Add tamper-proof audit trail

4. **#600: Validate Against Token Store**
   - Implement token validation
   - Check against revocation list
   - Add token expiry checking

5. **#611, #619, #623: Security Infrastructure**
   - Create security monitor
   - Implement security mesh
   - Add security validation layers

6. **#627, #629: Guardian Compliance**
   - Address security regression
   - Implement identity verification for guardian
   - Ensure constitutional AI compliance

**Approach**:
1. Audit current security posture
2. Prioritize by risk (authentication first, monitoring second)
3. Implement in phases:
   - Phase 1: Authentication layer (JWT/API keys)
   - Phase 2: WebAuthn/device keys
   - Phase 3: Audit logging enhancement
   - Phase 4: Token validation
   - Phase 5: Security monitoring
4. Test thoroughly with security scenarios
5. Document security architecture

**Expected Output**:
- Authentication system implemented
- WebAuthn support added
- Security audit logging complete
- Token validation working
- All security TODOs closed
- Security documentation updated

**Testing**:
- Unit tests for each security component
- Integration tests for auth flows
- Security penetration testing
- Audit log verification

**Commit Message**:
```
security(auth): implement authentication and validation layer

Problem:
- Multiple security TODOs open since Oct 2024
- No centralized authentication
- Missing WebAuthn support
- Insufficient audit logging

Solution:
- Implemented JWT/API key authentication
- Added WebAuthn device key support
- Enhanced Λ-trace security logging
- Token validation against store
- Security monitoring infrastructure

Impact:
- Closes 10 security issues (#552, #581, #582, #584, #600, #611, #619, #623, #627, #629)
- Production-ready authentication
- Comprehensive audit trail
- Guardian constitutional compliance

Security-Impact: Major - Addresses authentication gaps
Tests: Full security test suite passes
```

**Priority**: P1 - Critical security requirements
""",
        },
        {
            "title": "🟠 P1: Implement Lazy Loading Refactors (5 Copilot Tasks)",
            "prompt": """**HIGH PRIORITY: Implement Lazy Loading Pattern Across Components**

**Objective**: Add `__getattr__` lazy loading to 5 key modules to reduce import overhead and enable optional dependencies

**Issues**: #814, #815, #816, #817, #818 (Copilot Tasks 01-08)
- **Priority**: High/Medium
- **Type**: Performance refactoring
- **Pattern**: Lazy loading with `__getattr__`

**Tasks**:

**1. Issue #814: Lazy-load labs in gpt_colony_orchestrator.py**
- Priority: High
- File: `provider/gpt_colony_orchestrator.py`
- Pattern: Make labs imports lazy to avoid circular deps

**2. Issue #815: Enhance lazy loading in evidence_collection.py**
- Priority: High
- File: `observability/evidence_collection.py`
- Pattern: Lazy load observability backends

**3. Issue #816: Add lazy dream engine loader**
- Priority: Medium
- File: `matriz/dream_engine.py` (or similar)
- Pattern: Load dream engine only when used

**4. Issue #817: Create lazy proxy for tag exports**
- Priority: Medium
- File: `tags/__init__.py` or `tags/registry.py`
- Pattern: Lazy load tag registry

**5. Issue #818: Add lazy proxy for governance features**
- Priority: High
- File: `governance/__init__.py`
- Pattern: Lazy load guardian, ethics modules

**Implementation Pattern**:
```python
# In __init__.py or module file
def __getattr__(name: str):
    '''Lazy load submodules and heavy dependencies'''

    if name == 'HeavyModule':
        from .heavy_module import HeavyModule
        globals()[name] = HeavyModule
        return HeavyModule

    elif name == 'OptionalFeature':
        try:
            from .optional_feature import OptionalFeature
            globals()[name] = OptionalFeature
            return OptionalFeature
        except ImportError:
            # Return stub or None for missing optional deps
            return None

    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
```

**Benefits**:
- Faster import times
- Reduced memory footprint
- Optional dependency support
- Breaks circular import cycles

**Testing**:
- Verify modules still importable
- Test optional dependency graceful degradation
- Measure import time improvement
- Check no behavioral changes

**Expected Output**:
- All 5 modules using lazy loading
- Import times reduced by 20-50%
- All tests passing
- Documentation of lazy patterns

**Commit Messages** (one PR or separate):
```
refactor(performance): add lazy loading to 5 core modules

Problem:
- Heavy imports slow down startup
- Circular dependency issues
- Optional features always loaded

Solution:
- Added __getattr__ lazy loading pattern
- Deferred heavy imports until first use
- Graceful degradation for optional deps

Impact:
- 30% faster import times
- Reduced memory footprint
- Breaks circular import cycles

Closes: #814, #815, #816, #817, #818
Tests: All tests pass, import benchmarks improved
```

**Priority**: P1 - Performance and architecture improvement
""",
        },
    ],
    "MEDIUM": [
        {
            "title": "🟡 P2: Implement Memory Module TODOs (indexer, pgvector, observability)",
            "prompt": """**MEDIUM PRIORITY: Complete Memory Module Implementation**

**Objective**: Implement placeholder TODOs in memory module for production readiness

**Files with TODOs**:
1. `memory/indexer.py` - Embedding provider integration
2. `memory/backends/pgvector_store.py` - Database operations
3. `memory/observability.py` - Prometheus metrics

**Task 1: memory/indexer.py**
Current TODOs:
- Line 17: Plug in actual embedding providers
- Line 20: Call provider, cache results
- Line 36: Detect duplicates by fingerprint in metadata

Implementation:
```python
# Before (stub):
def get_embedding(self, text: str) -> list[float]:
    # TODO: call provider, cache results
    return [0.0] * 384

# After:
def get_embedding(self, text: str) -> list[float]:
    '''Get embedding from provider with caching'''
    cache_key = hashlib.sha256(text.encode()).hexdigest()

    if cache_key in self._cache:
        return self._cache[cache_key]

    # Use configured provider (OpenAI, Anthropic, local, etc)
    embedding = self.provider.embed(text)
    self._cache[cache_key] = embedding
    return embedding
```

**Task 2: memory/backends/pgvector_store.py**
Current TODOs:
- Line 29: Implement upsert on id, return id
- Line 30: SQL INSERT ... ON CONFLICT
- Line 34: Chunked COPY for performance
- Line 39: Apply filters to search
- Line 48: SELECT COUNT(*) for stats

Implementation:
```python
def upsert(self, doc: dict) -> str:
    '''Upsert document with conflict resolution'''
    query = '''
    INSERT INTO {table} (id, embedding, metadata, text)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        embedding = EXCLUDED.embedding,
        metadata = EXCLUDED.metadata,
        text = EXCLUDED.text,
        updated_at = NOW()
    RETURNING id
    '''.format(table=self.table)

    cursor = self.conn.execute(query, (
        doc['id'],
        doc['embedding'],
        json.dumps(doc['metadata']),
        doc['text']
    ))
    return cursor.fetchone()[0]
```

**Task 3: memory/observability.py**
Current TODOs:
- Line 14: Initialize actual prometheus_client metrics
- Line 19: Record histogram observations
- Line 24: Record counter increments

Implementation:
```python
from prometheus_client import Histogram, Counter

class MemoryMetrics:
    def __init__(self):
        self.query_duration = Histogram(
            'memory_query_duration_ms',
            'Memory query latency in milliseconds',
            ['operation']
        )
        self.query_count = Counter(
            'memory_query_total',
            'Total memory queries',
            ['operation', 'status']
        )

    def record_duration(self, operation: str, duration_ms: float):
        self.query_duration.labels(operation=operation).observe(duration_ms)

    def record_query(self, operation: str, success: bool):
        status = 'success' if success else 'error'
        self.query_count.labels(operation=operation, status=status).inc()
```

**Testing**:
- Unit tests for each function
- Integration tests with real PostgreSQL (or docker)
- Performance benchmarks
- Observability validation

**Expected Output**:
- All memory/ TODOs implemented
- Production-ready memory subsystem
- Tests passing with 85%+ coverage
- Metrics exporting correctly

**Commit Message**:
```
feat(memory): implement production-ready memory subsystem

Problem:
- Memory module has placeholder TODOs
- No real embedding provider integration
- Missing database operations
- No observability metrics

Solution:
- Integrated embedding providers (OpenAI, local)
- Implemented pgvector upsert, search, bulk insert
- Added Prometheus metrics
- Caching layer for embeddings

Impact:
- Production-ready memory system
- Vector search working
- Full observability
- Performance optimized

Tests: 85%+ coverage, integration tests pass
Performance: <50ms p95 for vector search
```

**Priority**: P2 - Feature completeness
""",
        },
        {
            "title": "🟡 P2: Clean Up Test Import TODOs",
            "prompt": """**MEDIUM PRIORITY: Clean Up Test Import Pattern TODOs**

**Objective**: Remove or fix the repeated TODO comments in test files about importlib

**Pattern Found** (many test files):
```python
import module_name  # TODO: module_name; consider using importlib...
```

**Files Affected** (sample):
- agents/tests/test_agents_unit.py
- vocabulary_refresh_data/tests/test_vocabulary_refresh_data_unit.py
- alerts/tests/test_alerts_integration.py
- delegation_reports/tests/test_delegation_reports_unit.py
- Many more...

**Analysis**:
These TODOs suggest converting to importlib.import_module for dynamic imports, but:
1. Static imports are fine for test files
2. No real benefit to using importlib here
3. Makes code less readable
4. Pattern is repeated ~50+ times

**Decision Options**:

**Option A: Remove TODOs** (Recommended)
- Simply delete the TODO comments
- Static imports are appropriate for tests
- No action needed beyond cleanup

**Option B: Use try/except for Optional Modules**
```python
try:
    import optional_module
except ImportError:
    optional_module = None
    pytestmark = pytest.mark.skip("optional_module not available")
```

**Option C: Use importlib (only if truly dynamic)**
```python
import importlib
module = importlib.import_module('module_name')
```

**Task**:
1. Review all test files with this TODO pattern
2. Determine if any truly need dynamic imports
3. For most cases: Simply remove the TODO comment
4. For optional deps: Add try/except with skip marker
5. Clean up with automated script:

```bash
# Find all occurrences
ruff check --select F401 tests/ --output-format=json

# Simple cleanup (remove TODO comment)
find tests/ -name "*.py" -type f -exec sed -i '' 's/  # TODO: .* consider using importlib.*//' {} +
```

**Expected Output**:
- 50+ TODO comments removed
- Tests still passing
- Optional import handling added where needed
- Cleaner test files

**Commit Message**:
```
chore(tests): remove unnecessary importlib TODO comments

Problem:
- 50+ test files have TODO about using importlib
- Static imports are appropriate for tests
- TODOs add noise without value

Solution:
- Removed TODO comments from test imports
- Added try/except for truly optional modules
- Tests use standard import patterns

Impact:
- Cleaner, more readable tests
- No functional changes
- Better handling of optional dependencies

Tests: All tests still pass
```

**Priority**: P2 - Code cleanup
""",
        },
        {
            "title": "🟡 P2: Implement MATRIZ PQC Migration to Dilithium2",
            "prompt": """**MEDIUM PRIORITY: Migrate MATRIZ Checkpoint Signing to Post-Quantum Cryptography**

**Objective**: Migrate checkpoint signing from classical crypto to Dilithium2 (NIST PQC standard)

**Issue**: GitHub Issue #490 - MATRIZ-007
- **Priority**: P1
- **Type**: Security, Future-proofing
- **Algorithm**: Dilithium2 (NIST FIPS 204)

**Background**:
Post-Quantum Cryptography (PQC) protects against quantum computer attacks. MATRIZ checkpoints need quantum-resistant signatures for long-term security.

**Task**:
1. Install liboqs (Open Quantum Safe library)
```bash
# macOS
brew install liboqs

# Python wrapper
pip install liboqs-python
```

2. Implement Dilithium2 signing for checkpoints:
```python
from oqs import Signature

class PQCCheckpointSigner:
    def __init__(self):
        self.sig = Signature('Dilithium2')
        self.public_key = self.sig.generate_keypair()

    def sign_checkpoint(self, checkpoint_data: bytes) -> bytes:
        '''Sign checkpoint with Dilithium2'''
        return self.sig.sign(checkpoint_data)

    def verify_checkpoint(self, checkpoint_data: bytes, signature: bytes) -> bool:
        '''Verify Dilithium2 signature'''
        return self.sig.verify(checkpoint_data, signature, self.public_key)
```

3. Update MATRIZ checkpoint serialization:
```python
# Add PQC signature to checkpoint
checkpoint = {
    'data': matrix_state,
    'timestamp': utc_now(),
    'signature_algorithm': 'Dilithium2',
    'signature': pqc_signer.sign_checkpoint(serialized_data)
}
```

4. Maintain backward compatibility:
```python
def verify_checkpoint(checkpoint: dict) -> bool:
    '''Verify checkpoint with PQC or legacy crypto'''
    algo = checkpoint.get('signature_algorithm', 'classical')

    if algo == 'Dilithium2':
        return pqc_verifier.verify(checkpoint)
    else:
        # Legacy verification
        return classical_verifier.verify(checkpoint)
```

5. CI Integration (Issue #492):
```yaml
# .github/workflows/pqc-tests.yml
- name: Install liboqs
  run: |
    brew install liboqs  # macOS runner
    pip install liboqs-python

- name: Test PQC signing
  run: pytest tests/security/test_pqc_signing.py
```

**Testing**:
- Unit tests for signing/verification
- Performance benchmarks (Dilithium2 is fast)
- Backward compatibility tests
- CI integration tests

**Security Considerations**:
- Key management (secure key storage)
- Key rotation policy
- Migration path for old checkpoints
- Quantum threat timeline (10-20 years)

**Expected Output**:
- Dilithium2 signing implemented
- MATRIZ checkpoints PQC-protected
- Backward compatibility maintained
- CI running PQC tests
- Documentation updated

**Commit Message**:
```
security(matriz): migrate checkpoint signing to Dilithium2 PQC

Problem:
- Classical crypto vulnerable to quantum attacks
- Need future-proof checkpoint signatures
- MATRIZ checkpoints have long lifetime

Solution:
- Implemented Dilithium2 (NIST FIPS 204) signing
- Backward compatible verification
- CI integration with liboqs

Impact:
- Quantum-resistant checkpoint signatures
- Future-proof MATRIZ security
- Maintains compatibility with existing checkpoints

Security-Impact: High - Protects against quantum threats
Tests: Full PQC test suite passing
Closes: #490 (MATRIZ-007)
Related: #492 (CI provisioning)
```

**Priority**: P2 - Important security enhancement (not urgent)
""",
        },
    ],
    "LOW": [
        {
            "title": "🟢 P3: Improve Documentation - Manifest Coverage (Issue #436)",
            "prompt": """**LOW PRIORITY: Achieve 99% Manifest Coverage**

**Objective**: Create 363 missing module manifests to reach 99% documentation coverage

**Issue**: GitHub Issue #436
- **Priority**: P3
- **Type**: Documentation enhancement
- **Target**: 99% manifest coverage
- **Missing**: 363 manifests

**Background**:
Module manifests (`MANIFEST.md` or `README.md`) provide quick reference for developers:
- Module purpose
- Key components
- Usage examples
- Dependencies
- Testing info

**Task**:
1. Identify modules without manifests:
```bash
# Find Python modules
find . -type f -name "__init__.py" -not -path "./.venv/*" | xargs dirname > /tmp/all_modules.txt

# Find existing manifests
find . -name "MANIFEST.md" -o -name "README.md" | grep -v ".venv" > /tmp/existing_manifests.txt

# Diff to find missing
comm -23 <(sort /tmp/all_modules.txt) <(sort /tmp/existing_manifests.txt) > /tmp/missing_manifests.txt
```

2. Generate manifest template:
```markdown
# Module: {module_name}

## Purpose
Brief description of what this module does.

## Key Components
- `component1.py`: Description
- `component2.py`: Description

## Usage
\```python
from {module_name} import Component

# Example usage
comp = Component()
result = comp.process()
\```

## Dependencies
- Core: List core dependencies
- Optional: List optional dependencies

## Testing
\```bash
pytest tests/unit/{module_name}/
\```

## Status
- **Lane**: candidate | core | lukhas
- **Stability**: experimental | beta | stable
- **Coverage**: X%
```

3. Automate manifest generation:
```python
# Script to generate manifests from code inspection
import ast
import os

def generate_manifest(module_path):
    # Parse __init__.py
    # Extract docstrings
    # List components
    # Generate manifest
    pass
```

4. Prioritize by importance:
   - P1: Public API modules (lukhas/)
   - P2: Core modules (core/)
   - P3: Experimental (candidate/)

**Automation Approach**:
- Use AST to parse module structure
- Extract docstrings for descriptions
- Generate component lists automatically
- Human review and enhancement

**Expected Output**:
- 363 new module manifests
- 99% coverage achieved
- Consistent documentation format
- Improved developer onboarding

**Commit Message**:
```
docs(coverage): add 363 module manifests for 99% coverage

Problem:
- Many modules lack documentation
- Hard for new developers to understand structure
- No quick reference for modules

Solution:
- Generated manifests for 363 modules
- Automated manifest creation from code
- Consistent format across all modules

Impact:
- 99% manifest coverage achieved
- Better developer experience
- Easier onboarding
- Clear module boundaries

Closes: #436
```

**Priority**: P3 - Documentation improvement (not blocking)
""",
        },
        {
            "title": "🟢 P3: Improve Security Posture Score (Issue #360)",
            "prompt": """**LOW PRIORITY: Improve Security Posture Score from 35/100 to >80/100**

**Objective**: Address security posture alerts and improve overall security score

**Issue**: GitHub Issue #360
- **Priority**: P3 (monitoring/improvement)
- **Current Score**: 35.0/100
- **Target Score**: >80/100
- **Created**: 2025-10-08

**Security Posture Components**:
1. **Dependency Security**: Known vulnerabilities
2. **Code Security**: SAST findings (Bandit, Semgrep)
3. **Secrets Management**: Hardcoded secrets
4. **Authentication**: Auth mechanisms
5. **Audit Logging**: Security event logging
6. **Access Control**: RBAC, permissions
7. **Encryption**: Data at rest/transit

**Task**:
1. Audit current security posture:
```bash
# Run security scans
bandit -r . -f json -o security_scan.json
pip-audit
semgrep --config auto .
gitleaks detect
```

2. Address findings by category:
   - **Critical**: Fix immediately
   - **High**: Fix in current sprint
   - **Medium**: Schedule for next sprint
   - **Low**: Track for future improvement

3. Implement missing security controls:
   - Add API authentication
   - Implement RBAC
   - Enhance audit logging
   - Encrypt sensitive data
   - Add rate limiting
   - Implement CORS policies

4. Automate security monitoring:
```yaml
# .github/workflows/security-posture.yml
name: Security Posture Check
on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  push:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit
        run: bandit -r . -f json -o bandit-report.json
      - name: Run pip-audit
        run: pip-audit
      - name: Calculate Security Score
        run: python scripts/calculate_security_score.py
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        run: |
          gh pr comment ${{ github.event.number }} \\
            --body "Security Score: $(cat security_score.txt)"
```

5. Document security improvements:
   - Update docs/security/POSTURE.md
   - Create security runbooks
   - Document incident response

**Metrics to Track**:
- CVE count: 0
- Bandit findings: <10 medium or higher
- Secrets exposed: 0
- Auth coverage: 100% of endpoints
- Audit coverage: 100% of sensitive operations
- Encryption: 100% of sensitive data

**Expected Output**:
- Security score >80/100
- All critical/high findings addressed
- Automated security monitoring
- Security documentation complete
- CI/CD security gates in place

**Commit Message**:
```
security(posture): improve security score from 35 to 85

Problem:
- Security posture score below threshold (35/100)
- Multiple security gaps identified
- No automated security monitoring

Solution:
- Fixed all critical/high security findings
- Implemented missing security controls:
  * API authentication and RBAC
  * Enhanced audit logging
  * Data encryption at rest/transit
  * Rate limiting and CORS
- Added automated security monitoring to CI/CD

Impact:
- Security score: 35 → 85 (+50 points)
- CVE count: X → 0
- All API endpoints authenticated
- Full audit trail for sensitive operations
- Continuous security monitoring

Security-Impact: Major - Comprehensive security improvements
Closes: #360
```

**Priority**: P3 - Continuous improvement (not blocking deployment)
""",
        },
    ],
}


async def create_batch2_sessions():
    """Create batch 2 of Jules sessions across all priority levels"""

    print("\n" + "="*80)
    print("🚀 JULES SESSION BATCH 2: PRIORITY-ORGANIZED TODO DELEGATION")
    print("="*80)
    print("\nCreating sessions across priority levels:")
    print("  🔴 CRITICAL (P0): 3 sessions")
    print("  🟠 HIGH (P1): 5 sessions")
    print("  🟡 MEDIUM (P2): 3 sessions")
    print("  🟢 LOW (P3): 2 sessions")
    print(f"\n  TOTAL: {sum(len(s) for s in SESSIONS.values())} sessions")
    print("\n" + "="*80 + "\n")

    created_sessions = []

    async with JulesClient() as jules:
        for priority, sessions in SESSIONS.items():
            priority_icon = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }[priority]

            print(f"\n{priority_icon} {priority} Priority Sessions:")
            print("-" * 70)

            for session_config in sessions:
                try:
                    print(f"\n📝 Creating: {session_config['title']}")

                    session = await jules.create_session(
                        prompt=session_config['prompt'],
                        source_id="sources/github/LukhasAI/Lukhas",
                        automation_mode="AUTO_CREATE_PR"
                    )

                    session_id = session['name'].split('/')[-1]
                    created_sessions.append({
                        'title': session_config['title'],
                        'session_id': session_id,
                        'priority': priority
                    })

                    print(f"✅ Created: {session_id}")
                    print(f"   URL: https://jules.google.com/session/{session_id}")

                except Exception as e:
                    print(f"❌ Failed: {e}")
                    continue

                # Brief delay between sessions
                await asyncio.sleep(1)

    # Summary
    print("\n" + "="*80)
    print("📊 BATCH 2 SUMMARY")
    print("="*80)

    by_priority = {}
    for session in created_sessions:
        priority = session['priority']
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(session)

    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if priority in by_priority:
            sessions = by_priority[priority]
            icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[priority]
            print(f"\n{icon} {priority}: {len(sessions)} sessions created")
            for s in sessions:
                print(f"   • {s['title']}")
                print(f"     ID: {s['session_id']}")

    print(f"\n✅ Total Created: {len(created_sessions)} sessions")
    print(f"🎯 Remaining Daily Quota: ~{100 - 11 - len(created_sessions)}/100")

    print("\n" + "="*80)
    print("📋 NEXT STEPS")
    print("="*80)
    print("\n1. Monitor sessions: python3 scripts/jules_session_helper.py list")
    print("2. Check for PRs: gh pr list --author 'google-labs-jules[bot]'")
    print("3. Approve plans if needed: python3 scripts/jules_session_helper.py approve SESSION_ID")
    print("4. Review PRs as they arrive: gh pr view PR_NUMBER")
    print("\n" + "="*80 + "\n")

    return created_sessions


if __name__ == "__main__":
    try:
        asyncio.run(create_batch2_sessions())
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
