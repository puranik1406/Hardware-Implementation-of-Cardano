# Arduino-Cardano Hardware Integration System
## IndiaCodex Hackathon 2025 Submission

🚀 **A revolutionary hardware-to-blockchain integration system that enables physical Arduino button presses to trigger real Cardano blockchain transactions.**

![Demo System](https://img.shields.io/badge/Status-Fully%20Functional-brightgreen)
![Arduino](https://img.shields.io/badge/Arduino-Uno-blue)
![Cardano](https://img.shields.io/badge/Cardano-Preprod%20Testnet-orange)
![Node.js](https://img.shields.io/badge/Node.js-Microservices-green)

## 🎯 **Project Overview**

This project demonstrates a complete **hardware-to-blockchain integration** where pressing a physical Arduino button triggers real Cardano blockchain transactions on the preprod testnet. The system features dual Arduino boards, real-time monitoring, and a complete microservices architecture.

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
- Node.js
- Python (for wallet generation)

### Hardware Setup
```bash
# Arduino #1 (Payment Trigger)
Button: Pin 2 → GND
LEDs: Pins 11, 12, 13

# Arduino #2 (Transaction Display)  
LCD I2C: SDA → A4, SCL → A5
```

### Software Setup
```bash
# 1. Clone the repository
git clone https://github.com/DhanushKenkiri/IndiaCodexHackathon--25-Submission.git

# 2. Start Docker services
docker compose up -d

# 3. Generate wallet
python scripts/create_lucid_wallet.py

# 4. Fund wallet at Cardano faucet
# https://testnets.cardano.org/en/testnets/cardano/tools/faucet/

# 5. Upload Arduino code
# payment_trigger.ino → Arduino #1 (COM6)
# transaction_display.ino → Arduino #2 (COM3)

# 6. Start Arduino Bridge
cd backend/arduino-bridge
npm start

# 7. Open dashboard
http://localhost:8090
```

## 🎥 **Demo Video**

[Link to demo video showing button press → blockchain transaction]

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

## 📈 **Future Roadmap**

- **IoT Integration**: Expand to ESP32/IoT devices
- **Multi-blockchain**: Support for other blockchain networks
- **Mobile App**: Remote monitoring and control
- **Smart Contracts**: Integration with Cardano smart contracts

## 👥 **Team**

- **Hardware Integration**: Arduino programming and circuit design
- **Blockchain Development**: Cardano integration and wallet management
- **Full-Stack Development**: Microservices architecture and real-time dashboard
- **DevOps**: Docker containerization and deployment

## 📞 **Contact**

For questions about this IndiaCodex Hackathon 2025 submission:
- GitHub: [DhanushKenkiri](https://github.com/DhanushKenkiri)
- Repository: https://github.com/DhanushKenkiri/IndiaCodexHackathon--25-Submission

---

**🎯 This project demonstrates the future of hardware-blockchain integration, making blockchain technology tangible and accessible through physical interfaces.**