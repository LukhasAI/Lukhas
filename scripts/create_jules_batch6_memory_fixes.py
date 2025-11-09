#!/usr/bin/env python3
"""
Jules Batch 6: Memory Subsystem Code Quality Fixes
===================================================

Critical fixes for labs/memory/ code quality issues discovered via automated analysis.

**Issues to Fix**:
1. Import typo: `fromfromfromcandidate` → `candidate` (4 files)
2. Duplicate logger definitions (194 occurrences across 183 files)
3. Undefined logger references (log_init_fallback, _init_log)
4. Inconsistent logging patterns

**Expected Impact**:
- Fix 4 import errors preventing module loading
- Clean up 194 duplicate logger definitions
- Standardize logging across 183 files
- Improve code maintainability and reduce technical debt

Created: 2025-01-08 (Batch 6 - Memory Subsystem Cleanup)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient

BATCH6_SESSIONS = [
    {
        "title": "🔴 P0: Fix Critical Import Typo `fromfromfromcandidate` (4 files)",
        "prompt": """**CRITICAL BUG FIX: Correct Import Typo Preventing Module Loading**

**📚 CONTEXT FILES - READ THESE FIRST**:
- `labs/memory/lukhas_context.md` - Memory subsystem architecture and patterns
- `labs/memory/claude.me` - Memory domain context (alternative format)
- `CLAUDE.md` - Project standards and lane architecture
- `labs/memory/systems/memory_legacy/README.md` - Legacy memory system docs (if exists)

**🛠️ TOOLKIT**:
- Grep/search across `labs/memory/` for patterns
- Read all 4 affected files to understand context
- Run tests after fixes: `pytest labs/memory/tests/ -v`
- Validate no remaining `fromfromfrom` pattern: `grep -r "fromfromfrom" labs/memory/`

**Problem**:
4 files have a critical import typo that prevents them from loading:
```python
from fromfromfromcandidate.core.common import get_logger
```

Should be:
```python
from candidate.core.common import get_logger
```

**Files to Fix**:
1. `labs/memory/systems/memory_legacy/gpt_reflection.py:25`
2. `labs/memory/systems/memory_legacy/dream_cron.py:33`
3. `labs/memory/tools/__init__.py:9`
4. `labs/memory/systems/in_memory_cache_storage_wrapper.py`

**Solution**:
Replace `fromfromfromcandidate` with `candidate` in all import statements.

**Testing**:
```python
# Verify imports work after fix
from labs.memory.systems.memory_legacy import gpt_reflection
from labs.memory.systems.memory_legacy import dream_cron
from labs.memory.tools import MemoryDriftAuditor
from labs.memory.systems import in_memory_cache_storage_wrapper

# All imports should succeed without errors
```

**Success Criteria**:
- ✅ All 4 files import successfully
- ✅ No `fromfromfrom` pattern remains in codebase
- ✅ Tests pass: `pytest labs/memory/tests/ -v`

**Commit Message**:
```
fix(memory): correct critical import typo fromfromfromcandidate → candidate

Problem:
- 4 files had broken imports preventing module loading
- Typo: `from fromfromfromcandidate.core.common`

Solution:
- Corrected to: `from candidate.core.common`
- Fixed: gpt_reflection.py, dream_cron.py, __init__.py, in_memory_cache_storage_wrapper.py

Impact:
- 4 broken imports now functional
- Memory subsystem modules can load correctly

🤖 Generated with Claude Code
```
""",
        "priority": "P0"
    },
    {
        "title": "🔴 P0: Clean Duplicate Logger Definitions in memory_legacy/ (3 files)",
        "prompt": """**CRITICAL: Remove Duplicate Logger Definitions in Legacy Memory Files**

**📚 CONTEXT FILES - READ THESE FIRST**:
- `labs/memory/lukhas_context.md` - Memory subsystem patterns
- `labs/memory/systems/memory_legacy/claude.me` - Legacy system context (if exists)
- `CLAUDE.md` - Logging standards and best practices

