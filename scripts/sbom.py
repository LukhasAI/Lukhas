#!/usr/bin/env python3
"""
Generate Software Bill of Materials (SBOM) in CycloneDX JSON format.

Usage:
    python3 scripts/sbom.py [--output build/sbom.cyclonedx.json]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Generate SBOM for LUKHAS")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/sbom.cyclonedx.json"),
        help="Output file path (default: build/sbom.cyclonedx.json)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "xml"],
        default="json",
        help="Output format (default: json)"
    )
    args = parser.parse_args()
    
    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if cyclonedx-bom is installed
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "cyclonedx-bom"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("[sbom] Installing cyclonedx-bom...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "cyclonedx-bom"]
            )
    except Exception as e:
        print(f"[sbom] Warning: Failed to check/install cyclonedx-bom: {e}")
    
    # Generate SBOM
    try:
        print(f"[sbom] Generating SBOM to {args.output}...")
        
        # Use cyclonedx-py command directly
        cmd = [
            "cyclonedx-py",
            "-o", str(args.output),
            "--format", args.format
        ]
        
        subprocess.check_call(cmd)
        
        if args.output.exists():
            size = args.output.stat().st_size
            print(f"[sbom] ✅ Successfully generated SBOM ({size:,} bytes)")
            print(f"[sbom] Output: {args.output}")
            return 0
        else:
            print(f"[sbom] ❌ SBOM file not created")
            return 1
            
    except FileNotFoundError:
        print("[sbom] ❌ cyclonedx-py command not found")
        print("[sbom] Install with: pip install cyclonedx-bom")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"[sbom] ❌ Failed to generate SBOM: {e}")
        return 1
    except Exception as e:
        print(f"[sbom] ❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

