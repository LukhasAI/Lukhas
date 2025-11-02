"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: settings_loader.py
Advanced: settings_loader.py
Integration Date: 2025-05-31T07:55:28.120950
"""

# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: settings_loader.py
# 🧠 PURPOSE: Load and serve symbolic settings from system_settings.json
# 🔄 USAGE: Imported by modules to access config values
# ════════════════════════════════════════════════════════════════════════
import json

SETTINGS_PATH = "lukhas_settings.json"


def load_settings(path=SETTINGS_PATH):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"[Settings Loader Error] {e!s}")
        return {}


SETTINGS = load_settings()


def get_setting(key_path, default=None):
    """
    Access nested settings via dot notation.
    Example: get_setting("memory.allow_forgetting")
    """
    keys = key_path.split(".")
    value = SETTINGS
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    log_setting_access(key_path)
    return value


def is_module_enabled(module_name):
    return SETTINGS.get("modules", {}).get(module_name, False)


def print_all_settings():
    print(json.dumps(SETTINGS, indent=2))


def validate_settings(required_keys=None):
    if required_keys is None:
        required_keys = [
            "version",
            "created",
            "modules",
            "privacy",
            "permissions",
        ]
    missing = [key for key in required_keys if key not in SETTINGS]
    if missing:
        print(f"[Settings Validation Warning] Missing keys: {missing}")
    else:
        print("✅ Settings validation passed.")


def log_setting_access(key_path):
    if SETTINGS.get("privacy", {}).get("user_analytics_logging", False):
        try:
            with open("logs/setting_access.log", "a") as log:
                log.write(f"{key_path}\n")
        except Exception as e:
            print(f"[Log Access Error] {e!s}")


def preview_defaults():
    tone = get_setting("default_tone", "symbolic")
    lang = get_setting("default_language", "en")
    mood = get_setting("persona.mood_palette", ["curious"])
    return f"🧠 Lukhas starts in '{tone}' tone, speaks '{lang}', and feels '{mood[0]}'."


def list_all_keys():
    def flatten(d, prefix=""):
        keys = []
        for k, v in d.items():
            if isinstance(v, dict):
                keys += flatten(v, prefix + k + ".")
            else:
                keys.append(prefix + k)
        return keys

    return flatten(SETTINGS)


# Example usage (can be removed in prod):
if __name__ == "__main__":
    print("🧠 Loaded Lukhas Settings:")
    print_all_settings()
    validate_settings()
    print(preview_defaults())
