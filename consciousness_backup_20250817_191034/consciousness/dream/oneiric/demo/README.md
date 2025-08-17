# 🌙 Dream Interpreter - Enhanced Edition

A sophisticated dream interpretation application with voice input, multimedia processing, and AI-powered dream generation capabilities.

## ✨ Features

### 🎙️ Quick Voice Capture
- **iPhone-style quick access**: Triple-click side button simulation for sleepy users
- **Voice-to-text conversion**: Automatic transcription with confidence scoring
- **Auto-enhancement**: Automatically adds emojis and symbols to voice transcriptions
- **Multiple language support**: Supports various locales for international users

### 🎨 Dream Enhancement
- **Smart emoji integration**: Contextually adds relevant emojis based on dream content
- **Symbolic interpretation**: Adds symbolic meanings to common dream elements
- **Emotional analysis**: Detects and highlights emotional themes
- **Multi-level enhancement**: Adjustable enhancement levels (low, moderate, high)

### 🤖 AI Dream Generation
- **Multimedia input processing**: Combines voice, images, emojis, URLs, and text
- **Creative dream synthesis**: AI generates unique dreams from multiple inputs
- **Thematic analysis**: Extracts and weaves themes across different media types
- **Non-bias narrative generation**: Creates balanced, creative dream narratives

### 🔮 Advanced Interpretation
- **Multi-LLM support**: Works with OpenAI, Anthropic, Lukhas, and other LLMs
- **Psychological insights**: Provides deep personal insights and guidance
- **Cultural awareness**: Adapts interpretations based on user locale
- **Symbol database**: Comprehensive dream symbol meanings

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your AI provider** (optional):
   ```python
   from dream_interpreter import LLMConfig, DreamInterpreter
   
   llm_config = LLMConfig(
       provider="openai",  # or "anthropic", "lukhas"
       api_key="your-api-key",
       model="gpt-4"
   )
   
   interpreter = DreamInterpreter(llm_config=llm_config)
   ```

3. **Run the application**:
   ```bash
   python dream_interpreter.py
   ```

## 💡 Usage Examples

### Voice Dream Capture (iPhone-style)
```python
# Quick voice recording for sleepy users
dream_text = interpreter.quick_recorder.quick_dream_capture()
if dream_text:
    interpretation = interpreter.interpret_dream_with_ai(ai_function)
    interpreter.display_interpretation()
```

### Multimedia Dream Creation
```python
# Create AI dream from multiple inputs
media_inputs = [
    {"type": "voice_note", "content": "base64_audio_data"},
    {"type": "image", "content": "base64_image_data"},
    {"type": "emoji_sequence", "content": "🌙✨🦋🌊"},
    {"type": "url", "content": "https://news-article.com"},
    {"type": "text", "content": "I've been thinking about..."}
]

processed_inputs = interpreter.multimedia_input_processor.process_multiple_inputs(media_inputs)
ai_dream = await interpreter.create_multimedia_dream(processed_inputs)
print(ai_dream.narrative)
```

### Enhanced Text Processing
```python
# Smart emoji enhancement
enhancement = interpreter.dream_enhancer.smart_emoji_enhancement(
    "I was flying through a dark forest", 
    enhancement_level='high'
)
print(enhancement.enriched_text)  # "I was flying 🕊️ through a dark forest 🌲 ✨"
```

## 🔧 Configuration

### LLM Providers
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude-3 Sonnet, Claude-3 Opus
- **Lukhas**: Local LLM integration
- **Custom**: Implement your own provider

### Voice Settings
```python
# Configure voice input
voice_config = {
    'language': 'en-US',  # or 'es-ES', 'fr-FR', etc.
    'auto_enhance': True,
    'wake_up_mode': True,  # Optimized for sleepy users
    'duration_limit': 300  # 5 minutes max
}
```

### Enhancement Levels
- **Low**: Minimal emoji additions
- **Moderate**: Balanced enhancement (default)
- **High**: Rich emoji and symbol integration

## 🎯 Core Components

### QuickAccessRecorder
- iPhone-style quick recording
- Automatic transcription
- Sleep-friendly interface

### DreamEnhancer
- Smart emoji integration
- Symbolic element detection
- Emotional tone analysis

### MultimediaInputProcessor
- Voice note processing
- Image analysis
- URL content extraction
- Emoji sequence interpretation

### AIModelIntegration
- Multi-provider support
- Async processing
- Custom model configuration

## 📱 Mobile Integration Ideas

For iPhone integration (future development):
- **Shortcuts app**: Create voice recording shortcuts
- **Widget support**: Quick dream capture widget
- **Siri integration**: "Hey Siri, record my dream"
- **Health app sync**: Sleep pattern correlation

## 🌍 Internationalization

Supported languages:
- 🇺🇸 English (en-US)
- 🇪🇸 Spanish (es-ES)
- 🇫🇷 French (fr-FR) - Coming soon
- 🇩🇪 German (de-DE) - Coming soon

Add new languages by extending the `TRANSLATIONS` dictionary.

## 🔮 Dream Symbol Database

The system includes interpretations for common dream symbols:
- **Flying**: Freedom, transcendence, liberation
- **Water**: Emotions, subconscious, cleansing
- **Doors**: Opportunities, transitions, choices
- **Animals**: Instincts, natural wisdom, aspects of self
- **Colors**: Emotional states, energy, meanings

## 🚧 Future Enhancements

- **Dream journal**: Persistent storage with SQLite
- **Pattern recognition**: Recurring dream analysis
- **Visual dream mapping**: Generate images from dreams
- **Social features**: Share and compare interpretations
- **Biometric integration**: Heart rate, sleep quality correlation
- **AR/VR visualization**: Immersive dream exploration

## 🤝 Contributing

Feel free to contribute by:
1. Adding new LLM providers
2. Expanding the symbol database
3. Improving voice processing
4. Adding new languages
5. Enhancing AI dream generation

## 📄 License

This project is open for educational and personal use. Please respect API terms of service for commercial applications.

---

*Sweet dreams! 🌙✨*
