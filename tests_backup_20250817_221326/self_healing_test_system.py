#!/usr/bin/env python3
"""
LUKHAS AI Consolidated Self-Healing Test System
Combines best features from all test artifacts
"""

import os
import sys
import json
import ast
import asyncio
import traceback
import subprocess
import re
import difflib
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from collections import defaultdict

# For web interface
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# For AI integration
import aiohttp
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemHealth(Enum):
    """System health states"""
    CRITICAL = "critical"
    WARNING = "warning"
    HEALTHY = "healthy"
    OPTIMAL = "optimal"


class FixConfidence(Enum):
    """Confidence levels for automated fixes"""
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    MANUAL = 0.0


@dataclass
class TestFailure:
    """Represents a test failure with comprehensive details"""
    test_name: str
    test_file: str
    module: str
    error_type: str
    error_message: str
    stack_trace: str
    line_number: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    previous_attempts: int = 0
    
    def to_dict(self):
        return {
            "test_name": self.test_name,
            "test_file": self.test_file,
            "module": self.module,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "line_number": self.line_number,
            "timestamp": self.timestamp.isoformat(),
            "previous_attempts": self.previous_attempts
        }


@dataclass
class HealingSolution:
    """Represents a healing solution with AI enhancement"""
    action: str
    description: str
    confidence: float
    auto_fixable: bool
    commands: List[str] = field(default_factory=list)
    code_changes: Dict[str, str] = field(default_factory=dict)
    ai_suggestion: Optional[str] = None
    rollback_available: bool = False
    estimated_time: float = 0.0
    
    def to_dict(self):
        return {
            "action": self.action,
            "description": self.description,
            "confidence": self.confidence,
            "auto_fixable": self.auto_fixable,
            "commands": self.commands,
            "code_changes": self.code_changes,
            "ai_suggestion": self.ai_suggestion,
            "rollback_available": self.rollback_available,
            "estimated_time": self.estimated_time
        }


