---
status: wip
type: documentation
---
# LUKHAS Dream System - OpenAI Integration Guide

## Overview

The LUKHAS Dream System now features comprehensive OpenAI integration, enabling multi-modal dream experiences with text generation, image creation, voice synthesis, and voice recognition capabilities.

## 🚀 Quick Start

### Prerequisites

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Install required dependencies:
```bash
pip install openai aiohttp
```

### Basic Usage

```python
from creativity.dream.dream_pipeline import UnifiedDreamPipeline

# Initialize pipeline
pipeline = UnifiedDreamPipeline(user_id="your_user_id")

# Generate a dream from text
dream = await pipeline.generate_dream_from_text(
    "a journey through crystalline memories",
    dream_type="narrative"
)

# Generate a dream from voice
dream = await pipeline.generate_dream_from_voice(
    "path/to/audio.mp3",
    dream_type="oracle"
)
```

## 📚 Components

### 1. OpenAI Dream Integration (`openai_dream_integration.py`)

Core integration module providing:

- **Text Enhancement**: GPT-4 powered narrative generation
- **Image Generation**: DALL-E 3 dream visualization
- **Voice Synthesis**: TTS for dream narration
- **Voice Recognition**: Whisper for voice-to-dream conversion

#### Key Methods:

```python
# Enhance dream narrative
enhanced_dream = await integration.enhance_dream_narrative(base_dream)

# Generate dream image
dream_with_image = await integration.generate_dream_image(dream)

# Create voice narration
dream_with_audio = await integration.narrate_dream(dream)

# Convert voice to dream
voice_result = await integration.voice_to_dream_prompt(audio_file)

# Complete pipeline
full_dream = await integration.create_full_dream_experience(prompt)
```

### 2. Enhanced Dream Generator (`dream_generator.py`)

Updated with:
- Human-interpretable narrative generation
- SORA-ready visual descriptions
- OpenAI integration support

```python
# Basic dream generation
dream = generate_dream(evaluate_action)

# OpenAI-enhanced generation
dream = await generate_dream_with_openai(
    evaluate_action,
    use_voice_input="voice.mp3",
    generate_visuals=True,
    generate_audio=True
)
```

### 3. Oracle Dream Enhancement (`lukhas_oracle_dream.py`)

Oracle dreams now support:
- AI-enhanced narratives
- Personalized suggestions
- Multi-modal delivery

```python
# Enhanced oracle dream
oracle_dream = await oracle.generate_oracle_dream_enhanced()
```

### 4. Unified Dream Pipeline (`dream_pipeline.py`)

Complete orchestration system:
- Voice-to-dream pipeline
- Multi-type dream generation
- Memory integration
- Analytics and logging

```python
# Initialize pipeline
pipeline = UnifiedDreamPipeline(
    user_id="user_123",
    output_dir="dream_outputs",
    use_openai=True
)

# Generate different dream types
narrative_dream = await pipeline.generate_dream_from_text(
    "floating through time",
    dream_type="narrative"
)

oracle_dream = await pipeline.generate_dream_from_text(
    "guidance for tomorrow",
    dream_type="oracle"
)

symbolic_dream = await pipeline.generate_dream_from_text(
    "quantum consciousness",
    dream_type="symbolic"
)
```

## 🎯 Dream Types

### 1. Narrative Dreams
- Rich, story-like experiences
- Visual descriptions for image generation
- Emotional depth and sensory details
- SORA-compatible video prompts

### 2. Oracle Dreams
- Personalized guidance and suggestions
- Memory-aware recommendations
- Consent-respecting delivery
- Whimsical or reflective tones

### 3. Symbolic Dreams
- GLYPH integration
- Quantum-inspired elements
- Abstract conceptual exploration
- Technical symbolic representation

## 🔧 Configuration

### OpenAI Models Used

- **Text Generation**: GPT-4
- **Image Generation**: DALL-E 3
- **Voice Synthesis**: TTS-1-HD (nova voice)
- **Voice Recognition**: Whisper-1

### Output Structure

Dreams are saved with the following structure:
```
dream_outputs/
├── dream_DREAM_20250728_123456.json
├── dream_DREAM_20250728_123456.png
├── dream_DREAM_20250728_123456.mp3
└── dream_log.jsonl
```

### Dream Object Format

```json
{
  "dream_id": "DREAM_20250728_123456",
  "created_at": "2025-07-28T12:34:56Z",
  "type": "narrative",
  "narrative": {
    "description": "A dreamlike scene...",
    "theme": "crystalline memories",
    "primary_emotion": "wonder",
    "visual_prompt": "Surreal dreamscape..."
  },
  "enhanced_narrative": {
    "full_text": "In the twilight realm...",
    "style": "surreal and poetic",
    "gpt_model": "gpt-4"
  },
  "generated_image": {
    "path": "dream_outputs/dream_123.png",
    "size": "1024x1024",
    "revised_prompt": "A surreal scene..."
  },
  "narration": {
    "path": "dream_outputs/dream_123.mp3",
    "voice": "nova",
    "model": "tts-1-hd"
  },
  "sora_prompt": "Camera slowly pans through..."
}
```

## 🎨 Example Outputs

### Narrative Examples

1. **Crystalline Sky Journey**
   - *"A dreamlike and fluid scene of floating through a crystalline sky filled with memories. The world is bathed in iridescent purple light, evoking a deep sense of wonder. Particles of light dance like butterflies."*

2. **Whispering Forest**
   - *"A mysterious and beckoning scene of walking through a forest where trees whisper forgotten names. The world is bathed in misty jade light, evoking a deep sense of nostalgia. The air shimmers with ancient wisdom."*

3. **Liquid Starlight Ocean**
   - *"A peaceful and infinite scene of swimming in an ocean of liquid starlight. The world is bathed in deep cerulean light, evoking a deep sense of tranquility. Shadows move like gentle waves."*

## 🔐 Privacy & Consent

The system respects user consent for:
- Memory sampling
- Image generation
- Voice synthesis
- Data logging

Configure consent in the user profile or pass to the pipeline.

## 🚨 Error Handling

The system includes comprehensive error handling:
- Fallback to basic generation if OpenAI unavailable
- Graceful degradation for missing components
- Detailed error logging and reporting

## 📊 Analytics

Track dream generation with built-in analytics:

```python
analytics = await pipeline.get_dream_analytics()
# Returns:
# {
#   "total_dreams": 42,
#   "by_type": {"narrative": 20, "oracle": 15, "symbolic": 7},
#   "with_audio": 35,
#   "with_image": 38,
#   "errors": 2
# }
```

## 🔮 Future Enhancements

- SORA video generation (when available)
- Real-time dream streaming
- Multi-language support
- Dream collaboration features
- VR/AR dream experiences

## 📝 Testing

Run the demo scripts:

```bash
# Test OpenAI integration
python creativity/dream/openai_dream_integration.py

# Test unified pipeline
python creativity/dream/dream_pipeline.py

# Generate sample dreams
python creativity/dream/dream_generator.py
```

## 🆘 Troubleshooting

### OpenAI API Key Issues
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connection
python -c "from openai import OpenAI; client = OpenAI(); print('Connected')"
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install openai aiohttp asyncio structlog
```

### Memory/Emotion System Errors
The system gracefully handles missing components. Check logs for details:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

*Last Updated: 2025-07-28 by Claude Code*
*Module Version: 1.0.0*