**🛠️ TOOLKIT**:
- Read all 3 files to see current state
- Search for logger patterns: `grep -n "logger = " <file>`
- Validate single definition: `grep -c "^logger = " <file>` (should be 1)
- Test imports: `python -c "from labs.memory.systems.memory_legacy import replayer"`

**Problem**:
Multiple files define logger variables 2-3 times, causing confusion and potential bugs:

**File 1: labs/memory/systems/memory_legacy/replayer.py**
```python
# Lines 3, 7, 36 - THREE duplicate definitions!
log = logging.getLogger(__name__)  # Line 3
logger = logging.getLogger(__name__)  # Line 7
logger = get_logger(__name__)  # Line 36
```

**File 2: labs/memory/systems/memory_legacy/dream_cron.py**
```python
# Lines 3, 6, 36 - THREE duplicate definitions!
log = logging.getLogger(__name__)  # Line 3
logger = logging.getLogger(__name__)  # Line 6
logger = get_logger(__name__)  # Line 36
# Plus undefined _init_log at line 54
```

**File 3: labs/memory/tools/__init__.py**
```python
# Lines 3, 17 - TWO duplicate definitions!
logger = logging.getLogger(__name__)  # Line 3
logger = get_logger(__name__)  # Line 17
```

**Solution**:
Keep ONLY ONE logger definition per file using the standard pattern:
```python
from candidate.core.common import get_logger

logger = get_logger(__name__)
```

**Additional Fixes**:
- Replace undefined `_init_log` with `logger` in dream_cron.py:54
- Replace undefined `log` references with `logger` in replayer.py
- Ensure all logger.* calls use the single defined logger

**Testing**:
```python
# Test all modules load and log correctly
from labs.memory.systems.memory_legacy import replayer, dream_cron
from labs.memory.tools import MemoryDriftAuditor

# Verify logging works
replayer.logger.info("Test")
dream_cron.logger.info("Test")
```

**Success Criteria**:
- ✅ ONE logger definition per file
- ✅ No undefined logger references
- ✅ All modules import successfully
- ✅ Tests pass: `pytest labs/memory/tests/ -k "legacy or tools" -v`

**Commit Message**:
```
fix(memory): remove duplicate logger definitions in legacy modules

Problem:
- replayer.py: 3 duplicate logger definitions (lines 3, 7, 36)
- dream_cron.py: 3 duplicate + undefined _init_log
- __init__.py: 2 duplicate logger definitions

Solution:
- Standardized to single get_logger(__name__) per file
- Fixed undefined logger references
- Consistent logging pattern across modules

Impact:
- Cleaner code, no logger confusion
- Fixed potential bugs from wrong logger usage

🤖 Generated with Claude Code
```
""",
        "priority": "P0"
    },
    {
        "title": "🟠 P1: Systematic Logger Cleanup for labs/memory/ (183 files)",
        "prompt": """**HIGH PRIORITY: Systematic Logger Cleanup Across Memory Subsystem**

**📚 CONTEXT FILES - READ THESE FIRST**:
- `labs/memory/lukhas_context.md` - Memory subsystem architecture
- `labs/memory/claude.me` - Domain context and patterns
- `CLAUDE.md` - Lane architecture and import rules
- `candidate/core/common/lukhas_context.md` - get_logger implementation details

**🛠️ TOOLKIT**:
- Use comprehensive grep: `grep -rn "logger = " labs/memory/ | grep -v ".pyc"`
- Count duplicates per file: `grep -c "^logger = " <file>`
- Test all imports after fix: `pytest labs/memory/ --collect-only`
- Validate pattern: `grep -r "from candidate.core.common import get_logger" labs/memory/ | wc -l`

**SCOPE**: This is a large refactor (183 files) - work systematically by subdirectory:
1. Start with `labs/memory/systems/memory_legacy/` (already partially fixed)
2. Then `labs/memory/temporal/`
3. Then `labs/memory/learning/`
4. Continue through remaining subdirectories

**Problem**:
Discovered 194 duplicate logger definitions across 183 files in `labs/memory/`:
- Files with 2+ logger definitions
- Inconsistent patterns (logging.getLogger vs get_logger)
- Mix of `log` and `logger` variable names

