# ΛUDIT: Validates commit messages for symbolic compliance

import re

REQUIRED_TAGS = ["ΛORIGIN_AGENT", "ΛTASK_ID", "ΛCOMMIT_WINDOW", "ΛPROVED_BY"]


def validate_commit_message(message: str) -> bool:
    for tag in REQUIRED_TAGS:
        if not re.search(rf"{tag}:\s*\S+", message):
            print(f"❌ Missing required tag: {tag}")
            return False
    print("✅ All required LUKHAS-tags found")
    return True


# Example usage
if __name__ == "__main__":
    test_commit = """
    Fix: Symbolic memory correction

    ΛORIGIN_AGENT: Jules-07
    ΛTASK_ID: 188
    ΛCOMMIT_WINDOW: pre-audit
    ΛPROVED_BY: Human Overseer (GRDM)
    """
    validate_commit_message(test_commit)
