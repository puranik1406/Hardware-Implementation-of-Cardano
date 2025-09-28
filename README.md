# Arduino Masumi Network Simulator

A production-grade React application simulating Arduino boards integrated with the Masumi Network for agentic payments using the Sokosumi agent framework on the Cardano blockchain.

## 🚀 Features

### Arduino Simulation
- **Dual Arduino Boards**: Complete simulation of Arduino Uno R3 with digital and analog pins
- **Real Code Editor**: Syntax-highlighted C++ code editor with Arduino libraries
- **Serial Monitor**: Live serial output simulation
- **Pin Visualization**: Interactive digital (0-13) and analog (A0-A5) pin states
- **Upload & Run**: Simulate code compilation and execution

### Masumi Network Integration
- **Agentic Payments**: Automated payments between Arduino agents
- **Real-time Monitoring**: Live network status and agent activity
- **Sokosumi Framework**: Integration with Sokosumi agent network
- **Cardano Blockchain**: Simulated ADA transactions
- **Payment History**: Complete transaction tracking and analytics

### Advanced Features
- **Network Statistics**: Real-time latency, throughput, and block height monitoring
- **Agent Management**: Registration and status tracking of Arduino agents
- **Payment Panel**: Interactive payment interface with quick amounts
- **Visual Feedback**: Animated status indicators and payment flows
- **Responsive Design**: Works on desktop and mobile devices

## 🛠 Technology Stack

- **Frontend**: React 18 + Vite
- **Styling**: Tailwind CSS with custom Arduino and Masumi themes
- **Code Editor**: CodeMirror 6 with C++ syntax highlighting
- **Icons**: Lucide React
- **State Management**: React Hooks
- **Build Tool**: Vite for fast development and building

## 📦 Installation & Usage

### Quick Start (Production-Ready)

```powershell
# 1) Install dependencies
npm install

# 2) Start Masumi services (Postgres + Payment + Registry)
npm run compose:up

# 3) Start frontend
npm run dev
```

### Alternative: Mock Mode (No Backend)

```powershell
# 1) Install dependencies  
npm install

# 2) Run mock API
npm run mock-api

# 3) Start frontend (separate terminal)
npm run dev
```

Open http://localhost:5173

📋 **See SETUP_INSTRUCTIONS.md for complete production workflow**

## 🎯 Quick Start

1. **Launch Application**: The app automatically connects to the simulated Masumi Network
2. **View Arduino Boards**: Two pre-configured boards (Sender and Receiver) with real Arduino code
3. **Send Payments**: Use the payment panel to transfer ADA between Arduino agents
4. **Monitor Activity**: Watch real-time network statistics and transaction history
5. **Edit Code**: Modify Arduino C++ code and simulate execution

## 🌐 Masumi Network Integration

This simulator implements the complete Masumi Network ecosystem:
- **Sokosumi Agents**: Arduino devices as autonomous payment agents
- **Cardano Integration**: Simulated ADA transactions on Cardano blockchain
- **Real-time Communication**: WebSocket connections for instant updates
- **Agent Framework**: Complete lifecycle management for Arduino agents

## 📊 Key Components

- **ArduinoBoard**: Complete Arduino Uno simulation with pins and code editor
- **MasumiPaymentPanel**: Payment interface with transaction history
- **AgentStatusPanel**: Network monitoring and agent management
- **CodeEditor**: Syntax-highlighted Arduino C++ code editor

## 🧪 Testing

- Use the payment panel to send ADA between agents
- Watch the Agent Status panel for network stats and recent activity
- Edit Arduino code and click Run to simulate device behavior

## 🏭 Production Setup

For a complete, production-ready workflow (Docker Compose, env, REST/WS examples, deployment notes), see:

- docs/PRODUCTION_SETUP.md

This includes:
- Docker Compose stack for Postgres + Masumi Payment/Registry
- Root `.env` placeholders for backend and frontend
- Health checks and example curl calls
- Node.js sample to register an agent and subscribe to payment WebSocket

## 📚 Examples

- Node (register + listen): examples/node/register-and-listen.mjs
	- Run with:
		```powershell
		npm run example:node
		```

## 📝 Submission Checklist (Hackathon)

- [x] Repository public and accessible
- [x] README with setup, usage, and architecture
- [x] Video demo link included (placeholder below)
- [x] Clear explanation of value and features
- [x] Links to Masumi/Sokosumi docs and faucet

### Video Demo
- Presentation + Live Demo: https://example.com/your-demo-video

## 🔗 Helpful Links

- Masumi Docs: https://docs.masumi.network/
- Install Masumi Services: https://docs.masumi.network/documentation/get-started/installation
- CrewAI Quickstart: https://github.com/masumi-network/crewai-masumi-quickstart-template
- Sokosumi Agents: https://app.sokosumi.com/agents
- tAda Faucet: https://dispenser.masumi.network/
- Telegram: https://t.me/+FtkeBaITmjlkZDky
- Discord: https://discord.gg/WVDHxZQdzp

## 🧰 Project Structure

See `MASUMI_INTEGRATION_GUIDE.md` for detailed integration steps and `.env.example` for environment variables.

## ⚠️ Security

- Do not commit `.env` files
- Use testnet credentials for development
- Enable HTTPS/WSS in production

---

Built with ❤️ for the Arduino and Cardano communities using Masumi Network technology.
