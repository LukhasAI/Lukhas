#!/usr/bin/env python3
"""
🔧 Validation Script API Fixes

Fixes the remaining API mismatches in research_validation_pack.py:
1. send_message() → tell()
2. create_agent() → create_colony()
3. total_messages attribute access
4. send_large_data() parameters
"""
import re
from pathlib import Path


def fix_validation_script():
    """Apply all remaining fixes to the validation script"""
    print("🔧 Fixing remaining API issues in validation script...")

    script_path = Path("research_validation_pack.py")
    if not script_path.exists():
        print("  ❌ research_validation_pack.py not found")
        return False

    content = script_path.read_text()
    original_content = content

    # 1. Fix send_message calls to tell
    send_message_pattern = r"(\w+)\.send_message\(([^)]+)\)"

    def replace_send_message(match):
        obj = match.group(1)
        args = match.group(2)

        # For actor refs, convert to tell
        if "agent_ref" in obj or "actor_ref" in obj:
            # Extract the message dict from args
            if args.startswith("{") and args.endswith("}"):
                return f'{obj}.tell("task", {args})'
            else:
                return f'{obj}.tell("task", {{{args})'
        else:
            # For fabric, keep as is
            return match.group(0)

    content = re.sub(send_message_pattern, replace_send_message, content)

    # 2. Fix create_agent calls to create_colony
    content = re.sub(
        r"await (\w*system\w*)\.create_agent\(",
        r'await \1.create_colony("validation-colony", ReasoningColony, ',
        content,
    )

    # Also fix the standalone create_agent call
    content = re.sub(
        r"(\w+)\.create_agent\(\[[^\]]+\], [^)]+\)",
        r'await \1.create_colony("validation-colony", ReasoningColony)',
        content,
    )

    # 3. Fix total_messages access - this should work after we fix the fabric
    # The issue is we need to ensure the attribute exists in get_statistics

    # 4. Fix send_large_data parameter
    content = re.sub(
        r"await fabric\.send_large_data\(([^,]+), ([^,]+), use_p2p=True\)",
        r"await fabric.send_large_data(\1, \2)",
        content,
    )

    # 5. Add necessary imports for ReasoningColony if not present
    if "ReasoningColony" in content and "from core.colonies.reasoning_colony import ReasoningColony" not in content:
        # Add import after the existing imports
        import_section = content.find("from core.integrated_system")
        if import_section != -1:
            end_of_line = content.find("\n", import_section)
            content = (
                content[:end_of_line]
                + "\nfrom candidate.core.colonies.reasoning_colony import ReasoningColony"
                + content[end_of_line:]
            )

    # Write the fixed content
    if content != original_content:
        backup_path = script_path.with_suffix(".fixed.py")
        script_path.rename(backup_path)
        script_path.write_text(content)

        print(f"  ✅ Fixed validation script (backup: {backup_path.name})")
        return True
    else:
        print("  📋 No changes needed in validation script")
        return False


def fix_efficient_communication():
    """Fix the EfficientCommunicationFabric to properly include total_messages"""
    print("\n🔧 Fixing EfficientCommunicationFabric total_messages...")

    fabric_path = Path("lukhas/core/efficient_communication.py")
    if not fabric_path.exists():
        print("  ❌ efficient_communication.py not found")
        return False

    content = fabric_path.read_text()

    # Check if _message_count is initialized in __init__
    if "_message_count" not in content:
        # Add message count tracking to __init__
        init_pattern = (
            r'(def __init__\(self[^\)]*\):[^\n]*\n(?:[ ]*"""[\s\S]*?"""\n)?)([\s\S]*?)(?=\n[ ]*def|\n[ ]*async def|\Z)'
        )

        def add_message_count(match):
            init_signature = match.group(1)
            init_body = match.group(2)

            # Add message count initialization
            if "_message_count = 0" not in init_body:
                # Find where to insert (after basic initialization)
                lines = init_body.split("\n")
                insert_index = -1
                for i, line in enumerate(lines):
                    if "self." in line and "=" in line:
                        insert_index = i + 1

                if insert_index > 0:
                    lines.insert(insert_index, "        self._message_count = 0")
                else:
                    lines.insert(1, "        self._message_count = 0")

                return init_signature + "\n".join(lines)
            return match.group(0)

        content = re.sub(init_pattern, add_message_count, content, flags=re.MULTILINE)

    # Update send_message to increment the counter
    if "_message_count += 1" not in content:
        send_msg_pattern = r"(async def send_message\([^\)]*\)[^\{]*\{[^\}]*)(return [^\n]*?)"

        def add_counter_increment(match):
            method_body = match.group(1)
            return_stmt = match.group(2)

            # Add counter increment before return
            if "self._message_count += 1" not in method_body:
                return method_body + "\n        self._message_count += 1\n        " + return_stmt
            return match.group(0)

        content = re.sub(send_msg_pattern, add_counter_increment, content, flags=re.DOTALL)

    # Write the updated content
    backup_path = fabric_path.with_suffix(".final.bak")
    fabric_path.rename(backup_path)
    fabric_path.write_text(content)

    print(f"  ✅ Updated EfficientCommunicationFabric (backup: {backup_path.name})")
    return True


def main():
    """Apply all validation script fixes"""
    print("🚀 Applying Validation Script API Fixes\n")

    fixes_applied = 0

    if fix_validation_script():
        fixes_applied += 1

    if fix_efficient_communication():
        fixes_applied += 1

    print(f"\n✅ Applied {fixes_applied} validation fixes!")
    print("\n📋 Next: Run validation script to test all fixes")

    return fixes_applied > 0


if __name__ == "__main__":
    main()
