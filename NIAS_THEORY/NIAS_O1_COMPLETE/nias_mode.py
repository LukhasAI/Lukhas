"""
nias_mode.py — Symbolic Mode Detector for NIAS

Determines the current operating mode of NIAS:
- Standalone
- DAST-enhanced
- Full LUCΛS integration

Author: You
"""


def detect_mode():
    has_dast = False
    has_abas = False
    has_mesh = False

    try:
        has_dast = True
    except ImportError:
        pass

    try:
        has_abas = True
    except ImportError:
        pass

    try:
        has_mesh = True
    except ImportError:
        pass

    if has_dast and has_abas and has_mesh:
        return "LUCAS_FULL"
    elif has_dast:
        return "DAST_ENHANCED"
    else:
        return "STANDALONE"


def print_mode_banner():
    mode = detect_mode()
    banners = {
        "STANDALONE": "🧍 NIAS running in Standalone Mode — symbolic SDK active",
        "DAST_ENHANCED": "🧿 NIAS running in DAST-Enhanced Mode — task stream linked",
        "LUCAS_FULL": "🧠 NIAS fully integrated with LUCΛS — dream-aware symbolic alignment enabled",
    }
    print(banners.get(mode, "🔘 Unknown NIAS mode"))
