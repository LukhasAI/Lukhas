#!/usr/bin/env python3
"""
TEQ Gate with Provenance Integration
Automatically generates execution receipts for all policy decisions
"""

import time
import hashlib
import uuid
from typing import Dict, Any, Optional

from qi.safety.teq_gate import TEQCoupler, GateResult
from qi.provenance.receipts_hub import emit_receipt

class TEQWithProvenance(TEQCoupler):
    """TEQ Gate enhanced with automatic provenance generation"""
    
    def __init__(self, *args, enable_provenance: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_provenance = enable_provenance
        self.service_name = "lukhas-teq"
    
    def run(self, task: str, context: Dict[str, Any]) -> GateResult:
        """Run TEQ checks and generate provenance receipt"""
        
        # Track execution timing
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        # Extract relevant context
        user_id = self._extract_user_id(context)
        text_content = context.get("text", "")
        
        # Generate content hash for artifact tracking
        artifact_sha = hashlib.sha256(
            text_content.encode("utf-8") if text_content else b"empty"
        ).hexdigest()
        
        # Run the original TEQ checks
        result = super().run(task, context)
        
        end_time = time.time()
        
        # Generate provenance receipt if enabled
        if self.enable_provenance:
            try:
                receipt = self._generate_receipt(
                    artifact_sha=artifact_sha,
                    run_id=run_id,
                    task=task,
                    start_time=start_time,
                    end_time=end_time,
                    user_id=user_id,
                    context=context,
                    result=result
                )
                
                # Attach receipt ID to result for reference
                result.provenance_receipt_id = receipt.get("id")
                
            except Exception as e:
                # Don't fail TEQ if provenance fails
                print(f"Warning: Provenance generation failed: {e}")
        
        return result
    
    def _extract_user_id(self, context: Dict[str, Any]) -> Optional[str]:
        """Extract user ID from various context formats"""
        # Try common patterns
        if "user_id" in context:
            return context["user_id"]
        if "user_profile" in context and isinstance(context["user_profile"], dict):
            return context["user_profile"].get("user_id")
        if "user" in context:
            return str(context["user"])
        return None
    
    def _generate_receipt(
        self,
        artifact_sha: str,
        run_id: str,
        task: str,
        start_time: float,
        end_time: float,
        user_id: Optional[str],
        context: Dict[str, Any],
        result: GateResult
    ) -> Dict[str, Any]:
        """Generate comprehensive provenance receipt"""
        
        # Extract policy-relevant metadata
        jurisdiction = result.jurisdiction
        ctx_type = context.get("context", None)
        
        # Determine risk flags from TEQ reasons
        risk_flags = []
        if "PII" in str(result.reasons):
            risk_flags.append("pii_detected")
        if "medical" in str(result.reasons).lower():
            risk_flags.append("medical_content")
        if "budget" in str(result.reasons).lower():
            risk_flags.append("budget_exceeded")
        if not result.allowed:
            risk_flags.append("policy_blocked")
        
        # Extract consent/capability references if available
        consent_id = context.get("consent_receipt_id")
        capability_ids = context.get("capability_lease_ids", [])
        
        # Token counts if available
        tokens_in = context.get("tokens_in")
        tokens_out = context.get("tokens_out")
        
        # Generate the receipt
        receipt_data = emit_receipt(
            artifact_sha=artifact_sha,
            artifact_mime="text/plain",
            artifact_size=len(context.get("text", "")),
            storage_url=None,  # No storage for inline text
            run_id=run_id,
            task=task,
            started_at=start_time,
            ended_at=end_time,
            user_id=user_id,
            service_name=self.service_name,
            jurisdiction=jurisdiction,
            context=ctx_type,
            policy_decision_id=f"teq-{run_id}",
            consent_receipt_id=consent_id,
            capability_lease_ids=capability_ids,
            risk_flags=risk_flags,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            # Add TEQ-specific metadata
            extra_steps=[
                {
                    "phase": "teq_decision",
                    "allowed": result.allowed,
                    "reasons": result.reasons,
                    "remedies": result.remedies
                }
            ]
        )
        
        return receipt_data


def demo():
    """Demo the provenance-enabled TEQ gate"""
    import os
    
    # Initialize with provenance
    gate = TEQWithProvenance(
        policy_dir=os.path.join(os.path.dirname(__file__), "policy_packs"),
        jurisdiction="global",
        enable_provenance=True
    )
    
    # Test with various contexts
    test_cases = [
        {
            "task": "generate_summary",
            "context": {
                "user_id": "demo_user",
                "text": "Please summarize this document about AI safety.",
                "tokens_in": 15,
                "tokens_out": 50
            }
        },
        {
            "task": "answer_medical",
            "context": {
                "user_profile": {"user_id": "medical_user", "age": 25},
                "text": "What are the side effects of aspirin?",
                "tokens_in": 10,
                "tokens_out": 100
            }
        },
        {
            "task": "personalize_reply",
            "context": {
                "user_id": "personal_user",
                "text": "Customize this response for me.",
                "consent_receipt_id": "consent-demo-123"
            }
        }
    ]
    
    print("=" * 60)
    print("TEQ Gate with Provenance - Demo")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['task']}")
        print("-" * 40)
        
        result = gate.run(test["task"], test["context"])
        
        print(f"Allowed: {result.allowed}")
        if not result.allowed:
            print(f"Reasons: {result.reasons}")
        
        if hasattr(result, "provenance_receipt_id"):
            print(f"Receipt ID: {result.provenance_receipt_id}")
        
        # Load and display the receipt
            state_dir = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
            receipt_path = os.path.join(
                state_dir, 
                "provenance", 
                "exec_receipts", 
                f"{result.provenance_receipt_id}.json"
            )
            
            if os.path.exists(receipt_path):
                import json
                with open(receipt_path, 'r') as f:
                    receipt = json.load(f)
                    print(f"  - Task: {receipt['activity']['type']}")
                    print(f"  - Jurisdiction: {receipt['activity']['jurisdiction']}")
                    print(f"  - Risk flags: {receipt['risk_flags']}")
                    print(f"  - Latency: {receipt['latency_ms']}ms")
    
    print("\n" + "=" * 60)
    print("✅ Provenance integration complete!")
    print("All policy decisions now generate cryptographically-sealed receipts.")
    print("=" * 60)


if __name__ == "__main__":
    demo()