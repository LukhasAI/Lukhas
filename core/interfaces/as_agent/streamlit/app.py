"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: app.py
Advanced: app.py
Integration Date: 2025-05-31T07:55:30.384694
"""

#
# ╔═══════════════════════════════════════════════════════════════════╗
# ║ 📦 MODULE: app.py                                                 ║
# ║ 🧾 DESCRIPTION: Main Streamlit dashboard for LUKHAS Agent          ║
# ║ 🎮 TYPE: Assistant Layer / UI Logic                               ║
# ║ 🛠️ AUTHOR: LUCΛS SYSTEMS                                          ║
# ║ 🗓️ CREATED: 2025-04-22                                            ║
# ║ 🔄 UPDATED: 2025-04-22                                            ║
# ╚═══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import streamlit as st

from core.dashboard_settings import get_paired_apps

logger = logging.getLogger(__name__)

st.set_page_config(page_title="LUKHAS Agent Dashboard", layout="wide")
st.title("🧠 LUKHAS - AGENT")


@dataclass
class ModuleDiscoveryResult:
    """Structured representation of module metadata for the dashboard."""

    lane: str
    name: str
    description: str
    module_type: str
    version: str
    source_path: Path

    # ΛTAG: module_blocks_format
    def as_block(self) -> tuple[str, str, str]:
        """Convert the discovery result into a tuple consumed by the UI."""

        display_name = f"{self.name} · {self.lane}".strip()
        version_label = f"{self.version}" if self.version else "unspecified"
        header = f"### 📦 {display_name}"
        header_info = (
            "## 📘 Header Info\n"
            "```text\n"
            f"Name: {self.name}\n"
            f"Lane: {self.lane}\n"
            f"Type: {self.module_type or 'unknown'}\n"
            f"Version: {version_label}\n"
            f"Source: {self.source_path.as_posix()}\n"
            f"Description: {self.description or 'Not documented.'}\n"
            "```\n"
        )
        usage_guide = (
            "## 📄 Usage Guide\n"
            "```text\n"
            "- Review the module docstring for integration specifics.\n"
            "- Confirm lane permissions before invoking symbolic actions.\n"
            "- Use ModuleRegistry for tier-aware access when applicable.\n"
            "```\n"
        )
        return header, display_name, header_info + usage_guide


# ΛTAG: repo_root_lookup

def _find_repo_root(start: Path) -> Path:
    """Locate the repository root by searching for a .git directory."""

    for candidate in (start, *tuple(start.parents)):
        if (candidate / ".git").exists():
            return candidate
    return start


def _clean_metadata_value(raw_value: str) -> str:
    """Normalize metadata text by removing framing characters."""

    cleaned = re.sub(r"[│║┤┐┘╚╔╠╣╦╩═]", "", raw_value)
    cleaned = cleaned.replace("🔧", "").replace("📦", "")
    return cleaned.strip(" :|-•\t\n\r")


def _extract_module_metadata(text: str, source_path: Path) -> Optional[ModuleDiscoveryResult]:
    """Extract module metadata from the leading portion of a source file."""

    snippet = text[:4000]
    if "MODULE" not in snippet.upper():
        return None

    module_match = re.search(r"MODULE[^:]*:\s*(?P<value>[^\n]+)", snippet, re.IGNORECASE)
    description_match = re.search(r"DESCRIPTION[^:]*:\s*(?P<value>[^\n]+)", snippet, re.IGNORECASE)
    type_match = re.search(r"TYPE[^:]*:\s*(?P<value>[^\n]+)", snippet, re.IGNORECASE)
    version_match = re.search(r"VERSION[^:]*:\s*(?P<value>[\w\.\-]+)", snippet, re.IGNORECASE)

    name = _clean_metadata_value(module_match.group("value")) if module_match else source_path.stem
    description = _clean_metadata_value(description_match.group("value")) if description_match else ""
    raw_type = _clean_metadata_value(type_match.group("value")) if type_match else ""
    module_type = re.split(r"(?:VERSION|UPDATED)", raw_type, maxsplit=1)[0].strip()
    version = _clean_metadata_value(version_match.group("value")) if version_match else ""

    lane = source_path.parts[source_path.parts.index("core")] if "core" in source_path.parts else ""
    if "matriz" in source_path.parts:
        lane = "matriz"
    elif "lukhas" in source_path.parts:
        lane = "lukhas"

    if not lane:
        lane = source_path.parts[0]

    return ModuleDiscoveryResult(
        lane=lane,
        name=name,
        description=description,
        module_type=module_type,
        version=version,
        source_path=source_path.relative_to(_find_repo_root(source_path)),
    )


def _discover_python_modules(base_path: Path, lane: str, limit: int = 5) -> Iterable[ModuleDiscoveryResult]:
    """Discover modules within a directory by parsing module metadata."""

    if not base_path.exists():
        return []

    discovered: list[ModuleDiscoveryResult] = []
    for file_path in sorted(base_path.rglob("*.py")):
        if file_path.name.startswith("_"):
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        metadata = _extract_module_metadata(text, file_path)
        if metadata and metadata.lane == lane:
            discovered.append(metadata)
        if len(discovered) >= limit:
            break
    return discovered


# ΛTAG: module_discovery
@st.cache_data(show_spinner=False)
def build_module_blocks() -> list[tuple[str, str, str]]:
    """Build the cached list of module blocks for the Streamlit dashboard."""

    repo_root = _find_repo_root(Path(__file__).resolve())
    discovery_plan = [
        (repo_root / "core", "core"),
        (repo_root / "matriz", "matriz"),
        (repo_root / "lukhas_website" / "lukhas", "lukhas"),
    ]

    module_results: list[ModuleDiscoveryResult] = []
    for path, lane in discovery_plan:
        module_results.extend(_discover_python_modules(path, lane))

    if not module_results:
        logger.info("No module metadata discovered for Streamlit dashboard display.")
        return []

    module_results.sort(key=lambda item: (item.lane, item.name))
    return [result.as_block() for result in module_results]


st.sidebar.title("Settings")
lukhas_plugin_enabled = st.sidebar.checkbox("🧠 Enable LUKHAS Brain Add-on", value=False)

paired_apps = get_paired_apps("user_123")
if paired_apps:
    st.sidebar.markdown("🧩 **Paired Apps:**")
    for app in paired_apps:
        st.sidebar.write(f"• {app}")

module_blocks = build_module_blocks()
if module_blocks:
    module_options = [mod_name for _, mod_name, _ in module_blocks]
    selected_module = st.sidebar.selectbox("📦 Select Module", module_options)
else:
    selected_module = None
    st.sidebar.info("No module metadata discovered yet.")

if lukhas_plugin_enabled:
    try:
        from core.lukhas_overview_log import log_event

        st.sidebar.success("🧠 LUKHAS symbolic brain is active.")
        log_event(
            "agent",
            "LUKHAS symbolic agent activated via dashboard.",
            tier=0,
            source="app.py",
        )
    except ImportError:
        st.sidebar.error("⚠️ Could not load LUKHAS_AGENT_PLUGIN. Check folder structure.")


st.markdown("##  🧱 Symbolic Widget Preview")
try:
    from core.lukhas_widget_engine import create_symbolic_widget
except ImportError:
    st.warning("⚠️ lukhas_widget_engine not found.")
else:
    widget_types = [
        "travel",
        "dining",
        "dream",
        "checkout",
        "reminder",
        "event_ticket",
        "deliveroo",
        "glovo",
        "grubhub",
        "uber_eats",
        "cinema",
        "ticketmaster",
        "royal_mail",
        "correos",
        "laposte",
        "usps",
        "fedex",
    ]
    selected_widget = st.selectbox("🔧 Choose widget type", widget_types)
    user_tier = st.slider("⭐️ Simulated Tier", 0, 5, 3)
    if st.button("🎛️ Generate Widget"):
        widget = create_symbolic_widget(selected_widget, user_tier)
        if widget and "visual_style" in widget:
            visual = widget["visual_style"]
            st.markdown(
                f"""
                <div style='background-color:{visual["background_color"]};
                            padding:16px; border-radius:12px; color:white;
                            font-family:Inter,sans-serif; margin-bottom:16px;'>
                    <h3 style='margin:0;'>{visual["emoji_header"]}</h3>
                    <p><b>Vendor:</b> {widget.get("vendor", "N/A")}</p>
                    <p><b>Type:</b> {widget.get("type", "N/A")}</p>
                    <p><b>Status:</b> {widget.get("status", "N/A")}</p>
                    <button style='padding:8px 16px; background-color:white; color:black; border:none;
                                    border-radius:8px; cursor:pointer;'>Book Now</button>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("⚠️ No visual style found in widget.")

        try:
            from core.lukhas_agent_handoff import agent_handoff

            handoff = agent_handoff(widget.get("vendor", ""))
            if handoff["status"] == "ready":
                st.markdown("###  🤝 Vendor Agent Preview")
                st.markdown(
                    f"""
                    <div style='background-color:{handoff["theme_color"]}; padding:16px; border-radius:12px; color:white; font-family:Inter, sans-serif;'>
                        <b>{handoff["agent_name"]}</b> from <i>{widget["vendor"]}</i><br>
                        {handoff["greeting"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except BaseException:
            pass


selected_block = None
if module_blocks and selected_module:
    for full_header, mod_name, body in module_blocks:
        if mod_name == selected_module:
            selected_block = (full_header, body)
            break

if selected_block:
    full_header, body = selected_block
    st.markdown(full_header)
    header_info_match = re.search(
        r"(## 📘 Header Info\s*\n```text\n.*?\n```)", body, re.DOTALL
    )
    usage_guide_match = re.search(
        r"(## 📄 Usage Guide\s*\n```text\n.*?\n```)", body, re.DOTALL
    )

    st.markdown("#")
    if header_info_match:
        st.markdown(header_info_match.group(1))
    else:
        st.markdown("```text\n" + body.strip() + "\n```")
    if usage_guide_match:
        st.markdown(usage_guide_match.group(1))
    else:
        st.warning("Could not extract content for this module.")

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
#   - Sidebar toggle for Agent core (LUKHAS symbolic modules)
#   - Symbolic widget preview with DST and vendor handoff
#   - Multi-tier access simulation (Tier 0–5)
#   - Emotional state-aware scheduler (backend logic)
#
# 📡 PAIRED APPS OVERVIEW:
#   - Visible in sidebar (linked from dashboard_settings)
#   - Useful for showing what services/devices user has authorized
#
# 🔍 TROUBLESHOOTING:
#   - If Streamlit fails to launch, ensure:
#       • Virtual environment is active
#       • Dependencies are installed (streamlit, etc.)
#
# END OF FILE
# ─────────────────────────────────────────────────────────────────────
