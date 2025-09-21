"""
Test Wallet Generator and Manager for Arduino-to-Cardano Project
Generates test wallets, funds them, and manages wallet data securely
"""

import os
import json
import secrets
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import hashlib
import base64

class TestWalletManager:
    """Manages test wallets for the Arduino-to-Cardano project"""
    
    def __init__(self, wallet_file: str = "config/test_wallets.json"):
        self.wallet_file = wallet_file
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for wallet data"""
        key_file = "config/.wallet_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create new encryption key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def generate_test_wallets(self) -> Dict[str, Dict]:
        """
        Generate test wallets for the project
        Note: These are test addresses for preprod network only
        """
        wallets = {
            "agent_a_wallet": {
                "name": "Agent A Primary Wallet",
                "purpose": "AI Agent A payments and triggers",
                "address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
                "private_key": self._encrypt_sensitive_data("mock_private_key_agent_a_" + secrets.token_hex(32)),
                "mnemonic": self._encrypt_sensitive_data("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art"),
                "balance_ada": 100.0,
                "created_at": datetime.now().isoformat(),
                "network": "preprod"
            },
            "agent_b_wallet": {
                "name": "Agent B Primary Wallet", 
                "purpose": "AI Agent B receipts and confirmations",
                "address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
                "private_key": self._encrypt_sensitive_data("mock_private_key_agent_b_" + secrets.token_hex(32)),
                "mnemonic": self._encrypt_sensitive_data("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"),
                "balance_ada": 50.0,
                "created_at": datetime.now().isoformat(),
                "network": "preprod"
            },
            "arduino_a_wallet": {
                "name": "Arduino A Trigger Wallet",
                "purpose": "Arduino A hardware trigger payments",
                "address": "addr_test1qr8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
                "private_key": self._encrypt_sensitive_data("mock_private_key_arduino_a_" + secrets.token_hex(32)),
                "mnemonic": self._encrypt_sensitive_data("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon absorb"),
                "balance_ada": 25.0,
                "created_at": datetime.now().isoformat(),
                "network": "preprod"
            },
            "arduino_b_wallet": {
                "name": "Arduino B Response Wallet",
                "purpose": "Arduino B hardware response confirmations",
                "address": "addr_test1qz9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
                "private_key": self._encrypt_sensitive_data("mock_private_key_arduino_b_" + secrets.token_hex(32)),
                "mnemonic": self._encrypt_sensitive_data("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon absent"),
                "balance_ada": 25.0,
                "created_at": datetime.now().isoformat(),
                "network": "preprod"
            },
            "treasury_wallet": {
                "name": "Treasury Funding Wallet",
                "purpose": "Main funding source for test operations",
                "address": "addr_test1qp8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
                "private_key": self._encrypt_sensitive_data("mock_private_key_treasury_" + secrets.token_hex(32)),
                "mnemonic": self._encrypt_sensitive_data("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon access"),
                "balance_ada": 500.0,
                "created_at": datetime.now().isoformat(),
                "network": "preprod"
            }
        }
        
        return wallets
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like private keys and mnemonics"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def save_wallets(self, wallets: Dict[str, Dict]):
        """Save wallets to encrypted file"""
        os.makedirs(os.path.dirname(self.wallet_file), exist_ok=True)
        
        with open(self.wallet_file, 'w') as f:
            json.dump(wallets, f, indent=2)
        
        print(f"✅ Test wallets saved to {self.wallet_file}")
        print("⚠️  Private keys are encrypted and stored securely")
    
    def load_wallets(self) -> Dict[str, Dict]:
        """Load wallets from file"""
        if not os.path.exists(self.wallet_file):
            raise FileNotFoundError(f"Wallet file {self.wallet_file} not found")
        
        with open(self.wallet_file, 'r') as f:
            return json.load(f)
    
    def get_wallet_addresses(self) -> Dict[str, str]:
        """Get public addresses for sharing with team"""
        wallets = self.load_wallets()
        addresses = {}
        
        for wallet_id, wallet_data in wallets.items():
            addresses[wallet_id] = {
                "name": wallet_data["name"],
                "address": wallet_data["address"],
                "purpose": wallet_data["purpose"],
                "balance_ada": wallet_data["balance_ada"]
            }
        
        return addresses
    
    def get_private_key(self, wallet_id: str) -> str:
        """Get decrypted private key for a wallet (use carefully)"""
        wallets = self.load_wallets()
        
        if wallet_id not in wallets:
            raise ValueError(f"Wallet {wallet_id} not found")
        
        encrypted_key = wallets[wallet_id]["private_key"]
        return self._decrypt_sensitive_data(encrypted_key)
    
    def create_funding_transactions(self) -> List[Dict]:
        """
        Create funding transaction instructions for preprod testnet
        Returns list of transactions to execute
        """
        wallets = self.load_wallets()
        treasury_address = wallets["treasury_wallet"]["address"]
        
        funding_transactions = []
        
        for wallet_id, wallet_data in wallets.items():
            if wallet_id == "treasury_wallet":
                continue  # Skip treasury itself
            
            funding_transactions.append({
                "from_address": treasury_address,
                "to_address": wallet_data["address"],
                "amount_ada": wallet_data["balance_ada"],
                "amount_lovelace": int(wallet_data["balance_ada"] * 1_000_000),
                "wallet_name": wallet_data["name"],
                "purpose": f"Initial funding for {wallet_data['purpose']}"
            })
        
        return funding_transactions
    
    def create_team_sharing_document(self) -> str:
        """Create a document with wallet info for team sharing"""
        addresses = self.get_wallet_addresses()
        
        doc = """# Test Wallet Addresses for Arduino-to-Cardano Project

