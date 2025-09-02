#!/usr/bin/env python3
"""
NIAS OpenAI Adapter
Provides comprehensive OpenAI integration for NIAS multimodal data fusion.
Handles visual, textual, audio, and contextual data processing.
"""

import base64
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

import cv2  # For image processing
import numpy as np
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Types of data modalities NIAS processes"""

    VISUAL = "visual"  # Eye tracking, facial expressions, body language
    BIOMETRIC = "biometric"  # Heart rate, skin conductance, etc.
    CONTEXTUAL = "contextual"  # Weather, location, time, calendar
    BEHAVIORAL = "behavioral"  # Click patterns, navigation, history
    TEXTUAL = "textual"  # User input, product descriptions
    AUDIO = "audio"  # Voice input, ambient sound


@dataclass
class MultimodalData:
    """Container for multimodal data streams"""

    modality: ModalityType
    raw_data: Any
    processed_data: Optional[Any] = None
    embeddings: Optional[list[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class NIASOpenAIAdapter:
    """
    OpenAI adapter for NIAS multimodal data fusion.

    Features:
    - GPT-4V for visual analysis (eye tracking, expressions)
    - GPT-4 for contextual understanding and fusion
    - Embeddings for semantic similarity
    - Whisper for audio transcription
    - DALL-E 3 for visualization generation
    - Moderation for safety
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

        # Configuration
        self.fusion_strategy = "intermediate"  # late, intermediate, or early
        self.max_context_length = 8000
        self.embedding_model = "text-embedding-3-large"
        self.vision_detail = "high"  # for GPT-4V

        # Cache for embeddings
        self.embedding_cache: dict[str, list[float]] = {}

        logger.info("NIAS OpenAI Adapter initialized")

    async def fuse_multimodal_streams(
        self, data_streams: list[MultimodalData], user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Fuse multiple data streams using OpenAI models.

        This is the main entry point for multimodal fusion.
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, using fallback fusion")
            return await self._fallback_fusion(data_streams, user_context)

        try:
            # Step 1: Process each modality
            processed_streams = await self._process_individual_modalities(data_streams)

            # Step 2: Apply fusion strategy
            if self.fusion_strategy == "late":
                fusion_result = await self._late_fusion(processed_streams, user_context)
            elif self.fusion_strategy == "intermediate":
                fusion_result = await self._intermediate_fusion(processed_streams, user_context)
            else:  # early
                fusion_result = await self._early_fusion(processed_streams, user_context)

            # Step 3: Generate unified interpretation
            interpretation = await self._generate_unified_interpretation(fusion_result, user_context)

            return {
                "fusion_result": fusion_result,
                "interpretation": interpretation,
                "confidence": self._calculate_fusion_confidence(processed_streams),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Multimodal fusion failed: {e}")
            return await self._fallback_fusion(data_streams, user_context)

    async def _process_individual_modalities(self, data_streams: list[MultimodalData]) -> list[MultimodalData]:
        """Process each modality with appropriate OpenAI model"""
        processed = []

        for stream in data_streams:
            if stream.modality == ModalityType.VISUAL:
                processed_stream = await self._process_visual_stream(stream)
            elif stream.modality == ModalityType.BIOMETRIC:
                processed_stream = await self._process_biometric_stream(stream)
            elif stream.modality == ModalityType.CONTEXTUAL:
                processed_stream = await self._process_contextual_stream(stream)
            elif stream.modality == ModalityType.BEHAVIORAL:
                processed_stream = await self._process_behavioral_stream(stream)
            elif stream.modality == ModalityType.TEXTUAL:
                processed_stream = await self._process_textual_stream(stream)
            elif stream.modality == ModalityType.AUDIO:
                processed_stream = await self._process_audio_stream(stream)
            else:
                processed_stream = stream

            processed.append(processed_stream)

        return processed

    async def _process_visual_stream(self, stream: MultimodalData) -> MultimodalData:
        """Process visual data using GPT-4V"""
        try:
            # Prepare image for GPT-4V
            if isinstance(stream.raw_data, dict) and "image_data" in stream.raw_data:
                image_data = stream.raw_data["image_data"]

                # Convert to base64 if needed
                if isinstance(image_data, np.ndarray):
                    _, buffer = cv2.imencode(".jpg", image_data)
                    base64_image = base64.b64encode(buffer).decode("utf-8")
                else:
                    base64_image = image_data

                # Analyze with GPT-4V
                response = await self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Analyze visual biometric data for NIAS.
                        Focus on: eye tracking patterns, facial expressions,
    body language.
                        Provide insights about attention, emotional state,
    and engagement.""",
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Metadata: {json.dumps(stream.metadata)}",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": self.vision_detail,
                                    },
                                },
                            ],
                        },
                    ],
                    max_tokens=500,
                )

                analysis = response.choices[0].message.content
                stream.processed_data = {
                    "visual_analysis": analysis,
                    "attention_metrics": self._extract_attention_metrics(analysis),
                    "emotional_indicators": self._extract_emotional_indicators(analysis),
                }

            # Process eye tracking data
            elif "gaze_path" in stream.raw_data:
                gaze_analysis = await self._analyze_gaze_patterns(stream.raw_data["gaze_path"])
                stream.processed_data = gaze_analysis

        except Exception as e:
            logger.error(f"Visual processing failed: {e}")
            stream.processed_data = {"error": str(e)}

        return stream

    async def _analyze_gaze_patterns(self, gaze_path: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze eye tracking gaze patterns"""
        if not gaze_path:
            return {"error": "No gaze data"}

        # Calculate gaze metrics
        fixations = []
        saccades = []

        for i in range(1, len(gaze_path)):
            prev = gaze_path[i - 1]
            curr = gaze_path[i]

            # Calculate movement
            distance = np.sqrt((curr["x"] - prev["x"]) ** 2 + (curr["y"] - prev["y"]) ** 2)
            duration = curr["timestamp"] - prev["timestamp"]

            if distance < 50:  # Fixation threshold
                fixations.append({"x": curr["x"], "y": curr["y"], "duration": duration})
            else:  # Saccade
                saccades.append(
                    {
                        "distance": distance,
                        "velocity": distance / duration if duration > 0 else 0,
                    }
                )

        # Use GPT-4 to interpret patterns
        try:
            interpretation = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Interpret eye tracking patterns for attention and interest analysis",
                    },
                    {
                        "role": "user",
                        "content": f"""Fixations: {len(fixations)} total,
    avg duration: {np.mean([f["duration"] for f in fixations]) if fixations else 0}ms
                    Saccades: {len(saccades)} total, avg velocity: {np.mean([s["velocity"] for s in saccades]) if saccades else 0}px/ms
                    Total gaze points: {len(gaze_path)}""",
                    },
                ],
                temperature=0.3,
            )

            return {
                "fixation_count": len(fixations),
                "saccade_count": len(saccades),
                "interpretation": interpretation.choices[0].message.content,
                "attention_score": (
                    len(fixations) / (len(fixations) + len(saccades)) if (fixations or saccades) else 0.5
                ),
            }

        except Exception as e:
            logger.error(f"Gaze pattern analysis failed: {e}")
            return {"error": str(e)}

    async def _process_biometric_stream(self, stream: MultimodalData) -> MultimodalData:
        """Process biometric data (heart rate, skin conductance, etc.)"""
        try:
            biometric_data = stream.raw_data

            # Analyze biometric patterns
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze biometric data for emotional and physiological state.
                    Consider: arousal levels, stress indicators, engagement patterns.""",
                    },
                    {"role": "user", "content": json.dumps(biometric_data)},
                ],
                functions=[
                    {
                        "name": "analyze_biometrics",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "arousal_level": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "stress_level": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "engagement": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "emotional_valence": {
                                    "type": "number",
                                    "minimum": -1,
                                    "maximum": 1,
                                },
                                "key_insights": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "arousal_level",
                                "stress_level",
                                "engagement",
                                "emotional_valence",
                            ],
                        },
                    }
                ],
                function_call={"name": "analyze_biometrics"},
            )

            analysis = json.loads(response.choices[0].message.function_call.arguments)
            stream.processed_data = analysis

        except Exception as e:
            logger.error(f"Biometric processing failed: {e}")
            stream.processed_data = {"error": str(e)}

        return stream

    async def _process_contextual_stream(self, stream: MultimodalData) -> MultimodalData:
        """Process contextual data (weather, location, time, etc.)"""
        try:
            context_data = stream.raw_data

            # Enrich context with AI insights
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze contextual factors for their impact on user state and receptivity.
                    Consider how weather, time, location affect mood and attention.""",
                    },
                    {"role": "user", "content": json.dumps(context_data)},
                ],
                temperature=0.5,
            )

            stream.processed_data = {
                "context_analysis": response.choices[0].message.content,
                "receptivity_modifier": self._calculate_context_receptivity(context_data),
                "suggested_adaptations": self._suggest_context_adaptations(context_data),
            }

        except Exception as e:
            logger.error(f"Contextual processing failed: {e}")
            stream.processed_data = {"error": str(e)}

        return stream

    def _calculate_context_receptivity(self, context_data: dict[str, Any]) -> float:
        """Calculate receptivity modifier based on context"""
        receptivity = 1.0

        # Time of day factor
        hour = context_data.get("time_of_day", {}).get("hour", 12)
        if 9 <= hour <= 11 or 14 <= hour <= 16:  # Peak hours
            receptivity *= 1.2
        elif hour < 7 or hour > 22:  # Off hours
            receptivity *= 0.7

        # Weather factor
        weather = context_data.get("weather", {}).get("condition", "clear")
        if weather in ["sunny", "clear"]:
            receptivity *= 1.1
        elif weather in ["rainy", "stormy"]:
            receptivity *= 0.9

        # Location factor
        location_type = context_data.get("location", {}).get("type", "unknown")
        if location_type == "home":
            receptivity *= 1.15
        elif location_type == "work":
            receptivity *= 0.95
        elif location_type == "transit":
            receptivity *= 0.8

        return min(2.0, max(0.5, receptivity))  # Cap between 0.5 and 2.0

    def _suggest_context_adaptations(self, context_data: dict[str, Any]) -> list[str]:
        """Suggest UI/UX adaptations based on context"""
        suggestions = []

        # Light conditions
        if context_data.get("ambient_light", {}).get("level", "normal") == "low":
            suggestions.append("Use dark mode with higher contrast")

        # Noise level
        if context_data.get("ambient_noise", {}).get("level", "normal") == "high":
            suggestions.append("Increase visual prominence, reduce audio reliance")

        # Movement
        if context_data.get("motion", {}).get("is_moving", False):
            suggestions.append("Simplify UI, increase touch targets")

        return suggestions

    async def _process_behavioral_stream(self, stream: MultimodalData) -> MultimodalData:
        """Process behavioral data (clicks, navigation, history)"""
        try:
            behavioral_data = stream.raw_data

            # Generate embeddings for behavioral patterns
            behavior_text = self._serialize_behavior(behavioral_data)
            embeddings = await self._get_embeddings(behavior_text)
            stream.embeddings = embeddings

            # Analyze patterns
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze user behavioral patterns for preferences and intent.
                    Identify: interests, decision patterns, engagement style.""",
                    },
                    {"role": "user", "content": behavior_text},
                ],
                temperature=0.4,
            )

            stream.processed_data = {
                "behavior_analysis": response.choices[0].message.content,
                "intent_prediction": self._predict_user_intent(behavioral_data),
                "preference_profile": self._build_preference_profile(behavioral_data),
            }

        except Exception as e:
            logger.error(f"Behavioral processing failed: {e}")
            stream.processed_data = {"error": str(e)}

        return stream

    def _serialize_behavior(self, behavioral_data: dict[str, Any]) -> str:
        """Convert behavioral data to text for analysis"""
        parts = []

        if "clicks" in behavioral_data:
            parts.append(f"Click patterns: {behavioral_data['clicks']}")

        if "navigation" in behavioral_data:
            parts.append(f"Navigation path: {' -> '.join(behavioral_data['navigation'])}")

        if "dwell_times" in behavioral_data:
            parts.append(f"Dwell times: {behavioral_data['dwell_times']}")

        if "interactions" in behavioral_data:
            parts.append(f"Interactions: {behavioral_data['interactions']}")

        return "\n".join(parts)

    def _predict_user_intent(self, behavioral_data: dict[str, Any]) -> str:
        """Predict user intent from behavior"""
        # Simple heuristic - would be enhanced with ML
        if behavioral_data.get("search_queries"):
            return "active_search"
        elif behavioral_data.get("comparison_views", 0) > 2:
            return "comparing_options"
        elif behavioral_data.get("cart_adds", 0) > 0:
            return "ready_to_purchase"
        else:
            return "browsing"

    def _build_preference_profile(self, behavioral_data: dict[str, Any]) -> dict[str, Any]:
        """Build user preference profile from behavior"""
        return {
            "categories_viewed": behavioral_data.get("categories", []),
            "price_sensitivity": behavioral_data.get("price_range_preference", "medium"),
            "brand_loyalty": behavioral_data.get("brand_repeat_rate", 0.5),
            "decision_speed": behavioral_data.get("avg_decision_time", "moderate"),
        }

    async def _process_textual_stream(self, stream: MultimodalData) -> MultimodalData:
        """Process textual data"""
        try:
            text_data = stream.raw_data

            # Get embeddings
            if isinstance(text_data, str):
                embeddings = await self._get_embeddings(text_data)
                stream.embeddings = embeddings

            # Analyze sentiment and intent
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze text for sentiment, intent, and key topics",
                    },
                    {
                        "role": "user",
                        "content": (text_data if isinstance(text_data, str) else json.dumps(text_data)),
                    },
                ],
                functions=[
                    {
                        "name": "analyze_text",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sentiment": {
                                    "type": "string",
                                    "enum": [
                                        "positive",
                                        "negative",
                                        "neutral",
                                        "mixed",
                                    ],
                                },
                                "sentiment_score": {
                                    "type": "number",
                                    "minimum": -1,
                                    "maximum": 1,
                                },
                                "intent": {"type": "string"},
                                "key_topics": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "urgency": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                            },
                        },
                    }
                ],
                function_call={"name": "analyze_text"},
            )

            analysis = json.loads(response.choices[0].message.function_call.arguments)
            stream.processed_data = analysis

        except Exception as e:
            logger.error(f"Textual processing failed: {e}")
            stream.processed_data = {"error": str(e)}

        return stream

    async def _process_audio_stream(self, stream: MultimodalData) -> MultimodalData:
        """Process audio data using Whisper"""
        try:
            audio_data = stream.raw_data

            if "audio_file" in audio_data:
                # Transcribe with Whisper
                transcription = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data["audio_file"],
                    response_format="verbose_json",
                )

                # Analyze emotional tone from transcription
                tone_analysis = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze emotional tone and stress indicators in transcribed speech",
                        },
                        {
                            "role": "user",
                            # First 5 segments
                            "content": f"Transcription: {transcription.text}\nSegments: {json.dumps(transcription.segments[:5])}",
                        },
                    ],
                )

                stream.processed_data = {
                    "transcription": transcription.text,
                    "language": transcription.language,
                    "tone_analysis": tone_analysis.choices[0].message.content,
                    "segments": transcription.segments,
                }

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            stream.processed_data = {"error": str(e)}

        return stream

    async def _get_embeddings(self, text: str) -> list[float]:
        """Get embeddings for text, with caching"""
        # Check cache
        cache_key = f"{self.embedding_model}:{text[:100]}"  # Use first 100 chars as key
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        try:
            response = await self.client.embeddings.create(model=self.embedding_model, input=text)
            embeddings = response.data[0].embedding

            # Cache result
            self.embedding_cache[cache_key] = embeddings

            # Limit cache size
            if len(self.embedding_cache) > 1000:
                # Remove oldest entries
                keys = list(self.embedding_cache.keys())
                for key in keys[:100]:
                    del self.embedding_cache[key]

            return embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    async def _intermediate_fusion(
        self,
        processed_streams: list[MultimodalData],
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Intermediate fusion using cross-attention mechanisms"""
        # Prepare fusion prompt
        fusion_data = {"user_context": user_context, "modalities": {}}

        for stream in processed_streams:
            fusion_data["modalities"][stream.modality.value] = stream.processed_data

        # Use GPT-4 to fuse modalities
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Perform intermediate fusion of multimodal data.
                    Identify cross-modal patterns and synthesize unified understanding.
                    Consider how different modalities reinforce or contradict each other.""",
                    },
                    {"role": "user", "content": json.dumps(fusion_data)},
                ],
                functions=[
                    {
                        "name": "fuse_modalities",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "unified_state": {
                                    "type": "object",
                                    "properties": {
                                        "attention_level": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },
                                        "emotional_state": {"type": "string"},
                                        "intent": {"type": "string"},
                                        "receptivity": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },
                                        "cognitive_load": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },
                                    },
                                },
                                "cross_modal_insights": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "confidence_scores": {
                                    "type": "object",
                                    "properties": {
                                        "overall": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },
                                        "per_modality": {"type": "object"},
                                    },
                                },
                                "recommendations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    }
                ],
                function_call={"name": "fuse_modalities"},
            )

            fusion_result = json.loads(response.choices[0].message.function_call.arguments)
            return fusion_result

        except Exception as e:
            logger.error(f"Intermediate fusion failed: {e}")
            return self._basic_fusion(processed_streams)

    async def _late_fusion(
        self,
        processed_streams: list[MultimodalData],
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Late fusion - combine already processed modalities"""
        # Weight each modality's contribution
        weights = {
            ModalityType.VISUAL: 0.3,
            ModalityType.BIOMETRIC: 0.25,
            ModalityType.BEHAVIORAL: 0.2,
            ModalityType.CONTEXTUAL: 0.15,
            ModalityType.TEXTUAL: 0.1,
        }

        fusion_result = {
            "attention_level": 0,
            "stress_level": 0,
            "engagement": 0,
            "intent_clarity": 0,
        }

        total_weight = 0

        for stream in processed_streams:
            weight = weights.get(stream.modality, 0.1)
            total_weight += weight

            if stream.processed_data and isinstance(stream.processed_data, dict):
                # Extract relevant metrics
                data = stream.processed_data
                fusion_result["attention_level"] += weight * data.get("attention_score", 0.5)
                fusion_result["stress_level"] += weight * data.get("stress_level", 0.5)
                fusion_result["engagement"] += weight * data.get("engagement", 0.5)

        # Normalize
        if total_weight > 0:
            for key in fusion_result:
                fusion_result[key] /= total_weight

        return fusion_result

    async def _early_fusion(
        self,
        processed_streams: list[MultimodalData],
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Early fusion - combine raw features"""
        # Concatenate all embeddings
        all_embeddings = []

        for stream in processed_streams:
            if stream.embeddings:
                all_embeddings.extend(stream.embeddings[:100])  # Limit size

        # Use embeddings for similarity search or clustering
        # For now, return basic fusion
        return {
            "embedding_count": len(all_embeddings),
            "fusion_type": "early",
            "status": "experimental",
        }

    def _basic_fusion(self, processed_streams: list[MultimodalData]) -> dict[str, Any]:
        """Basic fusion fallback"""
        return {
            "unified_state": {
                "attention_level": 0.5,
                "emotional_state": "neutral",
                "intent": "browsing",
                "receptivity": 0.7,
                "cognitive_load": 0.5,
            },
            "cross_modal_insights": ["Basic fusion applied"],
            "confidence_scores": {"overall": 0.6, "per_modality": {}},
            "recommendations": ["Gather more data for accurate fusion"],
        }

    async def _generate_unified_interpretation(
        self, fusion_result: dict[str, Any], user_context: dict[str, Any]
    ) -> str:
        """Generate human-readable interpretation of fused data"""
        if not self.client:
            return "Multimodal data processed successfully"

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Generate a concise, actionable interpretation of multimodal fusion results.
                    Focus on: user state, recommendations, and opportunities.""",
                    },
                    {
                        "role": "user",
                        "content": f"Fusion result: {json.dumps(fusion_result)}\nUser context: {json.dumps(user_context)}",
                    },
                ],
                temperature=0.7,
                max_tokens=200,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Interpretation generation failed: {e}")
            return "Multimodal fusion complete"

    def _calculate_fusion_confidence(self, processed_streams: list[MultimodalData]) -> float:
        """Calculate overall confidence in fusion results"""
        if not processed_streams:
            return 0.0

        # Check how many modalities were successfully processed
        successful = sum(
            1 for stream in processed_streams if stream.processed_data and "error" not in stream.processed_data
        )

        # Base confidence on success rate and modality importance
        confidence = successful / len(processed_streams)

        # Boost confidence if key modalities are present
        key_modalities = {
            ModalityType.VISUAL,
            ModalityType.BIOMETRIC,
            ModalityType.BEHAVIORAL,
        }
        present_modalities = {stream.modality for stream in processed_streams}

        if key_modalities.issubset(present_modalities):
            confidence *= 1.2

        return min(1.0, confidence)

    async def _fallback_fusion(
        self, data_streams: list[MultimodalData], user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Fallback fusion when OpenAI is not available"""
        return {
            "fusion_result": {
                "unified_state": {
                    "attention_level": 0.5,
                    "emotional_state": "unknown",
                    "intent": "unknown",
                    "receptivity": 0.5,
                    "cognitive_load": 0.5,
                },
                "confidence_scores": {"overall": 0.3},
            },
            "interpretation": "Basic fusion applied without AI enhancement",
            "confidence": 0.3,
            "timestamp": datetime.now().isoformat(),
        }

    def _extract_attention_metrics(self, analysis: str) -> dict[str, float]:
        """Extract attention metrics from visual analysis"""
        # Simple keyword-based extraction
        metrics = {"focus": 0.5, "interest": 0.5, "distraction": 0.5}

        analysis_lower = analysis.lower()

        # Focus indicators
        if "focused" in analysis_lower or "concentrated" in analysis_lower:
            metrics["focus"] = 0.8
        elif "distracted" in analysis_lower or "unfocused" in analysis_lower:
            metrics["focus"] = 0.3

        # Interest indicators
        if "interested" in analysis_lower or "engaged" in analysis_lower:
            metrics["interest"] = 0.8
        elif "bored" in analysis_lower or "disengaged" in analysis_lower:
            metrics["interest"] = 0.3

        return metrics

    def _extract_emotional_indicators(self, analysis: str) -> dict[str, float]:
        """Extract emotional indicators from visual analysis"""
        # Emotion keywords mapping
        emotions = {
            "happy": ["happy", "joy", "pleased", "content"],
            "sad": ["sad", "unhappy", "disappointed"],
            "stressed": ["stressed", "anxious", "tense", "worried"],
            "calm": ["calm", "relaxed", "peaceful"],
            "confused": ["confused", "puzzled", "uncertain"],
            "excited": ["excited", "enthusiastic", "eager"],
        }

        indicators = {}
        analysis_lower = analysis.lower()

        for emotion, keywords in emotions.items():
            if any(keyword in analysis_lower for keyword in keywords):
                indicators[emotion] = 0.8
            else:
                indicators[emotion] = 0.2

        return indicators

    async def generate_personalization_recommendations(self, fusion_result: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate personalization recommendations based on fusion results"""
        if not self.client:
            return []

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Generate personalization recommendations for NIAS.
                    Consider user state, preferences, and ethical guidelines.
                    Prioritize user wellbeing and consent.""",
                    },
                    {"role": "user", "content": json.dumps(fusion_result)},
                ],
                functions=[
                    {
                        "name": "generate_recommendations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recommendations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "content": {"type": "string"},
                                            "priority": {
                                                "type": "number",
                                                "minimum": 0,
                                                "maximum": 1,
                                            },
                                            "ethical_score": {
                                                "type": "number",
                                                "minimum": 0,
                                                "maximum": 1,
                                            },
                                            "timing": {
                                                "type": "string",
                                                "enum": [
                                                    "immediate",
                                                    "deferred",
                                                    "dream",
                                                ],
                                            },
                                        },
                                    },
                                }
                            },
                        },
                    }
                ],
                function_call={"name": "generate_recommendations"},
            )

            result = json.loads(response.choices[0].message.function_call.arguments)
            return result["recommendations"]

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []

    async def moderate_content(self, content: Union[str, list[str]]) -> dict[str, Any]:
        """Moderate content for safety using OpenAI moderation API"""
        if not self.client:
            return {"flagged": False, "categories": {}}

        try:
            response = await self.client.moderations.create(input=content)

            results = []
            for result in response.results:
                results.append(
                    {
                        "flagged": result.flagged,
                        "categories": {
                            cat: getattr(result.categories, cat)
                            for cat in dir(result.categories)
                            if not cat.startswith("_")
                        },
                        "category_scores": {
                            cat: getattr(result.category_scores, cat)
                            for cat in dir(result.category_scores)
                            if not cat.startswith("_")
                        },
                    }
                )

            return {
                "results": results,
                "any_flagged": any(r["flagged"] for r in results),
            }

        except Exception as e:
            logger.error(f"Content moderation failed: {e}")
            return {"flagged": False, "error": str(e)}

    async def visualize_attention_state(self, fusion_result: dict[str, Any], style: str = "abstract") -> Optional[str]:
        """Generate visual representation of attention state using DALL-E"""
        if not self.client:
            return None

        try:
            # Create visualization prompt
            unified_state = fusion_result.get("unified_state", {})

            prompt = f"""Abstract visualization of human attention state:
            Attention level: {unified_state.get("attention_level", 0.5):.1%}
            Emotional state: {unified_state.get("emotional_state", "neutral")}
            Cognitive load: {unified_state.get("cognitive_load", 0.5):.1%}
            Style: {style}, flowing, gentle colors, no text"""

            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid",
            )

            return response.data[0].url

        except Exception as e:
            logger.error(f"Attention visualization failed: {e}")
            return None


# Singleton instance
_adapter_instance = None


def get_nias_openai_adapter(
    api_key: Optional[str] = None,
) -> NIASOpenAIAdapter:
    """Get or create the singleton NIAS OpenAI Adapter instance"""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = NIASOpenAIAdapter(api_key)
    return _adapter_instance
