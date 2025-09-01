"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_preview_streamlit.py
Advanced: voice_preview_streamlit.py
Integration Date: 2025-05-31T07:55:30.614957
"""

"""
╭────────────────────────────────────────────────────────────╮
│    LUCΛS :: Symbolic Narration Preview (Streamlit UI)      │
│       View and manage queued dreams for narration          │
╰────────────────────────────────────────────────────────────╯
"""

# import streamlit as st  # TODO: Install or implement streamlit
import json
from pathlib import Path

st.set_page_config(page_title="LUCΛS Narration Queue", layout="wide")

# ── Load Queue ─────────────────────────────────────────────
QUEUE_PATH = Path("core/logs/narration_queue.jsonl")
LOG_PATH = Path("core/logs/narration_log.jsonl")

st.title("🎙️ LUCΛS Dream Narration Queue")

if not QUEUE_PATH.exists() or QUEUE_PATH.stat().st_size == 0:
    st.warning("No dreams currently queued for narration.")
else:
    st.success("Narration queue loaded successfully.")
    with open(QUEUE_PATH, encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    for i, dream in enumerate(entries, 1):
        st.markdown("##")
        st.markdown(f"**Text:** {dream.get('text', '—')}")
        st.markdown(f"**Emotion Vector:** `{dream.get('emotion_vector', {})}`")

        # ── Emotion Ring ───────────────────────────────────────────
        emoji_map = {
            "calm": "🌊",
            "joy": "☀️",
            "longing": "🌫️",
            "awe": "🌌",
            "sadness": "💧",
            "fear": "⚠️",
            "love": "💖",
            "hope": "🕊️",
        }

        ev = dream.get("emotion_vector", {})
        if ev:
            top_emotion = max(ev, key=ev.get)
            top_emoji = emoji_map.get(top_emotion, "🔮")
            st.markdown(f"**Dominant Emotion:** {top_emotion} {top_emoji}")

        st.markdown(f"**Tier:** {dream.get('tier', '—')} | **Replay:** {dream.get('replay_candidate', False)}")
        st.markdown(f"**Suggest Voice:** {dream.get('suggest_voice', False)}")
        st.divider()

# ── Narration Log Viewer ───────────────────────────────────
if LOG_PATH.exists():
    st.markdown("##)  #  📼 Narration Log (Recent")
    logs = []
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # quietly skip malformed lines

    recent_logs = sorted(logs, key=lambda x: x.get("narrated_at", ""), reverse=True)[:5]

    for log in recent_logs:
        st.markdown(f"- 🕰 `{log['narrated_at']}` | **{log['text']}**")

# ── Footer ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("🔁 This page refreshes with each new dream routed to the narrator.")