class PatternLearner:
    """Learn from past fixes to improve future solutions"""
    
    def __init__(self):
        self.pattern_db_path = Path("tests/.healing_patterns.pkl")
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """Load learned patterns from disk"""
        if self.pattern_db_path.exists():
            try:
                with open(self.pattern_db_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Failed to load patterns: {e}")
        return defaultdict(list)
        
    def save_patterns(self):
        """Save learned patterns to disk"""
        try:
            with open(self.pattern_db_path, 'wb') as f:
                pickle.dump(dict(self.patterns), f)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
            
    def learn_from_fix(self, failure: TestFailure, solution: HealingSolution, success: bool):
        """Learn from a fix attempt"""
        pattern_key = f"{failure.error_type}:{failure.error_message[:50]}"
        self.patterns[pattern_key].append({
            "solution": solution.to_dict(),
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        self.save_patterns()
        
    def get_similar_fixes(self, failure: TestFailure) -> List[HealingSolution]:
        """Get similar fixes from history"""
        similar_fixes = []
        pattern_key = f"{failure.error_type}:{failure.error_message[:50]}"
        
        if pattern_key in self.patterns:
            successful_fixes = [
                p for p in self.patterns[pattern_key] 
                if p["success"]
            ]
            
            for fix in successful_fixes[-5:]:  # Get last 5 successful fixes
                solution_data = fix["solution"]
                similar_fixes.append(HealingSolution(
                    action=solution_data["action"],
                    description=f"Previously successful: {solution_data['description']}",
                    confidence=0.85,  # High confidence for previously successful fixes
                    auto_fixable=solution_data["auto_fixable"],
                    commands=solution_data.get("commands", []),
                    code_changes=solution_data.get("code_changes", {})
                ))
                
        return similar_fixes


class SelfHealingEngine:
    """Main self-healing engine with AI capabilities"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        self.pattern_learner = PatternLearner()
        self.healing_history = []
        self.current_health = SystemHealth.HEALTHY
        
        # AI endpoints (configurable)
        self.ollama_url = "http://localhost:11434/api/generate"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    async def analyze_failure(self, failure: TestFailure) -> List[HealingSolution]:
        """Analyze test failure and propose solutions"""
        solutions = []
        
        # 1. Check learned patterns first
        historical_fixes = self.pattern_learner.get_similar_fixes(failure)
        solutions.extend(historical_fixes)
        
        # 2. Apply rule-based analysis
        rule_based_solutions = await self._rule_based_analysis(failure)
        solutions.extend(rule_based_solutions)
        
        # 3. Get AI suggestions if available
        if self.ollama_url or self.openai_api_key:
            ai_solutions = await self._ai_analysis(failure)
            solutions.extend(ai_solutions)
            
        # 4. Sort by confidence
        solutions.sort(key=lambda x: x.confidence, reverse=True)
        
        return solutions[:5]  # Return top 5 solutions
        
    async def _rule_based_analysis(self, failure: TestFailure) -> List[HealingSolution]:
        """Rule-based failure analysis"""
        solutions = []
        
        # Import errors
        if "ImportError" in failure.error_type or "ModuleNotFoundError" in failure.error_type:
            module_match = re.search(r"No module named '([\w\.]+)'", failure.error_message)
            if module_match:
                missing_module = module_match.group(1)
                
                # Check if it's a local module
                local_path = self.project_root / missing_module.replace(".", "/")
                if local_path.exists():
                    solutions.append(HealingSolution(
                        action="fix_import_path",
                        description=f"Add project root to Python path",
                        confidence=FixConfidence.HIGH.value,
                        auto_fixable=True,
                        code_changes={
                            failure.test_file: f"import sys\nsys.path.insert(0, '{self.project_root}')"
                        }
                    ))
                else:
                    solutions.append(HealingSolution(
                        action="install_dependency",
                        description=f"Install missing module: {missing_module}",
                        confidence=FixConfidence.MEDIUM.value,
                        auto_fixable=True,
                        commands=[f"pip install {missing_module}"]
                    ))
                    
        # Assertion errors
        elif "AssertionError" in failure.error_type:
            solutions.append(HealingSolution(
                action="update_assertion",
                description="Review and update test assertion",
                confidence=FixConfidence.LOW.value,
                auto_fixable=False,
                ai_suggestion="Manual review required - check if implementation changed"
            ))
            
        # Attribute errors
        elif "AttributeError" in failure.error_type:
            attr_match = re.search(r"'(\w+)' object has no attribute '(\w+)'", failure.error_message)
            if attr_match:
                obj_type = attr_match.group(1)
                attr_name = attr_match.group(2)
                
                solutions.append(HealingSolution(
                    action="add_missing_attribute",
                    description=f"Add missing attribute '{attr_name}' to {obj_type}",
                    confidence=FixConfidence.MEDIUM.value,
                    auto_fixable=True,
                    code_changes={
                        "implementation": f"self.{attr_name} = None  # Initialize in __init__"
                    }
                ))
                
        # Type errors
        elif "TypeError" in failure.error_type:
            solutions.append(HealingSolution(
                action="fix_type_mismatch",
                description="Fix type mismatch in function call",
                confidence=FixConfidence.LOW.value,
                auto_fixable=False,
                ai_suggestion="Check function signature and argument types"
            ))
            
        return solutions
        
    async def _ai_analysis(self, failure: TestFailure) -> List[HealingSolution]:
        """AI-powered failure analysis"""
        solutions = []
        
        # Prepare context for AI
        context = f"""
        Test Failure Analysis:
        - Test: {failure.test_name}
        - Error Type: {failure.error_type}
        - Error Message: {failure.error_message}
        - Stack Trace: {failure.stack_trace[:500]}
        
        Please suggest a fix for this test failure.
        """
        
        # Try Ollama first (local AI)
        if self.ollama_url:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": "codellama",
                        "prompt": context,
                        "stream": False
                    }
                    async with session.post(self.ollama_url, json=payload) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            ai_suggestion = result.get("response", "")
                            
                            solutions.append(HealingSolution(
                                action="ai_suggested_fix",
                                description="AI-suggested solution",
                                confidence=FixConfidence.MEDIUM.value,
                                auto_fixable=False,
                                ai_suggestion=ai_suggestion
                            ))
            except Exception as e:
                logger.warning(f"Ollama API error: {e}")
                
        return solutions
        
    async def apply_solution(self, failure: TestFailure, solution: HealingSolution) -> bool:
        """Apply a healing solution"""
        success = False
        
        try:
            # Create backup before applying changes
            self._create_backup(failure.test_file)
            
            # Apply code changes
            for file_path, changes in solution.code_changes.items():
                if file_path == "implementation":
                    # Special case for implementation changes
                    logger.info(f"Suggested implementation change: {changes}")
                else:
                    # Apply to specific file
                    full_path = self.project_root / file_path
                    if full_path.exists():
                        with open(full_path, 'r') as f:
                            content = f.read()
                        
                        # Simple prepend for imports
                        if "import" in changes and changes not in content:
                            content = changes + "\n\n" + content
                            with open(full_path, 'w') as f:
                                f.write(content)
                            logger.info(f"Applied import fix to {file_path}")
                            
            # Execute commands
            for command in solution.commands:
                logger.info(f"Executing: {command}")
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Command failed: {result.stderr}")
                    return False
                    
            # Re-run test to verify fix
            success = await self._verify_fix(failure.test_file)
            
            # Learn from the result
            self.pattern_learner.learn_from_fix(failure, solution, success)
            
        except Exception as e:
            logger.error(f"Failed to apply solution: {e}")
            self._restore_backup(failure.test_file)
            
        return success
        
    def _create_backup(self, file_path: str):
        """Create backup of file before changes"""
        backup_dir = self.test_dir / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        original = Path(file_path)
        if original.exists():
            backup = backup_dir / f"{original.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            subprocess.run(f"cp {original} {backup}", shell=True)
            logger.info(f"Created backup: {backup}")
            
    def _restore_backup(self, file_path: str):
        """Restore file from backup"""
        backup_dir = self.test_dir / ".backups"
        original = Path(file_path)
        
        # Find latest backup
        backups = list(backup_dir.glob(f"{original.name}.*"))
        if backups:
            latest = max(backups, key=lambda p: p.stat().st_mtime)
            subprocess.run(f"cp {latest} {original}", shell=True)
            logger.info(f"Restored from backup: {latest}")
            
    async def _verify_fix(self, test_file: str) -> bool:
        """Verify if the fix worked by re-running the test"""
        cmd = f"python -m pytest {test_file} -v"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
        
    def get_system_health(self) -> SystemHealth:
        """Calculate overall system health"""
        # Count recent failures
        recent_failures = len([
            h for h in self.healing_history[-50:]
            if not h.get("success", False)
        ])
        
        if recent_failures > 30:
            return SystemHealth.CRITICAL
        elif recent_failures > 15:
            return SystemHealth.WARNING
        elif recent_failures > 5:
            return SystemHealth.HEALTHY
        else:
            return SystemHealth.OPTIMAL
            

# FastAPI Application
app = FastAPI(title="LUKHAS Self-Healing Test System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

engine = SelfHealingEngine()


@app.get("/")
async def serve_dashboard():
    """Serve the test dashboard"""
    dashboard_path = Path(__file__).parent / "self_healing_dashboard.html"
    return FileResponse(dashboard_path)


@app.get("/api/health")
async def get_health():
    """Get system health status"""
    health = engine.get_system_health()
    return {
        "status": health.value,
        "healing_history_count": len(engine.healing_history),
        "patterns_learned": len(engine.pattern_learner.patterns)
    }


@app.post("/api/analyze")
async def analyze_failure(failure_data: dict):
    """Analyze a test failure"""
    failure = TestFailure(
        test_name=failure_data["test_name"],
        test_file=failure_data["test_file"],
        module=failure_data.get("module", "unknown"),
        error_type=failure_data["error_type"],
        error_message=failure_data["error_message"],
        stack_trace=failure_data.get("stack_trace", "")
    )
    
    solutions = await engine.analyze_failure(failure)
    
    return {
        "failure": failure.to_dict(),
        "solutions": [s.to_dict() for s in solutions]
    }


@app.post("/api/heal")
async def apply_healing(data: dict):
    """Apply a healing solution"""
    failure = TestFailure(
        test_name=data["failure"]["test_name"],
        test_file=data["failure"]["test_file"],
        module=data["failure"].get("module", "unknown"),
        error_type=data["failure"]["error_type"],
        error_message=data["failure"]["error_message"],
        stack_trace=data["failure"].get("stack_trace", "")
    )
    
    solution = HealingSolution(
        action=data["solution"]["action"],
        description=data["solution"]["description"],
        confidence=data["solution"]["confidence"],
        auto_fixable=data["solution"]["auto_fixable"],
        commands=data["solution"].get("commands", []),
        code_changes=data["solution"].get("code_changes", {})
    )
    
    success = await engine.apply_solution(failure, solution)
    
    # Record in history
    engine.healing_history.append({
        "timestamp": datetime.now().isoformat(),
        "failure": failure.to_dict(),
        "solution": solution.to_dict(),
        "success": success
    })
    
    return {"success": success}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send periodic health updates
            health_data = {
                "type": "health_update",
                "health": engine.get_system_health().value,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(health_data)
            await asyncio.sleep(5)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    print("🚀 Starting LUKHAS Self-Healing Test System...")
    print("🔧 Dashboard: http://localhost:8001")
    print("📡 API Docs: http://localhost:8001/docs")
    print("🤖 AI Support: Ollama (local) and OpenAI (if configured)")
    uvicorn.run(app, host="0.0.0.0", port=8001)