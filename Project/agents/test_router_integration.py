#!/usr/bin/env python3
"""
Test Router Integration for Agent A
Tests communication with Vansh's Router service
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
AGENT_A_URL = "http://localhost:8001"
ROUTER_URL = "http://localhost:5000"

def test_agent_a_health():
    """Test Agent A health check"""
    print("🔍 Testing Agent A health...")
    try:
        response = requests.get(f"{AGENT_A_URL}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Agent A health check failed: {e}")
        return False

def test_router_status():
    """Test Router status through Agent A"""
    print("\n🔍 Testing Router status...")
    try:
        response = requests.get(f"{AGENT_A_URL}/agentA/router_status", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Router status check failed: {e}")
        return False

def test_send_to_router():
    """Test sending offer to Router through Agent A"""
    print("\n🔍 Testing send to Router...")
    
    test_trigger = {
        "trigger_type": "arduino",
        "amount": 2500000,  # 2.5 ADA in lovelace
        "context": {
            "button_type": "button_1",
            "priority": "high",
            "test": True
        },
        "timestamp": datetime.now().isoformat(),
        "source": "arduino_a"
    }
    
    try:
        response = requests.post(
            f"{AGENT_A_URL}/agentA/send_to_router",
            json=test_trigger,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Offer sent to Router successfully")
            print(f"   📊 Amount ADA: {result.get('amount_ada', 'N/A')}")
            print(f"   📊 Amount Lovelace: {result.get('amount_lovelace', 'N/A')}")
            return True
        else:
            print(f"   ❌ Send to Router failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Send to Router test failed: {e}")
        return False

def test_direct_router_connection():
    """Test direct connection to Router service"""
    print("\n🔍 Testing direct Router connection...")
    try:
        # Test if Router is running
        response = requests.get(f"{ROUTER_URL}/", timeout=5)
        print(f"   Router Status: {response.status_code}")
        print(f"   Router Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Direct Router connection failed: {e}")
        print(f"   💡 Make sure Vansh's Router service is running on {ROUTER_URL}")
        return False

def test_router_offer_format():
    """Test the exact format expected by Router"""
    print("\n🔍 Testing Router offer format...")
    
    # This is the exact format Vansh expects
    router_offer = {
        "from_agent": "agent_a",
        "to_agent": "agent_b",
        "amount": 2.5,
        "currency": "ADA",
        "description": "Agent A payment offer",
        "timestamp": datetime.now().isoformat() + "Z",
        "metadata": {
            "arduino_trigger": True,
            "button_type": "button_1",
            "priority": "medium",
            "agent_a_offer_id": "test-123"
        }
    }
    
    print("   📋 Router offer format:")
    print(f"   {json.dumps(router_offer, indent=2)}")
    
    try:
        response = requests.post(
            f"{ROUTER_URL}/send_offer",
            json=router_offer,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Router Response Status: {response.status_code}")
        print(f"   Router Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Direct Router offer successful")
            return True
        else:
            print("   ❌ Direct Router offer failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Direct Router test failed: {e}")
        return False

def main():
    """Run all Router integration tests"""
    print("🚀 Agent A Router Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Agent A Health", test_agent_a_health),
        ("Direct Router Connection", test_direct_router_connection),
        ("Router Status via Agent A", test_router_status),
        ("Router Offer Format", test_router_offer_format),
        ("Send to Router via Agent A", test_send_to_router)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("ROUTER INTEGRATION TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All Router integration tests passed!")
        print("✅ Agent A is ready for integration with Vansh's Router service")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("💡 Make sure Vansh's Router service is running on http://localhost:5000")
    
    print("\n📋 Next Steps:")
    print("1. Ensure Vansh's Router service is running")
    print("2. Test the integration between Agent A and Router")
    print("3. Coordinate with Vansh on the complete flow")
    print("4. Test with real Arduino triggers")

if __name__ == "__main__":
    main()