**Scope**: 183 files need review and cleanup

**Top Priority Files** (2+ duplicates):
```
labs/memory/systems/memory_legacy/reflector.py (2 dups)
labs/memory/systems/exponential_learning.py (2 dups)
labs/memory/systems/agent_memory.py (2 dups)
labs/memory/systems/healix_memory_core.py (2 dups)
labs/memory/systems/bio_symbolic_memory.py (2 dups)
labs/memory/systems/core.py (2 dups)
labs/memory/systems/agent_memory_trace_animator.py (2 dups)
labs/memory/temporal/diagnostic_payloads.py (2 dups)
```

**Standard Pattern** (use this everywhere):
```python
from candidate.core.common import get_logger

logger = get_logger(__name__)
```

**Solution Steps**:
1. Search for all files with pattern: `^(log|logger)\s*=\s*logging\.getLogger`
2. For each file:
   - Keep FIRST logger definition at top of file (after imports)
   - Remove ALL duplicate definitions
   - Standardize to: `logger = get_logger(__name__)`
   - Update any `log.` references to `logger.`
3. Ensure proper import: `from candidate.core.common import get_logger`

**Automated Approach**:
```python
import re
from pathlib import Path

def clean_duplicate_loggers(file_path):
    '''Remove duplicate logger definitions from file'''
    with open(file_path) as f:
        lines = f.readlines()

    # Find all logger definition lines
    logger_lines = []
    for i, line in enumerate(lines):
        if re.match(r'^\s*(log|logger)\s*=\s*(logging\.getLogger|get_logger)', line):
            logger_lines.append(i)

    # Keep only first definition, remove duplicates
    if len(logger_lines) > 1:
        for line_idx in reversed(logger_lines[1:]):
            lines.pop(line_idx)

        # Write cleaned file
        with open(file_path, 'w') as f:
            f.writelines(lines)

# Process all files
for py_file in Path('labs/memory').rglob('*.py'):
    clean_duplicate_loggers(py_file)
```

**Testing Strategy**:
```bash
# Verify no duplicate loggers remain
grep -r "^logger = " labs/memory/ | sort | uniq -c | grep -v " 1 "

# Test all modules import
pytest labs/memory/ --collect-only

# Run full test suite
pytest labs/memory/tests/ -v --tb=short
```

**Success Criteria**:
- ✅ ONE logger definition per file across all 183 files
- ✅ Consistent `logger = get_logger(__name__)` pattern
- ✅ All modules import successfully
- ✅ No broken logger references
- ✅ Tests pass: `pytest labs/memory/ -v`

**Commit Message**:
```
refactor(memory): systematic logger cleanup across 183 files

Problem:
- 194 duplicate logger definitions found
- Inconsistent patterns (logging.getLogger vs get_logger)
- Mix of variable names (log vs logger)

Solution:
- Standardized to single get_logger(__name__) per file
- Removed all duplicate definitions
- Consistent naming: logger (not log)

Impact:
- Cleaner, more maintainable codebase
- Consistent logging patterns
- Reduced technical debt

Files modified: 183
Duplicates removed: 194

🤖 Generated with Claude Code
```
""",
        "priority": "P1"
    },
    {
        "title": "🟠 P1: Fix Undefined Logger References (gpt_reflection.py)",
        "prompt": """**HIGH PRIORITY: Fix Undefined Logger Reference in GPT Reflection Module**

**📚 CONTEXT FILES - READ THESE FIRST**:
- `labs/memory/lukhas_context.md` - Memory subsystem patterns
- `labs/memory/systems/memory_legacy/lukhas_context.md` - Legacy system context (if exists)
- `CLAUDE.md` - Error handling standards

**🛠️ TOOLKIT**:
- Read file: `labs/memory/systems/memory_legacy/gpt_reflection.py`
- Search for undefined refs: `grep -n "log_init_fallback\|_init_log" labs/memory/`
- Test import error path with mock: simulate OpenAI unavailable
- Validate fix: `python -c "import sys; sys.modules['openai']=None; from labs.memory.systems.memory_legacy import gpt_reflection"`

