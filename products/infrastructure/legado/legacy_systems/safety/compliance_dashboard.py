"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: compliance_dashboard.py
Advanced: compliance_dashboard.py
Integration Date: 2025-05-31T07:55:27.745437
"""

# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: compliance_dashboard.py
# 🛡️ PURPOSE: Institutional compliance viewer for emergency logs and GDPR status
# 🎯 AUDIENCE: Governance reviewers (e.g. Sam Altman, auditors)
# ════════════════════════════════════════════════════════════════════════
import json
import logging
import os
import warnings
from pathlib import Path
from typing import Any, Iterable, Sequence

warnings.filterwarnings("ignore", category=DeprecationWarning)

import pandas as pd

try:  # pragma: no cover - optional integration
    from core.interfaces.voice.core.sayit import (
        trace_tools,  # assuming trace_tools.py is importable
    )
except Exception:  # - fallback when integration not present

    class _TraceToolsFallback:
        """Minimal analytics fallback for environments without voice interfaces."""

        @staticmethod
        def get_summary_stats(frame: pd.DataFrame) -> dict[str, Any]:
            return {
                "row_count": len(frame.index),
                "columns": list(frame.columns),
                "ΛTAG": "ΛTRACE_FALLBACK",
            }

    trace_tools = _TraceToolsFallback()

logger = logging.getLogger(__name__)

try:  # pragma: no cover - exercised in environments with streamlit available
    import streamlit as st  # type: ignore

    STREAMLIT_AVAILABLE = True
except Exception:  # - optional dependency fallback
    STREAMLIT_AVAILABLE = False

    class _StreamlitFallback:
        """Deterministic fallback that records dashboard intent via logging."""

        def __init__(self) -> None:
            self._state: dict[str, Any] = {}

        def set_page_config(self, **kwargs: Any) -> None:
            self._state["page_config"] = kwargs
            logger.info("Streamlit fallback set_page_config", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "config": kwargs})

        def title(self, text: str) -> None:
            logger.info("Streamlit fallback title", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "title": text})

        def warning(self, text: str) -> None:
            logger.warning("Streamlit fallback warning", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "warning": text})

        def markdown(self, text: str) -> None:
            logger.info("Streamlit fallback markdown", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "markdown": text})

        def code(self, code_text: str, language: str = "") -> None:
            logger.info(
                "Streamlit fallback code",
                extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "code": code_text, "language": language},
            )

        def caption(self, text: str) -> None:
            logger.info("Streamlit fallback caption", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "caption": text})

        def multiselect(self, label: str, options: Sequence[str], default: Iterable[str] | None = None) -> list[str]:
            selected = list(default if default is not None else options)
            logger.info(
                "Streamlit fallback multiselect",
                extra={
                    "ΛTAG": "ΛSTREAMLIT_FALLBACK",
                    "label": label,
                    "options": list(options),
                    "selected": selected,
                },
            )
            return selected

        def dataframe(self, data: Any) -> None:
            logger.info(
                "Streamlit fallback dataframe",
                extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "rows": getattr(data, "shape", None)},
            )

        def json(self, value: Any) -> None:
            logger.info(
                "Streamlit fallback json",
                extra={
                    "ΛTAG": "ΛSTREAMLIT_FALLBACK",
                    "json_keys": list(value.keys()) if isinstance(value, dict) else None,
                },
            )

        def button(self, label: str) -> bool:
            logger.info("Streamlit fallback button", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "label": label})
            return False

        def error(self, text: str) -> None:
            logger.error("Streamlit fallback error", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "error": text})

        def info(self, text: str) -> None:
            logger.info("Streamlit fallback info", extra={"ΛTAG": "ΛSTREAMLIT_FALLBACK", "info": text})

    st = _StreamlitFallback()

LOG_PATH = "logs/emergency_log.jsonl"

st.set_page_config(page_title="LUKHAS Institutional Compliance Viewer")
st.title("🛡️ LUKHAS AGI - Compliance Audit Dashboard")

if not os.path.exists(LOG_PATH):
    st.warning("No emergency logs found.")
else:
    st.markdown("## 📜 Emergency Override Incidents")
    with open(LOG_PATH) as f:
        logs = [json.loads(line) for line in f if line.strip()]

    for entry in reversed(logs[-25:]):
        st.markdown("---")
        st.markdown(f"**⏱️ Timestamp:** {entry.get('timestamp')}")
        st.markdown(f"**🔍 Reason:** {entry.get('reason')}")
        st.markdown(f"**🧑‍💼 User:** {entry.get('user')} (Tier {entry.get('tier')})")
        st.markdown("**🧩 Actions Taken:**")
        st.code(", ".join(entry.get("actions_taken", [])), language="bash")

        st.markdown("**📋 Compliance Tags:**")
        for tag, value in entry.get("institutional_compliance", {}).items():
            st.markdown(f"- `{tag}`: {'✅' if value else '❌'}")

st.caption("🔒 All emergency actions are traceable, tiered, and GDPR-aligned.")

# ────────────────────────────────────────────────────────────────────────────────
# Symbolic Trace Dashboard Viewer (Enhanced via trace_tools)
# ────────────────────────────────────────────────────────────────────────────────


trace_path = Path("logs/symbolic_trace_dashboard.csv")
if trace_path.exists():
    st.markdown("## 🧠 Symbolic Trace Overview")

    try:
        df = pd.read_csv(trace_path)
        filter_cols = st.multiselect("Filter Columns", df.columns.tolist(), default=df.columns.tolist())
        st.dataframe(df[filter_cols] if filter_cols else df)

        # Optional Summary Tools
        st.markdown("## 📊 Symbolic Summary")
        summary = trace_tools.get_summary_stats(df)
        st.json(summary)

        if st.button("🧹 Filter by status = 'FAIL' or confidence < 0.6"):
            filtered = df[(df["status"] == "FAIL") | (df["confidence"] < 0.6)]
            st.dataframe(filtered)

    except Exception as e:
        st.error(f"Failed to load or process symbolic trace dashboard: {e}")
else:
    st.info("No symbolic trace data found.")
