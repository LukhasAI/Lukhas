#!/usr/bin/env python3
"""
Generate Software Bill of Materials (SBOM) for LUKHAS
"""
import json
import subprocess
from datetime import datetime


def generate_sbom():
    """Generate SBOM in SPDX format"""
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "creationInfo": {
            "created": datetime.now().isoformat(),
            "creators": ["Tool: lukhas-sbom-generator"]
        },
        "name": "LUKHAS AI System",
        "packages": []
    }

    # Get Python dependencies
    result = subprocess.run(
        ["pip", "freeze"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split('\n'):
        if '==' in line:
            name, version = line.split('==')
            sbom["packages"].append({
                "name": name,
                "version": version,
                "supplier": "PyPI"
            })

    return sbom

if __name__ == "__main__":
    sbom = generate_sbom()
    with open("sbom.json", "w") as f:
        json.dump(sbom, f, indent=2)
    print("✅ SBOM generated: sbom.json")
