---
status: wip
type: documentation
---
# Developer Quick Reference Guide (QRG) 🧪

> Experimental — enable feature flags before using these steps.

## Environment Setup
1. Clone the repo and create a virtual environment.
   ```bash
   git clone <repo-url>
   cd Lukhas
   python3 -m venv .venv
   source .venv/bin/activate
   make install
   make setup-hooks
   ```
2. Activate experimental mode when working with new features:
   ```bash
   export LUKHAS_EXPERIMENTAL=1
   ```

## Commit Hygiene
- Keep commits small and focused.
- Format and lint before committing:
  ```bash
  make format
  make lint
  pre-commit run --files <changed-files>
  ```
- Verify a clean state with `git status` and craft descriptive commit messages.

## Testing and Debugging
- Quick suite (smoke & tier1):
  ```bash
  make test-fast
  ```
- Full suite:
  ```bash
  make test-all
  ```
- Jules-06 adapters lane:
  ```bash
  make test-jules06
  ```
- Run specific tests with `pytest path/to/test -k pattern -vv`.
- Debug interactively with `pytest -s` or `pdb.set_trace()`.

### Provided Checks
| Check | Command | Purpose |
|-------|---------|---------|
| Lint | `make lint` | Run Flake8, Ruff, MyPy, Bandit, and import hygiene checks |
| Unused Imports | `make lint-unused` / `make lint-unused-strict` | Report or enforce F401 violations |
| Format | `make format` | Apply Black and isort formatting |
| Types (core) | `make types-core` | Run MyPy on core paths |
| Spec Lint | `make spec-lint` | Validate test specs for consistency |
| Contract Check | `make contract-check` | Ensure contracts align with the base branch |
| Tests | `make test-fast` / `make test-all` / `make test-jules06` | Execute test suites |
| Test Report | `make test-report` | Summarize coverage metrics |

## PR Submission Guidelines
1. Gate all new work behind `LUKHAS_EXPERIMENTAL` or another appropriate feature flag.
2. Run all checks above and resolve any failures.
3. Re-run `pre-commit run --files <changed-files>` and `make test-fast` before pushing.
4. Push your branch and open a PR containing:
   - Summary of changes
   - Note about feature flag usage
   - Test results
5. Await review and approvals before merging.
