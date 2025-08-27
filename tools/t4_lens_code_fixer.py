#!/usr/bin/env python3
"""
T4 Lens Code Quality Automation
Based on the four pillars: Scale, Safety, Rigor, Experience
"""

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path


class T4LensCodeFixer:
    def __init__(self):
        self.base_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
        self.verification_path = self.base_path / "verification_artifacts"
        self.verification_path.mkdir(exist_ok=True)

    def get_current_sha(self):
        """SCIENTIFIC RIGOR: SHA-bound verification"""
        try:
            result = subprocess.run(["git", "rev-parse", "HEAD"],
                                  capture_output=True, text=True, cwd=self.base_path)
            return result.stdout.strip()[:8]
        except Exception:
            return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]

    def create_verification_artifact(self, operation, before_count, after_count, files_affected):
        """SCIENTIFIC RIGOR: Evidence-based tracking"""
        sha = self.get_current_sha()
        artifact = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "sha": sha,
            "before_count": before_count,
            "after_count": after_count,
            "improvement": before_count - after_count,
            "files_affected": files_affected,
            "success": after_count < before_count
        }

        artifact_file = self.verification_path / f"{sha}_{operation}.json"
        with open(artifact_file, "w") as f:
            json.dump(artifact, f, indent=2)

        return artifact

    def get_ruff_stats(self):
        """Get current Ruff statistics"""
        try:
            result = subprocess.run(["ruff", "check", ".", "--statistics"],
                                  capture_output=True, text=True, cwd=self.base_path)
            lines = result.stdout.strip().split("\n")
            total_line = [line for line in lines if "Found" in line and "errors" in line]
            if total_line:
                count = int(total_line[0].split()[1])
                return count, lines
            return 0, lines
        except Exception as e:
            print(f"Error getting Ruff stats: {e}")
            return None, []

    def run_safe_fixes(self):
        """CONSTITUTIONAL SAFETY: Apply only safe, automated fixes"""
        print("🛡️ T4 LENS: Constitutional Safety - Running Safe Fixes Only")

        before_count, _ = self.get_ruff_stats()

        # Run safe fixes only (fail-closed approach)
        subprocess.run(["ruff", "check", ".", "--fix"],
                      capture_output=True, text=True, cwd=self.base_path)

        after_count, stats = self.get_ruff_stats()

        # Create verification artifact
        artifact = self.create_verification_artifact(
            "safe_fixes", before_count, after_count,
            ["automated_safe_fixes"]
        )

        print(f"   ✅ Before: {before_count} issues")
        print(f"   ✅ After:  {after_count} issues")
        print(f"   ✅ Fixed:  {artifact['improvement']} issues")
        print(f"   📋 Artifact: {artifact['sha']}_safe_fixes.json")

        return artifact

    def analyze_by_category(self):
        """EXPERIENCE DISCIPLINE: Simple, opinionated categorization"""
        print("\n✨ T4 LENS: Experience Discipline - Issue Categorization")

        _, stats = self.get_ruff_stats()
        categories = {
            "CRITICAL_BLOCKERS": [],      # Syntax errors, undefined names
            "AUTOMATION_READY": [],       # Import fixes, unused imports
            "SAFETY_REVIEW": [],          # Bare except, error handling
            "POLISH_ITEMS": []           # Style, naming, minor issues
        }

        for line in stats:
            if any(code in line for code in ["invalid-syntax", "undefined-name"]):
                categories["CRITICAL_BLOCKERS"].append(line.strip())
            elif any(code in line for code in ["E402", "F401", "unused-import"]):
                categories["AUTOMATION_READY"].append(line.strip())
            elif any(code in line for code in ["E722", "bare-except"]):
                categories["SAFETY_REVIEW"].append(line.strip())
            elif line.strip() and line[0].isdigit():
                categories["POLISH_ITEMS"].append(line.strip())

        for category, items in categories.items():
            if items:
                print(f"\n   📂 {category}: {len(items)} issues")
                for item in items[:3]:  # Show top 3
                    print(f"      {item}")
                if len(items) > 3:
                    print(f"      ... and {len(items) - 3} more")

        return categories

    def run_t4_analysis(self):
        """SCALE & AUTOMATION: Complete T4 Lens analysis"""
        print("🎯 T4 LENS: Comprehensive Code Quality Analysis")
        print("=" * 50)

        # Get baseline
        total_issues, _ = self.get_ruff_stats()
        print(f"📊 Current Issues: {total_issues}")

        # Apply Constitutional Safety
        safe_fixes_artifact = self.run_safe_fixes()

        # Apply Experience Discipline
        categories = self.analyze_by_category()

        # Scientific Rigor Summary
        print("\n🧪 T4 LENS: Scientific Rigor - Verification")
        print(f"   📋 SHA: {safe_fixes_artifact['sha']}")
        print(f"   📈 Improvement: {safe_fixes_artifact['improvement']} issues fixed")
        print(f"   ✅ Success Rate: {safe_fixes_artifact['success']}")

        # Scale & Automation Recommendations
        print("\n⚡ T4 LENS: Scale & Automation - Next Steps")
        critical_count = len(categories.get("CRITICAL_BLOCKERS", []))
        automation_count = len(categories.get("AUTOMATION_READY", []))

        print(f"   🔥 Priority 1: {critical_count} critical blockers")
        print(f"   🤖 Priority 2: {automation_count} automation-ready fixes")
        print("   🛡️ Priority 3: Safety review items")
        print("   ✨ Priority 4: Polish items")

if __name__ == "__main__":
    fixer = T4LensCodeFixer()
    fixer.run_t4_analysis()
