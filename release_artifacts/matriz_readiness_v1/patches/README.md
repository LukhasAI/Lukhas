This patch demonstrates shim-first flattening:
1. COPY original file contents into new flattened module `MATRIZ/matriz_memory_node.py`
   - Use AST rewrite if relative imports are present
2. Replace original file with a shim that re-exports the symbol(s)
3. Run black/ruff/compile/test and commit
4. Open PR for review

Apply:
- Prefer to create PR via `git` and `gh` as shown in TODO-02.