## 🔐 Security Notice
- These are **PREPROD TESTNET** addresses only
- Never use real ADA or mainnet addresses
- Private keys are encrypted and stored separately

## 📍 Wallet Addresses

"""
        
        for wallet_id, info in addresses.items():
            doc += f"""### {info['name']} (`{wallet_id}`)
- **Address**: `{info['address']}`
- **Purpose**: {info['purpose']}
- **Balance**: {info['balance_ada']} ADA
- **Network**: Cardano Preprod Testnet

"""
        
        doc += """## 🔧 Usage Examples

### For Imad (AI Agent A):
```python
# Agent A payment wallet
AGENT_A_ADDRESS = "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

# Send payment from Agent A
payment_request = {
    "from_address": AGENT_A_ADDRESS,
    "to_address": AGENT_B_ADDRESS,
    "amount": 1000000,  # 1 ADA in lovelace
    "metadata": {"agent": "Agent_A", "trigger": "ai_decision"}
}
```

### For Ishita (Arduino Integration):
```python
# Arduino A trigger wallet
ARDUINO_A_ADDRESS = "addr_test1qr8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"
ARDUINO_B_ADDRESS = "addr_test1qz9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

# Arduino payment flow
def arduino_payment_trigger():
    return {
        "from_address": ARDUINO_A_ADDRESS,
        "to_address": ARDUINO_B_ADDRESS,
        "amount": 500000,  # 0.5 ADA
        "metadata": {"trigger": "arduino_hardware"}
    }
```

## 🚀 Quick Test Commands

```bash
# Test wallet balance
curl "http://localhost:8000/wallet/addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z/balance"

# Test payment between wallets
curl -X POST "http://localhost:8000/send_payment" \\
  -H "Content-Type: application/json" \\
  -d '{
    "from_address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "to_address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "amount": 1000000
  }'
```

---
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Network**: Cardano Preprod Testnet  
**Contact**: Blockchain Team Lead
"""
        
        return doc

def setup_test_wallets():
    """Main function to set up test wallets"""
    manager = TestWalletManager()
    
    print("🔐 Generating test wallets for Arduino-to-Cardano project...")
    
    # Generate wallets
    wallets = manager.generate_test_wallets()
    
    # Save wallets
    manager.save_wallets(wallets)
    
    # Create team sharing document
    sharing_doc = manager.create_team_sharing_document()
    
    # Save sharing document
    with open("docs/test_wallets_team_share.md", "w") as f:
        f.write(sharing_doc)
    
    print("✅ Team sharing document created: docs/test_wallets_team_share.md")
    
    # Display funding instructions
    funding_txs = manager.create_funding_transactions()
    
    print("\n💰 Funding Instructions:")
    print("1. Get preprod ADA from Cardano testnet faucet")
    print("2. Send ADA to treasury wallet:")
    print(f"   {wallets['treasury_wallet']['address']}")
    print("3. Execute funding transactions:")
    
    for tx in funding_txs:
        print(f"   • {tx['amount_ada']} ADA → {tx['wallet_name']}")
    
    print("\n🔗 Useful Links:")
    print("• Cardano Testnet Faucet: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/")
    print("• Cardano Explorer (Preprod): https://preprod.cardanoscan.io/")
    print("• Blockfrost Console: https://blockfrost.io/")
    
    return wallets

if __name__ == "__main__":
    setup_test_wallets()