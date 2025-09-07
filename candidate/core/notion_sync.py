import logging
import time
logger = logging.getLogger(__name__)
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ CONSOLIDATED NOTION SYNC SYSTEM - MASTER FILE                       ║
║ DESCRIPTION: Complete LUKHAS Notion synchronization system          ║
║                                                                         ║
║ FUNCTIONALITY: Modular AI-powered sync • Multi-format support      ║
║ IMPLEMENTATION: Streamlit UI • CLI • Background scheduler           ║
║ INTEGRATION: Multi-Platform AI Architecture • Legacy Support       ║
║ CONSOLIDATION: All notion_sync logic from workspace unified         ║
╚═══════════════════════════════════════════════════════════════════════════╝

"Enhancing beauty while adding sophistication" - LUKHAS Systems 2025
"Enhancing beauty while adding sophistication" - lukhas Systems 2025

OFFICIAL RESOURCES:
• www.lukhas.ai - Advanced AI Solutions
• www.lukhas.dev - Algorithm Development Hub
• www.lukhas.id - Digital Identity Platform

INTEGRATION POINTS: Notion • WebManager • Documentation Tools • ISO Standards
EXPORT FORMATS: Markdown • LaTeX • HTML • PDF • JSON • XML
METADATA TAGS: #LuKhas #AI #Professional #Deployment #AI Professional System

CONSOLIDATED FEATURES:
- ✅ Modular architecture with separate components
- ✅ Legacy Streamlit UI support with dark mode
- ✅ GPT-4 integration for content analysis and summaries
- ✅ Multi-layout support (toggle, flat, minimal)
- ✅ Automated scheduling and background sync
- ✅ ΛDoc adapter integration for symbolic documentation
- ✅ LukhasDoc adapter integration for symbolic documentation
- ✅ Comprehensive audit logging and analytics
- ✅ CLI interface with full argument support
- ✅ Configuration management with persistent settings

This is the MASTER consolidated file containing all notion_sync functionality
from across the entire workspace. All other notion_sync files should be removed
after this consolidation is complete.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

# Core Notion and AI imports
# Specific Notion client imports for security
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError, RequestTimeoutError
except ImportError:
    # Fallback if notion_client is not installed
    print("⚠️ notion_client not installed. Some features will be limited.")
    Client = None
    APIResponseError = Exception
    RequestTimeoutError = Exception

# Security and reflection imports

# import streamlit as st  # TODO: Install or implement streamlit

# Add the current directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import modular components
try:
    from constants import LAMBDA_ID, SYSTEM_NAME, VERSION
    from sync_engine import SyncEngine
except ImportError as e:
    print(f"⚠️ Warning: Some modular components not available: {e}")
    # Fallback constants
    LAMBDA_ID = "Λ_NOTION_SYNC"
    VERSION = "2.0.0"
    SYSTEM_NAME = "LUKHAS Notion Sync"
    LAMBDA_ID = "lukhas_NOTION_SYNC"
    VERSION = "2.0.0"
    SYSTEM_NAME = "LUKHAS Notion Sync"

# Legacy support for OpenAI integration
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available for GPT features")

# Streamlit support (optional)
try:
    import streamlit as st

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("⚠️ Streamlit not available for UI features")


# Logger setup
class LambdaLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{LAMBDA_ID}] {msg}", kwargs


logger = LambdaLoggerAdapter(logging.getLogger(__name__), {"lambda_id": LAMBDA_ID})

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY STREAMLIT FUNCTIONS - CONSOLIDATED FROM ORIGINAL NOTION_SYNC FILES
# ═══════════════════════════════════════════════════════════════════════════════


def make_code_block(content, lang="text"):
    """Create a Notion code block from content."""
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": lang,
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": content.strip()[:2000]},  # max block length
                }
            ],
        },
    }


def make_toggle_block(module_name, header_text, usage_text):
    """Create a Notion toggle block for module documentation."""
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": f"📦 {module_name}.py"}],
            "children": [
                make_code_block(header_text, lang="text"),
                make_code_block(usage_text, lang="python"),
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"🕒 Synced on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'}"
                                },
                            }
                        ]
                    },
                },
            ],
        },
    }


def make_flat_block(module_name, header_text, usage_text):
    """Create flat layout blocks for module documentation."""
    return [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"📦 {module_name}.py"},
                    }
                ]
            },
        },
        make_code_block(header_text, lang="text"),
        make_code_block(usage_text, lang="python"),
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"🕒 Synced on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'}"},
                    }
                ]
            },
        },
    ]


