#!/usr/bin/env python3
"""
Emergency Aid - Emergency detection, response, and contact management
Handles medical emergencies, safety protocols, and automated assistance
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Types of emergencies"""
    MEDICAL = "medical"
    SECURITY = "security"
    FIRE = "fire"
    NATURAL_DISASTER = "natural_disaster"
    TECHNICAL = "technical"
    PSYCHOLOGICAL = "psychological"
    UNKNOWN = "unknown"


class EmergencySeverity(Enum):
    """Emergency severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    LIFE_THREATENING = 5


@dataclass
class EmergencyContact:
    """Emergency contact information"""
    name: str
    phone: str
    email: Optional[str]
    relationship: str
    contact_type: str  # medical, family, professional, emergency_services
    priority: int
    availability: str  # 24/7, business_hours, on_call
    specialties: List[str]
    languages: List[str]
    notes: Optional[str]


@dataclass
class EmergencyIncident:
    """Emergency incident record"""
    incident_id: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    timestamp: float
    location: Optional[str]
    description: str
    symptoms: List[str]
    actions_taken: List[str]
    contacts_notified: List[str]
    response_time: Optional[float]
    resolution_time: Optional[float]
    status: str  # active, resolved, escalated
    notes: List[str]
    symbolic_signature: List[str]


class EmergencyAid:
    """
    Emergency detection and response system
    Provides automated emergency assistance and contact management
    """
    
    # Emergency detection patterns
    EMERGENCY_KEYWORDS = {
        EmergencyType.MEDICAL: [
            "chest pain", "heart attack", "stroke", "unconscious", "seizure",
            "severe bleeding", "allergic reaction", "overdose", "poisoning",
            "broken bone", "severe pain", "can't breathe", "choking"
        ],
        EmergencyType.SECURITY: [
            "intruder", "break in", "theft", "assault", "robbery",
            "suspicious activity", "stalker", "harassment"
        ],
        EmergencyType.FIRE: [
            "fire", "smoke", "burning", "flames", "gas leak"
        ],
        EmergencyType.PSYCHOLOGICAL: [
            "suicidal", "panic attack", "severe anxiety", "psychotic episode",
            "self harm", "violence threat"
        ]
    }
    
    # Symbolic patterns for different emergency types
    EMERGENCY_SYMBOLS = {
        EmergencyType.MEDICAL: ["🚑", "⚕️", "🏥"],
        EmergencyType.SECURITY: ["🚨", "👮", "🔒"],
        EmergencyType.FIRE: ["🚒", "🔥", "🚨"],
        EmergencyType.NATURAL_DISASTER: ["🌪️", "🚨", "🏠"],
        EmergencyType.TECHNICAL: ["💻", "⚡", "🔧"],
        EmergencyType.PSYCHOLOGICAL: ["🧠", "💚", "👨‍⚕️"],
        EmergencyType.UNKNOWN: ["🚨", "❓", "📞"]
    }
    
    # Severity symbols
    SEVERITY_SYMBOLS = {
        EmergencySeverity.LOW: ["🟢", "ℹ️"],
        EmergencySeverity.MEDIUM: ["🟡", "⚠️"],
        EmergencySeverity.HIGH: ["🟠", "🚨"],
        EmergencySeverity.CRITICAL: ["🔴", "💥"],
        EmergencySeverity.LIFE_THREATENING: ["⚫", "💀", "🚨"]
    }
    
    def __init__(self, 
                 config_path: str = "config/emergency_contacts.yaml",
                 data_dir: str = "data/emergency_data"):
        
        self.config_path = Path(config_path)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Emergency contacts and configuration
        self.emergency_contacts: Dict[str, EmergencyContact] = {}
        self.emergency_services: Dict[str, Dict] = {}
        self.emergency_protocols: Dict[str, Dict] = {}
        
        # Active incidents
        self.active_incidents: Dict[str, EmergencyIncident] = {}
        self.incident_history: List[EmergencyIncident] = []
        
        # Response tracking
        self.response_stats = {
            "total_incidents": 0,
            "incidents_by_type": {},
            "average_response_time": 0.0,
            "successful_resolutions": 0,
            "false_positives": 0
        }
        
        # Load configuration
        self._load_emergency_configuration()
        
        logger.info("🚨 Emergency Aid system initialized")
    
    def _load_emergency_configuration(self):
        """Load emergency contacts and configuration"""
        try:
            if self.config_path.exists():
                import yaml
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Load emergency contacts
                if "emergency_contacts" in config:
                    self._load_emergency_contacts(config["emergency_contacts"])
                
                # Load emergency services
                if "emergency_services" in config:
                    self.emergency_services = config["emergency_services"]
                
                # Load protocols
                if "emergency_protocols" in config:
                    self.emergency_protocols = config["emergency_protocols"]
                    
                logger.info(f"Loaded emergency configuration from {self.config_path}")
            else:
                # Create default configuration
                self._create_default_configuration()
                
        except Exception as e:
            logger.error(f"Failed to load emergency configuration: {e}")
            self._create_default_configuration()
    
    def _load_emergency_contacts(self, contacts_config: Dict):
        """Load emergency contacts from configuration"""
        for category, contacts in contacts_config.items():
            for contact_data in contacts:
                if isinstance(contact_data, dict):
                    contact = EmergencyContact(
                        name=contact_data.get("name", "Unknown"),
                        phone=contact_data.get("phone", ""),
                        email=contact_data.get("email"),
                        relationship=contact_data.get("relationship", "unknown"),
                        contact_type=category,
                        priority=contact_data.get("priority", 5),
                        availability=contact_data.get("availability", "unknown"),
                        specialties=contact_data.get("specialties", []),
                        languages=contact_data.get("languages", ["en"]),
                        notes=contact_data.get("notes")
                    )
                    
                    contact_id = f"{category}_{contact.name.lower().replace(' ', '_')}"
                    self.emergency_contacts[contact_id] = contact
        
        logger.info(f"Loaded {len(self.emergency_contacts)} emergency contacts")
    
    def _create_default_configuration(self):
        """Create default emergency configuration"""
        default_config = {
            "emergency_contacts": {
                "emergency_services": [
                    {
                        "name": "Emergency Services",
                        "phone": "911",
                        "relationship": "emergency_services",
                        "priority": 1,
                        "availability": "24/7",
                        "specialties": ["all_emergencies"]
                    }
                ],
                "medical": [
                    {
                        "name": "Primary Care Physician",
                        "phone": "+1-555-DOCTOR",
                        "email": "doctor@example.com",
                        "relationship": "primary_care",
                        "priority": 2,
                        "availability": "business_hours",
                        "specialties": ["general_medicine"]
                    }
                ],
                "family": [
                    {
                        "name": "Emergency Contact",
                        "phone": "+1-555-FAMILY",
                        "relationship": "family",
                        "priority": 3,
                        "availability": "24/7"
                    }
                ]
            },
            "emergency_services": {
                "local_emergency": "911",
                "poison_control": "1-800-222-1222",
                "crisis_hotline": "988"
            },
            "emergency_protocols": {
                "medical": {
                    "steps": [
                        "Assess consciousness and breathing",
                        "Call 911 if life-threatening",
                        "Provide first aid if trained",
                        "Notify emergency contacts",
                        "Document incident"
                    ]
                },
                "security": {
                    "steps": [
                        "Ensure personal safety",
                        "Call 911 if immediate danger",
                        "Document what happened",
                        "Notify contacts",
                        "Secure premises"
                    ]
                }
            }
        }
        
        # Save default configuration
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            import yaml
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, indent=2)
            
            # Load the defaults
            self._load_emergency_contacts(default_config["emergency_contacts"])
            self.emergency_services = default_config["emergency_services"]
            self.emergency_protocols = default_config["emergency_protocols"]
            
            logger.info("Created default emergency configuration")
            
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    async def initialize_emergency_protocols(self):
        """Initialize emergency response protocols"""
        logger.info("🚨 Initializing emergency protocols")
        
        # Start background monitoring tasks
        await asyncio.gather(
            self._monitor_active_incidents(),
            self._periodic_contact_verification(),
            return_exceptions=True
        )
    
    async def detect_emergency(self, text: str, context: Dict = None) -> Optional[Dict]:
        """Detect emergency from text input"""
        text_lower = text.lower()
        context = context or {}
        
        # Check for emergency keywords
        detected_type = None
        confidence = 0.0
        matching_keywords = []
        
        for emergency_type, keywords in self.EMERGENCY_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                match_confidence = len(matches) / len(keywords)
                if match_confidence > confidence:
                    confidence = match_confidence
                    detected_type = emergency_type
                    matching_keywords = matches
        
        if detected_type and confidence > 0.1:  # Threshold for detection
            # Determine severity
            severity = self._assess_severity(text_lower, detected_type, matching_keywords)
            
            return {
                "emergency_detected": True,
                "emergency_type": detected_type.value,
                "severity": severity.value,
                "confidence": confidence,
                "matching_keywords": matching_keywords,
                "recommended_actions": self._get_recommended_actions(detected_type, severity)
            }
        
        return None
    
    def _assess_severity(self, text: str, emergency_type: EmergencyType, keywords: List[str]) -> EmergencySeverity:
        """Assess emergency severity based on context"""
        # High severity keywords
        critical_keywords = [
            "unconscious", "not breathing", "severe bleeding", "chest pain",
            "heart attack", "stroke", "overdose", "poisoning", "choking"
        ]
        
        urgent_keywords = [
            "severe pain", "allergic reaction", "seizure", "break in",
            "intruder", "fire", "gas leak"
        ]
        
        # Check for critical indicators
        if any(kw in text for kw in critical_keywords):
            return EmergencySeverity.LIFE_THREATENING
        
        if any(kw in text for kw in urgent_keywords):
            return EmergencySeverity.CRITICAL
        
        # Multiple symptoms or emergency words
        if len(keywords) >= 3:
            return EmergencySeverity.HIGH
        elif len(keywords) >= 2:
            return EmergencySeverity.MEDIUM
        else:
            return EmergencySeverity.LOW
    
    def _get_recommended_actions(self, emergency_type: EmergencyType, severity: EmergencySeverity) -> List[str]:
        """Get recommended actions for emergency type and severity"""
        actions = []
        
        # Life-threatening emergencies
        if severity == EmergencySeverity.LIFE_THREATENING:
            actions.extend([
                "Call 911 immediately",
                "Do not move the person unless in immediate danger",
                "Begin CPR if trained and person is not breathing",
                "Stay on the line with 911 dispatcher"
            ])
        
        # Critical emergencies
        elif severity == EmergencySeverity.CRITICAL:
            actions.extend([
                "Call 911",
                "Notify emergency contacts",
                "Provide first aid if trained",
                "Stay with the person"
            ])
        
        # Type-specific actions
        if emergency_type == EmergencyType.MEDICAL:
            actions.extend([
                "Check for medical alert bracelet/wallet card",
                "Gather medication list if available",
                "Note time of symptom onset"
            ])
        elif emergency_type == EmergencyType.SECURITY:
            actions.extend([
                "Ensure your safety first",
                "Do not confront intruders",
                "Lock doors and stay in safe room if possible"
            ])
        elif emergency_type == EmergencyType.FIRE:
            actions.extend([
                "Evacuate immediately",
                "Close doors behind you",
                "Do not use elevators",
                "Meet at designated meeting point"
            ])
        
        return actions
    
    async def handle_emergency(self, 
                             emergency_type: str,
                             severity: str = "medium",
                             context: Dict = None) -> Dict:
        """Handle an emergency situation"""
        start_time = time.time()
        context = context or {}
        
        try:
            # Create incident record
            incident = EmergencyIncident(
                incident_id=str(uuid.uuid4()),
                emergency_type=EmergencyType(emergency_type),
                severity=EmergencySeverity[severity.upper()],
                timestamp=start_time,
                location=context.get("location"),
                description=context.get("description", f"{emergency_type} emergency"),
                symptoms=context.get("symptoms", []),
                actions_taken=[],
                contacts_notified=[],
                response_time=None,
                resolution_time=None,
                status="active",
                notes=[],
                symbolic_signature=self._generate_incident_symbols(
                    EmergencyType(emergency_type), 
                    EmergencySeverity[severity.upper()]
                )
            )
            
            # Add to active incidents
            self.active_incidents[incident.incident_id] = incident
            
            # Execute emergency response
            response_result = await self._execute_emergency_response(incident, context)
            
            # Update incident with response
            incident.actions_taken = response_result["actions_taken"]
            incident.contacts_notified = response_result["contacts_notified"]
            incident.response_time = time.time() - start_time
            
            # Update statistics
            self._update_emergency_stats(incident)
            
            logger.critical(f"🚨 Emergency handled: {incident.incident_id[:8]} ({emergency_type})")
            
            return {
                "incident_id": incident.incident_id,
                "emergency_type": emergency_type,
                "severity": severity,
                "response_time": incident.response_time,
                "actions_taken": incident.actions_taken,
                "contacts_notified": incident.contacts_notified,
                "symbolic_signature": "".join(incident.symbolic_signature),
                "status": incident.status
            }
            
        except Exception as e:
            logger.error(f"Emergency handling failed: {e}")
            return {
                "error": str(e),
                "emergency_type": emergency_type,
                "severity": severity
            }
    
    async def _execute_emergency_response(self, incident: EmergencyIncident, context: Dict) -> Dict:
        """Execute emergency response protocol"""
        actions_taken = []
        contacts_notified = []
        
        try:
            # Get protocol for emergency type
            protocol = self.emergency_protocols.get(incident.emergency_type.value, {})
            protocol_steps = protocol.get("steps", [])
            
            # Execute protocol steps
            for step in protocol_steps[:3]:  # Execute first 3 steps automatically
                actions_taken.append(step)
                await asyncio.sleep(0.1)  # Simulate action execution
            
            # Notify emergency contacts based on severity
            if incident.severity.value >= EmergencySeverity.HIGH.value:
                # High severity - notify all priority contacts
                priority_contacts = self._get_priority_contacts(incident.emergency_type, max_priority=3)
                
                for contact in priority_contacts:
                    try:
                        await self._notify_contact(contact, incident)
                        contacts_notified.append(contact.name)
                    except Exception as e:
                        logger.error(f"Failed to notify {contact.name}: {e}")
            
            elif incident.severity.value >= EmergencySeverity.MEDIUM.value:
                # Medium severity - notify primary contacts
                primary_contacts = self._get_priority_contacts(incident.emergency_type, max_priority=2)
                
                for contact in primary_contacts[:2]:  # Limit to top 2
                    try:
                        await self._notify_contact(contact, incident)
                        contacts_notified.append(contact.name)
                    except Exception as e:
                        logger.error(f"Failed to notify {contact.name}: {e}")
            
            # Log emergency actions
            actions_taken.append("Emergency response protocol executed")
            actions_taken.append(f"Notified {len(contacts_notified)} contacts")
            
            return {
                "actions_taken": actions_taken,
                "contacts_notified": contacts_notified,
                "protocol_executed": True
            }
            
        except Exception as e:
            logger.error(f"Emergency response execution failed: {e}")
            return {
                "actions_taken": actions_taken,
                "contacts_notified": contacts_notified,
                "protocol_executed": False,
                "error": str(e)
            }
    
    def _get_priority_contacts(self, emergency_type: EmergencyType, max_priority: int = 3) -> List[EmergencyContact]:
        """Get priority contacts for emergency type"""
        relevant_contacts = []
        
        # Filter contacts by type and priority
        for contact in self.emergency_contacts.values():
            if (contact.contact_type in ["emergency_services", emergency_type.value, "family"] and
                contact.priority <= max_priority):
                relevant_contacts.append(contact)
        
        # Sort by priority
        relevant_contacts.sort(key=lambda c: c.priority)
        
        return relevant_contacts
    
    async def _notify_contact(self, contact: EmergencyContact, incident: EmergencyIncident):
        """Notify an emergency contact"""
        logger.warning(f"📞 Notifying {contact.name} ({contact.phone})")
        
        # In production, this would integrate with:
        # - SMS/messaging services
        # - Email services
        # - Voice call services
        # - Emergency notification systems
        
        # Simulate notification delay
        await asyncio.sleep(0.5)
        
        # Create notification message
        message = self._create_notification_message(incident, contact)
        
        # Log the notification
        logger.info(f"Emergency notification sent to {contact.name}: {message[:50]}...")
    
    def _create_notification_message(self, incident: EmergencyIncident, contact: EmergencyContact) -> str:
        """Create emergency notification message"""
        severity_text = incident.severity.name.replace("_", " ").title()
        
        message = f"""
