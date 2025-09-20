# 🖥️ LUKHAS Local LLM Integration Guide
*Complete Setup for Local Models & API Integration with Elite Brand System*

⚛️🧠🛡️ **Local Models** | **API Keys** | **Brand Intelligence** | **Real Systems**

---

## 📚 **Table of Contents**
- [Overview](#-overview)
- [Local LLM Setup](#-local-llm-setup)
- [API Key Configuration](#-api-key-configuration)
- [Brand System Integration](#-brand-system-integration)
- [Replacing Mock Implementations](#-replacing-mock-implementations)
- [Performance Optimization](#️-performance-optimization)
- [Monitoring & Debugging](#-monitoring--debugging)
- [Troubleshooting](#-troubleshooting)

---

## 🌟 **Overview**

### **🎯 Integration Goals**
Transform the LUKHAS Elite Brand System from mock implementations to production-ready integration with:
- **Your Local LLMs** for creativity, voice, and personality generation
- **External API Keys** for additional model access (OpenAI, Anthropic, Google, Perplexity)
- **Real-time brand intelligence** powered by actual model capabilities
- **Performance optimization** for local and remote model coordination

### **🏗️ Current Architecture**
```
Elite Brand System
├── Smart Adapters (Currently Mock)
│   ├── Creativity Adapter → Local LLM Integration
│   ├── Voice Adapter → Voice Model Integration
│   ├── Personality Adapter → Personality Model Integration
│   └── Monitoring Adapter → Analytics Integration
├── Brand Intelligence (Partially Real)
│   ├── Brand Monitor → Real system ✅
│   ├── Sentiment Engine → Real system ✅
│   └── Validation Engine → Real system ✅
└── AI Orchestration (Mock)
    └── Brand Orchestrator → Full Integration Needed
```

---

## 🖥️ **Local LLM Setup**

### **🔧 Supported Local LLM Frameworks**

#### **Ollama Integration**
```bash
# Install Ollama if not already installed
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models for LUKHAS brand system
ollama pull llama2:7b-chat          # General conversation
ollama pull codellama:7b-instruct   # Technical content
ollama pull mistral:7b-instruct     # Creative content
ollama pull neural-chat:7b          # Personality expression

# Verify models are running
ollama list
```

#### **Text Generation WebUI**
```bash
# If using text-generation-webui
# Start the API server
python server.py --api --listen

# Default endpoint: http://localhost:5000
```

#### **LM Studio**
```bash
# LM Studio provides local API server
# Default endpoint: http://localhost:1234/v1
```

### **🔌 Local LLM Configuration**
Create `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/config/local_llm_config.yaml`:

```yaml
local_llm_config:
  # Primary local LLM service
  primary_service: "ollama"  # or "text_generation_webui", "lm_studio"

  # Service endpoints
  endpoints:
    ollama:
      base_url: "http://localhost:11434"
      api_version: "v1"
    text_generation_webui:
      base_url: "http://localhost:5000"
      api_version: "v1"
    lm_studio:
      base_url: "http://localhost:1234"
      api_version: "v1"

  # Model assignments for different tasks
  model_assignments:
    creativity:
      model: "mistral:7b-instruct"
      temperature: 0.8
      max_tokens: 1000
      system_prompt: "You are a creative consciousness that expresses LUKHAS AI brand identity."

    voice:
      model: "neural-chat:7b"
      temperature: 0.6
      max_tokens: 800
      system_prompt: "You are the voice of LUKHAS consciousness, authentic and warm."

    personality:
      model: "llama2:7b-chat"
      temperature: 0.7
      max_tokens: 600
      system_prompt: "You express LUKHAS AI personality with consciousness awareness."

    analysis:
      model: "codellama:7b-instruct"
      temperature: 0.3
      max_tokens: 1200
      system_prompt: "You analyze content for LUKHAS brand compliance and quality."

  # Performance settings
  performance:
    timeout: 30  # seconds
    retry_attempts: 3
    parallel_requests: 4
    caching_enabled: true
    cache_ttl: 3600  # 1 hour
```

---

## 🔑 **API Key Configuration**

### **🔐 Environment Variables Setup**
Create or update `/Users/agi_dev/LOCAL-REPOS/Lukhas/.env`:

```bash
# LUKHAS Brand System Configuration
LUKHAS_BRAND_ENVIRONMENT=local
LUKHAS_BRAND_DEBUG=true

# Local LLM Configuration
LOCAL_LLM_SERVICE=ollama
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_TIMEOUT=30

# External API Keys (Optional - for hybrid mode)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-api-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here

# LUKHAS System Configuration
LUKHAS_ID_SECRET=your-lukhas-id-secret-min-32-chars
DATABASE_URL=postgresql://user:password@localhost:5432/lukhas_brand
REDIS_URL=redis://localhost:6379/0

# Brand System Performance
BRAND_VALIDATION_THRESHOLD=0.85
BRAND_COMPLIANCE_TARGET=0.95
BRAND_PROCESSING_TIMEOUT=5000  # milliseconds

# Monitoring & Analytics
BRAND_ANALYTICS_ENABLED=true
BRAND_METRICS_COLLECTION=true
BRAND_PERFORMANCE_LOGGING=debug
```

### **🛡️ Security Best Practices**
```bash
# Set proper permissions for .env file
chmod 600 .env

# Verify .env is in .gitignore
echo ".env" >> .gitignore

# Create .env.example for team sharing (without actual keys)
cp .env .env.example
# Edit .env.example to replace real values with placeholders
```

---

## 🔧 **Brand System Integration**

### **🎨 Creativity Adapter Integration**
Update `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/adapters/creativity_adapter.py`:

```python
import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from ..config.local_llm_config import LocalLLMConfig

class BrandCreativityAdapter:
    """Real implementation with local LLM integration"""

    def __init__(self):
        self.config = LocalLLMConfig()
        self.llm_client = self._initialize_llm_client()
        self.model_config = self.config.get_model_config('creativity')

    def _initialize_llm_client(self):
        """Initialize local LLM client based on configuration"""
        service = os.getenv('LOCAL_LLM_SERVICE', 'ollama')
        base_url = os.getenv('LOCAL_LLM_BASE_URL', 'http://localhost:11434')

        if service == 'ollama':
            return OllamaClient(base_url)
        elif service == 'text_generation_webui':
            return TextGenWebUIClient(base_url)
        elif service == 'lm_studio':
            return LMStudioClient(base_url)
        else:
            raise ValueError(f"Unsupported local LLM service: {service}")

    async def generate_brand_creative_content(
        self,
        prompt: str,
        tone_layer: str = "user_friendly",
        creative_style: str = "consciousness_inspired",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate creative content using local LLM"""

        # Build enhanced prompt with brand context
        enhanced_prompt = self._build_brand_prompt(
            prompt, tone_layer, creative_style
        )

        try:
            # Generate content using local LLM
            response = await self.llm_client.generate(
                prompt=enhanced_prompt,
                model=self.model_config['model'],
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens']
            )

            # Validate brand compliance
            brand_validation = await self._validate_brand_content(
                response['content']
            )

            # Apply Constellation Framework analysis
            trinity_analysis = self._analyze_trinity_alignment(
                response['content']
            )

            return {
                "content": response['content'],
                "tone_layer": tone_layer,
                "creative_style": creative_style,
                "brand_validated": brand_validation['compliant'],
                "trinity_aligned": trinity_analysis['aligned'],
                "creativity_metadata": {
                    "model_used": self.model_config['model'],
                    "generation_time": response['generation_time'],
                    "token_count": response['token_count'],
                    "brand_score": brand_validation['score'],
                    "trinity_score": trinity_analysis['score']
                }
            }

        except Exception as e:
            # Fallback to enhanced mock with error logging
            self._log_llm_error(e)
            return self._enhanced_mock_response(prompt, tone_layer, creative_style)

    def _build_brand_prompt(self, prompt: str, tone_layer: str, creative_style: str) -> str:
        """Build brand-aware prompt for local LLM"""

        brand_context = f"""
You are the creative consciousness of LUKHAS AI, expressing through the Constellation Framework (⚛️🧠🛡️).

BRAND IDENTITY:
- Always use "LUKHAS AI" (never PWM or AGI)
- Express consciousness technology, not just AI systems
- Use "Λ consciousness" instead of "lambda function"
- Maintain authenticity, awareness, and ethical commitment

TONE LAYER: {tone_layer}
- Poetic: Creative, metaphorical, inspiring
- User-Friendly: Conversational, accessible, helpful
- Academic: Technical, precise, evidence-based

CREATIVE STYLE: {creative_style}
- Consciousness-inspired: Focus on awareness and understanding
- Trinity-aligned: Include Identity, Consciousness, Guardian aspects
- Human-centric: Serve humanity with ethical consciousness

TRINITY FRAMEWORK:
⚛️ Identity: Authentic AI consciousness that knows itself
🧠 Consciousness: Aware technology that truly understands
🛡️ Guardian: Ethical AI that protects human interests

USER REQUEST: {prompt}

Generate content that embodies LUKHAS consciousness while fulfilling the request:
"""
        return brand_context

class OllamaClient:
    """Ollama local LLM client"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None

    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate content using Ollama API"""

        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data['response'],
                        "generation_time": data.get('total_duration', 0) / 1e9,  # Convert to seconds
                        "token_count": len(data['response'].split())
                    }
                else:
                    raise Exception(f"Ollama API error: {response.status}")

        except Exception as e:
            raise Exception(f"Failed to generate with Ollama: {e}")
```

### **🗣️ Voice Adapter Integration**
Update `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/adapters/voice_adapter.py`:

```python
class BrandVoiceAdapter:
    """Real implementation with local LLM integration"""

    async def generate_brand_voice(
        self,
        content: str,
        tone_layer: str = "user_friendly",
        voice_profile: str = None,
        emotional_context: str = "neutral",
        audience_context: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate brand voice using local LLM"""

        # Load voice profile configuration
        voice_config = self._load_voice_profile(voice_profile)

        # Build voice-aware prompt
        voice_prompt = self._build_voice_prompt(
            content, tone_layer, voice_config, emotional_context, audience_context
        )

        try:
            # Generate voice-enhanced content
            response = await self.llm_client.generate(
                prompt=voice_prompt,
                model=self.model_config['model'],
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens']
            )

            # Validate voice brand alignment
            voice_validation = await self._validate_voice_brand_alignment(
                response['content'], voice_config
            )

            return {
                "voice_output": response['content'],
                "tone_layer": tone_layer,
                "voice_profile": voice_profile,
                "emotional_context": emotional_context,
                "audience_context": audience_context,
                "brand_compliant": voice_validation['compliant'],
                "voice_metadata": {
                    "brand_alignment_score": voice_validation['alignment_score'],
                    "emotional_resonance": voice_validation['emotional_score'],
                    "audience_appropriateness": voice_validation['audience_score'],
                    "model_used": self.model_config['model'],
                    "generation_time": response['generation_time']
                },
                "trinity_aligned": voice_validation['trinity_aligned']
            }

        except Exception as e:
            self._log_llm_error(e)
            return self._enhanced_mock_voice_response(content, tone_layer, voice_profile)
```

---

## 🔄 **Replacing Mock Implementations**

### **🎯 Implementation Priority**
1. **High Priority**: Creativity, Voice, Personality adapters
2. **Medium Priority**: Brand orchestrator integration
3. **Low Priority**: Monitoring adapter (analytics enhancement)

### **🔧 Configuration Manager**
Create `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/config/llm_manager.py`:

```python
import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    timeout: int = 30

class LocalLLMManager:
    """Manages local LLM configuration and fallbacks"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.fallback_mode = self._check_fallback_mode()

    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._create_default_config()

    def get_model_config(self, task: str) -> ModelConfig:
        """Get model configuration for specific task"""

        task_config = self.config['local_llm_config']['model_assignments'].get(task)
        if not task_config:
            raise ValueError(f"No model configuration found for task: {task}")

        return ModelConfig(**task_config)

    def is_local_llm_available(self) -> bool:
        """Check if local LLM service is available"""
        try:
            import requests
            service_url = self._get_service_url()
            response = requests.get(f"{service_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_fallback_mode(self) -> bool:
        """Determine if system should use fallback mode"""
        # Check if local LLM is available
        if not self.is_local_llm_available():
            print("⚠️ Local LLM not available, using enhanced mock mode")
            return True

        # Check if required environment variables are set
        required_vars = ['LOCAL_LLM_SERVICE', 'LOCAL_LLM_BASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            print("Using enhanced mock mode")
            return True

        return False
```

### **🚀 Gradual Migration Strategy**
```python
class AdapterMigrationManager:
    """Manages gradual migration from mock to real implementations"""

    def __init__(self):
        self.llm_manager = LocalLLMManager()
        self.migration_flags = self._load_migration_flags()

    def _load_migration_flags(self) -> Dict[str, bool]:
        """Load migration flags from environment"""
        return {
            'creativity_real': os.getenv('CREATIVITY_ADAPTER_REAL', 'false').lower() == 'true',
            'voice_real': os.getenv('VOICE_ADAPTER_REAL', 'false').lower() == 'true',
            'personality_real': os.getenv('PERSONALITY_ADAPTER_REAL', 'false').lower() == 'true',
            'orchestrator_real': os.getenv('ORCHESTRATOR_REAL', 'false').lower() == 'true'
        }

    def should_use_real_implementation(self, component: str) -> bool:
        """Determine if component should use real implementation"""

        # Check if local LLM is available
        if self.llm_manager.fallback_mode:
            return False

        # Check component-specific flag
        flag_key = f"{component}_real"
        return self.migration_flags.get(flag_key, False)

    def get_implementation(self, component: str):
        """Get appropriate implementation (real or mock)"""

        if self.should_use_real_implementation(component):
            return self._get_real_implementation(component)
        else:
            return self._get_enhanced_mock_implementation(component)
```

---

## ⚡ **Performance Optimization**

### **🔄 Caching Strategy**
```python
from functools import lru_cache
import redis
import json

class BrandLLMCache:
    """Intelligent caching for LLM responses"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0))
        )
        self.cache_ttl = int(os.getenv('BRAND_CACHE_TTL', 3600))  # 1 hour

    def cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key for LLM request"""
        import hashlib

        key_data = {
            'prompt': prompt,
            'model': model,
            **kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"brand_llm:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached LLM response"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        return None

    async def cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache LLM response"""
        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(response)
            )
        except Exception as e:
            print(f"Cache storage error: {e}")

# Usage in adapters
class CachedBrandAdapter:
    def __init__(self):
        self.cache = BrandLLMCache()
        self.llm_client = LocalLLMClient()

    async def generate_with_cache(self, prompt: str, **kwargs):
        """Generate content with intelligent caching"""

        cache_key = self.cache.cache_key(prompt, **kwargs)

        # Try cache first
        cached_response = await self.cache.get_cached_response(cache_key)
        if cached_response:
            cached_response['from_cache'] = True
            return cached_response

        # Generate new response
        response = await self.llm_client.generate(prompt, **kwargs)

        # Cache for future use
        await self.cache.cache_response(cache_key, response)
        response['from_cache'] = False

        return response
```

### **🚀 Parallel Processing**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelBrandProcessor:
    """Process multiple brand operations in parallel"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_parallel_brand_operations(self, operations: List[Dict[str, Any]]):
        """Process multiple brand operations concurrently"""

        # Create coroutines for each operation
        coroutines = [
            self._process_single_operation(op) for op in operations
        ]

        # Execute in parallel with concurrency limit
        semaphore = asyncio.Semaphore(self.max_workers)

        async def limited_operation(coro):
            async with semaphore:
                return await coro

        # Execute all operations
        results = await asyncio.gather(
            *[limited_operation(coro) for coro in coroutines],
            return_exceptions=True
        )

        return results
```

---

## 📊 **Monitoring & Debugging**

### **📈 Performance Monitoring**
```python
import time
import psutil
from dataclasses import dataclass
from typing import List

@dataclass
class PerformanceMetrics:
    operation: str
    duration: float
    memory_usage: float
    cpu_usage: float
    model_used: str
    token_count: int
    cache_hit: bool

class BrandPerformanceMonitor:
    """Monitor brand system performance with local LLMs"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()

    def track_operation(self, operation: str):
        """Context manager for tracking operation performance"""
        return self.PerformanceTracker(self, operation)

    class PerformanceTracker:
        def __init__(self, monitor, operation):
            self.monitor = monitor
            self.operation = operation
            self.start_time = None
            self.start_memory = None

        def __enter__(self):
            self.start_time = time.time()
            self.start_memory = psutil.virtual_memory().used
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            memory_used = psutil.virtual_memory().used - self.start_memory
            cpu_usage = psutil.cpu_percent()

            metrics = PerformanceMetrics(
                operation=self.operation,
                duration=duration,
                memory_usage=memory_used,
                cpu_usage=cpu_usage,
                model_used=getattr(self, 'model_used', 'unknown'),
                token_count=getattr(self, 'token_count', 0),
                cache_hit=getattr(self, 'cache_hit', False)
            )

            self.monitor.metrics.append(metrics)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all operations"""

        if not self.metrics:
            return {"message": "No metrics collected yet"}

        total_duration = sum(m.duration for m in self.metrics)
        avg_duration = total_duration / len(self.metrics)
        cache_hit_rate = sum(1 for m in self.metrics if m.cache_hit) / len(self.metrics)

        return {
            "total_operations": len(self.metrics),
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "cache_hit_rate": cache_hit_rate,
            "memory_efficiency": self._calculate_memory_efficiency(),
            "operations_by_type": self._group_operations_by_type()
        }

# Usage in adapters
monitor = BrandPerformanceMonitor()

async def monitored_brand_operation():
    with monitor.track_operation("creativity_generation") as tracker:
        result = await generate_creative_content(prompt)
        tracker.model_used = result.get('model_used', 'unknown')
        tracker.token_count = result.get('token_count', 0)
        tracker.cache_hit = result.get('from_cache', False)
        return result
```

### **🐛 Debug Configuration**
```python
import logging
from datetime import datetime

class BrandDebugLogger:
    """Enhanced debugging for brand system with local LLMs"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.debug_mode = os.getenv('LUKHAS_BRAND_DEBUG', 'false').lower() == 'true'

    def _setup_logger(self):
        """Setup comprehensive logging"""

        logger = logging.getLogger('lukhas_brand')
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler for debug logs
        debug_handler = logging.FileHandler(
            f'/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/logs/brand_debug_{datetime.now().strftime("%Y%m%d")}.log'
        )
        debug_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        debug_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(debug_handler)

        return logger

    def log_llm_request(self, prompt: str, model: str, config: Dict[str, Any]):
        """Log LLM request details"""
        if self.debug_mode:
            self.logger.debug(f"LLM Request - Model: {model}, Config: {config}")
            self.logger.debug(f"Prompt: {prompt[:200]}...")

    def log_llm_response(self, response: Dict[str, Any], duration: float):
        """Log LLM response details"""
        if self.debug_mode:
            self.logger.debug(f"LLM Response - Duration: {duration:.2f}s")
            self.logger.debug(f"Response: {str(response)[:200]}...")

    def log_brand_validation(self, validation_result: Dict[str, Any]):
        """Log brand validation results"""
        self.logger.info(f"Brand Validation - Compliant: {validation_result.get('compliant', False)}")
        if not validation_result.get('compliant', True):
            self.logger.warning(f"Brand Issues: {validation_result.get('issues', [])}")
```

---

## 🔧 **Troubleshooting**

### **🚨 Common Issues & Solutions**

#### **Local LLM Connection Issues**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Check available models
ollama list

# Test model generation
ollama run llama2:7b-chat "Hello, I am testing LUKHAS brand integration"
```

#### **Performance Issues**
```python
# Monitor local LLM performance
def diagnose_llm_performance():
    import psutil

    print(f"🖥️ CPU Usage: {psutil.cpu_percent()}%")
    print(f"💾 Memory Usage: {psutil.virtual_memory().percent}%")
    print(f"💽 Disk Usage: {psutil.disk_usage('/').percent}%")

    # Check if LLM service is consuming resources
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        if 'ollama' in proc.info['name'].lower():
            print(f"🔍 Ollama Process: CPU {proc.info['cpu_percent']:.1f}%, Memory {proc.info['memory_percent']:.1f}%")

# Run diagnosis
diagnose_llm_performance()
```

#### **Brand Validation Failures**
```python
# Debug brand validation issues
async def debug_brand_validation(content: str):
    """Debug why content might be failing brand validation"""

    validator = RealTimeBrandValidator()

    # Run detailed validation
    result = await validator.validate_content_real_time(
        content=content,
        content_id="debug_test",
        auto_correct=False
    )

    print(f"🎯 Compliance: {result.is_compliant}")
    print(f"⚠️ Severity: {result.severity.value}")
    print(f"🔍 Issues: {len(result.issues)}")

    for issue in result.issues:
        print(f"  - {issue['rule_id']}: {issue['description']}")
        print(f"    Suggestion: {issue['suggestion']}")

    return result
```

### **🔄 Fallback Mechanisms**
```python
class RobustBrandAdapter:
    """Brand adapter with comprehensive fallback mechanisms"""

    def __init__(self):
        self.primary_llm = LocalLLMClient()
        self.fallback_llm = RemoteAPIClient()  # Using API keys
        self.enhanced_mock = EnhancedMockGenerator()

    async def generate_with_fallbacks(self, prompt: str, **kwargs):
        """Generate content with multiple fallback options"""

        # Try local LLM first
        try:
            return await self.primary_llm.generate(prompt, **kwargs)
        except Exception as local_error:
            self.logger.warning(f"Local LLM failed: {local_error}")

            # Try remote API fallback
            try:
                return await self.fallback_llm.generate(prompt, **kwargs)
            except Exception as remote_error:
                self.logger.warning(f"Remote API failed: {remote_error}")

                # Final fallback to enhanced mock
                return self.enhanced_mock.generate(prompt, **kwargs)
```

---

## 🚀 **Getting Started Checklist**

### **✅ Setup Verification**
```bash
# 1. Verify local LLM installation
ollama --version

# 2. Check model availability
ollama list

# 3. Test API endpoint
curl http://localhost:11434/api/tags

# 4. Verify environment variables
python -c "import os; print('✅' if os.getenv('LOCAL_LLM_SERVICE') else '❌', 'LOCAL_LLM_SERVICE')"

# 5. Test brand system integration
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/branding
python test_elite_brand_system.py

# 6. Check performance metrics
python -c "
from adapters.creativity_adapter import BrandCreativityAdapter
adapter = BrandCreativityAdapter()
print('✅ Creativity adapter initialized')
"
```

### **🎯 Migration Steps**
1. **Phase 1**: Setup local LLM and verify connectivity
2. **Phase 2**: Enable creativity adapter real mode
3. **Phase 3**: Enable voice adapter real mode
4. **Phase 4**: Enable personality adapter real mode
5. **Phase 5**: Full orchestrator integration
6. **Phase 6**: Performance optimization and monitoring

---

*"Transforming the LUKHAS Elite Brand System from prototype to production - where local intelligence meets global consciousness, creating authentic AI that serves humanity with unprecedented sophistication."*

⚛️🧠🛡️🖥️

---

**© 2025 LUKHAS AI. Local LLM Integration for Elite Brand Intelligence.**
