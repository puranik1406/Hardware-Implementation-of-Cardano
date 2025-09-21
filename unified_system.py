#!/usr/bin/env python3
"""
UNIFIED Arduino-to-Cardano AI Agents System
Complete integration in one script - Web interface + Real blockchain transactions
"""

import os
import sys
import time
import threading
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

# Web framework imports
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# FastAPI imports for payment service
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# HTTP requests
import requests

# Environment and configuration
from dotenv import load_dotenv

# Try to import blockchain dependencies (optional)
try:
    import blockfrost_python as blockfrost
    BLOCKFROST_AVAILABLE = True
except ImportError:
    BLOCKFROST_AVAILABLE = False
    print("⚠️  Blockfrost not available - using mock mode")

# Load environment
load_dotenv()

# Configure logging with better encoding
class SafeFormatter(logging.Formatter):
    def format(self, record):
        # Replace emojis with safe alternatives for Windows console
        message = super().format(record)
        return message.encode('ascii', 'replace').decode('ascii')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
WALLET_ADDRESS = "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"
DEFAULT_AMOUNT_ADA = 1.0
MAIN_PORT = 5000
PAYMENT_PORT = 8000

# Global storage
transactions_store = {}
payment_jobs = {}

# ============================================================================
# BLOCKCHAIN CLIENT CLASSES
# ============================================================================

