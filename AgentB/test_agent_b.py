#!/usr/bin/env python3
"""
Test script for Agent B - Seller Logic
Tests the complete workflow with mock data
"""

import requests
import json
import time
import threading
from datetime import datetime

# Configuration
AGENT_B_URL = "http://localhost:5001"
TEST_OFFERS = [
    {
        "amount": 150.0,
        "product": "Premium Widget",
        "buyer_address": "addr1q9test...",
        "buyer_id": "buyer_001"
    },
    {
        "amount": 75.0,
        "product": "Basic Widget", 
        "buyer_address": "addr1q9test...",
        "buyer_id": "buyer_002"
    },
    {
        "amount": 200.0,
        "product": "Deluxe Widget",
        "buyer_address": "addr1q9test...",
        "buyer_id": "buyer_003"
    }
]

def test_health_check():
    """Test Agent B health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{AGENT_B_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_offer_response(offer_data):
    """Test offer response endpoint"""
    print(f"\n📝 Testing offer response for {offer_data['product']} (${offer_data['amount']})...")
    try:
        response = requests.post(
            f"{AGENT_B_URL}/respond",
            json=offer_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Offer response successful")
            print(f"   Status: {result.get('status')}")
            print(f"   Decision: {result.get('decision', {}).get('decision')}")
            if 'tx_hash' in result:
                print(f"   Transaction Hash: {result['tx_hash']}")
            return result
        else:
            print(f"❌ Offer response failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Offer response error: {e}")
        return None

def test_transaction_confirmation(tx_hash):
    """Test transaction confirmation endpoint"""
    print(f"\n🔔 Testing transaction confirmation for {tx_hash}...")
    try:
        confirmation_data = {
            "tx_hash": tx_hash,
            "status": "confirmed"
        }
        
        response = requests.post(
            f"{AGENT_B_URL}/confirm_tx",
            json=confirmation_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Transaction confirmation successful")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Transaction confirmation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Transaction confirmation error: {e}")
        return False

def test_status_endpoint():
    """Test status endpoint"""
    print("\n📊 Testing status endpoint...")
    try:
        response = requests.get(f"{AGENT_B_URL}/status")
        if response.status_code == 200:
            result = response.json()
            print("✅ Status endpoint successful")
            print(f"   Service: {result.get('service')}")
            print(f"   Cost Threshold: {result.get('cost_threshold')}")
            print(f"   Pending Transactions: {result.get('pending_transactions')}")
            return True
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False

def simulate_arduino_display(tx_hash):
    """Simulate Arduino B display"""
    print(f"\n📱 Arduino B Display Simulation:")
    print(f"   ✅ CONFIRMED: {tx_hash}")
    print(f"   [LCD would show this message]")
    print(f"   [Serial Monitor would log this]")

def run_complete_workflow():
    """Run complete workflow test"""
    print("🚀 Starting complete workflow test...")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed, stopping tests")
        return False
    
    # Test status endpoint
    test_status_endpoint()
    
    # Test each offer
    successful_transactions = []
    
    for i, offer in enumerate(TEST_OFFERS, 1):
        print(f"\n{'='*20} Test {i}/3 {'='*20}")
        result = test_offer_response(offer)
        
        if result and result.get('status') == 'accepted':
            tx_hash = result.get('tx_hash')
            if tx_hash:
                successful_transactions.append(tx_hash)
                
                # Simulate transaction confirmation after a delay
                print(f"⏳ Simulating payment confirmation delay...")
                time.sleep(2)
                
                # Test transaction confirmation
                if test_transaction_confirmation(tx_hash):
                    # Simulate Arduino display
                    simulate_arduino_display(tx_hash)
    
    print(f"\n{'='*50}")
    print(f"📊 Test Summary:")
    print(f"   Total offers tested: {len(TEST_OFFERS)}")
    print(f"   Successful transactions: {len(successful_transactions)}")
    print(f"   Transaction hashes: {successful_transactions}")
    
    return len(successful_transactions) > 0

def main():
    """Main test function"""
    print("🧪 Agent B - Seller Logic Test Suite")
    print("=" * 50)
    print(f"Testing Agent B at: {AGENT_B_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Check if Agent B is running
    try:
        response = requests.get(f"{AGENT_B_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Agent B is not running or not responding")
            print("   Please start Agent B first: python agent_b.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Agent B")
        print("   Please start Agent B first: python agent_b.py")
        return
    
    # Run tests
    success = run_complete_workflow()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("   Agent B is working correctly")
        print("   Ready for integration with Router and Blockchain Service")
    else:
        print("\n❌ Some tests failed")
        print("   Please check Agent B logs for errors")

if __name__ == "__main__":
    main()
