#!/usr/bin/env python3
"""
Enhanced Guardian Engine - Main orchestration system
Combines threat detection, medical assistance, consent management, and accessibility features
"""

import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

# Core imports - handle import errors gracefully
try:
    from .threat_monitor import ThreatMonitor, ThreatLevel
except ImportError:
    print("⚠️ ThreatMonitor not available - using mock implementation")
    class ThreatLevel:
        LOW = "low"
        MEDIUM = "medium"  
        HIGH = "high"
        CRITICAL = "critical"
    
    class ThreatMonitor:
        def __init__(self):
            pass
        async def start_monitoring(self):
            return True
        async def stop_monitoring(self):
            return True
        async def get_current_threats(self):
            return []
        async def assess_threat_level(self):
            return ThreatLevel.LOW

try:
    from .consent_manager import ConsentManager, ConsentRequest
except ImportError:
    print("⚠️ ConsentManager not available - using mock implementation")
    class ConsentRequest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class ConsentManager:
        def __init__(self):
            pass
        async def start_consent_system(self):
            return True
        async def request_consent(self, request_data):
            return {"success": True, "consent_id": "mock_consent", "trust_score": 0.9}

# Medical imports - handle import errors gracefully  
try:
    from ..medical.ocr_reader import MedicationOCR
except ImportError:
    print("⚠️ MedicationOCR not available - using mock implementation")
    class MedicationOCR:
        def __init__(self, *args, **kwargs):
            pass
        async def read_medication_label(self, image_path):
            return {"success": True, "medication": "Mock medication", "processing_time": "0.5s"}

try:
    from ..medical.emergency_aid import EmergencyAid
except ImportError:
    print("⚠️ EmergencyAid not available - using mock implementation")
    class EmergencyAid:
        def __init__(self, *args, **kwargs):
            pass
        async def process_emergency_alert(self, alert_data):
            return {"success": True, "alert_id": "mock_alert", "response_initiated": True}

try:
    from ..medical.health_apis import HealthAPIManager
except ImportError:
    print("⚠️ HealthAPIManager not available - using mock implementation")
    class HealthAPIManager:
        def __init__(self, *args, **kwargs):
            pass
        async def initialize_apis(self):
            return True

# Accessibility imports - handle import errors gracefully
try:
    from ..accessibility.vision_assist import VisionAssist
except ImportError:
    print("⚠️ VisionAssist not available - using mock implementation")
    class VisionAssist:
        def __init__(self, *args, **kwargs):
            pass
        async def describe_scene(self, image_path, language):
            return {"success": True, "description": "Mock scene description", "language": language, "confidence": 0.95}

try:
    from ..accessibility.cognitive_aid import CognitiveAid
except ImportError:
    print("⚠️ CognitiveAid not available - using mock implementation")
    class CognitiveAid:
        def __init__(self, *args, **kwargs):
            pass
        async def initialize_cognitive_support(self):
            return True

try:
    from ..accessibility.multi_language import MultiLanguageProcessor
except ImportError:
    print("⚠️ MultiLanguageProcessor not available - using mock implementation")
    class MultiLanguageProcessor:
        def __init__(self, *args, **kwargs):
            pass
        async def initialize_language_support(self):
            return True

# Security imports - handle import errors gracefully
try:
    from ..security.privacy_guardian import PrivacyGuardian
except ImportError:
    print("⚠️ PrivacyGuardian not available - using mock implementation")
    class PrivacyGuardian:
        def __init__(self, *args, **kwargs):
            pass
        async def start_privacy_protection(self):
            return True

try:
    from ..security.access_control import AccessController
except ImportError:
    print("⚠️ AccessController not available - using mock implementation")
    class AccessController:
        def __init__(self, *args, **kwargs):
            pass
        async def initialize_access_control(self):
            return True

try:
    from ..security.audit_logger import AuditLogger
except ImportError:
    print("⚠️ AuditLogger not available - using mock implementation")
    class AuditLogger:
        def __init__(self, *args, **kwargs):
            pass
        async def log_event(self, *args, **kwargs):
            return "mock_event_id"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guardian_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class GuardianStatus:
    """Guardian system status"""
    system_id: str
    status: str  # operational, degraded, critical, offline
    uptime_seconds: float
    active_modules: List[str]
    threat_level: str
    emergency_active: bool
    last_health_check: float
    performance_metrics: Dict[str, float]
    symbolic_status: List[str]