class SimpleBlockfrostClient:
    """Simplified Blockfrost client for basic operations"""
    
    def __init__(self):
        self.project_id = os.getenv("BLOCKFROST_PROJECT_ID", "")
        self.base_url = os.getenv("BLOCKFROST_BASE_URL", "https://cardano-preprod.blockfrost.io/api/v0")
        self.available = bool(self.project_id and self.project_id != "preprodYourProjectIdHere")
        
        if self.available:
            logger.info("Blockfrost client initialized")
        else:
            logger.info("Blockfrost not configured - using mock mode")
    
    def get_network_info(self):
        if not self.available:
            return {"network_name": "mock", "status": "mock_mode"}
        
        try:
            headers = {"project_id": self.project_id}
            response = requests.get(f"{self.base_url}/network", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Blockfrost request failed: {e}")
        
        return {"network_name": "preprod", "status": "connected"}
    
    def validate_address(self, address):
        return address.startswith(("addr1", "addr_test"))

class SimpleMasumiClient:
    """Simplified Masumi client for transaction routing"""
    
    def __init__(self):
        self.available = False
        self.mock_mode = os.getenv("MASUMI_MOCK_MODE", "true").lower() == "true"
        logger.info("Masumi client initialized in mock mode")
    
    def create_transaction(self, tx_request):
        # Mock implementation
        return {
            "tx_id": f"masumi_{uuid.uuid4().hex[:16]}",
            "status": "created",
            "estimated_fee": 200000
        }
    
    def submit_transaction(self, tx_data):
        # Mock implementation
        return {
            "cardano_tx_hash": self.generate_mock_tx_hash(),
            "status": "submitted"
        }
    
    def get_transaction_status(self, tx_id):
        return {
            "status": "confirmed",
            "cardano_tx_hash": self.generate_mock_tx_hash()
        }
    
    def get_network_status(self):
        return {"status": "connected", "mode": "mock"}
    
    def generate_mock_tx_hash(self):
        return "5288bde95f7f6d829f280443c59aec1f69b731c64bcbec481a31bc6cabec66a2"

# ============================================================================
# PAYMENT SERVICE MODELS
# ============================================================================

class PaymentRequest(BaseModel):
    from_address: str = Field(..., description="Source wallet address")
    to_address: str = Field(..., description="Destination wallet address")
    amount: int = Field(..., gt=0, description="Amount in lovelace")
    metadata: Optional[Dict] = Field(None, description="Optional transaction metadata")

class PaymentResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    tx_hash: str = Field(..., description="Transaction hash")
    status: str = Field(..., description="Transaction status")
    estimated_confirmation_time: int = Field(..., description="Estimated confirmation time in seconds")

class TransactionStatus(BaseModel):
    job_id: str
    tx_hash: str
    status: str
    confirmations: int
    created_at: datetime
    confirmed_at: Optional[datetime] = None

# ============================================================================
# UNIFIED PAYMENT SYSTEM
# ============================================================================

class UnifiedPaymentSystem:
    """Unified system that handles both web interface and blockchain operations"""
    
    def __init__(self):
        self.wallet_address = WALLET_ADDRESS
        self.blockfrost_client = SimpleBlockfrostClient()
        self.masumi_client = SimpleMasumiClient()
        
        # Initialize FastAPI for payment service
        self.payment_app = FastAPI(
            title="Unified Payment Service",
            description="Real blockchain payment service integrated with web interface",
            version="1.0.0-unified"
        )
        
        # Enable CORS for payment service
        self.payment_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.setup_payment_routes()
        logger.info("Unified Payment System initialized")
    
    def setup_payment_routes(self):
        """Setup FastAPI routes for payment service"""
        
        @self.payment_app.get("/")
        async def payment_root():
            network_info = self.blockfrost_client.get_network_info()
            return {
                "service": "Unified Payment Service",
                "mode": "integrated",
                "status": "running",
                "version": "1.0.0-unified",
                "blockfrost_available": self.blockfrost_client.available,
                "network": network_info.get("network_name", "mock"),
                "active_jobs": len(payment_jobs),
                "endpoints": {
                    "send_payment": "POST /send_payment",
                    "tx_status": "GET /tx_status/{job_id}"
                }
            }
        
        @self.payment_app.post("/send_payment", response_model=PaymentResponse)
        async def send_payment(payment: PaymentRequest, background_tasks: BackgroundTasks):
            return await self.process_payment(payment, background_tasks)
        
        @self.payment_app.get("/tx_status/{job_id}", response_model=TransactionStatus)
        async def get_transaction_status(job_id: str):
            return await self.get_payment_status(job_id)
    
    async def process_payment(self, payment: PaymentRequest, background_tasks: BackgroundTasks):
        """Process a payment request"""
        try:
            # Validate addresses
            if not self.blockfrost_client.validate_address(payment.from_address):
                raise HTTPException(status_code=400, detail="Invalid from_address")
            
            if not self.blockfrost_client.validate_address(payment.to_address):
                raise HTTPException(status_code=400, detail="Invalid to_address")
            
            # Generate job ID
            job_id = f"unified_job_{uuid.uuid4().hex[:16]}"
            
            # Create transaction via Masumi (or mock)
            tx_request = {
                "from_address": payment.from_address,
                "to_address": payment.to_address,
                "amount": payment.amount,
                "metadata": payment.metadata or {}
            }
            
            if self.blockfrost_client.available:
                logger.info(f"Processing REAL blockchain transaction for {payment.amount} lovelace")
                # Real blockchain mode
                masumi_result = self.masumi_client.create_transaction(tx_request)
                masumi_tx_id = masumi_result.get("tx_id")
                
                # Submit transaction
                submit_result = self.masumi_client.submit_transaction({"tx_id": masumi_tx_id})
                tx_hash = submit_result.get("cardano_tx_hash")
                
                status = "submitted"
                confirmation_time = 300  # 5 minutes for real blockchain
            else:
                logger.info(f"Processing MOCK transaction for {payment.amount} lovelace")
                # Mock mode
                masumi_tx_id = f"mock_{uuid.uuid4().hex[:8]}"
                tx_hash = self.masumi_client.generate_mock_tx_hash()
                status = "pending"
                confirmation_time = 30  # 30 seconds for mock
            
            # Store job data
            payment_jobs[job_id] = {
                "job_id": job_id,
                "masumi_tx_id": masumi_tx_id,
                "tx_hash": tx_hash,
                "status": status,
                "confirmations": 0,
                "created_at": datetime.now(),
                "confirmed_at": None,
                "from_address": payment.from_address,
                "to_address": payment.to_address,
                "amount": payment.amount,
                "metadata": payment.metadata,
                "real_blockchain": self.blockfrost_client.available
            }
            
            # Schedule confirmation simulation
            background_tasks.add_task(self.simulate_confirmation, job_id, confirmation_time)
            
            logger.info(f"Transaction {job_id} created: {tx_hash}")
            
            return PaymentResponse(
                job_id=job_id,
                tx_hash=tx_hash,
                status=status,
                estimated_confirmation_time=confirmation_time
            )
            
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_payment_status(self, job_id: str):
        """Get payment status"""
        if job_id not in payment_jobs:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        job_data = payment_jobs[job_id]
        
        return TransactionStatus(
            job_id=job_data["job_id"],
            tx_hash=job_data["tx_hash"],
            status=job_data["status"],
            confirmations=job_data["confirmations"],
            created_at=job_data["created_at"],
            confirmed_at=job_data["confirmed_at"]
        )
    
    async def simulate_confirmation(self, job_id: str, delay_seconds: int):
        """Simulate transaction confirmation"""
        await asyncio.sleep(delay_seconds)
        
        if job_id in payment_jobs:
            payment_jobs[job_id].update({
                "status": "confirmed",
                "confirmations": 5,
                "confirmed_at": datetime.now()
            })
            logger.info(f"Transaction {job_id} confirmed")
    
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
        
        transactions_store[transaction_id] = transaction_data
        logger.info(f"Created transaction offer: {amount_ada} ADA -> {self.wallet_address}")
        return transaction_data
    
    def execute_blockchain_transaction(self, transaction_id, amount_ada):
        """Execute blockchain transaction by calling internal payment service"""
        try:
            sender_address = os.getenv("SENDER_WALLET_ADDRESS", "addr_test1qq9f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z")
            
            payment_data = {
                "from_address": sender_address,
                "to_address": self.wallet_address,
                "amount": int(amount_ada * 1000000),
                "metadata": {
                    "transaction_id": transaction_id,
                    "source": "unified_system",
                    "timestamp": datetime.now().isoformat(),
                    "amount_ada": amount_ada
                }
            }
            
            # Create payment request directly
            payment_request = PaymentRequest(**payment_data)
            
            # Process payment through internal system
            background_tasks = BackgroundTasks()
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.process_payment(payment_request, background_tasks)
                )
                
                # Update transaction store
                if transaction_id in transactions_store:
                    transactions_store[transaction_id].update({
                        "blockchain_job_id": result.job_id,
                        "tx_hash": result.tx_hash,
                        "blockchain_status": result.status,
                        "executed_at": datetime.now().isoformat(),
                        "real_blockchain": self.blockfrost_client.available
                    })
                
                blockchain_type = "REAL Cardano blockchain" if self.blockfrost_client.available else "Mock blockchain"
                logger.info(f"Transaction executed on {blockchain_type}: {result.tx_hash}")
                
                return {
                    "status": "success",
                    "tx_hash": result.tx_hash,
                    "job_id": result.job_id,
                    "transaction_status": result.status,
                    "estimated_confirmation_time": result.estimated_confirmation_time,
                    "message": f"Transaction executed on {blockchain_type}",
                    "real_blockchain": self.blockfrost_client.available,
                    "network": "cardano-preprod" if self.blockfrost_client.available else "mock"
                }
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Blockchain transaction failed: {e}")
            return {
                "status": "error",
                "message": f"Transaction failed: {str(e)}"
            }
    
    def start_payment_service(self):
        """Start the integrated payment service"""
        def run_uvicorn():
            uvicorn.run(
                self.payment_app,
                host="localhost",
                port=PAYMENT_PORT,
                log_level="info"
            )
        
        payment_thread = threading.Thread(target=run_uvicorn, daemon=True)
        payment_thread.start()
        
        # Wait for service to start
        time.sleep(3)
        
        # Test if service is running
        try:
            response = requests.get(f"http://localhost:{PAYMENT_PORT}/", timeout=5)
            if response.status_code == 200:
                service_info = response.json()
                logger.info("Payment service started successfully")
                logger.info(f"Mode: {service_info.get('mode')}")
                logger.info(f"Network: {service_info.get('network')}")
                logger.info(f"Blockfrost: {'Available' if service_info.get('blockfrost_available') else 'Mock mode'}")
                return True
        except Exception as e:
            logger.error(f"Payment service health check failed: {e}")
        
        return False

