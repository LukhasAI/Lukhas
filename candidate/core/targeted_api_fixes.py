#!/usr/bin/env python3
"""
🎯 Targeted API Fixes for Core LUKHAS Components

Based on validation results and API_INDEX.md, this script applies specific fixes
for the known API mismatches in the core distributed AI infrastructure.

Known Issues from validation_report.json:
1. ActorRef.send_message() → should be .tell()
2. EfficientCommunicationFabric missing total_messages attribute
3. EfficientCommunicationFabric missing send_large_data method
4. DistributedAIAgent missing from integrated_system.py
5. DistributedAIAgent.process_task() → should use colony.execute_task()
"""

import re
from pathlib import Path


def apply_actor_ref_fixes():
    """Fix ActorRef.send_message() calls to use .tell()"""
    print("🎯 Fixing ActorRef.send_message() → .tell()...")

    # Files that likely contain send_message calls
    test_files = [
        "research_validation_pack.py",
        "lukhas/core/test_coordination_simple.py",
    ]

    replacements = 0

    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            original_content = content

            # Pattern: actor_ref.send_message(...) → actor_ref.tell(...)
            pattern = r"(\w*actor_ref\w*)\.send_message\("
            replacement = r"\1.tell("

            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

            if new_content != original_content:
                # Count changes
                changes = len(re.findall(pattern, content, flags=re.IGNORECASE))
                replacements += changes

                # Backup and save
                backup_path = path.with_suffix(path.suffix + ".bak")
                path.rename(backup_path)
                path.write_text(new_content)

                print(f"  ✅ Fixed {changes} instances in {path.name} (backup: {backup_path.name})")

    print(f"  📊 Total ActorRef fixes applied: {replacements}")
    return replacements


def fix_communication_fabric():
    """Add missing methods to EfficientCommunicationFabric"""
    print("\n🎯 Adding missing methods to EfficientCommunicationFabric...")

    fabric_path = Path("lukhas/core/efficient_communication.py")
    if not fabric_path.exists():
        print("  ❌ EfficientCommunicationFabric file not found")
        return False

    content = fabric_path.read_text()

    # Check if total_messages is already in get_statistics
    if "total_messages" not in content:
        # Find the get_statistics method and add total_messages
        stats_pattern = r"(def get_statistics\(self\) -> Dict\[str, Any\]:[\s\S]*?return {[\s\S]*?)(}[\s\n]*?)"

        def add_total_messages(match):
            stats_dict = match.group(1)
            closing = match.group(2)

            # Add total_messages if not present
            if "total_messages" not in stats_dict:
                # Insert before the closing brace
                new_stats = stats_dict + '            "total_messages": self._message_count,\n            '
                return new_stats + closing
            return match.group(0)

        content = re.sub(stats_pattern, add_total_messages, content)

    # Check if send_large_data method exists
    if "def send_large_data" not in content:
        # Find the class definition and add the method
        class_pattern = r"(class EfficientCommunicationFabric[\s\S]*?)(\n\n\nclass|\Z)"

        def add_send_large_data(match):
            class_content = match.group(1)
            rest = match.group(2) if match.group(2) else ""

            # Add the method before the class ends
            new_method = '''
    async def send_large_data(self, recipient: str, data: bytes, chunk_size: int = \
    1024*1024) -> bool:
        """Send large data in chunks to prevent memory issues"""
        if len(data) <= chunk_size:
            # Small data, send normally
            return await self.send_message(recipient, data)

        # Split into chunks
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        chunk_id = str(uuid.uuid4())

        # Send metadata first
        metadata = {
            "type": "large_data_start",
            "chunk_id": chunk_id,
            "total_chunks": len(chunks),
            "total_size": len(data)
        }

        if not await self.send_message(recipient, metadata, MessagePriority.HIGH):
            return False

        # Send chunks
        for i, chunk in enumerate(chunks):
            chunk_msg = {
                "type": "large_data_chunk",
                "chunk_id": chunk_id,
                "chunk_index": i,
                "data": chunk
            }

            if not await self.send_message(recipient, chunk_msg, MessagePriority.HIGH):
                return False

        # Send completion message
        completion = {
            "type": "large_data_complete",
            "chunk_id": chunk_id
        }

        return await self.send_message(recipient, completion, MessagePriority.HIGH)
'''

            return class_content + new_method + rest

        content = re.sub(class_pattern, add_send_large_data, content, flags=re.DOTALL)

    # Add uuid import if needed for send_large_data
    if "send_large_data" in content and "import uuid" not in content:
        # Add import at the top
        import_pattern = r"(import [\w\s,]*?\n)"
        content = re.sub(import_pattern, r"\1import uuid\n", content, count=1)

    # Write back the updated content
    backup_path = fabric_path.with_suffix(".bak")
    fabric_path.rename(backup_path)
    fabric_path.write_text(content)

    print(f"  ✅ Updated EfficientCommunicationFabric (backup: {backup_path.name})")
    return True


