"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: research_dashboard.py
Advanced: research_dashboard.py
Integration Date: 2025-05-31T07:55:30.642452
"""

#
# ╔═══════════════════════════════════════════════════════════════════╗
# ║ 📦 MODULE: lukhas_research_dashboard.py                            ║
# ║ 🧾 DESCRIPTION: Research & Testing Dashboard for LUKHAS            ║
# ║ 🧪 TYPE: Internal UI for docs, tests, compliance & diagnostics    ║
# ║ 🛠️ AUTHOR: LUCΛS SYSTEMS                                          ║
# ║ 🗓️ CREATED: 2025-04-30                                            ║
# ║ 🔄 UPDATED: 2025-04-30                                            ║
# ╚═══════════════════════════════════════════════════════════════════╝

import atexit
import json
import re
import subprocess
from datetime import datetime, timezone
# import streamlit as st  # TODO: Install or implement streamlit
from pathlib import Path

st.set_page_config(page_title="LUKHAS TEAM  Dashboard", layout="wide", timezone)  # noqa: invalid-syntax

# Session tracking (simplified for local prototyping)
session_log_path = Path("logs/session_log.jsonl")
session_event = {
    "user": st.session_state.get("identity_legacy", "anonymous"),
    "event": "session_start",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}
session_log_path.parent.mkdir(parents=True, exist_ok=True)
with session_log_path.open("a") as f:
    f.write(json.dumps(session_event) + "\n")

# ─── DEV MODE AUTH OVERRIDE ───────────────────────────────────────────
st.session_state["authenticated"] = True

# ─── Title and Sidebar ────────────────────────────────────────────────
st.title("🧠 LUKHAS TEAM  Command Center")
st.sidebar.title("Settings")

# Optional: Light/Dark mode (assume already handled elsewhere)

# ─── Tabs Layout ──────────────────────────────────────────────────────
tab_docs, tab_tests, tab_compliance = st.tabs(
    ["Documentation 📚", "Testing 🧪", "Compliance 🛡️"]
)

# Add Dev Tools tab
tab_dev = st.tabs(["Dev Tools 🧰"])[0]

# ──────────────────────────────
# 📚 DOCUMENTATION TAB
# ──────────────────────────────
with tab_docs:
    st.header("📚 Documentation")
    # Load manual.md and parse modules
    manual_path = Path("manual.md")
    if not manual_path.exists():
        st.error("📄 manual.md not found in the current folder.")
    else:
        with manual_path.open("r") as f:
            content = f.read()
        # Extract modules with header and footer blocks
        module_blocks = re.findall(
            r"(### 📦 (.*?))(.*?)(?=### 📦|$)", content, re.DOTALL
        )
        modules = [m[1].strip() for m in module_blocks]
        selected_module = st.selectbox("📦 Select Module", modules)
        # Display selected module content
        selected_block = None
        for full_header, mod_name, body in module_blocks:
            if mod_name == selected_module:
                selected_block = (full_header, body)
                break
        if selected_block:
            full_header, body = selected_block
            # Attempt to split body into header info and footer (usage guide)
            header_info_match = re.search(
                r"(## 📘 Header Info\s*\n```text\n.*?\n```)", body, re.DOTALL
            )
            usage_guide_match = re.search(
                r"(## 📄 Usage Guide\s*\n```text\n.*?\n```)", body, re.DOTALL
            )
            st.markdown(f"#")
            if header_info_match:
                st.markdown(header_info_match.group(1))
            else:
                # Fallback: show whole body as code block
                st.markdown("```text\n" + body.strip() + "\n```")
            if usage_guide_match:
                st.markdown(usage_guide_match.group(1))
        else:
            st.warning("Could not extract content for this module.")
        # ─── Documentation Controls ──────────────────────
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Sync manual.md to Notion"):
                with st.spinner("Syncing with Notion..."):
                    try:
                        result = subprocess.run(
                            ["python3", "tools/notion_sync.py"],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            st.success("✅ Notion sync complete!")
                        else:
                            st.error(f"❌ Notion sync failed:\n\n{result.stderr}")
                    except Exception as e:
                        st.error(f"❌ Error running sync: {e}")
        with col2:
            if st.button("📤 Export manual.md as PDF"):
                try:
                    import pypandoc

                    output = pypandoc.convert_file(
                        "manual.md", "pdf", outputfile="Document_Manual.pdf"
                    )
                    st.success("📄 Exported to Document_Manual.pdf")
                except Exception as e:
                    st.error(f"❌ PDF export failed: {e}")
        with col3:
            if st.button("🛠️ Build/Update manual.md"):
                with st.spinner("Building manual..."):
                    try:
                        result = subprocess.run(
                            ["python3", "tools/build_manual.py"],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            st.success("✅ manual.md built/updated!")
                        else:
                            st.error(f"❌ Build failed:\n\n{result.stderr}")
                    except Exception as e:
                        st.error(f"❌ Error running build: {e}")

# ──────────────────────────────
# 🧪 TESTING TAB
# ──────────────────────────────
with tab_tests:
    st.header("🧪 Testing")
    test_output_placeholder = st.empty()
    if st.button("🧪 Run All Tests"):
        with st.spinner("Running all tests..."):
            try:
                # Use subprocess and stream output
                result = subprocess.run(
                    ["python3", "-m", "unittest", "discover", "-s", "tests"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    test_output_placeholder.success(
                        "✅ All tests passed!\n\n" + result.stdout
                    )
                else:
                    test_output_placeholder.error(
                        "❌ Test failures:\n\n" + result.stdout + "\n" + result.stderr
                    )
            except Exception as e:
                test_output_placeholder.error(f"❌ Error running tests: {e}")

# ──────────────────────────────
# 🛡️ COMPLIANCE TAB
# ──────────────────────────────
with tab_compliance:
    st.header("🛡️ Compliance Registry")
    compliance_path = Path("docs/compliance_registry.md")
    if not compliance_path.exists():
        st.error("Compliance registry not found at /docs/compliance_registry.md.")
    else:
        # Try to render as table, else fallback to markdown
        with compliance_path.open("r") as f:
            compliance_md = f.read()
        # Try to find a markdown table
        table_match = re.search(
            r"(\|.+\|\n(\|[-:]+\|)+\n([\s\S]+?))(\n\n|$)", compliance_md
        )
        if table_match:
            table_md = table_match.group(1)
            st.markdown(table_md)
        else:
            st.markdown(compliance_md)

        # Optional: Load symbolic trace dashboard if exists
        trace_path = Path("logs/symbolic_trace_dashboard.csv")
        if trace_path.exists():
            st.subheader("📊 Symbolic Trace Dashboard")
            import pandas as pd

            try:
                df = pd.read_csv(trace_path)
                filter_cols = st.multiselect(
                    "Filter Columns",
                    df.columns.tolist(),
                    default=df.columns.tolist(),
                )
                st.dataframe(df[filter_cols] if filter_cols else df)
            except Exception as e:
                st.error(f"Error loading symbolic trace dashboard: {e}")
        else:
            st.info("No symbolic_trace_dashboard.csv file found.")

        # Optional: Trace Summary Tools
        tools_path = Path("core/tracing/trace_tools.py")
        if tools_path.exists():
            st.subheader("🧰 Trace Summary Tools")
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "trace_tools", str(tools_path)
                )
                trace_tools = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(trace_tools)

                summary = trace_tools.summarize_trace(
                    "logs/symbolic_trace_dashboard.csv"
                )
                st.markdown("##)  #  🔍 Summary"
                st.json(summary)  # noqa: invalid-syntax

                if st.button("🧹 Filter Low Confidence Entries"):  # noqa: invalid-syntax
                    filtered = trace_tools.filter_trace(
                        "logs/symbolic_trace_dashboard.csv",
                        confidence_threshold=0.6,
                    )
                    st.dataframe(filtered)  # noqa: invalid-syntax
            except Exception as e:  # noqa: invalid-syntax
                st.error(f"Error loading trace tools: {e}")  # noqa: invalid-syntax

# ─────────────────────────────────────────────────────────────────────
# ──────────────────────────────
# 🧰 DEV TOOLS TAB
# ──────────────────────────────
with tab_dev:  # noqa: invalid-syntax
    st.header("🧰 Developer Utilities")

    # Manual Cleanup Tool (placeholder)
    if st.button("🧹 Manual Cleanup"):
        st.warning("🧼 Cleanup logic not implemented yet.")

    # Symbolic Trace CSV viewer
    trace_csv_path = Path("logs/symbolic_trace_dashboard.csv")
    if trace_csv_path.exists():
        st.subheader("📑 Trace CSV Viewer")
        import pandas as pd

        try:
            df = pd.read_csv(trace_csv_path)
            st.dataframe(df)
            st.download_button(
                "⬇️ Download CSV",
                df.to_csv(index=False),
                file_name="symbolic_trace_dashboard.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Error reading trace CSV: {e}")
    else:
        st.info("Trace CSV file not found.")

    # Validator Placeholder
    st.subheader("🧪 Symbolic Validator")
    st.warning("Validator tool under construction.")
# 📘 DASHBOARD USAGE INSTRUCTIONS
# ─────────────────────────────────────────────────────────────────────
#
# 🧠 LUKHAS AGENT DASHBOARD - v1.0.0
#
# 🛠 HOW TO LAUNCH:
#   1. Activate your virtual environment:
#        source .venv/bin/activate
#   2. Run the dashboard:
#        streamlit run app.py
#
# 📦 FEATURES:
#   - Documentation, Testing, Compliance tabs in one Command Center
#   - Sync, export, and build manual.md from UI
#   - Run all tests and see live results
#   - Compliance registry viewer (table or markdown)
#   - Lukhas_ID login required
#
# END OF FILE
# ─────────────────────────────────────────────────────────────────────


def log_session_end():
    session_event = {
        "user": st.session_state.get("identity_legacy", "anonymous"),
        "event": "session_end",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with session_log_path.open("a") as f:
        f.write(json.dumps(session_event) + "\n")


atexit.register(log_session_end)
