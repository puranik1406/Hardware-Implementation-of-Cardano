"""
Test script for Agent A service
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_DATA = {
    "trigger": {
        "trigger_type": "arduino",
        "amount": 1000000,  # 1 ADA in lovelace
        "context": {"test": True, "source": "test_script"},
        "timestamp": datetime.now().isoformat(),
        "source": "arduino_a"
    },
    "decision": {
        "offer_id": "test-offer-123",
        "counter_offer": {"amount": 1500000, "agent": "agent_b"},
        "context": {"test": True},
        "agent_b_response": {"status": "counter_offer", "amount": 1500000}
    }
}

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_propose_offer():
    """Test offer proposal endpoint"""
    print("\nTesting propose offer...")
    try:
        response = requests.post(
            f"{BASE_URL}/agentA/propose",
            json=TEST_DATA["trigger"],
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            # Store offer_id for decision test
            TEST_DATA["decision"]["offer_id"] = result["offer_id"]
            return True
        return False
    except Exception as e:
        print(f"Propose offer failed: {e}")
        return False

def test_decide_offer():
    """Test offer decision endpoint"""
    print("\nTesting decide offer...")
    try:
        response = requests.post(
            f"{BASE_URL}/agentA/decide",
            json=TEST_DATA["decision"],
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Decide offer failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")
    
    # Test with invalid amount
    invalid_trigger = TEST_DATA["trigger"].copy()
    invalid_trigger["amount"] = -1000  # Negative amount
    
    try:
        response = requests.post(
            f"{BASE_URL}/agentA/propose",
            json=invalid_trigger,
            headers={"Content-Type": "application/json"}
        )
        print(f"Invalid amount test - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Invalid amount test failed: {e}")
    
    # Test with missing required fields
    incomplete_trigger = {"trigger_type": "test"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/agentA/propose",
            json=incomplete_trigger,
            headers={"Content-Type": "application/json"}
        )
        print(f"Incomplete data test - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Incomplete data test failed: {e}")

def run_performance_test():
    """Run performance test with multiple requests"""
    print("\nRunning performance test...")
    
    start_time = time.time()
    success_count = 0
    total_requests = 10
    
    for i in range(total_requests):
        try:
            trigger = TEST_DATA["trigger"].copy()
            trigger["amount"] = 1000000 + (i * 100000)  # Vary amounts
            
            response = requests.post(
                f"{BASE_URL}/agentA/propose",
                json=trigger,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                success_count += 1
            
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Performance test results:")
    print(f"  Total requests: {total_requests}")
    print(f"  Successful: {success_count}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Average response time: {duration/total_requests:.2f} seconds")

def main():
    """Run all tests"""
    print("Starting Agent A service tests...")
    print("=" * 50)
    
    # Wait for service to be ready
    print("Waiting for service to start...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Propose Offer", test_propose_offer),
        ("Decide Offer", test_decide_offer),
        ("Edge Cases", test_edge_cases),
        ("Performance Test", run_performance_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()

