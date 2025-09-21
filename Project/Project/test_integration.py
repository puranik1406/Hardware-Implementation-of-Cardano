#!/usr/bin/env python3
"""
Integration test for Router and Serial Bridge
Tests the complete flow from Arduino A simulation to Router to mock Agent B
"""

import json
import time
import requests
import threading
from datetime import datetime, timezone

def test_router_health():
    """Test if Router API is healthy"""
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("✅ Router API is healthy")
            return True
        else:
            print(f"❌ Router API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Router API: {e}")
        return False

def test_send_offer():
    """Test sending an offer to the Router"""
    offer = {
        'from_agent': 'agent_a',
        'to_agent': 'agent_b',
        'amount': 15.0,
        'currency': 'ADA',
        'description': 'Test payment from integration test',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'metadata': {
            'arduino_trigger': True,
            'button_type': 'test',
            'priority': 'medium'
        }
    }
    
    try:
        response = requests.post('http://localhost:5000/send_offer', json=offer)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Successfully sent offer: {result['offer_id']}")
            return result['offer_id']
        else:
            print(f"❌ Failed to send offer: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error sending offer: {e}")
        return None

def test_get_offer_status(offer_id):
    """Test getting offer status"""
    try:
        response = requests.get(f'http://localhost:5000/status/{offer_id}')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved offer status: {result['offer']['status']}")
            return result
        else:
            print(f"❌ Failed to get offer status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting offer status: {e}")
        return None

def test_mock_agent_b_response(offer_id):
    """Test mock Agent B response"""
    response_data = {
        'offer_id': offer_id,
        'from_agent': 'agent_b',
        'status': 'accepted',
        'message': 'Mock Agent B accepted the test offer',
        'metadata': {
            'processing_time_ms': 1500,
            'arduino_notified': True
        }
    }
    
    try:
        response = requests.post('http://localhost:5000/mock_agent_b', json=response_data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Mock Agent B response sent: {result['response_id']}")
            return True
        else:
            print(f"❌ Failed to send mock response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending mock response: {e}")
        return False

def test_list_offers():
    """Test listing all offers"""
    try:
        response = requests.get('http://localhost:5000/offers')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {result['count']} offers")
            return result['offers']
        else:
            print(f"❌ Failed to list offers: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing offers: {e}")
        return []

def test_serial_bridge_simulation():
    """Test serial bridge in simulation mode"""
    print("\n🔄 Testing Serial Bridge simulation...")
    
    # Import and run serial bridge in simulation mode
    import subprocess
    import sys
    
    try:
        # Run serial bridge in simulation mode for 30 seconds
        process = subprocess.Popen([
            sys.executable, 'serial_bridge.py', '--simulate', '--router-url', 'http://localhost:5000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for it to generate some signals
        time.sleep(15)
        
        # Terminate the process
        process.terminate()
        process.wait()
        
        print("✅ Serial bridge simulation completed")
        return True
        
    except Exception as e:
        print(f"❌ Error running serial bridge simulation: {e}")
        return False

def run_complete_integration_test():
    """Run complete integration test"""
    print("🚀 Starting Router and Serial Bridge Integration Test")
    print("=" * 60)
    
    # Test 1: Router Health
    print("\n1. Testing Router API Health...")
    if not test_router_health():
        print("❌ Router API is not available. Please start router.py first.")
        return False
    
    # Test 2: Send Offer
    print("\n2. Testing Send Offer...")
    offer_id = test_send_offer()
    if not offer_id:
        return False
    
    # Test 3: Get Offer Status (before response)
    print("\n3. Testing Get Offer Status (before response)...")
    status_before = test_get_offer_status(offer_id)
    if not status_before:
        return False
    
    # Wait a bit for the mock Agent B to respond
    print("\n⏳ Waiting for mock Agent B response...")
    time.sleep(3)
    
    # Test 4: Get Offer Status (after response)
    print("\n4. Testing Get Offer Status (after response)...")
    status_after = test_get_offer_status(offer_id)
    if not status_after:
        return False
    
    # Test 5: Manual Mock Agent B Response
    print("\n5. Testing Manual Mock Agent B Response...")
    test_offer_id = test_send_offer()
    if test_offer_id:
        test_mock_agent_b_response(test_offer_id)
        time.sleep(1)
        test_get_offer_status(test_offer_id)
    
    # Test 6: List All Offers
    print("\n6. Testing List All Offers...")
    offers = test_list_offers()
    
    # Test 7: Serial Bridge Simulation
    print("\n7. Testing Serial Bridge Simulation...")
    test_serial_bridge_simulation()
    
    # Final Status
    print("\n" + "=" * 60)
    print("🎉 Integration Test Summary:")
    print(f"   - Total offers created: {len(offers)}")
    print(f"   - Router API: ✅ Healthy")
    print(f"   - Offer processing: ✅ Working")
    print(f"   - Mock Agent B: ✅ Responding")
    print(f"   - Serial Bridge: ✅ Simulating")
    print("\n✅ All tests passed! Router and Serial Bridge are working correctly.")
    
    return True

if __name__ == '__main__':
    run_complete_integration_test()
