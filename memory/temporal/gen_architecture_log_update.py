"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : gen_architecture_log_update.py                            │
│ 🧾 DESCRIPTION : Auto-update architecture_change_log.md with new entries   │
│ 🧩 TYPE        : Developer Utility       🔧 VERSION: v1.0.0                 │
│ 🖋️ AUTHOR      : LUCAS SYSTEMS          📅 UPDATED: 2025-04-28              │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - Standard Python                                                        │
└────────────────────────────────────────────────────────────────────────────┘
"""

import datetime

ARCHITECTURE_LOG_FILE = "logs/architecture/architecture_change_log.md"


def add_architecture_log_entry(change_summary, affected_modules):
    """Appends a new change entry into the protected architecture change log."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    entry = f"| {today} | {change_summary} | {affected_modules} |\n"

    try:
        with open(ARCHITECTURE_LOG_FILE) as f:
            contents = f.readlines()

        # Insert the new log entry after the 'Change History' header
        updated_contents = []
        inserted = False
        for line in contents:
            updated_contents.append(line)
            if (
                not inserted
                and line.strip()
                == "| Date         | Change Summary                                           | Module/Folder Affected         |"
            ):
                updated_contents.append(entry)
                inserted = True

        if not inserted:
            raise Exception("Failed to locate insertion point in architecture log.")

        with open(ARCHITECTURE_LOG_FILE, "w") as f:
            f.writelines(updated_contents)

        print(f"✅ Architecture log updated successfully on {today}!")

    except FileNotFoundError:
        print(
            f"❌ Architecture log file not found at {ARCHITECTURE_LOG_FILE}. Please check your paths."
        )
    except Exception as e:
        print(f"❌ Error updating architecture log: {e}")


# ==============================================================================
# 💻 USAGE EXAMPLE
# ==============================================================================

if __name__ == "__main__":
    print("\n📖 LUKHAS_AGI_3 Architecture Log Update")
    change_summary = input("📝 Enter a brief change summary: ")
    affected_modules = input("📂 Enter affected module(s)/folder(s): ")
    add_architecture_log_entry(change_summary, affected_modules)
