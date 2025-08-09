"""
Symbolic Module
"""

# Import vocabularies
from . import vocabularies

# Import personal symbol dictionary
try:
    from .personal.symbol_dictionary import PersonalSymbolDictionary, GestureType
except ImportError:
    PersonalSymbolDictionary = None
    GestureType = None

# Import universal exchange
try:
    from .exchange.universal_exchange import UniversalSymbolExchange, ExchangeProtocol
except ImportError:
    UniversalSymbolExchange = None
    ExchangeProtocol = None

__all__ = [
    'vocabularies',
    'PersonalSymbolDictionary',
    'GestureType',
    'UniversalSymbolExchange',
    'ExchangeProtocol',
]