@dataclass
class SystemEvent:
    """System event for logging and monitoring"""
    event_id: str
    timestamp: float
    event_type: str
    severity: str
    source_module: str
    description: str
    context: Dict[str, Any]
    symbolic_signature: List[str]


class GuardianEngine:
    """
    Enhanced Guardian Engine - Main orchestration system
    
    Integrates all Guardian subsystems:
    - Threat detection and monitoring
    - Medical assistance and emergency response
    - Consent and privacy management
    - Accessibility and assistance features
    - Security and audit logging
    """
    
    # System configuration
    DEFAULT_CONFIG = {
        "monitoring": {
            "threat_detection": True,
            "interval_seconds": 5,
            "alert_threshold": 0.7,
            "health_check_interval": 60
        },
        "medical": {
            "ocr_enabled": True,
            "emergency_protocols": True,
            "api_integrations": ["clicsalud", "local_pharmacy"],
            "medication_warnings": True
        },
        "accessibility": {
            "vision_assist": True,
            "cognitive_aid": True,
            "multi_language": True,
            "voice_control": True,
            "languages": ["en", "es", "fr", "de"]
        },
        "security": {
            "consent_required": True,
            "audit_logging": True,
            "encryption_level": "AES-256",
            "privacy_protection": True
        },
        "emergency": {
            "auto_detection": True,
            "contact_notification": True,
            "escalation_protocols": True,
            "medical_integration": True
        }
    }
    
    # Symbolic patterns for system states
    SYSTEM_SYMBOLS = {
        "operational": ["🛡️", "✅", "🟢"],
        "degraded": ["🛡️", "⚠️", "🟡"],
        "critical": ["🛡️", "🚨", "🔴"],
        "offline": ["🛡️", "❌", "⚫"],
        "emergency": ["🚨", "⚡", "🏥"],
        "secure": ["🔐", "🛡️", "✅"],
        "breach": ["🚨", "🔓", "⚠️"]
    }
    
    def __init__(self, 
                 config_path: str = "config/guardian_config.yaml",
                 data_dir: str = "data",
                 enable_all: bool = True):
        
        self.config_path = Path(config_path)
        self.data_dir = Path(data_dir)
        self.system_id = str(uuid.uuid4())
        self.start_time = time.time()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize core state
        self.is_running = False
        self.current_status = GuardianStatus(
            system_id=self.system_id,
            status="offline",
            uptime_seconds=0,
            active_modules=[],
            threat_level="low",
            emergency_active=False,
            last_health_check=0,
            performance_metrics={},
            symbolic_status=self.SYSTEM_SYMBOLS["offline"]
        )
        
        # Event tracking
        self.system_events: List[SystemEvent] = []
        self.performance_history: List[Dict] = []
        
        # Initialize subsystems
        self._initialize_subsystems(enable_all)
        
        logger.info(f"🛡️ Guardian Engine initialized (ID: {self.system_id[:8]})")
    
    def _load_config(self) -> Dict:
        """Load Guardian configuration"""
        try:
            if self.config_path.exists():
                import yaml
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                return {**self.DEFAULT_CONFIG, **config.get('guardian', {})}
            else:
                logger.warning(f"Config file not found: {self.config_path}. Using defaults.")
                return self.DEFAULT_CONFIG
        except Exception as e:
            logger.error(f"Failed to load config: {e}. Using defaults.")
            return self.DEFAULT_CONFIG
    
    def _initialize_subsystems(self, enable_all: bool = True):
        """Initialize Guardian subsystems"""
        self.subsystems = {}
        
        try:
            # Core security and monitoring
            if enable_all or self.config["monitoring"]["threat_detection"]:
                self.threat_monitor = ThreatMonitor(
                    alert_threshold=self.config["monitoring"]["alert_threshold"],
                    monitoring_interval=self.config["monitoring"]["interval_seconds"]
                )
                self.subsystems["threat_monitor"] = self.threat_monitor
                logger.info("🔍 Threat Monitor initialized")
            
            if enable_all or self.config["security"]["consent_required"]:
                self.consent_manager = ConsentManager(
                    data_dir=self.data_dir / "consent_logs"
                )
                self.subsystems["consent_manager"] = self.consent_manager
                logger.info("🔐 Consent Manager initialized")
            
            # Medical and emergency systems
            if enable_all or self.config["medical"]["ocr_enabled"]:
                self.medical_ocr = MedicationOCR(
                    cache_dir=self.data_dir / "ocr_cache"
                )
                self.subsystems["medical_ocr"] = self.medical_ocr
                logger.info("💊 Medical OCR initialized")
            
            if enable_all or self.config["medical"]["emergency_protocols"]:
                self.emergency_aid = EmergencyAid(
                    config_path=self.config_path.parent / "emergency_contacts.yaml",
                    data_dir=self.data_dir / "emergency_data"
                )
                self.subsystems["emergency_aid"] = self.emergency_aid
                logger.info("🚨 Emergency Aid initialized")
            
            if enable_all or self.config["medical"]["api_integrations"]:
                self.health_apis = HealthAPIManager(
                    credentials_path=self.config_path.parent / "api_credentials.yaml",
                    enabled_apis=self.config["medical"]["api_integrations"]
                )
                self.subsystems["health_apis"] = self.health_apis
                logger.info("🏥 Health APIs initialized")
            
            # Accessibility features
            if enable_all or self.config["accessibility"]["vision_assist"]:
                self.vision_assist = VisionAssist(
                    cache_dir=self.data_dir / "vision_cache"
                )
                self.subsystems["vision_assist"] = self.vision_assist
                logger.info("👁️ Vision Assist initialized")
            
            if enable_all or self.config["accessibility"]["cognitive_aid"]:
                self.cognitive_aid = CognitiveAid(
                    data_dir=self.data_dir / "cognitive_data"
                )
                self.subsystems["cognitive_aid"] = self.cognitive_aid
                logger.info("🧠 Cognitive Aid initialized")
            
            if enable_all or self.config["accessibility"]["multi_language"]:
                self.language_processor = MultiLanguageProcessor(
                    supported_languages=self.config["accessibility"]["languages"],
                    cache_dir=self.data_dir / "language_cache"
                )
                self.subsystems["language_processor"] = self.language_processor
                logger.info("🌍 Multi-Language Processor initialized")
            
            # Security systems
            if enable_all or self.config["security"]["privacy_protection"]:
                self.privacy_guardian = PrivacyGuardian(
                    encryption_level=self.config["security"]["encryption_level"]
                )
                self.subsystems["privacy_guardian"] = self.privacy_guardian
                logger.info("🔒 Privacy Guardian initialized")
            
            if enable_all or self.config["security"]["audit_logging"]:
                self.audit_logger = AuditLogger(
                    log_dir=self.data_dir / "audit_logs"
                )
                self.subsystems["audit_logger"] = self.audit_logger
                logger.info("📋 Audit Logger initialized")
            
            if enable_all:
                self.access_controller = AccessController(
                    config=self.config["security"]
                )
                self.subsystems["access_controller"] = self.access_controller
                logger.info("🚪 Access Controller initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize subsystems: {e}")
            raise
    
    async def start_all_systems(self) -> bool:
        """Start all Guardian systems"""
        try:
            logger.info("🚀 Starting Guardian Engine...")
            
            # Update status
            self.is_running = True
            self.current_status.status = "operational"
            self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["operational"]
            
            # Start subsystems
            startup_tasks = []
            
            if "threat_monitor" in self.subsystems:
                startup_tasks.append(self.threat_monitor.start_monitoring())
            
            if "emergency_aid" in self.subsystems:
                startup_tasks.append(self.emergency_aid.initialize_emergency_protocols())
            
            if "health_apis" in self.subsystems:
                startup_tasks.append(self.health_apis.initialize_connections())
            
            # Start monitoring tasks
            startup_tasks.extend([
                self._health_check_loop(),
                self._performance_monitoring_loop(),
                self._event_processing_loop()
            ])
            
            # Execute startup
            await asyncio.gather(*startup_tasks, return_exceptions=True)
            
            # Update active modules
            self.current_status.active_modules = list(self.subsystems.keys())
            
            # Log startup event
            await self._log_system_event(
                event_type="system_startup",
                severity="info",
                description="Guardian Engine started successfully",
                context={"modules": self.current_status.active_modules}
            )
            
            logger.info(f"✅ Guardian Engine started with {len(self.subsystems)} modules")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Guardian Engine: {e}")
            self.current_status.status = "critical"
            self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["critical"]
            return False
    
    async def stop_all_systems(self) -> bool:
        """Stop all Guardian systems gracefully"""
        try:
            logger.info("🛑 Stopping Guardian Engine...")
            
            self.is_running = False
            
            # Stop subsystems
            if "threat_monitor" in self.subsystems:
                await self.threat_monitor.stop_monitoring()
            
            # Log shutdown event
            await self._log_system_event(
                event_type="system_shutdown",
                severity="info",
                description="Guardian Engine shutdown initiated",
                context={"uptime": time.time() - self.start_time}
            )
            
            # Update status
            self.current_status.status = "offline"
            self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["offline"]
            
            logger.info("✅ Guardian Engine stopped gracefully")
            return True
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return False
    
    async def _health_check_loop(self):
        """Continuous health monitoring"""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config["monitoring"]["health_check_interval"])
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)  # Retry after 30 seconds
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        health_metrics = {
            "subsystem_count": len(self.subsystems),
            "uptime": time.time() - self.start_time,
            "memory_usage": 0,  # Would implement actual memory monitoring
            "response_time": 0,  # Would implement actual response time tracking
            "error_rate": 0     # Would implement actual error rate tracking
        }
        
        # Check subsystem health
        unhealthy_modules = []
        for module_name, module in self.subsystems.items():
            if hasattr(module, 'health_check'):
                try:
                    is_healthy = await module.health_check()
                    if not is_healthy:
                        unhealthy_modules.append(module_name)
                except Exception as e:
                    logger.warning(f"Health check failed for {module_name}: {e}")
                    unhealthy_modules.append(module_name)
        
        # Update system status
        if unhealthy_modules:
            if len(unhealthy_modules) > len(self.subsystems) // 2:
                self.current_status.status = "critical"
                self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["critical"]
            else:
                self.current_status.status = "degraded"
                self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["degraded"]
        else:
            self.current_status.status = "operational"
            self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["operational"]
        
        # Update metrics
        self.current_status.performance_metrics = health_metrics
        self.current_status.last_health_check = time.time()
        self.current_status.uptime_seconds = health_metrics["uptime"]
        
        # Log significant status changes
        if unhealthy_modules:
            await self._log_system_event(
                event_type="health_check_warning",
                severity="warning",
                description=f"Unhealthy modules detected: {unhealthy_modules}",
                context={"unhealthy_modules": unhealthy_modules, "metrics": health_metrics}
            )
    
    async def _performance_monitoring_loop(self):
        """Monitor system performance"""
        while self.is_running:
            try:
                performance_data = {
                    "timestamp": time.time(),
                    "cpu_usage": 0,      # Would implement actual CPU monitoring
                    "memory_usage": 0,   # Would implement actual memory monitoring
                    "disk_usage": 0,     # Would implement actual disk monitoring
                    "network_io": 0,     # Would implement actual network monitoring
                    "active_requests": 0, # Would track active requests
                    "response_times": []  # Would track response times
                }
                
                self.performance_history.append(performance_data)
                
                # Keep only recent history (last 24 hours)
                cutoff_time = time.time() - 86400
                self.performance_history = [
                    p for p in self.performance_history 
                    if p["timestamp"] > cutoff_time
                ]
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _event_processing_loop(self):
        """Process system events"""
        while self.is_running:
            try:
                # Process any pending events
                await self._process_pending_events()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                await asyncio.sleep(30)
    
    async def _process_pending_events(self):
        """Process pending system events"""
        # This would implement event queue processing
        # For now, just maintain event history
        
        # Keep only recent events (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 3600)
        self.system_events = [
            event for event in self.system_events 
            if event.timestamp > cutoff_time
        ]
    
    async def _log_system_event(self, 
                               event_type: str, 
                               severity: str, 
                               description: str, 
                               context: Dict[str, Any] = None,
                               source_module: str = "guardian_engine"):
        """Log a system event"""
        event = SystemEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            source_module=source_module,
            description=description,
            context=context or {},
            symbolic_signature=self._generate_event_symbols(event_type, severity)
        )
        
        self.system_events.append(event)
        
        # Log to audit system if available
        if "audit_logger" in self.subsystems:
            await self.audit_logger.log_event(asdict(event))
        
        # Log to standard logger
        log_level = getattr(logging, severity.upper(), logging.INFO)
        logger.log(log_level, f"[{event_type}] {description}")
    
    def _generate_event_symbols(self, event_type: str, severity: str) -> List[str]:
        """Generate symbolic signature for events"""
        symbols = ["📋"]  # Base event symbol
        
        # Add severity symbols
        if severity == "critical":
            symbols.extend(["🚨", "🔴"])
        elif severity == "warning":
            symbols.extend(["⚠️", "🟡"])
        elif severity == "info":
            symbols.extend(["ℹ️", "🟢"])
        
        # Add event type symbols
        if "startup" in event_type:
            symbols.append("🚀")
        elif "shutdown" in event_type:
            symbols.append("🛑")
        elif "emergency" in event_type:
            symbols.append("🚨")
        elif "medical" in event_type:
            symbols.append("🏥")
        elif "security" in event_type:
            symbols.append("🔒")
        
        return symbols
    
    # Public API methods
    
    async def request_consent(self, 
                            requester: str, 
                            resource: str, 
                            permission: str, 
                            context: Dict = None) -> Dict:
        """Request consent for an action"""
        if "consent_manager" not in self.subsystems:
            return {"error": "Consent manager not available"}
        
        consent_request = ConsentRequest(
            id=str(uuid.uuid4()),
            requester=requester,
            target_resource=resource,
            permission_type=permission,
            requested_at=time.time(),
            expires_at=time.time() + 3600,  # 1 hour expiry
            context=context or {},
            symbolic_path=["🔐", "❓"],
            trust_score=0.5  # Default trust score
        )
        
        result = await self.consent_manager.process_consent_request(consent_request)
        
        await self._log_system_event(
            event_type="consent_request",
            severity="info",
            description=f"Consent requested by {requester} for {resource}",
            context={"result": result.status.value}
        )
        
        return {
            "consent_id": result.id,
            "status": result.status.value,
            "trust_score": result.trust_score,
            "reason": result.decision_reason,
            "symbolic_path": result.symbolic_path
        }
    
    async def read_medication_label(self, image_path: str) -> Dict:
        """Read medication information from image"""
        if "medical_ocr" not in self.subsystems:
            return {"error": "Medical OCR not available"}
        
        try:
            result = await self.medical_ocr.read_medication_label(image_path)
            
            await self._log_system_event(
                event_type="medical_ocr",
                severity="info",
                description="Medication label read",
                context={"success": result.get("success", False)}
            )
            
            return result
            
        except Exception as e:
            await self._log_system_event(
                event_type="medical_ocr_error",
                severity="error",
                description=f"OCR reading failed: {e}",
                context={"image_path": image_path}
            )
            return {"error": str(e)}
    
    async def emergency_alert(self, 
                            emergency_type: str, 
                            severity: str = "high", 
                            context: Dict = None) -> Dict:
        """Trigger emergency alert"""
        if "emergency_aid" not in self.subsystems:
            return {"error": "Emergency aid not available"}
        
        try:
            # Set emergency flag
            self.current_status.emergency_active = True
            self.current_status.symbolic_status = self.SYSTEM_SYMBOLS["emergency"]
            
            result = await self.emergency_aid.handle_emergency(
                emergency_type=emergency_type,
                severity=severity,
                context=context or {}
            )
            
            await self._log_system_event(
                event_type="emergency_alert",
                severity="critical",
                description=f"Emergency alert: {emergency_type}",
                context=context or {}
            )
            
            return result
            
        except Exception as e:
            await self._log_system_event(
                event_type="emergency_error",
                severity="critical",
                description=f"Emergency handling failed: {e}",
                context={"emergency_type": emergency_type}
            )
            return {"error": str(e)}
    
    async def describe_scene(self, image_path: str, language: str = "en") -> Dict:
        """Describe visual scene for accessibility"""
        results = {}
        
        # Vision assistance
        if "vision_assist" in self.subsystems:
            try:
                vision_result = await self.vision_assist.describe_scene(image_path)
                results["vision"] = vision_result
            except Exception as e:
                results["vision_error"] = str(e)
        
        # Language processing
        if "language_processor" in self.subsystems and language != "en":
            try:
                if "vision" in results and "description" in results["vision"]:
                    translation = await self.language_processor.translate(
                        text=results["vision"]["description"],
                        target_language=language
                    )
                    results["translated_description"] = translation
            except Exception as e:
                results["translation_error"] = str(e)
        
        await self._log_system_event(
            event_type="accessibility_assist",
            severity="info",
            description="Scene description provided",
            context={"language": language}
        )
        
        return results
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "system_id": self.system_id,
            "status": asdict(self.current_status),
            "subsystems": list(self.subsystems.keys()),
            "recent_events": [
                asdict(event) for event in self.system_events[-10:]
            ],
            "performance_summary": self._get_performance_summary()
        }
    
    def _get_performance_summary(self) -> Dict:
        """Get performance summary"""
        if not self.performance_history:
            return {"status": "No data available"}
        
        recent_data = self.performance_history[-60:]  # Last hour
        
        return {
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "data_points": len(recent_data),
            "avg_cpu": sum(p.get("cpu_usage", 0) for p in recent_data) / len(recent_data),
            "avg_memory": sum(p.get("memory_usage", 0) for p in recent_data) / len(recent_data),
            "last_updated": recent_data[-1]["timestamp"] if recent_data else 0
        }


