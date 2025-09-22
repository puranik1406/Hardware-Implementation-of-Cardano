"""
Integration tests for the complete Cardano-Arduino-AI system
"""

import asyncio
import json
import pytest
import requests
import time
from typing import Dict, Any

# Test configuration
BASE_URLS = {
    "agent_a": "http://localhost:8001",
    "agent_b": "http://localhost:8002", 
    "router": "http://localhost:8003",
    "payment": "http://localhost:8000"
}

TIMEOUT = 30

class TestSystemIntegration:
    """Test complete system integration"""
    
    @pytest.fixture(autouse=True)
    def setup_system(self):
        """Ensure all services are running"""
        for service, url in BASE_URLS.items():
            try:
                response = requests.get(f"{url}/", timeout=5)
                assert response.status_code == 200, f"{service} not responding"
            except Exception as e:
                pytest.skip(f"Service {service} not available: {e}")
    
    def test_health_checks(self):
        """Test that all services are healthy"""
        for service, url in BASE_URLS.items():
            response = requests.get(f"{url}/", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "online"]
    
    def test_system_status(self):
        """Test router system status endpoint"""
        response = requests.get(f"{BASE_URLS['router']}/status", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "router_status" in data
        assert "agents" in data
        assert "system_stats" in data
        
        # Check that all agents are reported as online
        agents = data["agents"]
        for agent in ["agent_a", "agent_b", "payment_service"]:
            assert agent in agents
            assert agents[agent]["status"] == "online"
    
    def test_arduino_trigger_workflow(self):
        """Test complete Arduino trigger workflow"""
        # Step 1: Trigger Arduino offer
        trigger_data = {
            "amount": 150.0,
            "product": "Test Sensor Data",
            "context": {"test": True}
        }
        
        response = requests.post(
            f"{BASE_URLS['router']}/arduino_trigger",
            json=trigger_data,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "forwarded"
        assert "agent_a_response" in result
        
        # Extract offer ID from Agent A response
        agent_a_response = result["agent_a_response"]
        offer_id = agent_a_response["offer_id"]
        
        # Step 2: Check that offer was created in router
        response = requests.get(f"{BASE_URLS['router']}/offers/{offer_id}", timeout=5)
        assert response.status_code == 200
        
        offer = response.json()
        assert offer["offer_id"] == offer_id
        assert offer["amount"] == 150.0
    
    def test_agent_a_trigger(self):
        """Test Agent A offer creation"""
        trigger_data = {
            "trigger_type": "test",
            "amount": 120.0,
            "product": "Test Product"
        }
        
        response = requests.post(
            f"{BASE_URLS['agent_a']}/trigger",
            json=trigger_data,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "offer_id" in result
        assert "status" in result
        assert "amount" in result
        assert result["amount"] == 120.0
    
    def test_agent_b_response(self):
        """Test Agent B offer response"""
        offer_data = {
            "offer_id": "test_offer_123",
            "agent_id": "agent_a",
            "amount": 150.0,
            "product": "Test Product",
            "status": "pending"
        }
        
        response = requests.post(
            f"{BASE_URLS['agent_b']}/respond",
            json=offer_data,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "decision" in result
        assert result["decision"] in ["accept", "reject"]
        assert result["amount"] == 150.0
    
    def test_payment_service_flow(self):
        """Test payment service transaction flow"""
        # Step 1: Create test payment
        response = requests.post(f"{BASE_URLS['payment']}/test_payment", timeout=TIMEOUT)
        assert response.status_code == 200
        
        result = response.json()
        assert "job_id" in result
        assert result["status"] == "pending"
        
        job_id = result["job_id"]
        
        # Step 2: Wait and check job status
        max_attempts = 10
        for attempt in range(max_attempts):
            response = requests.get(
                f"{BASE_URLS['payment']}/job_status/{job_id}",
                timeout=5
            )
            assert response.status_code == 200
            
            status = response.json()
            if status["status"] in ["completed", "failed"]:
                break
            
            time.sleep(2)
        
        # Step 3: Verify final status
        assert status["status"] in ["completed", "failed"]
        if status["status"] == "completed":
            assert "transaction_hash" in status
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This test simulates the complete Arduino-to-blockchain workflow
        
        # Step 1: Arduino A triggers offer
        arduino_trigger = {
            "amount": 125.0,
            "product": "Arduino Sensor Reading",
            "context": {
                "sensor_value": 567,
                "timestamp": int(time.time())
            }
        }
        
        response = requests.post(
            f"{BASE_URLS['router']}/arduino_trigger",
            json=arduino_trigger,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        # Step 2: Extract offer details
        result = response.json()
        agent_a_response = result["agent_a_response"]
        offer_id = agent_a_response["offer_id"]
        
        # Step 3: Wait for workflow to complete (router will coordinate agents)
        time.sleep(5)
        
        # Step 4: Check final offer status
        response = requests.get(f"{BASE_URLS['router']}/offers/{offer_id}", timeout=5)
        assert response.status_code == 200
        
        final_offer = response.json()
        assert final_offer["offer_id"] == offer_id
        
        # The offer should have been processed by now
        assert final_offer["status"] in ["accept", "reject", "completed", "pending"]
        
        # Step 5: Check system statistics
        response = requests.get(f"{BASE_URLS['router']}/status", timeout=5)
        assert response.status_code == 200
        
        status = response.json()
        stats = status["system_stats"]
        assert stats["total_offers"] >= 1
    
    def test_concurrent_offers(self):
        """Test system handling of multiple concurrent offers"""
        # Create multiple offers simultaneously
        import threading
        
        results = []
        errors = []
        
        def create_offer(offer_num):
            try:
                trigger_data = {
                    "amount": 100.0 + offer_num * 10,
                    "product": f"Concurrent Test {offer_num}",
                    "context": {"concurrent_test": True, "offer_num": offer_num}
                }
                
                response = requests.post(
                    f"{BASE_URLS['router']}/arduino_trigger",
                    json=trigger_data,
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    results.append(response.json())
                else:
                    errors.append(f"Offer {offer_num}: HTTP {response.status_code}")
                    
            except Exception as e:
                errors.append(f"Offer {offer_num}: {str(e)}")
        
        # Create 5 concurrent offers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_offer, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        # Check that all offers have unique IDs
        offer_ids = [r["agent_a_response"]["offer_id"] for r in results]
        assert len(set(offer_ids)) == 5, "Duplicate offer IDs detected"

class TestErrorHandling:
    """Test system error handling and recovery"""
    
    def test_invalid_offer_data(self):
        """Test handling of invalid offer data"""
        invalid_data = {
            "amount": "invalid_amount",  # Should be numeric
            "product": "",  # Empty product
        }
        
        response = requests.post(
            f"{BASE_URLS['router']}/arduino_trigger",
            json=invalid_data,
            timeout=5
        )
        
        # Should handle gracefully, not crash
        assert response.status_code in [400, 422, 500]
    
    def test_nonexistent_offer_lookup(self):
        """Test looking up non-existent offers"""
        fake_offer_id = "nonexistent_offer_12345"
        
        response = requests.get(
            f"{BASE_URLS['router']}/offers/{fake_offer_id}",
            timeout=5
        )
        assert response.status_code == 404
    
    def test_service_resilience(self):
        """Test system behavior when services are under load"""
        # Send many requests quickly to test resilience
        for i in range(20):
            response = requests.get(f"{BASE_URLS['router']}/status", timeout=2)
            # Should not crash or timeout
            assert response.status_code == 200

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])