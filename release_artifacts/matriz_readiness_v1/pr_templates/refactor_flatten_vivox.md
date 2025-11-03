Title: refactor(flatten-vivox): shim memory_node → MATRIZ/matriz_memory_node.py

Summary:
- Created new flattened module: MATRIZ/matriz_memory_node.py
- Replaced original file with shim at candidate/core/matrix/nodes/memory_node.py
- Verified: compile, ruff E/F, smoke tests pass locally

Changes:
- Added: MATRIZ/matriz_memory_node.py
- Modified: candidate/core/matrix/nodes/memory_node.py (now shim)

Verification:
- `python3 -m compileall candidate/core/matrix/nodes/memory_node.py MATRIZ/matriz_memory_node.py`
- `ruff check --select E,F,E741 MATRIZ/matriz_memory_node.py candidate/core/matrix/nodes/memory_node.py`
- smoke tests: `pytest -q -m "matriz or tier1"`

Checklist:
- [ ] ruff E/F/E741 checks pass
- [ ] compile check passes
- [ ] smoke tests pass
- [ ] `restoration_audit.csv` entry added
- [ ] Shim marked DEPRECATED and contains __all__ and comment

Rollback:
- `git reset --hard origin/main && git branch -D refactor/flatten-vivox-v1`
