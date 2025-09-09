"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                   LUCΛS :: Dream Export Streamlit Dashboard                 │
│         Exports symbolic dream logs based on tag, tier, or emotion          │
│               Author: Gonzo R.D.M | Version: 1.0 | Symbolic UI              │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

# import streamlit as st  # TODO: Install or implement streamlit
import json
import os

DREAM_LOG_PATH = "core/logs/dream_log.jsonl"
EXPORT_PATH = "exports/filtered_dreams.jsonl"

st.set_page_config(page_title="LUCΛS | Dream Export", page_icon="🌙")
st.title("🌙 Symbolic Dream Exporter")
st.markdown("Filter and export symbolic dreams for analysis, reflection, or narration.")

# Filters
filter_tag = st.text_input("🔖 Filter by Tag (optional)")
filter_tier = st.selectbox("🔐 Minimum Tier", options=[0, 1, 2, 3, 4, 5], index=0)
suggest_voice_only = st.checkbox("🎙 Only dreams marked for Lukhas narration (suggest_voice: true)")

# Export trigger
if st.button("📤 Export Filtered Dreams"):
    if not os.path.exists(DREAM_LOG_PATH):
        st.error("No dream log found.")
    else:
        os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
        exported = []

        with open(DREAM_LOG_PATH) as f:
            for line in f:
                dream = json.loads(line)
                if dream.get("tier", 0) < filter_tier:
                    continue
                if filter_tag and filter_tag not in dream.get("tags", []):
                    continue
                if suggest_voice_only and not dream.get("suggest_voice", False):
                    continue
                exported.append(dream)

        if exported:
            with open(EXPORT_PATH, "w") as out:
                for d in exported:
                    out.write(json.dumps(d) + "\n")
            st.success(f"✅ Exported {len(exported)} dreams to `{EXPORT_PATH}`")
        else:
            st.warning("⚠️ No matching dreams found.")