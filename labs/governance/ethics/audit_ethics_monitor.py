#!/usr/bin/env python3
"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Quick audit script for ethics monitor without terminal complications.
"""
import sys

sys.path.append("/Users/A_G_I/L_U_K_H_A_C_O_X")


def main():
    """Audit the ethics monitor file."""
    file_path = "/Users/A_G_I/L_U_K_H_A_C_O_X/lukhas/core/security/ethics_monitor.py"

    print("🔍 Auditing enhanced ethics monitor...")
    print(f"📁 File: {file_path}")
    print("=" * 60)

    try:
        # Import the audit function and run it
        import asyncio

        from lukhas.tools.lukhas_audit import audit_file_implementation

        # Run the audit
        result = asyncio.run(audit_file_implementation(file_path))

        if result:
            print(f"📊 Current Score: {result.get('score', 'N/A')}")
            print(f"📈 Target Score: {result.get('target_score', 'N/A')}")
            print(f"📋 Status: {result.get('status', 'N/A')}")
            print("=" * 60)

            if "improvements" in result:
                print("🚀 Improvement Suggestions:")
                for i, improvement in enumerate(result["improvements"], 1):
                    print(f"{i}. {improvement}")

        else:
            print("❌ Audit failed or no results returned")

    except Exception as e:
        print(f"❌ Error running audit: {e}")
        print("📋 Let's continue with batch analysis...")


if __name__ == "__main__":
    main()
