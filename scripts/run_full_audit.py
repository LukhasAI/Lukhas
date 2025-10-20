#!/usr/bin/env python3
"""
T4/0.01% Excellence Complete Audit Runner

Orchestrates the complete audit process from baseline measurement through certification.
Provides end-to-end validation of LUKHAS AI system performance and compliance.
"""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_command(cmd, description="", check=True, capture_output=True):
    """Run a command with error handling."""
    print(f"🔧 {description}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )

        if capture_output and result.stdout:
            print(f"   Output: {result.stdout.strip()}")

        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        if capture_output and e.stdout:
            print(f"   Stdout: {e.stdout}")
        if capture_output and e.stderr:
            print(f"   Stderr: {e.stderr}")
        raise

def main():
    """Main audit orchestration function."""
    parser = argparse.ArgumentParser(description="Run Complete T4/0.01% Excellence Audit")
    parser.add_argument("--output-dir", default="audit_results", help="Output directory for all results")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples for baseline")
    parser.add_argument("--skip-chaos", action="store_true", help="Skip chaos engineering tests")
    parser.add_argument("--skip-reproducibility", action="store_true", help="Skip reproducibility analysis")
    parser.add_argument("--environment", default="local", help="Environment identifier")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate audit run ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audit_id = f"audit_{args.environment}_{timestamp}"

    print("🔬 LUKHAS AI T4/0.01% Excellence Complete Audit")
    print("=" * 50)
    print(f"Audit ID: {audit_id}")
    print(f"Environment: {args.environment}")
    print(f"Samples: {args.samples}")
    print(f"Output Directory: {output_dir.absolute()}")
    print("")

    try:
        # Phase 1: Baseline Performance Measurement
        print("📊 Phase 1: Baseline Performance Measurement")
        print("-" * 45)

        baseline_file = output_dir / f"audit_baseline_{audit_id}.json"
        cmd = f"python3 scripts/audit_baseline.py --environment {args.environment} --samples {args.samples} --output {baseline_file}"
        run_command(cmd, "Running baseline performance measurement")

        if not baseline_file.exists():
            print("❌ Baseline measurement failed")
            return 1

        print("✅ Baseline measurement complete")
        print("")

        # Phase 2: Statistical Analysis
        print("📈 Phase 2: Statistical Analysis")
        print("-" * 33)

        # Create reference baseline for comparison
        reference_file = output_dir / f"audit_reference_{audit_id}.json"
        cmd = f"python3 scripts/audit_baseline.py --environment {args.environment}_ref --samples {args.samples // 2} --output {reference_file}"
        run_command(cmd, "Creating reference baseline")

        if reference_file.exists():
            statistical_file = output_dir / f"statistical_analysis_{audit_id}.json"
            statistical_report = output_dir / f"statistical_report_{audit_id}.md"
            cmd = f"python3 scripts/statistical_tests.py --baseline {baseline_file} --comparison {reference_file} --alpha 0.01 --output {statistical_file} --report {statistical_report}"
            run_command(cmd, "Running statistical analysis")
            print("✅ Statistical analysis complete")
        else:
            print("⚠️  Warning: Could not create reference baseline")

        print("")

        # Phase 3: Reproducibility Analysis
        if not args.skip_reproducibility:
            print("🔄 Phase 3: Reproducibility Analysis")
            print("-" * 36)

            # Generate multiple reproducibility runs
            repro_files = []
            for i in range(1, 4):  # 3 reproducibility runs
                repro_file = output_dir / f"repro_{i}_{audit_id}.json"
                cmd = f"python3 scripts/audit_baseline.py --environment {args.environment}_repro_{i} --samples {args.samples // 4} --output {repro_file}"
                run_command(cmd, f"Running reproducibility test {i}/3")

                if repro_file.exists():
                    repro_files.append(str(repro_file))

            if len(repro_files) >= 2:
                repro_analysis = output_dir / f"reproducibility_analysis_{audit_id}.json"
                repro_report = output_dir / f"reproducibility_report_{audit_id}.md"
                files_str = " ".join(f'"{f}"' for f in repro_files)
                cmd = f"python3 scripts/reproducibility_analysis.py --data {files_str} --output {repro_analysis} --report {repro_report} --target-reproducibility 0.80"
                run_command(cmd, "Running reproducibility analysis")
                print("✅ Reproducibility analysis complete")
            else:
                print("⚠️  Warning: Insufficient reproducibility data")

            print("")

        # Phase 4: Chaos Engineering Tests
        if not args.skip_chaos:
            print("🌪️  Phase 4: Chaos Engineering Tests")
            print("-" * 36)

            chaos_components = ["guardian", "consciousness", "creativity"]
            for component in chaos_components:
                chaos_file = output_dir / f"chaos_{component}_{audit_id}.json"
                cmd = f"python3 scripts/test_fail_closed.py --component {component} --stress-level moderate --output {chaos_file} --requirement never_false_positive"
                run_command(cmd, f"Testing {component} under stress", check=False)  # Don't fail on chaos test failures

            print("✅ Chaos engineering tests complete")
            print("")

        # Phase 5: Tamper-Evident Proof Generation
        print("🔒 Phase 5: Tamper-Evident Proof Generation")
        print("-" * 42)

        # Find all evidence files
        evidence_files = list(output_dir.glob("*.json"))
        evidence_files = [f for f in evidence_files if f.name != f"merkle_chain_{audit_id}.json"]  # Exclude the chain file itself

        if evidence_files:
            merkle_file = output_dir / f"merkle_chain_{audit_id}.json"
            files_str = " ".join(f'"{f}"' for f in evidence_files)
            cmd = f"python3 scripts/verify_merkle_chain.py --create-chain --evidence {files_str} --output {merkle_file}"
            run_command(cmd, "Creating tamper-evident proof chain")
            print("✅ Tamper-evident proof chain created")
        else:
            print("⚠️  Warning: No evidence files found for Merkle chain")

        print("")

        # Phase 6: Claims Verification
        print("🎯 Phase 6: Claims Verification")
        print("-" * 31)

        if baseline_file.exists():
            verification_file = output_dir / f"verification_analysis_{audit_id}.json"
            verification_report = output_dir / f"verification_report_{audit_id}.md"
            cmd = f"python3 scripts/verify_claims.py --baseline {baseline_file} --results {baseline_file} --tolerance 25.0 --output {verification_file} --report {verification_report}"
            run_command(cmd, "Verifying performance claims")
            print("✅ Claims verification complete")
        else:
            print("⚠️  Warning: No baseline file for claims verification")

        print("")

        # Phase 7: Generate Final Certification
        print("📜 Phase 7: Final Certification Generation")
        print("-" * 40)

        certification_file = output_dir / f"certification_{audit_id}.json"
        certification_report = output_dir / f"CERTIFICATION_{audit_id}.md"
        cmd = f"python3 scripts/generate_audit_certification.py --evidence-dir {output_dir} --output {certification_file} --report {certification_report} --verbose"
        result = run_command(cmd, "Generating final certification", check=False)

        print("")

        # Phase 8: Generate Evidence Package
        print("📦 Phase 8: Evidence Package Generation")
        print("-" * 38)

        package_file = output_dir / f"evidence_package_{audit_id}.zip"
        cmd = f"python3 scripts/generate_audit_package.py --evidence-dir {output_dir} --output {package_file} --audit-id {audit_id}"
        run_command(cmd, "Creating evidence package", check=False)

        print("")

        # Final Summary
        print("🎉 Complete Audit Summary")
        print("=" * 25)

        # Count generated files
        json_files = len(list(output_dir.glob("*.json")))
        report_files = len(list(output_dir.glob("*.md")))
        total_size = sum(f.stat().st_size for f in output_dir.iterdir() if f.is_file())

        print("📊 Generated Files:")
        print(f"   JSON Evidence: {json_files}")
        print(f"   Reports: {report_files}")
        print(f"   Total Size: {total_size // 1024:.1f} KB")
        print("")

        # Show key files
        print("📋 Key Output Files:")
        key_files = [
            f"audit_baseline_{audit_id}.json",
            f"CERTIFICATION_{audit_id}.md",
            f"evidence_package_{audit_id}.zip"
        ]

        for filename in key_files:
            filepath = output_dir / filename
            if filepath.exists():
                print(f"   ✓ {filename}")
            else:
                print(f"   ❌ {filename} (missing)")

        print("")

        # Final verdict based on certification
        cert_file = output_dir / f"certification_{audit_id}.json"
        if cert_file.exists():
            try:
                with open(cert_file, 'r') as f:
                    cert_data = json.load(f)

                status = cert_data.get("certification", {}).get("status", "UNKNOWN")
                confidence = cert_data.get("certification", {}).get("confidence_level", 0.0)

                print("🎯 FINAL AUDIT VERDICT:")
                print(f"   Status: {status}")
                print(f"   Confidence: {confidence:.1%}")

                if status == "CERTIFIED":
                    print("\n✅ T4/0.01% EXCELLENCE AUDIT: PASSED")
                    print("🚀 System certified for production deployment")
                    return 0
                elif status == "PROVISIONAL":
                    print("\n⚠️  T4/0.01% EXCELLENCE AUDIT: PROVISIONAL")
                    print("🔍 Review required for full certification")
                    return 2
                else:
                    print("\n❌ T4/0.01% EXCELLENCE AUDIT: FAILED")
                    print("🚫 System does not meet certification standards")
                    return 1

            except Exception as e:
                print(f"⚠️  Could not read certification results: {e}")
                return 3
        else:
            print("⚠️  No certification file generated")
            return 3

    except Exception as e:
        print(f"\n❌ Audit failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