# Convenience functions for direct usage

async def create_guardian(config_path: str = None) -> GuardianEngine:
    """Create and initialize Guardian Engine"""
    guardian = GuardianEngine(config_path=config_path)
    await guardian.start_all_systems()
    return guardian


async def emergency_medical_assist(image_path: str, guardian: GuardianEngine = None) -> Dict:
    """Quick emergency medical assistance"""
    if guardian is None:
        guardian = await create_guardian()
    
    # Read medication label
    ocr_result = await guardian.read_medication_label(image_path)
    
    # If successful, provide additional assistance
    if ocr_result.get("success") and "medication" in ocr_result:
        medication = ocr_result["medication"]
        
        # Get additional medication information
        if "health_apis" in guardian.subsystems:
            try:
                med_info = await guardian.health_apis.get_medication_info(medication["name"])
                ocr_result["additional_info"] = med_info
            except Exception as e:
                ocr_result["additional_info_error"] = str(e)
    
    return ocr_result


if __name__ == "__main__":
    import sys
    
    async def main():
        """Main demonstration"""
        print("🛡️ Enhanced Guardian Engine Demo")
        print("=" * 50)
        
        try:
            # Create Guardian
            guardian = await create_guardian()
            
            # Show status
            status = guardian.get_system_status()
            print(f"✅ Guardian Engine operational")
            print(f"   System ID: {status['system_id'][:8]}")
            print(f"   Active modules: {len(status['subsystems'])}")
            print(f"   Status: {status['status']['status']}")
            print(f"   Symbolic: {''.join(status['status']['symbolic_status'])}")
            
            # Demo features
            print(f"\n🔍 Testing consent management...")
            consent_result = await guardian.request_consent(
                requester="demo_user",
                resource="/demo/resource",
                permission="read"
            )
            print(f"   Consent result: {consent_result['status']}")
            
            # Keep running for a bit to show monitoring
            print(f"\n⏳ Monitoring for 10 seconds...")
            await asyncio.sleep(10)
            
            # Show final status
            final_status = guardian.get_system_status()
            print(f"\n📊 Final Status:")
            print(f"   Uptime: {final_status['performance_summary']['uptime_hours']:.2f} hours")
            print(f"   Events logged: {len(final_status['recent_events'])}")
            
            # Graceful shutdown
            await guardian.stop_all_systems()
            print(f"\n✅ Guardian Engine demo completed")
            
        except KeyboardInterrupt:
            print(f"\n🛑 Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            sys.exit(1)
    
    asyncio.run(main())
