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

import json
import logging
import time
from pathlib import Path

# ΛTAG: streamlit_fallback, memory_ui

logger = logging.getLogger("ΛTRACE.memory.temporal.output_log")
logger.addHandler(logging.NullHandler())

try:  # ΛTAG: dependency_check
    import streamlit as st  # type: ignore[import-untyped]

    STREAMLIT_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on environment
    STREAMLIT_AVAILABLE = False
    st = None  # type: ignore[assignment]
    logger.warning(
        "Streamlit not available; Lukhas Output Log Viewer UI disabled."
    )

LOG_PATH = Path("logs/lukhas_output_log.jsonl")


def _render_streamlit_ui() -> None:
    """Render the interactive Streamlit interface."""

    st.title("🧠 Lukhas Output Log Viewer")

    if LOG_PATH.exists():
        with LOG_PATH.open(encoding="utf-8") as log_file:
            lines = log_file.readlines()

        if not lines:
            st.info("No symbolic outputs recorded yet.")
        else:
            message_types = sorted(
                {
                    json.loads(line).get("type", "unknown")
                    for line in lines
                    if line.strip()
                }
            )
            selected_type = st.selectbox(
                "🔍 Filter by Type", options=["All", *message_types]
            )

            search_term = st.text_input(
                "🔎 Search by keyword (input/output):"
            ).lower()

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
                    st.markdown(f"**📥 Input:** {entry.get('input', '')}")
                    st.markdown("**📤 Output:**")
                    st.code(entry.get("output", ""), language="markdown")
                except Exception as parse_err:  # pragma: no cover - UI reporting
                    st.warning(f"⚠️ Error reading entry: {parse_err}")

        st.caption("⏳ Auto-refreshes every 30 seconds. Press R to refresh manually.")
        time.sleep(30)
        st.experimental_rerun()
    else:
        st.error("Log file not found. Try generating a symbolic message first.")


def _render_cli_notice() -> None:
    """Emit a CLI notice when Streamlit is unavailable."""

    message = (
        "Streamlit is not installed. Install 'streamlit' to run the Lukhas Output Log Viewer.\n"
        f"Log path: {LOG_PATH}"
    )
    logger.info(message)
    print(message)
    # TODO: Provide an interactive CLI fallback for environments without Streamlit support.


if STREAMLIT_AVAILABLE:
    _render_streamlit_ui()
else:
    _render_cli_notice()
