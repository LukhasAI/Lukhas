#!/usr/bin/env python3
"""
Vision Assist - Accessibility support for users with visual impairments
Provides audio descriptions, screen reading, and visual enhancement features
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib
import uuid

logger = logging.getLogger(__name__)


@dataclass
class VisualElement:
    """Visual element description"""
    element_id: str
    element_type: str  # text, image, button, link, etc.
    text_content: str
    position: Tuple[int, int]  # x, y coordinates
    size: Tuple[int, int]  # width, height
    description: str
    importance: int  # 1-5 scale
    interactive: bool
    accessibility_label: Optional[str]


@dataclass
class AudioDescription:
    """Audio description for visual content"""
    description_id: str
    visual_element_id: str
    text_description: str
    audio_duration: float
    priority: int
    timestamp: float
    language: str
    voice_settings: Dict


class VisionAssistant:
    """
    Vision assistance system for users with visual impairments
    Provides screen reading, audio descriptions, and visual enhancements
    """
    
    # Screen reader modes
    READING_MODES = {
        "sequential": "Read content in order",
        "heading_nav": "Navigate by headings",
        "landmark_nav": "Navigate by landmarks", 
        "link_nav": "Navigate by links",
        "form_nav": "Navigate by form elements",
        "table_nav": "Navigate by tables"
    }
    
    # Voice settings for different content types
    VOICE_PROFILES = {
        "heading": {"rate": 0.8, "pitch": 1.2, "volume": 0.9},
        "text": {"rate": 1.0, "pitch": 1.0, "volume": 0.8},
        "link": {"rate": 0.9, "pitch": 1.1, "volume": 0.85},
        "button": {"rate": 0.9, "pitch": 1.15, "volume": 0.9},
        "alert": {"rate": 0.7, "pitch": 1.3, "volume": 1.0},
        "notification": {"rate": 1.1, "pitch": 0.9, "volume": 0.7}
    }
    
    # Visual enhancement options
    VISUAL_ENHANCEMENTS = {
        "high_contrast": "High contrast color scheme",
        "large_text": "Increased text size",
        "focus_highlight": "Enhanced focus indicators",
        "motion_reduction": "Reduced animations",
        "color_inversion": "Inverted colors",
        "zoom_enhancement": "Screen magnification"
    }
    
    # Accessibility symbols
    ACCESSIBILITY_SYMBOLS = {
        "reading": ["👁️", "📖", "🔊"],
        "describing": ["🎙️", "📸", "💬"],
        "navigating": ["🧭", "➡️", "📍"],
        "enhancing": ["🔍", "✨", "👁️"],
        "error": ["❌", "👁️", "⚠️"],
        "success": ["✅", "👁️", "🎯"]
    }
    
    def __init__(self, 
                 config_path: str = "config/vision_config.yaml",
                 voice_enabled: bool = True,
                 enhancement_level: str = "moderate"):
        
        self.config_path = Path(config_path)
        self.voice_enabled = voice_enabled
        self.enhancement_level = enhancement_level
        
        # Screen reading state
        self.current_mode = "sequential"
        self.reading_position = 0
        self.focus_history: List[str] = []
        self.visual_elements: Dict[str, VisualElement] = {}
        
        # Audio description
        self.audio_queue: List[AudioDescription] = []
        self.current_description: Optional[AudioDescription] = None
        self.description_history: List[AudioDescription] = []
        
        # User preferences
        self.user_preferences = {
            "speech_rate": 1.0,
            "speech_pitch": 1.0,
            "speech_volume": 0.8,
            "preferred_voice": "default",
            "reading_mode": "sequential",
            "verbosity_level": "normal",  # brief, normal, detailed
            "sound_notifications": True,
            "haptic_feedback": False
        }
        
        # Visual enhancements
        self.active_enhancements: List[str] = []
        self.contrast_ratio = 4.5  # WCAG AA standard
        self.zoom_level = 1.0
        
        # Performance tracking
        self.stats = {
            "descriptions_generated": 0,
            "navigation_commands": 0,
            "enhancement_activations": 0,
            "reading_sessions": 0,
            "average_description_time": 0.0
        }
        
        # Load configuration
        self._load_configuration()
        
        logger.info("👁️ Vision Assistant initialized")
    
    def _load_configuration(self):
        """Load vision assistant configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Load user preferences
                if "user_preferences" in config:
                    self.user_preferences.update(config["user_preferences"])
                
                # Load active enhancements
                if "active_enhancements" in config:
                    self.active_enhancements = config["active_enhancements"]
                
                logger.info("Vision assistant configuration loaded")
            else:
                self._create_default_configuration()
                
        except Exception as e:
            logger.warning(f"Failed to load vision configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default configuration file"""
        default_config = {
            "user_preferences": self.user_preferences,
            "active_enhancements": [],
            "voice_profiles": self.VOICE_PROFILES,
            "accessibility_settings": {
                "minimum_contrast_ratio": 4.5,
                "maximum_zoom_level": 5.0,
                "focus_indicator_width": 3,
                "animation_duration_limit": 0.2
            }
        }
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default vision configuration: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    async def initialize_vision_services(self):
        """Initialize vision assistance services"""
        logger.info("👁️ Initializing vision assistance services")
        
        try:
            # Initialize screen reader
            await self._initialize_screen_reader()
            
            # Initialize audio description engine
            await self._initialize_audio_engine()
            
            # Apply visual enhancements
            await self._apply_visual_enhancements()
            
            logger.info("✅ Vision services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vision services: {e}")
            return False
    
    async def _initialize_screen_reader(self):
        """Initialize screen reading capabilities"""
        await asyncio.sleep(0.1)  # Simulate initialization
        logger.info("📖 Screen reader initialized")
    
    async def _initialize_audio_engine(self):
        """Initialize audio description engine"""
        await asyncio.sleep(0.1)  # Simulate initialization
        logger.info("🎙️ Audio description engine initialized")
    
    async def _apply_visual_enhancements(self):
        """Apply active visual enhancements"""
        for enhancement in self.active_enhancements:
            await self._activate_enhancement(enhancement)
    
    async def scan_visual_content(self, content_data: Dict) -> List[VisualElement]:
        """Scan and analyze visual content for accessibility"""
        start_time = time.time()
        
        try:
            visual_elements = []
            
            # Simulate content analysis
            await asyncio.sleep(0.3)
            
            # Mock visual element detection
            if "text" in content_data:
                for i, text_item in enumerate(content_data["text"]):
                    element = VisualElement(
                        element_id=f"text_{i}",
                        element_type="text",
                        text_content=text_item.get("content", ""),
                        position=(text_item.get("x", 0), text_item.get("y", 0)),
                        size=(text_item.get("width", 100), text_item.get("height", 20)),
                        description=f"Text content: {text_item.get('content', '')[:50]}...",
                        importance=text_item.get("importance", 3),
                        interactive=False,
                        accessibility_label=text_item.get("alt_text")
                    )
                    visual_elements.append(element)
                    self.visual_elements[element.element_id] = element
            
            if "images" in content_data:
                for i, image_item in enumerate(content_data["images"]):
                    element = VisualElement(
                        element_id=f"image_{i}",
                        element_type="image",
                        text_content="",
                        position=(image_item.get("x", 0), image_item.get("y", 0)),
                        size=(image_item.get("width", 200), image_item.get("height", 150)),
                        description=image_item.get("alt_text", "Image without description"),
                        importance=4,
                        interactive=False,
                        accessibility_label=image_item.get("alt_text")
                    )
                    visual_elements.append(element)
                    self.visual_elements[element.element_id] = element
            
            if "buttons" in content_data:
                for i, button_item in enumerate(content_data["buttons"]):
                    element = VisualElement(
                        element_id=f"button_{i}",
                        element_type="button",
                        text_content=button_item.get("label", ""),
                        position=(button_item.get("x", 0), button_item.get("y", 0)),
                        size=(button_item.get("width", 80), button_item.get("height", 30)),
                        description=f"Button: {button_item.get('label', 'Unlabeled button')}",
                        importance=5,
                        interactive=True,
                        accessibility_label=button_item.get("aria_label")
                    )
                    visual_elements.append(element)
                    self.visual_elements[element.element_id] = element
            
            analysis_time = time.time() - start_time
            
            logger.info(f"Scanned {len(visual_elements)} visual elements in {analysis_time:.2f}s")
            
            return visual_elements
            
        except Exception as e:
            logger.error(f"Visual content scanning failed: {e}")
            return []
    
    async def generate_audio_description(self, visual_element: VisualElement) -> AudioDescription:
        """Generate audio description for a visual element"""
        start_time = time.time()
        
        try:
            # Generate contextual description
            description_text = await self._create_contextual_description(visual_element)
            
            # Calculate audio duration (rough estimate)
            words = len(description_text.split())
            speech_rate = self.user_preferences["speech_rate"]
            estimated_duration = (words / (150 * speech_rate))  # 150 WPM base rate
            
            # Create audio description
            description = AudioDescription(
                description_id=str(uuid.uuid4()),
                visual_element_id=visual_element.element_id,
                text_description=description_text,
                audio_duration=estimated_duration,
                priority=visual_element.importance,
                timestamp=start_time,
                language="en",
                voice_settings=self.VOICE_PROFILES.get(visual_element.element_type, self.VOICE_PROFILES["text"])
            )
            
            self.description_history.append(description)
            self.stats["descriptions_generated"] += 1
            
            # Update average description time
            description_time = time.time() - start_time
            self._update_average_description_time(description_time)
            
            logger.info(f"Generated audio description for {visual_element.element_id}")
            
            return description
            
        except Exception as e:
            logger.error(f"Audio description generation failed: {e}")
            
            # Return basic description on error
            return AudioDescription(
                description_id=str(uuid.uuid4()),
                visual_element_id=visual_element.element_id,
                text_description=f"Error describing {visual_element.element_type}",
                audio_duration=1.0,
                priority=1,
                timestamp=start_time,
                language="en",
                voice_settings=self.VOICE_PROFILES["text"]
            )
    
    async def _create_contextual_description(self, element: VisualElement) -> str:
        """Create contextual description based on element type and content"""
        descriptions = []
        
        # Element type announcement
        if element.element_type == "heading":
            level = element.text_content.count("#") if element.text_content.startswith("#") else 1
            descriptions.append(f"Heading level {level}")
        elif element.element_type == "button":
            descriptions.append("Button")
        elif element.element_type == "link":
            descriptions.append("Link")
        elif element.element_type == "image":
            descriptions.append("Image")
        elif element.element_type == "text":
            descriptions.append("Text")
        
        # Content description
        if element.text_content:
            if element.element_type == "button":
                descriptions.append(f'labeled "{element.text_content}"')
            elif element.element_type == "link":
                descriptions.append(f'to "{element.text_content}"')
            else:
                descriptions.append(f'"{element.text_content}"')
        
        # Accessibility label if available
        if element.accessibility_label and element.accessibility_label != element.text_content:
            descriptions.append(f"Description: {element.accessibility_label}")
        
        # Position context (if needed for detailed verbosity)
        if self.user_preferences["verbosity_level"] == "detailed":
            descriptions.append(f"at position {element.position[0]}, {element.position[1]}")
        
        # Interactive status
        if element.interactive:
            descriptions.append("interactive")
        
        return " ".join(descriptions)
    
    async def read_content(self, mode: str = None, start_position: int = 0) -> Dict:
        """Read content using specified mode"""
        if mode:
            self.current_mode = mode
        
        start_time = time.time()
        
        try:
            elements_to_read = []
            
            # Filter elements based on reading mode
            if self.current_mode == "sequential":
                elements_to_read = list(self.visual_elements.values())
            elif self.current_mode == "heading_nav":
                elements_to_read = [e for e in self.visual_elements.values() if e.element_type == "heading"]
            elif self.current_mode == "link_nav":
                elements_to_read = [e for e in self.visual_elements.values() if e.element_type == "link"]
            elif self.current_mode == "form_nav":
                elements_to_read = [e for e in self.visual_elements.values() if e.element_type in ["button", "input", "select"]]
            
            # Sort by reading order (position-based)
            elements_to_read.sort(key=lambda e: (e.position[1], e.position[0]))
            
            # Generate descriptions for elements
            descriptions = []
            for i, element in enumerate(elements_to_read[start_position:], start_position):
                description = await self.generate_audio_description(element)
                descriptions.append(description)
                
                if i >= start_position + 10:  # Limit to 10 elements per batch
                    break
            
            self.stats["reading_sessions"] += 1
            self.stats["navigation_commands"] += 1
            
            reading_result = {
                "success": True,
                "mode": self.current_mode,
                "elements_read": len(descriptions),
                "total_elements": len(elements_to_read),
                "start_position": start_position,
                "descriptions": [asdict(desc) for desc in descriptions],
                "reading_time": time.time() - start_time,
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["reading"]
            }
            
            logger.info(f"Read {len(descriptions)} elements in {self.current_mode} mode")
            
            return reading_result
            
        except Exception as e:
            logger.error(f"Content reading failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": self.current_mode,
                "reading_time": time.time() - start_time,
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
            }
    
    async def navigate_to_element(self, element_id: str) -> Dict:
        """Navigate to specific element"""
        start_time = time.time()
        
        try:
            if element_id not in self.visual_elements:
                return {
                    "success": False,
                    "error": f"Element {element_id} not found",
                    "navigation_time": time.time() - start_time,
                    "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
                }
            
            element = self.visual_elements[element_id]
            
            # Add to focus history
            self.focus_history.append(element_id)
            if len(self.focus_history) > 50:  # Limit history size
                self.focus_history = self.focus_history[-50:]
            
            # Generate description
            description = await self.generate_audio_description(element)
            
            self.stats["navigation_commands"] += 1
            
            return {
                "success": True,
                "element_id": element_id,
                "element_type": element.element_type,
                "description": asdict(description),
                "position": element.position,
                "interactive": element.interactive,
                "navigation_time": time.time() - start_time,
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["navigating"]
            }
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "navigation_time": time.time() - start_time,
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
            }
    
    async def activate_enhancement(self, enhancement: str) -> Dict:
        """Activate visual enhancement"""
        start_time = time.time()
        
        try:
            if enhancement not in self.VISUAL_ENHANCEMENTS:
                return {
                    "success": False,
                    "error": f"Unknown enhancement: {enhancement}",
                    "enhancement_time": time.time() - start_time,
                    "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
                }
            
            # Activate enhancement
            result = await self._activate_enhancement(enhancement)
            
            if result:
                if enhancement not in self.active_enhancements:
                    self.active_enhancements.append(enhancement)
                self.stats["enhancement_activations"] += 1
                
                return {
                    "success": True,
                    "enhancement": enhancement,
                    "description": self.VISUAL_ENHANCEMENTS[enhancement],
                    "active_enhancements": self.active_enhancements,
                    "enhancement_time": time.time() - start_time,
                    "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["enhancing"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to activate {enhancement}",
                    "enhancement_time": time.time() - start_time,
                    "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
                }
                
        except Exception as e:
            logger.error(f"Enhancement activation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "enhancement_time": time.time() - start_time,
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
            }
    
    async def _activate_enhancement(self, enhancement: str) -> bool:
        """Activate specific visual enhancement"""
        try:
            # Simulate enhancement activation
            await asyncio.sleep(0.1)
            
            if enhancement == "high_contrast":
                self.contrast_ratio = 7.0  # WCAG AAA standard
                logger.info("High contrast mode activated")
            elif enhancement == "large_text":
                logger.info("Large text mode activated")
            elif enhancement == "focus_highlight":
                logger.info("Enhanced focus indicators activated")
            elif enhancement == "motion_reduction":
                logger.info("Motion reduction activated")
            elif enhancement == "color_inversion":
                logger.info("Color inversion activated")
            elif enhancement == "zoom_enhancement":
                self.zoom_level = 1.5
                logger.info("Zoom enhancement activated")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate {enhancement}: {e}")
            return False
    
    def deactivate_enhancement(self, enhancement: str) -> Dict:
        """Deactivate visual enhancement"""
        try:
            if enhancement in self.active_enhancements:
                self.active_enhancements.remove(enhancement)
                
                # Reset enhancement-specific settings
                if enhancement == "high_contrast":
                    self.contrast_ratio = 4.5
                elif enhancement == "zoom_enhancement":
                    self.zoom_level = 1.0
                
                logger.info(f"Deactivated enhancement: {enhancement}")
                
                return {
                    "success": True,
                    "enhancement": enhancement,
                    "active_enhancements": self.active_enhancements,
                    "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["success"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Enhancement {enhancement} is not active",
                    "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
                }
                
        except Exception as e:
            logger.error(f"Enhancement deactivation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
            }
    
    def update_preferences(self, preferences: Dict) -> Dict:
        """Update user preferences"""
        try:
            # Validate preferences
            valid_prefs = {}
            
            if "speech_rate" in preferences:
                rate = float(preferences["speech_rate"])
                if 0.1 <= rate <= 3.0:
                    valid_prefs["speech_rate"] = rate
            
            if "speech_pitch" in preferences:
                pitch = float(preferences["speech_pitch"])
                if 0.5 <= pitch <= 2.0:
                    valid_prefs["speech_pitch"] = pitch
            
            if "speech_volume" in preferences:
                volume = float(preferences["speech_volume"])
                if 0.0 <= volume <= 1.0:
                    valid_prefs["speech_volume"] = volume
            
            if "reading_mode" in preferences:
                mode = preferences["reading_mode"]
                if mode in self.READING_MODES:
                    valid_prefs["reading_mode"] = mode
                    self.current_mode = mode
            
            if "verbosity_level" in preferences:
                level = preferences["verbosity_level"]
                if level in ["brief", "normal", "detailed"]:
                    valid_prefs["verbosity_level"] = level
            
            # Update preferences
            self.user_preferences.update(valid_prefs)
            
            # Save configuration
            self._save_configuration()
            
            return {
                "success": True,
                "updated_preferences": valid_prefs,
                "current_preferences": self.user_preferences,
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["success"]
            }
            
        except Exception as e:
            logger.error(f"Preference update failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbolic_signature": self.ACCESSIBILITY_SYMBOLS["error"]
            }
    
    def _save_configuration(self):
        """Save current configuration to file"""
        try:
            config = {
                "user_preferences": self.user_preferences,
                "active_enhancements": self.active_enhancements,
                "voice_profiles": self.VOICE_PROFILES
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Vision configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _update_average_description_time(self, description_time: float):
        """Update average description generation time"""
        current_avg = self.stats["average_description_time"]
        descriptions_count = self.stats["descriptions_generated"]
        
        if descriptions_count == 1:
            self.stats["average_description_time"] = description_time
        else:
            new_avg = ((current_avg * (descriptions_count - 1)) + description_time) / descriptions_count
            self.stats["average_description_time"] = new_avg
    
    def get_vision_statistics(self) -> Dict:
        """Get vision assistant statistics"""
        stats = self.stats.copy()
        
        # Add current state information
        stats["active_enhancements"] = self.active_enhancements
        stats["current_reading_mode"] = self.current_mode
        stats["visual_elements_count"] = len(self.visual_elements)
        stats["focus_history_length"] = len(self.focus_history)
        stats["description_queue_length"] = len(self.audio_queue)
        
        # Calculate efficiency metrics
        if stats["reading_sessions"] > 0:
            stats["average_elements_per_session"] = stats["descriptions_generated"] / stats["reading_sessions"]
        else:
            stats["average_elements_per_session"] = 0
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Test core functionality
            test_element = VisualElement(
                element_id="test",
                element_type="text",
                text_content="Test content",
                position=(0, 0),
                size=(100, 20),
                description="Test element",
                importance=1,
                interactive=False,
                accessibility_label=None
            )
            
            # Test description generation
            description = await self.generate_audio_description(test_element)
            
            return description is not None
            
        except Exception as e:
            logger.error(f"Vision assistant health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo vision assistant functionality"""
        print("👁️ Vision Assistant Demo")
        print("=" * 30)
        
        assistant = VisionAssistant()
        await assistant.initialize_vision_services()
        
        # Test content scanning
        print("\n📖 Scanning test content...")
        test_content = {
            "text": [
                {"content": "Welcome to the application", "x": 10, "y": 20, "importance": 4},
                {"content": "This is a paragraph of text", "x": 10, "y": 50, "importance": 3}
            ],
            "images": [
                {"alt_text": "Company logo", "x": 200, "y": 10, "width": 100, "height": 50}
            ],
            "buttons": [
                {"label": "Submit", "x": 10, "y": 100, "aria_label": "Submit form"},
                {"label": "Cancel", "x": 100, "y": 100, "aria_label": "Cancel operation"}
            ]
        }
        
        elements = await assistant.scan_visual_content(test_content)
        print(f"   ✅ Found {len(elements)} visual elements")
        
        # Test reading content
        print("\n🔊 Reading content in sequential mode...")
        reading_result = await assistant.read_content("sequential")
        
        if reading_result["success"]:
            print(f"   ✅ Read {reading_result['elements_read']} elements")
            print(f"   ⏱️  Reading time: {reading_result['reading_time']:.2f}s")
            
            # Show first description
            if reading_result["descriptions"]:
                first_desc = reading_result["descriptions"][0]
                print(f"   💬 First description: \"{first_desc['text_description']}\"")
        
        # Test navigation
        print("\n🧭 Testing navigation...")
        if elements:
            nav_result = await assistant.navigate_to_element(elements[0].element_id)
            if nav_result["success"]:
                print(f"   ✅ Navigated to {nav_result['element_type']}")
                print(f"   💬 Description: \"{nav_result['description']['text_description']}\"")
        
        # Test visual enhancements
        print("\n✨ Testing visual enhancements...")
        for enhancement in ["high_contrast", "large_text", "focus_highlight"]:
            result = await assistant.activate_enhancement(enhancement)
            if result["success"]:
                print(f"   ✅ Activated: {enhancement}")
            else:
                print(f"   ❌ Failed: {enhancement}")
        
        print(f"   📊 Active enhancements: {len(assistant.active_enhancements)}")
        
        # Test preference updates
        print("\n⚙️ Testing preference updates...")
        prefs_result = assistant.update_preferences({
            "speech_rate": 1.2,
            "verbosity_level": "detailed",
            "reading_mode": "heading_nav"
        })
        
        if prefs_result["success"]:
            print(f"   ✅ Updated {len(prefs_result['updated_preferences'])} preferences")
        
        # Show statistics
        stats = assistant.get_vision_statistics()
        print(f"\n📊 Vision Assistant Statistics:")
        print(f"   Descriptions generated: {stats['descriptions_generated']}")
        print(f"   Navigation commands: {stats['navigation_commands']}")
        print(f"   Enhancement activations: {stats['enhancement_activations']}")
        print(f"   Average description time: {stats['average_description_time']:.3f}s")
        print(f"   Active enhancements: {', '.join(stats['active_enhancements'])}")
    
    asyncio.run(demo())
