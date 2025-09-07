"""
Enhanced Swarm Architecture Components
Provides enhanced implementations for swarm-based consciousness systems
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
from datetime import datetime

class AgentState(Enum):
    """State enumeration for swarm agents."""
    INACTIVE = "inactive"
    ACTIVE = "active" 
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"

class CapabilityLevel(Enum):
    """Agent capability levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class MemoryType(Enum):
    """Types of agent memory"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"

@dataclass
class AgentCapability:
    """Represents an agent's capability in a specific domain"""
    domain: str
    level: CapabilityLevel = CapabilityLevel.BASIC
    confidence: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_confidence(self, new_confidence: float):
        """Update capability confidence level"""
        self.confidence = max(0.0, min(1.0, new_confidence))
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "domain": self.domain,
            "level": self.level.value,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class AgentMemory:
    """Enhanced agent memory system"""
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: Dict[str, Any] = field(default_factory=dict)
    working: Dict[str, Any] = field(default_factory=dict)
    episodic: List[Dict[str, Any]] = field(default_factory=list)
    max_episodic: int = 100
    
    def store(self, memory_type: MemoryType, key: str, value: Any):
        """Store memory in specified type"""
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term[key] = value
        elif memory_type == MemoryType.LONG_TERM:
            self.long_term[key] = value
        elif memory_type == MemoryType.WORKING:
            self.working[key] = value
        elif memory_type == MemoryType.EPISODIC:
            episode = {
                "timestamp": datetime.now().isoformat(),
                "key": key,
                "value": value
            }
            self.episodic.append(episode)
            # Keep only recent episodes
            if len(self.episodic) > self.max_episodic:
                self.episodic = self.episodic[-self.max_episodic:]
    
    def retrieve(self, memory_type: MemoryType, key: str) -> Any:
        """Retrieve memory from specified type"""
        if memory_type == MemoryType.SHORT_TERM:
            return self.short_term.get(key)
        elif memory_type == MemoryType.LONG_TERM:
            return self.long_term.get(key)
        elif memory_type == MemoryType.WORKING:
            return self.working.get(key)
        elif memory_type == MemoryType.EPISODIC:
            # Return episodes matching key
            return [ep for ep in self.episodic if ep.get("key") == key]
        return None
    
    def clear(self, memory_type: Optional[MemoryType] = None):
        """Clear specified memory type or all memory"""
        if memory_type is None:
            self.short_term.clear()
            self.long_term.clear()
            self.working.clear()
            self.episodic.clear()
        elif memory_type == MemoryType.SHORT_TERM:
            self.short_term.clear()
        elif memory_type == MemoryType.LONG_TERM:
            self.long_term.clear()
        elif memory_type == MemoryType.WORKING:
            self.working.clear()
        elif memory_type == MemoryType.EPISODIC:
            self.episodic.clear()

class EnhancedSwarmAgent:
    """Enhanced swarm agent with advanced capabilities"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities: Dict[str, AgentCapability] = {}
        self.memory = AgentMemory()
        self.active = True
        self.created_at = datetime.now()
    
    def add_capability(self, domain: str, level: CapabilityLevel = CapabilityLevel.BASIC):
        """Add a new capability to the agent"""
        self.capabilities[domain] = AgentCapability(domain=domain, level=level)
    
    def get_capability(self, domain: str) -> Optional[AgentCapability]:
        """Get capability for specified domain"""
        return self.capabilities.get(domain)
    
    def update_capability_confidence(self, domain: str, confidence: float):
        """Update confidence for a specific capability"""
        if domain in self.capabilities:
            self.capabilities[domain].update_confidence(confidence)

class EnhancedColony:
    """Enhanced colony for agent coordination"""
    
    def __init__(self, colony_id: str):
        self.colony_id = colony_id
        self.agents: Dict[str, EnhancedSwarmAgent] = {}
        self.created_at = datetime.now()
        self.active = True
    
    def add_agent(self, agent: EnhancedSwarmAgent):
        """Add agent to colony"""
        self.agents[agent.agent_id] = agent
    
    def remove_agent(self, agent_id: str):
        """Remove agent from colony"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def get_agents_with_capability(self, domain: str) -> List[EnhancedSwarmAgent]:
        """Get all agents that have a specific capability"""
        return [
            agent for agent in self.agents.values()
            if domain in agent.capabilities and agent.active
        ]

class EnhancedSwarmHub:
    """Enhanced swarm hub for multi-colony coordination"""
    
    def __init__(self, hub_id: str):
        self.hub_id = hub_id
        self.colonies: Dict[str, EnhancedColony] = {}
        self.created_at = datetime.now()
        self.active = True
    
    def add_colony(self, colony: EnhancedColony):
        """Add colony to hub"""
        self.colonies[colony.colony_id] = colony
    
    def remove_colony(self, colony_id: str):
        """Remove colony from hub"""
        if colony_id in self.colonies:
            del self.colonies[colony_id]
    
    def get_total_agents(self) -> int:
        """Get total number of agents across all colonies"""
        return sum(len(colony.agents) for colony in self.colonies.values())
    
    def find_agents_with_capability(self, domain: str) -> List[EnhancedSwarmAgent]:
        """Find all agents across colonies with specified capability"""
        agents = []
        for colony in self.colonies.values():
            agents.extend(colony.get_agents_with_capability(domain))
        return agents

# Export main classes
__all__ = [
    "AgentCapability",
    "AgentMemory", 
    "EnhancedSwarmAgent",
    "EnhancedColony",
    "EnhancedSwarmHub",
    "CapabilityLevel",
    "MemoryType"
]
