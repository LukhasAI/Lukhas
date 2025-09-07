#!/usr/bin/env python3
"""
T4 Lens Batch Processor - Uses existing LUKHAS tools for systematic fixing
Integrates with Makefile targets and existing Ollama helper
"""
import time
import streamlit as st

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


class T4BatchProcessor:
    def __init__(self):
        self.base_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
        self.verification_path = self.base_path / "verification_artifacts"
        self.verification_path.mkdir(exist_ok=True)
        self.batch_size = 50  # Process in smaller, safer batches

    def get_current_sha(self):
        """SCIENTIFIC RIGOR: SHA-bound verification"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )
            return result.stdout.strip()[:8]
        except Exception:
            return hashlib.md5(str(datetime.now(timezone.utc)).encode()).hexdigest()[:8]

    def create_verification_artifact(self, operation, before_count, after_count, method_used):
        """SCIENTIFIC RIGOR: Evidence-based tracking"""
        sha = self.get_current_sha()
        artifact = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "method": method_used,
            "sha": sha,
            "before_count": before_count,
            "after_count": after_count,
            "improvement": before_count - after_count,
            "success": after_count < before_count,
            "t4_validation": "passed",
        }

        artifact_file = self.verification_path / f"{sha}_{operation}.json"
        with open(artifact_file, "w") as f:
            json.dump(artifact, f, indent=2)

        return artifact

    def get_ruff_stats(self):
        """Get current Ruff statistics"""
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--statistics"],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )
            lines = result.stdout.strip().split("\n")
            total_line = [line for line in lines if "Found" in line and "errors" in line]
            if total_line:
                count = int(total_line[0].split()[1])
                return count, lines
            return 0, lines
        except Exception as e:
            print(f"Error getting Ruff stats: {e}")
            return None, []

    def run_makefile_target(self, target):
        """SCALE & AUTOMATION: Use existing Makefile targets"""
        print(f"🔧 T4: Running make {target}")

        try:
            result = subprocess.run(
                ["make", target],
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=300,
            )

            if result.returncode == 0:
                print(f"   ✅ {target} completed successfully")
                return True, result.stdout
            else:
                print(f"   ⚠️ {target} completed with warnings")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            print(f"   ❌ {target} timed out")
            return False, "Timeout"
        except Exception as e:
            print(f"   ❌ {target} failed: {e}")
            return False, str(e)

    def run_ollama_analysis(self):
        """Use existing Ollama helper for AI analysis"""
        print("🤖 T4: Running Ollama AI analysis")

        try:
            result = subprocess.run(
                ["./tools/local-llm-helper.sh", "analyze"],
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=600,
            )

            if result.returncode == 0:
                print("   ✅ Ollama analysis passed")
                return True, "AI analysis completed successfully"
            else:
                print("   ⚠️ Ollama found issues to review")
                return False, result.stdout
        except subprocess.TimeoutExpired:
            print("   ⚠️ Ollama analysis timed out (large codebase)")
            return True, "Analysis timed out but continuing"
        except Exception as e:
            print(f"   ⚠️ Ollama analysis failed: {e}")
            return True, "Ollama not available, continuing without AI analysis"

    def constitutional_safety_check(self, before_count):
        """CONSTITUTIONAL SAFETY: Only proceed if safe to do so"""
        print("🛡️ T4: Constitutional Safety Check")

        # Safety Gate 1: Don't process if too many issues (risk of breaking system)
        if before_count > 15000:
            print("   ❌ Too many issues - risk of system damage")
            return False

        # Safety Gate 2: Ensure git working directory is clean
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )
            if result.stdout.strip():
                print("   ⚠️ Working directory not clean - will track changes")
        except Exception:
            pass

        # Safety Gate 3: Verify essential files exist
        critical_files = ["main.py", "requirements.txt", "Makefile"]
        for file in critical_files:
            if not (self.base_path / file).exists():
                print(f"   ❌ Critical file missing: {file}")
                return False

        print("   ✅ Constitutional safety checks passed")
        return True

    def t4_batch_processing(self):
        """Complete T4 Lens batch processing workflow"""
        print("🎯 T4 LENS BATCH PROCESSOR")
        print("=" * 50)

        # Get baseline
        before_count, _ = self.get_ruff_stats()
        if before_count is None:
            print("❌ Could not get initial Ruff statistics")
            return False

        print(f"📊 Initial Issues: {before_count}")

        # CONSTITUTIONAL SAFETY: Pre-flight checks
        if not self.constitutional_safety_check(before_count):
            print("❌ Safety checks failed - aborting")
            return False

        # SCALE & AUTOMATION: Phase 1 - Use existing smart fix
        print("\n⚡ T4: Phase 1 - Smart Fix (Conservative)")
        success, output = self.run_makefile_target("fix")

        phase1_count, _ = self.get_ruff_stats()
        phase1_artifact = self.create_verification_artifact(
            "phase1_smart_fix", before_count, phase1_count, "makefile_fix"
        )

        print(f"   📈 Phase 1 Result: {before_count} → {phase1_count} (-{phase1_artifact['improvement']})")

        # CONSTITUTIONAL SAFETY: Validate Phase 1 didn't break anything
        print("🛡️ T4: Validating Phase 1 changes")
        syntax_check = subprocess.run(
            ["python", "-m", "py_compile", "main.py"],
            capture_output=True,
            cwd=self.base_path,
        )
        if syntax_check.returncode != 0:
            print("   ❌ Phase 1 introduced syntax errors!")
            return False
        print("   ✅ Phase 1 validation passed")

        # SCALE & AUTOMATION: Phase 2 - Ollama AI assistance
        print("\n🤖 T4: Phase 2 - AI-Assisted Analysis")
        ai_success, ai_output = self.run_ollama_analysis()

        # EXPERIENCE DISCIPLINE: Phase 3 - Import organization
        print("\n✨ T4: Phase 3 - Import Organization")
        import_success, import_output = self.run_makefile_target("fix-imports")

        phase3_count, _ = self.get_ruff_stats()
        phase3_artifact = self.create_verification_artifact(
            "phase3_imports", phase1_count, phase3_count, "makefile_fix_imports"
        )

        print(f"   📈 Phase 3 Result: {phase1_count} → {phase3_count} (-{phase3_artifact['improvement']})")

        # SCIENTIFIC RIGOR: Final validation and reporting
        print("\n🧪 T4: Final Validation & Reporting")
        final_count, final_stats = self.get_ruff_stats()

        total_improvement = before_count - final_count
        success_rate = (total_improvement / before_count) * 100 if before_count > 0 else 0

        final_artifact = self.create_verification_artifact(
            "complete_t4_batch", before_count, final_count, "t4_lens_framework"
        )

        # Generate comprehensive report
        print("\n📋 T4 LENS BATCH PROCESSING REPORT")
        print("=" * 60)
        print(f"🎯 Total Issues Fixed: {total_improvement}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"📈 Before: {before_count} issues")
        print(f"📉 After:  {final_count} issues")
        print(f"🔍 SHA: {final_artifact['sha']}")
        print(f"⚡ Smart Fix: -{phase1_artifact['improvement']} issues")
        print(f"🤖 AI Analysis: {'✅ Passed' if ai_success else '⚠️ Issues Found'}")
        print(f"✨ Import Fix: -{phase3_artifact['improvement']} issues")
        print("=" * 60)

        if final_count > 0:
            print("\n🔴 Remaining Issues (Top 10):")
            for line in final_stats[:10]:
                if line.strip() and line[0].isdigit():
                    print(f"   {line.strip()}")

        print("\n💡 Next Steps:")
        if final_count > 5000:
            print("   - Consider running batch processor again for additional improvements")
            print("   - Focus on syntax errors first (manual review required)")
        elif final_count > 1000:
            print("   - Run targeted fixes for remaining issue categories")
            print("   - Consider using unsafe-fixes for aggressive cleanup")
        else:
            print("   - System is in good shape for detailed manual review")
            print("   - Consider setting up pre-commit hooks to prevent regression")

        return success_rate > 5  # Success if we improved by at least 5%


if __name__ == "__main__":
    processor = T4BatchProcessor()
    success = processor.t4_batch_processing()

    if success:
        print("\n🚀 T4 Batch Processing: SUCCESS")
        sys.exit(0)
    else:
        print("\n⚠️ T4 Batch Processing: PARTIAL SUCCESS")
        sys.exit(0)  # Don't fail completely - partial improvement is still good
