#!/usr/bin/env python3
"""
Test script for ΛLens API functionality
"""

import os
import sys

# Add the current directory and api_new to the path
current_dir = os.path.dirname(__file__)
api_dir = os.path.join(current_dir, "api_new")
sys.path.insert(0, current_dir)
sys.path.insert(0, api_dir)

try:
    from api_new.endpoints import router
    from api_new.main import app
    from api_new.schemas import JobRequest, JobResponse, PhotonDocument

    print("✅ API imports successful!")
    print(f"📡 FastAPI app: {app.title}")
    print(f"🔗 Router endpoints: {len(router.routes)}")
    print("📋 Schemas: JobRequest, JobResponse, PhotonDocument")

    # Test schema validation
    test_request = JobRequest()
    print(f"🔍 Default request: {test_request.dict()}")

    print("\n🎉 ΛLens API is ready to use!")
    print("\nTo start the server:")
    print("cd api_new && python main.py")
    print("\nAPI will be available at: http://localhost:8000")
    print("Documentation at: http://localhost:8000/docs")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to install required packages:")
    print("pip install fastapi uvicorn pydantic")
except Exception as e:
    print(f"❌ Error: {e}")
