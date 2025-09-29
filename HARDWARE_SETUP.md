# Arduino Masumi Network with Satoshi AI Agents - Complete Setup Guide

## 🚀 Overview

This project combines real Arduino hardware with Masumi Network blockchain integration and Satoshi AI agents via Model Context Protocol (MCP). You'll have:

1. **Real Hardware Integration**: Arduino Uno and ESP32 boards
2. **Blockchain Payments**: Real Cardano transactions via Masumi Network  
3. **AI Agents**: Autonomous Satoshi agents via MCP
4. **Web Interface**: React dashboard for monitoring and control

## 📋 Prerequisites

### Hardware Required
- **Arduino Uno** (or compatible board)
- **ESP32 Development Board** 
- **USB Cables** for both boards
- **Breadboard and LEDs** (optional, for visual feedback)
- **Buzzer** (optional, for ESP32 audio feedback)

### Software Required
- **Arduino IDE** 2.0+
- **Python** 3.10+
- **Node.js** 18+
- **Docker** (for Masumi services)
- **Git**

## 🔧 Step 1: Hardware Setup

### Arduino Uno Wiring
```
Arduino Uno Connections:
- Pin 2: Button (for manual payments)
- Pin 8: Status LED
- Pin 13: Built-in LED (status indicator)
```

### ESP32 Wiring  
```
ESP32 Connections:
- Pin 2: Green LED (success indicator)
- Pin 4: Red LED (error indicator) 
- Pin 5: Buzzer (audio feedback)
- Pin 18: Additional display pin
```

## 🔧 Step 2: Arduino Code Upload

### Upload Arduino Uno Code
1. Open Arduino IDE
2. Load `arduino-code/arduino_uno_sender.ino`
3. Install required libraries:
   - ArduinoJson
4. Select your Arduino Uno board and port
5. Upload the code

### Upload ESP32 Code
1. Install ESP32 board package in Arduino IDE
2. Load `arduino-code/esp32_receiver.ino`
3. Install required libraries:
   - ArduinoJson
   - WebSocketsServer
   - LiquidCrystal_I2C (optional)
4. **Update WiFi credentials** in the code:
   ```cpp
   const char* ssid = "YourWiFi";
   const char* password = "YourPassword";
   ```
5. Select ESP32 board and port
6. Upload the code

## 🔧 Step 3: Masumi Network Setup

### Start Masumi Services
```bash
# Navigate to project directory
cd arduino-masumi-simulator

# Start Masumi services (Registry & Payment)
cd masumi-services-dev-quickstart
docker-compose up -d

# Verify services are running
curl http://localhost:3000/health  # Registry Service
curl http://localhost:3001/health  # Payment Service
```

## 🔧 Step 4: Python Environment Setup

### Install Python Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Step 5: MCP Server Setup

### Start Satoshi AI Agent MCP Server
```bash
# In project directory
python mcp-server/satoshi_agent_server.py
```

The MCP server provides these tools:
- `detect_arduino_boards` - Find connected Arduino devices
- `create_satoshi_agent` - Create autonomous AI agents  
- `send_arduino_command` - Send commands to hardware
- `initiate_payment_from_arduino` - Full payment flow
- `get_agent_status` - Monitor agent activity
- `enable_autonomous_mode` - Toggle AI agent autonomy

## 🔧 Step 6: Web Interface Setup

### Start React Development Server
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Step 7: Hardware Bridge Setup

### Start Arduino Communication Bridge
```bash
# In project directory
python arduino_bridge.py
```

This will:
- Detect your Arduino Uno and ESP32
- Establish serial communication
- Enable real-time command sending
- Process payment flows between hardware and blockchain

## 🎮 Usage Scenarios

### Scenario 1: Manual Payment via Web Interface
1. Open http://localhost:5173
2. Navigate to "Real Arduino Hardware" panel
3. Click "Detect Boards" to connect your Arduino devices
4. Send payment command: `SEND_PAYMENT:2.5:esp32_receiver`
5. Watch transaction hash appear on ESP32 display