def fix_integrated_system():
    """Fix DistributedAIAgent import and add missing methods"""
    print("\n🎯 Fixing integrated_system.py imports and methods...")

    system_path = Path("lukhas/core/integrated_system.py")
    if not system_path.exists():
        print("  ❌ integrated_system.py not found")
        return False

    content = system_path.read_text()

    # Add DistributedAIAgent class if it doesn't exist
    if "class DistributedAIAgent" not in content:
        # Add the class at the end before the demo function
        agent_class = '''

class DistributedAIAgent:
    """Legacy wrapper for backward compatibility with tests"""

    def __init__(self, agent_id: str = "legacy-agent"):
        self.agent_id = agent_id
        self.system = None

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using the distributed system - legacy compatibility method"""
        if not self.system:
            # Create a temporary system for compatibility
            self.system = DistributedAISystem(f"legacy-{self.agent_id}")
            await self.system.start()

            # Create a default reasoning colony
            try:
                await self.system.create_colony("default-reasoning", ReasoningColony)
            except Exception:
                pass  # Colony might already exist or class not available

        # Execute the task through the distributed system
        return await self.system.execute_distributed_task(task_data)

    async def close(self):
        """Clean up the legacy agent"""
        if self.system:
            await self.system.stop()
'''

        # Insert before the demo function
        demo_pattern = r"(\n\nasync def demo_integrated_system)"
        content = re.sub(demo_pattern, agent_class + r"\1", content)

    # Write back
    backup_path = system_path.with_suffix(".bak")
    system_path.rename(backup_path)
    system_path.write_text(content)

    print(f"  ✅ Updated integrated_system.py with DistributedAIAgent (backup: {backup_path.name})")
    return True


def update_validation_script():
    """Update the validation script to use correct APIs"""
    print("\n🎯 Updating research_validation_pack.py...")

    validation_path = Path("research_validation_pack.py")
    if not validation_path.exists():
        print("  ❌ research_validation_pack.py not found")
        return False

    content = validation_path.read_text()

    # Fix import - add DistributedAIAgent import
    if "DistributedAIAgent" in content and "from candidate.core.integrated_system import" in content:
        # Import pattern already exists, make sure DistributedAIAgent is included
        import_pattern = r"from core\.core\.integrated_system import ([^\n]*)"

        def fix_import(match):
            imports = match.group(1)
            if "DistributedAIAgent" not in imports:
                return f"from candidate.core.integrated_system import {imports}, DistributedAIAgent"
            return match.group(0)

        content = re.sub(import_pattern, fix_import, content)

    # Fix the Actor System test that uses send_message
    if "actor_ref.send_message" in content:
        content = content.replace("actor_ref.send_message", "actor_ref.tell")
        print("  ✅ Fixed actor_ref.send_message → .tell()")

    # Fix the communication fabric test for total_messages
    if "fabric_stats['total_messages']" in content:
        # This should work after we fix the EfficientCommunicationFabric class
        print("  ✅ total_messages access should work after fabric fix")

    # Write back
    backup_path = validation_path.with_suffix(".bak")
    validation_path.rename(backup_path)
    validation_path.write_text(content)

    print(f"  ✅ Updated validation script (backup: {backup_path.name})")
    return True


def main():
    """Apply all targeted API fixes"""
    print("🚀 LUKHAS Targeted API Fixes - Phase 1 Implementation\n")
    print("This script applies specific fixes for known API mismatches.\n")

    fixes_applied = 0

    # Apply each fix
    try:
        fixes_applied += apply_actor_ref_fixes()

        if fix_communication_fabric():
            fixes_applied += 1

        if fix_integrated_system():
            fixes_applied += 1

        if update_validation_script():
            fixes_applied += 1

    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

    print(f"\n✅ Applied {fixes_applied} targeted fixes!")
    print("\n📋 Next steps:")
    print("1. Run the validation script to test fixes")
    print("2. Check that all tests pass")
    print("3. Update API_INDEX.md if needed")
    print("4. Proceed to Phase 2 of the strategic plan")

    return True


if __name__ == "__main__":
    main()
