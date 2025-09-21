# Unified Arduino-to-Cardano AI Agents System

A unified system that integrates Arduino devices with the Cardano blockchain through AI agents, supporting **real blockchain transactions**.

## 🚀 Features

- **Real Cardano Blockchain Integration**: Uses actual Cardano preprod testnet
- **Web Interface**: User-friendly interface on port 5000
- **Transaction Address Generation**: Generates wallet addresses for receiving payments
- **Blockchain Execution**: Executes real transactions and returns transaction hashes
- **Transaction Monitoring**: Real-time status updates and blockchain explorer links
- **Unified Architecture**: Combines Project and Project-dagadaga implementations

## 📋 Prerequisites

1. **Python 3.8+**
2. **Blockfrost API Key** (free from [blockfrost.io](https://blockfrost.io/))
3. **Test Wallet** with Cardano preprod test ADA
4. **Network Connection** for blockchain operations

## 🛠️ Setup Instructions

### Step 1: Quick Setup
```bash
cd Project
python setup.py
```

### Step 2: Manual Configuration (if needed)

1. **Get Blockfrost API Key**:
   - Go to [blockfrost.io](https://blockfrost.io/)
   - Create a free account
   - Create a new project for "Cardano Preprod"
   - Copy your project ID

2. **Configure Environment**:
   ```bash
   # Copy template
   cp .env.example ../Project-dagadaga/blockchain/.env
   
   # Edit the file and add your Blockfrost project ID
   # Replace 'your_blockfrost_project_id_here' with your actual project ID
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r ../Project-dagadaga/blockchain/requirements.txt
   ```

## 🚀 Running the System

### Start the Unified System
```bash
cd Project
python main.py
```

### What Happens:
1. System prompts: "Do you want to start the REAL blockchain system? (yes/no)"
2. Answer **yes** to proceed
3. Real blockchain payment service starts on port 8000
4. Main web interface starts on port 5000
5. Open browser to `http://localhost:5000`

## 🌐 Web Interface Usage

1. **Open** `http://localhost:5000` in your browser
2. **Click** "Initiate Transaction" button
3. **System will**:
   - Generate transaction address
   - Send address to blockchain service
   - Execute real Cardano transaction
   - Display transaction hash
   - Provide blockchain explorer link

## 🔗 API Endpoints

- `GET /` - Web interface
- `GET /health` - System health check
- `GET /send_request` - Generate transaction address
- `POST /execute_transaction` - Execute blockchain transaction
- `GET /transaction_status/<job_id>` - Check transaction status
- `GET /transactions` - List all transactions

## ⚠️ Important Notes

### Real Blockchain Usage
- This system uses **real Cardano blockchain** (preprod testnet)
- Transactions are **permanent** and **irreversible**
- Requires **test ADA** in sender wallet
- Network fees apply (small amounts)

### Transaction Flow
```
User Input → Address Generation → Real Blockchain Service → Cardano Network → Transaction Hash
```

### Network Information
- **Network**: Cardano Preprod Testnet
- **Explorer**: [preprod.cardanoscan.io](https://preprod.cardanoscan.io/)
- **Faucet**: [testnets.cardano.org](https://testnets.cardano.org/en/testnets/cardano/tools/faucet/)

## 📁 Project Structure

```
Project/
├── main.py                 # Unified main application
├── setup.py               # Setup script
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file

Project-dagadaga/
└── blockchain/
    ├── src/
    │   ├── real_payment_service.py    # Real blockchain service
    │   ├── blockfrost_client.py       # Cardano API client
    │   └── masumi_client.py           # Masumi protocol client
    └── .env                          # Environment configuration
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
BLOCKFROST_PROJECT_ID=your_actual_project_id
BLOCKFROST_BASE_URL=https://cardano-preprod.blockfrost.io/api/v0

# Optional
SENDER_WALLET_ADDRESS=your_test_wallet_address
MASUMI_NETWORK_URL=http://localhost:3001
PAYMENT_SERVICE_PORT=8000
```

## 🧪 Testing

### Test Real Blockchain Connection
```bash
cd Project-dagadaga/blockchain/src
python -c "from blockfrost_client import BlockfrostClient; client = BlockfrostClient(); print(client.get_network_info())"
```

### Test Payment Service
```bash
# Start payment service manually
cd Project-dagadaga/blockchain/src
python real_payment_service.py

# In another terminal, test health
curl http://localhost:8000/
```

## 🎯 Example Transaction

When you initiate a transaction through the web interface:

1. **Address Generated**: `addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp`
2. **Amount**: 1 ADA (1,000,000 lovelace)
3. **Transaction Hash**: Real Cardano transaction hash (e.g., `5288bde95f7f6d829f280443c59aec1f69b731c64bcbec481a31bc6cabec66a2`)
4. **Explorer Link**: Direct link to view transaction on CardanoScan

## 🔍 Troubleshooting

### Common Issues

1. **"Payment service not available"**
   - Check .env file configuration
   - Verify Blockfrost API key
   - Ensure network connectivity

2. **"Invalid address format"**
   - Verify wallet addresses are valid Cardano addresses
   - Check if addresses are for correct network (preprod)

3. **"Insufficient balance"**
   - Ensure sender wallet has test ADA
   - Get test ADA from Cardano faucet

4. **Connection timeouts**
   - Check internet connection
   - Verify Blockfrost service status
   - Try restarting the system

### Logs
Check system logs in:
- `unified_system.log` - Main system logs
- Console output - Real-time status updates

## 💡 Development

### Adding Features
- Transaction monitoring dashboard
- Multi-wallet support
- Custom transaction amounts
- Smart contract integration
- Arduino hardware integration

### Architecture
The system combines:
- **Flask web server** (port 5000) - User interface
- **FastAPI payment service** (port 8000) - Blockchain operations
- **Blockfrost API** - Cardano blockchain access
- **Masumi protocol** - Transaction routing (optional)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify .env configuration
3. Test Blockfrost connectivity
4. Check system logs

## 🚀 Ready to Start?

```bash
cd Project
python setup.py  # Configure system
python main.py   # Start unified system
```

Open `http://localhost:5000` and start sending real blockchain transactions! 🎉