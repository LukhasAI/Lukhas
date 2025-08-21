#!/usr/bin/env python3
"""
Multi-Language Support - Internationalization and localization for accessibility
Provides language detection, translation, and culturally appropriate assistance
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
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LanguageProfile:
    """User language profile"""
    profile_id: str
    primary_language: str
    secondary_languages: List[str]
    preferred_script: str  # latin, cyrillic, arabic, etc.
    reading_direction: str  # ltr, rtl
    proficiency_levels: Dict[str, str]  # language -> beginner/intermediate/advanced/native
    cultural_context: str
    accessibility_needs: List[str]


@dataclass
class TranslationRequest:
    """Translation request"""
    request_id: str
    source_text: str
    source_language: str
    target_language: str
    context: str
    priority: int
    timestamp: float
    translation_result: Optional[str]
    confidence: float
    method_used: str


@dataclass
class CulturalAdaptation:
    """Cultural adaptation for content"""
    adaptation_id: str
    content_type: str
    original_content: Dict
    adapted_content: Dict
    cultural_context: str
    adaptation_rules: List[str]
    effectiveness_score: float


class MultiLanguageSupport:
    """
    Multi-language support system for accessibility
    Provides translation, localization, and cultural adaptation
    """
    
    # Supported languages with metadata
    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "native_name": "English",
            "script": "latin",
            "direction": "ltr",
            "regions": ["US", "UK", "CA", "AU", "NZ"],
            "accessibility_support": "full"
        },
        "es": {
            "name": "Spanish",
            "native_name": "Español",
            "script": "latin",
            "direction": "ltr",
            "regions": ["ES", "MX", "AR", "CO", "PE"],
            "accessibility_support": "full"
        },
        "fr": {
            "name": "French",
            "native_name": "Français",
            "script": "latin",
            "direction": "ltr",
            "regions": ["FR", "CA", "BE", "CH"],
            "accessibility_support": "full"
        },
        "de": {
            "name": "German",
            "native_name": "Deutsch",
            "script": "latin",
            "direction": "ltr",
            "regions": ["DE", "AT", "CH"],
            "accessibility_support": "full"
        },
        "zh": {
            "name": "Chinese",
            "native_name": "中文",
            "script": "han",
            "direction": "ltr",
            "regions": ["CN", "TW", "HK", "SG"],
            "accessibility_support": "partial"
        },
        "ar": {
            "name": "Arabic",
            "native_name": "العربية",
            "script": "arabic",
            "direction": "rtl",
            "regions": ["SA", "AE", "EG", "MA"],
            "accessibility_support": "partial"
        },
        "pt": {
            "name": "Portuguese",
            "native_name": "Português",
            "script": "latin",
            "direction": "ltr",
            "regions": ["PT", "BR"],
            "accessibility_support": "full"
        },
        "ru": {
            "name": "Russian",
            "native_name": "Русский",
            "script": "cyrillic",
            "direction": "ltr",
            "regions": ["RU", "BY", "KZ"],
            "accessibility_support": "partial"
        },
        "ja": {
            "name": "Japanese",
            "native_name": "日本語",
            "script": "mixed",
            "direction": "ltr",
            "regions": ["JP"],
            "accessibility_support": "partial"
        },
        "it": {
            "name": "Italian",
            "native_name": "Italiano",
            "script": "latin",
            "direction": "ltr",
            "regions": ["IT"],
            "accessibility_support": "full"
        }
    }
    
    # Cultural contexts and their characteristics
    CULTURAL_CONTEXTS = {
        "western": {
            "communication_style": "direct",
            "formality_level": "moderate",
            "health_privacy": "high",
            "family_involvement": "limited",
            "authority_respect": "moderate"
        },
        "latin": {
            "communication_style": "warm",
            "formality_level": "moderate",
            "health_privacy": "moderate", 
            "family_involvement": "high",
            "authority_respect": "high"
        },
        "asian": {
            "communication_style": "indirect",
            "formality_level": "high",
            "health_privacy": "high",
            "family_involvement": "high",
            "authority_respect": "very_high"
        },
        "middle_eastern": {
            "communication_style": "formal",
            "formality_level": "high",
            "health_privacy": "very_high",
            "family_involvement": "very_high",
            "authority_respect": "very_high"
        },
        "african": {
            "communication_style": "community_oriented",
            "formality_level": "moderate",
            "health_privacy": "low",
            "family_involvement": "very_high",
            "authority_respect": "high"
        }
    }
    
    # Language symbols
    LANGUAGE_SYMBOLS = {
        "translation": ["🌐", "💬", "🔄"],
        "detection": ["🔍", "🌍", "📝"],
        "adaptation": ["🎭", "🌍", "✨"],
        "success": ["✅", "🌐", "💫"],
        "error": ["❌", "🌐", "⚠️"],
        "multilingual": ["🗣️", "🌍", "🔤"]
    }
    
    def __init__(self, 
                 config_path: str = "config/language_config.yaml",
                 user_profile_path: str = "data/user_language_profile.json",
                 translation_cache_path: str = "data/translation_cache.json"):
        
        self.config_path = Path(config_path)
        self.user_profile_path = Path(user_profile_path)
        self.translation_cache_path = Path(translation_cache_path)
        
        # User language profile
        self.user_profile: Optional[LanguageProfile] = None
        self.detected_languages: List[str] = []
        
        # Translation management
        self.translation_cache: Dict[str, str] = {}
        self.translation_history: List[TranslationRequest] = []
        self.active_translations: Dict[str, TranslationRequest] = {}
        
        # Cultural adaptation
        self.cultural_adaptations: List[CulturalAdaptation] = []
        self.adaptation_rules: Dict[str, List[str]] = {}
        
        # Configuration
        self.enabled_languages = ["en", "es", "fr", "de", "pt"]
        self.auto_detect_language = True
        self.translation_quality = "high"  # low, medium, high
        self.cultural_adaptation_level = "moderate"  # minimal, moderate, high
        
        # Performance tracking
        self.stats = {
            "translations_performed": 0,
            "successful_translations": 0,
            "language_detections": 0,
            "cultural_adaptations": 0,
            "cache_hits": 0,
            "average_translation_time": 0.0,
            "supported_language_pairs": 0
        }
        
        # Load configuration and data
        self._load_configuration()
        self._load_user_profile()
        self._load_translation_cache()
        
        logger.info("🌐 Multi-Language Support initialized")
    
    def _load_configuration(self):
        """Load language configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                if "enabled_languages" in config:
                    self.enabled_languages = config["enabled_languages"]
                
                if "translation_settings" in config:
                    settings = config["translation_settings"]
                    self.auto_detect_language = settings.get("auto_detect", True)
                    self.translation_quality = settings.get("quality", "high")
                    self.cultural_adaptation_level = settings.get("cultural_adaptation", "moderate")
                
                if "adaptation_rules" in config:
                    self.adaptation_rules = config["adaptation_rules"]
                
                logger.info("Language configuration loaded")
            else:
                self._create_default_configuration()
                
        except Exception as e:
            logger.warning(f"Failed to load language configuration: {e}")
            self._create_default_configuration()
    
    def _load_user_profile(self):
        """Load user language profile"""
        try:
            if self.user_profile_path.exists():
                with open(self.user_profile_path, 'r') as f:
                    profile_data = json.load(f)
                
                self.user_profile = LanguageProfile(**profile_data)
                logger.info(f"Loaded user language profile: {self.user_profile.primary_language}")
            else:
                self._create_default_user_profile()
                
        except Exception as e:
            logger.warning(f"Failed to load user language profile: {e}")
            self._create_default_user_profile()
    
    def _load_translation_cache(self):
        """Load translation cache"""
        try:
            if self.translation_cache_path.exists():
                with open(self.translation_cache_path, 'r') as f:
                    self.translation_cache = json.load(f)
                
                logger.info(f"Loaded {len(self.translation_cache)} cached translations")
            
        except Exception as e:
            logger.warning(f"Failed to load translation cache: {e}")
    
    def _create_default_configuration(self):
        """Create default language configuration"""
        default_config = {
            "enabled_languages": self.enabled_languages,
            "translation_settings": {
                "auto_detect": True,
                "quality": "high",
                "cultural_adaptation": "moderate",
                "cache_translations": True
            },
            "accessibility_settings": {
                "screen_reader_support": True,
                "voice_navigation": True,
                "simplified_language": False,
                "cultural_sensitivity": True
            },
            "adaptation_rules": {
                "medical": [
                    "use_formal_language",
                    "respect_privacy_customs",
                    "include_family_context",
                    "consider_authority_hierarchy"
                ],
                "emergency": [
                    "use_clear_simple_language",
                    "respect_cultural_taboos",
                    "adapt_contact_methods"
                ]
            }
        }
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default language configuration: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    def _create_default_user_profile(self):
        """Create default user language profile"""
        default_profile = LanguageProfile(
            profile_id=str(uuid.uuid4()),
            primary_language="en",
            secondary_languages=[],
            preferred_script="latin",
            reading_direction="ltr",
            proficiency_levels={"en": "native"},
            cultural_context="western",
            accessibility_needs=[]
        )
        
        self.user_profile = default_profile
        self._save_user_profile()
    
    async def initialize_language_services(self):
        """Initialize language support services"""
        logger.info("🌐 Initializing language support services")
        
        try:
            # Initialize translation services
            await self._initialize_translation_engine()
            
            # Initialize language detection
            await self._initialize_language_detection()
            
            # Load cultural adaptation rules
            await self._load_cultural_adaptations()
            
            # Calculate supported language pairs
            enabled_count = len(self.enabled_languages)
            self.stats["supported_language_pairs"] = enabled_count * (enabled_count - 1)
            
            logger.info("✅ Language services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize language services: {e}")
            return False
    
    async def _initialize_translation_engine(self):
        """Initialize translation engine"""
        await asyncio.sleep(0.1)  # Simulate initialization
        logger.info("🔄 Translation engine initialized")
    
    async def _initialize_language_detection(self):
        """Initialize language detection"""
        await asyncio.sleep(0.1)  # Simulate initialization
        logger.info("🔍 Language detection initialized")
    
    async def _load_cultural_adaptations(self):
        """Load cultural adaptation rules"""
        await asyncio.sleep(0.1)  # Simulate loading
        logger.info("🎭 Cultural adaptation rules loaded")
    
    async def detect_language(self, text: str) -> Dict:
        """Detect language of text"""
        start_time = time.time()
        
        try:
            # Simulate language detection
            await asyncio.sleep(0.1)
            
            # Mock language detection based on common words/patterns
            detected_language = self._mock_language_detection(text)
            confidence = self._calculate_detection_confidence(text, detected_language)
            
            self.stats["language_detections"] += 1
            
            if detected_language not in self.detected_languages:
                self.detected_languages.append(detected_language)
            
            return {
                "success": True,
                "detected_language": detected_language,
                "language_name": self.SUPPORTED_LANGUAGES.get(detected_language, {}).get("name", "Unknown"),
                "confidence": confidence,
                "supported": detected_language in self.SUPPORTED_LANGUAGES,
                "script": self.SUPPORTED_LANGUAGES.get(detected_language, {}).get("script", "unknown"),
                "direction": self.SUPPORTED_LANGUAGES.get(detected_language, {}).get("direction", "ltr"),
                "detection_time": time.time() - start_time,
                "symbolic_signature": self.LANGUAGE_SYMBOLS["detection"]
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "detection_time": time.time() - start_time,
                "symbolic_signature": self.LANGUAGE_SYMBOLS["error"]
            }
    
    def _mock_language_detection(self, text: str) -> str:
        """Mock language detection based on text patterns"""
        text_lower = text.lower()
        
        # Simple keyword-based detection
        language_keywords = {
            "es": ["el", "la", "de", "que", "y", "en", "un", "es", "se", "no", "te", "lo", "le", "da", "su", "por", "son", "con", "para", "está", "son", "del", "las", "una"],
            "fr": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir", "que", "pour", "dans", "ce", "son", "une", "sur", "avec", "ne", "se", "pas", "tout", "plus", "par"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich", "des", "auf", "für", "ist", "im", "dem", "nicht", "ein", "eine", "als", "auch", "es", "an"],
            "pt": ["o", "de", "e", "do", "da", "em", "um", "para", "é", "com", "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "foi", "ao"],
            "it": ["di", "che", "e", "la", "il", "un", "a", "per", "non", "una", "in", "con", "i", "da", "su", "le", "si", "lo", "come", "del", "questo", "ma", "alla", "sono"],
            "ar": ["في", "من", "إلى", "على", "هذا", "هذه", "التي", "التي", "كان", "كانت", "يكون", "تكون", "كل", "بعض", "عند", "عندما", "حيث", "كيف", "لماذا", "ماذا"],
            "zh": ["的", "一", "是", "在", "不", "了", "有", "和", "人", "这", "中", "大", "为", "上", "个", "国", "我", "以", "要", "他", "时", "来", "用", "们"],
            "ru": ["в", "и", "не", "на", "я", "быть", "он", "с", "что", "а", "по", "это", "она", "этот", "к", "но", "они", "мы", "как", "из", "за", "то", "же"],
            "ja": ["の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ", "ある", "いる", "も", "する", "から", "な", "こと", "として", "い", "や", "れる"]
        }
        
        # Count matches for each language
        scores = {}
        for lang, keywords in language_keywords.items():
            scores[lang] = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Return language with highest score, default to English
        if scores:
            best_match = max(scores, key=scores.get)
            if scores[best_match] > 0:
                return best_match
        
        return "en"  # Default to English
    
    def _calculate_detection_confidence(self, text: str, detected_language: str) -> float:
        """Calculate confidence score for language detection"""
        # Simple confidence calculation based on text length and pattern matches
        text_length = len(text.split())
        
        if text_length < 3:
            return 0.3
        elif text_length < 10:
            return 0.6
        elif text_length < 20:
            return 0.8
        else:
            return 0.9
    
    async def translate_text(self, 
                           text: str, 
                           target_language: str, 
                           source_language: str = None,
                           context: str = "general") -> Dict:
        """Translate text to target language"""
        start_time = time.time()
        
        try:
            # Auto-detect source language if not provided
            if not source_language and self.auto_detect_language:
                detection_result = await self.detect_language(text)
                if detection_result["success"]:
                    source_language = detection_result["detected_language"]
                else:
                    source_language = "en"  # Default fallback
            elif not source_language:
                source_language = self.user_profile.primary_language if self.user_profile else "en"
            
            # Check if translation is needed
            if source_language == target_language:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 1.0,
                    "cached": False,
                    "translation_time": time.time() - start_time,
                    "symbolic_signature": self.LANGUAGE_SYMBOLS["success"]
                }
            
            # Check cache first
            cache_key = self._generate_translation_cache_key(text, source_language, target_language)
            if cache_key in self.translation_cache:
                self.stats["cache_hits"] += 1
                
                return {
                    "success": True,
                    "translated_text": self.translation_cache[cache_key],
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 0.95,  # Cached translations have high confidence
                    "cached": True,
                    "translation_time": time.time() - start_time,
                    "symbolic_signature": self.LANGUAGE_SYMBOLS["translation"]
                }
            
            # Perform translation
            translation_result = await self._perform_translation(text, source_language, target_language, context)
            
            # Cache the result
            if translation_result["success"]:
                self.translation_cache[cache_key] = translation_result["translated_text"]
                self._save_translation_cache()
            
            # Create translation request record
            request = TranslationRequest(
                request_id=str(uuid.uuid4()),
                source_text=text,
                source_language=source_language,
                target_language=target_language,
                context=context,
                priority=1,
                timestamp=start_time,
                translation_result=translation_result.get("translated_text"),
                confidence=translation_result.get("confidence", 0.0),
                method_used="mock_engine"
            )
            
            self.translation_history.append(request)
            self.stats["translations_performed"] += 1
            
            if translation_result["success"]:
                self.stats["successful_translations"] += 1
            
            self._update_average_translation_time(time.time() - start_time)
            
            translation_result["translation_time"] = time.time() - start_time
            translation_result["cached"] = False
            translation_result["symbolic_signature"] = self.LANGUAGE_SYMBOLS["translation"]
            
            logger.info(f"Translated text from {source_language} to {target_language}")
            
            return translation_result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_language": source_language,
                "target_language": target_language,
                "translation_time": time.time() - start_time,
                "symbolic_signature": self.LANGUAGE_SYMBOLS["error"]
            }
    
    async def _perform_translation(self, text: str, source_lang: str, target_lang: str, context: str) -> Dict:
        """Perform the actual translation"""
        # Simulate translation delay
        await asyncio.sleep(0.2)
        
        # Mock translation based on context and language pairs
        mock_translations = {
            ("en", "es"): {
                "Hello": "Hola",
                "Thank you": "Gracias",
                "Please": "Por favor",
                "Help": "Ayuda",
                "Emergency": "Emergencia",
                "Medicine": "Medicina",
                "Doctor": "Doctor",
                "Hospital": "Hospital",
                "Pain": "Dolor",
                "I need help": "Necesito ayuda"
            },
            ("en", "fr"): {
                "Hello": "Bonjour",
                "Thank you": "Merci",
                "Please": "S'il vous plaît",
                "Help": "Aide",
                "Emergency": "Urgence",
                "Medicine": "Médicament",
                "Doctor": "Docteur",
                "Hospital": "Hôpital",
                "Pain": "Douleur",
                "I need help": "J'ai besoin d'aide"
            },
            ("en", "de"): {
                "Hello": "Hallo",
                "Thank you": "Danke",
                "Please": "Bitte",
                "Help": "Hilfe",
                "Emergency": "Notfall",
                "Medicine": "Medizin",
                "Doctor": "Arzt",
                "Hospital": "Krankenhaus",
                "Pain": "Schmerz",
                "I need help": "Ich brauche Hilfe"
            }
        }
        
        # Try to find exact match
        translation_dict = mock_translations.get((source_lang, target_lang), {})
        if text in translation_dict:
            return {
                "success": True,
                "translated_text": translation_dict[text],
                "confidence": 0.9,
                "method": "dictionary_lookup"
            }
        
        # Generate mock translation for unknown text
        if target_lang == "es":
            translated = f"[ES] {text}"
        elif target_lang == "fr":
            translated = f"[FR] {text}"
        elif target_lang == "de":
            translated = f"[DE] {text}"
        elif target_lang == "pt":
            translated = f"[PT] {text}"
        else:
            translated = f"[{target_lang.upper()}] {text}"
        
        return {
            "success": True,
            "translated_text": translated,
            "confidence": 0.7,
            "method": "mock_translation"
        }
    
    def _generate_translation_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        key_string = f"{source_lang}_{target_lang}_{text}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def adapt_content_culturally(self, content: Dict, target_culture: str) -> Dict:
        """Adapt content for cultural context"""
        start_time = time.time()
        
        try:
            cultural_context = self.CULTURAL_CONTEXTS.get(target_culture, self.CULTURAL_CONTEXTS["western"])
            
            adapted_content = content.copy()
            adaptations_made = []
            
            # Apply cultural adaptations based on context
            if cultural_context["communication_style"] == "formal":
                adaptations_made.append("formal_language")
                if "message" in adapted_content:
                    adapted_content["message"] = self._make_formal(adapted_content["message"])
            
            if cultural_context["health_privacy"] == "very_high":
                adaptations_made.append("enhanced_privacy")
                adapted_content["privacy_notice"] = "Your health information is strictly confidential"
            
            if cultural_context["family_involvement"] == "high":
                adaptations_made.append("family_context")
                adapted_content["family_note"] = "You may wish to discuss this with your family"
            
            if cultural_context["authority_respect"] == "very_high":
                adaptations_made.append("authority_respect")
                if "instructions" in adapted_content:
                    adapted_content["instructions"] = self._add_authority_respect(adapted_content["instructions"])
            
            # Create adaptation record
            adaptation = CulturalAdaptation(
                adaptation_id=str(uuid.uuid4()),
                content_type=content.get("type", "general"),
                original_content=content,
                adapted_content=adapted_content,
                cultural_context=target_culture,
                adaptation_rules=adaptations_made,
                effectiveness_score=0.8
            )
            
            self.cultural_adaptations.append(adaptation)
            self.stats["cultural_adaptations"] += 1
            
            return {
                "success": True,
                "original_content": content,
                "adapted_content": adapted_content,
                "cultural_context": target_culture,
                "adaptations_made": adaptations_made,
                "adaptation_time": time.time() - start_time,
                "symbolic_signature": self.LANGUAGE_SYMBOLS["adaptation"]
            }
            
        except Exception as e:
            logger.error(f"Cultural adaptation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "adaptation_time": time.time() - start_time,
                "symbolic_signature": self.LANGUAGE_SYMBOLS["error"]
            }
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal"""
        # Simple formalization rules
        replacements = {
            "Hi": "Greetings",
            "Hey": "Hello",
            "Thanks": "Thank you",
            "OK": "Very well",
            "Yeah": "Yes"
        }
        
        for informal, formal in replacements.items():
            text = text.replace(informal, formal)
        
        return text
    
    def _add_authority_respect(self, text: str) -> str:
        """Add authority respect to instructions"""
        if not text.endswith("."):
            text += "."
        
        return f"Please {text.lower()}" if not text.lower().startswith("please") else text
    
    def update_user_language_profile(self, profile_updates: Dict) -> Dict:
        """Update user language profile"""
        try:
            if not self.user_profile:
                self._create_default_user_profile()
            
            updated_fields = {}
            
            # Update primary language
            if "primary_language" in profile_updates:
                lang = profile_updates["primary_language"]
                if lang in self.SUPPORTED_LANGUAGES:
                    self.user_profile.primary_language = lang
                    updated_fields["primary_language"] = lang
            
            # Update secondary languages
            if "secondary_languages" in profile_updates:
                langs = [lang for lang in profile_updates["secondary_languages"] if lang in self.SUPPORTED_LANGUAGES]
                self.user_profile.secondary_languages = langs
                updated_fields["secondary_languages"] = langs
            
            # Update cultural context
            if "cultural_context" in profile_updates:
                context = profile_updates["cultural_context"]
                if context in self.CULTURAL_CONTEXTS:
                    self.user_profile.cultural_context = context
                    updated_fields["cultural_context"] = context
            
            # Update accessibility needs
            if "accessibility_needs" in profile_updates:
                needs = profile_updates["accessibility_needs"]
                if isinstance(needs, list):
                    self.user_profile.accessibility_needs = needs
                    updated_fields["accessibility_needs"] = needs
            
            # Save updated profile
            self._save_user_profile()
            
            return {
                "success": True,
                "updated_fields": updated_fields,
                "current_profile": asdict(self.user_profile),
                "symbolic_signature": self.LANGUAGE_SYMBOLS["success"]
            }
            
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbolic_signature": self.LANGUAGE_SYMBOLS["error"]
            }
    
    def _save_user_profile(self):
        """Save user language profile"""
        try:
            if self.user_profile:
                self.user_profile_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.user_profile_path, 'w') as f:
                    json.dump(asdict(self.user_profile), f, indent=2)
                
                logger.info("User language profile saved")
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
    
    def _save_translation_cache(self):
        """Save translation cache"""
        try:
            self.translation_cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.translation_cache_path, 'w') as f:
                json.dump(self.translation_cache, f, indent=2)
            
            logger.info(f"Translation cache saved with {len(self.translation_cache)} entries")
        except Exception as e:
            logger.error(f"Failed to save translation cache: {e}")
    
    def _update_average_translation_time(self, translation_time: float):
        """Update average translation time"""
        current_avg = self.stats["average_translation_time"]
        translations_count = self.stats["translations_performed"]
        
        if translations_count == 1:
            self.stats["average_translation_time"] = translation_time
        else:
            new_avg = ((current_avg * (translations_count - 1)) + translation_time) / translations_count
            self.stats["average_translation_time"] = new_avg
    
    def get_supported_languages(self) -> List[Dict]:
        """Get list of supported languages"""
        languages = []
        
        for code, info in self.SUPPORTED_LANGUAGES.items():
            if code in self.enabled_languages:
                language_info = info.copy()
                language_info["code"] = code
                language_info["enabled"] = True
                languages.append(language_info)
        
        return languages
    
    def get_language_statistics(self) -> Dict:
        """Get language support statistics"""
        stats = self.stats.copy()
        
        # Add current state information
        stats["enabled_languages"] = len(self.enabled_languages)
        stats["detected_languages"] = len(self.detected_languages)
        stats["cached_translations"] = len(self.translation_cache)
        stats["cultural_adaptations_stored"] = len(self.cultural_adaptations)
        
        # Calculate success rate
        if stats["translations_performed"] > 0:
            stats["translation_success_rate"] = stats["successful_translations"] / stats["translations_performed"]
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["translations_performed"]
        else:
            stats["translation_success_rate"] = 0.0
            stats["cache_hit_rate"] = 0.0
        
        # Add user profile info
        if self.user_profile:
            stats["user_primary_language"] = self.user_profile.primary_language
            stats["user_secondary_languages"] = len(self.user_profile.secondary_languages)
            stats["user_cultural_context"] = self.user_profile.cultural_context
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Test language detection
            detection_result = await self.detect_language("Hello world, this is a test")
            if not detection_result["success"]:
                return False
            
            # Test translation
            translation_result = await self.translate_text("Hello", "es", "en")
            if not translation_result["success"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Language support health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo multi-language support functionality"""
        print("🌐 Multi-Language Support Demo")
        print("=" * 35)
        
        language_support = MultiLanguageSupport()
        await language_support.initialize_language_services()
        
        # Test language detection
        test_texts = [
            "Hello, how are you today?",
            "Hola, ¿cómo estás hoy?",
            "Bonjour, comment allez-vous?",
            "Hallo, wie geht es dir heute?"
        ]
        
        print("\n🔍 Testing language detection...")
        for text in test_texts:
            result = await language_support.detect_language(text)
            if result["success"]:
                print(f"   '{text[:30]}...' -> {result['language_name']} ({result['detected_language']}) [{result['confidence']:.2f}]")
            else:
                print(f"   Detection failed for: {text[:30]}...")
        
        # Test translation
        print("\n🔄 Testing translation...")
        translations = [
            ("Hello", "en", "es"),
            ("Thank you", "en", "fr"),
            ("Help", "en", "de"),
            ("Emergency", "en", "es")
        ]
        
        for text, source, target in translations:
            result = await language_support.translate_text(text, target, source)
            if result["success"]:
                cached = " (cached)" if result["cached"] else ""
                print(f"   {text} ({source}) -> {result['translated_text']} ({target}){cached}")
            else:
                print(f"   Translation failed: {text}")
        
        # Test cultural adaptation
        print("\n🎭 Testing cultural adaptation...")
        test_content = {
            "type": "medical_advice",
            "message": "Hi! You should take your medicine.",
            "instructions": "Take the pill with water"
        }
        
        cultures = ["western", "latin", "asian"]
        for culture in cultures:
            result = await language_support.adapt_content_culturally(test_content, culture)
            if result["success"]:
                print(f"   {culture.title()} adaptation:")
                print(f"      Adaptations: {', '.join(result['adaptations_made'])}")
                if "message" in result["adapted_content"]:
                    print(f"      Message: {result['adapted_content']['message']}")
        
        # Test user profile update
        print("\n👤 Testing user profile update...")
        profile_updates = {
            "primary_language": "es",
            "secondary_languages": ["en", "fr"],
            "cultural_context": "latin",
            "accessibility_needs": ["screen_reader", "large_text"]
        }
        
        update_result = language_support.update_user_language_profile(profile_updates)
        if update_result["success"]:
            print(f"   ✅ Updated profile fields: {', '.join(update_result['updated_fields'].keys())}")
            print(f"   Primary language: {update_result['current_profile']['primary_language']}")
            print(f"   Cultural context: {update_result['current_profile']['cultural_context']}")
        
        # Show supported languages
        supported = language_support.get_supported_languages()
        print(f"\n🌍 Supported languages: {len(supported)}")
        for lang in supported[:5]:  # Show first 5
            print(f"   {lang['code']}: {lang['native_name']} ({lang['name']})")
        
        # Show statistics
        stats = language_support.get_language_statistics()
        print(f"\n📊 Language Statistics:")
        print(f"   Translations performed: {stats['translations_performed']}")
        print(f"   Translation success rate: {stats['translation_success_rate']:.2f}")
        print(f"   Language detections: {stats['language_detections']}")
        print(f"   Cultural adaptations: {stats['cultural_adaptations']}")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.2f}")
        print(f"   Average translation time: {stats['average_translation_time']:.3f}s")
    
    asyncio.run(demo())
