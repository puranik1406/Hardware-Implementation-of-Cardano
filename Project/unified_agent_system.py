#!/usr/bin/env python3
"""
Unified Agent System - Arduino-to-Cardano AI Agents
Combines both projects with simplified initiation and transaction address display
"""

import os
import sys
import time
import threading
import subprocess
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
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

# Flask app setup
app = Flask(__name__)
CORS(app)

# In-memory storage for transactions
transactions_store = {}

class BedrockAgentService:
    """Simplified Bedrock Agent Service"""
    
    def __init__(self):
        self.use_mock = True  # Always use mock for simplicity
        self.wallet_address = WALLET_ADDRESS
        
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

# Initialize services
bedrock_service = BedrockAgentService()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Unified Agent System',
        'status': 'running',
        'wallet_address': WALLET_ADDRESS,
        'timestamp': datetime.now().isoformat(),
        'transactions_count': len(transactions_store)
    })

@app.route('/send_request', methods=['POST', 'GET'])
def send_request():
    """
    Main endpoint that displays transaction address
    This is the localhost:5000/send_request endpoint requested
    """
    try:
        if request.method == 'GET':
            # Display current wallet address and create a default transaction
            transaction = bedrock_service.create_transaction_offer()
            
            return jsonify({
                'status': 'success',
                'message': 'Transaction address ready',
                'transaction_address': transaction['wallet_address'],
                'transaction_id': transaction['transaction_id'],
                'amount_ada': transaction['amount_ada'],
                'amount_lovelace': transaction['amount_lovelace'],
                'timestamp': transaction['timestamp'],
                'endpoint': 'localhost:5000/send_request',
                'usage': 'This address can be used for ADA transactions'
            })
        
        elif request.method == 'POST':
            # Handle POST requests with custom amount
            data = request.get_json() or {}
            amount_ada = data.get('amount', DEFAULT_AMOUNT_ADA)
            
            # Ensure amount is valid
            if isinstance(amount_ada, (int, float)) and amount_ada > 0:
                transaction = bedrock_service.create_transaction_offer(amount_ada)
                
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

@app.route('/transactions', methods=['GET'])
def list_transactions():
    """List all transactions"""
    return jsonify({
        'transactions': list(transactions_store.values()),
        'count': len(transactions_store)
    })

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
    print("🚀 UNIFIED AGENT SYSTEM - Arduino-to-Cardano AI Agents")
    print("="*80)
    print(f"💰 Transaction Address: {WALLET_ADDRESS}")
    print(f"🌐 Server URL: http://localhost:{PORT}")
    print(f"📡 Main Endpoint: http://localhost:{PORT}/send_request")
    print("\n📋 Available Endpoints:")
    print(f"   GET  /                     - Health check")
    print(f"   GET  /send_request         - Get transaction address")
    print(f"   POST /send_request         - Create custom transaction")
    print(f"   GET  /transactions         - List all transactions")
    print(f"   GET  /transaction/<id>     - Get specific transaction")
    print("\n💡 Usage Examples:")
    print(f"   curl http://localhost:{PORT}/send_request")
    print(f"   curl -X POST http://localhost:{PORT}/send_request -H 'Content-Type: application/json' -d '{{\"amount\": 2.5}}'")
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
    print("\n🤖 Arduino-to-Cardano AI Agents - Unified System")
    print("=" * 60)
    
    # Yes/No prompt
    while True:
        response = input("\n❓ Do you want to initiate the Bedrock Agent system? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print("\n✅ Initiating Bedrock Agent system...")
            break
        elif response in ['no', 'n']:
            print("\n❌ System initiation cancelled.")
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("⚠️  Please enter 'yes' or 'no'")
    
    # Display system information
    display_system_info()
    
    # Start the server
    print("🔄 Starting unified system...")
    
    try:
        # Create a default transaction to display
        transaction = bedrock_service.create_transaction_offer()
        
        print(f"\n✅ System initialized successfully!")
        print(f"🎯 Transaction Address: {transaction['wallet_address']}")
        print(f"💵 Default Amount: {transaction['amount_ada']} ADA")
        print(f"🆔 Transaction ID: {transaction['transaction_id']}")
        print(f"\n🌐 Access the transaction address at: http://localhost:{PORT}/send_request")
        print("\nPress Ctrl+C to stop the system")
        
        # Start Flask server
        start_flask_server()
        
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"\n❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
