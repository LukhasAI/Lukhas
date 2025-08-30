# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: read_settings.py
# MODULE: core.config.read_settings
# DESCRIPTION: Script to display symbolic system settings loaded from configuration
#              (e.g., lukhas_settings.json via settings_loader.py).
# DEPENDENCIES: structlog, .settings_loader
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

# Original Header:
# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: read_settings.py
# 🧠 PURPOSE: Display symbolic system settings from features.config.settings.json
# 🛠️ DEPENDENCY: settings_loader.py
# ════════════════════════════════════════════════════════════════════════

import structlog

from .settings_loader import (
    SETTINGS,
    get_setting,
    list_all_keys,
    preview_defaults,
    validate_settings,
)

# Initialize logger for ΛTRACE using structlog
logger = structlog.get_logger("ΛTRACE.core.config.ReadSettingsScript")

if (
    __name__ == "__main__" and not structlog.is_configured()
):  # Ensure configuration for standalone run
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger("ΛTRACE.core.config.ReadSettingsScript")  # Re-bind after config

# AIMPORT_TODO: Ensure settings_loader.py is robustly available in the
# same directory or via PYTHONPATH.


def display_settings():
    """Prints the LUKHAS system settings snapshot to the console."""
    logger.info("Starting to display LUKHAS system settings snapshot.")

    logger.info("🔍 LUKHAS SYSTEM SETTINGS SNAPSHOT")
    logger.info("═══════════════════════════════════")
    defaults_preview = preview_defaults()
    logger.debug("Defaults preview fetched", preview_length=len(defaults_preview))
    logger.info(defaults_preview)
    logger.info("───────────────────────────────────")

    logger.info("Displaying Active Modules.")
    logger.info("🧠 Active Modules:")
    active_modules = SETTINGS.get("modules", {})
    for mod_name, is_enabled in active_modules.items():  # Corrected iteration
        status = "✅ Enabled" if is_enabled else "⛔ Disabled"
        logger.info(f"  - {mod_name}: {status}")
    logger.debug("Active modules displayed", module_states=active_modules)

    logger.info("Displaying Privacy Controls.")
    logger.info("\n🛡️ Privacy Controls:")
    privacy_settings = SETTINGS.get("privacy", {})
    for k, v in privacy_settings.items():
        logger.info(f"  - {k}: {v}")
    logger.debug("Privacy controls displayed", privacy_settings=privacy_settings)

    logger.info("Displaying Current Behavior Settings.")
    logger.info("\n🎛️ Current Behavior Settings:")
    voice_enabled = get_setting("interface.voice_enabled")
    autosave_interval = get_setting("system_behavior.autosave_interval_sec")
    logger.info(f"  - Voice Enabled: {voice_enabled}")
    logger.info(f"  - Autosave Interval: {autosave_interval} sec")
    logger.debug(
        "Behavior settings displayed",
        voice_enabled=voice_enabled,
        autosave_interval=autosave_interval,
    )

    logger.info("Displaying Symbolic Keys Available.")
    logger.info("\n📜 Symbolic Keys Available:")
    all_keys = list_all_keys()
    for key_item in all_keys:  # Renamed key to key_item to avoid conflict
        logger.info(f"  • {key_item}")
    logger.debug("Symbolic keys displayed", num_keys=len(all_keys))

    logger.info("Validating settings...")
    validation_result = (
        validate_settings()
    )  # Assuming this returns a meaningful status or logs itself
    logger.info("Settings validation complete.", validation_status=str(validation_result))

    logger.info("Displaying Consent and Memory Policy.")
    logger.info("\n📖 Consent and Memory Policy:")
    consent_required = get_setting("privacy.consent_required")
    allow_forgetting = get_setting("memory.allow_forgetting")
    memory_visible = get_setting("privacy.memory_visible_to_user")
    retention_days = get_setting("privacy.data_retention_period_days")
    export_enabled = get_setting("privacy.data_export_enabled")
    output_log = get_setting("message_output_log")
    logger.info(f"  - Consent Required: {consent_required}")
    logger.info(f"  - Forgettable Memories Allowed: {allow_forgetting}")
    logger.info(f"  - Memory Visible to User: {memory_visible}")
    logger.info(f"  - Data Retention (days): {retention_days}")
    logger.info(f"  - Export Enabled: {export_enabled}")
    logger.info(f"  - Output Log Path: {output_log}")
    logger.debug(
        "Consent/Memory policy displayed",
        consent_required=consent_required,
        allow_forgetting=allow_forgetting,
        retention_days=retention_days,
    )

    logger.info("Displaying Lukhas Persona Snapshot.")
    logger.info("\n🎭 Lukhas Persona Snapshot:")
    mood_palette = get_setting("persona.mood_palette")
    visual_theme = get_setting("persona.visual_theme")
    signature_phrase = get_setting("persona.signature_phrase")
    logger.info(f"  - Mood Palette: {mood_palette}")
    logger.info(f"  - Visual Theme: {visual_theme}")
    logger.info(f'  - Signature Phrase: "{signature_phrase}"')
    logger.debug(
        "Persona snapshot displayed",
        mood_palette_type=type(mood_palette).__name__,
        visual_theme=visual_theme,
    )

    logger.info("Displaying Context Management settings.")
    logger.info("\n🧠 Context Management:")
    mem_context_enabled = get_setting("context.enable_memory_context")
    max_window = get_setting("context.context_window_limit")
    exclude_forgettable = get_setting("context.exclude_forgettable_memories")
    logger.info(f"  - Memory Context Enabled: {mem_context_enabled}")
    logger.info(f"  - Max Context Window: {max_window}")
    logger.info(f"  - Exclude Forgettable from Context: {exclude_forgettable}")
    logger.debug(
        "Context management settings displayed",
        mem_context_enabled=mem_context_enabled,
        max_window=max_window,
    )

    logger.info("Displaying Symbolic Trace Engine settings.")
    logger.info("\n📊 Symbolic Trace Engine:")
    track_ethics = get_setting("symbolic_trace.track_ethics")
    collapse_model = get_setting("symbolic_trace.collapse_model")
    trace_log = get_setting("symbolic_trace.trace_log_path")
    logger.info(f"  - Ethics Tracking: {track_ethics}")
    logger.info(f"  - Collapse Model: {collapse_model}")
    logger.info(f"  - Trace Log Path: {trace_log}")
    logger.debug(
        "Symbolic Trace Engine settings displayed",
        track_ethics=track_ethics,
        collapse_model=collapse_model,
    )

    logger.info("Displaying User Affinity Profile settings.")
    logger.info("\n🫂 User Affinity Profile:")
    last_user = get_setting("user_affinity.last_known_user")
    sync_rate = get_setting("user_affinity.symbolic_sync_rate")
    trust_decay = get_setting("user_affinity.trust_curve_decay_days")
    logger.info(f"  - Last Known User: {last_user}")
    logger.info(f"  - Sync Rate: {sync_rate}")
    logger.info(f"  - Trust Decay (days): {trust_decay}")
    logger.debug(
        "User Affinity Profile settings displayed",
        last_user=last_user,
        sync_rate=sync_rate,
    )

    logger.info("Finished displaying LUKHAS system settings snapshot.")


if __name__ == "__main__":
    # ΛPHASE_NODE: Script Execution Start
    logger.info("read_settings.py executed as main script.")
    display_settings()
    # ΛPHASE_NODE: Script Execution End
    logger.info("read_settings.py script finished.")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: read_settings.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 0 (Utility Script)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Displays various system settings loaded via `settings_loader.py`.
#               Validates settings structure.
# FUNCTIONS: display_settings.
# CLASSES: None.
# DECORATORS: None.
# DEPENDENCIES: structlog, .settings_loader.
# INTERFACES: Command-line execution.
# ERROR HANDLING: Relies on `settings_loader.py` for handling load errors.
#                 Logs script execution phases.
# LOGGING: ΛTRACE_ENABLED via structlog. Logs start/end of script and display sections.
#          Configures basic structlog for standalone execution.
# AUTHENTICATION: Not applicable (local utility script).
# HOW TO USE:
#   python core/config/read_settings.py
# INTEGRATION NOTES: Depends on `settings_loader.py` and the JSON configuration it loads.
#                    Output is to console, designed for developer/admin inspection.
# MAINTENANCE: Update print sections if settings structure in `lukhas_settings.json` changes.
#              Ensure `settings_loader.py` functions remain compatible.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
