"""
Decision Audit Embedding Engine
Tracks and audits all system decisions for transparency and compliance
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class DecisionAuditEngine:
    """
    Central engine for auditing and tracking system decisions
    Provides transparency and traceability for all AI decisions
    """
    
    def __init__(self, audit_dir: str = "audits"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        self.active_sessions = {}
        self.decision_count = 0
        self.audit_cache = []
        self.initialized = False
        
    async def initialize(self):
        """Initialize the audit engine"""
        logger.info("Initializing Decision Audit Engine")
        self.initialized = True
        return True
        
    async def embed_decision(self, 
                           decision_type: str,
                           context: Dict[str, Any],
                           source: str,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Embed a decision into the audit trail
        
        Args:
            decision_type: Type of decision being made
            context: Context information about the decision
            source: Source module/component making the decision
            metadata: Additional metadata
            
        Returns:
            Decision ID for tracking
        """
        decision_id = self._generate_decision_id(decision_type, source)
        
        audit_entry = {
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type,
            "source": source,
            "context": context,
            "metadata": metadata or {},
            "session_id": self._get_session_id(source)
        }
        
        # Add to cache
        self.audit_cache.append(audit_entry)
        self.decision_count += 1
        
        # Persist if cache is large enough
        if len(self.audit_cache) >= 100:
            await self._persist_audit_cache()
            
        logger.debug(f"Decision embedded: {decision_id} from {source}")
        return decision_id
        
    async def track_outcome(self, 
                          decision_id: str,
                          outcome: Any,
                          success: bool = True,
                          error: Optional[str] = None):
        """Track the outcome of a decision"""
        outcome_entry = {
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "outcome": str(outcome),
            "success": success,
            "error": error
        }
        
        # Find and update the original decision
        for entry in reversed(self.audit_cache):
            if entry.get("decision_id") == decision_id:
                entry["outcome"] = outcome_entry
                break
                
    async def get_audit_trail(self, 
                            source: Optional[str] = None,
                            decision_type: Optional[str] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit trail with optional filters"""
        # Ensure cache is persisted
        await self._persist_audit_cache()
        
        # Load audit files
        audit_entries = []
        audit_files = sorted(self.audit_dir.glob("*.json"), reverse=True)
        
        for audit_file in audit_files[:10]:  # Last 10 files
            with open(audit_file, 'r') as f:
                entries = json.load(f)
                
                # Apply filters
                for entry in entries:
                    if source and entry.get("source") != source:
                        continue
                    if decision_type and entry.get("decision_type") != decision_type:
                        continue
                        
                    audit_entries.append(entry)
                    
                    if len(audit_entries) >= limit:
                        return audit_entries
                        
        return audit_entries
        
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate a compliance report from audit data"""
        await self._persist_audit_cache()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_decisions": self.decision_count,
            "decision_types": {},
            "sources": {},
            "success_rate": 0.0
        }
        
        # Analyze recent audits
        recent_audits = await self.get_audit_trail(limit=1000)
        
        total_with_outcome = 0
        successful_outcomes = 0
        
        for audit in recent_audits:
            # Count by type
            dtype = audit.get("decision_type", "unknown")
            report["decision_types"][dtype] = report["decision_types"].get(dtype, 0) + 1
            
            # Count by source
            source = audit.get("source", "unknown")
            report["sources"][source] = report["sources"].get(source, 0) + 1
            
            # Calculate success rate
            if "outcome" in audit:
                total_with_outcome += 1
                if audit["outcome"].get("success", False):
                    successful_outcomes += 1
                    
        if total_with_outcome > 0:
            report["success_rate"] = successful_outcomes / total_with_outcome
            
        return report
        
    def _generate_decision_id(self, decision_type: str, source: str) -> str:
        """Generate unique decision ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{decision_type}:{source}:{timestamp}:{self.decision_count}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
        
    def _get_session_id(self, source: str) -> str:
        """Get or create session ID for source"""
        if source not in self.active_sessions:
            self.active_sessions[source] = hashlib.sha256(
                f"{source}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:8]
        return self.active_sessions[source]
        
    async def _persist_audit_cache(self):
        """Persist audit cache to disk"""
        if not self.audit_cache:
            return
            
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audit_file = self.audit_dir / f"audit_{timestamp}.json"
        
        with open(audit_file, 'w') as f:
            json.dump(self.audit_cache, f, indent=2)
            
        logger.info(f"Persisted {len(self.audit_cache)} audit entries to {audit_file}")
        self.audit_cache = []


class DecisionAuditDecorator:
    """Decorator for automatic decision auditing"""
    
    def __init__(self, audit_engine: DecisionAuditEngine, decision_type: str):
        self.audit_engine = audit_engine
        self.decision_type = decision_type
        
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract source from first arg if it's self
            source = "unknown"
            if args and hasattr(args[0], '__class__'):
                source = args[0].__class__.__name__
                
            # Create context from function args
            context = {
                "function": func.__name__,
                "args": str(args[1:]),  # Skip self
                "kwargs": str(kwargs)
            }
            
            # Embed decision
            decision_id = await self.audit_engine.embed_decision(
                self.decision_type,
                context,
                source
            )
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Track outcome
                await self.audit_engine.track_outcome(
                    decision_id,
                    result,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Track failure
                await self.audit_engine.track_outcome(
                    decision_id,
                    None,
                    success=False,
                    error=str(e)
                )
                raise
                
        return wrapper