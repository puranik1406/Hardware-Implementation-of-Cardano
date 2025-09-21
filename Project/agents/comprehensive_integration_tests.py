#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Agent A
Tests all components: Agent A, Router, AWS Bedrock, and end-to-end flows
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import concurrent.futures
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationTestSuite:
    """Comprehensive integration test suite for Agent A"""
    
    def __init__(self):
        self.agent_a_url = "http://localhost:8001"
        self.router_url = "http://localhost:5000"
        self.test_results = []
        self.start_time = time.time()
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
    
    def test_agent_a_health(self) -> bool:
        """Test Agent A service health"""
        try:
            response = requests.get(f"{self.agent_a_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Agent A Health", True, f"Service running: {data.get('service', 'Unknown')}")
                return True
            else:
                self.log_test_result("Agent A Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Agent A Health", False, str(e))
            return False
    
    def test_router_connectivity(self) -> bool:
        """Test Router service connectivity"""
        try:
            response = requests.get(f"{self.router_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test_result("Router Connectivity", True, "Router service accessible")
                return True
            else:
                self.log_test_result("Router Connectivity", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Router Connectivity", False, str(e))
            return False
    
    def test_router_status_via_agent_a(self) -> bool:
        """Test Router status through Agent A"""
        try:
            response = requests.get(f"{self.agent_a_url}/agentA/router_status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                router_status = data.get('router_status', {})
                if router_status.get('status') == 'connected':
                    self.log_test_result("Router Status via Agent A", True, "Router connected through Agent A")
                    return True
                else:
                    self.log_test_result("Router Status via Agent A", False, f"Router status: {router_status}")
                    return False
            else:
                self.log_test_result("Router Status via Agent A", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Router Status via Agent A", False, str(e))
            return False
    
    def test_offer_creation(self) -> bool:
        """Test offer creation endpoint"""
        try:
            test_trigger = {
                "trigger_type": "arduino",
                "amount": 1000000,
                "context": {"test": True},
                "timestamp": datetime.now().isoformat(),
                "source": "test_script"
            }
            
            response = requests.post(
                f"{self.agent_a_url}/agentA/propose",
                json=test_trigger,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Offer Creation", True, f"Offer created: {data.get('offer_id', 'Unknown')}")
                return True
            else:
                self.log_test_result("Offer Creation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Offer Creation", False, str(e))
            return False
    
    def test_router_integration(self) -> bool:
        """Test complete Router integration flow"""
        try:
            test_trigger = {
                "trigger_type": "arduino",
                "amount": 2500000,  # 2.5 ADA in lovelace
                "context": {
                    "button_type": "button_1",
                    "priority": "high"
                },
                "timestamp": datetime.now().isoformat(),
                "source": "integration_test"
            }
            
            response = requests.post(
                f"{self.agent_a_url}/agentA/send_to_router",
                json=test_trigger,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'sent_to_router':
                    self.log_test_result("Router Integration", True, f"Offer sent to Router: {data.get('amount_ada', 'Unknown')} ADA")
                    return True
                else:
                    self.log_test_result("Router Integration", False, f"Unexpected status: {data.get('status')}")
                    return False
            else:
                self.log_test_result("Router Integration", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Router Integration", False, str(e))
            return False
    
    def test_direct_router_communication(self) -> bool:
        """Test direct communication with Router service"""
        try:
            test_offer = {
                "from_agent": "agent_a",
                "to_agent": "agent_b",
                "amount": 1.5,
                "currency": "ADA",
                "description": "Integration test offer",
                "timestamp": datetime.now().isoformat() + "Z",
                "metadata": {
                    "arduino_trigger": True,
                    "button_type": "button_1",
                    "priority": "medium",
                    "test": True
                }
            }
            
            response = requests.post(
                f"{self.router_url}/send_offer",
                json=test_offer,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test_result("Direct Router Communication", True, "Direct Router communication successful")
                return True
            else:
                self.log_test_result("Direct Router Communication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test_result("Direct Router Communication", False, str(e))
            return False
    
    def test_performance(self) -> bool:
        """Test performance with multiple concurrent requests"""
        try:
            def send_request():
                test_trigger = {
                    "trigger_type": "arduino",
                    "amount": 1000000,
                    "context": {"test": True},
                    "timestamp": datetime.now().isoformat(),
                    "source": "performance_test"
                }
                
                response = requests.post(
                    f"{self.agent_a_url}/agentA/propose",
                    json=test_trigger,
                    timeout=5
                )
                return response.status_code == 200
            
            # Send 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(send_request) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_count = sum(results)
            if success_count >= 8:  # Allow 2 failures
                self.log_test_result("Performance Test", True, f"{success_count}/10 requests successful")
                return True
            else:
                self.log_test_result("Performance Test", False, f"Only {success_count}/10 requests successful")
                return False
        except Exception as e:
            self.log_test_result("Performance Test", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs"""
        try:
            # Test with invalid data
            invalid_trigger = {
                "trigger_type": "invalid",
                "amount": -1000,  # Negative amount
                "context": None
            }
            
            response = requests.post(
                f"{self.agent_a_url}/agentA/propose",
                json=invalid_trigger,
                timeout=5
            )
            
            # Should handle gracefully (either accept with validation or return error)
            if response.status_code in [200, 400, 422]:
                self.log_test_result("Error Handling", True, f"Handled invalid input gracefully: {response.status_code}")
                return True
            else:
                self.log_test_result("Error Handling", False, f"Unexpected response: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Error Handling", False, str(e))
            return False
    
    def test_aws_bedrock_fallback(self) -> bool:
        """Test AWS Bedrock fallback mechanism"""
        try:
            # Test with mock Bedrock mode
            response = requests.get(f"{self.agent_a_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                bedrock_mode = data.get('bedrock_mode', 'unknown')
                if bedrock_mode in ['mock', 'real']:
                    self.log_test_result("AWS Bedrock Fallback", True, f"Bedrock mode: {bedrock_mode}")
                    return True
                else:
                    self.log_test_result("AWS Bedrock Fallback", False, f"Unknown Bedrock mode: {bedrock_mode}")
                    return False
            else:
                self.log_test_result("AWS Bedrock Fallback", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("AWS Bedrock Fallback", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("🚀 Starting Comprehensive Integration Tests")
        logger.info("=" * 60)
        
        # Define test methods
        tests = [
            ("Agent A Health", self.test_agent_a_health),
            ("Router Connectivity", self.test_router_connectivity),
            ("Router Status via Agent A", self.test_router_status_via_agent_a),
            ("Offer Creation", self.test_offer_creation),
            ("Direct Router Communication", self.test_direct_router_communication),
            ("Router Integration", self.test_router_integration),
            ("Performance Test", self.test_performance),
            ("Error Handling", self.test_error_handling),
            ("AWS Bedrock Fallback", self.test_aws_bedrock_fallback)
        ]
        
        # Run tests
        for test_name, test_method in tests:
            logger.info(f"\n🔍 Running {test_name}...")
            try:
                test_method()
            except Exception as e:
                self.log_test_result(test_name, False, f"Test execution failed: {str(e)}")
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        # Generate report
        end_time = time.time()
        duration = end_time - self.start_time
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
                "duration_seconds": round(duration, 2)
            },
            "results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("INTEGRATION TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Integration is ready for production.")
        else:
            logger.info("⚠️  Some tests failed. Review the results above.")
        
        return report

def main():
    """Run comprehensive integration tests"""
    test_suite = IntegrationTestSuite()
    report = test_suite.run_all_tests()
    
    # Save report to file
    with open('integration_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n📊 Detailed report saved to: integration_test_report.json")
    
    return report

if __name__ == "__main__":
    main()
