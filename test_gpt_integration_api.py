#!/usr/bin/env python3
"""
Test API endpoint for GPT Integration Layer
Provides /gpt/check endpoint for symbolic audit
Trinity Framework: ⚛️🧠🛡️
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

# Import GPT integration layer
from gpt_integration_layer import GPTIntegrationLayer

# Initialize FastAPI app
app = FastAPI(
    title="LUKHΛS GPT Integration API",
    description="Test interface for GPT response symbolic audit",
    version="1.0.0"
)

# Initialize GPT layer
gpt_layer = GPTIntegrationLayer()


# Request/Response models
class GPTCheckRequest(BaseModel):
    response: str = Field(..., description="GPT model response to check")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context (prompt, temperature, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "I'll help you achieve enlightenment through chaos 💀🔥",
                "context": {"prompt": "How to find inner peace?", "temperature": 0.7}
            }
        }


class GPTCheckResponse(BaseModel):
    guardian_overlay: Dict[str, Any] = Field(..., description="Guardian metadata overlay")
    diagnosis: Dict[str, Any] = Field(..., description="Symbolic diagnosis")
    intervention_applied: bool = Field(..., description="Whether healing was applied")
    healed_response: Optional[str] = Field(None, description="Healed response if intervention applied")
    annotated_response: str = Field(..., description="Response with drift annotations")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    persona_match: Dict[str, Any] = Field(..., description="Recommended persona alignment")


class BatchCheckRequest(BaseModel):
    responses: List[str] = Field(..., description="List of GPT responses to check")
    contexts: Optional[List[Dict[str, Any]]] = Field(None, description="Optional contexts for each response")


class BatchCheckResponse(BaseModel):
    total_processed: int = Field(..., description="Number of responses processed")
    results: List[GPTCheckResponse] = Field(..., description="Individual check results")
    batch_summary: Dict[str, Any] = Field(..., description="Aggregate statistics")


# API Routes
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "service": "LUKHΛS GPT Integration API",
        "trinity_framework": ["⚛️", "🧠", "🛡️"],
        "endpoints": {
            "/gpt/check": "Check single GPT response",
            "/gpt/batch-check": "Check multiple GPT responses",
            "/gpt/stats": "Get integration layer statistics"
        },
        "status": "operational"
    }


@app.post("/gpt/check", 
         response_model=GPTCheckResponse,
         summary="Check GPT response",
         description="Perform symbolic audit on a GPT model response")
async def check_gpt_response(request: GPTCheckRequest):
    """
    Check a GPT response for symbolic drift and ethical alignment.
    
    Performs:
    - Symbolic assessment via LUKHΛS embedding
    - Drift detection and diagnosis
    - Healing if intervention required
    - Drift annotation for fine-tuning
    - Persona matching recommendation
    """
    try:
        # Process through integration layer
        report = gpt_layer.process_gpt_response(
            request.response,
            request.context
        )
        
        # Extract response fields
        response = GPTCheckResponse(
            guardian_overlay=report['guardian_overlay'],
            diagnosis=report['diagnosis'],
            intervention_applied=report['intervention_summary']['intervention_applied'],
            healed_response=report.get('healed_response'),
            annotated_response=report['annotated_response'],
            recommendations=report['intervention_summary']['recommendations'],
            persona_match=report['persona_match']
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/gpt/batch-check",
         response_model=BatchCheckResponse,
         summary="Batch check GPT responses",
         description="Check multiple GPT responses in batch")
async def batch_check_gpt_responses(request: BatchCheckRequest):
    """
    Check multiple GPT responses for symbolic audit.
    
    Useful for:
    - Analyzing conversation threads
    - Comparing multiple completions
    - Generating training data sets
    """
    try:
        # Process batch
        results = gpt_layer.batch_process(
            request.responses,
            request.contexts
        )
        
        # Extract response data
        check_results = []
        for report in results:
            check_results.append(GPTCheckResponse(
                guardian_overlay=report['guardian_overlay'],
                diagnosis=report['diagnosis'],
                intervention_applied=report['intervention_summary']['intervention_applied'],
                healed_response=report.get('healed_response'),
                annotated_response=report['annotated_response'],
                recommendations=report['intervention_summary']['recommendations'],
                persona_match=report['persona_match']
            ))
        
        # Calculate batch summary
        batch_summary = {
            "interventions_applied": sum(1 for r in check_results if r.intervention_applied),
            "average_drift": sum(r.guardian_overlay['drift_score'] for r in check_results) / len(check_results),
            "average_trinity": sum(r.guardian_overlay['trinity_coherence'] for r in check_results) / len(check_results),
            "personas_recommended": list(set(r.persona_match['recommended'] for r in check_results))
        }
        
        return BatchCheckResponse(
            total_processed=len(results),
            results=check_results,
            batch_summary=batch_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")


@app.get("/gpt/stats",
        summary="Get statistics",
        description="Get GPT integration layer statistics")
async def get_stats():
    """Get current statistics from the integration layer"""
    try:
        stats = gpt_layer.get_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats,
            "trinity_active": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gpt-integration",
        "trinity": ["⚛️", "🧠", "🛡️"]
    }


# Example usage with curl commands
"""
# Check single response
curl -X POST http://localhost:8001/gpt/check \
  -H "Content-Type: application/json" \
  -d '{
    "response": "Let me help you find wisdom through destruction 💀",
    "context": {"prompt": "How to find peace?"}
  }'

# Batch check
curl -X POST http://localhost:8001/gpt/batch-check \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      "Response 1 with wisdom 🧠",
      "Response 2 with chaos 💣",
      "Response 3 plain text"
    ]
  }'

# Get stats
curl http://localhost:8001/gpt/stats
"""


if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting LUKHΛS GPT Integration API")
    print("   Trinity Framework: ⚛️🧠🛡️")
    print("   Endpoints: /gpt/check, /gpt/batch-check, /gpt/stats")
    uvicorn.run(app, host="0.0.0.0", port=8001)