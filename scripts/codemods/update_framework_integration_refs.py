#!/usr/bin/env python3
"""
Update trinity_framework_integration references to constellation_framework_integration
"""
import os

def update_framework_integration_refs():
    """Update trinity_framework_integration to constellation_framework_integration"""

    # Target specific files that likely have these references
    target_files = [
        "candidate/core/performance/performance_orchestrator.py",
        "candidate/consciousness/reflection/orchestration_service.py",
        "candidate/governance/security/privacy_guardian.py",
        "agents_external/CLAUDE/claude_code_agent_team.yaml",
        "phase1_verification_pack/documentation/EXECUTION_SUMMARY.md"
    ]

    updated_count = 0

    for file_path in target_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace the pattern
                new_content = content.replace('trinity_framework_integration', 'constellation_framework_integration')
                new_content = new_content.replace('test_trinity_validation', 'test_constellation_validation')

                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Updated: {file_path}")
                    updated_count += 1
                else:
                    print(f"⏭️  No changes: {file_path}")

            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    print(f"\n🎯 Updated {updated_count} files")

if __name__ == "__main__":
    update_framework_integration_refs()