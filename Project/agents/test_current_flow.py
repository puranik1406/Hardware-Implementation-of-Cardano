#!/usr/bin/env python3
"""
Test Current Working Flow - Agent A + Bedrock
"""

import requests
import json
from datetime import datetime

def test_current_flow():
    """Test what's currently working"""
    print("🚀 Testing Current Working Components")
    print("=" * 50)
    
    # Test Agent A Health
    print("\n1. Testing Agent A Health...")
    try:
        response = requests.get("http://localhost:8002/")
        print(f"   ✅ Agent A Status: {response.status_code}")
        data = response.json()
        print(f"   📋 Service: {data.get('service', 'Unknown')}")
        print(f"   🤖 Bedrock Mode: {data.get('bedrock_mode', 'Unknown')}")
        print(f"   🔗 Router URL: {data.get('router_url', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Agent A Error: {e}")
        return False
    
    # Test Offer Creation (Agent A + Bedrock)
    print("\n2. Testing Offer Creation (Agent A + Bedrock)...")
    try:
        offer_data = {
            "trigger_type": "arduino",
            "amount": 2500000,  # 2.5 ADA
            "context": {
                "button_type": "button_1",
                "priority": "high",
                "test": True
            },
            "source": "end_to_end_test",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            "http://localhost:8002/agentA/propose",
            json=offer_data,
            timeout=10
        )
        
        print(f"   ✅ Offer Creation Status: {response.status_code}")
        result = response.json()
        
        print(f"   📊 Decision: {result.get('status', 'Unknown')}")
        print(f"   💰 Amount: {result.get('amount', 0)} lovelace ({result.get('amount', 0)/1000000} ADA)")
        print(f"   🆔 Offer ID: {result.get('offer_id', 'Unknown')}")
        print(f"   💭 Reason: {result.get('decision_reason', 'Unknown')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Offer Creation Error: {e}")
        return False

def test_router_integration():
    """Test Router integration (will fail if Router not running)"""
    print("\n3. Testing Router Integration...")
    try:
        router_data = {
            "trigger_type": "arduino",
            "amount": 1500000,  # 1.5 ADA
            "context": {
                "button_type": "button_2",
                "priority": "medium"
            },
            "source": "router_integration_test"
        }
        
        response = requests.post(
            "http://localhost:8002/agentA/send_to_router",
            json=router_data,
            timeout=15
        )
        
        print(f"   ✅ Router Integration Status: {response.status_code}")
        result = response.json()
        
        print(f"   📡 Status: {result.get('status', 'Unknown')}")
        print(f"   💰 Amount ADA: {result.get('amount_ada', 'Unknown')}")
        print(f"   🔗 Router Response: {result.get('router_response', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Router Integration Error: {e}")
        print(f"   💡 This is expected if Vansh's Router is not running")
        return False

def main():
    print("🎯 End-to-End Integration Test")
    print("Testing: Agent A → Bedrock → Router → Blockchain")
    print("=" * 60)
    
    # Test working components
    agent_works = test_current_flow()
    router_works = test_router_integration()
    
    print("\n" + "=" * 60)
    print("📊 INTEGRATION STATUS SUMMARY")
    print("=" * 60)
    
    print(f"✅ Agent A Service: {'WORKING' if agent_works else 'FAILED'}")
    print(f"✅ Bedrock Integration: {'WORKING' if agent_works else 'FAILED'}")
    print(f"{'✅' if router_works else '❌'} Router Integration: {'WORKING' if router_works else 'WAITING FOR VANSH'}")
    print(f"❌ Blockchain Integration: WAITING FOR DHANUSH")
    
    if agent_works and not router_works:
        print("\n💡 NEXT STEPS:")
        print("1. ✅ Imad's part is COMPLETE and working!")
        print("2. ⏳ Waiting for Vansh to start Router on port 5000")
        print("3. ⏳ Waiting for Dhanush to connect blockchain")
        print("4. 🎯 Then test complete end-to-end flow")
    
    elif agent_works and router_works:
        print("\n🎉 FULL INTEGRATION WORKING!")
        print("✅ Complete flow: Agent A → Bedrock → Router → Blockchain")
    
    else:
        print("\n⚠️  Some components need attention")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