def make_minimal_block(module_name, usage_text):
    """Create minimal layout blocks for module documentation."""
    return [
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": f"{module_name}.py"}]},
        },
        make_code_block(usage_text, lang="python"),
    ]


def generate_summary(text):
    """Generate GPT-4 summary of documentation content."""
    if not OPENAI_AVAILABLE:
        return "GPT summary not available - OpenAI not installed"

    try:
        summary_prompt = f"Summarize this documentation for internal AI team awareness:\n\n{text[:4000]}"

        # Try new OpenAI API format first, fall back to legacy
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}],
            )
            return response.choices[0].message.content
        except AttributeError:
            # Fallback to legacy API
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}],
            )
            return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Summary generation failed: {e}"


def sync_to_notion_legacy(doc_path: str, notion_page_id: str = "symbolic-notion-demo"):
    """
    Legacy ΛDoc → Notion Sync Adapter function.
    Mock sync function that reads symbolic docs and simulates pushing them to Notion.
    In production, this connects to Notion API with secure OAuth tokens and blocks API.
    """
    logger.info("🔗 Syncing LukhasDoc output to Notion (legacy adapter)...")
    path = Path(doc_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {doc_path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Simulate push to Notion
    logger.info(f"📄 Document title: {data.get('overview', 'Untitled'}")
    logger.info(f"📌 Target Notion Page ID: {notion_page_id}")
    logger.info(f"🕓 Synced at: {datetime.date.today().isoformat(}")

    # Mocked success
    return {"status": "ok", "notion_page": notion_page_id}


# ΛiD audit logging integration


def log_audit_with_lid(action: str, metadata: Optional[dict[str, Any]] = None):
    """Log Notion sync or other actions using ΛiD signature."""


# Lukhas_ID audit logging integration


def log_audit_with_lid(action: str, metadata: Optional[dict[str, Any]] = None):
    """Log Notion sync or other actions using Lukhas_ID signature."""
    if metadata is None:
        metadata = {}

    audit_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "action": action,
        "lambda_id": LAMBDA_ID,
        "metadata": metadata,
    }
    audit_path = Path("reflection/audits")
    audit_path.mkdir(parents=True, exist_ok=True)
    log_file_path = audit_path / f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'}.json"
    with log_file_path.open("w") as f:
        json.dump(audit_entry, f, indent=2)

    logger.info(f"🔐 Audit log saved: {log_file_path}")


def run_legacy_streamlit_mode():
    """
    Run the legacy Streamlit interface with full functionality.
    This consolidates the original notion_sync.py Streamlit features.
    """
    try:
        #         import streamlit as st  # TODO: Install or implement streamlit

        # Load configuration
        config_path = Path("config.json")
        if config_path.exists():
            with config_path.open("r") as cfg:
                stored_config = json.load(cfg)
            default_dark = stored_config.get("dark_mode", False)
        else:
            stored_config = {}
            default_dark = False

        # Sidebar controls
        dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode", value=default_dark)
        auto_summary_enabled = st.sidebar.checkbox("🧠 Enable GPT Auto Summary", value=False)

        # Save settings
        stored_config["dark_mode"] = dark_mode
        with config_path.open("w") as cfg:
            json.dump(stored_config, cfg)

        # Apply dark mode styling
        if dark_mode:
            st.markdown(
                """
                <style>
                body {
                    background-color: #121212;
                    color: #e0e0e0;
                }
                </style>
            """,
                unsafe_allow_html=True,
            )

        # Load environment variables
        load_dotenv()
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

        if not NOTION_TOKEN or not NOTION_PAGE_ID:
            st.error("❌ Notion credentials not found in .env file")
            return

        notion = Client(auth=NOTION_TOKEN)

        # Read and parse manual.md if it exists
        manual_path = Path("manual.md")
        if manual_path.exists():
            with open(manual_path) as f:
                content = f.read()

            # Split modules from markdown
            modules = re.split(r"##)  #  📦 (.*?\n", content)[1:]
            modules = [(modules[i], modules[i + 1]) for i in range(0, len(modules), 2)]

            # Layout selection
            layout_template = st.sidebar.selectbox("📋 Layout Style", ["toggle", "flat", "minimal"], index=0)

            # Prepare blocks
            blocks = []
            for mod_name, mod_text in modules:
                header_match = re.search(r"#### Header Info\n```text\n(.*?)```", mod_text, re.DOTALL)
                usage_match = re.search(r"#### Usage Guide\n```text\n(.*?)```", mod_text, re.DOTALL)

                header = header_match.group(1) if header_match else "No header found"
                usage = usage_match.group(1) if usage_match else "No usage guide found"

                if layout_template == "toggle":
                    blocks.append(make_toggle_block(mod_name, header, usage))
                elif layout_template == "flat":
                    blocks.extend(make_flat_block(mod_name, header, usage))
                elif layout_template == "minimal":
                    blocks.extend(make_minimal_block(mod_name, usage))

            # Add summary if enabled
            if auto_summary_enabled and OPENAI_AVAILABLE:
                summary = generate_summary(content)
                if summary:
                    summary_block = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": f"🧠 GPT Summary: {summary}"},
                                }
                            ]
                        },
                    }
                    blocks.append(summary_block)

            # Add audit information
            lambda_id = os.getenv("LAMBDA_ID", "anonymous")
            audit_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"🔏 Synced by {lambda_id}"},
                        }
                    ]
                },
            }
            blocks.append(audit_block)

            # Sync to Notion
            if st.button("🔄 Sync to Notion"):
                try:
                    notion.blocks.children.append(NOTION_PAGE_ID, children=blocks)
                    st.success("✅ Notion sync complete!")

                    # ΛiD audit log
                    # Lukhas_ID audit log
                    log_audit_with_lid(
                        "notion_sync",
                        {
                            "modules_synced": [mod[0] for mod in modules],
                            "notion_page": NOTION_PAGE_ID,
                        },
                    )

                except Exception as e:
                    st.error(f"❌ Error syncing to Notion: {e}")

            # Display Notion link
            notion_link = f"https://www.notion.so/{NOTION_PAGE_ID.replace('-', ''}"
            if st.button("🔗 Copy Notion Page Link"):
                st.code(notion_link)

            # GPT Assistant
            if OPENAI_AVAILABLE:
                st.markdown("### 🤖 Ask ChatGPT about this module")
                user_question = st.text_input("💬 Enter your question about this module:", "")

                if user_question and modules:
                    try:
                        first_mod_name, first_mod_text = modules[0]
                        header_match = re.search(
                            r"#### Header Info\n```text\n(.*?)```",
                            first_mod_text,
                            re.DOTALL,
                        )
                        usage_match = re.search(
                            r"#### Usage Guide\n```text\n(.*?)```",
                            first_mod_text,
                            re.DOTALL,
                        )

                        header = header_match.group(1) if header_match else "No header found"
                        usage = usage_match.group(1) if usage_match else "No usage guide found"

                        module_text = f"MODULE: {first_mod_name}.py\n\nHeader Info:\n{header}\n\nUsage Guide:\n{usage}"

                        full_prompt = (
                            f"You are an assistant for the LUKHAS AI system. Answer the following question about this module:\n\n"
                            f"You are an assistant for the LUKHAS AI system. Answer the following question about this module:\n\n"
                            f"{module_text}\n\nQUESTION: {user_question}\n\nANSWER:"
                        )

                        # Try new OpenAI API format first, fall back to legacy
                        try:
                            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[{"role": "user", "content": full_prompt}],
                            )
                            answer = response.choices[0].message.content
                        except AttributeError:
                            # Fallback to legacy API
                            openai.api_key = os.getenv("OPENAI_API_KEY")
                            response = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[{"role": "user", "content": full_prompt}],
                            )
                            answer = response["choices"][0]["message"]["content"]

                        st.markdown("### 💡 GPT Response")
                        st.markdown(f"> {answer}")

                        # Extract concepts
                        try:
                            concept_prompt = (
                                f"From this module answer, extract 3 to 5 key technical or symbolic concepts "
                                f"the user might want to explore. Return them as a simple comma-separated list.\n\n{answer}"
                            )

                            # Try new OpenAI API format first, fall back to legacy
                            try:
                                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                                concept_response = client.chat.completions.create(
                                    model="gpt-4",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": concept_prompt,
                                        }
                                    ],
                                )
                                concept_text = concept_response.choices[0].message.content
                            except AttributeError:
                                # Fallback to legacy API
                                concept_response = openai.ChatCompletion.create(
                                    model="gpt-4",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": concept_prompt,
                                        }
                                    ],
                                )
                                concept_text = concept_response["choices"][0]["message"]["content"]

                            extracted_concepts = [c.strip() for c in concept_text.split(",") if len(c.strip()) > 2]

                            st.markdown("### 🔍 Explore GPT-Generated Concepts:")
                            for concept in extracted_concepts:
                                if st.button(f"🔹 {concept}"):
                                    st.info(f"🧠 GPT says: **{concept}** is worth exploring.")

                        except Exception:
                            st.warning("Could not generate concept list.")

                    except Exception as e:
                        st.error(f"GPT error: {e}")
            else:
                st.warning("OpenAI API key not found in .env file.")

        else:
            st.warning("manual.md not found - please create it with module documentation")

        # Background scheduler
        if st.sidebar.button("Enable Notion Watchdog"):

            def schedule_sync():
                logger.info("⏱️ Notion sync watchdog started.")
                try:
                    notion.blocks.children.append(NOTION_PAGE_ID, children=blocks)
                    logger.info("✅ Notion multi-module sync complete (scheduled)!")
                except Exception as e:
                    logger.error(f"❌ Error in scheduled sync: {e}")

            try:
                from apscheduler.schedulers.background import BackgroundScheduler

                scheduler = BackgroundScheduler()
                scheduler.add_job(schedule_sync, "interval", days=7)
                scheduler.start()
                st.success("🔁 Scheduled weekly Notion sync activated.")
            except ImportError:
                st.warning("Scheduler not available - apscheduler not installed")

    except ImportError:
        logger.error("Streamlit not available for legacy UI mode")
        return False
    except Exception as e:
        logger.error(f"Legacy Streamlit mode failed: {e}")
        return False

    return True


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [LUKHAS%(lambda_id)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Add lambda_id to all log records


class LambdaLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{LAMBDA_ID}] {msg}", kwargs


