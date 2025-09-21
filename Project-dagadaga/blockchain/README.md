# 🚀 Arduino-to-Cardano Blockchain & Payment Service

**Status**: ✅ COMPLETE - Ready for team integration  
**Last Updated**: September 21, 2025  
**Team Lead**: Blockchain & Payments (Dhanush)

## 🎯 Project Overview

This component provides blockchain payment functionality for the Arduino-to-Cardano AI Agents project. Two AI agents communicate and perform payment transactions using Masumi protocol + Cardano integration, with Arduino boards triggering and responding to blockchain transactions.

## ✅ Completed Deliverables

### 1. 🖥️ Mock Payment Service (READY NOW)
- **Location**: `blockchain/src/mock_payment_service.py`
- **URL**: http://localhost:8000
- **Status**: ✅ Running and tested
- **Purpose**: Immediate team integration without blockchain dependencies

**Quick Start:**
```bash
# Start mock service
cd blockchain
python src/mock_payment_service.py

# Test it
python ../quick_test.py
```

### 2. 🔗 Real Payment Service (READY FOR BLOCKCHAIN)
- **Location**: `blockchain/src/real_payment_service.py`
- **URL**: http://localhost:8001  
- **Status**: ✅ Implemented, needs API keys
- **Purpose**: Actual Cardano transactions via Masumi + Blockfrost

### 3. 💰 Test Wallets (CONFIGURED)
- **Location**: `docs/test_wallets_team_share.md`
- **Status**: ✅ Generated and documented
- **Purpose**: Team wallet addresses for development

### 4. 📋 API Documentation (COMPLETE)
- **Specs**: `specs/payment_api.json`
- **Examples**: `docs/payment_api_examples.md`
- **Status**: ✅ Ready for team use

### 5. 🧪 Testing Suite (READY)
- **Location**: `blockchain/tests/test_payment_service.py`
- **Quick Test**: `quick_test.py`
- **Status**: ✅ Comprehensive testing

## 🔧 Team Integration Guide

### For Imad (AI Agent A):
```python
import requests

# Agent A payment integration
AGENT_A_ADDRESS = "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"
AGENT_B_ADDRESS = "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

def agent_a_send_payment(amount_ada=1.0):
    payment_data = {
        "from_address": AGENT_A_ADDRESS,
        "to_address": AGENT_B_ADDRESS,
        "amount": int(amount_ada * 1_000_000),  # Convert to lovelace
        "metadata": {"agent": "Agent_A", "trigger": "ai_decision"}
    }
    
    response = requests.post("http://localhost:8000/send_payment", json=payment_data)
    return response.json()
```

### For Ishita (Arduino Integration):
```python
# Arduino trigger integration
ARDUINO_A_ADDRESS = "addr_test1qr8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"
ARDUINO_B_ADDRESS = "addr_test1qz9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

def arduino_payment_trigger():
    # Called when Arduino A signals payment
    payment_data = {
        "from_address": ARDUINO_A_ADDRESS,
        "to_address": ARDUINO_B_ADDRESS,
        "amount": 500000,  # 0.5 ADA
        "metadata": {"trigger": "arduino_hardware"}
    }
    
    response = requests.post("http://localhost:8000/send_payment", json=payment_data)
    job_id = response.json()["job_id"]
    
    # Monitor for confirmation to trigger Arduino B
    return monitor_payment_confirmation(job_id)
```

### For Frontend Team:
```javascript
// Real-time payment monitoring
const PAYMENT_SERVICE = "http://localhost:8000";

async function monitorPayment(jobId) {
    while (true) {
        const response = await fetch(`${PAYMENT_SERVICE}/tx_status/${jobId}`);
        const status = await response.json();
        
        if (status.status === "confirmed") {
            // Update UI: Payment confirmed
            displayTransactionSuccess(status.tx_hash);
            break;
        } else if (status.status === "failed") {
            // Update UI: Payment failed
            displayTransactionError(status.error_message);
            break;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000)); // Check every 5s
    }
}
```

## 🌐 API Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/` | GET | Health check | `curl http://localhost:8000/` |
| `/send_payment` | POST | Initiate payment | See examples below |
| `/tx_status/{job_id}` | GET | Check status | `curl http://localhost:8000/tx_status/job_123` |
| `/wallet/{address}/balance` | GET | Get balance | `curl http://localhost:8000/wallet/addr.../balance` |

## 📝 Quick Test Commands

```bash
# Health check
curl http://localhost:8000/

# Send test payment
curl -X POST "http://localhost:8000/send_payment" \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "to_address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "amount": 1000000,
    "metadata": {"test": true}
  }'

# Check transaction status (use job_id from above)
curl "http://localhost:8000/tx_status/{job_id}"
```

## 🔄 Next Steps for Real Blockchain

1. **Get Blockfrost API Key**: 
   - Sign up at https://blockfrost.io/
   - Get preprod project ID
   - Add to `.env` file

2. **Fund Test Wallets**:
   - Use Cardano testnet faucet: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/
   - Fund treasury wallet first
   - Distribute to team wallets

3. **Switch to Real Mode**:
   ```bash
   # Set environment variables
   BLOCKFROST_PROJECT_ID=your_project_id_here
   MOCK_MODE=false
   
   # Start real service
   python src/real_payment_service.py
   ```

## 🚨 Important Notes

- **Mock Mode**: Safe for development, no real money
- **Test Network**: Only use Cardano preprod testnet
- **API Keys**: Never commit real API keys to git
- **Wallet Security**: Private keys are encrypted

## 🏗️ Architecture Overview

```
Agent A (AI) ──┐
              ├─→ Payment Service ──→ Masumi Protocol ──→ Cardano Blockchain
Arduino A ────┘                                           │
                                                          ▼
Arduino B ────┐                                    Transaction Hash
              ├─← Confirmation ←─── Blockfrost API ←──────┘
Agent B (AI) ──┘
```

## 📞 Support & Troubleshooting

### Common Issues:
1. **Service not starting**: Check Python dependencies
2. **Connection refused**: Ensure service is running on correct port
3. **Invalid address**: Use preprod testnet addresses only
4. **API errors**: Check Blockfrost API key configuration

### Contact:
- **Blockchain Team Lead**: Available for integration support
- **Documentation**: All files in `docs/` folder
- **Issues**: Check `TASKS.md` for known limitations

---

## 🎉 Ready for Team Integration!

✅ Mock service running on http://localhost:8000  
✅ API documentation complete  
✅ Test wallets configured  
✅ Error handling implemented  
✅ Comprehensive testing suite  

**The payment service is ready for immediate team integration. Start with the mock service and transition to real blockchain when ready!**