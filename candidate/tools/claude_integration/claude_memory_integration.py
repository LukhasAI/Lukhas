#!/usr/bin/env python3
"""
Claude Code Memory Integration
Integrates Claude Code conversations with LUKHAS memory system.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add LUKHAS to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from candidate.core.symbolic_tokens import SymbolicToken
    from memory.folding.advanced_folding import MemoryFold

    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("Warning: LUKHAS memory system not available. Using fallback storage.")


class ClaudeContextMemory:
    """Integrates Claude Code contexts with LUKHAS memory system."""

    def __init__(self):
        self.memory_dir = Path("/Users/agi_dev/Lukhas/memory/claude_contexts")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def create_memory_fold(self, context_data):
        """Create a memory fold for the Claude conversation."""
        if not MEMORY_AVAILABLE:
            return self.save_fallback(context_data)

        try:
            # Create symbolic tokens for the conversation
            tokens = []
            for msg in context_data.get("messages", []):
                token = SymbolicToken(
                    symbol=f"CLAUDE_{msg['role'].upper()}",
                    content=msg["content"],
                    metadata={
                        "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                        "role": msg["role"],
                        "context": "claude_code_chat",
                    },
                )
                tokens.append(token)

            # Create memory fold
            fold = MemoryFold(
                fold_type="claude_context",
                data={
                    "session_id": context_data.get("session_id"),
                    "timestamp": datetime.now().isoformat(),
                    "tokens": [t.to_dict() for t in tokens],
                    "metadata": context_data.get("metadata", {}),
                },
            )

            # Save fold
            fold_path = self.memory_dir / f"fold_{fold.fold_id}.json"
            with open(fold_path, "w") as f:
                json.dump(fold.to_dict(), f, indent=2)

            print(f"✅ Memory fold created: {fold.fold_id}")
            return fold_path

        except Exception as e:
            print(f"Error creating memory fold: {e}")
            return self.save_fallback(context_data)

    def save_fallback(self, context_data):
        """Fallback storage when memory system is unavailable."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"claude_context_{timestamp}.json"
        filepath = self.memory_dir / filename

        with open(filepath, "w") as f:
            json.dump(context_data, f, indent=2)

        print(f"✅ Context saved to: {filepath}")
        return filepath

    def create_markdown_export(self, context_data):
        """Export context as markdown for easy reading."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"claude_context_{timestamp}.md"
        filepath = self.memory_dir / filename

        with open(filepath, "w") as f:
            f.write(
                f"# Claude Code Context - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            # Session info
            f.write("## Session Information\n")
            metadata = context_data.get("metadata", {})
            for key, value in metadata.items():
                f.write(f"- {key}: {value}\n")
            f.write("\n")

            # Messages
            f.write("## Conversation\n\n")
            for msg in context_data.get("messages", []):
                f.write(f"### {msg['role']}\n")
                f.write(f"{msg['content']}\n\n")

            # Files modified
            if "files_modified" in context_data:
                f.write("## Files Modified\n")
                for file in context_data["files_modified"]:
                    f.write(f"- {file}\n")
                f.write("\n")

        print(f"✅ Markdown export created: {filepath}")
        return filepath


def main():
    """Main function to save Claude context."""
    print("Claude Code Context Memory Integration")
    print("=" * 50)

    # Example context structure
    example_context = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "metadata": {
            "repository": "LUKHAS ",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "purpose": "Save Claude Code chat context",
        },
        "messages": [
            {
                "role": "user",
                "content": "How can I save the context of a current frozen Claude Code chat?",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "role": "assistant",
                "content": "I'll help you save the context...",
                "timestamp": datetime.now().isoformat(),
            },
        ],
        "files_modified": [],
    }

    memory = ClaudeContextMemory()

    print("\nTo use this tool:")
    print("1. Copy your Claude Code conversation")
    print("2. Format it as JSON matching the example structure")
    print("3. Or use the manual input mode below\n")

    choice = input("Would you like to create a template now? (y/n): ")

    if choice.lower() == "y":
        # Create both memory fold and markdown
        fold_path = memory.create_memory_fold(example_context)
        md_path = memory.create_markdown_export(example_context)

        print("\n✅ Created template files:")
        print(f"   - Memory fold: {fold_path}")
        print(f"   - Markdown: {md_path}")
        print("\nYou can now edit these files with your actual conversation content.")


if __name__ == "__main__":
    main()
