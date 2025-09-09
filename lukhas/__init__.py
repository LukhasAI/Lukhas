"""
LUKHAS AI - Accepted/Production Code
Stable, tested, and ready for production use
"""
import streamlit as st

# Import all lukhas submodules to enable lukhas.* namespace access
try:
    from . import memory
except ImportError:
    memory = None

try:
    from . import consciousness
except ImportError:
    consciousness = None

try:
    from . import api
except ImportError:
    api = None

try:
    from . import core
except ImportError:
    core = None

try:
    from . import identity
except ImportError:
    identity = None

try:
    from . import agents
except ImportError:
    agents = None

try:
    from . import governance
except ImportError:
    governance = None

try:
    from . import bio
except ImportError:
    bio = None

try:
    from . import qi
except ImportError:
    qi = None

try:
    from . import branding
except ImportError:
    branding = None

try:
    from . import emotion
except ImportError:
    emotion = None

try:
    from . import security
except ImportError:
    security = None

try:
    from . import orchestration
except ImportError:
    orchestration = None

try:
    from . import bridge
except ImportError:
    bridge = None

try:
    from . import observability
except ImportError:
    observability = None

try:
    from . import matriz
except ImportError:
    matriz = None

try:
    from . import vivox
except ImportError:
    vivox = None

try:
    from . import rl
except ImportError:
    rl = None