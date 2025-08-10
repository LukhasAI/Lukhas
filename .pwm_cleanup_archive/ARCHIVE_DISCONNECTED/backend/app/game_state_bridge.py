"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : game_state_bridge.py                           │
│ DESCRIPTION : Symbolic game save state bridge for LUKHASID    │
│ TYPE        : Symbolic Game Memory Bridge                    │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import shutil
from datetime import datetime
from pathlib import Path

# ── Base Cloud Directory (Linked to Tiered Storage) ────────────

BASE_CLOUD_STORAGE = {
    1: "cloud_storage_tier1",
    2: "cloud_storage_tier2",
    3: "cloud_storage_tier3",
    4: "cloud_storage_tier4",
}

# ── Symbolic Game State Functions ─────────────────────────────


def archive_game_state(user_id: int, file_path: str, game_name: str, user_tier: int):
    """
    Archive a symbolic game save or progress memory.
    """
    base_dir = BASE_CLOUD_STORAGE.get(user_tier)
    if not base_dir:
        raise ValueError("Invalid user tier.")

    destination = Path(base_dir) / str(user_id) / "game_states" / game_name
    destination.mkdir(parents=True, exist_ok=True)

    filename = f"save_{datetime.utcnow().timestamp()}.sav"
    shutil.copy(file_path, destination / filename)

    print(f"🎮 Game state archived: {destination}/{filename}")
    return str(destination / filename)


def list_user_game_states(user_id: int, user_tier: int):
    """
    List all symbolic game saves for a user.
    """
    base_dir = BASE_CLOUD_STORAGE.get(user_tier)
    if not base_dir:
        raise ValueError("Invalid user tier.")

    user_dir = Path(base_dir) / str(user_id) / "game_states"
    if not user_dir.exists():
        return []

    games = {}
    for game_folder in user_dir.glob("*"):
        if game_folder.is_dir():
            saves = [f.name for f in game_folder.glob("*")]
            games[game_folder.name] = saves

    return games


# ===============================================================
# 💾 HOW TO USE
# ===============================================================
# ▶️ IMPORT THIS MODULE:
#     from backend.app.game_state_bridge import archive_game_state, list_user_game_states
#
# 🧠 WHAT THIS MODULE DOES:
# - Symbolically archives user game progress saves
# - Lists all symbolic game memories across the mesh
#
# 🧑‍🏫 GOOD FOR:
# - Gaming continuity between devices
# - Symbolic emotional memory linkage to games
# - Mesh-linked symbolic gaming experience mapping
# ===============================================================
