# Arduino-Cardano Hardware Integration System
## IndiaCodex Hackathon 2025 Submission

🚀 **A revolutionary hardware-to-blockchain integration system that enables physical Arduino button presses to trigger real Cardano blockchain transactions.**

![Demo System](https://img.shields.io/badge/Status-Fully%20Functional-brightgreen)
![Arduino](https://img.shields.io/badge/Arduino-Uno-blue)
![Cardano](https://img.shields.io/badge/Cardano-Preprod%20Testnet-orange)
![Node.js](https://img.shields.io/badge/Node.js-Microservices-green)

## 🎯 **Project Overview**

This project demonstrates a complete **hardware-to-blockchain integration** where pressing a physical Arduino button triggers real Cardano blockchain transactions on the preprod testnet. The system features dual Arduino boards, real-time monitoring, and a complete microservices architecture.

## 🎥 **Demo Videos**

### 🏆 **Hackathon Day Demo**
**Live Arduino-Cardano Integration System**

<div align="center">
  <a href="https://youtu.be/UafLTltfD5o">
    <img src="https://img.youtube.com/vi/UafLTltfD5o/maxresdefault.jpg" alt="Hackathon Demo" style="width:100%; max-width:800px;">
  </a>
  <p><em>Click to watch: Arduino button press → Real Cardano blockchain transaction → LCD display → Live dashboard monitoring</em></p>
</div>

**Watch on YouTube:** https://youtu.be/UafLTltfD5o

---

### 🚀 **Future Vision Demo**
**Real-World Application Showcase**

<div align="center">
  <a href="https://youtu.be/tLkZvUDTP0s">
    <img src="https://img.youtube.com/vi/tLkZvUDTP0s/maxresdefault.jpg" alt="Future Vision Demo" style="width:100%; max-width:800px;">
  </a>
  <p><em>Click to watch: A fun representation showcasing how this technology will be used in real-world scenarios</em></p>
</div>

**Watch on YouTube:** https://youtu.be/tLkZvUDTP0s

---

## 🏗️ **System Architecture**

```
Arduino Button → Arduino Bridge → Masumi Payment → Cardano Integration → Blockchain
     ↓               ↓                ↓                     ↓                ↓
Physical Input   Serial COM      REST API           Blockfrost API    Real Transaction
     ↓               ↓                ↓                     ↓                ↓
LCD Display ← Transaction Display ← Socket.IO ← Real-time Dashboard ← Live Monitoring
```

## 🔧 **Hardware Components**

### Arduino #1 - Payment Trigger (COM6)
- **Button**: Pin 2 (with pull-up resistor)
- **LEDs**: 
  - Pin 13: Success indicator
  - Pin 12: Processing indicator  
  - Pin 11: Error indicator
- **Function**: Triggers payment commands via serial

### Arduino #2 - Transaction Display (COM3)
- **LCD I2C Display**: A4 (SDA), A5 (SCL)
- **Function**: Shows transaction hashes and status messages

## 💻 **Software Stack**

### **Microservices Architecture**
- **Arduino Bridge** (Port 5001): Serial communication gateway
- **Masumi Payment** (Port 3001): Payment orchestration service
- **Cardano Integration** (Port 4002): Blockchain transaction service
- **AI Agents** (Port 6001): Decision engine service
- **Web Dashboard** (Port 8090): Real-time monitoring interface

### **Technologies**
- **Backend**: Node.js, Express, Socket.IO
- **Database**: PostgreSQL, Redis
- **Blockchain**: Cardano Preprod Testnet via Blockfrost API
- **Hardware**: Arduino Uno, I2C LCD, Serial Communication
- **Containerization**: Docker Compose
- **Real-time**: WebSockets for live monitoring

## 🚀 **Key Features**

### ✅ **Physical Hardware Integration**
- Real Arduino button triggers blockchain transactions
- LCD display shows transaction hashes in real-time
- LED indicators for transaction status

### ✅ **Real-time Monitoring**
- Live web dashboard showing serial communication
- Transaction status tracking
- Wallet balance monitoring

### ✅ **Blockchain Integration**
- Real Cardano preprod testnet transactions
- Proper wallet generation and signing
- UTxO management and transaction building

### ✅ **Microservices Architecture**
- Scalable Docker-based services
- Health monitoring and auto-restart
- Service discovery and communication

## 📱 **Live Demo Flow**

1. **Press Arduino Button** → Physical button press detected
2. **Serial Communication** → Commands sent via COM6
3. **Payment Processing** → Arduino Bridge forwards to payment service
4. **Blockchain Transaction** → Real Cardano transaction created
5. **Real-time Display** → Transaction hash shown on LCD and dashboard
6. **Confirmation** → LEDs indicate success/failure

## 🔧 **Quick Setup**

### Prerequisites
- Arduino IDE
- Docker Desktop
- Node.js 18+
- Python (for wallet generation)
- Blockfrost Preprod API key

### Hardware Setup
```bash
# Arduino #1 (Payment Trigger) - Connect to COM6
Button: Pin 2 → GND (with pull-up resistor)
Success LED: Pin 13 → 220Ω resistor → LED → GND
Processing LED: Pin 12 → 220Ω resistor → LED → GND
Error LED: Pin 11 → 220Ω resistor → LED → GND

# Arduino #2 (Transaction Display) - Connect to COM3
LCD I2C: SDA → A4, SCL → A5, VCC → 5V, GND → GND
```

### Software Setup
```bash
# 1. Clone the repository
git clone https://github.com/DhanushKenkiri/IndiaCodexHackathon--25-Submission.git
cd IndiaCodexHackathon--25-Submission

# 2. Configure environment
# Edit 'env' file with your Blockfrost key and settings
cp env.example env

# 3. Generate Cardano wallet
python scripts/create_lucid_wallet.py

# 4. Fund wallet at Cardano faucet
# Visit: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/
# Use address from: keys/new-wallet/address.txt

# 5. Start Docker services
docker compose up -d --build

# 6. Upload Arduino code
# Upload hardware/arduino-uno/payment_trigger.ino → Arduino #1 (COM6)
# Upload hardware/arduino-uno/transaction_display.ino → Arduino #2 (COM3)

# 7. Start web dashboard
cd frontend/web-dashboard
npm ci
npm start
# Dashboard available at: http://localhost:8090

# 8. Test the system
# Press the Arduino button and watch the magic happen!
```

## 🏆 **Innovation Highlights**

### 🌟 **Hardware-Blockchain Bridge**
First-of-its-kind direct integration between physical Arduino hardware and Cardano blockchain

### 🌟 **Real-time Monitoring**
Live dashboard showing every step from button press to blockchain confirmation

### 🌟 **Dual Arduino Architecture**
Separate boards for input (trigger) and output (display) with coordinated communication

### 🌟 **Production-Ready Code**
Complete microservices architecture with proper error handling and monitoring

## 📊 **Technical Achievements**

- ✅ **Real Blockchain Transactions**: Not simulated - actual Cardano preprod transactions
- ✅ **Multi-COM Port Management**: Simultaneous communication with two Arduino boards  
- ✅ **Real-time Communication**: WebSocket-based live monitoring
- ✅ **Containerized Deployment**: Full Docker Compose stack
- ✅ **Wallet Integration**: Proper Cardano wallet generation and signing

## 🔐 **Security Features**

- Environment-based key management
- Testnet-only operations (no mainnet risk)
- Proper CBOR key formatting
- Health check monitoring
- Admin token protection for sensitive endpoints

## 📡 **API Endpoints**

### Arduino Bridge Service (Port 5001)
- `GET /status` - Service health check
- `POST /trigger` - Manual payment trigger
- WebSocket events for real-time communication

### Masumi Payment Service (Port 3001)
- `POST /payments` - Create payment
- `GET /payments` - List transactions
- `GET /balance` - Check wallet balance

### Cardano Integration Service (Port 4002)
- `POST /transfer` - Execute blockchain transaction
- `GET /utxos` - Query UTxOs
- `GET /balance` - Get wallet balance

## 📈 **Future Roadmap**

- **IoT Integration**: Expand to ESP32/IoT devices
- **Multi-blockchain**: Support for other blockchain networks
- **Mobile App**: Remote monitoring and control
- **Smart Contracts**: Integration with Cardano smart contracts
- **Mainnet Support**: Production deployment considerations

## 🛠️ **Troubleshooting**

### Common Issues
1. **COM Port Issues**: Ensure Arduino boards are connected to correct ports (COM6 & COM3)
2. **Docker Issues**: Make sure Docker Desktop is running
3. **Wallet Issues**: Ensure wallet is funded via Cardano testnet faucet
4. **Serial Communication**: Check Arduino IDE Serial Monitor for debugging

### Debugging Commands
```bash
# Check Docker services
docker compose ps

# View service logs
docker compose logs arduino-bridge
docker compose logs masumi-payment

# Check Arduino connectivity
# Use Arduino IDE Serial Monitor on COM6 and COM3
```

## 👥 **Team & Development**

- **Hardware Integration**: Arduino programming and circuit design
- **Blockchain Development**: Cardano integration and wallet management  
- **Full-Stack Development**: Microservices architecture and real-time dashboard
- **DevOps**: Docker containerization and deployment

## 📞 **Contact & Support**

For questions about this IndiaCodex Hackathon 2025 submission:
- **GitHub**: [DhanushKenkiri](https://github.com/DhanushKenkiri)
- **Repository**: https://github.com/DhanushKenkiri/IndiaCodexHackathon--25-Submission
- **Documentation**: See `docs/` folder for detailed guides

## 📚 **Additional Documentation**

- `docs/setup-guide.md` - Detailed setup instructions
- `docs/api-documentation.md` - Complete API reference
- `docs/hardware-wiring.md` - Hardware connection diagrams
- `TASKS.md` - Development task tracking

---

**🎯 This project demonstrates the future of hardware-blockchain integration, making blockchain technology tangible and accessible through physical interfaces.**

---

## 🏅 **Hackathon Submission Summary**

This Arduino-Cardano integration system represents a breakthrough in making blockchain technology accessible through physical interfaces. By enabling real Arduino button presses to trigger actual Cardano blockchain transactions, we've created a tangible bridge between the physical and digital worlds.

**Key achievements:**
- ✅ Fully functional hardware-to-blockchain integration
- ✅ Real Cardano preprod testnet transactions
- ✅ Complete microservices architecture
- ✅ Real-time monitoring and display
- ✅ Production-ready code with proper security

**Demo the future of blockchain interaction - where pressing a button is all it takes to execute a blockchain transaction!** 🚀