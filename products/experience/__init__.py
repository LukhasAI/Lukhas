"""Experience Products - User Experience, Voice, and Language Systems.

- voice/              - Complete voice system (TTS, recognition, modulation, branding)
- feedback/           - User feedback collection and analysis systems
- universal_language/ - Linguistic framework (vocabulary, grammar, glyph systems)
- dashboard/          - Visualization and dashboard systems
"""

from .streamlit_safe import STREAMLIT_AVAILABLE, get_streamlit

# ΛTAG: experience_streamlit
st = get_streamlit()

__all__ = ["dashboard", "feedback", "universal_language", "voice", "st", "STREAMLIT_AVAILABLE"]