**Problem**:
`labs/memory/systems/memory_legacy/gpt_reflection.py:47` references undefined logger:
```python
log_init_fallback.warning(
    "OpenAI library not found. `generate_gpt_reflection` will use placeholder.",
    component="GPTReflection")
```

But `log_init_fallback` is never defined - this will raise `NameError` at runtime.

**Root Cause**:
Copy-paste error from another module that had early logging before logger was initialized.

**Solution**:
Replace `log_init_fallback` with properly defined `logger`:
```python
# At top of file (after fixing import typo):
from candidate.core.common import get_logger
logger = get_logger(__name__)

# Then at line 47:
logger.warning(
    "OpenAI library not found. `generate_gpt_reflection` will use placeholder.",
    component="GPTReflection"
)
```

**Testing**:
```python
# Test the import error handling path
import sys
sys.modules['openai'] = None  # Simulate missing OpenAI

from labs.memory.systems.memory_legacy import gpt_reflection

# Should log warning without NameError
assert not gpt_reflection.OPENAI_AVAILABLE
```

**Success Criteria**:
- ✅ No undefined `log_init_fallback` reference
- ✅ Module imports without NameError
- ✅ Warning logs correctly when OpenAI unavailable
- ✅ Tests pass: `pytest labs/memory/tests/test_gpt_reflection.py -v`

**Commit Message**:
```
fix(memory): resolve undefined log_init_fallback in gpt_reflection

Problem:
- Line 47 references undefined log_init_fallback
- Causes NameError when OpenAI import fails

Solution:
- Replaced log_init_fallback with properly defined logger
- Ensured logger is initialized before use

Impact:
- Module loads correctly even when OpenAI unavailable
- No runtime NameError

🤖 Generated with Claude Code
```
""",
        "priority": "P1"
    },
    {
        "title": "🟡 P2: Standardize Logging Imports Across labs/memory/",
        "prompt": """**MEDIUM PRIORITY: Standardize Logging Import Patterns**

**📚 CONTEXT FILES - READ THESE FIRST**:
- `labs/memory/lukhas_context.md` - Memory subsystem architecture
- `candidate/core/common/lukhas_context.md` - get_logger implementation
- `CLAUDE.md` - Import standards and lane rules

**🛠️ TOOLKIT**:
- Find old patterns: `grep -r "import logging" labs/memory/ | grep -v ".pyc"`
- Find structlog usage: `grep -r "import structlog" labs/memory/`
- Validate new pattern: `grep -r "from candidate.core.common import get_logger" labs/memory/`
- Test after migration: `pytest labs/memory/ --collect-only`

**Problem**:
Mixed import patterns across `labs/memory/` subsystem:
- Some use: `import logging; logger = logging.getLogger(__name__)`
- Some use: `from candidate.core.common import get_logger; logger = get_logger(__name__)`
- Some use: `import structlog; logger = structlog.get_logger(__name__)`

This inconsistency makes:
- Hard to grep for logging patterns
- Difficult to switch logging backends
- Confusing for new contributors

**Standard Pattern** (enforce this):
```python
# At top of file, after __future__ imports and docstring
from candidate.core.common import get_logger

logger = get_logger(__name__)
```

**Migration Steps**:
1. Replace `import logging` with `from candidate.core.common import get_logger`
2. Replace `logging.getLogger(__name__)` with `get_logger(__name__)`
3. Remove `import structlog` where only used for logger
4. Ensure logger definition is right after imports (before constants)

**Example Transformation**:
```python
# BEFORE:
import logging
import structlog

logger = logging.getLogger(__name__)

# Some code...

log = structlog.get_logger()

# AFTER:
from candidate.core.common import get_logger

logger = get_logger(__name__)

# Some code...
# (structlog configured centrally in get_logger)
```

**Files to Update** (high-traffic modules):
- `labs/memory/service.py`
- `labs/memory/memory_core.py`
- `labs/memory/basic.py`
- `labs/memory/systems/memory_system.py`
- All files in `labs/memory/temporal/`
- All files in `labs/memory/learning/`