logger = LambdaLoggerAdapter(logging.getLogger(__name__), {"lambda_id": LAMBDA_ID})


def print_banner():
    """Print the system banner."""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          {SYSTEM_NAME} v{VERSION}                           ║
║                     Advanced AI-Powered Notion Synchronization                ║
║                                                                              ║
║  🔄 Intelligent markdown-to-Notion sync with GPT-4 analysis                 ║
║  🧠 AI-focused content understanding and categorization                     ║
║  ⚡ Real-time monitoring with Streamlit UI                                  ║
║  📊 Comprehensive audit logging and analytics                               ║
║  🎯 Lambda calculus-inspired modular architecture                           ║
║                                                                              ║
║  Lambda ID: {LAMBDA_ID}                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_sync_engine(args):
    """Run the sync engine in command-line mode."""
    logger.info("Starting sync engine in CLI mode")

    try:
        # Initialize sync engine
        engine = SyncEngine(args.config)
        await engine.start()

        if args.sync_type:
            # Run immediate sync
            logger.info(f"Running {args.sync_type} sync")
            result = await engine.run_sync(sync_type=args.sync_type, files=args.files, force=args.force)

            if result.get("success"):
                print("✅ Sync completed successfully!")
                if "summary" in result:
                    summary = result["summary"]
                    print(f"📊 Files processed: {summary['files_processed']}")
                    print(f"✅ Successful: {summary['successful_files']}")
                    print(f"❌ Failed: {summary['failed_files']}")
                    print(f"⏱️  Total time: {summary['total_time']:.2f}s")
            else:
                print(f"❌ Sync failed: {result.get('error', 'Unknown error'}")
                sys.exit(1)

        if args.daemon:
            # Run as daemon
            logger.info("Running in daemon mode - press Ctrl+C to stop")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")

        await engine.stop()

    except Exception as e:
        logger.error(f"Sync engine failed: {e}")
        sys.exit(1)


