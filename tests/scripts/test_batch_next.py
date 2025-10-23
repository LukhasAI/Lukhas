import os
import subprocess
import textwrap
from pathlib import Path


def test_run_pytest_falls_back_to_virtualenv(tmp_path):
    repo_stub = tmp_path / "repo"
    repo_stub.mkdir()

    venv_bin = repo_stub / ".venv" / "bin"
    venv_bin.mkdir(parents=True)

    log_file = repo_stub / "pytest_log.txt"
    runner = venv_bin / "python"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"${LUKHAS_REPO}/pytest_log.txt\"\n"
        "exit 0\n"
    )
    runner.chmod(0o755)

    repo_root = Path(__file__).resolve().parents[2]
    command = textwrap.dedent(
        """
        set -euo pipefail
        source scripts/batch_next.sh
        resolve_pytest_command
        run_pytest --example-flag
        """
    )

    env = os.environ.copy()
    env["LUKHAS_REPO"] = str(repo_stub)
    env["BATCH_NEXT_FORCE_PYTEST_FALLBACK"] = "1"

    subprocess.run(["bash", "-c", command], check=True, cwd=repo_root, env=env)

    assert log_file.exists(), "fallback runner should log invocation"
    assert log_file.read_text().strip() == "-m pytest --example-flag"
