#!/usr/bin/env python3
"""
Multi-LLM API Testing Suite for LUKHAS AI
==========================================

Tests all available LLM APIs with minimal token usage to verify connections
before beginning cost-optimized promotions.

APIs Tested:
- OpenAI (with org/project ID)
- Anthropic Claude  
- Google Gemini
- Perplexity
- Local Ollama (DeepSeek Coder, Llama 3.2)
"""

import os
import sys
import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# API client imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

class APITester:
    """Test suite for all LLM APIs"""
    
    def __init__(self):
        self.results = {}
        self.total_cost_estimate = 0.0
        
    def log_result(self, api_name: str, success: bool, message: str, cost_estimate: float = 0.0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results[api_name] = {
            "success": success,
            "message": message,
            "cost_estimate": cost_estimate,
            "timestamp": datetime.now().isoformat()
        }
        self.total_cost_estimate += cost_estimate
        print(f"{status} {api_name}: {message}")
        if cost_estimate > 0:
            print(f"   💰 Estimated cost: ${cost_estimate:.4f}")
    
    def test_openai_api(self) -> bool:
        """Test OpenAI API with organization and project ID"""
        if not OPENAI_AVAILABLE:
            self.log_result("OpenAI", False, "OpenAI library not installed")
            return False
            
        api_key = os.getenv("OPENAI_API_KEY")
        org_id = os.getenv("OPENAI_ORG_ID")
        project_id = os.getenv("OPENAI_PROJECT_ID")
        
        if not api_key:
            self.log_result("OpenAI", False, "OPENAI_API_KEY not found in .env")
            return False
            
        try:
            client = openai.OpenAI(
                api_key=api_key,
                organization=org_id,
                project=project_id
            )
            
            # Test with minimal tokens using cheapest model
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            # Estimate cost: gpt-4o-mini is ~$0.00015/1K input, $0.0006/1K output
            cost = (4 * 0.00015 + 5 * 0.0006) / 1000  # ~$0.0000036
            
            self.log_result("OpenAI", True, f"Connection successful with gpt-4o-mini", cost)
            return True
            
        except Exception as e:
            self.log_result("OpenAI", False, f"Connection failed: {str(e)}")
            return False
    
    def test_anthropic_api(self) -> bool:
        """Test Anthropic Claude API"""
        if not ANTHROPIC_AVAILABLE:
            self.log_result("Anthropic", False, "Anthropic library not installed")
            return False
            
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.log_result("Anthropic", False, "ANTHROPIC_API_KEY not found in .env")
            return False
            
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # Test with minimal tokens using cheapest model
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Test"}]
            )
            
            # Estimate cost: Claude Haiku is ~$0.00025/1K input, $0.00125/1K output
            cost = (4 * 0.00025 + 5 * 0.00125) / 1000  # ~$0.0000073
            
            self.log_result("Anthropic", True, f"Connection successful with Claude Haiku", cost)
            return True
            
        except Exception as e:
            self.log_result("Anthropic", False, f"Connection failed: {str(e)}")
            return False
    
    def test_google_api(self) -> bool:
        """Test Google Gemini API"""
        if not GOOGLE_AVAILABLE:
            self.log_result("Google", False, "Google GenerativeAI library not installed")
            return False
            
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.log_result("Google", False, "GOOGLE_API_KEY not found in .env")
            return False
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test with minimal tokens
            response = model.generate_content(
                "Test",
                generation_config=genai.types.GenerationConfig(max_output_tokens=5)
            )
            
            # Estimate cost: Gemini Flash is ~$0.00035/1K input, $0.00105/1K output
            cost = (4 * 0.00035 + 5 * 0.00105) / 1000  # ~$0.0000067
            
            self.log_result("Google", True, f"Connection successful with Gemini Flash", cost)
            return True
            
        except Exception as e:
            self.log_result("Google", False, f"Connection failed: {str(e)}")
            return False
    
    def test_perplexity_api(self) -> bool:
        """Test Perplexity API"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            self.log_result("Perplexity", False, "PERPLEXITY_API_KEY not found in .env")
            return False
            
        try:
            # Perplexity uses OpenAI-compatible API
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            
            # Test with minimal tokens using cheapest model
            response = client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-chat",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            # Estimate cost: Perplexity Sonar Small is ~$0.0002/1K input, $0.0002/1K output
            cost = (4 * 0.0002 + 5 * 0.0002) / 1000  # ~$0.0000018
            
            self.log_result("Perplexity", True, f"Connection successful with Sonar Small", cost)
            return True
            
        except Exception as e:
            self.log_result("Perplexity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_local_ollama(self) -> bool:
        """Test local Ollama models"""
        try:
            # Test Ollama API server
            response = requests.get("http://localhost:11434/api/tags", timeout=15)
            if response.status_code != 200:
                self.log_result("Ollama", False, "Ollama server not running. Start with: ollama serve")
                return False
                
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            # Check for our required models
            deepseek_available = any("deepseek-coder" in name for name in model_names)
            llama_available = any("llama3.2" in name for name in model_names)
            
            if not deepseek_available:
                self.log_result("Ollama", False, "DeepSeek Coder not found. Install with: ollama pull deepseek-coder:6.7b")
                return False
                
            if not llama_available:
                self.log_result("Ollama", False, "Llama 3.2 not found. Install with: ollama pull llama3.2:1b")
                return False
            
            # Test actual inference
            test_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": "Say 'OK' to confirm local LLM working",
                    "stream": False
                },
                timeout=30
            )
            
            if test_response.status_code == 200:
                self.log_result("Ollama", True, f"Local LLMs working: DeepSeek Coder + Llama 3.2 (FREE)", 0.0)
                return True
            else:
                self.log_result("Ollama", False, f"Inference test failed: {test_response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_result("Ollama", False, "Cannot connect to Ollama. Start with: ollama serve")
            return False
        except Exception as e:
            self.log_result("Ollama", False, f"Unexpected error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests"""
        print("🤖 LUKHAS AI - Multi-LLM API Testing Suite")
        print("=" * 50)
        print()
        
        # Test all APIs
        print("📡 Testing API Connections...")
        print()
        
        openai_ok = self.test_openai_api()
        claude_ok = self.test_anthropic_api()
        google_ok = self.test_google_api()
        perplexity_ok = self.test_perplexity_api()
        ollama_ok = self.test_local_ollama()
        
        print()
        print("📊 Test Summary:")
        print("-" * 30)
        
        total_apis = 5
        working_apis = sum([openai_ok, claude_ok, google_ok, perplexity_ok, ollama_ok])
        
        print(f"APIs Working: {working_apis}/{total_apis}")
        print(f"Estimated Test Cost: ${self.total_cost_estimate:.6f}")
        print()
        
        # Recommendations
        if ollama_ok:
            print("💡 Recommendations:")
            print("- Use local LLMs (DeepSeek + Llama) for 80% of work (FREE)")
            if claude_ok:
                print("- Use Claude Haiku for safety validation (~$0.50/module)")
            if openai_ok:
                print("- Use GPT-4o-mini for complex architecture (~$1.00/module)")
            if google_ok:
                print("- Use Gemini Flash as backup option")
            if perplexity_ok:
                print("- Use Perplexity for research tasks")
        else:
            print("⚠️  Local LLMs not available - will rely on API models (higher cost)")
            
        print()
        print("🎯 Ready for budget-optimized promotions!")
        
        return {
            "working_apis": working_apis,
            "total_apis": total_apis,
            "estimated_cost": self.total_cost_estimate,
            "results": self.results,
            "local_available": ollama_ok
        }

def main():
    """Main test runner"""
    tester = APITester()
    results = tester.run_all_tests()
    
    # Save results
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: api_test_results.json")
    
    # Exit with appropriate code
    if results["working_apis"] >= 3:  # Need at least 3 working APIs
        print("✅ API tests passed - ready for promotions!")
        sys.exit(0)
    else:
        print("❌ Insufficient APIs working - check configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()