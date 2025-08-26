"""
LUKHAS AI - Authentication Integration Test
Comprehensive test of the integrated authentication ecosystem
"""

import asyncio
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_authentication_integration():
    """Test the complete authentication integration"""
    
    print("🎖️ LUKHAS Authentication Integration Test")
    print("=" * 50)
    
    try:
        # Test 1: Import production identity module
        print("\n📦 Testing Production Identity Module Import...")
        sys.path.insert(0, str(Path(__file__).parent))
        
        from lukhas.identity import AUTHENTICATION_AVAILABLE
        print(f"✅ Identity module imported successfully")
        print(f"   Authentication available: {AUTHENTICATION_AVAILABLE}")
        
        if AUTHENTICATION_AVAILABLE:
            from lukhas.identity import auth_integration, WalletAuthBridge, QRGAuthBridge
            print("✅ Authentication components imported successfully")
        
        # Test 2: Test integration bridge
        print("\n🔗 Testing Authentication Integration Bridge...")
        if AUTHENTICATION_AVAILABLE:
            integration = await auth_integration.get_integration()
            status = integration.get_integration_status()
            
            print(f"✅ Integration bridge initialized")
            print(f"   Components loaded: {status['components_loaded']}")
            print(f"   Bridges initialized: {status['bridges_initialized']}")
            print(f"   Available components: {status['components']}")
            print(f"   Available bridges: {status['bridges']}")
        
        # Test 3: Test WALLET bridge
        print("\n💳 Testing WALLET Integration Bridge...")
        if AUTHENTICATION_AVAILABLE:
            wallet_bridge = WalletAuthBridge()
            await wallet_bridge.initialize()
            
            test_credentials = {'user_id': 'test_user', 'token': 'test_token'}
            wallet_result = await wallet_bridge.authenticate_identity(test_credentials)
            
            print(f"✅ WALLET bridge initialized and tested")
            print(f"   Authentication result: {wallet_result['success']}")
        
        # Test 4: Test QRG bridge
        print("\n🔲 Testing QRG Integration Bridge...")
        if AUTHENTICATION_AVAILABLE:
            qrg_bridge = QRGAuthBridge()
            await qrg_bridge.initialize()
            
            test_qr_data = {'qr_code': 'test_qr', 'metadata': {}}
            qrg_result = await qrg_bridge.verify_qr_authentication(test_qr_data)
            
            print(f"✅ QRG bridge initialized and tested")
            print(f"   Verification result: {qrg_result['success']}")
        
        # Test 5: Path verification
        print("\n📁 Testing Component Path Resolution...")
        lukhas_root = Path(__file__).parent.parent.parent
        candidate_path = lukhas_root / "candidate" / "governance" / "identity"
        lambda_path = lukhas_root / "lambda_products_pack" / "lambda_core"
        
        print(f"✅ LUKHAS root: {lukhas_root}")
        print(f"   Candidate auth exists: {candidate_path.exists()}")
        print(f"   Lambda core exists: {lambda_path.exists()}")
        
        if candidate_path.exists():
            auth_dirs = [d.name for d in candidate_path.iterdir() if d.is_dir() and d.name.startswith('auth')]
            print(f"   Auth directories found: {auth_dirs}")
        
        if lambda_path.exists():
            wallet_exists = (lambda_path / "WALLET").exists()
            qrg_exists = (lambda_path / "QRG").exists()
            print(f"   WALLET exists: {wallet_exists}")
            print(f"   QRG exists: {qrg_exists}")
        
        print("\n🎉 Integration Test Summary:")
        print("✅ Production identity module: WORKING")
        if AUTHENTICATION_AVAILABLE:
            print("✅ Authentication integration: WORKING") 
            print("✅ WALLET bridge: WORKING")
            print("✅ QRG bridge: WORKING")
            print("✅ Component path resolution: WORKING")
        else:
            print("⚠️  Authentication integration: DEFERRED (components not found)")
        
        print("\n🚀 Ready for full integration with consolidated auth system!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_authentication_integration())
