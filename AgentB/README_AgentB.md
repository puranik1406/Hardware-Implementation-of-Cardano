# Agent B - Seller Logic & Arduino B - Transaction Display

## Overview
Agent B is responsible for listening for offers, deciding whether to accept them, and displaying transaction hashes when payments are confirmed. Arduino B provides a physical display for confirmed transactions.

## Components

### 1. Agent B (Python Flask API)
- **File**: `agent_b.py`
- **Port**: 5001
- **Endpoints**:
  - `GET /health` - Health check
  - `POST /respond` - Receive and respond to offers
  - `POST /confirm_tx` - Handle transaction confirmations
  - `GET /status` - Get current status

### 2. Arduino B (Transaction Display)
- **File**: `arduino_b.ino`
- **Platform**: Arduino (Wokwi simulation)
- **Display**: LCD + Serial Monitor
- **Function**: Shows confirmed transaction hashes

## Setup Instructions

### Prerequisites
- Python 3.7+
- Arduino IDE or Wokwi
- Flask and requests libraries

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Agent B
```bash
python agent_b.py
```
Agent B will start on `http://localhost:5001`

### 3. Upload Arduino B Sketch
1. Open `arduino_b.ino` in Arduino IDE or Wokwi
2. Upload to Arduino board
3. Open Serial Monitor (9600 baud)

## API Usage

### Health Check
```bash
curl http://localhost:5001/health
```

### Respond to Offer
```bash
curl -X POST http://localhost:5001/respond \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.0,
    "product": "Premium Widget",
    "buyer_address": "addr1q9test...",
    "buyer_id": "buyer_001"
  }'
```

### Confirm Transaction
```bash
curl -X POST http://localhost:5001/confirm_tx \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "mock_tx_1234567890_150.50",
    "status": "confirmed"
  }'
```

## Decision Logic

Agent B uses rule-based decision logic:
- **Accept**: If offer amount ≥ cost threshold (default: 100.0)
- **Reject**: If offer amount < cost threshold
- **Counter**: Not implemented (future enhancement)

## Testing

### Run Test Suite
```bash
python test_agent_b.py
```

### Manual Testing
1. Start Agent B: `python agent_b.py`
2. Run test script: `python test_agent_b.py`
3. Check Arduino B display for transaction confirmations

## Configuration

### Agent B Settings
- **Cost Threshold**: `self.cost_threshold = 100.0`
- **Blockchain Service URL**: `self.blockchain_service_url = "http://localhost:5002"`
- **Arduino Serial Port**: `self.arduino_serial_port = "COM3"`

### Arduino B Settings
- **Serial Baud Rate**: 9600
- **LCD Size**: 16x2
- **Display Format**: "✅ CONFIRMED: [tx_hash]"

## Workflow

1. **Offer Received**: Router sends offer to Agent B `/respond`
2. **Decision Made**: Agent B evaluates offer against cost threshold
3. **Payment Initiated**: If accepted, payment request sent to Blockchain Service
4. **Confirmation Polled**: Agent B polls for transaction confirmation
5. **Display Updated**: Confirmed transaction sent to Arduino B for display

## Mock Implementation

Currently uses mock data for testing:
- Mock transaction hashes: `mock_tx_{timestamp}_{amount}`
- Simulated payment confirmation after 3 polling attempts
- Arduino display simulation via console output

## Integration Points

### With Router
- Receives offers via `/respond` endpoint
- Returns decision and transaction hash

### With Blockchain Service
- Sends payment requests to `/send_payment`
- Polls transaction status via `/tx_status`
- Receives confirmations via `/confirm_tx`

### With Arduino B
- Sends confirmed transaction hashes via serial communication
- Arduino displays confirmation on LCD and Serial Monitor

## Troubleshooting

### Common Issues
1. **Agent B not starting**: Check port 5001 is available
2. **Arduino not responding**: Verify serial port and baud rate
3. **Offers being rejected**: Check cost threshold setting
4. **No transaction display**: Verify Arduino serial connection

### Logs
- Agent B logs to console with timestamps
- Arduino B logs to Serial Monitor
- Test script provides detailed output

## Future Enhancements

1. **Real Blockchain Integration**: Replace mock with actual Cardano/Masumi
2. **Counter-Offer Logic**: Implement negotiation capabilities
3. **Database Storage**: Persist transaction history
4. **Web Dashboard**: Real-time status monitoring
5. **Multiple Arduino Support**: Support multiple display devices

## File Structure
```
AgentB/
├── agent_b.py              # Main Agent B Flask API
├── arduino_b.ino           # Arduino B sketch
├── test_agent_b.py         # Test suite
├── requirements.txt        # Python dependencies
├── TASKS.md               # Task breakdown
└── README_AgentB.md       # This file
```
