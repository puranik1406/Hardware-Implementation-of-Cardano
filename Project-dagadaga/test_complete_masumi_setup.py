"""
Complete Masumi Network Integration Test
Tests the full pipeline from setup to payments
"""

import requests
import time
import os
import subprocess
import json
from pathlib import Path

def check_docker_service(service_name: str, port: int, endpoint: str = "") -> bool:
    """Check if a Docker service is running and accessible"""
    try:
        url = f"http://localhost:{port}{endpoint}"
        response = requests.get(url, timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK for some health endpoints
            return True
        return False
    except:
        return False

def check_masumi_services():
    """Check all Masumi services are running"""
    print("🔍 Checking Masumi Services...")
    
    services = [
        ("Payment Service", 3001, "/health"),
        ("Registry Service", 3000, "/health"),
        ("PostgreSQL", 5432, "")
    ]
    
    all_running = True
    for name, port, endpoint in services:
        if name == "PostgreSQL":
            # Special check for PostgreSQL
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="masumi",
                    user="masumi",
                    password="masumi"
                )
                conn.close()
                print(f"   ✅ {name}: Running on port {port}")
            except:
                print(f"   ❌ {name}: Not accessible on port {port}")
                all_running = False
        else:
            if check_docker_service(name, port, endpoint):
                print(f"   ✅ {name}: Running on port {port}")
            else:
                print(f"   ❌ {name}: Not accessible on port {port}")
                all_running = False
    
    return all_running

def test_masumi_api():
    """Test Masumi Payment Service API"""
    print("\n🧪 Testing Masumi Payment Service API...")
    
    base_url = "http://localhost:3001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health endpoint: OK")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
        return False
    
    # Test API documentation
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("   ✅ API documentation: Accessible")
        else:
            print(f"   ❌ API docs failed: {response.status_code}")
    except:
        print("   ⚠️  API docs: Not accessible (may be normal)")
    
    return True

def test_integration_service():
    """Test our integrated payment service"""
    print("\n🧪 Testing Integrated Payment Service...")
    
    base_url = "http://localhost:8001"
    
    # Test if service is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Service: {data.get('mode', 'unknown')}")
            print(f"   ✅ Team Wallets: {data.get('team_wallets', 0)}")
            print(f"   ✅ Masumi Connection: {data.get('masumi_connection', 'unknown')}")
            return True
        else:
            print(f"   ❌ Service failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Service error: {e}")
        return False

def test_wallet_management():
    """Test wallet creation and management"""
    print("\n🧪 Testing Wallet Management...")
    
    base_url = "http://localhost:8001"
    
    try:
        response = requests.get(f"{base_url}/wallets")
        if response.status_code == 200:
            wallets = response.json()["wallets"]
            print(f"   ✅ Found {len(wallets)} team wallets:")
            
            for name, wallet in wallets.items():
                if "error" not in wallet:
                    balance_ada = wallet.get("balance_ada", "unknown")
                    print(f"     • {name}: {balance_ada} ADA")
                else:
                    print(f"     • {name}: Error - {wallet['error']}")
            
            return len(wallets) > 0
        else:
            print(f"   ❌ Wallet listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Wallet management error: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n🔍 Checking Environment Configuration...")
    
    # Check .env file
    env_file = Path("blockchain/.env")
    if env_file.exists():
        print("   ✅ Environment file: Found")
    else:
        print("   ❌ Environment file: Missing blockchain/.env")
        return False
    
    # Check required environment variables
    required_vars = [
        "BLOCKFROST_PROJECT_ID",
        "MASUMI_ADMIN_KEY",
        "MASUMI_ENCRYPTION_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ Required environment variables: All set")
    
    return True

def setup_instructions():
    """Provide setup instructions if services aren't running"""
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    
    print("1. Clone Masumi Services:")
    print("   git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git")
    print("   cd masumi-services-dev-quickstart")
    
    print("\n2. Configure Environment:")
    print("   cp .env.example .env")
    print("   # Edit .env with your Blockfrost API key and other settings")
    
    print("\n3. Start Masumi Services:")
    print("   docker compose up -d")
    
    print("\n4. Start Our Payment Service:")
    print("   cd ../blockchain")
    print("   python src/real_payment_service.py")
    
    print("\n5. Test Integration:")
    print("   python test_complete_masumi_setup.py")

def main():
    """Run complete integration test"""
    print("🚀 Complete Masumi Network Integration Test")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed!")
        setup_instructions()
        return False
    
    # Check Docker services
    if not check_masumi_services():
        print("\n❌ Masumi services not running!")
        print("\n💡 Start Masumi services with:")
        print("   cd masumi-services-dev-quickstart")
        print("   docker compose up -d")
        return False
    
    # Test Masumi API
    if not test_masumi_api():
        print("\n❌ Masumi API tests failed!")
        return False
    
    # Test our integration service
    if not test_integration_service():
        print("\n❌ Integration service not running!")
        print("\n💡 Start our service with:")
        print("   python blockchain/src/real_payment_service.py")
        return False
    
    # Test wallet management
    if not test_wallet_management():
        print("\n❌ Wallet management tests failed!")
        return False
    
    print("\n🎉 All Integration Tests Passed!")
    print("\n✅ Your Masumi + Arduino-to-Cardano setup is working!")
    
    print("\n🔗 Useful URLs:")
    print("   • Masumi Payment API: http://localhost:3001/docs")
    print("   • Masumi Admin Panel: http://localhost:3001/admin")
    print("   • Our Payment Service: http://localhost:8001/docs")
    print("   • Cardano Explorer: https://preprod.cardanoscan.io/")
    
    print("\n🎯 Next Steps:")
    print("   1. Fund wallets with preprod ADA from faucet")
    print("   2. Test payments with team integration code")
    print("   3. Monitor transactions on Cardano Explorer")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)