"""
Masumi Network Configuration and Client
Handles local Masumi protocol integration with Cardano
"""

import os
import json
import requests
from typing import Dict, Optional, List
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MasumiConfig:
    """Configuration class for Masumi Network settings"""
    
    def __init__(self):
        self.network_url = os.getenv("MASUMI_NETWORK_URL", "http://localhost:3001")
        self.api_key = os.getenv("MASUMI_API_KEY", "")
        self.testnet = os.getenv("MASUMI_TESTNET", "true").lower() == "true"
        self.timeout = int(os.getenv("MASUMI_TIMEOUT", "30"))
        
        # Masumi protocol specific settings
        self.protocol_version = "1.0"
        self.chain_id = "masumi-testnet" if self.testnet else "masumi-mainnet"
        
        logger.info(f"Masumi config: {self.network_url} (testnet: {self.testnet})")
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return {
            "network_url": self.network_url,
            "testnet": self.testnet,
            "protocol_version": self.protocol_version,
            "chain_id": self.chain_id,
            "timeout": self.timeout
        }

class MasumiClient:
    """Client for interacting with Masumi Network"""
    
    def __init__(self, config: Optional[MasumiConfig] = None):
        self.config = config or MasumiConfig()
        self.session = requests.Session()
        
        # Set up authentication headers
        if self.config.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "X-Masumi-Version": self.config.protocol_version
            })
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Masumi API"""
        url = f"{self.config.network_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=self.config.timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=self.config.timeout)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=self.config.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Masumi API request failed: {e}")
            raise Exception(f"Masumi API error: {str(e)}")
    
    def get_network_status(self) -> Dict:
        """Get Masumi network status"""
        return self._make_request("/api/v1/network/status")
    
    def get_node_info(self) -> Dict:
        """Get local Masumi node information"""
        return self._make_request("/api/v1/node/info")
    
    def create_transaction(self, tx_request: Dict) -> Dict:
        """
        Create a transaction request through Masumi protocol
        
        Args:
            tx_request: {
                "from_address": str,
                "to_address": str,
                "amount": int (lovelace),
                "metadata": dict (optional)
            }
        """
        masumi_tx = {
            "protocol": "cardano",
            "network": "preprod" if self.config.testnet else "mainnet",
            "transaction": tx_request,
            "timestamp": datetime.now().isoformat(),
            "chain_id": self.config.chain_id
        }
        
        return self._make_request("/api/v1/transactions/create", "POST", masumi_tx)
    
    def submit_transaction(self, tx_data: Dict) -> Dict:
        """Submit a signed transaction through Masumi"""
        return self._make_request("/api/v1/transactions/submit", "POST", tx_data)
    
    def get_transaction_status(self, tx_id: str) -> Dict:
        """Get transaction status from Masumi"""
        return self._make_request(f"/api/v1/transactions/{tx_id}/status")
    
    def get_wallet_info(self, address: str) -> Dict:
        """Get wallet information through Masumi"""
        return self._make_request(f"/api/v1/wallets/{address}")
    
    def register_webhook(self, webhook_url: str, events: List[str]) -> Dict:
        """Register a webhook for transaction events"""
        webhook_data = {
            "url": webhook_url,
            "events": events,  # e.g., ["transaction.confirmed", "transaction.failed"]
            "active": True
        }
        return self._make_request("/api/v1/webhooks", "POST", webhook_data)

# Mock Masumi client for development when real Masumi is not available
class MockMasumiClient:
    """Mock Masumi client for development and testing"""
    
    def __init__(self, config: Optional[MasumiConfig] = None):
        self.config = config or MasumiConfig()
        logger.info("Using Mock Masumi Client (no real network connection)")
    
    def get_network_status(self) -> Dict:
        return {
            "status": "online",
            "network": "testnet" if self.config.testnet else "mainnet",
            "node_version": "mock-1.0.0",
            "sync_progress": 100.0,
            "connected_peers": 8
        }
    
    def get_node_info(self) -> Dict:
        return {
            "version": "mock-masumi-1.0.0",
            "protocol_version": self.config.protocol_version,
            "chain_id": self.config.chain_id,
            "block_height": 8500000,
            "network_magic": 1 if self.config.testnet else 764824073
        }
    
    def create_transaction(self, tx_request: Dict) -> Dict:
        # Simulate transaction creation
        import uuid
        tx_id = f"masumi_tx_{uuid.uuid4().hex[:16]}"
        
        return {
            "tx_id": tx_id,
            "status": "created",
            "cardano_tx_hash": None,  # Will be set after submission
            "created_at": datetime.now().isoformat(),
            "estimated_fee": 170000,
            "estimated_confirmation_time": 60
        }
    
    def submit_transaction(self, tx_data: Dict) -> Dict:
        # Simulate successful submission
        import uuid
        cardano_tx_hash = f"tx_{uuid.uuid4().hex[:56]}"
        
        return {
            "tx_id": tx_data.get("tx_id"),
            "cardano_tx_hash": cardano_tx_hash,
            "status": "submitted",
            "submitted_at": datetime.now().isoformat(),
            "network": "preprod" if self.config.testnet else "mainnet"
        }
    
    def get_transaction_status(self, tx_id: str) -> Dict:
        # Simulate confirmation after some time
        return {
            "tx_id": tx_id,
            "status": "confirmed",
            "cardano_tx_hash": f"tx_{tx_id.replace('masumi_tx_', '')}_cardano",
            "confirmations": 5,
            "block_height": 8500123,
            "confirmed_at": datetime.now().isoformat()
        }
    
    def get_wallet_info(self, address: str) -> Dict:
        return {
            "address": address,
            "balance": 100000000,  # 100 ADA in lovelace
            "utxo_count": 3,
            "last_activity": datetime.now().isoformat()
        }
    
    def register_webhook(self, webhook_url: str, events: List[str]) -> Dict:
        return {
            "webhook_id": f"webhook_{len(events)}",
            "url": webhook_url,
            "events": events,
            "status": "registered"
        }

def get_masumi_client(use_mock: bool = None) -> MasumiClient:
    """Factory function to get appropriate Masumi client"""
    if use_mock is None:
        use_mock = os.getenv("MASUMI_MOCK_MODE", "false").lower() == "true"
    
    config = MasumiConfig()
    
    if use_mock:
        return MockMasumiClient(config)
    else:
        return MasumiClient(config)

# Test function
async def test_masumi_connection():
    """Test Masumi network connectivity"""
    try:
        client = get_masumi_client()
        
        # Test network status
        status = client.get_network_status()
        print(f"✅ Masumi network status: {status.get('status')}")
        
        # Test node info
        node_info = client.get_node_info()
        print(f"✅ Node version: {node_info.get('version')}")
        
        # Test transaction creation (mock)
        tx_request = {
            "from_address": "addr_test1qq...",
            "to_address": "addr_test1vr...",
            "amount": 1000000,
            "metadata": {"test": True}
        }
        tx_result = client.create_transaction(tx_request)
        print(f"✅ Transaction created: {tx_result.get('tx_id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Masumi connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Run connection test
    import asyncio
    asyncio.run(test_masumi_connection())