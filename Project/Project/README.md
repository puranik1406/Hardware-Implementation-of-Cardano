# Router and Serial Bridge - Arduino-to-Cardano AI Agents

This component acts as the "traffic controller" for the Arduino-to-Cardano AI Agents system, ensuring smooth message flow between Arduino A, Agent A, Agent B, and the blockchain service.

## 🏗️ Architecture

```
Arduino A (Wokwi) → Serial Bridge → Router API → Agent B → Blockchain Service
                                    ↓
                              Mock Agent B (for testing)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Arduino A connected via USB (or simulation mode)
- Router API dependencies installed

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the complete system
python start_router.py --simulate

# Or start with real Arduino
python start_router.py --port COM3  # Windows
python start_router.py --port /dev/ttyUSB0  # Linux/Mac
```

### Individual Components
```bash
# Start only Router API
python start_router.py --router-only

# Start only Serial Bridge (simulation)
python serial_bridge.py --simulate

# Start Serial Bridge with Arduino
python serial_bridge.py --port COM3
```

## 📡 API Endpoints

### Router API (http://localhost:5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/send_offer` | POST | Receive payment offers from Agent A |
| `/status/{offer_id}` | GET | Get offer status and details |
| `/mock_agent_b` | POST | Mock Agent B responses for testing |
| `/offers` | GET | List all offers (debugging) |

### Example API Usage

#### Send an Offer
```bash
curl -X POST http://localhost:5000/send_offer \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "agent_a",
    "to_agent": "agent_b", 
    "amount": 25.0,
    "currency": "ADA",
    "description": "Coffee payment",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

#### Check Offer Status
```bash
curl http://localhost:5000/status/{offer_id}
```

## 🔌 Serial Bridge

The Serial Bridge connects Arduino A to the Router API:

### Arduino A Integration
- Listens for button presses on Arduino A
- Converts button signals to payment offers
- Supports multiple button types (1, 2, 3, emergency)

### Button Mapping
| Button | Amount | Description |
|--------|--------|-------------|
| Button 1 | 10 ADA | Coffee payment |
| Button 2 | 25 ADA | Lunch payment |
| Button 3 | 50 ADA | Dinner payment |
| Emergency | 100 ADA | Emergency payment |

### Arduino Code Example
```cpp
// Arduino A code for Wokwi simulation
void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);  // Button 1
  pinMode(3, INPUT_PULLUP);  // Button 2
  pinMode(4, INPUT_PULLUP);  // Button 3
  pinMode(5, INPUT_PULLUP);  // Emergency button
}

void loop() {
  if (digitalRead(2) == LOW) {
    Serial.println("button1");
    delay(200);
  }
  if (digitalRead(3) == LOW) {
    Serial.println("button2");
    delay(200);
  }
  if (digitalRead(4) == LOW) {
    Serial.println("button3");
    delay(200);
  }
  if (digitalRead(5) == LOW) {
    Serial.println("emergency");
    delay(200);
  }
}
```

## 📋 JSON Schemas

### Offer Schema (`schemas/offer.json`)
```json
{
  "offer_id": "string",
  "from_agent": "agent_a|agent_b",
  "to_agent": "agent_a|agent_b",
  "amount": 25.0,
  "currency": "ADA|USD|EUR|BTC",
  "timestamp": "2024-01-15T10:30:00Z",
  "description": "Payment description",
  "metadata": {
    "arduino_trigger": true,
    "button_type": "button_1",
    "priority": "medium"
  }
}
```

### Response Schema (`schemas/response.json`)
```json
{
  "response_id": "string",
  "offer_id": "string",
  "from_agent": "agent_a|agent_b",
  "status": "accepted|rejected|pending|expired",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Response message",
  "transaction_details": {
    "tx_hash": "abc123...",
    "block_height": 12345,
    "confirmation_time": "2024-01-15T10:35:00Z"
  }
}
```

## 🧪 Testing

### Run Integration Tests
```bash
# Make sure Router API is running first
python start_router.py --router-only

# In another terminal, run tests
python test_integration.py
```

### Manual Testing
1. Start the system: `python start_router.py --simulate`
2. Check health: `curl http://localhost:5000/health`
3. Send test offer using the API examples above
4. Monitor logs for message flow

## 📊 Logging

All components log to both console and files:
- `router.log` - Router API logs
- `serial_bridge.log` - Serial Bridge logs

Log levels: INFO, WARNING, ERROR

## 🔧 Configuration

### Environment Variables
- `ROUTER_PORT` - Router API port (default: 5000)
- `SERIAL_PORT` - Arduino serial port (auto-detect if not set)
- `SERIAL_BAUDRATE` - Serial baudrate (default: 9600)

### Command Line Options
```bash
# Serial Bridge options
python serial_bridge.py --help

# Router options  
python router.py --help

# Startup script options
python start_router.py --help
```

## 🤝 Team Collaboration

### For Imad (Agent A)
- Use `/send_offer` endpoint to send payment offers
- Ensure offer JSON matches the schema
- Test with mock Agent B responses

### For Ishita (Agent B)
- Use `/mock_agent_b` endpoint for testing
- Response JSON must match response schema
- Check `/status/{offer_id}` for offer details

### For Dhanush (Blockchain)
- Router will call your blockchain service when offers are accepted
- Transaction hashes will be stored and logged
- Arduino B will be notified of completed transactions

### For Ishita (Frontend)
- Use `/offers` endpoint to display all offers
- Use `/status/{offer_id}` for individual offer details
- Monitor `/health` for system status

## 🐛 Troubleshooting

### Common Issues

1. **Serial port not found**
   - Check Arduino connection
   - Use `--simulate` mode for testing
   - Verify port permissions (Linux/Mac)

2. **Router API not responding**
   - Check if port 5000 is available
   - Verify all dependencies are installed
   - Check router.log for errors

3. **Arduino not detected**
   - Install Arduino drivers
   - Check USB cable connection
   - Try different USB ports

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=.
python router.py  # Will run with debug=True
```

## 📁 Project Structure

```
├── router.py              # Main Router API
├── serial_bridge.py       # Arduino A Serial Bridge
├── start_router.py        # Startup script
├── test_integration.py    # Integration tests
├── requirements.txt       # Python dependencies
├── schemas/
│   ├── offer.json        # Offer JSON schema
│   └── response.json     # Response JSON schema
├── TASKS.md              # Detailed task breakdown
└── README.md             # This file
```

## 🎯 Success Criteria

- [x] Router receives offers from Agent A via REST API
- [x] Serial Bridge detects Arduino A button presses
- [x] Messages flow correctly to mock Agent B
- [x] Transaction hashes are properly tracked and logged
- [x] Team members can test against mock endpoints
- [x] All message flows are logged for debugging
- [x] System handles errors gracefully

## 🚀 Next Steps

1. **Integration with Real Agents**: Replace mock Agent B with actual Agent B implementation
2. **Blockchain Integration**: Connect to Dhanush's blockchain service
3. **Arduino B Integration**: Add real Arduino B notification system
4. **Frontend Integration**: Connect to Ishita's monitoring dashboard
5. **Production Deployment**: Add Docker containers and production configuration
