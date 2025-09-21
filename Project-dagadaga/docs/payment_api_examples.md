# Payment Service API Documentation

## 🚀 Quick Start

The Payment Service provides blockchain payment functionality for the Arduino-to-Cardano AI Agents project. It runs in two modes:

- **Mock Mode**: For immediate development and testing (default)
- **Real Mode**: Actual Cardano blockchain transactions

## 📍 Endpoints

### Base URL
- **Mock Mode**: `http://localhost:8000`
- **Real Mode**: `http://localhost:8001`

## 🔧 Installation & Setup

```bash
# Navigate to blockchain directory
cd blockchain

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Start mock service (for immediate team integration)
python src/mock_payment_service.py
```

## 📝 API Examples

### 1. Health Check

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "Payment Service",
  "mode": "mock",
  "status": "running",
  "version": "1.0.0-mock",
  "endpoints": {
    "send_payment": "POST /send_payment",
    "tx_status": "GET /tx_status/{job_id}",
    "list_jobs": "GET /jobs"
  }
}
```

### 2. Send Payment

**Request:**
```bash
curl -X POST "http://localhost:8000/send_payment" \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "to_address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "amount": 1000000,
    "metadata": {
      "agent": "Agent_A",
      "trigger": "arduino_signal"
    }
  }'
```

**Response:**
```json
{
  "job_id": "job_a1b2c3d4e5f6g7h8",
  "tx_hash": "tx_9f8e7d6c5b4a3928374656473829102847365738291028473657382910284736573829",
  "status": "pending",
  "estimated_confirmation_time": 30
}
```

### 3. Check Transaction Status

**Request:**
```bash
curl "http://localhost:8000/tx_status/job_a1b2c3d4e5f6g7h8"
```

**Response (Pending):**
```json
{
  "job_id": "job_a1b2c3d4e5f6g7h8",
  "tx_hash": "tx_9f8e7d6c5b4a3928374656473829102847365738291028473657382910284736573829",
  "status": "pending",
  "confirmations": 0,
  "created_at": "2025-09-21T10:30:00Z",
  "confirmed_at": null,
  "block_height": null,
  "fee": null
}
```

**Response (Confirmed):**
```json
{
  "job_id": "job_a1b2c3d4e5f6g7h8", 
  "tx_hash": "tx_9f8e7d6c5b4a3928374656473829102847365738291028473657382910284736573829",
  "status": "confirmed",
  "confirmations": 5,
  "created_at": "2025-09-21T10:30:00Z",
  "confirmed_at": "2025-09-21T10:30:30Z",
  "block_height": 8500123,
  "fee": 170000
}
```

### 4. Get Wallet Balance

**Request:**
```bash
curl "http://localhost:8000/wallet/addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z/balance"
```

**Response:**
```json
{
  "address": "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
  "balance_lovelace": 150000000,
  "balance_ada": 150.0,
  "utxos_count": 3
}
```

## 🔄 Integration Patterns

### For AI Agents (Imad - Agent A)

```python
import requests
import time

class PaymentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def send_payment(self, from_addr, to_addr, amount_ada, metadata=None):
        """Send payment and return job_id for tracking"""
        response = requests.post(f"{self.base_url}/send_payment", json={
            "from_address": from_addr,
            "to_address": to_addr, 
            "amount": int(amount_ada * 1_000_000),  # Convert ADA to lovelace
            "metadata": metadata or {}
        })
        return response.json()
    
    def wait_for_confirmation(self, job_id, timeout=60):
        """Poll for transaction confirmation"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_tx_status(job_id)
            if status["status"] == "confirmed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Transaction failed: {status}")
            time.sleep(5)
        raise TimeoutError("Transaction confirmation timeout")
    
    def get_tx_status(self, job_id):
        """Get current transaction status"""
        response = requests.get(f"{self.base_url}/tx_status/{job_id}")
        return response.json()

# Usage example
client = PaymentClient()
result = client.send_payment(
    from_addr="addr_test1qq...", 
    to_addr="addr_test1vr...",
    amount_ada=1.5,
    metadata={"agent": "Agent_A", "decision": "autonomous_payment"}
)
print(f"Payment initiated: {result['job_id']}")

# Wait for confirmation
confirmed = client.wait_for_confirmation(result['job_id'])
print(f"Payment confirmed: {confirmed['tx_hash']}")
```

### For Arduino Integration (Ishita)

```python
# Arduino trigger handler
def on_arduino_payment_signal(from_addr, to_addr, amount):
    """Called when Arduino sends payment signal"""
    payment_data = {
        "from_address": from_addr,
        "to_address": to_addr,
        "amount": amount,
        "metadata": {
            "trigger": "arduino_hardware",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    response = requests.post("http://localhost:8000/send_payment", json=payment_data)
    job_data = response.json()
    
    # Store job_id for status checking
    return job_data["job_id"]

def check_payment_for_arduino_response(job_id):
    """Check if payment is confirmed to trigger Arduino B"""
    response = requests.get(f"http://localhost:8000/tx_status/{job_id}")
    status = response.json()
    
    if status["status"] == "confirmed":
        # Trigger Arduino B with transaction details
        return {
            "confirmed": True,
            "tx_hash": status["tx_hash"],
            "block_height": status["block_height"]
        }
    return {"confirmed": False}
```

### For Frontend Display

```javascript
// React/Vue component example
async function PaymentMonitor({ jobId }) {
  const [status, setStatus] = useState(null);
  
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/tx_status/${jobId}`);
        const data = await response.json();
        setStatus(data);
        
        // Continue polling if still pending
        if (data.status === 'pending') {
          setTimeout(checkStatus, 5000);
        }
      } catch (error) {
        console.error('Error checking payment status:', error);
      }
    };
    
    checkStatus();
  }, [jobId]);
  
  return (
    <div className="payment-status">
      <h3>Payment Status</h3>
      <p>Job ID: {jobId}</p>
      <p>Status: <span className={status?.status}>{status?.status}</span></p>
      {status?.tx_hash && <p>TX Hash: {status.tx_hash}</p>}
      {status?.confirmations && <p>Confirmations: {status.confirmations}</p>}
    </div>
  );
}
```

## 🔀 Mock vs Real Mode Differences

| Feature | Mock Mode | Real Mode |
|---------|-----------|-----------|
| **Transaction Speed** | 30 seconds (configurable) | 20-60 seconds (blockchain dependent) |
| **TX Hash Format** | `tx_uuid...` | Real Cardano hash |
| **Fees** | Mock fee (~0.17 ADA) | Actual blockchain fees |
| **Address Validation** | Basic format check | Full Cardano validation |
| **Balance Checks** | Simulated balances | Real wallet queries |
| **Error Handling** | Simulated failures | Real blockchain errors |

## 📋 Test Wallet Addresses (For Development)

```bash
# Agent A Test Wallet
FROM_ADDRESS="addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

# Agent B Test Wallet  
TO_ADDRESS="addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z"

# Test payment command
curl -X POST "http://localhost:8000/send_payment" \
  -H "Content-Type: application/json" \
  -d "{
    \"from_address\": \"$FROM_ADDRESS\",
    \"to_address\": \"$TO_ADDRESS\", 
    \"amount\": 1000000
  }"
```

## 🚨 Error Handling

Common error scenarios and responses:

### Invalid Address Format
```json
{
  "detail": "Invalid from_address format",
  "status_code": 400
}
```

### Job Not Found
```json
{
  "detail": "Job job_invalid123 not found",
  "status_code": 404
}
```

### Insufficient Balance (Real Mode)
```json
{
  "detail": "Insufficient funds in source wallet",
  "status_code": 400
}
```

## 🔒 Security Notes

- **Mock Mode**: Safe for development, no real funds at risk
- **Real Mode**: Uses actual testnet ADA, handle private keys securely
- **API Keys**: Store Blockfrost keys in `.env` file, never commit to git
- **Wallet Security**: Encrypt private keys, use test wallets only

## 📞 Team Communication

When integrating with the Payment Service:

1. **Start with Mock Mode** - Test your integration logic first
2. **Share Job IDs** - Use job_id for cross-team debugging
3. **Check Status Regularly** - Poll `/tx_status/{job_id}` every 5-10 seconds
4. **Handle Timeouts** - Implement proper error handling for failed transactions
5. **Log Transaction Hashes** - Keep tx_hash for blockchain verification

## 🔄 Next Steps

1. ✅ Mock service running for immediate integration
2. 🟡 Real blockchain implementation (Dhanush working on it)
3. 🟡 Test wallet funding and distribution
4. 🟡 Production-ready error handling and monitoring

---

**Last Updated**: September 21, 2025  
**Contact**: Blockchain Team Lead  
**Issues**: Create GitHub issues for bugs or feature requests