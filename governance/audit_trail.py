#!/usr/bin/env python3
"""
Comprehensive Audit Trail System for LUKHAS
============================================
Provides complete transparency and traceability for all AI decisions.
Based on GPT5 audit recommendations.
"""

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import numpy as np


class AuditLevel(Enum):
    """Audit detail levels"""
    MINIMAL = "minimal"          # Basic tracking
    STANDARD = "standard"        # Normal operations
    DETAILED = "detailed"        # Include reasoning
    FORENSIC = "forensic"        # Full reconstruction capability


class DecisionType(Enum):
    """Types of decisions being audited"""
    RESPONSE = "response"              # AI response generation
    MODERATION = "moderation"          # Content filtering
    ROUTING = "routing"                # Request routing
    CACHING = "caching"                # Cache decisions
    SAFETY = "safety"                  # Safety interventions
    LEARNING = "learning"              # Learning updates
    CONFIGURATION = "configuration"    # Config changes
    SYSTEM = "system"                  # System operations


@dataclass
class AuditEntry:
    """
    Single audit trail entry capturing a decision or action.
    Immutable once created for forensic integrity.
    """
    # Identifiers
    audit_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""
    interaction_id: str = ""
    
    # Decision details
    decision_type: DecisionType = DecisionType.RESPONSE
    decision: str = ""
    reasoning: str = ""
    confidence: float = 0.0
    
    # Context
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    
    # Influences
    signals: Dict[str, float] = field(default_factory=dict)  # Active signals
    policies: List[str] = field(default_factory=list)  # Applied policies
    overrides: List[str] = field(default_factory=list)  # Manual overrides
    
    # Traceability
    parent_id: Optional[str] = None  # Parent decision
    child_ids: List[str] = field(default_factory=list)  # Child decisions
    related_ids: List[str] = field(default_factory=list)  # Related decisions
    
    # Metadata
    model_version: str = ""
    component: str = ""  # Component making decision
    user_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    
    # Integrity
    checksum: str = ""  # Computed after creation
    verified: bool = False
    
    def compute_checksum(self) -> str:
        """Compute SHA-256 checksum for integrity verification"""
        # Create deterministic representation
        # Handle both enum and string types for decision_type
        decision_type_value = (
            self.decision_type.value 
            if hasattr(self.decision_type, 'value') 
            else self.decision_type
        )
        data = {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "decision_type": decision_type_value,
            "decision": self.decision,
            "input_data": json.dumps(self.input_data, sort_keys=True),
            "output_data": json.dumps(self.output_data, sort_keys=True)
        }
        
        checksum_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(checksum_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify entry hasn't been tampered with"""
        return self.checksum == self.compute_checksum()


class AuditTrail:
    """
    Comprehensive audit trail system with transparency features.
    Provides decision explanations, traceability, and forensic capabilities.
    """
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        audit_level: AuditLevel = AuditLevel.STANDARD,
        retention_days: int = 90,
        enable_explanations: bool = True
    ):
        """
        Initialize audit trail system.
        
        Args:
            db_path: Path to audit database
            audit_level: Level of audit detail
            retention_days: Days to retain audit entries
            enable_explanations: Generate human-readable explanations
        """
        self.db_path = db_path or Path("data/audit_trail.db")
        self.audit_level = audit_level
        self.retention_days = retention_days
        self.enable_explanations = enable_explanations
        
        # Initialize database
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Active session tracking
        self.active_sessions: Dict[str, List[str]] = {}
        
        # Statistics
        self.stats = {
            "total_entries": 0,
            "decisions_by_type": {},
            "average_confidence": 0.0,
            "interventions": 0
        }
        
        # Load stats
        self._load_statistics()
    
    def _init_database(self):
        """Initialize SQLite database for audit storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main audit table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_entries (
                audit_id TEXT PRIMARY KEY,
                timestamp REAL,
                session_id TEXT,
                interaction_id TEXT,
                decision_type TEXT,
                decision TEXT,
                reasoning TEXT,
                confidence REAL,
                input_data TEXT,
                output_data TEXT,
                system_state TEXT,
                signals TEXT,
                policies TEXT,
                overrides TEXT,
                parent_id TEXT,
                child_ids TEXT,
                related_ids TEXT,
                model_version TEXT,
                component TEXT,
                user_id TEXT,
                tags TEXT,
                checksum TEXT,
                verified INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (parent_id) REFERENCES audit_entries(audit_id)
            )
        """)
        
        # Create indexes for efficient queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_entries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON audit_entries(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON audit_entries(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON audit_entries(decision_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent ON audit_entries(parent_id)")
        
        # Explanations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS explanations (
                audit_id TEXT PRIMARY KEY,
                human_explanation TEXT,
                technical_explanation TEXT,
                confidence_factors TEXT,
                alternative_decisions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (audit_id) REFERENCES audit_entries(audit_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_decision(
        self,
        decision_type: DecisionType,
        decision: str,
        reasoning: str = "",
        confidence: float = 0.0,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        session_id: str = "",
        parent_id: Optional[str] = None,
        **kwargs
    ) -> AuditEntry:
        """
        Log a decision to the audit trail.
        
        Args:
            decision_type: Type of decision
            decision: The decision made
            reasoning: Reasoning behind decision
            confidence: Confidence level (0-1)
            input_data: Input that led to decision
            output_data: Output produced
            session_id: Session identifier
            parent_id: Parent decision ID
            **kwargs: Additional fields
            
        Returns:
            Created audit entry
        """
        # Create entry
        entry = AuditEntry(
            decision_type=decision_type,
            decision=decision,
            reasoning=reasoning if self.audit_level != AuditLevel.MINIMAL else "",
            confidence=confidence,
            input_data=input_data or {},
            output_data=output_data or {},
            session_id=session_id,
            parent_id=parent_id,
            **kwargs
        )
        
        # Add checksum
        entry.checksum = entry.compute_checksum()
        entry.verified = True
        
        # Save to database
        self._save_entry(entry)
        
        # Generate explanation if enabled
        if self.enable_explanations and self.audit_level in [AuditLevel.DETAILED, AuditLevel.FORENSIC]:
            self._generate_explanation(entry)
        
        # Track in session
        if session_id:
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = []
            self.active_sessions[session_id].append(entry.audit_id)
        
        # Update statistics
        self.stats["total_entries"] += 1
        if decision_type.value not in self.stats["decisions_by_type"]:
            self.stats["decisions_by_type"][decision_type.value] = 0
        self.stats["decisions_by_type"][decision_type.value] += 1
        
        return entry
    
    def _save_entry(self, entry: AuditEntry):
        """Save audit entry to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_entries (
                audit_id, timestamp, session_id, interaction_id,
                decision_type, decision, reasoning, confidence,
                input_data, output_data, system_state,
                signals, policies, overrides,
                parent_id, child_ids, related_ids,
                model_version, component, user_id, tags,
                checksum, verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.audit_id, entry.timestamp, entry.session_id, entry.interaction_id,
            entry.decision_type.value, entry.decision, entry.reasoning, entry.confidence,
            json.dumps(entry.input_data), json.dumps(entry.output_data), json.dumps(entry.system_state),
            json.dumps(entry.signals), json.dumps(entry.policies), json.dumps(entry.overrides),
            entry.parent_id, json.dumps(entry.child_ids), json.dumps(entry.related_ids),
            entry.model_version, entry.component, entry.user_id, json.dumps(list(entry.tags)),
            entry.checksum, entry.verified
        ))
        
        conn.commit()
        conn.close()
    
    def _generate_explanation(self, entry: AuditEntry):
        """Generate human-readable explanation for a decision"""
        explanations = {
            "human": "",
            "technical": "",
            "confidence_factors": [],
            "alternatives": []
        }
        
        # Human explanation
        if entry.decision_type == DecisionType.RESPONSE:
            explanations["human"] = f"Generated response based on user input with {entry.confidence:.0%} confidence."
            if entry.signals:
                active_signals = [f"{k}: {v:.1f}" for k, v in entry.signals.items() if v > 0.3]
                if active_signals:
                    explanations["human"] += f" System state: {', '.join(active_signals)}."
        
        elif entry.decision_type == DecisionType.SAFETY:
            explanations["human"] = f"Safety intervention: {entry.decision}"
            if entry.reasoning:
                explanations["human"] += f" Reason: {entry.reasoning}"
        
        elif entry.decision_type == DecisionType.MODERATION:
            explanations["human"] = f"Content moderation decision: {entry.decision}"
        
        # Technical explanation
        explanations["technical"] = f"Type: {entry.decision_type.value}\n"
        explanations["technical"] += f"Component: {entry.component}\n"
        explanations["technical"] += f"Confidence: {entry.confidence:.3f}\n"
        if entry.policies:
            explanations["technical"] += f"Policies: {', '.join(entry.policies)}\n"
        
        # Confidence factors
        if entry.confidence > 0:
            factors = []
            if entry.confidence > 0.9:
                factors.append("High pattern match")
            elif entry.confidence > 0.7:
                factors.append("Good pattern match")
            else:
                factors.append("Moderate certainty")
            
            if entry.signals.get("trust", 0) > 0.6:
                factors.append("Trusted context")
            if entry.signals.get("alignment_risk", 0) < 0.3:
                factors.append("Low risk")
            
            explanations["confidence_factors"] = factors
        
        # Save explanations
        self._save_explanation(entry.audit_id, explanations)
    
    def _save_explanation(self, audit_id: str, explanations: Dict[str, Any]):
        """Save explanation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO explanations (
                audit_id, human_explanation, technical_explanation,
                confidence_factors, alternative_decisions
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            audit_id,
            explanations["human"],
            explanations["technical"],
            json.dumps(explanations["confidence_factors"]),
            json.dumps(explanations["alternatives"])
        ))
        
        conn.commit()
        conn.close()
    
    def get_entry(self, audit_id: str) -> Optional[AuditEntry]:
        """Retrieve a specific audit entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM audit_entries WHERE audit_id = ?", (audit_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_entry(row)
        return None
    
    def get_session_trail(self, session_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM audit_entries WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    def get_decision_chain(self, audit_id: str) -> List[AuditEntry]:
        """Get complete decision chain (parents and children)"""
        entries = []
        visited = set()
        
        def traverse(aid: str):
            if aid in visited:
                return
            visited.add(aid)
            
            entry = self.get_entry(aid)
            if entry:
                entries.append(entry)
                
                # Traverse parent
                if entry.parent_id:
                    traverse(entry.parent_id)
                
                # Traverse children
                for child_id in entry.child_ids:
                    traverse(child_id)
        
        traverse(audit_id)
        
        # Sort by timestamp
        entries.sort(key=lambda e: e.timestamp)
        return entries
    
    def _row_to_entry(self, row: Tuple) -> AuditEntry:
        """Convert database row to AuditEntry"""
        entry = AuditEntry(
            audit_id=row[0],
            timestamp=row[1],
            session_id=row[2],
            interaction_id=row[3],
            decision_type=DecisionType(row[4]),
            decision=row[5],
            reasoning=row[6],
            confidence=row[7],
            input_data=json.loads(row[8]) if row[8] else {},
            output_data=json.loads(row[9]) if row[9] else {},
            system_state=json.loads(row[10]) if row[10] else {},
            signals=json.loads(row[11]) if row[11] else {},
            policies=json.loads(row[12]) if row[12] else [],
            overrides=json.loads(row[13]) if row[13] else [],
            parent_id=row[14],
            child_ids=json.loads(row[15]) if row[15] else [],
            related_ids=json.loads(row[16]) if row[16] else [],
            model_version=row[17],
            component=row[18],
            user_id=row[19],
            tags=set(json.loads(row[20])) if row[20] else set(),
            checksum=row[21],
            verified=bool(row[22])
        )
        return entry
    
    def explain_decision(self, audit_id: str) -> Dict[str, Any]:
        """Get human-readable explanation for a decision"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get explanation
        cursor.execute(
            "SELECT * FROM explanations WHERE audit_id = ?",
            (audit_id,)
        )
        row = cursor.fetchone()
        
        if row:
            explanation = {
                "human": row[1],
                "technical": row[2],
                "confidence_factors": json.loads(row[3]) if row[3] else [],
                "alternatives": json.loads(row[4]) if row[4] else []
            }
        else:
            # Generate on-demand if not exists
            entry = self.get_entry(audit_id)
            if entry:
                self._generate_explanation(entry)
                # Retry
                cursor.execute(
                    "SELECT * FROM explanations WHERE audit_id = ?",
                    (audit_id,)
                )
                row = cursor.fetchone()
                if row:
                    explanation = {
                        "human": row[1],
                        "technical": row[2],
                        "confidence_factors": json.loads(row[3]) if row[3] else [],
                        "alternatives": json.loads(row[4]) if row[4] else []
                    }
                else:
                    explanation = {"error": "Could not generate explanation"}
            else:
                explanation = {"error": "Audit entry not found"}
        
        conn.close()
        return explanation
    
    def search(
        self,
        decision_type: Optional[DecisionType] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        user_id: Optional[str] = None,
        min_confidence: Optional[float] = None,
        component: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Search audit trail with filters.
        
        Args:
            decision_type: Filter by decision type
            start_time: Start timestamp
            end_time: End timestamp
            user_id: Filter by user
            min_confidence: Minimum confidence level
            component: Filter by component
            limit: Maximum results
            
        Returns:
            List of matching audit entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_entries WHERE 1=1"
        params = []
        
        if decision_type:
            query += " AND decision_type = ?"
            params.append(decision_type.value)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)
        
        if component:
            query += " AND component = ?"
            params.append(component)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    def verify_integrity(self, audit_id: str) -> bool:
        """Verify integrity of an audit entry"""
        entry = self.get_entry(audit_id)
        if entry:
            return entry.verify_integrity()
        return False
    
    def cleanup_old_entries(self):
        """Remove entries older than retention period"""
        if self.retention_days <= 0:
            return
        
        cutoff = time.time() - (self.retention_days * 86400)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete old entries
        cursor.execute("DELETE FROM audit_entries WHERE timestamp < ?", (cutoff,))
        deleted = cursor.rowcount
        
        # Delete orphaned explanations
        cursor.execute("""
            DELETE FROM explanations 
            WHERE audit_id NOT IN (SELECT audit_id FROM audit_entries)
        """)
        
        conn.commit()
        conn.close()
        
        if deleted > 0:
            print(f"Cleaned up {deleted} old audit entries")
    
    def get_statistics(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get audit trail statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where = "1=1"
        params = []
        
        if time_window:
            cutoff = time.time() - time_window.total_seconds()
            where = "timestamp >= ?"
            params = [cutoff]
        
        # Total entries
        cursor.execute(f"SELECT COUNT(*) FROM audit_entries WHERE {where}", params)
        total = cursor.fetchone()[0]
        
        # By type
        cursor.execute(
            f"SELECT decision_type, COUNT(*) FROM audit_entries WHERE {where} GROUP BY decision_type",
            params
        )
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average confidence
        cursor.execute(f"SELECT AVG(confidence) FROM audit_entries WHERE {where}", params)
        avg_conf = cursor.fetchone()[0] or 0.0
        
        # Safety interventions
        cursor.execute(
            f"SELECT COUNT(*) FROM audit_entries WHERE {where} AND decision_type = 'safety'",
            params
        )
        interventions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entries": total,
            "by_type": by_type,
            "average_confidence": avg_conf,
            "safety_interventions": interventions,
            "active_sessions": len(self.active_sessions)
        }
    
    def _load_statistics(self):
        """Load statistics from database"""
        self.stats = self.get_statistics()
    
    def generate_transparency_report(self, session_id: str) -> str:
        """Generate transparency report for a session"""
        entries = self.get_session_trail(session_id)
        
        if not entries:
            return "No audit trail found for this session."
        
        report = f"""
📋 Transparency Report
Session: {session_id}
Duration: {entries[-1].timestamp - entries[0].timestamp:.1f} seconds
Total Decisions: {len(entries)}

Decision Breakdown:
"""
        
        # Count by type
        type_counts = {}
        for entry in entries:
            t = entry.decision_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
        
        for decision_type, count in type_counts.items():
            report += f"  • {decision_type}: {count}\n"
        
        # Average confidence
        avg_conf = np.mean([e.confidence for e in entries if e.confidence > 0])
        report += f"\nAverage Confidence: {avg_conf:.1%}\n"
        
        # Key decisions
        report += "\nKey Decisions:\n"
        for entry in entries[:10]:  # First 10
            explanation = self.explain_decision(entry.audit_id)
            if "human" in explanation:
                report += f"  • {explanation['human']}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    # Create audit trail
    audit = AuditTrail(audit_level=AuditLevel.DETAILED)
    
    print("🔍 Audit Trail System Demo")
    print("=" * 40)
    
    # Log a response decision
    entry1 = audit.log_decision(
        decision_type=DecisionType.RESPONSE,
        decision="Generated helpful response",
        reasoning="User asked a clear question about Python",
        confidence=0.85,
        input_data={"prompt": "What is Python?"},
        output_data={"response": "Python is a programming language..."},
        session_id="demo-session",
        signals={"stress": 0.2, "trust": 0.8},
        component="response_generator"
    )
    print(f"Logged response decision: {entry1.audit_id}")
    
    # Log a safety intervention
    entry2 = audit.log_decision(
        decision_type=DecisionType.SAFETY,
        decision="Blocked potentially harmful content",
        reasoning="Request contained unsafe elements",
        confidence=0.95,
        session_id="demo-session",
        parent_id=entry1.audit_id,
        component="safety_filter"
    )
    print(f"Logged safety decision: {entry2.audit_id}")
    
    # Get explanation
    explanation = audit.explain_decision(entry1.audit_id)
    print(f"\nExplanation for {entry1.audit_id}:")
    print(f"  Human: {explanation['human']}")
    print(f"  Factors: {', '.join(explanation['confidence_factors'])}")
    
    # Verify integrity
    is_valid = audit.verify_integrity(entry1.audit_id)
    print(f"\nIntegrity check: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Get statistics
    stats = audit.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Avg confidence: {stats['average_confidence']:.1%}")
    
    # Generate transparency report
    report = audit.generate_transparency_report("demo-session")
    print(f"\n{report}")