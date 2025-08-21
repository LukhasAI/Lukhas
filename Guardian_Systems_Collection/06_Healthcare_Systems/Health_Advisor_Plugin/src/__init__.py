"""
HealthAdvisor Plugin - Main Interface

A commercial plugin for LUKHAS AGI that provides AI-powered health advisory
capabilities with strict safety and compliance measures.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from lucas.core import LukhasPlugin, SymbolicEngine
from lucas.core.safety import SafetyChecker
from lucas.core.compliance import ComplianceManager

logger = logging.getLogger(__name__)

@dataclass
class HealthAdvisorConfig:
    """Configuration for HealthAdvisor plugin"""
    tier: str = "personal"  # personal, professional, or enterprise
    compliance_mode: str = "strict"  # strict, standard
    emergency_protocols: bool = True
    custom_rules: Optional[Dict[str, Any]] = None
    data_retention_days: int = 365
    provider_access_level: str = "standard"

class HealthAdvisorPlugin(LukhasPlugin):
    """
    HealthAdvisor Plugin main class.
    
    Provides health monitoring, symptom analysis, and medical knowledge
    integration with strict safety protocols and medical compliance.
    """
    
    def __init__(self, config: Optional[HealthAdvisorConfig] = None):
        """Initialize the plugin with configuration"""
        super().__init__(name="health_advisor", version="1.0.0")
        self.config = config or HealthAdvisorConfig()
        
        # Initialize core components
        self._init_core_components()
        
        # Load components based on tier
        self._init_tier_components()
        
        logger.info(f"HealthAdvisor plugin initialized with tier: {self.config.tier}")
    
    def _init_core_components(self):
        """Initialize core safety and compliance components"""
        from .core_modules.diagnostic_engine import DiagnosticEngine
        from .core_modules.data_manager import HealthDataManager
        from .security.hipaa_compliance import HIPAACompliance
        
        self.symbolic_engine = SymbolicEngine()
        self.safety_checker = SafetyChecker()
        self.compliance_manager = ComplianceManager()
        
        self.diagnostic_engine = DiagnosticEngine()
        self.data_manager = HealthDataManager()
        self.hipaa_compliance = HIPAACompliance()
    
    def _init_tier_components(self):
        """Initialize components based on subscription tier"""
        # Personal tier components
        from .core_modules.user_interface_manager import UserInterfaceManager
        from .core_modules.user_profile_manager import UserProfileManager
        
        self.ui_manager = UserInterfaceManager()
        self.profile_manager = UserProfileManager()
        
        # Professional & Enterprise components
        if self.config.tier in ["professional", "enterprise"]:
            from .core_modules.external_services_connector import ExternalServicesConnector
            from .core_modules.action_scheduler import ActionScheduler
            
            self.external_connector = ExternalServicesConnector()
            self.action_scheduler = ActionScheduler()
        
        # Enterprise-only components
        if self.config.tier == "enterprise":
            from .core_modules.doctor_interface_module import DoctorInterfaceModule
            from .security.advanced_compliance import AdvancedCompliance
            
            self.doctor_interface = DoctorInterfaceModule()
            self.advanced_compliance = AdvancedCompliance()
    
    async def analyze_symptoms(self, 
                             user_id: str,
                             symptoms: List[Dict[str, Any]],
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze user symptoms and provide recommendations
        
        Args:
            user_id: User's Lucas ID
            symptoms: List of symptom descriptions with metadata
            context: Optional additional context
            
        Returns:
            Dict containing analysis and recommendations
        """
        # Ensure we have permission for the tier
        self._check_tier_permission("symptom_analysis")
        
        # Get user profile and history
        profile = await self.profile_manager.get_profile(user_id)
        
        # Run safety checks
        await self.safety_checker.verify_medical_input(symptoms)
        
        # Analyze symptoms
        analysis = await self.diagnostic_engine.analyze(
            symptoms=symptoms,
            user_profile=profile,
            context=context
        )
        
        # Check for emergencies
        if analysis.get("emergency_level", 0) > 7:
            await self._handle_emergency(user_id, analysis)
        
        # Log the interaction (HIPAA compliant)
        await self.data_manager.log_interaction(
            user_id=user_id,
            interaction_type="symptom_analysis",
            data=self.hipaa_compliance.sanitize_data(analysis)
        )
        
        return analysis
    
    async def track_wellness(self,
                           user_id: str,
                           metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track user's wellness metrics
        
        Args:
            user_id: User's Lucas ID
            metrics: Health and wellness metrics
            
        Returns:
            Dict containing analysis and recommendations
        """
        self._check_tier_permission("wellness_tracking")
        
        # Validate metrics
        await self.safety_checker.verify_wellness_metrics(metrics)
        
        # Store metrics
        await self.data_manager.store_metrics(
            user_id=user_id,
            metrics=metrics,
            timestamp=datetime.now()
        )
        
        # Analyze trends
        analysis = await self.diagnostic_engine.analyze_wellness(
            user_id=user_id,
            current_metrics=metrics
        )
        
        return analysis
    
    async def get_medical_advice(self,
                               user_id: str,
                               query: str,
                               include_provider_data: bool = False) -> Dict[str, Any]:
        """
        Get medical advice based on user query
        
        Args:
            user_id: User's Lucas ID
            query: User's medical question
            include_provider_data: Whether to include provider data
            
        Returns:
            Dict containing medical advice and relevant information
        """
        self._check_tier_permission("medical_knowledge")
        
        # Safety check the query
        await self.safety_checker.verify_medical_query(query)
        
        # Get personalized advice
        advice = await self.diagnostic_engine.get_advice(
            user_id=user_id,
            query=query,
            include_provider_data=include_provider_data and self.config.tier != "personal"
        )
        
        # Add medical disclaimers
        advice["disclaimers"] = self._get_medical_disclaimers()
        
        return advice
    
    async def _handle_emergency(self, user_id: str, analysis: Dict[str, Any]):
        """Handle emergency situations"""
        if not self.config.emergency_protocols:
            return
        
        # Get emergency contacts
        contacts = await self.profile_manager.get_emergency_contacts(user_id)
        
        # Send alerts
        if self.config.tier != "personal":
            await self.external_connector.send_emergency_alerts(
                user_id=user_id,
                analysis=analysis,
                contacts=contacts
            )
    
    def _check_tier_permission(self, feature: str):
        """Check if current tier has permission for a feature"""
        tier_features = {
            "personal": [
                "symptom_analysis",
                "wellness_tracking",
                "medical_knowledge"
            ],
            "professional": [
                "symptom_analysis",
                "wellness_tracking",
                "medical_knowledge",
                "emergency_alerts",
                "provider_communication"
            ],
            "enterprise": [
                "symptom_analysis",
                "wellness_tracking",
                "medical_knowledge",
                "emergency_alerts",
                "provider_communication",
                "ehr_integration",
                "custom_deployment"
            ]
        }
        
        if feature not in tier_features[self.config.tier]:
            raise ValueError(f"Feature '{feature}' requires a higher tier subscription")
    
    def _get_medical_disclaimers(self) -> List[str]:
        """Get appropriate medical disclaimers"""
        return [
            "This is not a substitute for professional medical advice.",
            "If this is an emergency, contact emergency services immediately.",
            "Always consult with healthcare professionals for medical decisions."
        ]