**Testing**:
```bash
# Verify standard pattern
grep -r "from candidate.core.common import get_logger" labs/memory/ | wc -l
# Should match number of Python files

# Ensure no old patterns remain
grep -r "logging.getLogger" labs/memory/ | wc -l
# Should be 0

# Test all modules import
pytest labs/memory/ --collect-only
```

**Success Criteria**:
- ✅ All files use `from candidate.core.common import get_logger`
- ✅ No `import logging` for logger creation
- ✅ Consistent pattern across all 183+ files
- ✅ Tests pass: `pytest labs/memory/tests/ -v`

**Commit Message**:
```
refactor(memory): standardize logging imports to get_logger pattern

Problem:
- Mixed logging patterns (logging.getLogger, structlog, get_logger)
- Inconsistent across 183+ files
- Hard to maintain and grep

Solution:
- Standardized to: from candidate.core.common import get_logger
- Consistent logger = get_logger(__name__) pattern
- Centralized logging configuration

Impact:
- Easier to maintain and modify logging
- Consistent patterns for contributors
- Simpler backend switching if needed

🤖 Generated with Claude Code
```
""",
        "priority": "P2"
    },
    {
        "title": "🟡 P2: Add Comprehensive Tests for Memory Legacy Modules",
        "prompt": """**MEDIUM PRIORITY: Test Coverage for Memory Legacy Subsystem**

**📚 CONTEXT FILES - READ THESE FIRST**:
- `labs/memory/lukhas_context.md` - Memory subsystem architecture
- `labs/memory/systems/memory_legacy/lukhas_context.md` - Legacy system docs (if exists)
- `MISSING_TESTS_DELEGATION_GUIDE.md` - Test creation guidelines
- `CLAUDE.md` - Testing standards (75%+ coverage requirement)

**🛠️ TOOLKIT**:
- Read source modules to understand functionality
- Check existing tests: `find tests/ -name "*legacy*" -o -name "*dream*" -o -name "*reflect*"`
- Run coverage: `pytest tests/unit/memory/legacy/ -v --cov=labs/memory/systems/memory_legacy --cov-report=term-missing`
- Follow test patterns from existing memory tests

**Problem**:
The `labs/memory/systems/memory_legacy/` modules have critical functionality but lack tests:
- `gpt_reflection.py` - GPT-based self-reflection (0% coverage)
- `dream_cron.py` - Dream scheduler daemon (0% coverage)
- `replayer.py` - Dream replay system (0% coverage)
- `reflector.py` - Memory reflection module (0% coverage)

After fixing logging and import issues, need comprehensive tests.

**Test Files to Create**:
```
tests/unit/memory/legacy/
├── test_gpt_reflection.py
├── test_dream_cron.py
├── test_replayer.py
└── test_reflector.py
```

**Test Coverage Requirements**:

**1. test_gpt_reflection.py**:
```python
import pytest
from labs.memory.systems.memory_legacy import gpt_reflection

def test_openai_unavailable_fallback():
    '''Test placeholder when OpenAI not available'''
    # Should use placeholder, not crash
    result = gpt_reflection.generate_gpt_reflection("test context")
    assert "placeholder" in result.lower()

def test_generate_gpt_reflection_with_openai(mocker):
    '''Test actual OpenAI integration'''
    mocker.patch('labs.memory.systems.memory_legacy.gpt_reflection.OPENAI_AVAILABLE', True)
    # Mock OpenAI client
    # Test successful reflection generation

@pytest.mark.integration
def test_gpt_reflection_error_handling():
    '''Test graceful error handling on API failures'''
    # Test network errors, rate limits, invalid responses
```

**2. test_dream_cron.py**:
```python
import pytest
from labs.memory.systems.memory_legacy import dream_cron

def test_schedule_configuration():
    '''Test dream cron schedule setup'''
    assert dream_cron.DREAM_SCHEDULE_TIME_CONFIG == "03:33"
    # Verify symbolic hour

def test_run_dream_script_not_found():
    '''Test handling of missing dream script'''
    # Should log critical error, not crash

def test_main_scheduler_loop_keyboard_interrupt():
    '''Test graceful shutdown on Ctrl+C'''
    # Mock schedule.run_pending
    # Simulate KeyboardInterrupt
    # Verify clean shutdown
```

