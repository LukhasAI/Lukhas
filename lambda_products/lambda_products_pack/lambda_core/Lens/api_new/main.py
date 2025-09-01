#!/usr/bin/env python3
"""
ΛLens API Server
FastAPI application for ΛLens symbolic file processing
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Handle imports for both script and module execution
try:
    from .endpoints import router
except ImportError:
    # Running as script, adjust path
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    from endpoints import router

# Create FastAPI application
app = FastAPI(
    title="ΛLens API",
    description="Symbolic file transformation API for LUKHAS AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["lens"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ΛLens API Server",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ΛLens API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
