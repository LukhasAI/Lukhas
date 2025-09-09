"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_export_streamlit.py
Advanced: dream_export_streamlit.py
Integration Date: 2025-05-31T07:55:30.537549
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                LUCΛS DREAM EXPORT DASHBOARD — STREAMLIT MODULE               │
│                       File: dream_export_streamlit.py                        │
│                      Author: Gonzo R.D.M | Version: v1.0                     │
╰──────────────────────────────────────────────────────────────────────────────╯

Symbolic Dream Exporter for LUCΛS — filters by tier, tags, emoji, or narration
intent and allows selective exporting to a .jsonl file.
"""

# import streamlit as st  # TODO: Install or implement streamlit
import json
from pathlib import Path

DATA_PATH = Path("core/sample_payloads/sample_payload_batch_dreams.json")
EXPORT_PATH = Path("exports/filtered_dreams_export.jsonl")

st.set_page_config(page_title="LUCΛS Dream Export", page_icon="🌙")
st.title("🌙 Symbolic Dream Export Panel")

# Load dreams
if DATA_PATH.exists():
    with open(DATA_PATH) as f:
        dreams = [json.loads(line) for line in f if line.strip()]
else:
    st.error("Dream payload file not found.")
    st.stop()

# Filter controls
st.sidebar.header("🔍 Filter Dreams")
all_tags = sorted({tag for d in dreams for tag in d.get("tags", [])})
all_emojis = sorted({d.get("emoji") for d in dreams if "emoji" in d})
tiers = sorted({d.get("tier") for d in dreams if "tier" in d})

selected_tiers = st.sidebar.multiselect("Filter by Tier", tiers)
selected_tags = st.sidebar.multiselect("Filter by Tags", all_tags)
selected_emojis = st.sidebar.multiselect("Filter by Emoji", all_emojis)
filter_voice = st.sidebar.checkbox("Only dreams marked for narration (suggest_voice)", value=True)

# Apply filters
filtered = [
    d
    for d in dreams
    if (not selected_tiers or d.get("tier") in selected_tiers)
    and (not selected_tags or any(tag in d.get("tags", []) for tag in selected_tags))
    and (not selected_emojis or d.get("emoji") in selected_emojis)
    and (not filter_voice or d.get("suggest_voice"))
]

st.success(f"{len(filtered)} dreams match your filters.")
st.json(filtered[:3], expanded=False)

# Export
if st.button("📤 Export Filtered Dreams"):
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_PATH, "w") as f:
        for d in filtered:
            f.write(json.dumps(d) + "\n")
    st.success(f"Exported to {EXPORT_PATH}")