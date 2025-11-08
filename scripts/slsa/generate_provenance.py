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

def generate_provenance(modules: list[str], output: Path, artifact_hashes: dict[str, str]):
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

    # Create subjects from the provided artifact hashes
    subjects = []
    for artifact_name, artifact_hash in artifact_hashes.items():
        subjects.append({
            "name": artifact_name,
            "digest": {"sha256": artifact_hash}
        })

    # Create SLSA provenance (v0.2 format)
    provenance = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "subject": subjects,
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
    parser.add_argument("--artifact-hashes", required=True, help="JSON string of artifact hashes")

    args = parser.parse_args()

    modules = [m.strip() for m in args.modules.split(",")]
    artifact_hashes = json.loads(args.artifact_hashes)
    generate_provenance(modules, Path(args.output), artifact_hashes)

if __name__ == "__main__":
    main()
