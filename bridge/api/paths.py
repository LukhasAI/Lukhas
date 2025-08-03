"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: paths.py
Advanced: paths.py
Integration Date: 2025-05-31T07:55:28.120299
"""

"""
Central path configuration for Lukhas System
----------------------------------------
All path-related configuration should be defined here and imported by other modules.
This ensures consistency across the system and makes path updates easier to manage.
"""

from pathlib import Path

# Core paths
ROOT_DIR = Path(__file__).parent.parent.parent  # /Users/Gonz/Lukhas
CORE_DIR = ROOT_DIR / "CORE"
DATA_DIR = ROOT_DIR / "data"
MODULES_DIR = ROOT_DIR / "MODULES"

# Interface paths
INTERFACES_DIR = CORE_DIR / "interfaces"
VIDEO_DIR = INTERFACES_DIR / "video"
VOICE_DIR = INTERFACES_DIR / "voice"
REM_DIR = CORE_DIR / "rem"

# Data file paths
DREAM_LOG_PATH = DATA_DIR / "dream_log.jsonl"
MEMORY_STORE_PATH = DATA_DIR / "memory_store"
VOICE_PROFILE_PATH = DATA_DIR / "voice_profiles"

# Module paths
REM_VISUALIZER_PATH = REM_DIR / "rem_visualizer.py"
VIDEO_ADAPTER_PATH = VIDEO_DIR / "video_adapter.py"
VOICE_INTERFACE_PATH = VOICE_DIR / "voice_interface.py"

def ensure_paths():
    """Ensure all required directories exist"""
    paths = [
        DATA_DIR,
        MEMORY_STORE_PATH,
        VOICE_PROFILE_PATH
    ]
    
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
        
def get_path(path_key: str) -> Path:
    """Get a path by its key name"""
    paths = {
        "root": ROOT_DIR,
        "core": CORE_DIR,
        "data": DATA_DIR,
        "modules": MODULES_DIR,
        "interfaces": INTERFACES_DIR,
        "video": VIDEO_DIR,
        "voice": VOICE_DIR,
        "rem": REM_DIR,
        "dream_log": DREAM_LOG_PATH,
        "memory_store": MEMORY_STORE_PATH,
        "voice_profiles": VOICE_PROFILE_PATH,
        "rem_visualizer": REM_VISUALIZER_PATH,
        "video_adapter": VIDEO_ADAPTER_PATH,
        "voice_interface": VOICE_INTERFACE_PATH
    }
    
    return paths.get(path_key, ROOT_DIR)