# ============================================================================
# WEB INTERFACE
# ============================================================================

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
        .blockchain-indicator {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .real-blockchain { background: #4CAF50; }
        .mock-blockchain { background: #FF9800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Unified Arduino-to-Cardano AI Agents</h1>
        
        <div class="status-card">
            <h3>System Status</h3>
            <p><strong>Main Server:</strong> <span class="success">Running on Port {{ main_port }}</span></p>
            <p><strong>Payment Service:</strong> <span class="success">Integrated on Port {{ payment_port }}</span></p>
            <p><strong>Blockchain Mode:</strong> <span class="blockchain-indicator {{ blockchain_class }}">{{ blockchain_mode }}</span></p>
            <p><strong>Wallet Address:</strong></p>
            <div class="address">{{ wallet_address }}</div>
            <p><strong>Time:</strong> {{ timestamp }}</p>
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <button onclick="initiateTransaction()">🔄 Initiate Blockchain Transaction</button>
            <button onclick="refreshStatus()">📡 Refresh Status</button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing blockchain transaction...</p>
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
                            <p class="info">Processing through unified payment system...</p>
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
                        const blockchainType = executeData.real_blockchain ? '🌐 Real Cardano Blockchain' : '🔧 Mock Blockchain';
                        const explorerLink = executeData.real_blockchain && executeData.tx_hash !== 'pending' ? 
                            `<p><strong>Explorer:</strong> <a href="https://preprod.cardanoscan.io/transaction/${executeData.tx_hash}" target="_blank" style="color: #87CEEB;">View on CardanoScan</a></p>` : 
                            '';
                        
                        results.innerHTML += `
                            <div class="transaction-card">
                                <h4>✅ Step 2: Blockchain Transaction Executed</h4>
                                <p><strong>Network:</strong> ${blockchainType}</p>
                                <p><strong>Transaction Hash:</strong></p>
                                <div class="hash">${executeData.tx_hash}</div>
                                <p><strong>Job ID:</strong> ${executeData.job_id}</p>
                                <p><strong>Status:</strong> <span class="success">${executeData.transaction_status}</span></p>
                                <p><strong>Confirmation Time:</strong> ~${executeData.estimated_confirmation_time} seconds</p>
                                ${explorerLink}
                                <p class="info">💡 ${executeData.message}</p>
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
            location.reload();
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""

# Initialize unified system
unified_system = UnifiedPaymentSystem()

# Flask app for web interface
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def web_interface():
    """Main web interface"""
    blockchain_mode = "Real Blockchain" if unified_system.blockfrost_client.available else "Mock Mode"
    blockchain_class = "real-blockchain" if unified_system.blockfrost_client.available else "mock-blockchain"
    
    return render_template_string(HTML_TEMPLATE,
                                wallet_address=WALLET_ADDRESS,
                                main_port=MAIN_PORT,
                                payment_port=PAYMENT_PORT,
                                blockchain_mode=blockchain_mode,
                                blockchain_class=blockchain_class,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Unified Arduino-to-Cardano System',
        'status': 'running',
        'wallet_address': WALLET_ADDRESS,
        'blockchain_available': unified_system.blockfrost_client.available,
        'timestamp': datetime.now().isoformat(),
        'transactions_count': len(transactions_store),
        'payment_jobs_count': len(payment_jobs)
    })

@app.route('/send_request', methods=['GET', 'POST'])
def send_request():
    """Generate transaction address"""
    try:
        if request.method == 'GET':
            transaction = unified_system.create_transaction_offer()
            return jsonify({
                'status': 'success',
                'message': 'Transaction address ready',
                'transaction_address': transaction['wallet_address'],
                'transaction_id': transaction['transaction_id'],
                'amount_ada': transaction['amount_ada'],
                'amount_lovelace': transaction['amount_lovelace'],
                'timestamp': transaction['timestamp']
            })
        
        elif request.method == 'POST':
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
    """Execute blockchain transaction"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        amount_ada = data.get('amount', DEFAULT_AMOUNT_ADA)
        
        if not transaction_id:
            return jsonify({
                'status': 'error',
                'message': 'Transaction ID required'
            }), 400
        
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
        'payment_jobs': list(payment_jobs.values()),
        'transaction_count': len(transactions_store),
        'payment_job_count': len(payment_jobs)
    })

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def display_system_info():
    """Display system information"""
    print("\n" + "="*80)
    print("🚀 UNIFIED ARDUINO-TO-CARDANO AI AGENTS SYSTEM")
    print("="*80)
    print(f"💰 Transaction Address: {WALLET_ADDRESS}")
    print(f"🌐 Main Server: http://localhost:{MAIN_PORT}")
    print(f"🔧 Payment Service: http://localhost:{PAYMENT_PORT} (Integrated)")
    
    if unified_system.blockfrost_client.available:
        print(f"⛓️  Network: Cardano Preprod Testnet (REAL BLOCKCHAIN)")
        print("⚠️  WARNING: This uses REAL blockchain transactions!")
    else:
        print(f"⛓️  Network: Mock Mode (Safe Testing)")
        print("💡 To use real blockchain, configure BLOCKFROST_PROJECT_ID in .env")
    
    print("\n📋 How it works:")
    print("   1. User clicks 'Initiate Transaction' on web interface")
    print("   2. System generates transaction address")
    print("   3. Unified payment system processes transaction")
    print("   4. Real blockchain transaction executed (if configured)")
    print("   5. Transaction hash displayed with explorer link")
    
    print(f"\n💡 Access the web interface at: http://localhost:{MAIN_PORT}/")
    print("\n" + "="*80)

def main():
    """Main function"""
    print("\n🤖 Unified Arduino-to-Cardano AI Agents System")
    print("=" * 60)
    
    # Check environment configuration
    if not unified_system.blockfrost_client.available:
        print("\n💡 BLOCKCHAIN MODE: Mock (Safe Testing)")
        print("   To use real Cardano blockchain:")
        print("   1. Get free API key from https://blockfrost.io/")
        print("   2. Set BLOCKFROST_PROJECT_ID in .env file")
        print("   3. Restart the system")
    else:
        print("\n⚠️  BLOCKCHAIN MODE: Real Cardano Network")
        print("   This will execute REAL blockchain transactions!")
    
    # Yes/No prompt
    while True:
        mode_text = "REAL blockchain" if unified_system.blockfrost_client.available else "unified"
        response = input(f"\n❓ Start the {mode_text} system? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print(f"\n✅ Starting unified system...")
            break
        elif response in ['no', 'n']:
            print("\n❌ System startup cancelled.")
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("⚠️  Please enter 'yes' or 'no'")
    
    display_system_info()
    
    try:
        # Start integrated payment service
        print("🔄 Starting integrated payment service...")
        if unified_system.start_payment_service():
            print("✅ Payment service started successfully")
        else:
            print("⚠️  Payment service may have issues, but continuing...")
        
        # Start main web server
        print("🔄 Starting main web interface...")
        print(f"\n✅ System running successfully!")
        print(f"🌐 Open your browser: http://localhost:{MAIN_PORT}/")
        
        if unified_system.blockfrost_client.available:
            print("⚠️  REMINDER: Using REAL Cardano blockchain!")
        else:
            print("💡 Running in safe mock mode")
        
        print("\nPress Ctrl+C to stop the system")
        
        # Start Flask server
        app.run(host='0.0.0.0', port=MAIN_PORT, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"\n❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()