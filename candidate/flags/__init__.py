"""
Flags Module
"""
from .ff import Flags

_flags_instance = Flags()

def get_flags() -> Flags:
    """Returns the singleton Flags instance"""
    return _flags_instance
