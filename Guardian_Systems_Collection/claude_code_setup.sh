# 🏥 Healthcare Guardian - Claude Code Setup Commands

# 1. INITIAL PROJECT SETUP
# Navigate to your Guardian_Systems_Collection directory
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/Guardian_Systems_Collection

# Create the new healthcare project structure
mkdir -p healthcare_guardian_es/{voice_andaluz,medical_ai,sas_integration,vision_systems,android_app,emergency_systems,tests}

# 2. CREATE SPECIALIZED AGENTS
# Copy and paste these commands one by one in Claude Code:

# Healthcare System Architect
claude-code add agent healthcare-architect \
  --context "You are a Spanish healthcare AI system architect specializing in eldercare. Expert in Lukhas AI integration, Trinity Framework (⚛️🧠🛡️), and Spanish healthcare regulations. Focus on plugin architecture that leverages existing Lukhas components (VIVOX, Guardian, Memory systems) while building healthcare-specific features for illiterate Spanish elders."

# Andaluz Voice Engineer  
claude-code add agent voice-engineer \
  --context "You are an Andaluz Spanish voice interface specialist. Expert in Spanish dialects, medical terminology, and voice AI for elderly users. Focus on natural language processing for Andaluz dialect, medical vocabulary recognition, and elder-friendly voice interactions. Integrate with Lukhas consciousness systems for empathetic responses."

# Medical AI Integration Specialist
claude-code add agent medical-ai \
  --context "You are a GPT-5 healthcare integration specialist. Expert in OpenAI GPT-5 healthcare features, medical AI, and Spanish healthcare systems. Focus on integrating GPT-5 medical capabilities with Lukhas AI consciousness for medication management, symptom analysis, and health monitoring for Spanish elders."

# SAS Integration Engineer
claude-code add agent sas-engineer \
  --context "You are a Servicio Andaluz de Salud (SAS) integration expert. Specialist in Spanish healthcare APIs, appointment booking systems, and medical record integration. Focus on connecting Lukhas AI with Andalusian healthcare infrastructure for seamless elder healthcare management."

# Android Developer for Elders
claude-code add agent android-developer \
  --context "You are an Android developer specializing in elder-friendly interfaces. Expert in accessibility design, large icon interfaces, voice-controlled apps, and Spanish localization. Focus on creating intuitive Android apps for illiterate Spanish elders with minimal UI complexity."

# Emergency Response Specialist
claude-code add agent emergency-specialist \
  --context "You are a medical emergency response system engineer. Expert in emergency protocols, GPS integration, automated dispatch systems, and Spanish emergency services. Focus on building rapid response systems that work with Lukhas Guardian for elder emergency situations."

# 3. INITIALIZE PROJECT STRUCTURE
# Create main project files
touch healthcare_guardian_es/README.md
touch healthcare_guardian_es/requirements.txt
touch healthcare_guardian_es/main.py
touch healthcare_guardian_es/config.py

# Create module init files
find healthcare_guardian_es -type d -exec touch {}/__init__.py \;

# 4. SETUP DEVELOPMENT WORKFLOW
# Create development scripts
cat > healthcare_guardian_es/setup_dev.sh << 'EOF'
#!/bin/bash
# Development environment setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Healthcare Guardian development environment ready!"
EOF

chmod +x healthcare_guardian_es/setup_dev.sh

# 5. CREATE INITIAL REQUIREMENTS
cat > healthcare_guardian_es/requirements.txt << 'EOF'
# Core Dependencies
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6

# Lukhas AI Integration
# (Add your Lukhas core dependencies here)

# Spanish/Voice Processing
speechrecognition>=3.10.0
gtts>=2.4.0
pydub>=0.25.1
librosa>=0.10.1

# Medical AI & GPT-5
openai>=1.3.0
pandas>=2.1.0
numpy>=1.25.0

# Computer Vision/OCR
opencv-python>=4.8.0
pytesseract>=0.3.10
pillow>=10.1.0

# Spanish Healthcare Integration
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.3

# Android Integration
flask>=3.0.0
flask-cors>=4.0.0

# Database & Caching
sqlalchemy>=2.0.0
redis>=5.0.0
psycopg2-binary>=2.9.0

# Testing & Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.1.0
EOF

# 6. START DEVELOPMENT WITH AGENTS
# Use these commands to begin development with your agents:

# Start with architecture design
claude-code chat healthcare-architect "Let's design the healthcare guardian plugin architecture. Review the existing Lukhas Guardian Systems Collection and plan how to integrate the best components into a unified healthcare solution for Spanish elders. Focus on leveraging existing Lukhas components and identify what new components we need to build."

# Begin voice engine development
claude-code chat voice-engineer "Start developing the Andaluz voice recognition system. We need to handle Spanish elderly speech patterns, medical terminology, and integrate with Lukhas consciousness for empathetic responses. What's your implementation approach?"

# Plan GPT-5 integration
claude-code chat medical-ai "Plan the GPT-5 healthcare integration. We need medication interaction checking, symptom analysis, and health recommendations for Spanish elders. How do we leverage GPT-5's healthcare features with Lukhas consciousness?"

# Design SAS integration
claude-code chat sas-engineer "Design the Servicio Andaluz de Salud integration. We need appointment booking, prescription synchronization, and emergency dispatch integration. What's the API strategy?"

# Plan Android app
claude-code chat android-developer "Design the elder-friendly Android interface. Large icons, voice control, minimal complexity for illiterate users. What's the UI/UX approach?"

# Design emergency systems
claude-code chat emergency-specialist "Design the emergency response system. GPS location, automatic dispatch, integration with Spanish emergency services. How do we ensure <2 minute response times?"

# 7. CONTINUOUS DEVELOPMENT COMMANDS
# Use these for ongoing development:

# Code review with agents
claude-code review --agent healthcare-architect voice_andaluz/

# Test with medical specialist
claude-code test --agent medical-ai medical_ai/

# Performance optimization
claude-code optimize --agent voice-engineer voice_andaluz/speech_processing.py

# Security review
claude-code security --agent sas-engineer sas_integration/

# UI/UX feedback
claude-code ui-review --agent android-developer android_app/

# Emergency testing
claude-code emergency-test --agent emergency-specialist emergency_systems/

# 8. DEPLOYMENT PREPARATION
# When ready to deploy:
claude-code build --target android --agent android-developer
claude-code deploy --environment staging --agent healthcare-architect
claude-code monitor --metrics voice-accuracy emergency-response-time --agent medical-ai

echo "🏥 Healthcare Guardian project setup complete!"
echo "💡 Next: Run 'claude-code chat healthcare-architect' to begin architecture design"
echo "🚀 Goal: Spanish eldercare AI system with voice-first interaction and emergency response"