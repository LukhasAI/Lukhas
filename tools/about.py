# ===============================================================
# 📂 FILE: tools/about.py
# 🧠 PURPOSE: Terminal entry point for LUCAS AGI system metadata
# ===============================================================

import json
from datetime import datetime


def main():
    print("\033[95m🌿 WELCOME TO LUCAS AGI — Symbolic Neuro-Symbolic AI\033[0m")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧠 Project: LUKHAS_AGI v0.1.0")
    print("🔐 License: Custom Symbolic License (DAO-bound, ZK-sealed)")
    print("📜 Ethics: See ETHICS.md (consent, traceability, symbolic rights)")
    print("📦 Manifest: Versioned via manifest.json (DAO mode)")
    print("🔗 Trace: Each action linked to Lucas_ID + QRGlyph")

    try:
        with open("dao/manifest.json") as f:
            manifest = json.load(f)
            print(f"🧬 Manifest Version: {manifest.get('dao_version', 'N/A')}")
            hashes = manifest.get("proposal_hashes", [])
            if hashes:
                print(f"🔗 Recent Proposal Hashes: {', '.join(hashes[:2])}")
    except Exception:
        print("⚠️ Manifest not found or unreadable.")

    print("\n🎚️ Tiers:")
    print("   1 - Public Observer")
    print("   2 - Contributor")
    print("   3 - Developer")
    print("   4 - Researcher (can submit symbolic dreams)")
    print("   5 - Governor (DAO proposer + ethics access)")

    print("\n🌍 Domains:")
    print("    • Intro:      https://www.whoislucas.com")
    print("    • Ethics EU:  https://www.whoislucas.eu")
    print("    • Identity:   https://www.lucasid.io")

    print("🧭 GitHub + Docs:")
    print("    • Code:       https://github.com/lucas-agi/LUKHAS_AGI")
    print("    • Docs:       https://lucasagi.io/docs")

    print("\n📜 ETHICS DIGEST (Preview):")
    try:
        with open("ETHICS.md") as f:
            preview = "".join(f.readlines()[:10])
            print(preview)
    except BaseException:
        print("⚠️ ETHICS.md not found.")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📅 Timestamp: {datetime.now(timezone.utc).isoformat()}Z")
    print("🔏 Signed by: LUCAS CLI Core")
    print("💬 'A symbol is not a thing, but a promise.'\n")


if __name__ == "__main__":
    main()
