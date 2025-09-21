"""
Simple test runner for payment service validation
"""

import requests
import json
import time

def test_mock_service():
    """Quick test of mock payment service"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Mock Payment Service...")
    
    try:
        # 1. Health check
        print("1. Health check...", end=" ")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            return False
        
        # 2. Send payment
        print("2. Send payment...", end=" ")
        payment_data = {
            "from_address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
            "to_address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
            "amount": 1000000,
            "metadata": {"test": True}
        }
        
        response = requests.post(f"{base_url}/send_payment", json=payment_data)
        if response.status_code == 200:
            result = response.json()
            job_id = result["job_id"]
            print(f"✅ PASS (Job ID: {job_id})")
        else:
            print("❌ FAIL")
            return False
        
        # 3. Check status
        print("3. Check status...", end=" ")
        response = requests.get(f"{base_url}/tx_status/{job_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ PASS (Status: {status['status']})")
        else:
            print("❌ FAIL")
            return False
        
        # 4. Check wallet balance
        print("4. Check balance...", end=" ")
        test_address = "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"
        response = requests.get(f"{base_url}/wallet/{test_address}/balance")
        if response.status_code == 200:
            balance = response.json()
            print(f"✅ PASS (Balance: {balance['balance_ada']} ADA)")
        else:
            print("❌ FAIL")
            return False
        
        print("\n🎉 All tests passed! Mock service is ready for team integration.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ FAIL - Service not running")
        print("\n💡 Start the service with: python blockchain/src/mock_payment_service.py")
        return False
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

if __name__ == "__main__":
    test_mock_service()