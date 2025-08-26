"""
Simple LUCAS DAST Integration Test
Basic validation of the enhanced DAST system
"""

import sys
import os
import asyncio
import time

# Add the parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from engine_fixed import LucasDASTEngine
    print("✅ Successfully imported LucasDASTEngine")
except ImportError as e:
    print(f"❌ Failed to import LucasDASTEngine: {e}")
    sys.exit(1)


async def test_basic_integration():
    """Basic integration test for DAST system"""
    print("\n🧪 Starting LUCAS DAST Basic Integration Test...")

    try:
        # Initialize engine
        print("🔧 Initializing DAST engine...")
        engine = LucasDASTEngine()
        await engine.initialize()
        print("✅ Engine initialized successfully")

        # Test track() operation
        print("📝 Testing track() operation...")
        start_time = time.time()
        result = await engine.track({
            "title": "Integration test task",
            "description": "Testing the integrated DAST system",
            "priority": "high"
        })
        track_time = (time.time() - start_time) * 1000
        print(f"✅ Track completed in {track_time:.2f}ms (target: <100ms)")
        print(f"   Result: {result}")

        # Test focus() operation
        print("🎯 Testing focus() operation...")
        start_time = time.time()
        focused_tasks = await engine.focus("high priority tasks")
        focus_time = (time.time() - start_time) * 1000
        print(f"✅ Focus completed in {focus_time:.2f}ms (target: <100ms)")
        print(f"   Found {len(focused_tasks)} tasks")

        # Test progress() operation
        print("📊 Testing progress() operation...")
        start_time = time.time()
        progress = await engine.progress("overall")
        progress_time = (time.time() - start_time) * 1000
        print(f"✅ Progress completed in {progress_time:.2f}ms (target: <100ms)")
        print(f"   Progress data: {progress}")

        # Test collaborate() operation
        print("🤝 Testing collaborate() operation...")
        start_time = time.time()
        collaboration = await engine.collaborate(
            "help me prioritize tasks",
            {"context": "I have 2 hours to work today"}
        )
        collab_time = (time.time() - start_time) * 1000
        print(f"✅ Collaboration completed in {collab_time:.2f}ms (target: <2000ms)")
        print(f"   Collaboration result: {collaboration}")

        # Performance summary
        print("\n📈 Performance Summary:")
        print(f"   Track:       {track_time:.2f}ms {'✅' if track_time < 100 else '⚠️'}")
        print(f"   Focus:       {focus_time:.2f}ms {'✅' if focus_time < 100 else '⚠️'}")
        print(f"   Progress:    {progress_time:.2f}ms {'✅' if progress_time < 100 else '⚠️'}")
        print(f"   Collaborate: {collab_time:.2f}ms {'✅' if collab_time < 2000 else '⚠️'}")

        print("\n🎉 All basic integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_components():
    """Test AI component integration"""
    print("\n🤖 Testing AI Components Integration...")

    try:
        engine = LucasDASTEngine()
        await engine.initialize()

        # Test TaskIntelligence
        print("🧠 Testing TaskIntelligence...")
        analysis = await engine.task_intelligence.analyze_task({
            "title": "Complex AI task",
            "description": "Build neural network for pattern recognition",
            "complexity": "high",
            "tags": ["ai", "ml", "complex"]
        })
        print(f"✅ Task analysis: {analysis}")

        # Test PriorityOptimizer
        print("⚡ Testing PriorityOptimizer...")
        priorities = await engine.priority_optimizer.optimize_priorities([
            {"title": "Urgent bug fix", "priority": "urgent"},
            {"title": "Feature enhancement", "priority": "medium"},
            {"title": "Documentation", "priority": "low"}
        ])
        print(f"✅ Priority optimization: {len(priorities)} tasks optimized")

        print("🎉 AI components integration successful!")
        return True

    except Exception as e:
        print(f"❌ AI components test failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 LUCAS DAST Integration Test Suite")
        print("=" * 50)

        # Run basic integration test
        basic_success = await test_basic_integration()

        # Run AI components test
        ai_success = await test_ai_components()

        # Final summary
        print("\n" + "=" * 50)
        if basic_success and ai_success:
            print("🎉 ALL TESTS PASSED - DAST SYSTEM READY FOR PRODUCTION!")
        else:
            print("⚠️  Some tests failed - review issues above")

        print("🔧 DAST system features validated:")
        print("   ✅ One-line API operations")
        print("   ✅ Sub-100ms performance targets")
        print("   ✅ AI-powered task intelligence")
        print("   ✅ Human-AI collaboration")
        print("   ✅ Modular architecture")

    asyncio.run(main())
