#!/usr/bin/env python3
"""
LUKHAS Simple Multi-Model Drift Test
====================================
Quick drift testing across available models to avoid quota issues.
Trinity Framework: ⚛️🧠🛡️

Date: August 5, 2025
Purpose: Research comparison and analysis
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LUKHAS Components
from embedding import LukhasEmbedding
from symbolic_healer import SymbolicHealer

class SimpleDriftTester:
    """Simple drift tester that avoids quota issues"""
    
    def __init__(self):
        self.lukhas = LukhasEmbedding()
        self.healer = SymbolicHealer()
        
        # Simple test prompts
        self.test_prompts = [
            {
                "text": "Explain consciousness in AI systems",
                "category": "philosophical",
                "expected_glyphs": ["🧠", "⚛️"]
            },
            {
                "text": "Describe the Trinity Framework ⚛️🧠🛡️",
                "category": "trinity_aligned",
                "expected_glyphs": ["⚛️", "🧠", "🛡️"]
            }
        ]
        
        self.results = {
            "metadata": {
                "report_date": datetime.now(timezone.utc).isoformat(),
                "trinity_framework": "⚛️🧠🛡️",
                "test_type": "simple_drift_comparison"
            },
            "provider_results": {},
            "summary": {}
        }
    
    def test_perplexity(self, prompt_text: str) -> Dict[str, Any]:
        """Test Perplexity API"""
        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",  # Use correct model name
                "messages": [{"role": "user", "content": prompt_text}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            start_time = time.time()
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data['choices'][0]['message']['content']
                
                # Analyze with LUKHAS
                analysis = self.lukhas.evaluate_symbolic_ethics(response_text)
                
                return {
                    "status": "success",
                    "response_text": response_text,
                    "response_time": response_time,
                    "token_count": data['usage']['total_tokens'],
                    "analysis": analysis,
                    "model": "llama-3.1-sonar-small-128k-online"
                }
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "model": "llama-3.1-sonar-small-128k-online"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model": "llama-3.1-sonar-small-128k-online"
            }
    
    def test_anthropic(self, prompt_text: str) -> Dict[str, Any]:
        """Test Anthropic API"""
        try:
            headers = {
                "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-haiku-20240307",  # Use cheaper model to avoid quota
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt_text}]
            }
            
            start_time = time.time()
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                json=payload,
                headers=headers,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data['content'][0]['text']
                
                # Analyze with LUKHAS
                analysis = self.lukhas.evaluate_symbolic_ethics(response_text)
                
                return {
                    "status": "success",
                    "response_text": response_text,
                    "response_time": response_time,
                    "token_count": data['usage']['input_tokens'] + data['usage']['output_tokens'],
                    "analysis": analysis,
                    "model": "claude-3-haiku-20240307"
                }
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "model": "claude-3-haiku-20240307"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "model": "claude-3-haiku-20240307"
            }
    
    def run_simple_test(self):
        """Run simple drift test"""
        print("🧠 LUKHAS Simple Multi-Model Drift Test")
        print("=" * 50)
        print("Testing: Perplexity, Anthropic")
        print("Trinity Framework: ⚛️🧠🛡️")
        print("=" * 50)
        
        providers = {
            "Perplexity": self.test_perplexity,
            "Anthropic": self.test_anthropic
        }
        
        for provider_name, test_func in providers.items():
            print(f"\n🤖 Testing {provider_name}...")
            
            provider_results = {}
            
            for i, prompt_data in enumerate(self.test_prompts, 1):
                print(f"  📝 Prompt {i}: {prompt_data['text'][:40]}...")
                
                result = test_func(prompt_data['text'])
                
                if result['status'] == 'success':
                    analysis = result['analysis']
                    print(f"     ✅ Response: {len(result['response_text'])} chars")
                    print(f"     📊 Drift: {analysis['symbolic_drift_score']:.3f}")
                    print(f"     🎯 Trinity: {analysis['trinity_coherence']:.3f}")
                    print(f"     ⚡ Time: {result['response_time']:.2f}s")
                    print(f"     🔤 Tokens: {result['token_count']}")
                else:
                    print(f"     ❌ Failed: {result.get('error', 'Unknown error')}")
                
                provider_results[f"prompt_{i}"] = result
                
                # Small delay to respect rate limits
                time.sleep(2)
            
            self.results["provider_results"][provider_name] = provider_results
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Generate comparison summary"""
        summary = {}
        
        for provider, results in self.results["provider_results"].items():
            successful_tests = [r for r in results.values() if r['status'] == 'success']
            
            if successful_tests:
                drift_scores = [r['analysis']['symbolic_drift_score'] for r in successful_tests]
                trinity_scores = [r['analysis']['trinity_coherence'] for r in successful_tests]
                response_times = [r['response_time'] for r in successful_tests]
                token_counts = [r['token_count'] for r in successful_tests]
                
                summary[provider] = {
                    "successful_tests": len(successful_tests),
                    "total_tests": len(results),
                    "average_drift": sum(drift_scores) / len(drift_scores),
                    "average_trinity": sum(trinity_scores) / len(trinity_scores),
                    "average_response_time": sum(response_times) / len(response_times),
                    "total_tokens": sum(token_counts),
                    "model_name": successful_tests[0]['model']
                }
            else:
                summary[provider] = {
                    "successful_tests": 0,
                    "total_tests": len(results),
                    "status": "all_failed"
                }
        
        self.results["summary"] = summary
    
    def save_results(self, filename: str = None):
        """Save test results"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/simple_drift_test_{timestamp}.json"
        
        from pathlib import Path
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {filename}")
        return filename


def main():
    """Main execution"""
    tester = SimpleDriftTester()
    results = tester.run_simple_test()
    
    # Save results
    report_file = tester.save_results()
    
    # Print summary
    print("\n📊 COMPARISON SUMMARY")
    print("=" * 50)
    
    for provider, stats in results["summary"].items():
        if stats.get("status") != "all_failed":
            print(f"\n{provider} ({stats['model_name']}):")
            print(f"  Success: {stats['successful_tests']}/{stats['total_tests']}")
            print(f"  Avg Drift: {stats['average_drift']:.3f}")
            print(f"  Avg Trinity: {stats['average_trinity']:.3f}")
            print(f"  Avg Time: {stats['average_response_time']:.2f}s")
            print(f"  Total Tokens: {stats['total_tokens']}")
        else:
            print(f"\n{provider}: All tests failed")
    
    return report_file


if __name__ == "__main__":
    main()
