#!/usr/bin/env python3
"""
LUKHAS AI Live Social Media API Integration Test
Comprehensive testing of live platform posting capabilities
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add branding directory to path
sys.path.append(str(Path(__file__).parent / "branding"))

# Import LUKHAS components
from automation.social_media_orchestrator import SocialMediaOrchestrator
from apis.platform_integrations import get_api_manager

async def test_api_integration():
    """Test the complete live API integration system"""
    
    print("🚀 LUKHAS AI Live Social Media API Integration Test")
    print("=" * 70)
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize orchestrator
    print("📱 Initializing Social Media Orchestrator...")
    orchestrator = SocialMediaOrchestrator()
    
    # Check API manager status
    print("\n🔌 API Manager Status:")
    api_manager = get_api_manager()
    api_status = api_manager.get_platform_status()
    
    configured_platforms = []
    for platform, status in api_status.items():
        credentials = "✅" if status["credentials_configured"] else "❌"
        client = "✅" if status["client_initialized"] else "❌"
        library = "✅" if status["library_available"] else "❌"
        
        print(f"   {platform.title()}: Credentials {credentials} | Client {client} | Library {library}")
        
        if status["credentials_configured"] and status["client_initialized"] and status["library_available"]:
            configured_platforms.append(platform)
    
    print(f"\n✅ Platforms ready for live posting: {len(configured_platforms)}")
    if configured_platforms:
        print(f"   Ready: {', '.join(configured_platforms)}")
    else:
        print("   ⚠️ No platforms configured - will run in simulation mode")
    
    # Test orchestrator API status
    print("\n📊 Orchestrator API Status:")
    orchestrator_status = orchestrator.get_api_status()
    print(f"   API Manager Available: {'✅' if orchestrator_status['api_manager_available'] else '❌'}")
    print(f"   Live Posting Enabled: {'✅' if orchestrator_status['live_posting_enabled'] else '❌'}")
    print(f"   Platforms Ready: {orchestrator_status['platforms_ready_for_live']}/{orchestrator_status['total_platforms']}")
    
    # Generate test content
    print("\n🎨 Generating Test Content...")
    test_posts = await orchestrator.generate_daily_content_batch()
    
    print(f"\n📝 Generated {len(test_posts)} posts:")
    for i, post in enumerate(test_posts, 1):
        print(f"   {i}. {post.platform}: {post.title}")
        print(f"      Content: {post.content[:80]}{'...' if len(post.content) > 80 else ''}")
        print(f"      Type: {post.content_type} | Media: {'Yes' if post.media_path else 'No'}")
        print()
    
    # Auto-approve all posts for testing
    print("🔐 Auto-approving all posts for testing...")
    for post in test_posts:
        orchestrator.approve_post(post.post_id)
    
    approved_posts = orchestrator.get_pending_approval_posts()
    print(f"✅ Posts approved: {len(test_posts) - len(approved_posts)}")
    
    # Test publishing in simulation mode first
    print("\n🎭 Testing Simulation Mode Publishing...")
    sim_results = await orchestrator.publish_approved_posts(live_mode=False)
    
    print(f"📊 Simulation Results:")
    print(f"   Published: {sim_results['published']}")
    print(f"   Failed: {sim_results['failed']}")
    print(f"   Mode: {'🚀 LIVE' if sim_results['live_posting_used'] else '🎭 SIMULATION'}")
    
    # Show detailed results
    for post_id, result in sim_results["posting_results"].items():
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['platform']}: {result.get('reason', result.get('error', 'Success'))}")
    
    # Test live posting if platforms are configured
    if configured_platforms and input("\n❓ Test live posting? (y/N): ").lower().startswith('y'):
        print("\n🚀 Testing Live API Publishing...")
        print("⚠️ WARNING: This will post to live social media platforms!")
        
        if input("❓ Are you sure? Type 'YES' to continue: ") == "YES":
            # Reset published status for live test
            for post in orchestrator.content_queue:
                if post.approved:
                    post.published = False
            
            live_results = await orchestrator.publish_approved_posts(live_mode=True)
            
            print(f"\n📊 Live Posting Results:")
            print(f"   Published: {live_results['published']}")
            print(f"   Failed: {live_results['failed']}")
            print(f"   Platforms Configured: {live_results['platforms_configured']}")
            
            # Show detailed live results
            for post_id, result in live_results["posting_results"].items():
                status = "✅" if result["success"] else "❌"
                if result["success"] and result.get("live_posting"):
                    print(f"   {status} {result['platform']}: {result.get('url', result.get('post_id', 'Posted'))}")
                else:
                    print(f"   {status} {result['platform']}: {result.get('error', 'Failed')}")
        else:
            print("   Skipped live posting test")
    else:
        print("\n⚠️ Live posting test skipped (no configured platforms or user declined)")
    
    # Show final analytics
    print("\n📈 Final Content Analytics:")
    analytics = orchestrator.get_content_analytics()
    print(f"   Total Generated: {analytics['total_content_generated']}")
    print(f"   Approved: {analytics['approved_content']}")
    print(f"   Published: {analytics['published_content']}")
    print(f"   Approval Rate: {analytics['approval_rate']:.1f}%")
    print(f"   Publish Rate: {analytics['publish_rate']:.1f}%")
    print(f"   Integration Status: {analytics['api_integration_status']}")
    
    print(f"\n📊 Platform Distribution:")
    for platform, count in analytics['platform_distribution'].items():
        print(f"   {platform}: {count} posts")
    
    print(f"\n📊 Content Type Distribution:")
    for content_type, count in analytics['content_type_distribution'].items():
        print(f"   {content_type}: {count} posts")
    
    print("\n" + "=" * 70)
    print(f"🎉 Integration Test Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚛️🧠🛡️ LUKHAS AI Social Media Platform Integration")

async def test_individual_platform_apis():
    """Test individual platform APIs directly"""
    
    print("\n🧪 Individual Platform API Tests")
    print("=" * 50)
    
    api_manager = get_api_manager()
    test_content = "🧠 Testing LUKHAS AI consciousness technology platform integration! The Trinity Framework (⚛️🧠🛡️) ensures our AI systems maintain authentic, aware, and ethical operation. #ConsciousnessTechnology #LUKHASIA #Test"
    
    platforms_to_test = ["twitter", "linkedin", "reddit"]
    
    for platform in platforms_to_test:
        print(f"\n🔌 Testing {platform.title()} API...")
        
        try:
            result = await api_manager.post_content(
                platform=platform,
                content=test_content,
                title="LUKHAS AI Platform Integration Test",
                subreddit="test" if platform == "reddit" else None
            )
            
            if result.success:
                print(f"✅ {platform} posting successful!")
                if result.url:
                    print(f"   URL: {result.url}")
                if result.post_id:
                    print(f"   Post ID: {result.post_id}")
            else:
                print(f"❌ {platform} posting failed: {result.error}")
                
        except Exception as e:
            print(f"❌ {platform} test error: {e}")
    
    print("\n🎯 Individual API tests complete")

def check_environment_setup():
    """Check if environment is properly set up for live posting"""
    
    print("🔍 Environment Setup Check")
    print("=" * 40)
    
    # Check for environment variables
    required_env_vars = {
        "Twitter": ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"],
        "LinkedIn": ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_ACCESS_TOKEN"],
        "Reddit": ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"],
        "Instagram": ["INSTAGRAM_ACCESS_TOKEN"]
    }
    
    configured_platforms = []
    
    for platform, vars_needed in required_env_vars.items():
        vars_present = [var for var in vars_needed if os.getenv(var)]
        vars_missing = [var for var in vars_needed if not os.getenv(var)]
        
        if len(vars_present) == len(vars_needed):
            print(f"✅ {platform}: All credentials configured")
            configured_platforms.append(platform)
        elif vars_present:
            print(f"⚠️ {platform}: Partial configuration ({len(vars_present)}/{len(vars_needed)})")
            print(f"   Missing: {', '.join(vars_missing)}")
        else:
            print(f"❌ {platform}: No credentials configured")
    
    print(f"\n📊 Summary:")
    print(f"   Platforms ready: {len(configured_platforms)}")
    print(f"   Platforms configured: {', '.join(configured_platforms) if configured_platforms else 'None'}")
    
    if not configured_platforms:
        print("\n💡 To enable live posting:")
        print("   1. Create a .env file in the project root")
        print("   2. Add your API credentials (see branding/config/api_setup_guide.md)")
        print("   3. Install dependencies: pip install -r branding/requirements-apis.txt")
    
    return configured_platforms

async def main():
    """Run the complete live API integration test suite"""
    
    print("🎯 LUKHAS AI Live Social Media API Test Suite")
    print("=" * 60)
    print("This test validates live platform integrations with enhanced branding quality.")
    print()
    
    # Check environment setup
    configured_platforms = check_environment_setup()
    
    print("\n" + "="*60)
    
    # Run main integration test
    await test_api_integration()
    
    # Run individual API tests if user wants
    if configured_platforms and input("\n❓ Run individual platform API tests? (y/N): ").lower().startswith('y'):
        await test_individual_platform_apis()
    
    print("\n🎉 All tests complete!")
    print("📚 See branding/config/api_setup_guide.md for setup instructions")
    print("📊 Check branding/logs/ for detailed logs")

if __name__ == "__main__":
    asyncio.run(main())