"""
MATRIZ Adapter for Bridge Module
Emits MATRIZ-compliant nodes for external API integration events
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path


class BridgeMatrizAdapter:
    """Adapter to emit MATRIZ nodes for bridge/API integration events"""
    
    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"
    
    @staticmethod
    def create_node(
        node_type: str,
        state: Dict[str, float],
        labels: Optional[List[str]] = None,
        provenance_extra: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a MATRIZ-compliant node for bridge events"""
        
        node = {
            "version": 1,
            "id": f"LT-BRDG-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.9),
                "salience": state.get("salience", 0.6),
                "urgency": state.get("urgency", 0.3),
                "novelty": state.get("novelty", 0.4),
                **state
            },
            "timestamps": {
                "created_ts": int(time.time() * 1000)
            },
            "provenance": {
                "producer": "lukhas.bridge",
                "capabilities": ["bridge:api", "bridge:llm", "bridge:orchestrate"],
                "tenant": "system",
                "trace_id": f"LT-BRDG-{int(time.time())}",
                "consent_scopes": ["system:bridge"],
                **(provenance_extra or {})
            }
        }
        
        if labels:
            node["labels"] = labels
            
        return node
    
    @staticmethod
    def emit_api_call(
        api_id: str,
        provider: str,
        endpoint: str,
        latency_ms: int,
        success: bool
    ) -> Dict[str, Any]:
        """Emit an external API call event"""
        
        urgency = 0.1 if success else 0.8
        
        return BridgeMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 1.0,
                "salience": 0.5,
                "urgency": urgency,
                "novelty": 0.2,
                "latency_ms": float(latency_ms),
                "success": 1.0 if success else 0.0
            },
            labels=[
                f"api:{api_id}",
                f"provider:{provider}",
                f"endpoint:{endpoint}",
                "status:success" if success else "status:failed",
                "bridge:api"
            ]
        )
    
    @staticmethod
    def emit_llm_interaction(
        llm_id: str,
        model: str,
        tokens_used: int,
        response_quality: float
    ) -> Dict[str, Any]:
        """Emit an LLM interaction event"""
        
        return BridgeMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": response_quality,
                "salience": 0.7,
                "urgency": 0.3,
                "novelty": 0.5,
                "tokens": float(tokens_used),
                "quality": response_quality
            },
            labels=[
                f"llm:{llm_id}",
                f"model:{model}",
                f"tokens:{tokens_used}",
                "bridge:llm"
            ]
        )
    
    @staticmethod
    def emit_orchestration_event(
        orchestration_id: str,
        services: List[str],
        coordination_type: str,
        success_rate: float
    ) -> Dict[str, Any]:
        """Emit a multi-service orchestration event"""
        
        return BridgeMatrizAdapter.create_node(
            node_type="CAUSAL",
            state={
                "confidence": 0.9,
                "salience": 0.8,
                "urgency": 0.4,
                "novelty": 0.3,
                "service_count": float(len(services)),
                "success_rate": success_rate
            },
            labels=[
                f"orchestration:{orchestration_id}",
                f"type:{coordination_type}",
                f"services:{len(services)}",
                "bridge:orchestrate"
            ] + [f"service:{s}" for s in services[:3]]
        )
    
    @staticmethod
    def emit_consensus_event(
        consensus_id: str,
        models: List[str],
        agreement_score: float,
        final_decision: str
    ) -> Dict[str, Any]:
        """Emit a multi-model consensus event"""
        
        return BridgeMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": agreement_score,
                "salience": 0.9,
                "urgency": 0.3,
                "novelty": 0.4,
                "model_count": float(len(models)),
                "agreement": agreement_score
            },
            labels=[
                f"consensus:{consensus_id}",
                f"decision:{final_decision}",
                f"models:{len(models)}",
                "bridge:consensus"
            ]
        )
    
    @staticmethod
    def validate_node(node: Dict[str, Any]) -> bool:
        """Validate that a node meets MATRIZ requirements"""
        required_fields = ["version", "id", "type", "state", "timestamps", "provenance"]
        
        for field in required_fields:
            if field not in node:
                return False
                
        # Check required provenance fields
        required_prov = ["producer", "capabilities", "tenant", "trace_id", "consent_scopes"]
        for field in required_prov:
            if field not in node.get("provenance", {}):
                return False
                
        return True
    
    @staticmethod
    def save_node(node: Dict[str, Any], output_dir: Optional[Path] = None) -> Path:
        """Save a MATRIZ node to disk for audit"""
        if output_dir is None:
            output_dir = Path("memory/inbox/bridge")
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(node, f, indent=2)
            
        return filepath