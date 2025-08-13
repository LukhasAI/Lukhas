"""
LUKHAS AI Colony System
Distributed agent colonies for specialized processing
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

__version__ = "1.0.0"
__trinity__ = "⚛️🧠🛡️"

# Core colony interfaces
from . import base
from . import governance
from . import reasoning
from . import consciousness
from . import identity
from . import memory
from . import creativity
from . import orchestrator

# Colony registry
from .base import ColonyRegistry, get_colony_registry

__all__ = [
    'base',
    'governance', 
    'reasoning',
    'consciousness',
    'identity',
    'memory',
    'creativity',
    'orchestrator',
    'ColonyRegistry',
    'get_colony_registry'
]

def trinity_sync():
    """Synchronize all colonies with Trinity Framework"""
    registry = get_colony_registry()
    
    sync_results = {}
    for colony_name, colony in registry.get_all_colonies().items():
        if hasattr(colony, 'trinity_sync'):
            sync_results[colony_name] = colony.trinity_sync()
        else:
            sync_results[colony_name] = {'status': 'no_trinity_support'}
    
    return {
        'identity': '⚛️',
        'consciousness': '🧠', 
        'guardian': '🛡️',
        'colony_sync': sync_results,
        'total_colonies': len(sync_results)
    }