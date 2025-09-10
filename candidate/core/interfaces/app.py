
"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: app.py
Advanced: app.py
Integration Date: 2025-05-31T07:55:27.733339
"""

#
# ╔═══════════════════════════════════════════════════════════════════╗
# ║ 📦 MODULE: app.py                                                 ║
# ║ 🧾 DESCRIPTION: Main Streamlit dashboard for LUKHAS Team           ║
# ║ 🎮 TYPE: Assistant Layer / UI Logic                               ║
# ║ 🛠️ AUTHOR: LUCΛS SYSTEMS                                          ║
# ║ 🗓️ CREATED: 2025-04-22                                            ║
# ║ 🔄 UPDATED: 2025-04-22                                            ║
# ╚═══════════════════════════════════════════════════════════════════╝

import re
import subprocess

try:
    import streamlit as st
except ImportError:
    # Fallback for when streamlit is not available
    class MockStreamlit:
        def __init__(self):
            self.session_state = {}

        def set_page_config(self, **kwargs): pass
        def error(self, msg): print(f"ERROR: {msg}")
        def stop(self): return
        def title(self, msg): print(f"TITLE: {msg}")
        def sidebar(self): return self
        def tabs(self, tabs): return [MockTab() for _ in tabs]
        def header(self, msg): print(f"HEADER: {msg}")
        def write(self, content): print(f"WRITE: {content}")
        def markdown(self, content, **kwargs): print(f"MARKDOWN: {content[:50]}...")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def button(self, label, **kwargs): return False
        def columns(self, specs): return [MockColumn() for _ in specs]
        def text_area(self, label, value="", **kwargs): return value
        def selectbox(self, label, options, **kwargs): return options[0] if options else None

    class MockTab:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class MockColumn:
        def button(self, label, **kwargs): return False
        def markdown(self, content, **kwargs): print(f"COL MARKDOWN: {content[:50]}...")

    st = MockStreamlit()
from pathlib import Path

st.set_page_config(page_title="LUKHAS TEAM  Dashboard", layout="wide")

# ─── Lukhas_ID Login Check ──────────────────────────────────────────────
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("🔒 This dashboard is restricted. Please authenticate via Lukhas_ID.")
    st.stop()

# ─── Title and Sidebar ────────────────────────────────────────────────
st.title("🧠 LUKHAS TEAM  Command Center")
st.sidebar.title("Settings")

# Optional: Light/Dark mode (assume already handled elsewhere)

# ─── Tabs Layout ──────────────────────────────────────────────────────
tab_docs, tab_tests, tab_compliance = st.tabs(["Documentation 📚", "Testing 🧪", "Compliance 🛡️"])

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
        module_blocks = re.findall(r"(### 📦 (.*?))(.*?)(?=### 📦|$)", content, re.DOTALL)
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
            header_info_match = re.search(r"(## 📘 Header Info\s*\n```text\n.*?\n```)", body, re.DOTALL)
            usage_guide_match = re.search(r"(## 📄 Usage Guide\s*\n```text\n.*?\n```)", body, re.DOTALL)
            st.markdown("#")
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

                    output = pypandoc.convert_file("manual.md", "pdf", outputfile="Document_Manual.pdf")
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
                    test_output_placeholder.success("✅ All tests passed!\n\n" + result.stdout)
                else:
                    test_output_placeholder.error("❌ Test failures:\n\n" + result.stdout + "\n" + result.stderr)
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
        table_match = re.search(r"(\|.+\|\n(\|[-:]+\|)+\n([\s\S]+?))(\n\n|$)", compliance_md)
        if table_match:
            table_md = table_match.group(1)
            st.markdown(table_md)
        else:
            st.markdown(compliance_md)

# ─────────────────────────────────────────────────────────────────────
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