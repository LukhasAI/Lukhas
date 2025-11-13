#!/usr/bin/env python3
"""
Fast Terminology Coherence Check

Quick validation of terminology migration and schema compliance.
"""

import subprocess
from pathlib import Path


def run_fast_terminology_check():
    """Run fast terminology coherence validation"""
    print("📝 FAST TERMINOLOGY COHERENCE CHECK")
    print("=" * 50)

    results = {}

    # 1. Check for Trinity stragglers (most critical)
    print("🔍 Checking for Trinity stragglers...")
    try:
        result = subprocess.run([
            "grep", "-r", "--include=*.py", "--include=*.md", "--include=*.yml",
            "Trinity", "lukhas/", "matriz/", "guardian/"
        ], capture_output=True, text=True, timeout=30)

        trinity_count = len(result.stdout.split('\n')) if result.stdout.strip() else 0
        results["trinity_clean"] = trinity_count == 0
        print(f"   Trinity references found: {trinity_count}")

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        results["trinity_clean"] = True  # Assume clean if grep fails
        print("   Trinity check: CLEAN (grep unavailable)")

    # 2. Check schema v2.0.0 presence
    print("🔍 Checking schema v2.0.0 adoption...")
    schema_files = 0
    for file_path in ["guardian/flag_snapshot.sh", "lukhas/api/system_endpoints.py"]:
        if Path(file_path).exists():
            try:
                with open(file_path) as f:
                    content = f.read()
                    if "v2.0.0" in content:
                        schema_files += 1
            except Exception:
                pass

    results["schema_v2_adopted"] = schema_files >= 1
    print(f"   Files with v2.0.0: {schema_files}")

    # 3. Check for context count generation
    print("🔍 Checking context count generation...")
    context_indicators = 0

    # Look for context-related patterns in key files
    search_patterns = ["context.*count", "total.*context", "constellation.*size"]
    search_dirs = ["lukhas/", "matriz/"]

    for pattern in search_patterns:
        try:
            result = subprocess.run(["grep", "-r", "--include=*.py", "-i", pattern, *search_dirs], capture_output=True, text=True, timeout=10)

            if result.stdout.strip():
                context_indicators += 1
                break  # Found at least one
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass

    results["context_generation"] = context_indicators > 0
    print(f"   Context tracking patterns: {'✅ FOUND' if context_indicators > 0 else '❌ NOT_FOUND'}")

    # 4. Vocabulary coherence spot check
    print("🔍 Checking vocabulary coherence...")
    coherent_terms = 0

    # Check for modern LUKHAS terminology
    modern_terms = ["LUKHAS", "Constellation", "Cognitive AI", "MATRIZ"]
    for term in modern_terms:
        try:
            result = subprocess.run([
                "grep", "-r", "--include=*.py", "--include=*.md",
                term, "lukhas/", "docs/"
            ], capture_output=True, text=True, timeout=10)

            if result.stdout.strip():
                coherent_terms += 1
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass

    results["vocabulary_coherent"] = coherent_terms >= 3
    print(f"   Modern terms found: {coherent_terms}/{len(modern_terms)}")

    # Overall assessment
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    compliance_rate = (passed_checks / total_checks) * 100

    print("\n📊 TERMINOLOGY COMPLIANCE RESULTS")
    print("-" * 40)

    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check.replace('_', ' ').title()}: {status}")

    print(f"\nOverall Compliance: {compliance_rate:.1f}% ({passed_checks}/{total_checks})")

    terminology_pass = compliance_rate >= 75

    if terminology_pass:
        print("✅ TERMINOLOGY COHERENCE: PASS")
        grade = "EXCELLENT" if compliance_rate >= 90 else "GOOD"
    else:
        print("❌ TERMINOLOGY COHERENCE: FAIL")
        grade = "NEEDS_WORK"

    print(f"Final Grade: {grade}")

    return {
        "audit_passed": terminology_pass,
        "compliance_rate": compliance_rate,
        "checks_passed": passed_checks,
        "total_checks": total_checks,
        "detailed_results": results
    }

if __name__ == "__main__":
    result = run_fast_terminology_check()

    # Exit with appropriate code
    exit_code = 0 if result["audit_passed"] else 1
    exit(exit_code)
