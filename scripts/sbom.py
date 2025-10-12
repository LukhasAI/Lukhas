#!/usr/bin/env python3
import subprocess, sys, pathlib
out = pathlib.Path("build"); out.mkdir(parents=True, exist_ok=True)
subprocess.check_call([sys.executable, "-m", "pip", "install", "cyclonedx-bom"])
subprocess.check_call([sys.executable, "-m", "cyclonedx_py", "-o", str(out / "sbom.cyclonedx.json")])
print("[sbom] wrote", out / "sbom.cyclonedx.json")
