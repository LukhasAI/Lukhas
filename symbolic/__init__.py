"""
Symbolic Module
"""

# Import vocabularies
from . import vocabularies

# Import personal symbol dictionary
try:
    from .personal.symbol_dictionary import (
        GestureType,
        PersonalSymbolDictionary,
    )
except ImportError:
    PersonalSymbolDictionary = None
    GestureType = None

# Import universal exchange
try:
    from .exchange.universal_exchange import (
        ExchangeProtocol,
        UniversalSymbolExchange,
    )
except ImportError:
    UniversalSymbolExchange = None
    ExchangeProtocol = None

__all__ = [
    "ExchangeProtocol",
    "GestureType",
    "PersonalSymbolDictionary",
    "UniversalSymbolExchange",
    "vocabularies",
]