### Scenario 2: Physical Button Payment
1. Press the button connected to Arduino Uno Pin 2
2. Arduino automatically sends 1.5 ADA payment
3. Transaction processes through Masumi Network
4. ESP32 receives and displays transaction hash with LEDs/buzzer

### Scenario 3: Autonomous AI Agent
1. Create a Satoshi AI agent via web interface
2. Enable autonomous mode
3. Agent monitors blockchain and makes decisions
4. Triggers Arduino payments based on AI logic
5. Real transaction hashes sent to ESP32

### Scenario 4: MCP Integration with Claude
If you have Claude for Desktop:

1. Configure Claude MCP settings (`~/.config/claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "satoshi-agent": {
      "command": "python",
      "args": ["C:/path/to/your/project/mcp-server/satoshi_agent_server.py"]
    }
  }
}
```

2. Ask Claude:
   - "Detect my Arduino boards"
   - "Create a new Satoshi agent called Alpha"
   - "Send 2 ADA from Arduino to ESP32"
   - "Show me the status of all agents"

## 🔍 Troubleshooting

### Arduino Detection Issues
- Check USB connections
- Verify correct COM ports in Device Manager
- Install Arduino drivers if needed
- Try different USB cables

### ESP32 WiFi Issues  
- Verify WiFi credentials in code
- Check 2.4GHz network (ESP32 doesn't support 5GHz)
- Monitor serial output for connection status

### Masumi Service Issues
```bash
# Check service logs
docker-compose logs registry-service
docker-compose logs payment-service

# Restart services if needed  
docker-compose restart
```

### MCP Connection Issues
- Ensure Python dependencies installed correctly
- Check firewall blocking local connections
- Verify Claude Desktop configuration

## 🔒 Wallet Funding

Your wallets are already funded with testnet ADA:
- **Arduino A**: `addr_test1qrffhpxs9ky88sxfm9788mr8a4924e0uhl4fexvy9z5pt084p3q2uhgh9wvft4ejrjhx5yes2xpmy2cuufmzljdwtf7qvgt5rz`
- **Arduino B**: `addr_test1qqxdsjedg0fpurjt345lymmyxrs2r4u7etwchfwze7fwvfx76eyhp6agt96xprlux3tgph0zm5degavwkge2f9jmszqqg3p703`

For additional funding: https://docs.cardano.org/cardano-testnets/tools/faucet

## 📊 Monitoring & Verification

### Transaction Verification
- All transactions show explorer links: https://preprod.cardanoscan.io/
- ESP32 displays transaction hashes in real-time
- Web interface shows complete transaction history

### Serial Monitor
- Arduino IDE Serial Monitor (115200 baud)
- Python bridge shows real-time communication
- Web interface has live serial output display

## 🎯 Advanced Features

### Custom AI Agent Behaviors
Modify `mcp-server/satoshi_agent_server.py` to add:
- Market analysis logic
- Risk management
- Multi-signature transactions  
- Cross-chain bridges

### Extended Hardware Integration
- Add more sensors to Arduino
- Implement LCD displays
- Add NFC/RFID for wallet authentication
- Integrate hardware wallets

### Blockchain Enhancements
- Support multiple cryptocurrencies
- Implement DeFi protocols
- Add NFT minting capabilities
- Connect to mainnet (with real funds)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 🎉 Hackathon Demo

For India Codex Hackathon 2025 demonstration:

1. **Live Hardware Demo**: Physical Arduino button → Real Cardano transaction → ESP32 display
2. **AI Agent Showcase**: Autonomous Satoshi agents making blockchain decisions
3. **MCP Integration**: Claude AI controlling Arduino hardware via natural language
4. **Real Transactions**: Verifiable on Cardano testnet explorer

This showcases the future of IoT + Blockchain + AI integration!

## 📞 Support

- GitHub Issues: [Hardware-Implementation-of-Cardano/issues](https://github.com/puranik1406/Hardware-Implementation-of-Cardano/issues)
- Email: [Your contact email]
- Discord: [Your Discord if applicable]

## 📄 License

MIT License - See LICENSE file for details