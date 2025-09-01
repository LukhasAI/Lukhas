#!/usr/bin/env python3
"""
LUKHAS Ollama Manager
Delegated management system for Ollama models and operations
Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import aiohttp


@dataclass
class ModelInfo:
    """Information about an Ollama model"""

    name: str
    size: str
    modified: str
    parameter_size: str
    quantization: str
    family: str
    recommended_for: list[str]
    performance_score: float  # 0-1, higher is better
    accuracy_score: float  # 0-1, higher is better


class OllamaManager:
    """
    Comprehensive Ollama management system for LUKHAS
    I'll handle all Ollama operations for you!
    """

    # Recommended models for different tasks
    RECOMMENDED_MODELS = {
        "code_fixing": {
            "primary": "deepseek-coder:6.7b",
            "alternatives": ["codellama:7b", "qwen2.5-coder:7b", "starcoder2:7b"],
        },
        "code_generation": {
            "primary": "codellama:13b",
            "alternatives": ["deepseek-coder:6.7b", "wizardcoder:7b"],
        },
        "documentation": {
            "primary": "mistral:7b",
            "alternatives": ["llama3.2:3b", "phi3:mini"],
        },
        "quick_fixes": {
            "primary": "qwen2.5-coder:1.5b",
            "alternatives": ["codegemma:2b", "phi3:mini"],
        },
    }

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.installed_models: dict[str, ModelInfo] = {}
        self.model_performance: dict[str, dict] = {}
        self.usage_stats: dict[str, dict] = {}

    async def health_check(self) -> dict:
        """Comprehensive health check of Ollama system"""
        health = {
            "status": "unknown",
            "service_running": False,
            "api_responsive": False,
            "models_loaded": 0,
            "disk_usage": None,
            "memory_usage": None,
            "recommendations": [],
        }

        # Check if service is running
        try:
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True)
            health["service_running"] = result.returncode == 0
        except:
            health["recommendations"].append("Install Ollama: brew install ollama")

        # Check API responsiveness
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(f"{self.ollama_host}/api/tags", timeout=5) as resp,
            ):
                if resp.status == 200:
                    health["api_responsive"] = True
                    data = await resp.json()
                    health["models_loaded"] = len(data.get("models", []))
        except:
            if health["service_running"]:
                health["recommendations"].append("Start Ollama service: ollama serve")

        # Check disk usage
        try:
            models_path = Path.home() / ".ollama" / "models"
            if models_path.exists():
                size = sum(f.stat().st_size for f in models_path.rglob("*") if f.is_file())
                health["disk_usage"] = f"{size / (1024**3):.2f} GB"
        except:
            pass

        # Overall status
        if health["api_responsive"] and health["models_loaded"] > 0:
            health["status"] = "healthy"
        elif health["api_responsive"]:
            health["status"] = "needs_models"
            health["recommendations"].append("Install recommended models")
        elif health["service_running"]:
            health["status"] = "service_issue"
        else:
            health["status"] = "not_running"

        return health

    async def list_installed_models(self) -> list[ModelInfo]:
        """Get detailed info about installed models"""
        models = []

        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            name = parts[0]
                            # Get detailed info
                            info = await self._get_model_details(name)
                            models.append(info)
                            self.installed_models[name] = info
        except Exception as e:
            print(f"Error listing models: {e}")

        return models

    async def _get_model_details(self, model_name: str) -> ModelInfo:
        """Get detailed information about a model"""
        # Extract base info from name
        size = "unknown"
        if "1.5b" in model_name.lower():
            size = "1.5B"
            perf = 0.9
            acc = 0.6
        elif "3b" in model_name.lower():
            size = "3B"
            perf = 0.8
            acc = 0.7
        elif "7b" in model_name.lower():
            size = "7B"
            perf = 0.6
            acc = 0.85
        elif "13b" in model_name.lower():
            size = "13B"
            perf = 0.4
            acc = 0.9
        else:
            perf = 0.5
            acc = 0.5

        # Determine recommended uses
        recommended = []
        if "code" in model_name.lower() or "deepseek" in model_name.lower():
            recommended = ["code_fixing", "code_generation"]
        elif "llama" in model_name.lower():
            recommended = ["code_fixing", "documentation"]
        elif "mistral" in model_name.lower():
            recommended = ["documentation", "quick_fixes"]
        elif "qwen" in model_name.lower():
            recommended = ["quick_fixes", "code_fixing"]

        return ModelInfo(
            name=model_name,
            size=size,
            modified="recent",
            parameter_size=size,
            quantization="Q4_K_M",
            family=model_name.split(":")[0],
            recommended_for=recommended,
            performance_score=perf,
            accuracy_score=acc,
        )

    async def recommend_models(self, task: str = "code_fixing") -> dict:
        """Recommend models for specific tasks"""
        recommendations = {
            "task": task,
            "installed": [],
            "recommended_to_install": [],
            "current_best": None,
        }

        # Get installed models
        installed = await self.list_installed_models()

        # Check what's recommended for this task
        task_models = self.RECOMMENDED_MODELS.get(task, self.RECOMMENDED_MODELS["code_fixing"])

        # Find installed models good for this task
        for model in installed:
            if task in model.recommended_for:
                recommendations["installed"].append(
                    {
                        "name": model.name,
                        "performance": model.performance_score,
                        "accuracy": model.accuracy_score,
                        "score": (model.performance_score + model.accuracy_score) / 2,
                    }
                )

        # Sort by score
        recommendations["installed"].sort(key=lambda x: x["score"], reverse=True)

        if recommendations["installed"]:
            recommendations["current_best"] = recommendations["installed"][0]["name"]

        # Recommend models to install
        installed_names = [m.name for m in installed]

        if task_models["primary"] not in installed_names:
            recommendations["recommended_to_install"].append(
                {
                    "name": task_models["primary"],
                    "reason": f"Best model for {task}",
                    "command": f"ollama pull {task_models['primary']}",
                }
            )

        for alt in task_models["alternatives"][:2]:
            if alt not in installed_names:
                recommendations["recommended_to_install"].append(
                    {
                        "name": alt,
                        "reason": f"Good alternative for {task}",
                        "command": f"ollama pull {alt}",
                    }
                )

        return recommendations

    async def install_model(self, model_name: str, force: bool = False) -> bool:
        """Install a model with progress tracking"""
        print(f"\n📦 Installing {model_name}...")

        # Check if already installed
        if not force:
            installed = await self.list_installed_models()
            if any(m.name == model_name for m in installed):
                print(f"✅ {model_name} is already installed")
                return True

        # Pull the model
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # Show progress
            for line in iter(process.stdout.readline, ""):
                if line:
                    # Parse progress if available
                    if "pulling" in line.lower() or "%" in line:
                        print(f"  {line.strip()}")

            process.wait()

            if process.returncode == 0:
                print(f"✅ Successfully installed {model_name}")
                return True
            else:
                print(f"❌ Failed to install {model_name}")
                return False

        except Exception as e:
            print(f"❌ Error installing model: {e}")
            return False

    async def optimize_models(self) -> dict:
        """Optimize model selection based on usage patterns"""
        optimization = {
            "current_models": [],
            "suggested_removes": [],
            "suggested_installs": [],
            "disk_saved": 0,
            "performance_gain": 0,
        }

        # Get current models
        installed = await self.list_installed_models()
        optimization["current_models"] = [m.name for m in installed]

        # Analyze usage (would need actual usage tracking)
        # For now, use heuristics

        # Suggest removing large, unused models
        for model in installed:
            if "13b" in model.name.lower() or "34b" in model.name.lower():
                optimization["suggested_removes"].append(
                    {
                        "model": model.name,
                        "reason": "Large model, consider smaller alternative",
                        "disk_saved": "5-20 GB",
                    }
                )

        # Suggest optimal models for tasks
        for task in ["code_fixing", "quick_fixes"]:
            recs = await self.recommend_models(task)
            if recs["recommended_to_install"]:
                optimization["suggested_installs"].extend(recs["recommended_to_install"][:1])

        return optimization

    async def benchmark_model(self, model_name: str, test_type: str = "code_fix") -> dict:
        """Benchmark a model's performance"""
        print(f"\n🧪 Benchmarking {model_name}...")

        benchmarks = {
            "model": model_name,
            "test_type": test_type,
            "response_time": 0,
            "accuracy": 0,
            "memory_usage": 0,
            "tokens_per_second": 0,
        }

        # Test prompts
        test_prompts = {
            "code_fix": "Fix this Python syntax error: print('Hello World'",
            "code_generate": "Write a Python function to calculate fibonacci numbers",
            "explain": "Explain what a Python decorator is",
        }

        prompt = test_prompts.get(test_type, test_prompts["code_fix"])

        try:
            start_time = time.time()

            # Run test
            result = subprocess.run(
                ["ollama", "run", model_name, prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )

            end_time = time.time()
            benchmarks["response_time"] = end_time - start_time

            # Estimate tokens/second (rough estimate)
            response_length = len(result.stdout.split())
            benchmarks["tokens_per_second"] = response_length / benchmarks["response_time"]

            # Check if response is valid
            if result.returncode == 0 and len(result.stdout) > 10:
                benchmarks["accuracy"] = 0.8  # Would need proper evaluation

            # Store performance data
            if model_name not in self.model_performance:
                self.model_performance[model_name] = []

            self.model_performance[model_name].append(benchmarks)

            print(f"  ⏱️  Response time: {benchmarks['response_time']:.2f}s")
            print(f"  💨 Tokens/second: {benchmarks['tokens_per_second']:.1f}")

        except subprocess.TimeoutExpired:
            benchmarks["response_time"] = 30
            print("  ⚠️  Model timed out")
        except Exception as e:
            print(f"  ❌ Benchmark failed: {e}")

        return benchmarks

    async def auto_manage(self) -> dict:
        """Automatic management based on best practices"""
        print("\n🤖 Running Automatic Ollama Management...")

        actions = {
            "health_check": {},
            "optimizations": {},
            "installations": [],
            "benchmarks": [],
            "final_recommendations": [],
        }

        # 1. Health check
        print("\n1️⃣ Health Check...")
        actions["health_check"] = await self.health_check()
        print(f"   Status: {actions['health_check']['status']}")

        # 2. Optimize models
        print("\n2️⃣ Optimizing Models...")
        actions["optimizations"] = await self.optimize_models()

        # 3. Install recommended models if needed
        print("\n3️⃣ Checking Recommended Models...")
        for task in ["code_fixing", "quick_fixes"]:
            recs = await self.recommend_models(task)

            if not recs["current_best"] and recs["recommended_to_install"]:
                model_to_install = recs["recommended_to_install"][0]
                print(f"   📦 Installing {model_to_install['name']} for {task}")

                if await self.install_model(model_to_install["name"]):
                    actions["installations"].append(model_to_install["name"])

        # 4. Benchmark installed models
        print("\n4️⃣ Benchmarking Models...")
        installed = await self.list_installed_models()
        for model in installed[:3]:  # Benchmark top 3
            benchmark = await self.benchmark_model(model.name)
            actions["benchmarks"].append(benchmark)

        # 5. Final recommendations
        print("\n5️⃣ Generating Recommendations...")

        # Find best model for code tasks
        best_model = None
        best_score = 0

        for benchmark in actions["benchmarks"]:
            score = benchmark["tokens_per_second"] / max(1, benchmark["response_time"])
            if score > best_score:
                best_score = score
                best_model = benchmark["model"]

        if best_model:
            actions["final_recommendations"].append(f"Use {best_model} for best performance")

        # Memory recommendations
        if actions["health_check"]["disk_usage"]:
            disk_gb = float(actions["health_check"]["disk_usage"].split()[0])
            if disk_gb > 20:
                actions["final_recommendations"].append("Consider removing large models to save disk space")

        return actions

    def generate_config(self) -> dict:
        """Generate optimal configuration for LUKHAS"""
        config = {
            "primary_model": "codellama:7b",
            "fallback_model": "qwen2.5-coder:1.5b",
            "quick_fix_model": "qwen2.5-coder:1.5b",
            "documentation_model": "mistral:7b",
            "temperature": 0.3,
            "max_tokens": 500,
            "timeout": 30,
            "retry_attempts": 3,
            "guardian_threshold": 0.85,
        }

        # Adjust based on installed models
        if "deepseek-coder:6.7b" in self.installed_models:
            config["primary_model"] = "deepseek-coder:6.7b"
        elif "codellama:7b" in self.installed_models:
            config["primary_model"] = "codellama:7b"

        return config

    async def monitor_performance(self, duration: int = 60) -> dict:
        """Monitor Ollama performance over time"""
        print(f"\n📊 Monitoring Ollama for {duration} seconds...")

        metrics = {
            "start_time": datetime.now().isoformat(),
            "duration": duration,
            "api_calls": 0,
            "avg_response_time": 0,
            "errors": 0,
            "memory_samples": [],
        }

        response_times = []
        start = time.time()

        while time.time() - start < duration:
            try:
                # Make a simple API call
                call_start = time.time()
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(f"{self.ollama_host}/api/tags", timeout=5) as resp,
                ):
                    if resp.status == 200:
                        metrics["api_calls"] += 1
                        response_times.append(time.time() - call_start)
                    else:
                        metrics["errors"] += 1
            except:
                metrics["errors"] += 1

            # Sample every 5 seconds
            await asyncio.sleep(5)

        if response_times:
            metrics["avg_response_time"] = sum(response_times) / len(response_times)

        print(f"   📈 API Calls: {metrics['api_calls']}")
        print(f"   ⏱️  Avg Response: {metrics['avg_response_time']:.3f}s")
        print(f"   ❌ Errors: {metrics['errors']}")

        return metrics


async def main():
    """Main management interface"""
    manager = OllamaManager()

    print("🤖 LUKHAS Ollama Manager")
    print("=" * 50)

    # Run automatic management
    results = await manager.auto_manage()

    # Generate optimal config
    config = manager.generate_config()

    # Save configuration
    config_path = Path(".env.ollama")
    with open(config_path, "w") as f:
        for key, value in config.items():
            f.write(f"{key.upper()}={value}\n")

    print("\n" + "=" * 50)
    print("✅ Management Complete!")
    print(f"   Models Installed: {len(results['health_check'].get('models_loaded', 0))}")
    print(f"   Status: {results['health_check']['status']}")
    print(f"   Config saved to: {config_path}")

    if results["final_recommendations"]:
        print("\n📋 Recommendations:")
        for rec in results["final_recommendations"]:
            print(f"   • {rec}")

    return results


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
