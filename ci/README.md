CI & Lockfile Guidance

Purpose

This file documents the recommended CI policy for generating reproducible runtime lockfiles for the LUKHAS project and explains the split runtime/dev lockfile strategy.

Recommendations

1. Runtime lockfile (single authoritative lockfile)
   - Use a CI image that installs native build dependencies required by runtime packages:
     - macOS (GitHub macos-latest): brew install libpq openssl@3
     - Linux (Ubuntu): apt-get update && apt-get install -y libpq-dev libssl-dev pkg-config
   - Activate a clean Python venv and run:
     pip install pip-tools
     pip-compile --generate-hashes --output-file=requirements.lock.txt requirements.txt
   - Install from the lockfile to verify: python -m pip install --require-hashes -r requirements.lock.txt

2. Dev lockfile (developer tooling)
   - Generate `requirements-dev.lock.txt` from `requirements-dev.txt` in a developer workstation or CI image. Dev tools may require newer transitive dependencies (for example, `semgrep` requires `urllib3` 2.x). Keeping dev lockfile separate avoids impossible resolver conflicts.

3. Commit lockfiles
   - Commit `requirements.lock.txt` (runtime) and `requirements-dev.lock.txt` (dev) to the repo after validation.

4. If you must produce a single combined lockfile
   - Build it inside the CI image that includes native libs (see step 1). This avoids psycopg/psycopg2 build failures.

Notes

- We intentionally keep `psycopg2-binary` pinned in `requirements.txt` to avoid requiring libpq on developer machines; CI should prefer system libpq for production builds.
- If you need help adding libpq/OpenSSL into your CI images, I can provide sample GitHub Actions and Dockerfile snippets.

GitHub Actions workflow
-----------------------

We added a workflow `.github/workflows/generate-lockfiles.yml` that automates the recommended process:

- Installs system libraries (libpq-dev, libssl-dev) on Ubuntu
- Creates a Python virtual environment
- Installs `pip-tools` and runs `pip-compile --generate-hashes` for both runtime and dev requirements
- Installs from `requirements.lock.txt` using `pip --require-hashes` to validate reproducibility
- Runs pre-gates (ruff, mypy, pytest) for quick validation (these are non-blocking by default in the workflow)
- Commits regenerated lockfiles back to the current branch when changes are detected

Usage
-----

From the Actions UI, run the `Generate and Validate Lockfiles` workflow (workflow_dispatch). The job will rebuild lockfiles and, on success, push them to your current branch.

Notes
-----

- The workflow uses Ubuntu and apt packages for libpq / OpenSSL. If your production runtime uses a different base image (musl, alpine), adapt the system package steps accordingly.
- The workflow currently installs `python 3.11` — update `PYTHON_VERSION` in the workflow if you need a different version.
- Pre-gates are executed but won't block lockfile commits; change `|| true` removal if you want the workflow to fail on linter/test failures.
