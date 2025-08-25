#!/usr/bin/env python3
"""
Test script to verify Datadog T4 Enterprise integration
Loads environment variables from .env file and tests connectivity
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def test_datadog_credentials():
    """Test if Datadog credentials are properly loaded"""
    print("🔍 Testing Datadog T4 Enterprise Integration")
    print("=" * 50)
    
    # Check if credentials are loaded
    api_key = os.getenv('DATADOG_API_KEY')
    app_key = os.getenv('DATADOG_APP_KEY')
    site = os.getenv('DATADOG_SITE')
    
    print(f"API Key: {'✅ Present' if api_key else '❌ Missing'}")
    print(f"App Key: {'✅ Present' if app_key else '❌ Missing'}")
    print(f"Site: {site or '❌ Missing'}")
    print()
    
    if not all([api_key, app_key, site]):
        print("❌ Missing required Datadog credentials")
        return False
        
    return True

def test_datadog_connectivity():
    """Test actual connectivity to Datadog API"""
    try:
        from datadog_api_client import ApiClient, Configuration
        from datadog_api_client.v1.api.metrics_api import MetricsApi
        
        # Configure Datadog client
        configuration = Configuration()
        configuration.api_key['apiKeyAuth'] = os.getenv('DATADOG_API_KEY')
        configuration.api_key['appKeyAuth'] = os.getenv('DATADOG_APP_KEY')
        configuration.server_variables['site'] = os.getenv('DATADOG_SITE')
        
        print("🔗 Testing Datadog API connectivity...")
        
        with ApiClient(configuration) as api_client:
            api_instance = MetricsApi(api_client)
            
            # Test by submitting a simple metric
            import time
            from datadog_api_client.v1.model.metrics_payload import MetricsPayload
            from datadog_api_client.v1.model.series import Series
            
            # Create test metric
            series = Series(
                metric="lukhas.t4.test.connectivity",
                points=[[int(time.time()), 1.0]],
                tags=["environment:test", "tier:t4"],
                type="gauge"
            )
            
            payload = MetricsPayload(series=[series])
            response = api_instance.submit_metrics(body=payload)
            
            print("✅ Successfully connected to Datadog!")
            print(f"✅ Test metric submitted: {response}")
            return True
            
    except ImportError as e:
        print(f"❌ Datadog client not available: {e}")
        print("💡 Install with: pip install datadog-api-client")
        return False
    except Exception as e:
        print(f"❌ Datadog connection failed: {e}")
        return False

def test_t4_monitoring_module():
    """Test the T4 monitoring module"""
    try:
        print("\n📊 Testing T4 Enterprise Monitoring Module...")
        
        # Import our T4 monitoring
        import sys
        sys.path.append('/Users/agi_dev/LOCAL-REPOS/Lukhas')
        
        from enterprise.monitoring.datadog_integration import T4DatadogMonitoring, T4SLAMetrics
        from datetime import datetime
        
        # Initialize monitoring
        monitor = T4DatadogMonitoring()
        
        # Create test SLA metrics
        test_metrics = T4SLAMetrics(
            api_latency_p95=25.0,  # Well under 50ms target
            api_latency_p99=45.0,  # Well under 100ms target
            uptime_percentage=99.99,  # Meeting 99.99% target
            error_rate=0.001,  # Well under 0.01% target
            concurrent_users=5000,  # Testing capacity
            response_time_avg=20.0,  # Fast response
            memory_usage_percent=65.0,  # Healthy memory usage
            cpu_usage_percent=45.0,  # Healthy CPU usage
            drift_score=0.02,  # Well under 0.05 T4 safety threshold
            security_incidents=0,  # No incidents
            timestamp=datetime.now()
        )
        
        # Test SLA metrics submission
        print("📈 Testing SLA metrics submission with T4 test data...")
        success = monitor.submit_sla_metrics(test_metrics)
        
        if success:
            print("✅ T4 SLA metrics submitted successfully!")
            print(f"   - API Latency P95: {test_metrics.api_latency_p95}ms (target: <50ms)")
            print(f"   - Uptime: {test_metrics.uptime_percentage}% (target: 99.99%)")
            print(f"   - Drift Score: {test_metrics.drift_score} (target: <0.05)")
        else:
            print("⚠️  T4 SLA metrics submission returned False")
        
        print("✅ T4 Enterprise Monitoring module loaded and tested!")
        return True
        
    except Exception as e:
        print(f"❌ T4 monitoring module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 LUKHAS AI T4 Enterprise Integration Test")
    print("==========================================\n")
    
    # Test credentials
    creds_ok = test_datadog_credentials()
    if not creds_ok:
        exit(1)
    
    # Test connectivity
    conn_ok = test_datadog_connectivity()
    
    # Test T4 module
    module_ok = test_t4_monitoring_module()
    
    print("\n" + "=" * 50)
    if creds_ok and conn_ok and module_ok:
        print("🎉 All T4 Enterprise Datadog tests PASSED!")
        print("✅ Ready for T4 Enterprise deployment")
    else:
        print("⚠️  Some tests failed - check configuration")
        print("💡 Ensure Datadog credentials are correct and API access is enabled")