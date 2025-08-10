"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: rem_visualizer.py
Advanced: rem_visualizer.py
Integration Date: 2025-5-31T07:55:28.209102
"""

from datetime import datetime
import os
import json
import streamlit as st
PP"""
rem_visualizer.py
-----------------
Visualizes symbolic REM cycles and dream collapses logged by Lucʌs.
Each phase is displayed with emoji, color, and optional collapse metadata.
"""


LOG_PATH = "data/dream_log.jsonl"


def load_dream_log():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


st.set_page_config(page_title="Lucʌs REM Visualizer", layout="centered")

st.markdown(
    """
    <style>
        body { background-color: #F3F4F6; color: #374151; font-family: 'Inter', sans-serif; }
        .rem-phase { background-color: #E5E7EB; padding: 1em; border-radius: 10px; margin-bottom: 1em; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌌 Lucʌs REM Cycle Viewer")
st.caption("Dream resonance visualized by symbolic state")

dreams = load_dream_log()

# Sidebar filters
st.sidebar.header("🔍 Filter Dreams")
phases = sorted(set(str(d.get("phase", "?")) for d in dreams))
selected_phase = st.sidebar.selectbox("REM Phase", ["All"] + phases)
collapse_only = st.sidebar.checkbox("Show collapse dreams only", value=False)
min_resonance = st.sidebar.slider("Minimum resonance", 0.0, 1.0, 0.0, 0.01)

# Filter dreams
filtered_dreams = []
for dream in dreams:
    if selected_phase != "All" and str(dream.get("phase", "?")) != selected_phase:
        continue
    if collapse_only and not dream.get("collapse_id"):
        continue
    if dream.get("resonance", 0.0) < min_resonance:
        continue
    filtered_dreams.append(dream)

# Display filtered results
if not filtered_dreams:
    st.info("No dreams match the selected filters.")
else:
    for dream in filtered_dreams[-10:]:
        symbol = dream.get("dream", "❔")
        collapse = dream.get("collapse_id", None)
        phase = dream.get("phase", "?")
        resonance = dream.get("resonance", 0.0)
        timestamp = dream.get("timestamp", "⏳")

        with st.container():
            st.markdown(f"""
            <div class='rem-phase'>
                <h3>REM Phase {phase} {symbol}</h3>
                <p><strong>Resonance:</strong> {resonance}</p>
                <p><strong>Collapse ID:</strong> {collapse or "-"}</p>
                <p><small>{timestamp}</small></p>
            </div>
            """, unsafe_allow_html=True)
"""
