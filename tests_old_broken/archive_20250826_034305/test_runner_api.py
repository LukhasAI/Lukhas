#!/usr/bin/env python3
"""
LUKHAS Test Runner API
Interactive test execution with self-healing capabilities
"""

import asyncio
import json
import subprocess
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import ast

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pytest
from pydantic import BaseModel


@dataclass
class TestResult:
    """Test execution result"""
    name: str
    module: str
    status: str  # passed, failed, skipped, error
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    
@dataclass
class TestSolution:
    """Proposed solution for test failure"""
    test_name: str
    error_type: str
    proposed_fix: str
    code_changes: Dict[str, str]
    confidence: float  # 0-1 confidence score
    

class TestRunner:
    """Core test runner with self-healing capabilities"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        self.results_cache = {}
        self.solutions_cache = {}
        
    async def run_test(self, test_path: str) -> TestResult:
        """Run a single test"""
        start_time = datetime.now()
        
        # Run pytest with JSON output
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "--json-report",
            "--json-report-file=/tmp/test_result.json",
            "-v"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse results
            if Path("/tmp/test_result.json").exists():
                with open("/tmp/test_result.json") as f:
                    json_result = json.load(f)
                    
                # Extract test result
                test_name = Path(test_path).stem
                status = "passed" if result.returncode == 0 else "failed"
                error_msg = None
                traceback = None
                
                if status == "failed":
                    error_msg = result.stdout.split("\n")[-2] if result.stdout else None
                    traceback = result.stderr
                    
                return TestResult(
                    name=test_name,
                    module=self._get_module(test_path),
                    status=status,
                    duration=duration,
                    error_message=error_msg,
                    traceback=traceback
                )
                
        except subprocess.TimeoutExpired:
            return TestResult(
                name=Path(test_path).stem,
                module=self._get_module(test_path),
                status="error",
                duration=30.0,
                error_message="Test timeout",
                traceback=None
            )
            
    def _get_module(self, test_path: str) -> str:
        """Extract module name from test path"""
        parts = Path(test_path).parts
        if "tests" in parts:
            idx = parts.index("tests")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "unknown"
        
    async def analyze_failure(self, result: TestResult) -> Optional[TestSolution]:
        """Analyze test failure and propose solution"""
        if result.status != "failed" or not result.error_message:
            return None
            
        # Pattern matching for common errors
        solutions = {
            r"ImportError|ModuleNotFoundError": self._fix_import_error,
            r"AttributeError": self._fix_attribute_error,
            r"AssertionError": self._fix_assertion_error,
            r"TypeError": self._fix_type_error,
            r"KeyError": self._fix_key_error,
            r"FileNotFoundError": self._fix_file_error,
        }
        
        for pattern, fix_func in solutions.items():
            if re.search(pattern, result.error_message):
                return await fix_func(result)
                
        return None
        
    async def _fix_import_error(self, result: TestResult) -> TestSolution:
        """Fix import errors"""
        # Extract missing module from error
        match = re.search(r"No module named '([\w\.]+)'", result.error_message)
        if match:
            missing_module = match.group(1)
            
            # Check if module exists in project
            module_path = self.project_root / missing_module.replace(".", "/")
            
            if module_path.exists():
                # Path issue
                return TestSolution(
                    test_name=result.name,
                    error_type="ImportError",
                    proposed_fix=f"Add project root to Python path",
                    code_changes={
                        "test_file": f"import sys\nsys.path.insert(0, '{self.project_root}')"
                    },
                    confidence=0.9
                )
            else:
                # Missing dependency
                return TestSolution(
                    test_name=result.name,
                    error_type="ImportError",
                    proposed_fix=f"Install missing module: {missing_module}",
                    code_changes={
                        "requirements.txt": f"{missing_module}\n"
                    },
                    confidence=0.7
                )
                
        return None
        
    async def _fix_assertion_error(self, result: TestResult) -> TestSolution:
        """Fix assertion errors"""
        # Analyze assertion failure
        if "assert" in result.error_message:
            return TestSolution(
                test_name=result.name,
                error_type="AssertionError",
                proposed_fix="Update test assertion or fix implementation",
                code_changes={
                    "test_file": "# Review assertion logic and expected values"
                },
                confidence=0.5
            )
        return None
        
    async def _fix_attribute_error(self, result: TestResult) -> TestSolution:
        """Fix attribute errors"""
        match = re.search(r"'(\w+)' object has no attribute '(\w+)'", result.error_message)
        if match:
            obj_type = match.group(1)
            attr_name = match.group(2)
            
            return TestSolution(
                test_name=result.name,
                error_type="AttributeError",
                proposed_fix=f"Add missing attribute '{attr_name}' to {obj_type}",
                code_changes={
                    "implementation": f"self.{attr_name} = None  # Initialize in __init__"
                },
                confidence=0.8
            )
        return None
        
    async def _fix_type_error(self, result: TestResult) -> TestSolution:
        """Fix type errors"""
        return TestSolution(
            test_name=result.name,
            error_type="TypeError",
            proposed_fix="Fix type mismatch in function call",
            code_changes={
                "test_file": "# Check function signature and argument types"
            },
            confidence=0.6
        )
        
    async def _fix_key_error(self, result: TestResult) -> TestSolution:
        """Fix key errors"""
        match = re.search(r"KeyError: '(\w+)'", result.error_message)
        if match:
            missing_key = match.group(1)
            
            return TestSolution(
                test_name=result.name,
                error_type="KeyError",
                proposed_fix=f"Add missing key '{missing_key}' to dictionary",
                code_changes={
                    "implementation": f"data['{missing_key}'] = default_value"
                },
                confidence=0.7
            )
        return None
        
    async def _fix_file_error(self, result: TestResult) -> TestSolution:
        """Fix file not found errors"""
        match = re.search(r"No such file or directory: '(.*)'", result.error_message)
        if match:
            missing_file = match.group(1)
            
            return TestSolution(
                test_name=result.name,
                error_type="FileNotFoundError",
                proposed_fix=f"Create missing file: {missing_file}",
                code_changes={
                    "filesystem": f"touch {missing_file}"
                },
                confidence=0.9
            )
        return None
        
    async def apply_solution(self, solution: TestSolution) -> bool:
        """Apply proposed solution"""
        try:
            for file_path, changes in solution.code_changes.items():
                if file_path == "filesystem":
                    # Execute filesystem commands
                    subprocess.run(changes, shell=True)
                elif file_path == "requirements.txt":
                    # Update requirements
                    req_path = self.project_root / "requirements.txt"
                    with open(req_path, "a") as f:
                        f.write(changes)
                else:
                    # Code changes would need more sophisticated handling
                    # For now, just log them
                    print(f"Proposed change for {file_path}:\n{changes}")
                    
            return True
        except Exception as e:
            print(f"Failed to apply solution: {e}")
            return False
            

# FastAPI Application
app = FastAPI(title="LUKHAS Test Runner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

runner = TestRunner()


class TestRequest(BaseModel):
    test_path: str
    module: Optional[str] = None
    

class SolutionAction(BaseModel):
    solution_id: str
    action: str  # apply, decline, defer
    

@app.get("/")
async def root():
    """Serve the test dashboard"""
    dashboard_path = Path(__file__).parent / "interactive_test_dashboard.html"
    return FileResponse(dashboard_path)
    

@app.get("/api/tests")
async def list_tests():
    """List all available tests"""
    tests = []
    test_dir = Path(__file__).parent
    
    for test_file in test_dir.rglob("test_*.py"):
        if "__pycache__" not in str(test_file):
            tests.append({
                "path": str(test_file.relative_to(test_dir)),
                "name": test_file.stem,
                "module": runner._get_module(str(test_file))
            })
            
    return {"tests": tests, "total": len(tests)}
    

@app.post("/api/run-test")
async def run_test(request: TestRequest):
    """Run a single test"""
    result = await runner.run_test(request.test_path)
    
    # If test failed, analyze and propose solution
    solution = None
    if result.status == "failed":
        solution = await runner.analyze_failure(result)
        
    return {
        "result": asdict(result),
        "solution": asdict(solution) if solution else None
    }
    

@app.post("/api/run-all")
async def run_all_tests():
    """Run all tests"""
    test_dir = Path(__file__).parent
    results = []
    
    for test_file in test_dir.rglob("test_*.py"):
        if "__pycache__" not in str(test_file) and "STUB" not in str(test_file):
            result = await runner.run_test(str(test_file))
            results.append(asdict(result))
            
    # Calculate statistics
    stats = {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "duration": sum(r["duration"] for r in results)
    }
    
    return {"results": results, "stats": stats}
    

@app.post("/api/apply-solution")
async def apply_solution(action: SolutionAction):
    """Apply, decline, or defer a solution"""
    # This would interact with the solution cache
    return {"status": "success", "action": action.action}
    

@app.get("/api/report")
async def generate_report():
    """Generate comprehensive test report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0
        },
        "modules": {},
        "recommendations": []
    }
    
    # Would generate detailed report here
    return report
    

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time test updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send test progress updates
            await websocket.send_json({
                "type": "progress",
                "data": {"current": 50, "total": 100}
            })
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
        

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting LUKHAS Test Runner API...")
    print("📊 Dashboard: http://localhost:8000")
    print("📡 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)