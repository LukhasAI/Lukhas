"""
LUKHAS Enhanced API System
Unified API with proper authentication, service integration, and error handling
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import asyncio
import structlog
from contextlib import asynccontextmanager

# Import enhanced security
from core.security.security_integration import get_security_integration
from core.security.enhanced_auth import get_auth_system

# Import core LUKHAS modules (with fallback for missing modules)
try:
    from core.symbolic.symbolic_reasoning import SymbolicEngine
except ImportError:
    class SymbolicEngine:
        def __init__(self):
            pass
        def reason(self, text):
            return {"reasoning": "Mock symbolic reasoning"}

try:
    from orchestration.brain.primary_hub import CoordinationManager
except ImportError:
    class CoordinationManager:
        def __init__(self):
            pass
        async def coordinate(self, request):
            return {"status": "coordinated"}

try:
    from consciousness.unified.auto_consciousness import UnifiedConsciousness
except ImportError:
    class UnifiedConsciousness:
        def __init__(self):
            pass
        async def process(self, data):
            return {"consciousness": "processing"}

try:
    from memory.systems.memory_manager import MemoryManager
except ImportError:
    class MemoryManager:
        def __init__(self):
            pass
        async def store(self, data):
            return {"stored": True}

try:
    from governance.guardian_system import GuardianSystem
except ImportError:
    class GuardianSystem:
        def __init__(self):
            pass
        async def validate(self, action):
            return {"approved": True}

try:
    from emotion.affect.emotion_engine import EmotionEngine
except ImportError:
    class EmotionEngine:
        def __init__(self):
            pass
        async def process_emotion(self, data):
            return {"emotion": "neutral"}

try:
    from creativity.dream.dream_engine import DreamEngine
except ImportError:
    class DreamEngine:
        def __init__(self):
            pass
        async def dream(self, prompt):
            return {"dream": "creative output"}

log = structlog.get_logger(__name__)


# API Models
class LUKHASRequest(BaseModel):
    """Base request model for LUKHAS operations"""
    operation: str = Field(..., description="Operation to perform")
    data: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default=None)
    options: Optional[Dict[str, Any]] = Field(default=None)


class LUKHASResponse(BaseModel):
    """Base response model for LUKHAS operations"""
    request_id: str
    timestamp: datetime
    operation: str
    status: str = Field(..., pattern="^(success|error|partial)$")
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float


class ConsciousnessRequest(BaseModel):
    """Consciousness operation request"""
    query: str = Field(..., min_length=1, max_length=5000)
    awareness_level: float = Field(default=0.7, ge=0.0, le=1.0)
    include_emotional_context: bool = True


class MemoryRequest(BaseModel):
    """Memory operation request"""
    action: str = Field(..., pattern="^(store|retrieve|search|update)$")
    content: Optional[Dict[str, Any]] = None
    query: Optional[str] = None
    memory_type: str = Field(default="general")
    

class GovernanceRequest(BaseModel):
    """Governance/ethics check request"""
    action_proposal: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)
    urgency: str = Field(default="normal", pattern="^(low|normal|high|critical)$")


class DreamRequest(BaseModel):
    """Creative dream generation request"""
    prompt: str = Field(..., min_length=1, max_length=1000)
    creativity_level: float = Field(default=0.8, ge=0.0, le=1.0)
    dream_type: str = Field(default="creative", pattern="^(creative|analytical|symbolic)$")


class EnhancedAPISystem:
    """
    Enhanced API system with full LUKHAS integration
    Addresses the 33.3% functionality issue
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="LUKHAS AGI Enhanced API",
            description="Production-ready API for LUKHAS AI System",
            version="2.0.0",
            docs_url="/api/v2/docs",
            redoc_url="/api/v2/redoc",
            openapi_url="/api/v2/openapi.json",
            lifespan=self.lifespan
        )
        
        # Core services (will be initialized in lifespan)
        self.security = None
        self.auth = None
        self.symbolic_engine = None
        self.coordination = None
        self.consciousness = None
        self.memory = None
        self.guardian = None
        self.emotion = None
        self.dream = None
        
        # Request tracking
        self.active_requests: Dict[str, Any] = {}
        self.request_counter = 0
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage API lifecycle"""
        # Startup
        log.info("Starting LUKHAS Enhanced API System")
        
        try:
            # Initialize security
            self.security = await get_security_integration()
            self.auth = get_auth_system()
            
            # Initialize core services
            await self._initialize_services()
            
            log.info("LUKHAS API System ready")
            
            yield
            
        finally:
            # Shutdown
            log.info("Shutting down LUKHAS API System")
            await self._shutdown_services()
            
    async def _initialize_services(self):
        """Initialize all LUKHAS services"""
        try:
            # Initialize in dependency order
            self.symbolic_engine = SymbolicEngine()
            await self.symbolic_engine.initialize()
            
            self.guardian = GuardianSystem()
            await self.guardian.initialize()
            
            self.memory = MemoryManager()
            await self.memory.initialize()
            
            self.consciousness = UnifiedConsciousness()
            await self.consciousness.initialize()
            
            self.emotion = EmotionEngine()
            await self.emotion.initialize()
            
            self.dream = DreamEngine()
            await self.dream.initialize()
            
            self.coordination = CoordinationManager()
            await self.coordination.initialize()
            
            log.info("All LUKHAS services initialized successfully")
            
        except Exception as e:
            log.error("Failed to initialize services", error=str(e))
            raise
            
    async def _shutdown_services(self):
        """Gracefully shutdown services"""
        services = [
            self.coordination,
            self.dream,
            self.emotion,
            self.consciousness,
            self.memory,
            self.guardian,
            self.symbolic_engine
        ]
        
        for service in services:
            if service and hasattr(service, 'shutdown'):
                try:
                    await service.shutdown()
                except Exception as e:
                    log.error(f"Error shutting down {service.__class__.__name__}", error=str(e))
                    
    def _setup_middleware(self):
        """Setup API middleware"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request tracking
        @self.app.middleware("http")
        async def track_requests(request: Request, call_next):
            request_id = f"req_{self.request_counter}_{datetime.now(timezone.utc).timestamp()}"
            self.request_counter += 1
            
            # Store request context
            request.state.request_id = request_id
            request.state.start_time = datetime.now(timezone.utc)
            
            # Track active request
            self.active_requests[request_id] = {
                'start_time': request.state.start_time,
                'path': request.url.path,
                'method': request.method
            }
            
            try:
                response = await call_next(request)
                return response
            finally:
                # Clean up
                self.active_requests.pop(request_id, None)
                
        # Error handling
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "message": exc.detail,
                        "status_code": exc.status_code,
                        "request_id": getattr(request.state, 'request_id', 'unknown')
                    }
                }
            )
            
    def _setup_routes(self):
        """Setup API routes"""
        # Health check
        @self.app.get("/api/v2/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "version": "2.0.0",
                "services": {
                    "symbolic_engine": self.symbolic_engine is not None,
                    "consciousness": self.consciousness is not None,
                    "memory": self.memory is not None,
                    "guardian": self.guardian is not None,
                    "emotion": self.emotion is not None,
                    "dream": self.dream is not None,
                    "coordination": self.coordination is not None
                },
                "active_requests": len(self.active_requests)
            }
            
        # Authentication endpoints
        @self.app.post("/api/v2/auth/login")
        async def login(credentials: Dict[str, Any]):
            """Login and get JWT token"""
            result = await self.security.create_secure_session(
                credentials.get('user_id'),
                credentials
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
                
            return result
            
        @self.app.post("/api/v2/auth/mfa/verify")
        async def verify_mfa(session_id: str, mfa_data: Dict[str, str]):
            """Verify MFA code"""
            result = await self.security.verify_mfa(
                session_id,
                mfa_data.get('method'),
                mfa_data.get('code')
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )
                
            return result
            
        # Core LUKHAS endpoints
        @self.app.post("/api/v2/consciousness/query", response_model=LUKHASResponse)
        async def consciousness_query(
            request: ConsciousnessRequest,
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Query consciousness system"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, 'consciousness.query')
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            start_time = datetime.now(timezone.utc)
            request_id = f"consciousness_{start_time.timestamp()}"
            
            try:
                # Process through consciousness
                result = await self.consciousness.process_query(
                    request.query,
                    awareness_level=request.awareness_level,
                    include_emotion=request.include_emotional_context
                )
                
                # Check with Guardian
                ethics_check = await self.guardian.validate_response(result)
                if not ethics_check['approved']:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Guardian rejected: {ethics_check['reason']}"
                    )
                
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation="consciousness.query",
                    status="success",
                    result=result,
                    processing_time_ms=processing_time
                )
                
            except Exception as e:
                log.error("Consciousness query failed", error=str(e))
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation="consciousness.query",
                    status="error",
                    error={"message": str(e), "type": type(e).__name__},
                    processing_time_ms=0
                )
                
        @self.app.post("/api/v2/memory/{action}", response_model=LUKHASResponse)
        async def memory_operation(
            action: str,
            request: MemoryRequest,
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Memory operations (store, retrieve, search, update)"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, f'memory.{action}')
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            if action not in ['store', 'retrieve', 'search', 'update']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid action: {action}"
                )
                
            start_time = datetime.now(timezone.utc)
            request_id = f"memory_{action}_{start_time.timestamp()}"
            
            try:
                # Execute memory operation
                if action == 'store':
                    result = await self.memory.store(
                        request.content,
                        memory_type=request.memory_type
                    )
                elif action == 'retrieve':
                    result = await self.memory.retrieve(
                        request.query,
                        memory_type=request.memory_type
                    )
                elif action == 'search':
                    result = await self.memory.search(
                        request.query,
                        memory_type=request.memory_type
                    )
                elif action == 'update':
                    result = await self.memory.update(
                        request.query,
                        request.content,
                        memory_type=request.memory_type
                    )
                    
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation=f"memory.{action}",
                    status="success",
                    result=result,
                    processing_time_ms=processing_time
                )
                
            except Exception as e:
                log.error(f"Memory {action} failed", error=str(e))
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation=f"memory.{action}",
                    status="error",
                    error={"message": str(e), "type": type(e).__name__},
                    processing_time_ms=0
                )
                
        @self.app.post("/api/v2/governance/check", response_model=LUKHASResponse)
        async def governance_check(
            request: GovernanceRequest,
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Check action proposal with Guardian system"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, 'governance.check')
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            start_time = datetime.now(timezone.utc)
            request_id = f"governance_{start_time.timestamp()}"
            
            try:
                # Guardian evaluation
                result = await self.guardian.evaluate_action(
                    request.action_proposal,
                    context=request.context,
                    urgency=request.urgency
                )
                
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation="governance.check",
                    status="success",
                    result=result,
                    processing_time_ms=processing_time
                )
                
            except Exception as e:
                log.error("Governance check failed", error=str(e))
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation="governance.check",
                    status="error",
                    error={"message": str(e), "type": type(e).__name__},
                    processing_time_ms=0
                )
                
        @self.app.post("/api/v2/dream/generate", response_model=LUKHASResponse)
        async def dream_generate(
            request: DreamRequest,
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Generate creative content through dream engine"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, 'dream.generate')
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            start_time = datetime.now(timezone.utc)
            request_id = f"dream_{start_time.timestamp()}"
            
            try:
                # Dream generation
                result = await self.dream.generate(
                    request.prompt,
                    creativity_level=request.creativity_level,
                    dream_type=request.dream_type
                )
                
                # Guardian check on generated content
                ethics_check = await self.guardian.validate_response(result)
                if not ethics_check['approved']:
                    # Regenerate with constraints
                    result = await self.dream.generate(
                        request.prompt,
                        creativity_level=request.creativity_level * 0.7,
                        dream_type=request.dream_type,
                        constraints=ethics_check.get('constraints', [])
                    )
                
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation="dream.generate",
                    status="success",
                    result=result,
                    processing_time_ms=processing_time
                )
                
            except Exception as e:
                log.error("Dream generation failed", error=str(e))
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation="dream.generate",
                    status="error",
                    error={"message": str(e), "type": type(e).__name__},
                    processing_time_ms=0
                )
                
        @self.app.post("/api/v2/process", response_model=LUKHASResponse)
        async def process_request(
            request: LUKHASRequest,
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Generic processing endpoint for complex operations"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, request.operation)
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            start_time = datetime.now(timezone.utc)
            request_id = f"process_{start_time.timestamp()}"
            
            try:
                # Route to appropriate handler
                if request.operation.startswith('symbolic.'):
                    result = await self._handle_symbolic_operation(request)
                elif request.operation.startswith('emotion.'):
                    result = await self._handle_emotion_operation(request)
                elif request.operation.startswith('coordination.'):
                    result = await self._handle_coordination_operation(request)
                else:
                    raise ValueError(f"Unknown operation: {request.operation}")
                    
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation=request.operation,
                    status="success",
                    result=result,
                    processing_time_ms=processing_time
                )
                
            except Exception as e:
                log.error(f"Process request failed", operation=request.operation, error=str(e))
                return LUKHASResponse(
                    request_id=request_id,
                    timestamp=datetime.now(timezone.utc),
                    operation=request.operation,
                    status="error",
                    error={"message": str(e), "type": type(e).__name__},
                    processing_time_ms=0
                )
                
        # System information endpoints
        @self.app.get("/api/v2/capabilities")
        async def get_capabilities(
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Get system capabilities"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, 'system.capabilities')
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            return {
                "consciousness": self.consciousness.get_capabilities() if self.consciousness else {},
                "memory": self.memory.get_capabilities() if self.memory else {},
                "guardian": self.guardian.get_capabilities() if self.guardian else {},
                "emotion": self.emotion.get_capabilities() if self.emotion else {},
                "dream": self.dream.get_capabilities() if self.dream else {},
                "symbolic": self.symbolic_engine.get_capabilities() if self.symbolic_engine else {},
            }
            
        @self.app.get("/api/v2/metrics")
        async def get_metrics(
            auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        ):
            """Get system metrics"""
            # Validate auth
            is_valid, error = await self._validate_auth(auth.credentials, 'system.metrics')
            if not is_valid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
                
            return {
                "timestamp": datetime.now(timezone.utc),
                "active_requests": len(self.active_requests),
                "total_requests": self.request_counter,
                "services": {
                    "consciousness": await self._get_service_metrics(self.consciousness),
                    "memory": await self._get_service_metrics(self.memory),
                    "guardian": await self._get_service_metrics(self.guardian),
                    "emotion": await self._get_service_metrics(self.emotion),
                    "dream": await self._get_service_metrics(self.dream),
                }
            }
            
    async def _validate_auth(self, token: str, operation: str) -> tuple[bool, Optional[str]]:
        """Validate authentication for operation"""
        request_data = {
            'authorization': f'Bearer {token}',
            'operation': operation,
            'data': {}
        }
        
        return await self.security.validate_request(request_data)
        
    async def _handle_symbolic_operation(self, request: LUKHASRequest) -> Dict[str, Any]:
        """Handle symbolic engine operations"""
        op = request.operation.replace('symbolic.', '')
        
        if op == 'encode':
            return await self.symbolic_engine.encode(request.data.get('text', ''))
        elif op == 'decode':
            return await self.symbolic_engine.decode(request.data.get('glyphs', []))
        elif op == 'analyze':
            return await self.symbolic_engine.analyze(request.data.get('content', ''))
        else:
            raise ValueError(f"Unknown symbolic operation: {op}")
            
    async def _handle_emotion_operation(self, request: LUKHASRequest) -> Dict[str, Any]:
        """Handle emotion engine operations"""
        op = request.operation.replace('emotion.', '')
        
        if op == 'analyze':
            return await self.emotion.analyze_emotion(request.data.get('text', ''))
        elif op == 'generate':
            return await self.emotion.generate_response(
                request.data.get('emotion', 'neutral'),
                request.data.get('intensity', 0.5)
            )
        else:
            raise ValueError(f"Unknown emotion operation: {op}")
            
    async def _handle_coordination_operation(self, request: LUKHASRequest) -> Dict[str, Any]:
        """Handle coordination operations"""
        op = request.operation.replace('coordination.', '')
        
        if op == 'orchestrate':
            return await self.coordination.orchestrate_task(
                request.data.get('task', {}),
                request.context
            )
        else:
            raise ValueError(f"Unknown coordination operation: {op}")
            
    async def _get_service_metrics(self, service: Any) -> Dict[str, Any]:
        """Get metrics for a service"""
        if service and hasattr(service, 'get_metrics'):
            return await service.get_metrics()
        return {"status": "unavailable"}


# Create application instance
def create_app() -> FastAPI:
    """Create and configure the enhanced API application"""
    api_system = EnhancedAPISystem()
    return api_system.app


# For direct running
if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )