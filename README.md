# 🚀 Cardano-Arduino-AI Hackathon Project

**Hardware Implementation of Cardano - Arduino to Blockchain AI Agents**

A comprehensive system that bridges Arduino hardware devices with the Cardano blockchain through AI agents, enabling real-time transaction processing and intelligent decision making.

## 🎯 Project Overview

This hackathon submission demonstrates a complete end-to-end system that:

- **🔗 Connects Arduino devices** to the Cardano blockchain via AI agents
- **🤖 Uses AI-powered agents** for intelligent transaction routing and decision making
- **💰 Processes real transactions** on Cardano preprod testnet via Blockfrost API
- **⚡ Provides real-time monitoring** of blockchain operations and Arduino interactions
- **🌐 Offers REST APIs** for easy integration and testing

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Arduino A     │───▶│   Agent A        │───▶│     Router      │───▶│   Agent B        │
│   (Trigger)     │    │   (Buyer AI)     │    │ (Coordinator)   │    │   (Seller)       │
│                 │    │                  │    │                 │    │                  │
│ - Sensors       │    │ - AI Decisions   │    │ - Traffic Ctrl  │    │ - Accept/Reject  │
│ - Button        │    │ - Offer Creation │    │ - State Mgmt    │    │ - Payment Init   │
│ - LCD Display   │    │ - Evaluation     │    │ - Agent Coord   │    │ - TX Monitoring  │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘
                                │                        │                        │
                                │                        │                        │
                                ▼                        ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │   Web Interface  │    │ Payment Service │    │   Arduino B     │
                       │   (Dashboard)    │    │ (Blockchain)    │    │   (Display)     │
                       │                  │    │                 │    │                 │
                       │ - Status Monitor │    │ - Blockfrost   │    │ - TX Display    │
                       │ - Transaction    │    │ - Smart Contract│    │ - Status LEDs   │
                       │ - Agent Control  │    │ - Real Cardano  │    │ - Confirmation  │
                       └──────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Key Features

### 🔥 Core Hackathon Features
- **Real Cardano Integration**: Actual blockchain transactions on Cardano preprod testnet
- **AI Agent System**: Intelligent buyer/seller agents with decision-making capabilities
- **Hardware Integration**: Arduino devices triggering and displaying blockchain transactions
- **Smart Contracts**: Plutus smart contracts for secure payment processing
- **Complete Workflow**: End-to-end automation from sensor trigger to blockchain confirmation

### 🛠️ Technical Features
- **FastAPI + Flask**: High-performance APIs with async support
- **Blockfrost Integration**: Real Cardano blockchain connectivity
- **Serial Communication**: Arduino hardware interface
- **Mock & Real Modes**: Development and production blockchain modes
- **Comprehensive Logging**: Full system monitoring and debugging
- **Docker Ready**: Containerized deployment support

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and enter directory
git clone <your-repo>
cd cardano-arduino-ai-hackathon

# Run automated setup
python setup.py

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

### 2. Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env

# Update .env with your settings:
# - BLOCKFROST_PROJECT_ID=your_blockfrost_key_here
# - ARDUINO_A_PORT=COM3  (or /dev/ttyUSB0 on Linux)
# - ARDUINO_B_PORT=COM4  (or /dev/ttyUSB1 on Linux)
# - MOCK_MODE=false      (for real blockchain)
```

### 3. Setup Arduino Hardware

Upload the Arduino sketches to your devices:
- **Arduino A**: Upload `src/arduino/arduino_a.ino`
- **Arduino B**: Upload `src/arduino/arduino_b.ino`

**Required Hardware:**
- 2x Arduino Uno/Nano
- 2x 16x2 LCD displays
- LEDs, buttons, sensors (see Arduino code for pin assignments)
- USB cables for PC connection

### 4. Launch System

```bash
# Start all services
python main.py
```

The system will start all components and display access URLs:
- 🤖 Agent A (Buyer): http://localhost:8001
- 🛒 Agent B (Seller): http://localhost:8002  
- 🔗 Router: http://localhost:8003
- 💰 Payment Service: http://localhost:8000

## 💡 Usage Examples

### Test the Complete Workflow

1. **Trigger Arduino A**: Press button or trigger sensor
2. **Monitor Agent A**: Creates offer based on AI decision
3. **Router Coordination**: Routes offer to Agent B
4. **Agent B Evaluation**: Accepts/rejects based on price threshold
5. **Payment Processing**: Initiates Cardano transaction
6. **Arduino B Display**: Shows transaction confirmation

### API Testing

```bash
# Test payment service
curl http://localhost:8000/test_payment

# Trigger offer from Arduino simulation
curl -X POST http://localhost:8003/arduino_trigger \
  -H "Content-Type: application/json" \
  -d '{"amount": 150, "product": "Sensor Data"}'

# Check system status
curl http://localhost:8003/status

# View all offers
curl http://localhost:8003/offers

# Check Agent A health
curl http://localhost:8001/

# Check Agent B transactions
curl http://localhost:8002/transactions
```

## 🏗️ Project Structure

```
cardano-arduino-ai-hackathon/
├── 📁 src/
│   ├── 📁 agents/
│   │   ├── agent_a.py          # AI Buyer Agent (FastAPI)
│   │   ├── agent_b.py          # Seller Agent (Flask)
│   │   └── router.py           # Traffic Controller (Flask)
│   ├── 📁 blockchain/
│   │   └── payment_service.py  # Cardano Payment Service (FastAPI)
│   └── 📁 arduino/
│       ├── arduino_a.ino       # Trigger Arduino Code
│       └── arduino_b.ino       # Display Arduino Code
├── 📁 contracts/
│   └── ArduinoPaymentContract.hs  # Plutus Smart Contract
├── 📁 config/
├── 📁 tests/
├── 📁 docs/
├── 📁 scripts/
├── main.py                     # System Launcher
├── setup.py                    # Automated Setup
├── requirements.txt            # Python Dependencies
├── .env.example               # Environment Template
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLOCKFROST_PROJECT_ID` | Blockfrost API key for Cardano | Required for real blockchain |
| `CARDANO_NETWORK` | Cardano network (preprod/mainnet) | preprod |
| `MOCK_MODE` | Use mock payments vs real blockchain | true |
| `AGENT_A_PORT` | Agent A service port | 8001 |
| `AGENT_B_PORT` | Agent B service port | 8002 |
| `ROUTER_PORT` | Router service port | 8003 |
| `PAYMENT_SERVICE_PORT` | Payment service port | 8000 |
| `ARDUINO_A_PORT` | Arduino A serial port | COM3 |
| `ARDUINO_B_PORT` | Arduino B serial port | COM4 |
| `COST_THRESHOLD` | Agent B acceptance threshold (ADA) | 100.0 |

### Getting Blockfrost API Key

1. Visit [blockfrost.io](https://blockfrost.io)
2. Sign up for free account
3. Create new project for "Cardano Preprod"
4. Copy project ID to `BLOCKFROST_PROJECT_ID` in `.env`

## 🧪 Testing

### Automated Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_agents.py
python -m pytest tests/test_blockchain.py
python -m pytest tests/test_integration.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Manual Testing

```bash
# Test individual components
python src/agents/agent_a.py      # Start Agent A only
python src/agents/agent_b.py      # Start Agent B only
python src/blockchain/payment_service.py  # Start Payment Service only

# Test Arduino communication (requires hardware)
python scripts/test_arduino.py
```

## 📊 Monitoring & Debugging

### System Status Dashboard

Visit http://localhost:8003/status for real-time system monitoring:
- Service health checks
- Active offers and transactions
- Agent connectivity status
- Performance metrics

### Logs

- **Console Output**: Real-time logs from all services
- **File Logs**: Stored in `logs/` directory
- **Structured Logging**: JSON format for easy parsing

### Arduino Serial Monitor

Monitor Arduino devices through serial connection:
- Arduino A: Commands and offer triggers
- Arduino B: Transaction confirmations and status

## 🔐 Blockchain Integration

### Smart Contracts

The system includes Plutus smart contracts for:
- **Payment Validation**: Secure transaction processing
- **Multi-signature Support**: Both parties must confirm
- **Dispute Resolution**: Built-in arbitration mechanism
- **Arduino Authentication**: Device signature verification

### Real Cardano Transactions

When `MOCK_MODE=false`:
- Real ADA transactions on Cardano preprod testnet
- Blockfrost API for blockchain interaction
- Transaction confirmation monitoring
- Real-time balance checking

## 🎛️ Hardware Requirements

### Minimum Arduino Setup

**Arduino A (Trigger Device):**
- Arduino Uno/Nano
- 16x2 LCD display
- Push button
- Potentiometer (sensor simulation)
- Status LED
- Breadboard and jumper wires

**Arduino B (Display Device):**
- Arduino Uno/Nano  
- 16x2 LCD display
- 3x LEDs (Green/Red/Blue)
- Push button (acknowledgment)
- Breadboard and jumper wires

### Pin Configurations

See Arduino sketch files for detailed pin assignments:
- `src/arduino/arduino_a.ino` - Lines 8-12
- `src/arduino/arduino_b.ino` - Lines 8-15

## 🚀 Deployment

### Local Development

```bash
python main.py  # Starts all services locally
```

### Docker Deployment

```bash
# Build container
docker build -t cardano-arduino-ai .

