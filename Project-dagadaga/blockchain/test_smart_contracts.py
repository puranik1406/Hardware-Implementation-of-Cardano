"""
Comprehensive Testing Suite for Smart Contract Payment System
Tests all components: Plutus contracts, PyCardano integration, API endpoints
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

import pytest
import requests
from pydantic import BaseModel

# Add blockchain directory to path
sys.path.append(os.path.dirname(__file__))

try:
    from smart_contract_payment import SmartContractPaymentService, PlutusPaymentContract
    from deploy_contract import ContractDeployer
    SMART_CONTRACT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Smart contract modules not available: {e}")
    SMART_CONTRACT_AVAILABLE = False

class TestResult(BaseModel):
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    message: str
    details: Dict[str, Any] = {}

class SmartContractTestSuite:
    """Comprehensive test suite for smart contract system"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.api_base_url = "http://localhost:8000"
        self.test_addresses = {
            "sender": "addr_test1vr0twevuqcdgp5nytqyus5dvtzf8vd2mk7zus253s593v8g5j7k3n",
            "recipient": "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"
        }
        
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Run a single test and record results"""
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if result.get("success", True):
                test_result = TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message=result.get("message", "Test passed"),
                    details=result.get("details", {})
                )
            else:
                test_result = TestResult(
                    test_name=test_name,
                    status="FAIL", 
                    duration=duration,
                    message=result.get("error", "Test failed"),
                    details=result.get("details", {})
                )
                
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Exception: {str(e)}",
                details={"exception_type": type(e).__name__}
            )
        
        self.results.append(test_result)
        print(f"{test_result.status}: {test_name} ({test_result.duration:.2f}s)")
        
        return test_result
    
    def test_contract_compilation(self) -> Dict[str, Any]:
        """Test Plutus contract compilation"""
        try:
            deployer = ContractDeployer("preprod")
            plutus_file = deployer.compile_plutus_contract("PaymentContract")
            
            # Verify file exists and has content
            if os.path.exists(plutus_file):
                with open(plutus_file, "r") as f:
                    contract_data = json.load(f)
                
                if "cborHex" in contract_data and len(contract_data["cborHex"]) > 0:
                    return {
                        "success": True,
                        "message": "Contract compiled successfully",
                        "details": {
                            "plutus_file": plutus_file,
                            "cbor_length": len(contract_data["cborHex"])
                        }
                    }
            
            return {"success": False, "error": "Compilation failed or invalid output"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_contract_deployment(self) -> Dict[str, Any]:
        """Test smart contract deployment"""
        try:
            deployer = ContractDeployer("preprod")
            deployment = deployer.deploy_contract("PaymentContract")
            
            # Verify deployment info
            required_fields = ["script_address", "script_hash", "cbor_hex", "network"]
            for field in required_fields:
                if field not in deployment:
                    return {"success": False, "error": f"Missing deployment field: {field}"}
            
            return {
                "success": True,
                "message": "Contract deployed successfully",
                "details": deployment
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_smart_contract_service_init(self) -> Dict[str, Any]:
        """Test smart contract service initialization"""
        if not SMART_CONTRACT_AVAILABLE:
            return {"success": False, "error": "Smart contract modules not available"}
        
        try:
            service = SmartContractPaymentService()
            
            # Test basic properties
            if hasattr(service, 'contract') and hasattr(service, 'payments'):
                return {
                    "success": True,
                    "message": "Smart contract service initialized",
                    "details": {
                        "contract_address": service.contract.contract.script_address,
                        "network": service.contract.network
                    }
                }
            else:
                return {"success": False, "error": "Service missing required attributes"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_api_server_health(self) -> Dict[str, Any]:
        """Test API server health and availability"""
        try:
            response = requests.get(f"{self.api_base_url}/", timeout=5)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "API server healthy",
                    "details": {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}"
                }
                
        except requests.RequestException as e:
            return {"success": False, "error": f"API connection failed: {str(e)}"}
    
    def test_send_payment_endpoint(self) -> Dict[str, Any]:
        """Test /send_payment endpoint"""
        try:
            payload = {
                "from_address": self.test_addresses["sender"],
                "to_address": self.test_addresses["recipient"],
                "amount": 1000000,  # 1 ADA
                "metadata": {
                    "test": "smart_contract_payment",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.api_base_url}/send_payment",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["job_id", "tx_hash", "status"]
                
                for field in required_fields:
                    if field not in data:
                        return {"success": False, "error": f"Missing response field: {field}"}
                
                return {
                    "success": True,
                    "message": "Send payment endpoint working",
                    "details": {
                        "job_id": data["job_id"],
                        "tx_hash": data["tx_hash"],
                        "status": data["status"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Payment endpoint returned {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_tx_status_endpoint(self) -> Dict[str, Any]:
        """Test /poll/tx_status endpoint"""
        try:
            response = requests.get(f"{self.api_base_url}/poll/tx_status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "tx_hash", "confirmations", "message"]
                
                for field in required_fields:
                    if field not in data:
                        return {"success": False, "error": f"Missing response field: {field}"}
                
                return {
                    "success": True,
                    "message": "TX status endpoint working",
                    "details": data
                }
            else:
                return {
                    "success": False,
                    "error": f"TX status endpoint returned {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_arduino_integration_format(self) -> Dict[str, Any]:
        """Test Arduino-compatible response format"""
        try:
            response = requests.get(f"{self.api_base_url}/poll/tx_status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check Arduino compatibility
                tx_hash = data.get("tx_hash", "")
                message = data.get("message", "")
                
                if len(tx_hash) >= 16 and message in ["TX_CONFIRMED", "TX_PENDING"]:
                    # Simulate Arduino display format
                    arduino_display = f"{message}:{tx_hash[:16]}"
                    
                    return {
                        "success": True,
                        "message": "Arduino format compatible",
                        "details": {
                            "arduino_display": arduino_display,
                            "tx_hash_length": len(tx_hash),
                            "message_format": message
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Incompatible Arduino format"
                    }
            else:
                return {"success": False, "error": "Failed to get status"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_end_to_end_flow(self) -> Dict[str, Any]:
        """Test complete payment flow"""
        try:
            # Step 1: Send payment
            payload = {
                "from_address": self.test_addresses["sender"],
                "to_address": self.test_addresses["recipient"],
                "amount": 500000,  # 0.5 ADA
                "metadata": {"test": "e2e_flow"}
            }
            
            send_response = requests.post(
                f"{self.api_base_url}/send_payment",
                json=payload,
                timeout=10
            )
            
            if send_response.status_code != 200:
                return {"success": False, "error": "Payment initiation failed"}
            
            payment_data = send_response.json()
            job_id = payment_data["job_id"]
            
            # Step 2: Check initial status
            time.sleep(1)
            status_response = requests.get(f"{self.api_base_url}/poll/tx_status", timeout=5)
            
            if status_response.status_code != 200:
                return {"success": False, "error": "Status check failed"}
            
            status_data = status_response.json()
            
            return {
                "success": True,
                "message": "End-to-end flow working",
                "details": {
                    "payment": payment_data,
                    "status": status_data,
                    "flow_complete": True
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🧪 Starting Smart Contract Test Suite")
        print("=" * 50)
        
        test_functions = [
            ("Contract Compilation", self.test_contract_compilation),
            ("Contract Deployment", self.test_contract_deployment),
            ("Smart Contract Service Init", self.test_smart_contract_service_init),
            ("API Server Health", self.test_api_server_health),
            ("Send Payment Endpoint", self.test_send_payment_endpoint),
            ("TX Status Endpoint", self.test_tx_status_endpoint),
            ("Arduino Integration Format", self.test_arduino_integration_format),
            ("End-to-End Flow", self.test_end_to_end_flow)
        ]
        
        for test_name, test_func in test_functions:
            self.run_test(test_name, test_func)
        
        # Generate summary
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        total = len(self.results)
        
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {passed}/{total} passed, {failed} failed")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if result.status == "FAIL":
                    print(f"   • {result.test_name}: {result.message}")
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0,
            "results": [r.dict() for r in self.results]
        }

def main():
    """Run the test suite"""
    test_suite = SmartContractTestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Detailed results saved to: test_results.json")
    
    # Exit with appropriate code
    exit_code = 0 if results["failed"] == 0 else 1
    return exit_code

if __name__ == "__main__":
    exit(main())