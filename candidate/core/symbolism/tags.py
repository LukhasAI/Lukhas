"""
Symbolic tags for agent colonies.
"""
from enum import Enum


class TagScope(Enum):
    """
    Defines the scope of a symbolic tag.
    """

    GLOBAL = "global"
    LOCAL = "local"
    ETHICAL = "ethical"
    TEMPORAL = "temporal"
    GENETIC = "genetic"


class TagPermission(Enum):
    """
    Defines the permissions for a symbolic tag.
    """

    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    RESTRICTED = "restricted"