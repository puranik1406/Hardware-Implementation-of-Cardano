# Test Wallet Addresses for Arduino-to-Cardano Project

## 🔐 Security Notice
- These are **PREPROD TESTNET** addresses only
- Never use real ADA or mainnet addresses
- Private keys are encrypted and stored separately

## 📍 Wallet Addresses

### Agent A Primary Wallet (`agent_a_wallet`)
- **Address**: `addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z`
- **Purpose**: AI Agent A payments and triggers
- **Balance**: 100.0 ADA
- **Network**: Cardano Preprod Testnet

### Agent B Primary Wallet (`agent_b_wallet`)
- **Address**: `addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z`
- **Purpose**: AI Agent B receipts and confirmations
- **Balance**: 50.0 ADA
- **Network**: Cardano Preprod Testnet

### Arduino A Trigger Wallet (`arduino_a_wallet`)
- **Address**: `addr_test1qr8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z`
- **Purpose**: Arduino A hardware trigger payments
- **Balance**: 25.0 ADA
- **Network**: Cardano Preprod Testnet

### Arduino B Response Wallet (`arduino_b_wallet`)
- **Address**: `addr_test1qz9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z`
- **Purpose**: Arduino B hardware response confirmations
- **Balance**: 25.0 ADA
- **Network**: Cardano Preprod Testnet

### Treasury Funding Wallet (`treasury_wallet`)
- **Address**: `addr_test1qp8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z`
- **Purpose**: Main funding source for test operations
- **Balance**: 500.0 ADA
- **Network**: Cardano Preprod Testnet

## 🔧 Usage Examples

### For Imad (AI Agent A):
```python
# Agent A payment wallet
AGENT_A_ADDRESS = "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"
AGENT_B_ADDRESS = "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

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

### For Frontend Team:
```javascript
// Wallet addresses for frontend display
const WALLET_ADDRESSES = {
  AGENT_A: "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
  AGENT_B: "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
  ARDUINO_A: "addr_test1qr8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
  ARDUINO_B: "addr_test1qz9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"
};

// Monitor wallet balances
async function getWalletBalance(address) {
  const response = await fetch(`http://localhost:8000/wallet/${address}/balance`);
  return response.json();
}
```

## 🚀 Quick Test Commands

```bash
# Test wallet balance
curl "http://localhost:8000/wallet/addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z/balance"

# Test payment between wallets
curl -X POST "http://localhost:8000/send_payment" \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "to_address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "amount": 1000000
  }'
```

## 💰 Funding Instructions

1. **Get preprod ADA from Cardano testnet faucet**
   - Visit: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/
   - Request ADA for the treasury wallet address

2. **Treasury Wallet**: `addr_test1qp8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z`

3. **Fund individual wallets from treasury**:
   - Agent A: 100 ADA
   - Agent B: 50 ADA  
   - Arduino A: 25 ADA
   - Arduino B: 25 ADA

## 🔗 Useful Links

- **Cardano Testnet Faucet**: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/
- **Cardano Explorer (Preprod)**: https://preprod.cardanoscan.io/
- **Blockfrost Console**: https://blockfrost.io/
- **Mock Payment Service**: http://localhost:8000/docs
- **Real Payment Service**: http://localhost:8001/docs

## 🔄 Integration Flow

1. **Agent A Decision** → Calls Payment Service
2. **Payment Service** → Creates transaction via Masumi + Cardano
3. **Transaction Confirmed** → Arduino B receives signal
4. **Agent B** → Processes confirmation and displays result

---
**Generated**: September 21, 2025  
**Network**: Cardano Preprod Testnet  
**Contact**: Blockchain Team Lead  
**Status**: Ready for team integration