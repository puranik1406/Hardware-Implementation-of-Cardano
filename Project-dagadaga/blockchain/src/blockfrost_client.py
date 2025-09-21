"""
Blockfrost API Client for Cardano Preprod Testnet
Handles transaction monitoring and wallet balance queries
"""

import os
import requests
import time
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class BlockfrostClient:
    """Client for interacting with Blockfrost API for Cardano preprod testnet"""
    
    def __init__(self, project_id: Optional[str] = None, base_url: Optional[str] = None):
        self.project_id = project_id or os.getenv("BLOCKFROST_PROJECT_ID")
        self.base_url = base_url or os.getenv("BLOCKFROST_BASE_URL", "https://cardano-preprod.blockfrost.io/api/v0")
        
        if not self.project_id:
            raise ValueError("BLOCKFROST_PROJECT_ID environment variable is required")
        
        self.headers = {
            "project_id": self.project_id,
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized Blockfrost client for {self.base_url}")
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Blockfrost API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Blockfrost API request failed: {e}")
            raise Exception(f"Blockfrost API error: {str(e)}")
    
    def get_network_info(self) -> Dict:
        """Get current network information"""
        return self._make_request("/network")
    
    def get_latest_block(self) -> Dict:
        """Get information about the latest block"""
        return self._make_request("/blocks/latest")
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction details by hash"""
        return self._make_request(f"/txs/{tx_hash}")
    
    def get_transaction_utxos(self, tx_hash: str) -> Dict:
        """Get transaction UTXOs (inputs and outputs)"""
        return self._make_request(f"/txs/{tx_hash}/utxos")
    
    def get_address_info(self, address: str) -> Dict:
        """Get address information including balance"""
        return self._make_request(f"/addresses/{address}")
    
    def get_address_utxos(self, address: str) -> List[Dict]:
        """Get UTXOs for a specific address"""
        return self._make_request(f"/addresses/{address}/utxos")
    
    def get_address_transactions(self, address: str, count: int = 10) -> List[Dict]:
        """Get transaction history for an address"""
        return self._make_request(f"/addresses/{address}/transactions?count={count}")
    
    def submit_transaction(self, tx_data: bytes) -> Dict:
        """Submit a signed transaction to the network"""
        # Note: This requires the transaction to be properly signed and serialized
        # Implementation depends on the transaction format from PyCardano
        endpoint = "/tx/submit"
        headers = {**self.headers, "Content-Type": "application/cbor"}
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=tx_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Transaction submission failed: {e}")
            raise Exception(f"Transaction submission error: {str(e)}")
    
    def wait_for_transaction_confirmation(self, tx_hash: str, max_wait_time: int = 300) -> Dict:
        """
        Wait for a transaction to be confirmed on the blockchain
        Returns transaction details once confirmed
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                tx_info = self.get_transaction(tx_hash)
                if tx_info:
                    logger.info(f"Transaction {tx_hash} confirmed in block {tx_info.get('block_height')}")
                    return tx_info
            except Exception as e:
                # Transaction not yet confirmed, continue waiting
                logger.debug(f"Transaction {tx_hash} not yet confirmed: {e}")
            
            time.sleep(10)  # Check every 10 seconds
        
        raise TimeoutError(f"Transaction {tx_hash} not confirmed within {max_wait_time} seconds")
    
    def get_transaction_confirmations(self, tx_hash: str) -> int:
        """Get number of confirmations for a transaction"""
        try:
            tx_info = self.get_transaction(tx_hash)
            latest_block = self.get_latest_block()
            
            tx_block_height = tx_info.get('block_height')
            latest_block_height = latest_block.get('height')
            
            if tx_block_height and latest_block_height:
                return latest_block_height - tx_block_height + 1
            return 0
            
        except Exception as e:
            logger.warning(f"Could not get confirmations for {tx_hash}: {e}")
            return 0
    
    def validate_address(self, address: str) -> bool:
        """Validate if an address is properly formatted and exists"""
        try:
            self.get_address_info(address)
            return True
        except Exception:
            return False
    
    def get_epoch_info(self) -> Dict:
        """Get current epoch information"""
        return self._make_request("/epochs/latest")

# Utility functions for common operations
def lovelace_to_ada(lovelace: int) -> float:
    """Convert lovelace to ADA"""
    return lovelace / 1_000_000

def ada_to_lovelace(ada: float) -> int:
    """Convert ADA to lovelace"""
    return int(ada * 1_000_000)

def format_tx_hash(tx_hash: str) -> str:
    """Format transaction hash for display"""
    if len(tx_hash) > 16:
        return f"{tx_hash[:8]}...{tx_hash[-8:]}"
    return tx_hash

# Test function
async def test_blockfrost_connection():
    """Test Blockfrost API connectivity"""
    try:
        client = BlockfrostClient()
        
        # Test basic connectivity
        network_info = client.get_network_info()
        print(f"✅ Connected to Cardano {network_info.get('network_name', 'unknown')}")
        
        # Test latest block
        latest_block = client.get_latest_block()
        print(f"✅ Latest block: {latest_block.get('height')} (slot: {latest_block.get('slot')})")
        
        # Test epoch info
        epoch_info = client.get_epoch_info()
        print(f"✅ Current epoch: {epoch_info.get('epoch')} (progress: {epoch_info.get('progress', 0):.1%})")
        
        return True
        
    except Exception as e:
        print(f"❌ Blockfrost connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Run connection test
    import asyncio
    asyncio.run(test_blockfrost_connection())