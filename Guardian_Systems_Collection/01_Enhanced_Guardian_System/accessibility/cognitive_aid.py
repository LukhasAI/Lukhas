#!/usr/bin/env python3
"""
Cognitive Aid - Assistance for users with cognitive disabilities and memory impairments
Provides memory aids, simplified interfaces, and cognitive support features
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import uuid

logger = logging.getLogger(__name__)


@dataclass
class MemoryAid:
    """Memory aid item"""
    aid_id: str
    title: str
    description: str
    reminder_time: Optional[datetime]
    category: str  # medication, appointment, task, important_info
    priority: int  # 1-5 scale
    completed: bool
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    personalization_data: Dict


@dataclass
class CognitivePattern:
    """Cognitive pattern and preferences"""
    pattern_id: str
    user_behavior: str
    preferred_interface: str
    attention_span: int  # minutes
    best_time_periods: List[str]
    difficulty_areas: List[str]
    success_strategies: List[str]
    confidence_level: float


@dataclass
class SimplificationRule:
    """Interface simplification rule"""
    rule_id: str
    target_element: str
    simplification_type: str  # reduce_options, larger_text, clearer_labels, etc.
    condition: str
    action: str
    effectiveness_score: float


class CognitiveAssistant:
    """
    Cognitive assistance system for users with cognitive disabilities
    Provides memory aids, simplified interfaces, and cognitive support
    """
    
    # Cognitive support categories
    SUPPORT_CATEGORIES = {
        "memory": "Memory aids and reminders",
        "attention": "Attention and focus support", 
        "planning": "Planning and organization help",
        "comprehension": "Reading and comprehension aids",
        "navigation": "Interface navigation assistance",
        "decision": "Decision-making support"
    }
    
    # Simplification levels
    SIMPLIFICATION_LEVELS = {
        "minimal": "Slight adjustments for clarity",
        "moderate": "Noticeable simplification",
        "high": "Significant interface reduction",
        "maximum": "Extremely simplified interface"
    }
    
    # Memory aid categories
    MEMORY_CATEGORIES = {
        "medication": {"color": "blue", "icon": "💊", "urgency": "high"},
        "appointment": {"color": "green", "icon": "📅", "urgency": "medium"},
        "task": {"color": "orange", "icon": "✅", "urgency": "medium"},
        "important_info": {"color": "red", "icon": "❗", "urgency": "high"},
        "personal": {"color": "purple", "icon": "👤", "urgency": "low"},
        "emergency": {"color": "red", "icon": "🚨", "urgency": "critical"}
    }
    
    # Cognitive symbols
    COGNITIVE_SYMBOLS = {
        "reminder": ["🧠", "⏰", "📝"],
        "simplification": ["🔄", "📋", "✨"],
        "guidance": ["🧭", "💡", "👋"],
        "success": ["✅", "🎯", "🌟"],
        "attention": ["👀", "🔍", "⚡"],
        "error": ["❌", "🧠", "⚠️"]
    }
    
    def __init__(self, 
                 config_path: str = "config/cognitive_config.yaml",
                 user_profile_path: str = "data/user_cognitive_profile.json",
                 simplification_level: str = "moderate"):
        
        self.config_path = Path(config_path)
        self.user_profile_path = Path(user_profile_path)
        self.simplification_level = simplification_level
        
        # Memory management
        self.memory_aids: Dict[str, MemoryAid] = {}
        self.active_reminders: List[str] = []
        self.completed_tasks: List[str] = []
        
        # Cognitive patterns
        self.user_patterns: List[CognitivePattern] = []
        self.current_attention_level = 5  # 1-10 scale
        self.cognitive_load = 0.0  # 0-1 scale
        
        # Interface simplification
        self.simplification_rules: List[SimplificationRule] = []
        self.active_simplifications: Dict[str, str] = {}
        self.interface_complexity = 1.0  # 0-1 scale, 0 = very simple
        
        # User preferences
        self.user_preferences = {
            "reminder_frequency": "normal",  # low, normal, high
            "interface_complexity": "moderate",
            "text_reading_speed": "normal",  # slow, normal, fast
            "attention_span": 15,  # minutes
            "preferred_interaction": "visual",  # visual, audio, haptic
            "error_tolerance": "high",  # low, medium, high
            "guidance_level": "detailed"  # minimal, basic, detailed
        }
        
        # Performance tracking
        self.stats = {
            "reminders_created": 0,
            "reminders_completed": 0,
            "simplifications_applied": 0,
            "guidance_requests": 0,
            "attention_breaks": 0,
            "successful_completions": 0,
            "average_task_completion_time": 0.0
        }
        
        # Load configuration and user profile
        self._load_configuration()
        self._load_user_profile()
        
        logger.info("🧠 Cognitive Assistant initialized")
    
    def _load_configuration(self):
        """Load cognitive assistant configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                if "user_preferences" in config:
                    self.user_preferences.update(config["user_preferences"])
                
                if "simplification_rules" in config:
                    self.simplification_rules = [
                        SimplificationRule(**rule) for rule in config["simplification_rules"]
                    ]
                
                logger.info("Cognitive configuration loaded")
            else:
                self._create_default_configuration()
                
        except Exception as e:
            logger.warning(f"Failed to load cognitive configuration: {e}")
            self._create_default_configuration()
    
    def _load_user_profile(self):
        """Load user cognitive profile"""
        try:
            if self.user_profile_path.exists():
                with open(self.user_profile_path, 'r') as f:
                    profile_data = json.load(f)
                
                # Load memory aids
                if "memory_aids" in profile_data:
                    for aid_data in profile_data["memory_aids"]:
                        aid = MemoryAid(
                            aid_id=aid_data["aid_id"],
                            title=aid_data["title"],
                            description=aid_data["description"],
                            reminder_time=datetime.fromisoformat(aid_data["reminder_time"]) if aid_data.get("reminder_time") else None,
                            category=aid_data["category"],
                            priority=aid_data["priority"],
                            completed=aid_data["completed"],
                            created_at=datetime.fromisoformat(aid_data["created_at"]),
                            last_accessed=datetime.fromisoformat(aid_data["last_accessed"]) if aid_data.get("last_accessed") else None,
                            access_count=aid_data.get("access_count", 0),
                            personalization_data=aid_data.get("personalization_data", {})
                        )
                        self.memory_aids[aid.aid_id] = aid
                
                # Load cognitive patterns
                if "cognitive_patterns" in profile_data:
                    self.user_patterns = [
                        CognitivePattern(**pattern) for pattern in profile_data["cognitive_patterns"]
                    ]
                
                logger.info(f"Loaded user profile with {len(self.memory_aids)} memory aids")
            else:
                self._create_default_user_profile()
                
        except Exception as e:
            logger.warning(f"Failed to load user profile: {e}")
            self._create_default_user_profile()
    
    def _create_default_configuration(self):
        """Create default configuration"""
        default_config = {
            "user_preferences": self.user_preferences,
            "support_categories": self.SUPPORT_CATEGORIES,
            "simplification_rules": [
                {
                    "rule_id": "reduce_menu_options",
                    "target_element": "navigation_menu",
                    "simplification_type": "reduce_options",
                    "condition": "complexity > 0.7",
                    "action": "show_only_essential",
                    "effectiveness_score": 0.8
                },
                {
                    "rule_id": "larger_buttons",
                    "target_element": "action_buttons",
                    "simplification_type": "larger_elements",
                    "condition": "user_preference.motor_difficulty",
                    "action": "increase_size_50_percent",
                    "effectiveness_score": 0.9
                }
            ]
        }
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default cognitive configuration: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    def _create_default_user_profile(self):
        """Create default user profile"""
        default_profile = {
            "memory_aids": [],
            "cognitive_patterns": [
                {
                    "pattern_id": "default_pattern",
                    "user_behavior": "new_user",
                    "preferred_interface": "simplified",
                    "attention_span": 15,
                    "best_time_periods": ["morning", "early_afternoon"],
                    "difficulty_areas": ["navigation", "complex_forms"],
                    "success_strategies": ["step_by_step", "visual_cues", "confirmation"],
                    "confidence_level": 0.5
                }
            ],
            "user_preferences": self.user_preferences
        }
        
        try:
            self.user_profile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_profile_path, 'w') as f:
                json.dump(default_profile, f, indent=2)
            
            logger.info(f"Created default user profile: {self.user_profile_path}")
        except Exception as e:
            logger.error(f"Failed to create default user profile: {e}")
    
    async def initialize_cognitive_services(self):
        """Initialize cognitive assistance services"""
        logger.info("🧠 Initializing cognitive assistance services")
        
        try:
            # Initialize memory management
            await self._initialize_memory_system()
            
            # Apply interface simplifications
            await self._apply_simplifications()
            
            # Start reminder monitoring
            await self._start_reminder_monitoring()
            
            logger.info("✅ Cognitive services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cognitive services: {e}")
            return False
    
    async def _initialize_memory_system(self):
        """Initialize memory aid system"""
        await asyncio.sleep(0.1)  # Simulate initialization
        
        # Check for overdue reminders
        current_time = datetime.now()
        for aid in self.memory_aids.values():
            if (aid.reminder_time and 
                aid.reminder_time <= current_time and 
                not aid.completed):
                self.active_reminders.append(aid.aid_id)
        
        logger.info(f"📝 Memory system initialized with {len(self.active_reminders)} active reminders")
    
    async def _apply_simplifications(self):
        """Apply interface simplifications"""
        applied_count = 0
        
        for rule in self.simplification_rules:
            if await self._should_apply_rule(rule):
                await self._apply_simplification_rule(rule)
                applied_count += 1
        
        self.stats["simplifications_applied"] += applied_count
        logger.info(f"✨ Applied {applied_count} interface simplifications")
    
    async def _should_apply_rule(self, rule: SimplificationRule) -> bool:
        """Check if simplification rule should be applied"""
        # Simple condition evaluation (would be more sophisticated in production)
        if "complexity" in rule.condition:
            return self.interface_complexity > 0.7
        elif "user_preference" in rule.condition:
            return True  # Assume user preferences are set
        return False
    
    async def _apply_simplification_rule(self, rule: SimplificationRule):
        """Apply a specific simplification rule"""
        self.active_simplifications[rule.target_element] = rule.action
        logger.info(f"Applied simplification: {rule.simplification_type} to {rule.target_element}")
    
    async def _start_reminder_monitoring(self):
        """Start monitoring for reminder notifications"""
        # This would run in the background in a real implementation
        logger.info("⏰ Reminder monitoring started")
    
    async def create_memory_aid(self, 
                              title: str, 
                              description: str, 
                              category: str = "task",
                              priority: int = 3,
                              reminder_time: Optional[datetime] = None) -> Dict:
        """Create a new memory aid"""
        start_time = time.time()
        
        try:
            aid_id = str(uuid.uuid4())
            
            memory_aid = MemoryAid(
                aid_id=aid_id,
                title=title,
                description=description,
                reminder_time=reminder_time,
                category=category,
                priority=priority,
                completed=False,
                created_at=datetime.now(),
                last_accessed=None,
                access_count=0,
                personalization_data={}
            )
            
            self.memory_aids[aid_id] = memory_aid
            
            # Schedule reminder if time is set
            if reminder_time and reminder_time > datetime.now():
                await self._schedule_reminder(aid_id, reminder_time)
            
            self.stats["reminders_created"] += 1
            
            # Save profile
            self._save_user_profile()
            
            creation_result = {
                "success": True,
                "aid_id": aid_id,
                "title": title,
                "category": category,
                "priority": priority,
                "reminder_scheduled": reminder_time is not None,
                "creation_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["reminder"]
            }
            
            logger.info(f"Created memory aid: {title}")
            
            return creation_result
            
        except Exception as e:
            logger.error(f"Memory aid creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "creation_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    async def _schedule_reminder(self, aid_id: str, reminder_time: datetime):
        """Schedule a reminder notification"""
        # In a real implementation, this would integrate with system notifications
        delay_seconds = (reminder_time - datetime.now()).total_seconds()
        
        if delay_seconds > 0:
            logger.info(f"Reminder scheduled for {reminder_time} (in {delay_seconds:.0f} seconds)")
        else:
            # Immediate reminder
            self.active_reminders.append(aid_id)
    
    async def get_memory_aids(self, 
                            category: Optional[str] = None,
                            completed: Optional[bool] = None,
                            priority_min: int = 1) -> Dict:
        """Get memory aids with optional filtering"""
        start_time = time.time()
        
        try:
            aids = list(self.memory_aids.values())
            
            # Apply filters
            if category:
                aids = [aid for aid in aids if aid.category == category]
            
            if completed is not None:
                aids = [aid for aid in aids if aid.completed == completed]
            
            aids = [aid for aid in aids if aid.priority >= priority_min]
            
            # Sort by priority and creation time
            aids.sort(key=lambda a: (-a.priority, a.created_at), reverse=True)
            
            # Convert to dict format
            aids_data = []
            for aid in aids:
                aid_dict = asdict(aid)
                aid_dict["created_at"] = aid.created_at.isoformat()
                if aid.reminder_time:
                    aid_dict["reminder_time"] = aid.reminder_time.isoformat()
                if aid.last_accessed:
                    aid_dict["last_accessed"] = aid.last_accessed.isoformat()
                aids_data.append(aid_dict)
            
            return {
                "success": True,
                "memory_aids": aids_data,
                "count": len(aids_data),
                "filters_applied": {
                    "category": category,
                    "completed": completed,
                    "priority_min": priority_min
                },
                "retrieval_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["reminder"]
            }
            
        except Exception as e:
            logger.error(f"Memory aid retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retrieval_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    async def complete_memory_aid(self, aid_id: str) -> Dict:
        """Mark memory aid as completed"""
        start_time = time.time()
        
        try:
            if aid_id not in self.memory_aids:
                return {
                    "success": False,
                    "error": f"Memory aid {aid_id} not found",
                    "completion_time": time.time() - start_time,
                    "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
                }
            
            aid = self.memory_aids[aid_id]
            aid.completed = True
            aid.last_accessed = datetime.now()
            aid.access_count += 1
            
            # Remove from active reminders
            if aid_id in self.active_reminders:
                self.active_reminders.remove(aid_id)
            
            self.completed_tasks.append(aid_id)
            self.stats["reminders_completed"] += 1
            self.stats["successful_completions"] += 1
            
            # Save profile
            self._save_user_profile()
            
            return {
                "success": True,
                "aid_id": aid_id,
                "title": aid.title,
                "completed_at": datetime.now().isoformat(),
                "completion_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["success"]
            }
            
        except Exception as e:
            logger.error(f"Memory aid completion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "completion_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    async def simplify_interface(self, complexity_level: str = None) -> Dict:
        """Apply interface simplifications"""
        start_time = time.time()
        
        try:
            if complexity_level:
                self.simplification_level = complexity_level
            
            # Apply simplifications based on level
            simplifications_applied = []
            
            if self.simplification_level == "maximum":
                self.interface_complexity = 0.2
                simplifications_applied = [
                    "hide_advanced_features",
                    "larger_buttons",
                    "reduced_menu_options",
                    "simplified_language",
                    "single_task_focus"
                ]
            elif self.simplification_level == "high":
                self.interface_complexity = 0.4
                simplifications_applied = [
                    "larger_buttons",
                    "reduced_menu_options",
                    "clearer_labels"
                ]
            elif self.simplification_level == "moderate":
                self.interface_complexity = 0.6
                simplifications_applied = [
                    "clearer_labels",
                    "better_organization"
                ]
            else:  # minimal
                self.interface_complexity = 0.8
                simplifications_applied = ["better_organization"]
            
            self.stats["simplifications_applied"] += len(simplifications_applied)
            
            return {
                "success": True,
                "simplification_level": self.simplification_level,
                "interface_complexity": self.interface_complexity,
                "simplifications_applied": simplifications_applied,
                "application_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["simplification"]
            }
            
        except Exception as e:
            logger.error(f"Interface simplification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "application_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    async def provide_guidance(self, task: str, user_context: Dict = None) -> Dict:
        """Provide step-by-step guidance for a task"""
        start_time = time.time()
        
        try:
            # Generate contextual guidance based on task and user patterns
            guidance_steps = await self._generate_guidance_steps(task, user_context)
            
            # Adapt guidance to user's cognitive patterns
            adapted_guidance = await self._adapt_guidance_to_user(guidance_steps)
            
            self.stats["guidance_requests"] += 1
            
            return {
                "success": True,
                "task": task,
                "guidance_steps": adapted_guidance,
                "step_count": len(adapted_guidance),
                "estimated_time": len(adapted_guidance) * 2,  # 2 minutes per step
                "guidance_level": self.user_preferences["guidance_level"],
                "generation_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["guidance"]
            }
            
        except Exception as e:
            logger.error(f"Guidance generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    async def _generate_guidance_steps(self, task: str, context: Dict = None) -> List[Dict]:
        """Generate step-by-step guidance for a task"""
        # Mock guidance generation based on common tasks
        guidance_templates = {
            "medication_reminder": [
                {"step": 1, "action": "Check medication label", "details": "Read the medication name and dosage"},
                {"step": 2, "action": "Verify timing", "details": "Check if it's the right time to take medication"},
                {"step": 3, "action": "Take medication", "details": "Take the prescribed amount with water"},
                {"step": 4, "action": "Mark as completed", "details": "Update your medication log"}
            ],
            "appointment_booking": [
                {"step": 1, "action": "Call healthcare provider", "details": "Use the phone number in your contacts"},
                {"step": 2, "action": "Provide information", "details": "Give your name and preferred appointment type"},
                {"step": 3, "action": "Check available times", "details": "Ask for times that work with your schedule"},
                {"step": 4, "action": "Confirm appointment", "details": "Repeat the date and time back to confirm"},
                {"step": 5, "action": "Add to calendar", "details": "Write down or add the appointment to your calendar"}
            ],
            "form_completion": [
                {"step": 1, "action": "Gather required documents", "details": "Collect ID, insurance card, and any other needed papers"},
                {"step": 2, "action": "Read instructions", "details": "Read through the form instructions carefully"},
                {"step": 3, "action": "Fill out basic information", "details": "Start with name, address, and contact information"},
                {"step": 4, "action": "Complete remaining sections", "details": "Fill out one section at a time"},
                {"step": 5, "action": "Review before submitting", "details": "Check all information is correct and complete"}
            ]
        }
        
        # Get guidance for task or provide generic steps
        if task.lower() in guidance_templates:
            return guidance_templates[task.lower()]
        else:
            return [
                {"step": 1, "action": "Break down the task", "details": "Identify the main steps needed"},
                {"step": 2, "action": "Gather what you need", "details": "Collect any required materials or information"},
                {"step": 3, "action": "Start with the first step", "details": "Focus on completing one step at a time"},
                {"step": 4, "action": "Check your progress", "details": "Review what you've completed so far"},
                {"step": 5, "action": "Complete and review", "details": "Finish the task and verify it's done correctly"}
            ]
    
    async def _adapt_guidance_to_user(self, guidance_steps: List[Dict]) -> List[Dict]:
        """Adapt guidance based on user's cognitive patterns"""
        adapted_steps = []
        
        for step in guidance_steps:
            adapted_step = step.copy()
            
            # Adjust detail level based on user preference
            if self.user_preferences["guidance_level"] == "minimal":
                adapted_step["details"] = step["action"]  # Just the action
            elif self.user_preferences["guidance_level"] == "detailed":
                # Add more context and tips
                adapted_step["tips"] = f"Take your time with this step. {step['details']}"
                adapted_step["estimated_time"] = "2-3 minutes"
            
            # Add visual cues for visual learners
            if self.user_preferences["preferred_interaction"] == "visual":
                adapted_step["visual_cue"] = "✓"
                adapted_step["progress_indicator"] = f"Step {step['step']} of {len(guidance_steps)}"
            
            adapted_steps.append(adapted_step)
        
        return adapted_steps
    
    async def check_attention_level(self) -> Dict:
        """Check and manage user's attention level"""
        start_time = time.time()
        
        try:
            # Simulate attention level assessment
            current_time = datetime.now()
            
            # Simple heuristic based on time and activity
            hour = current_time.hour
            if 6 <= hour <= 10:  # Morning
                self.current_attention_level = 8
            elif 10 <= hour <= 14:  # Late morning/early afternoon
                self.current_attention_level = 9
            elif 14 <= hour <= 16:  # Afternoon
                self.current_attention_level = 6
            elif 16 <= hour <= 19:  # Evening
                self.current_attention_level = 7
            else:  # Night
                self.current_attention_level = 4
            
            # Suggest break if attention is low
            suggestions = []
            if self.current_attention_level <= 5:
                suggestions = [
                    "Consider taking a short break",
                    "Try some light physical activity",
                    "Hydrate and have a healthy snack"
                ]
                self.stats["attention_breaks"] += 1
            
            return {
                "success": True,
                "attention_level": self.current_attention_level,
                "attention_description": self._get_attention_description(self.current_attention_level),
                "suggestions": suggestions,
                "optimal_for_tasks": self.current_attention_level >= 7,
                "check_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["attention"]
            }
            
        except Exception as e:
            logger.error(f"Attention level check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "check_time": time.time() - start_time,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    def _get_attention_description(self, level: int) -> str:
        """Get description for attention level"""
        if level >= 9:
            return "Excellent focus and attention"
        elif level >= 7:
            return "Good attention, suitable for complex tasks"
        elif level >= 5:
            return "Moderate attention, good for routine tasks"
        elif level >= 3:
            return "Low attention, consider simpler tasks"
        else:
            return "Very low attention, rest recommended"
    
    def update_cognitive_preferences(self, preferences: Dict) -> Dict:
        """Update cognitive assistance preferences"""
        try:
            updated_prefs = {}
            
            # Validate and update preferences
            valid_reminder_frequencies = ["low", "normal", "high"]
            if "reminder_frequency" in preferences and preferences["reminder_frequency"] in valid_reminder_frequencies:
                updated_prefs["reminder_frequency"] = preferences["reminder_frequency"]
            
            valid_complexities = ["minimal", "moderate", "high", "maximum"]
            if "interface_complexity" in preferences and preferences["interface_complexity"] in valid_complexities:
                updated_prefs["interface_complexity"] = preferences["interface_complexity"]
                self.simplification_level = preferences["interface_complexity"]
            
            if "attention_span" in preferences:
                span = int(preferences["attention_span"])
                if 5 <= span <= 60:  # 5 minutes to 1 hour
                    updated_prefs["attention_span"] = span
            
            valid_interactions = ["visual", "audio", "haptic"]
            if "preferred_interaction" in preferences and preferences["preferred_interaction"] in valid_interactions:
                updated_prefs["preferred_interaction"] = preferences["preferred_interaction"]
            
            valid_guidance_levels = ["minimal", "basic", "detailed"]
            if "guidance_level" in preferences and preferences["guidance_level"] in valid_guidance_levels:
                updated_prefs["guidance_level"] = preferences["guidance_level"]
            
            # Update preferences
            self.user_preferences.update(updated_prefs)
            
            # Save profile
            self._save_user_profile()
            
            return {
                "success": True,
                "updated_preferences": updated_prefs,
                "current_preferences": self.user_preferences,
                "symbolic_signature": self.COGNITIVE_SYMBOLS["success"]
            }
            
        except Exception as e:
            logger.error(f"Preference update failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbolic_signature": self.COGNITIVE_SYMBOLS["error"]
            }
    
    def _save_user_profile(self):
        """Save user profile to file"""
        try:
            profile_data = {
                "memory_aids": [],
                "cognitive_patterns": [asdict(pattern) for pattern in self.user_patterns],
                "user_preferences": self.user_preferences
            }
            
            # Convert memory aids to serializable format
            for aid in self.memory_aids.values():
                aid_dict = asdict(aid)
                aid_dict["created_at"] = aid.created_at.isoformat()
                if aid.reminder_time:
                    aid_dict["reminder_time"] = aid.reminder_time.isoformat()
                if aid.last_accessed:
                    aid_dict["last_accessed"] = aid.last_accessed.isoformat()
                profile_data["memory_aids"].append(aid_dict)
            
            self.user_profile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            logger.info("User cognitive profile saved")
            
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
    
    def get_cognitive_statistics(self) -> Dict:
        """Get cognitive assistant statistics"""
        stats = self.stats.copy()
        
        # Add current state information
        stats["active_memory_aids"] = len([aid for aid in self.memory_aids.values() if not aid.completed])
        stats["completed_memory_aids"] = len([aid for aid in self.memory_aids.values() if aid.completed])
        stats["active_reminders"] = len(self.active_reminders)
        stats["current_attention_level"] = self.current_attention_level
        stats["interface_complexity"] = self.interface_complexity
        stats["active_simplifications"] = len(self.active_simplifications)
        
        # Calculate completion rate
        total_aids = len(self.memory_aids)
        if total_aids > 0:
            stats["completion_rate"] = len(self.completed_tasks) / total_aids
        else:
            stats["completion_rate"] = 0.0
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Test core functionality
            test_aid = await self.create_memory_aid(
                title="Test reminder",
                description="Health check test",
                category="task"
            )
            
            if test_aid["success"]:
                # Clean up test aid
                await self.complete_memory_aid(test_aid["aid_id"])
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Cognitive assistant health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo cognitive assistant functionality"""
        print("🧠 Cognitive Assistant Demo")
        print("=" * 30)
        
        assistant = CognitiveAssistant()
        await assistant.initialize_cognitive_services()
        
        # Test memory aid creation
        print("\n📝 Creating memory aids...")
        
        aids = [
            ("Take morning medication", "Take blood pressure medication with breakfast", "medication", 5),
            ("Doctor appointment", "Visit Dr. Smith for checkup", "appointment", 4),
            ("Call pharmacy", "Refill prescription for diabetes medication", "task", 3)
        ]
        
        created_aids = []
        for title, description, category, priority in aids:
            result = await assistant.create_memory_aid(title, description, category, priority)
            if result["success"]:
                created_aids.append(result["aid_id"])
                print(f"   ✅ Created: {title}")
            else:
                print(f"   ❌ Failed: {title}")
        
        # Test memory aid retrieval
        print("\n📋 Retrieving memory aids...")
        aids_result = await assistant.get_memory_aids(completed=False)
        
        if aids_result["success"]:
            print(f"   ✅ Found {aids_result['count']} active memory aids")
            for aid in aids_result["memory_aids"][:2]:
                print(f"   💊 {aid['title']} (Priority: {aid['priority']})")
        
        # Test guidance provision
        print("\n🧭 Testing guidance...")
        guidance_result = await assistant.provide_guidance("medication_reminder")
        
        if guidance_result["success"]:
            print(f"   ✅ Generated {guidance_result['step_count']} guidance steps")
            print(f"   ⏱️  Estimated time: {guidance_result['estimated_time']} minutes")
            
            for step in guidance_result["guidance_steps"][:2]:
                print(f"   {step['step']}. {step['action']}: {step['details']}")
        
        # Test interface simplification
        print("\n✨ Testing interface simplification...")
        simplify_result = await assistant.simplify_interface("high")
        
        if simplify_result["success"]:
            print(f"   ✅ Applied simplification level: {simplify_result['simplification_level']}")
            print(f"   📊 Interface complexity: {simplify_result['interface_complexity']}")
            print(f"   🔧 Simplifications: {', '.join(simplify_result['simplifications_applied'])}")
        
        # Test attention level check
        print("\n👀 Checking attention level...")
        attention_result = await assistant.check_attention_level()
        
        if attention_result["success"]:
            print(f"   ✅ Attention level: {attention_result['attention_level']}/10")
            print(f"   📝 Description: {attention_result['attention_description']}")
            if attention_result["suggestions"]:
                print(f"   💡 Suggestions: {', '.join(attention_result['suggestions'])}")
        
        # Complete a memory aid
        if created_aids:
            print(f"\n✅ Completing memory aid...")
            complete_result = await assistant.complete_memory_aid(created_aids[0])
            if complete_result["success"]:
                print(f"   ✅ Completed: {complete_result['title']}")
        
        # Show statistics
        stats = assistant.get_cognitive_statistics()
        print(f"\n📊 Cognitive Assistant Statistics:")
        print(f"   Memory aids created: {stats['reminders_created']}")
        print(f"   Memory aids completed: {stats['reminders_completed']}")
        print(f"   Guidance requests: {stats['guidance_requests']}")
        print(f"   Current attention level: {stats['current_attention_level']}/10")
        print(f"   Completion rate: {stats['completion_rate']:.2f}")
        print(f"   Active simplifications: {stats['active_simplifications']}")
    
    asyncio.run(demo())
