# Unified Agent System - Arduino-to-Cardano AI Agents

A simplified, unified system that combines both the agents/ and Project/ components into a single, easy-to-use script.

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
python setup_unified_system.py
```

### 2. Run the System
```bash
python unified_agent_system.py
```

### 3. Initiate the System
- When prompted, type `yes` to initiate the Bedrock Agent system
- The system will start and display the transaction address
- Access the main endpoint at: `http://localhost:5000/send_request`

## 🎯 Key Features

- **Simple Yes/No Initiation**: Easy prompt to start the system
- **Transaction Address Display**: Shows the ADA wallet address for transactions
- **Bedrock Agent Integration**: Simplified agent logic without complex AWS setup
- **Clean API**: Single endpoint at `localhost:5000/send_request` as requested
- **Transaction Tracking**: Stores and manages transaction information

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and system status |
| `/send_request` | GET | **Main endpoint** - Get transaction address |
| `/send_request` | POST | Create custom transaction with amount |
| `/transactions` | GET | List all transactions |
| `/transaction/<id>` | GET | Get specific transaction details |

## 💰 Transaction Address

**Wallet Address:** `addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp`

This address will be displayed when you access `http://localhost:5000/send_request`

## 📋 Usage Examples

### Get Transaction Address
```bash
curl http://localhost:5000/send_request
```

### Create Custom Transaction
```bash
curl -X POST http://localhost:5000/send_request \
  -H "Content-Type: application/json" \
  -d '{"amount": 2.5}'
```

### Check System Health
```bash
curl http://localhost:5000/
```

## 🔧 Configuration

- **Default Amount**: 1.0 ADA
- **Port**: 5000
- **Wallet Address**: Cardano testnet address (built-in)
- **Mode**: Mock Bedrock (no AWS setup required)

## 📁 Files Overview

- `unified_agent_system.py` - Main unified script
- `setup_unified_system.py` - Setup and dependency installer
- `unified_requirements.txt` - Python dependencies
- `UNIFIED_README.md` - This documentation

## ✅ What This System Does

1. **Prompts for initiation** with yes/no question
2. **Starts the Bedrock agent** (simplified mock version)
3. **Displays transaction address** at the requested endpoint
4. **Hosts on localhost:5000/send_request** as specified
5. **Removes unnecessary complexity** from both original projects
6. **Provides clean API** for transaction address retrieval

## 🚫 What Was Removed

- Complex AWS Bedrock setup (uses mock instead)
- Arduino serial communication (simplified)
- Multiple agent interactions (unified into single service)
- Unnecessary configuration files
- Complex routing logic
- Multiple ports and services

## 🎯 Success Criteria

- ✅ Yes/No initiation prompt
- ✅ Bedrock agent initiation (simplified)
- ✅ Transaction address display
- ✅ Hosted on localhost:5000/send_request
- ✅ Removed unnecessary code
- ✅ Clean, simple setup

## 🤝 Original Projects

This unified system combines:
- **agents/** - Bedrock agent and wallet logic
- **Project/** - Router and API endpoints

Into a single, simplified script that meets your requirements without the complexity of the original multi-component architecture.
