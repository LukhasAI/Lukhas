import asyncio
import logging
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Union, Optional
import numpy as np
import os
from identity.backend.app.crypto import generate_collapse_hash


#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony


logger = logging.getLogger(__name__)

class IntentNode:
    """
    A hybrid node for intent detection using both symbolic rules and neural processing.
    Provides a weighted integration of both approaches for robust intent classification.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the IntentNode with configuration.

        Args:
            config: Configuration dictionary for the node
        """
        # Default configuration
        self.config = {
            "neural_weight": 0.7,
            "symbolic_weight": 0.3,
            "max_history_size": 1000,
            "min_confidence": 0.4
        }

        # Update with custom configuration if provided
        if config:
            self.config.update(config)

        # Extract weights for easier access
        self.neural_weight = self.config["neural_weight"]
        self.symbolic_weight = self.config["symbolic_weight"]

        # Initialize processing history
        self.processing_history = []
        self.last_processed = None

        # Log initialization
        logger.info(f"IntentNode initialized with neural_weight={self.neural_weight}, "
                   f"symbolic_weight={self.symbolic_weight}")
        # @JULES03_RENAME
        logger.info("JULES03_RENAME: Refined logging for clarity.")

    async def process(self,
                    input_data: Union[str, Dict[str, Any]],
                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process input to determine intent using both symbolic and neural approaches.

        Args:
            input_data: Text string or structured input data
            context: Additional context for processing

        Returns:
            Dict containing detected intent and metadata
        """
        start_time = time.time()

        # Normalize input to dictionary if string provided
        if isinstance(input_data, str):
            input_data = {"text": input_data, "type": "text"}

        # Initialize context if not provided
        context = context or {}

        # Track timestamps for performance monitoring
        processing_metadata = {
            "input_received": datetime.now().isoformat(),
        }

        # Accent and curiosity integration
        accent_adapter = context.get("accent_adapter") if context else None
        user_id = context.get("user_id", "unknown") if context else "unknown"
        user_text = input_data["text"] if isinstance(input_data, dict) and "text" in input_data else str(input_data)

        # Safeguard for formal/professional context
        if accent_adapter and not accent_adapter.safeguard_formal_context(context or {}):
            logger.info("Curiosity and slang suppressed due to formal/professional context.")
        else:
            # Detect new words and accents
            if accent_adapter:
                # Curiosity about new words
                words = re.findall(r'\b[a-zA-Z\']+\b', user_text)
                for word in words:
                    curiosity = accent_adapter.cognitive_curiosity(word, context or {})
                    if curiosity:
                        logger.info(f"Curiosity triggered: {curiosity}")
                        # Optionally, add to result or context
                        context["curiosity_question"] = curiosity
                        break  # Only ask about one word at a time
                # Accent detection (if audio provided)
                audio_sample = context.get("audio_sample") if context else None
                detected_accent = accent_adapter.detect_accent(audio_sample, context or {})
                if detected_accent:
                    logger.info(f"Accent detected: {detected_accent}")
                    context["detected_accent"] = detected_accent

        # Process through neural pathway
        neural_start = time.time()
        neural_result = await self._neural_process(input_data, context)
        neural_end = time.time()
        processing_metadata["neural_processing_time"] = neural_end - neural_start

        # Process through symbolic pathway
        symbolic_start = time.time()
        symbolic_result = self._symbolic_process(input_data, context)
        symbolic_end = time.time()
        processing_metadata["symbolic_processing_time"] = symbolic_end - symbolic_start

        # Integrate results from both pathways
        integrated_result = self._integrate_results(neural_result, symbolic_result)

        # Add metadata
        end_time = time.time()
        processing_metadata["total_processing_time"] = end_time - start_time
        integrated_result["metadata"] = processing_metadata

        # Update processing history
        self._update_history(input_data, integrated_result)

        # Log the completion of intent processing
        logger.info(f"Intent processing completed successfully for input: {input_data}")

        try:
            # Extend collapse_hash metrics with intent state
            collapse_hash_data = {
                "intent": integrated_result.get("intent"),
                "confidence": integrated_result.get("confidence"),
                "source": integrated_result.get("source"),
                "input_type": input_data.get("type", "unknown"),
            }
            integrated_result["collapse_hash"] = generate_collapse_hash(collapse_hash_data)
        except Exception as e:
            logger.error(f"Error generating collapse_hash: {e}")
            integrated_result["collapse_hash"] = None

        # Symbolic fallback logic
        try:
            if integrated_result["collapse_hash"] is None:
                integrated_result["intent"] = "fallback_intent"
                integrated_result["confidence"] = 0.0
                integrated_result["source"] = "symbolic_fallback"
        except Exception as e:
            logger.error(f"Error in symbolic fallback logic: {e}")
            integrated_result["intent"] = "error_intent"
        integrated_result["confidence"] = 0.0
        integrated_result["source"] = "error_handler"
        logger.info(f"Intent detected: {integrated_result.get('intent')} "
                   f"with confidence {integrated_result.get('confidence')}")

        return integrated_result

    async def _neural_process(self,
                            input_data: Dict[str, Any],
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input using neural network approach."""
        # The type of input determines how we extract features
        input_type = input_data.get("type", "text")

        # Extract features based on input type
        features = self._extract_features(input_data, input_type)

        # In a real implementation, this would use a trained neural model
        # For simulation, we'll use a rule-based approximation with some randomness

        # Simple intent classification logic
        text = input_data.get("text", "").lower() if input_type == "text" else ""

        # Define intent categories and their features
        intent_scores = {
            "query": 0.1,
            "command": 0.1,
            "statement": 0.1,
            "request": 0.1,
            "emotion": 0.1
        }

        # Question detection
        if "?" in text or text.startswith(("what", "why", "how", "when", "where", "who", "which", "is", "are", "can")):
            intent_scores["query"] += 0.6

        # Command detection
        if text.startswith(("show", "find", "get", "search", "tell", "give", "look", "open")):
            intent_scores["command"] += 0.5

        # Request detection
        if "please" in text or "could you" in text or "would you" in text or "can you" in text:
            intent_scores["request"] += 0.5

        # Emotion detection
        emotion_words = ["happy", "sad", "angry", "excited", "worried", "feel", "love", "hate"]
        if any(word in text for word in emotion_words):
            intent_scores["emotion"] += 0.5

        # Add randomness to simulate neural network uncertainty
        for intent in intent_scores:
            random_factor = np.random.random() * 0.2  # Random boost between 0 and 0.2
            intent_scores[intent] += random_factor

        # Normalize scores
        total_score = sum(intent_scores.values())
        normalized_scores = {k: v/total_score for k, v in intent_scores.items()}

        # Select the intent with highest score
        primary_intent = max(normalized_scores, key=normalized_scores.get)

        # Extract second best intent
        temp_scores = normalized_scores.copy()
        del temp_scores[primary_intent]
        secondary_intent = max(temp_scores, key=temp_scores.get) if temp_scores else None

        # Calculate confidence (highest score)
        confidence = normalized_scores[primary_intent]

        # Prepare result
        result = {
            "type": "neural",
            "primary_intent": primary_intent,
            "secondary_intent": secondary_intent,
            "confidence": confidence,
            "all_scores": normalized_scores,
            "features_used": list(features.keys())
        }

        # Add some parameter estimation based on intent
        if primary_intent == "query":
            result["parameters"] = {"query_type": "information" if "what" in text else "clarification"}
        elif primary_intent == "command":
            result["parameters"] = {"target_system": "self"}

        return result

    def _symbolic_process(self,
                         input_data: Union[str, Dict[str, Any]],
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input using symbolic reasoning."""
        # Extract text if input is a dictionary
        if isinstance(input_data, dict):
            text = input_data.get("text", "")
        else:
            text = input_data

        # Default values
        primary_intent = "statement"  # Default intent
        confidence = 0.6  # Base confidence
        rules_applied = []

        # Apply symbolic rules in order of precedence

        # Query detection
        if "?" in text:
            primary_intent = "query"
            confidence += 0.2
            rules_applied.append("question_mark_rule")
        elif re.match(r'^(what|why|how|when|where|who|which|is|are|can)', text.lower()):
            primary_intent = "query"
            confidence += 0.15
            rules_applied.append("question_word_rule")

        # Command detection
        elif re.match(r'^(show|find|get|search|tell|give|look|open)', text.lower()):
            primary_intent = "command"
            confidence += 0.2
            rules_applied.append("command_verb_rule")

        # Request detection
        elif "please" in text.lower() or re.search(r'(could|would|can)(\s+you|\s+i|\s+we)', text.lower()):
            primary_intent = "request"
            confidence += 0.2
            rules_applied.append("request_marker_rule")
        elif "help" in text.lower():
            primary_intent = "request"
            confidence += 0.15
            rules_applied.append("help_keyword_rule")

        # Emotion detection
        elif re.search(r'(feel|love|hate|happy|sad|angry|excited|worried)', text.lower()):
            primary_intent = "emotion"
            confidence += 0.2
            rules_applied.append("emotion_keyword_rule")

        # Add a bit of randomness to simulate uncertainty
        confidence += (np.random.random() * 0.1)

        # Cap confidence at 0.9 for symbolic pathway
        confidence = min(confidence, 0.9)

        return {
            "type": "symbolic",
            "primary_intent": primary_intent,
            "confidence": confidence,
            "rules_applied": rules_applied
        }

    def _extract_features(self, input_data: Dict[str, Any], input_type: str) -> Dict[str, Any]:
        """Extract relevant features from input data based on type."""
        features = {}

        if input_type == "text":
            text = input_data.get("text", "")
            features.update({
                "text_length": len(text),
                "has_question_mark": "?" in text,
                "word_count": len(text.split()),
                "contains_command_verb": any(cmd in text.lower() for cmd in
                                          ["show", "find", "get", "search", "tell"]),
                "contains_request_marker": any(req in text.lower() for req in
                                            ["please", "could you", "would you", "can you"]),
            })

        elif input_type == "voice":
            # Voice features
            features.update({
                "duration": input_data.get("duration", 0),
                "average_volume": input_data.get("volume", 0),
                "speech_rate": input_data.get("speech_rate", 0),
            })

        elif input_type == "multi":
            # Multimodal features
            features.update({
                "has_text": "text" in input_data,
                "has_image": "image" in input_data,
                "has_voice": "voice" in input_data,
            })

        return features

    def _integrate_results(self,
                          neural_result: Dict[str, Any],
                          symbolic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate neural and symbolic results."""
        # Calculate weighted confidence
        neural_confidence = neural_result["confidence"]
        symbolic_confidence = symbolic_result["confidence"]

        weighted_confidence = (
            (neural_confidence * self.neural_weight) +
            (symbolic_confidence * self.symbolic_weight)
        )

        # Determine primary intent based on weighted confidence
        neural_weighted = neural_confidence * self.neural_weight
        symbolic_weighted = symbolic_confidence * self.symbolic_weight

        # Select the winner and mark the source
        if neural_weighted >= symbolic_weighted:
            primary_intent = neural_result["primary_intent"]
            source = "neural"
            alternative_intent = symbolic_result["primary_intent"]
        else:
            primary_intent = symbolic_result["primary_intent"]
            source = "symbolic"
            alternative_intent = neural_result["primary_intent"]

        # Build combined result
        result = {
            "intent": primary_intent,
            "alternative_intent": alternative_intent,
            "confidence": weighted_confidence,
            "source": source,
            "neural_result": {
                "intent": neural_result["primary_intent"],
                "confidence": neural_result["confidence"]
            },
            "symbolic_result": {
                "intent": symbolic_result["primary_intent"],
                "confidence": symbolic_result["confidence"],
                "rules_applied": symbolic_result.get("rules_applied", [])
            }
        }

        # Add any parameters from the winning source
        if source == "neural" and "parameters" in neural_result:
            result["parameters"] = neural_result["parameters"]

        return result

    def _update_history(self, input_data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Update processing history with latest result."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "input_type": input_data.get("type", "unknown"),
            "detected_intent": result.get("intent"),
            "confidence": result.get("confidence"),
            "source": result.get("source")
        }

        self.processing_history.append(history_entry)
        self.last_processed = datetime.now().isoformat()

        # Limit history size
        if len(self.processing_history) > self.config["max_history_size"]:
            self.processing_history = self.processing_history[-self.config["max_history_size"]:]