async def run_ui_mode():
    """Run the Streamlit UI."""
    logger.info("Starting Streamlit UI mode")

    try:
        import subprocess
        import sys

        # Run Streamlit
        streamlit_cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(Path(__file__).parent / "streamlit_ui.py"),
            "--server.port",
            "8501",
            "--server.address",
            "localhost",
            "--browser.gatherUsageStats",
            "false",
        ]

        logger.info("Launching Streamlit UI...")
        subprocess.run(streamlit_cmd)

    except Exception as e:
        logger.error(f"Failed to start UI: {e}")
        sys.exit(1)


def test_system():
    """Run system tests."""
    logger.info("Running system tests")

    try:
        # Test imports
        from audit_logger import AuditLogger
        from block_builder import BlockBuilder
        from markdown_parser import MarkdownParser

        from candidate.core.config_manager import ConfigManager

        print("✅ All imports successful")

        # Test configuration
        ConfigManager()
        print("✅ Configuration manager initialized")

        # Test components
        MarkdownParser()
        BlockBuilder()
        AuditLogger()

        print("✅ Core components initialized")

        # Test directory structure
        from constants import ensure_directories

        ensure_directories()
        print("✅ Directory structure validated")

        print("🎉 All system tests passed!")

    except Exception as e:
        print(f"❌ System test failed: {e}")
        sys.exit(1)


