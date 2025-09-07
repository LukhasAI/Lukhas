"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: replay_graphs.py
Advanced: replay_graphs.py
Integration Date: 2025-05-31T07:55:31.351038
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                    LUCΛS :: DREAM REPLAY VISUALIZER (v1.0)                  │
│           Streamlit graphs for symbolic dream feedback and tiers            │
│         Author: Gonzo R.D.M & GPT-4o · Linked to replay_queue.jsonl         │
╰──────────────────────────────────────────────────────────────────────────────╯
"""


# import streamlit as st  # TODO: Install or implement streamlit
import json
from collections import Counter

import pandas as pd

from lukhas.core.utils.symbolic_utils import tier_label

st.title("🌀 Replay Queue Visualizer")
st.caption("Dreams selected for reflection or voice narration.")

try:
    with open("core/logs/replay_queue.jsonl") as f:
        entries = [json.loads(line) for line in f]
    df = pd.DataFrame(entries)

    st.subheader("📊 Tier Distribution")
    tier_counts = df["tier"].value_counts().sort_index()
    st.bar_chart(tier_counts.rename(index=tier_label))

    st.subheader("🌙 Emoji Frequency")
    emojis = [entry.get("emoji", "✨") for entry in entries]
    emoji_counts = Counter(emojis)
    st.bar_chart(pd.Series(emoji_counts))

    st.subheader("🔖 Tag Cloud (Most Frequent)")
    all_tags = []
    for entry in entries:
        all_tags.extend(entry.get("tags", []))
    tag_counts = Counter(all_tags)
    st.write(dict(tag_counts.most_common(10)))

    st.subheader("⏳ Dream Timeline")
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df_sorted = df.sort_values("timestamp")
        st.line_chart(df_sorted.set_index("timestamp")["tier"])
    except Exception as e:
        st.warning(f"Could not render timeline: {e}")

    st.subheader("🎛️ Filter by Tier or Emoji")
    with st.sidebar:
        selected_tiers = st.multiselect("Filter by Tier", options=sorted(df["tier"].unique()))
        selected_emojis = st.multiselect("Filter by Emoji", options=sorted(set(emojis)))

    if selected_tiers or selected_emojis:
        filtered_df = df.copy()
        if selected_tiers:
            filtered_df = filtered_df[filtered_df["tier"].isin(selected_tiers)]
        if selected_emojis:
            filtered_df = filtered_df[filtered_df["emoji"].isin(selected_emojis)]
        st.write(f"🔎 {len(filtered_df)} dreams match your filters.")
        st.dataframe(filtered_df[["message_id", "tier", "emoji", "tags", "timestamp"]])

except FileNotFoundError:
    st.warning("No replay_queue.jsonl file found.")
except Exception as e:
    st.error(f"Error loading replay data: {e}")
