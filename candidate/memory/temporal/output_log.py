"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhas_output_log.py
Advanced: lukhas_output_log.py
Integration Date: 2025-05-31T07:55:28.280860
"""

# import streamlit as st  # TODO: Install or implement streamlit
import json
import os
import time

st.title("🧠 Lukhas Output Log Viewer")

log_path = "logs/lukhas_output_log.jsonl"

if os.path.exists(log_path):
    with open(log_path) as f:
        lines = f.readlines()

    if not lines:
        st.info("No symbolic outputs recorded yet.")
    else:
        # Add filter options
        message_types = sorted({json.loads(line).get("type", "unknown") for line in lines if line.strip()})
        selected_type = st.selectbox("🔍 Filter by Type", options=["All", *message_types])

        search_term = st.text_input("🔎 Search by keyword (input/output):").lower()

        for line in reversed(lines[-200:]):
            try:
                entry = json.loads(line)
                entry_type = entry.get("type", "unknown")
                if selected_type != "All" and entry_type != selected_type:
                    continue
                if search_term and search_term not in json.dumps(entry).lower():
                    continue

                timestamp = entry.get("timestamp", "⏳ Not timestamped")
                tier = entry.get("tier", "🎚️ Unknown")

                st.markdown("----")
                st.markdown(f"**🕒 Timestamp:** `{timestamp}`")
                st.markdown(f"**🎚️ Tier:** `{tier}`")
                st.markdown(f"**📝 Type:** `{entry_type}`")
                st.markdown(f"**📥 Input:** {entry.get('input', ''}")
                st.markdown("**📤 Output:**")
                st.code(entry.get("output", ""), language="markdown")
            except Exception as parse_err:
                st.warning(f"⚠️ Error reading entry: {parse_err}")

    st.caption("⏳ Auto-refreshes every 30 seconds. Press R to refresh manually.")
    time.sleep(30)
    st.experimental_rerun()
else:
    st.error("Log file not found. Try generating a symbolic message first.")
