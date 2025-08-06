"""
Simple test for PWM Intelligence Integration
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from pwm_intelligence_adapter import PWMIntelligenceManager

async def test_basic_intelligence():
    """Test basic intelligence functionality"""
    
    print("🧪 Testing PWM Intelligence Integration...")
    
    try:
        # Initialize intelligence manager
        intelligence = PWMIntelligenceManager()
        await intelligence.initialize()
        print("✅ Intelligence manager initialized successfully")
        
        # Test parameter optimization
        current_params = {'frequency': 1000, 'duty_cycle': 0.5}
        target_performance = {'efficiency': 0.95}
        
        result = await intelligence.optimize_pwm_parameters(current_params, target_performance)
        print("✅ Parameter optimization completed")
        print(f"   Optimized frequency: {result['optimized_parameters'].get('frequency', 'unchanged')}")
        print(f"   Confidence: {result['optimization_confidence']:.2f}")
        
        # Test anomaly detection
        test_telemetry = {
            'frequency': 950,  # Slightly off from target
            'duty_cycle': 0.55,
            'efficiency': 0.82,  # Lower than expected
            'temperature': 45
        }
        
        anomaly_result = await intelligence.analyze_pwm_anomaly(test_telemetry)
        print("✅ Anomaly analysis completed")
        print(f"   Anomaly detected: {anomaly_result['anomaly_detected']}")
        
        if anomaly_result['anomaly_detected']:
            print(f"   Surprise level: {anomaly_result['surprise_level']:.2f}")
            print(f"   Questions to investigate: {len(anomaly_result['investigation_questions'])}")
        
        print("\n🎉 All tests passed! PWM Intelligence is ready for integration.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_intelligence())
    exit(0 if success else 1)