EMERGENCY ALERT - {severity_text}

Type: {incident.emergency_type.value.replace("_", " ").title()}
Time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(incident.timestamp))}
Location: {incident.location or "Unknown"}

Description: {incident.description}

Actions taken:
{chr(10).join(f"- {action}" for action in incident.actions_taken)}

Incident ID: {incident.incident_id}

This is an automated emergency notification.
        """.strip()
        
        return message
    
    def _generate_incident_symbols(self, emergency_type: EmergencyType, severity: EmergencySeverity) -> List[str]:
        """Generate symbolic signature for incident"""
        symbols = []
        
        # Add emergency type symbols
        symbols.extend(self.EMERGENCY_SYMBOLS.get(emergency_type, self.EMERGENCY_SYMBOLS[EmergencyType.UNKNOWN]))
        
        # Add severity symbols
        symbols.extend(self.SEVERITY_SYMBOLS.get(severity, self.SEVERITY_SYMBOLS[EmergencySeverity.MEDIUM]))
        
        return symbols
    
    def _update_emergency_stats(self, incident: EmergencyIncident):
        """Update emergency response statistics"""
        self.response_stats["total_incidents"] += 1
        
        # Update by type
        incident_type = incident.emergency_type.value
        if incident_type not in self.response_stats["incidents_by_type"]:
            self.response_stats["incidents_by_type"][incident_type] = 0
        self.response_stats["incidents_by_type"][incident_type] += 1
        
        # Update average response time
        if incident.response_time:
            current_avg = self.response_stats["average_response_time"]
            total_incidents = self.response_stats["total_incidents"]
            
            if total_incidents == 1:
                self.response_stats["average_response_time"] = incident.response_time
            else:
                new_avg = ((current_avg * (total_incidents - 1)) + incident.response_time) / total_incidents
                self.response_stats["average_response_time"] = new_avg
    
    async def _monitor_active_incidents(self):
        """Monitor active incidents for resolution"""
        while True:
            try:
                current_time = time.time()
                resolved_incidents = []
                
                for incident_id, incident in self.active_incidents.items():
                    # Auto-resolve incidents after 1 hour
                    if current_time - incident.timestamp > 3600:
                        incident.status = "auto_resolved"
                        incident.resolution_time = current_time - incident.timestamp
                        incident.notes.append("Auto-resolved after 1 hour")
                        
                        resolved_incidents.append(incident_id)
                        self.incident_history.append(incident)
                
                # Remove resolved incidents from active list
                for incident_id in resolved_incidents:
                    del self.active_incidents[incident_id]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Incident monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _periodic_contact_verification(self):
        """Periodically verify emergency contacts"""
        while True:
            try:
                # In production, this would verify contact availability
                # For now, just log verification
                logger.info(f"Verifying {len(self.emergency_contacts)} emergency contacts")
                
                # Check contact reachability (simulated)
                unreachable_contacts = []
                for contact_id, contact in self.emergency_contacts.items():
                    # Simulate contact verification
                    if not contact.phone or contact.phone == "unknown":
                        unreachable_contacts.append(contact.name)
                
                if unreachable_contacts:
                    logger.warning(f"Unreachable contacts: {', '.join(unreachable_contacts)}")
                
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"Contact verification error: {e}")
                await asyncio.sleep(86400)
    
    # Public API methods
    
    async def resolve_incident(self, incident_id: str, resolution_notes: str = "") -> bool:
        """Manually resolve an incident"""
        if incident_id in self.active_incidents:
            incident = self.active_incidents[incident_id]
            incident.status = "resolved"
            incident.resolution_time = time.time() - incident.timestamp
            
            if resolution_notes:
                incident.notes.append(resolution_notes)
            
            # Move to history
            self.incident_history.append(incident)
            del self.active_incidents[incident_id]
            
            self.response_stats["successful_resolutions"] += 1
            
            logger.info(f"Incident {incident_id[:8]} resolved")
            return True
        
        return False
    
    def get_active_incidents(self) -> List[Dict]:
        """Get all active incidents"""
        return [asdict(incident) for incident in self.active_incidents.values()]
    
    def get_incident_history(self, limit: int = 50) -> List[Dict]:
        """Get incident history"""
        recent_incidents = self.incident_history[-limit:] if limit > 0 else self.incident_history
        return [asdict(incident) for incident in recent_incidents]
    
    def get_emergency_contacts(self) -> List[Dict]:
        """Get all emergency contacts"""
        return [asdict(contact) for contact in self.emergency_contacts.values()]
    
    def get_emergency_statistics(self) -> Dict:
        """Get emergency response statistics"""
        stats = self.response_stats.copy()
        stats["active_incidents"] = len(self.active_incidents)
        stats["total_contacts"] = len(self.emergency_contacts)
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Check if we have emergency contacts
            if not self.emergency_contacts:
                logger.warning("No emergency contacts configured")
                return False
            
            # Check if emergency services contact exists
            has_emergency_services = any(
                contact.contact_type == "emergency_services" 
                for contact in self.emergency_contacts.values()
            )
            
            if not has_emergency_services:
                logger.warning("No emergency services contact configured")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Emergency aid health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo emergency aid functionality"""
        print("🚨 Emergency Aid Demo")
        print("=" * 40)
        
        emergency_aid = EmergencyAid()
        await emergency_aid.initialize_emergency_protocols()
        
        # Test emergency detection
        test_texts = [
            "I'm having chest pain and can't breathe",
            "Someone broke into my house",
            "There's smoke coming from the kitchen",
            "I feel dizzy but I think I'm okay"
        ]
        
        for text in test_texts:
            print(f"\n🔍 Testing: '{text}'")
            
            detection = await emergency_aid.detect_emergency(text)
            
            if detection and detection["emergency_detected"]:
                print(f"   🚨 Emergency: {detection['emergency_type']}")
                print(f"   📊 Severity: {detection['severity']}")
                print(f"   🎯 Confidence: {detection['confidence']:.2f}")
                print(f"   💡 Actions: {detection['recommended_actions'][:2]}")
                
                # Handle the emergency
                if detection['severity'] in ['high', 'critical', 'life_threatening']:
                    print(f"   ⚡ Handling emergency...")
                    
                    result = await emergency_aid.handle_emergency(
                        emergency_type=detection['emergency_type'],
                        severity=detection['severity'],
                        context={"description": text}
                    )
                    
                    print(f"   ✅ Response time: {result['response_time']:.2f}s")
                    print(f"   📞 Contacts notified: {len(result['contacts_notified'])}")
                    print(f"   🔮 Symbols: {result['symbolic_signature']}")
            else:
                print(f"   ✅ No emergency detected")
        
        # Show statistics
        stats = emergency_aid.get_emergency_statistics()
        print(f"\n📊 Emergency Statistics:")
        print(f"   Total incidents: {stats['total_incidents']}")
        print(f"   Active incidents: {stats['active_incidents']}")
        print(f"   Emergency contacts: {stats['total_contacts']}")
        if stats['average_response_time'] > 0:
            print(f"   Average response time: {stats['average_response_time']:.2f}s")
        
        # Show active incidents
        active = emergency_aid.get_active_incidents()
        if active:
            print(f"\n🚨 Active Incidents:")
            for incident in active:
                print(f"   - {incident['emergency_type']} ({incident['severity']})")
    
    asyncio.run(demo())