# Run container
docker run -p 8000-8003:8000-8003 \
  -v /dev/ttyUSB0:/dev/ttyUSB0 \
  --device=/dev/ttyUSB0 \
  cardano-arduino-ai
```

### Production Deployment

1. **Update Environment**: Set production API keys and endpoints
2. **Hardware Setup**: Connect physical Arduino devices
3. **Network Configuration**: Configure firewall and networking
4. **Monitoring**: Set up log aggregation and alerting
5. **Backup**: Regular database and configuration backups

## 🤝 API Reference

### Agent A (Buyer) API

**Base URL**: `http://localhost:8001`

- `POST /trigger` - Trigger new offer
- `POST /arduino_trigger` - Arduino-triggered offer
- `POST /evaluate_response` - Evaluate Agent B response
- `GET /offers` - List all offers
- `GET /offers/{offer_id}` - Get specific offer

### Agent B (Seller) API

**Base URL**: `http://localhost:8002`

- `POST /respond` - Respond to offer
- `GET /transaction_status/{tx_hash}` - Check transaction status
- `GET /transactions` - List all transactions
- `POST /confirm_tx` - Manual transaction confirmation

### Router API

**Base URL**: `http://localhost:8003`

- `POST /receive_offer` - Receive offer from Agent A
- `POST /transaction_confirmed` - Transaction confirmation
- `POST /arduino_trigger` - Arduino trigger endpoint
- `GET /status` - System status
- `GET /offers` - All offers
- `GET /transactions` - All transactions

### Payment Service API

**Base URL**: `http://localhost:8000`

- `POST /send_payment` - Initiate payment
- `GET /job_status/{job_id}` - Check payment status
- `GET /jobs` - List all payment jobs
- `POST /test_payment` - Create test payment

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8000
   # Kill the process or change port in .env
   ```

2. **Arduino Not Connected**
   ```bash
   # Check available ports (Windows)
   mode
   # Check available ports (Linux)
   ls /dev/tty*
   ```

3. **Blockfrost API Errors**
   - Verify your API key in `.env`
   - Check network connection
   - Ensure sufficient API rate limits

4. **Dependencies Missing**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Debug Mode

Enable detailed debugging:
```bash
# Set in .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🏆 Hackathon Demonstration

### Demo Script

1. **Setup Phase** (2 minutes)
   - Show project structure
   - Explain system architecture
   - Start all services with `python main.py`

2. **Arduino Interaction** (3 minutes)
   - Connect Arduino devices
   - Trigger offer with sensor/button
   - Show Agent A creating intelligent offer

3. **AI Agent Workflow** (3 minutes)
   - Router coordinates between agents
   - Agent B evaluates offer using threshold logic
   - Real-time decision making demonstration

4. **Blockchain Integration** (4 minutes)
   - Payment service processes transaction
   - Real Cardano blockchain interaction
   - Transaction confirmation on Arduino B display

5. **Monitoring & APIs** (3 minutes)
   - System status dashboard
   - API testing with curl commands
   - Real-time logs and monitoring

### Key Talking Points

- **Innovation**: First Arduino-to-Cardano AI agent system
- **Real Blockchain**: Actual Cardano transactions, not just simulation
- **Complete Solution**: Hardware to blockchain end-to-end
- **AI Integration**: Intelligent decision making and routing
- **Production Ready**: Comprehensive logging, error handling, testing

## 📚 Additional Resources

### Documentation
- [Cardano Developer Portal](https://developers.cardano.org/)
- [Blockfrost API Docs](https://docs.blockfrost.io/)
- [Arduino Reference](https://www.arduino.cc/reference/en/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Learning Resources
- [Plutus Smart Contracts](https://plutus-pioneer-program.readthedocs.io/)
- [Cardano Architecture](https://docs.cardano.org/learn/)
- [Arduino Programming](https://www.arduino.cc/en/Tutorial/HomePage)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Cardano Foundation** - For the amazing blockchain infrastructure
- **Blockfrost** - For providing excellent API services
- **Arduino Community** - For the hardware platform and libraries
- **FastAPI & Flask Teams** - For the fantastic web frameworks

---

**🎉 Ready to revolutionize IoT payments with Cardano!**

For questions, issues, or demo requests, please open an issue or contact the development team.