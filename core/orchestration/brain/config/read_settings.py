"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: read_settings.py
Advanced: read_settings.py
Integration Date: 2025-05-31T07:55:28.126331
"""

# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: read_settings.py
# 🧠 PURPOSE: Display symbolic system settings from system_settings.json
# 🛠️ DEPENDENCY: settings_loader.py
# ════════════════════════════════════════════════════════════════════════

from settings_loader import (
    SETTINGS,
    preview_defaults,
    validate_settings,
    list_all_keys,
    get_setting
)

print("🔍 LUKHAS SYSTEM SETTINGS SNAPSHOT")
print("═══════════════════════════════════")
print(preview_defaults())
print("───────────────────────────────────")

print("🧠 Active Modules:")
for mod in SETTINGS.get("modules", {}):
    status = "✅ Enabled" if SETTINGS["modules"][mod] else "⛔ Disabled"
    print(f"  - {mod}: {status}")

print("\n🛡️ Privacy Controls:")
for k, v in SETTINGS.get("privacy", {}).items():
    print(f"  - {k}: {v}")

print("\n🎛️ Current Behavior Settings:")
print(f"  - Voice Enabled: {get_setting('interface.voice_enabled')}")
print(f"  - Autosave Interval: {get_setting('system_behavior.autosave_interval_sec')} sec")

print("\n📜 Symbolic Keys Available:")
for key in list_all_keys():
    print(f"  • {key}")

validate_settings()

print("\n📖 Consent and Memory Policy:")
print(f"  - Consent Required: {get_setting('privacy.consent_required')}")
print(f"  - Forgettable Memories Allowed: {get_setting('memory.allow_forgetting')}")
print(f"  - Memory Visible to User: {get_setting('privacy.memory_visible_to_user')}")
print(f"  - Data Retention (days): {get_setting('privacy.data_retention_period_days')}")
print(f"  - Export Enabled: {get_setting('privacy.data_export_enabled')}")
print(f"  - Output Log Path: {get_setting('message_output_log')}")

print("\n🎭 Lukhas Persona Snapshot:")
print(f"  - Mood Palette: {get_setting('persona.mood_palette')}")
print(f"  - Visual Theme: {get_setting('persona.visual_theme')}")
print(f"  - Signature Phrase: \"{get_setting('persona.signature_phrase')}\"")

print("\n🧠 Context Management:")
print(f"  - Memory Context Enabled: {get_setting('context.enable_memory_context')}")
print(f"  - Max Context Window: {get_setting('context.context_window_limit')}")
print(f"  - Exclude Forgettable from Context: {get_setting('context.exclude_forgettable_memories')}")

print("\n📊 Symbolic Trace Engine:")
print(f"  - Ethics Tracking: {get_setting('symbolic_trace.track_ethics')}")
print(f"  - Collapse Model: {get_setting('symbolic_trace.collapse_model')}")
print(f"  - Trace Log Path: {get_setting('symbolic_trace.trace_log_path')}")

print("\n🫂 User Affinity Profile:")
print(f"  - Last Known User: {get_setting('user_affinity.last_known_user')}")
print(f"  - Sync Rate: {get_setting('user_affinity.symbolic_sync_rate')}")
print(f"  - Trust Decay (days): {get_setting('user_affinity.trust_curve_decay_days')}")