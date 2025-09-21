#!/usr/bin/env python3
"""
Unified Arduino-to-Cardano AI Agents System
Integrates Project wallet address generation with Project-dagadaga blockchain execution
"""

import os
import sys
import time
import threading
import subprocess
import json
import uuid
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
WALLET_ADDRESS = "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"
DEFAULT_AMOUNT_ADA = 1.0  # 1 ADA
PORT = 5000
PAYMENT_SERVICE_PORT = 8000
PAYMENT_SERVICE_URL = f"http://localhost:{PAYMENT_SERVICE_PORT}"

# Flask app setup
app = Flask(__name__)
CORS(app)

# In-memory storage for transactions
transactions_store = {}
payment_service_process = None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Arduino-to-Cardano AI Agents</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }
        .transaction-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .address {
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
            margin: 10px 0;
        }
        .hash {
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
            margin: 10px 0;
            color: #90EE90;
        }
        button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: all 0.3s ease;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid #fff;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .success { color: #90EE90; }
        .error { color: #ffcccb; }
        .info { color: #87CEEB; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Arduino-to-Cardano AI Agents</h1>
        
        <div class="status-card">
            <h3>System Status</h3>
            <p><strong>Server:</strong> <span class="success">Running on Port {{ port }}</span></p>
            <p><strong>Wallet Address:</strong></p>
            <div class="address">{{ wallet_address }}</div>
            <p><strong>Time:</strong> {{ timestamp }}</p>
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <button onclick="initiateTransaction()">🔄 Initiate Transaction</button>
            <button onclick="refreshStatus()">📡 Refresh Status</button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing transaction...</p>
        </div>

        <div id="results"></div>
    </div>

    <script>
        async function initiateTransaction() {
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            loading.style.display = 'block';
            results.innerHTML = '';
            
            try {
                // Step 1: Get transaction address
                const addressResponse = await fetch('/send_request');
                const addressData = await addressResponse.json();
                
                if (addressData.status === 'success') {
                    results.innerHTML += `
                        <div class="transaction-card">
                            <h4>✅ Step 1: Transaction Address Generated</h4>
                            <p><strong>Transaction ID:</strong> ${addressData.transaction_id}</p>
                            <p><strong>Amount:</strong> ${addressData.amount_ada} ADA</p>
                            <p><strong>Address:</strong></p>
                            <div class="address">${addressData.transaction_address}</div>
                        </div>
                    `;
                    
                    // Step 2: Execute blockchain transaction
                    results.innerHTML += `
                        <div class="transaction-card">
                            <h4>🔄 Step 2: Executing Blockchain Transaction...</h4>
                            <p class="info">Sending to payment service...</p>
                        </div>
                    `;
                    
                    const executeResponse = await fetch('/execute_transaction', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            transaction_id: addressData.transaction_id,
                            amount: addressData.amount_ada
                        })
                    });
                    
                    const executeData = await executeResponse.json();
                    
                    if (executeData.status === 'success') {
                        const realBlockchain = executeData.real_blockchain ? '🌐 Real Cardano Blockchain' : '🔧 Test Network';
                        const txHashDisplay = executeData.tx_hash === 'pending' ? 
                            '<span class="info">Transaction hash will be available after submission</span>' : 
                            executeData.tx_hash;
                        
                        results.innerHTML += `
                            <div class="transaction-card">
                                <h4>✅ Step 2: Real Blockchain Transaction Executed</h4>
                                <p><strong>Network:</strong> ${realBlockchain}</p>
                                <p><strong>Transaction Hash:</strong></p>
                                <div class="hash">${txHashDisplay}</div>
                                <p><strong>Job ID:</strong> ${executeData.job_id}</p>
                                ${executeData.masumi_tx_id ? `<p><strong>Masumi TX ID:</strong> ${executeData.masumi_tx_id}</p>` : ''}
                                <p><strong>Status:</strong> <span class="success">${executeData.transaction_status}</span></p>
                                <p><strong>Confirmation Time:</strong> ~${executeData.estimated_confirmation_time} seconds</p>
                                <p class="info">💡 This is a real Cardano transaction on preprod testnet</p>
                                ${executeData.tx_hash !== 'pending' ? 
                                    `<p><strong>Explorer:</strong> <a href="https://preprod.cardanoscan.io/transaction/${executeData.tx_hash}" target="_blank" style="color: #87CEEB;">View on CardanoScan</a></p>` : 
                                    '<p class="info">🔄 Transaction hash will appear once submitted to network</p>'
                                }
                            </div>
                        `;
                    } else {
                        results.innerHTML += `
                            <div class="transaction-card">
                                <h4>❌ Step 2: Transaction Failed</h4>
                                <p class="error">${executeData.message}</p>
                            </div>
                        `;
                    }
                } else {
                    results.innerHTML = `
                        <div class="transaction-card">
                            <h4>❌ Failed to Generate Transaction Address</h4>
                            <p class="error">${addressData.message}</p>
                        </div>
                    `;
                }
            } catch (error) {
                results.innerHTML = `
                    <div class="transaction-card">
                        <h4>❌ System Error</h4>
                        <p class="error">Error: ${error.message}</p>
                    </div>
                `;
            } finally {
                loading.style.display = 'none';
            }
        }
        
        async function refreshStatus() {
            try {
                const response = await fetch('/');
                const data = await response.json();
                location.reload();
            } catch (error) {
                console.error('Failed to refresh status:', error);
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""

class UnifiedPaymentSystem:
    """Unified system that integrates address generation with blockchain execution"""
    
    def __init__(self):
        self.wallet_address = WALLET_ADDRESS
        self.payment_service_running = False
        
    def create_transaction_offer(self, amount_ada=DEFAULT_AMOUNT_ADA):
        """Create a transaction offer with wallet address"""
        transaction_id = f"tx_{uuid.uuid4().hex[:8]}"
        amount_lovelace = int(amount_ada * 1000000)
        
        transaction_data = {
            "transaction_id": transaction_id,
            "wallet_address": self.wallet_address,
            "amount_ada": amount_ada,
            "amount_lovelace": amount_lovelace,
            "currency": "ADA",
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "action": "send_to_wallet"
        }
        
        # Store transaction
        transactions_store[transaction_id] = transaction_data
        
        logger.info(f"Created transaction: {amount_ada} ADA -> {self.wallet_address}")
        return transaction_data
    
    def start_payment_service(self):
        """Start the real blockchain payment service in background"""
        try:
            # Change to the Project-dagadaga directory
            payment_dir = "c:\\Users\\dhwin\\project-unifiedcardonahackathon\\Project-dagadaga\\blockchain\\src"
            
            if os.path.exists(payment_dir):
                logger.info(f"Starting REAL blockchain payment service from {payment_dir}")
                # Start the real payment service (not mock)
                process = subprocess.Popen([
                    sys.executable, "real_payment_service.py"
                ], 
                cwd=payment_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
                
                # Give it more time to start (real blockchain connections take longer)
                time.sleep(8)
                
                # Check if service is running
                try:
                    response = requests.get(f"{PAYMENT_SERVICE_URL}/", timeout=10)
                    if response.status_code == 200:
                        service_info = response.json()
                        if service_info.get("mode") == "real":
                            self.payment_service_running = True
                            logger.info("✅ Real blockchain payment service started successfully")
                            logger.info(f"🌐 Connected to {service_info.get('network', 'unknown')} network")
                            logger.info(f"🔗 Blockfrost: {service_info.get('clients', {}).get('blockfrost', 'unknown')}")
                            logger.info(f"🔗 Masumi: {service_info.get('clients', {}).get('masumi', 'unknown')}")
                            return process
                        else:
                            logger.error("❌ Payment service started in wrong mode (not real)")
                    else:
                        logger.error("❌ Payment service not responding correctly")
                except requests.exceptions.RequestException as e:
                    logger.error(f"❌ Payment service connection failed: {e}")
                    
            else:
                logger.error(f"❌ Payment service directory not found: {payment_dir}")
                
        except Exception as e:
            logger.error(f"❌ Failed to start real payment service: {e}")
            
        return None
    
    def execute_blockchain_transaction(self, transaction_id, amount_ada):
        """Execute the actual blockchain transaction using real Cardano network"""
        try:
            if not self.payment_service_running:
                return {
                    "status": "error",
                    "message": "Real blockchain payment service not available"
                }
            
            # For real transactions, we need a valid sender address with UTXOs
            # Using a test wallet address (this should be configurable)
            sender_address = os.getenv("SENDER_WALLET_ADDRESS", "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z")
            
            # Prepare real payment request
            payment_data = {
                "from_address": sender_address,
                "to_address": self.wallet_address,
                "amount": int(amount_ada * 1000000),  # Convert to lovelace
                "metadata": {
                    "transaction_id": transaction_id,
                    "source": "unified_system",
                    "timestamp": datetime.now().isoformat(),
                    "type": "real_blockchain_transaction",
                    "amount_ada": amount_ada
                }
            }
            
            logger.info(f"🔗 Executing real blockchain transaction: {amount_ada} ADA")
            logger.info(f"📤 From: {sender_address}")
            logger.info(f"📥 To: {self.wallet_address}")
            
            # Send to real payment service
            response = requests.post(
                f"{PAYMENT_SERVICE_URL}/send_payment",
                json=payment_data,
                timeout=60  # Longer timeout for real blockchain operations
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update transaction store with real blockchain data
                if transaction_id in transactions_store:
                    transactions_store[transaction_id].update({
                        "blockchain_job_id": result["job_id"],
                        "masumi_tx_id": result.get("masumi_tx_id"),
                        "tx_hash": result.get("tx_hash"),
                        "blockchain_status": result["status"],
                        "executed_at": datetime.now().isoformat(),
                        "real_blockchain": True,
                        "estimated_confirmation_time": result.get("estimated_confirmation_time", 300)
                    })
                
                logger.info(f"✅ Real blockchain transaction initiated!")
                logger.info(f"🆔 Job ID: {result['job_id']}")
                if result.get("tx_hash"):
                    logger.info(f"🔗 Transaction Hash: {result['tx_hash']}")
                logger.info(f"⏱️ Status: {result['status']}")
                
                return {
                    "status": "success",
                    "tx_hash": result.get("tx_hash", "pending"),
                    "job_id": result["job_id"],
                    "masumi_tx_id": result.get("masumi_tx_id"),
                    "transaction_status": result["status"],
                    "estimated_confirmation_time": result.get("estimated_confirmation_time", 300),
                    "message": "Real blockchain transaction initiated",
                    "network": "cardano-preprod",
                    "real_blockchain": True
                }
            else:
                error_detail = "Unknown error"
                try:
                    error_response = response.json()
                    error_detail = error_response.get("detail", str(error_response))
                except:
                    error_detail = response.text
                    
                logger.error(f"❌ Real payment service error: {response.status_code} - {error_detail}")
                return {
                    "status": "error",
                    "message": f"Real payment service error: {response.status_code} - {error_detail}"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Connection to real payment service failed: {e}")
            return {
                "status": "error",
                "message": f"Connection to real payment service failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Real blockchain transaction failed: {e}")
            return {
                "status": "error",
                "message": f"Real blockchain transaction failed: {str(e)}"
            }

# Initialize unified system
unified_system = UnifiedPaymentSystem()

@app.route('/', methods=['GET'])
def web_interface():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE, 
                                wallet_address=WALLET_ADDRESS,
                                port=PORT,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Unified Arduino-to-Cardano System',
        'status': 'running',
        'wallet_address': WALLET_ADDRESS,
        'payment_service_running': unified_system.payment_service_running,
        'timestamp': datetime.now().isoformat(),
        'transactions_count': len(transactions_store)
    })

@app.route('/send_request', methods=['GET', 'POST'])
def send_request():
    """Generate transaction address (Step 1)"""
    try:
        if request.method == 'GET':
            # Display current wallet address and create a default transaction
            transaction = unified_system.create_transaction_offer()
            
            return jsonify({
                'status': 'success',
                'message': 'Transaction address ready',
                'transaction_address': transaction['wallet_address'],
                'transaction_id': transaction['transaction_id'],
                'amount_ada': transaction['amount_ada'],
                'amount_lovelace': transaction['amount_lovelace'],
                'timestamp': transaction['timestamp'],
                'endpoint': f'localhost:{PORT}/send_request'
            })
        
        elif request.method == 'POST':
            # Handle POST requests with custom amount
            data = request.get_json() or {}
            amount_ada = data.get('amount', DEFAULT_AMOUNT_ADA)
            
            if isinstance(amount_ada, (int, float)) and amount_ada > 0:
                transaction = unified_system.create_transaction_offer(amount_ada)
                
                return jsonify({
                    'status': 'success',
                    'message': 'Transaction created successfully',
                    'transaction_address': transaction['wallet_address'],
                    'transaction_id': transaction['transaction_id'],
                    'amount_ada': transaction['amount_ada'],
                    'amount_lovelace': transaction['amount_lovelace'],
                    'timestamp': transaction['timestamp']
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid amount provided'
                }), 400
    
    except Exception as e:
        logger.error(f"Error in send_request: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/execute_transaction', methods=['POST'])
def execute_transaction():
    """Execute blockchain transaction (Step 2)"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        amount_ada = data.get('amount', DEFAULT_AMOUNT_ADA)
        
        if not transaction_id:
            return jsonify({
                'status': 'error',
                'message': 'Transaction ID required'
            }), 400
        
        # Execute the blockchain transaction
        result = unified_system.execute_blockchain_transaction(transaction_id, amount_ada)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in execute_transaction: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Transaction execution error: {str(e)}'
        }), 500

@app.route('/transactions', methods=['GET'])
def list_transactions():
    """List all transactions"""
    return jsonify({
        'transactions': list(transactions_store.values()),
        'count': len(transactions_store)
    })

@app.route('/transaction_status/<job_id>', methods=['GET'])
def get_transaction_status(job_id):
    """Get real-time transaction status from blockchain service"""
    try:
        if not unified_system.payment_service_running:
            return jsonify({
                'status': 'error',
                'message': 'Payment service not available'
            }), 503
        
        # Query the real payment service for status
        response = requests.get(f"{PAYMENT_SERVICE_URL}/tx_status/{job_id}", timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            
            # Enhance status data with explorer links if transaction is confirmed
            if status_data.get("tx_hash") and status_data.get("status") == "confirmed":
                status_data["explorer_url"] = f"https://preprod.cardanoscan.io/transaction/{status_data['tx_hash']}"
                status_data["blockfrost_url"] = f"https://preprod.blockfrost.io/api/v0/txs/{status_data['tx_hash']}"
            
            return jsonify(status_data)
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to get transaction status: {response.status_code}'
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting transaction status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        }), 500
    except Exception as e:
        logger.error(f"Error in get_transaction_status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal error: {str(e)}'
        }), 500

@app.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get specific transaction details"""
    transaction = transactions_store.get(transaction_id)
    if transaction:
        return jsonify(transaction)
    else:
        return jsonify({'error': 'Transaction not found'}), 404

def display_system_info():
    """Display system information"""
    print("\n" + "="*80)
    print("🚀 UNIFIED ARDUINO-TO-CARDANO AI AGENTS SYSTEM (REAL BLOCKCHAIN)")
    print("="*80)
    print(f"💰 Transaction Address: {WALLET_ADDRESS}")
    print(f"🌐 Server URL: http://localhost:{PORT}")
    print(f"📡 Main Interface: http://localhost:{PORT}/")
    print(f"🔧 Payment Service: {PAYMENT_SERVICE_URL}")
    print(f"⛓️  Network: Cardano Preprod Testnet (REAL BLOCKCHAIN)")
    print("\n📋 How it works:")
    print("   1. User clicks 'Initiate Transaction' on web interface")
    print("   2. System generates transaction address")
    print("   3. Address is sent to REAL blockchain payment service")
    print("   4. Payment service executes REAL Cardano transaction via Masumi")
    print("   5. REAL transaction hash is displayed to user")
    print("   6. Transaction can be viewed on Cardano blockchain explorer")
    print("\n⚠️  IMPORTANT:")
    print("   - This uses REAL Cardano preprod testnet")
    print("   - Transactions are permanent on the blockchain")
    print("   - Requires valid wallet with test ADA")
    print("   - Requires Blockfrost API key and Masumi setup")
    print("\n💡 Access the web interface at:")
    print(f"   http://localhost:{PORT}/")
    print("\n" + "="*80)

def start_flask_server():
    """Start the Flask server"""
    try:
        logger.info(f"Starting Flask server on port {PORT}")
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}")
        return False

def main():
    """Main function with yes/no prompt"""
    print("\n🤖 Arduino-to-Cardano AI Agents - Unified System (REAL BLOCKCHAIN)")
    print("=" * 70)
    
    # Check if environment is configured
    env_file = "c:\\Users\\dhwin\\project-unifiedcardonahackathon\\Project-dagadaga\\blockchain\\.env"
    if not os.path.exists(env_file):
        print("\n⚠️  SETUP REQUIRED:")
        print("   No .env file found for blockchain configuration.")
        print("   Please see .env.example in the Project folder for setup instructions.")
        print("   You need:")
        print("   - Blockfrost API key (free from https://blockfrost.io/)")
        print("   - Test wallet with preprod test ADA")
        print("   - Proper environment configuration")
        print("\n   After setup, the system will use REAL Cardano blockchain!")
    
    # Yes/No prompt
    while True:
        response = input("\n❓ Do you want to start the REAL blockchain system? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print("\n✅ Starting unified system with REAL blockchain...")
            break
        elif response in ['no', 'n']:
            print("\n❌ System startup cancelled.")
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("⚠️  Please enter 'yes' or 'no'")
    
    # Display system information
    display_system_info()
    
    # Start the payment service first
    print("🔄 Starting REAL blockchain payment service...")
    global payment_service_process
    payment_service_process = unified_system.start_payment_service()
    
    if not unified_system.payment_service_running:
        print("\n❌ Failed to start real blockchain payment service!")
        print("   Please check:")
        print("   - .env file is properly configured")
        print("   - Blockfrost API key is valid")
        print("   - Network connectivity")
        print("   - Requirements are installed: pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Start the main server
    print("🔄 Starting main server...")
    
    try:
        print(f"\n✅ REAL blockchain system initialized successfully!")
        print(f"🌐 Open your browser and go to: http://localhost:{PORT}/")
        print(f"⛓️  Connected to Cardano Preprod Testnet")
        print("\n⚠️  IMPORTANT: This will execute REAL blockchain transactions!")
        print("Press Ctrl+C to stop the system")
        
        # Start Flask server
        start_flask_server()
        
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
        if payment_service_process:
            print("🔄 Stopping payment service...")
            payment_service_process.terminate()
        print("👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"\n❌ System error: {e}")
        if payment_service_process:
            payment_service_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()