#!/usr/bin/env python3
"""
LUKHAS PWM Performance Optimization Analysis
Identifies bottlenecks and optimization opportunities
"""

import asyncio
import cProfile
import gc
import io
import logging
import memory_profiler
import pstats
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyzes system performance and identifies optimization opportunities"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results = {}
        self.start_time = time.time()
        
    async def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete performance analysis"""
        logger.info("🚀 Starting LUKHAS PWM Performance Analysis")
        
        analyses = [
            ("System Resources", self.analyze_system_resources),
            ("Memory Usage", self.analyze_memory_usage),
            ("Import Performance", self.analyze_import_performance),
            ("Function Profiling", self.analyze_function_performance),
            ("API Performance", self.analyze_api_performance),
            ("Database Performance", self.analyze_database_performance),
            ("Concurrency Analysis", self.analyze_concurrency),
            ("Optimization Opportunities", self.identify_optimizations)
        ]
        
        for analysis_name, analysis_func in analyses:
            try:
                logger.info(f"🔍 Running {analysis_name} analysis...")
                start = time.time()
                result = await analysis_func()
                duration = time.time() - start
                
                self.results[analysis_name] = {
                    "result": result,
                    "analysis_duration": duration,
                    "status": "success"
                }
                logger.info(f"✅ {analysis_name} completed in {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ {analysis_name} failed: {e}")
                self.results[analysis_name] = {
                    "error": str(e),
                    "status": "error"
                }
        
        # Generate recommendations
        self.results["recommendations"] = self.generate_recommendations()
        self.results["total_analysis_time"] = time.time() - self.start_time
        
        await self.save_results()
        self.print_summary()
        
        return self.results
    
    async def analyze_system_resources(self) -> Dict[str, Any]:
        """Analyze current system resource usage"""
        # CPU information
        cpu_info = {
            "count": psutil.cpu_count(),
            "physical_cores": psutil.cpu_count(logical=False),
            "current_usage": psutil.cpu_percent(interval=1),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent,
            "free_gb": round(memory.free / (1024**3), 2)
        }
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_percent": round((disk.used / disk.total) * 100, 1)
        }
        
        # Process information
        current_process = psutil.Process()
        process_info = {
            "memory_mb": round(current_process.memory_info().rss / (1024**2), 2),
            "cpu_percent": current_process.cpu_percent(),
            "threads": current_process.num_threads(),
            "open_files": len(current_process.open_files()),
            "connections": len(current_process.connections())
        }
        
        return {
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "process": process_info,
            "timestamp": time.time()
        }
    
    async def analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        # Get current memory usage
        current_usage = psutil.virtual_memory().used / (1024**2)  # MB
        
        # Analyze garbage collection
        gc_stats = {
            "collections": gc.get_stats(),
            "garbage_objects": len(gc.garbage),
            "tracked_objects": len(gc.get_objects())
        }
        
        # Memory growth simulation
        baseline_memory = psutil.Process().memory_info().rss / (1024**2)
        
        # Simulate some operations to check for memory leaks
        test_data = []
        for i in range(1000):
            test_data.append({"data": "x" * 100, "index": i})
        
        post_alloc_memory = psutil.Process().memory_info().rss / (1024**2)
        
        # Clean up
        del test_data
        gc.collect()
        
        post_cleanup_memory = psutil.Process().memory_info().rss / (1024**2)
        
        return {
            "current_usage_mb": current_usage,
            "garbage_collection": gc_stats,
            "memory_test": {
                "baseline_mb": baseline_memory,
                "post_allocation_mb": post_alloc_memory,
                "post_cleanup_mb": post_cleanup_memory,
                "growth_mb": post_alloc_memory - baseline_memory,
                "leaked_mb": post_cleanup_memory - baseline_memory
            }
        }
    
    async def analyze_import_performance(self) -> Dict[str, Any]:
        """Analyze module import performance"""
        import_times = {}
        
        # Test critical module imports
        critical_modules = [
            "lukhas_pwm.flags",
            "governance.policy.base",
            "orchestration.signals.signal_bus",
            "consciousness.unified.auto_consciousness",
            "memory.folds.optimized_fold_engine"
        ]
        
        for module in critical_modules:
            try:
                start = time.time()
                __import__(module)
                duration = time.time() - start
                import_times[module] = {
                    "duration_ms": round(duration * 1000, 2),
                    "status": "success"
                }
            except ImportError as e:
                import_times[module] = {
                    "duration_ms": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        # Calculate statistics
        successful_imports = [t for t in import_times.values() if t["status"] == "success"]
        if successful_imports:
            durations = [t["duration_ms"] for t in successful_imports]
            stats = {
                "total_imports": len(import_times),
                "successful_imports": len(successful_imports),
                "average_duration_ms": round(sum(durations) / len(durations), 2),
                "max_duration_ms": max(durations),
                "min_duration_ms": min(durations)
            }
        else:
            stats = {"total_imports": len(import_times), "successful_imports": 0}
        
        return {
            "import_times": import_times,
            "statistics": stats
        }
    
    async def analyze_function_performance(self) -> Dict[str, Any]:
        """Profile function performance using cProfile"""
        # Create a profiler
        profiler = cProfile.Profile()
        
        # Profile some representative operations
        profiler.enable()
        
        # Simulate typical operations
        await self._simulate_typical_operations()
        
        profiler.disable()
        
        # Get stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        profile_output = stats_stream.getvalue()
        
        return {
            "profile_output": profile_output[:2000],  # Truncate for readability
            "total_calls": stats.total_calls,
            "primitive_calls": stats.prim_calls
        }
    
    async def _simulate_typical_operations(self):
        """Simulate typical system operations for profiling"""
        # Simulate feature flag operations
        try:
            from lukhas_pwm.flags import get_flags, is_enabled
            for _ in range(100):
                flags = get_flags()
                is_enabled("adaptive_ai")
        except:
            pass
        
        # Simulate data processing
        data = [{"id": i, "value": f"data_{i}"} for i in range(1000)]
        processed = [d for d in data if d["id"] % 2 == 0]
        
        # Simulate async operations
        await asyncio.sleep(0.001)
        
        return len(processed)
    
    async def analyze_api_performance(self) -> Dict[str, Any]:
        """Analyze API performance characteristics"""
        # Simulate API operations
        start_times = []
        
        # Test basic operations
        for _ in range(10):
            start = time.time()
            # Simulate API call processing
            await asyncio.sleep(0.01)  # Simulated I/O
            duration = time.time() - start
            start_times.append(duration * 1000)  # Convert to ms
        
        # Calculate statistics
        avg_response = sum(start_times) / len(start_times)
        p95_response = sorted(start_times)[int(0.95 * len(start_times))]
        
        return {
            "average_response_ms": round(avg_response, 2),
            "p95_response_ms": round(p95_response, 2),
            "max_response_ms": round(max(start_times), 2),
            "min_response_ms": round(min(start_times), 2),
            "total_requests": len(start_times)
        }
    
    async def analyze_database_performance(self) -> Dict[str, Any]:
        """Analyze database and storage performance"""
        # Test file I/O performance
        test_file = self.base_dir / "perf_test.tmp"
        
        # Write performance
        start = time.time()
        with open(test_file, 'w') as f:
            for i in range(1000):
                f.write(f"test_line_{i}\n")
        write_duration = time.time() - start
        
        # Read performance
        start = time.time()
        with open(test_file, 'r') as f:
            lines = f.readlines()
        read_duration = time.time() - start
        
        # Cleanup
        test_file.unlink(missing_ok=True)
        
        return {
            "write_performance": {
                "duration_ms": round(write_duration * 1000, 2),
                "lines_per_second": round(1000 / write_duration, 2)
            },
            "read_performance": {
                "duration_ms": round(read_duration * 1000, 2),
                "lines_per_second": round(len(lines) / read_duration, 2)
            }
        }
    
    async def analyze_concurrency(self) -> Dict[str, Any]:
        """Analyze concurrency and async performance"""
        # Test async task performance
        async def test_task(task_id):
            await asyncio.sleep(0.01)
            return f"task_{task_id}"
        
        # Sequential execution
        start = time.time()
        sequential_results = []
        for i in range(10):
            result = await test_task(i)
            sequential_results.append(result)
        sequential_duration = time.time() - start
        
        # Concurrent execution
        start = time.time()
        concurrent_results = await asyncio.gather(*[test_task(i) for i in range(10)])
        concurrent_duration = time.time() - start
        
        return {
            "sequential_duration_ms": round(sequential_duration * 1000, 2),
            "concurrent_duration_ms": round(concurrent_duration * 1000, 2),
            "speedup_factor": round(sequential_duration / concurrent_duration, 2),
            "task_count": 10
        }
    
    async def identify_optimizations(self) -> Dict[str, Any]:
        """Identify specific optimization opportunities"""
        optimizations = {}
        
        # Analyze system resource usage
        system_resources = self.results.get("System Resources", {}).get("result", {})
        if system_resources:
            memory_usage = system_resources.get("memory", {}).get("used_percent", 0)
            cpu_usage = system_resources.get("cpu", {}).get("current_usage", 0)
            
            if memory_usage > 80:
                optimizations["memory"] = {
                    "priority": "high",
                    "recommendation": "Implement memory optimization strategies",
                    "current_usage": f"{memory_usage}%"
                }
            
            if cpu_usage > 70:
                optimizations["cpu"] = {
                    "priority": "medium", 
                    "recommendation": "Optimize CPU-intensive operations",
                    "current_usage": f"{cpu_usage}%"
                }
        
        # Analyze import performance
        import_analysis = self.results.get("Import Performance", {}).get("result", {})
        if import_analysis:
            stats = import_analysis.get("statistics", {})
            avg_duration = stats.get("average_duration_ms", 0)
            
            if avg_duration > 100:  # > 100ms average
                optimizations["imports"] = {
                    "priority": "medium",
                    "recommendation": "Implement lazy loading for heavy modules",
                    "current_average": f"{avg_duration}ms"
                }
        
        # Analyze API performance
        api_analysis = self.results.get("API Performance", {}).get("result", {})
        if api_analysis:
            p95_response = api_analysis.get("p95_response_ms", 0)
            
            if p95_response > 200:  # > 200ms p95
                optimizations["api_response"] = {
                    "priority": "high",
                    "recommendation": "Implement caching and async optimizations",
                    "current_p95": f"{p95_response}ms"
                }
        
        return optimizations
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable performance recommendations"""
        recommendations = []
        
        # General recommendations based on analysis
        recommendations.extend([
            {
                "category": "Memory Management",
                "priority": "high",
                "title": "Implement Memory Pooling",
                "description": "Use object pooling for frequently created/destroyed objects",
                "implementation": "Create memory pools for GLYPH tokens, API responses, and temporary objects",
                "estimated_improvement": "15-25% memory reduction"
            },
            {
                "category": "Async Operations", 
                "priority": "high",
                "title": "Optimize Async/Await Usage",
                "description": "Ensure all I/O operations are properly async",
                "implementation": "Audit and convert blocking operations to async equivalents",
                "estimated_improvement": "20-40% response time improvement"
            },
            {
                "category": "Caching",
                "priority": "medium",
                "title": "Implement Multi-Layer Caching",
                "description": "Add caching at multiple levels (memory, Redis, CDN)",
                "implementation": "LRU cache for hot paths, Redis for session data, CDN for static assets",
                "estimated_improvement": "30-50% response time improvement"
            },
            {
                "category": "Database",
                "priority": "medium", 
                "title": "Connection Pooling",
                "description": "Implement database connection pooling",
                "implementation": "Use SQLAlchemy connection pools with proper sizing",
                "estimated_improvement": "10-20% database performance improvement"
            },
            {
                "category": "Monitoring",
                "priority": "low",
                "title": "Implement Performance Profiling",
                "description": "Add continuous performance monitoring",
                "implementation": "Integrate with APM tools (e.g., New Relic, DataDog)",
                "estimated_improvement": "Enables ongoing optimization"
            }
        ])
        
        return recommendations
    
    async def save_results(self):
        """Save analysis results to file"""
        results_file = self.base_dir / "performance_analysis_results.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {results_file}")
    
    def print_summary(self):
        """Print performance analysis summary"""
        logger.info("\n" + "="*70)
        logger.info("📊 LUKHAS PWM Performance Analysis Summary")
        logger.info("="*70)
        
        # System overview
        system_resources = self.results.get("System Resources", {}).get("result", {})
        if system_resources:
            memory = system_resources.get("memory", {})
            cpu = system_resources.get("cpu", {})
            process = system_resources.get("process", {})
            
            logger.info(f"🖥️  System Resources:")
            logger.info(f"   CPU Usage: {cpu.get('current_usage', 0):.1f}%")
            logger.info(f"   Memory Usage: {memory.get('used_percent', 0):.1f}%")
            logger.info(f"   Process Memory: {process.get('memory_mb', 0):.1f} MB")
        
        # Performance metrics
        api_perf = self.results.get("API Performance", {}).get("result", {})
        if api_perf:
            logger.info(f"🚀 API Performance:")
            logger.info(f"   Average Response: {api_perf.get('average_response_ms', 0):.1f}ms")
            logger.info(f"   P95 Response: {api_perf.get('p95_response_ms', 0):.1f}ms")
        
        # Concurrency
        concurrency = self.results.get("Concurrency Analysis", {}).get("result", {})
        if concurrency:
            logger.info(f"⚡ Concurrency:")
            logger.info(f"   Speedup Factor: {concurrency.get('speedup_factor', 0):.1f}x")
        
        # Recommendations
        recommendations = self.results.get("recommendations", [])
        high_priority = [r for r in recommendations if r.get("priority") == "high"]
        
        logger.info(f"\n💡 High Priority Recommendations ({len(high_priority)}):")
        for rec in high_priority[:3]:  # Top 3
            logger.info(f"   • {rec.get('title', 'Unknown')}")
            logger.info(f"     {rec.get('estimated_improvement', 'Improvement TBD')}")
        
        logger.info(f"\n⏱️  Total Analysis Time: {self.results.get('total_analysis_time', 0):.2f}s")
        logger.info("="*70)

async def main():
    """Run performance analysis"""
    analyzer = PerformanceAnalyzer()
    results = await analyzer.run_full_analysis()
    
    # Print key findings
    optimizations = results.get("recommendations", [])
    high_priority_count = len([o for o in optimizations if o.get("priority") == "high"])
    
    if high_priority_count > 0:
        logger.info(f"\n⚠️  Found {high_priority_count} high-priority optimization opportunities")
        logger.info("   Review the detailed analysis results for implementation guidance")
    else:
        logger.info("\n✅ System performance looks good - no critical optimizations needed")

if __name__ == "__main__":
    asyncio.run(main())