**3. test_replayer.py**:
```python
import pytest
from labs.memory.systems.memory_legacy import replayer

def test_load_recent_dream_logs_empty():
    '''Test loading when no dream logs exist'''
    logs = replayer.load_recent_dream_logs(limit=3)
    assert logs == []

def test_load_recent_dream_logs_with_data(tmp_path):
    '''Test loading valid dream logs'''
    # Create test dream log file
    # Load and verify parsing

def test_replay_dreams_with_current_state(mocker):
    '''Test dream replay with mocked traits'''
    # Mock load_traits, speak, display_visual_traits
    # Verify replay logic
```

**4. test_reflector.py**:
```python
import pytest
from labs.memory.systems.memory_legacy import reflector

def test_reflector_initialization():
    '''Test reflector module loads correctly'''
    # Basic import and initialization tests

# Add more based on reflector.py actual functionality
```

**Success Criteria**:
- ✅ All 4 test files created
- ✅ 75%+ code coverage for each module
- ✅ Tests pass: `pytest tests/unit/memory/legacy/ -v --cov=labs/memory/systems/memory_legacy`
- ✅ Integration tests for external dependencies (OpenAI, schedule)
- ✅ Error handling tests for all failure modes

**Commit Message**:
```
test(memory): add comprehensive tests for legacy modules

Problem:
- 0% test coverage for memory legacy subsystem
- Critical modules untested (gpt_reflection, dream_cron, replayer)

Solution:
- Added 4 comprehensive test suites
- Unit tests for core functionality
- Integration tests for external deps
- Error handling and edge case coverage

Impact:
- 75%+ coverage for memory legacy modules
- Confidence in refactoring and fixes
- Better reliability for dream/reflection systems

🤖 Generated with Claude Code
```
""",
        "priority": "P2"
    }
]


async def create_batch6_sessions():
    """Create Jules Batch 6: Memory subsystem code quality fixes"""
    async with JulesClient() as jules:
        print("🚀 Creating Jules Batch 6: Memory Subsystem Code Quality Fixes")
        print("=" * 70)

        created_sessions = []

        for i, session_config in enumerate(BATCH6_SESSIONS, 1):
            priority = session_config['priority']
            title = session_config['title']

            print(f"\n📋 [{i}/{len(BATCH6_SESSIONS)}] Creating: {title}")
            print(f"   Priority: {priority}")

            try:
                session = await jules.create_session(
                    prompt=session_config['prompt'],
                    source_id="sources/github/LukhasAI/Lukhas",
                    automation_mode="AUTO_CREATE_PR"
                )

                session_id = session.get('name', 'unknown').split('/')[-1]
                session_url = f"https://jules.google.com/session/{session_id}"

                created_sessions.append({
                    'title': title,
                    'priority': priority,
                    'session_id': session_id,
                    'url': session_url
                })

                print(f"   ✅ Created: {session_id}")
                print(f"   🔗 URL: {session_url}")

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                if "429" in str(e):
                    print(f"   ⚠️  Rate limit hit. Created {len(created_sessions)}/{len(BATCH6_SESSIONS)} sessions.")
                    break

        print("\n" + "=" * 70)
        print(f"✅ Batch 6 Complete: {len(created_sessions)}/{len(BATCH6_SESSIONS)} sessions created")
        print("=" * 70)

        # Save session details
        print("\n📊 Session Summary:")
        for session in created_sessions:
            print(f"\n{session['priority']} - {session['title']}")
            print(f"   ID: {session['session_id']}")
            print(f"   URL: {session['url']}")

        return created_sessions


if __name__ == "__main__":
    sessions = asyncio.run(create_batch6_sessions())
    print(f"\n🎉 Successfully created {len(sessions)} Jules sessions in Batch 6!")