def main():
    """Main entry point with consolidated functionality."""
    parser = argparse.ArgumentParser(
        description=f"{SYSTEM_NAME} v{VERSION} - Advanced AI-Powered Notion Sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run modern Streamlit UI (modular)
  python notion_sync.py --ui

  # Run legacy Streamlit UI (original functionality)
  python notion_sync.py --legacy-ui

  # Run manual sync
  python notion_sync.py --sync manual

  # Run auto sync in daemon mode
  python notion_sync.py --sync auto --daemon

  # Test system
  python notion_sync.py --test

  # Sync specific files
  python notion_sync.py --sync manual --files file1.md file2.md

  # ΛDoc sync adapter
  python notion_sync.py --ΛDoc-sync /path/to/doc.json --notion-page-id your-page-id
  # LukhasDoc sync adapter
  python notion_sync.py --LukhasDoc-sync /path/to/doc.json --notion-page-id your-page-id
        """,
    )

    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch modern Streamlit UI (modular)",
    )
    parser.add_argument(
        "--legacy-ui",
        action="store_true",
        help="Launch legacy Streamlit UI (original functionality)",
    )
    parser.add_argument(
        "--sync",
        choices=["manual", "auto", "daily"],
        help="Run sync operation",
    )
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--files", nargs="+", help="Specific files to sync")
    parser.add_argument("--force", action="store_true", help="Force sync (ignore cache)")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--quiet", action="store_true", help="Suppress banner output")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--ΛDoc-sync", type=str, help="Sync ΛDoc output file to Notion")
    parser.add_argument(
        "--notion-page-id",
        type=str,
        help="Target Notion page ID for ΛDoc sync",
    )
    parser.add_argument(
        "--LukhasDoc-sync",
        type=str,
        help="Sync LukhasDoc output file to Notion",
    )
    parser.add_argument(
        "--notion-page-id",
        type=str,
        help="Target Notion page ID for LukhasDoc sync",
    )

    args = parser.parse_args()

    # Configure debug logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print banner unless quiet mode
    if not args.quiet:
        print_banner()

    # Handle different modes
    if args.test:
        test_system()
    elif args.legacy_ui:
        # Run legacy Streamlit UI with all original functionality
        logger.info("Starting legacy Streamlit UI mode")
        if not run_legacy_streamlit_mode():
            # Fallback to launching external Streamlit process
            try:
                import subprocess
                import sys

                streamlit_cmd = [
                    sys.executable,
                    "-c",
                    f"import sys; sys.path.insert(0, '{Path(__file__}.parent}'); "
                    "from notion_sync import run_legacy_streamlit_mode; "
                    "import streamlit as st; run_legacy_streamlit_mode()",
                ]
                logger.info("Launching legacy Streamlit UI as external process...")
                subprocess.run(streamlit_cmd)
            except Exception as e:
                logger.error(f"Failed to start legacy UI: {e}")
                sys.exit(1)
    elif args.ui:
        asyncio.run(run_ui_mode())
    elif args.ladoc_sync:
        # Run ΛDoc sync adapter
        notion_page_id = args.notion_page_id or "symbolic-notion-demo"
        try:
            result = sync_to_notion_legacy(args.ladoc_sync, notion_page_id)
            print(f"✅ ΛDoc sync completed: {result}")
        except Exception as e:
            logger.error(f"ΛDoc sync failed: {e}")
        # Run LukhasDoc sync adapter
        notion_page_id = args.notion_page_id or "symbolic-notion-demo"
        try:
            result = sync_to_notion_legacy(args.ladoc_sync, notion_page_id)
            print(f"✅ LukhasDoc sync completed: {result}")
        except Exception as e:
            logger.error(f"LukhasDoc sync failed: {e}")
            sys.exit(1)
    elif args.sync or args.daemon:
        asyncio.run(run_sync_engine(args))
    else:
        # Default to modern UI mode
        print("No mode specified, launching modern UI...")
        asyncio.run(run_ui_mode())


if __name__ == "__main__":
    main()