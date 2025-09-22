"""
Agent B - Seller Logic Service
Seller agent that evaluates offers and manages transaction confirmations
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, Optional

import requests
import serial
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
COST_THRESHOLD = float(os.getenv("COST_THRESHOLD", "100.0"))
PAYMENT_SERVICE_URL = f"http://localhost:{os.getenv('PAYMENT_SERVICE_PORT', '8000')}"
ROUTER_URL = f"http://localhost:{os.getenv('ROUTER_PORT', '8003')}"
ARDUINO_PORT = os.getenv("ARDUINO_B_PORT", "COM4")
ARDUINO_BAUD_RATE = int(os.getenv("ARDUINO_BAUD_RATE", "9600"))

class AgentB:
    """Seller agent for managing offers and transactions"""
    
    def __init__(self):
        self.cost_threshold = COST_THRESHOLD
        self.pending_transactions = {}
        self.arduino_connection = None
        self.init_arduino()
        
    def init_arduino(self):
        """Initialize Arduino connection"""
        try:
            self.arduino_connection = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD_RATE, timeout=1)
            logger.info(f"Arduino B connected on {ARDUINO_PORT}")
        except Exception as e:
            logger.warning(f"Could not connect to Arduino B: {e}")
            self.arduino_connection = None
    
    def send_to_arduino(self, message: str):
        """Send message to Arduino display"""
        try:
            if self.arduino_connection and self.arduino_connection.is_open:
                self.arduino_connection.write(f"{message}\n".encode())
                logger.info(f"Sent to Arduino B: {message}")
            else:
                logger.info(f"Arduino B (simulated): {message}")
        except Exception as e:
            logger.error(f"Error sending to Arduino B: {e}")
    
    def make_decision(self, offer_data: dict) -> dict:
        """
        Evaluate offer and make accept/reject decision
        """
        try:
            amount = float(offer_data.get('amount', 0))
            product = offer_data.get('product', 'Unknown Product')
            offer_id = offer_data.get('offer_id', 'unknown')
            
            logger.info(f"Evaluating offer {offer_id}: {amount} ADA for {product}")
            
            # Decision logic
            if amount >= self.cost_threshold:
                decision = "accept"
                response_message = f"✅ ACCEPTED: {amount} ADA for {product}"
                logger.info(f"✅ ACCEPTED: Offer {offer_id}")
            else:
                decision = "reject"
                response_message = f"❌ REJECTED: {amount} ADA too low (min: {self.cost_threshold})"
                logger.info(f"❌ REJECTED: Offer {offer_id}")
            
            return {
                "decision": decision,
                "amount": amount,
                "product": product,
                "offer_id": offer_id,
                "reason": response_message,
                "timestamp": datetime.now().isoformat(),
                "agent_id": "agent_b"
            }
            
        except Exception as e:
            logger.error(f"Error in decision logic: {e}")
            return {
                "decision": "reject",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "agent_id": "agent_b"
            }
    
    def initiate_payment(self, offer_data: dict) -> str:
        """
        Initiate payment request to blockchain service
        """
        try:
            payment_request = {
                "from_address": os.getenv("DEFAULT_WALLET_ADDRESS"),
                "to_address": offer_data.get("buyer_address", os.getenv("DEFAULT_WALLET_ADDRESS")),
                "amount": int(float(offer_data.get('amount', 0)) * 1000000),  # Convert ADA to lovelace
                "metadata": {
                    "agent": "agent_b",
                    "offer_id": offer_data.get("offer_id"),
                    "product": offer_data.get("product"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info(f"Initiating payment: {payment_request}")
            
            # Send to payment service
            response = requests.post(
                f"{PAYMENT_SERVICE_URL}/send_payment",
                json=payment_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                tx_hash = result.get("transaction_hash", f"mock_tx_{int(time.time())}")
                
                # Store pending transaction
                self.pending_transactions[tx_hash] = {
                    "job_id": job_id,
                    "status": "pending",
                    "amount": offer_data.get('amount'),
                    "product": offer_data.get('product'),
                    "offer_id": offer_data.get("offer_id"),
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Payment initiated: {tx_hash}")
                return tx_hash
            else:
                logger.error(f"Payment service error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            return None
    
    def check_transaction_status(self, tx_hash: str) -> dict:
        """
        Check status of a transaction
        """
        try:
            if tx_hash not in self.pending_transactions:
                return {"status": "not_found"}
            
            transaction = self.pending_transactions[tx_hash]
            job_id = transaction.get("job_id")
            
            if job_id:
                # Check with payment service
                response = requests.get(
                    f"{PAYMENT_SERVICE_URL}/job_status/{job_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    job_status = response.json()
                    status = job_status.get("status", "pending")
                    
                    # Update transaction status
                    transaction["status"] = status
                    transaction["updated_at"] = datetime.now().isoformat()
                    
                    if status == "completed":
                        transaction["tx_hash"] = job_status.get("transaction_hash", tx_hash)
                        self.handle_confirmed_transaction(tx_hash, transaction)
                    
                    return transaction
            
            # Fallback for mock transactions
            if tx_hash.startswith("mock_tx_"):
                # Simulate confirmation after some time
                created_time = transaction.get("timestamp")
                if created_time:
                    created_datetime = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    elapsed = (datetime.now() - created_datetime).total_seconds()
                    
                    if elapsed > 10:  # Confirm after 10 seconds
                        transaction["status"] = "completed"
                        self.handle_confirmed_transaction(tx_hash, transaction)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return {"status": "error", "error": str(e)}
    
    def handle_confirmed_transaction(self, tx_hash: str, transaction: dict):
        """
        Handle confirmed transaction - send to Arduino display
        """
        try:
            amount = transaction.get("amount", 0)
            product = transaction.get("product", "Unknown")
            
            # Format message for Arduino
            arduino_message = f"{tx_hash}:CONFIRMED"
            self.send_to_arduino(arduino_message)
            
            # Log success
            logger.info(f"🎉 TRANSACTION CONFIRMED: {tx_hash} - {amount} ADA for {product}")
            
            # Notify router of confirmation
            self.notify_router_confirmation(tx_hash, transaction)
            
        except Exception as e:
            logger.error(f"Error handling confirmed transaction: {e}")
    
    def notify_router_confirmation(self, tx_hash: str, transaction: dict):
        """
        Notify router of transaction confirmation
        """
        try:
            confirmation_data = {
                "tx_hash": tx_hash,
                "status": "confirmed",
                "amount": transaction.get("amount"),
                "product": transaction.get("product"),
                "offer_id": transaction.get("offer_id"),
                "agent_id": "agent_b",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{ROUTER_URL}/transaction_confirmed",
                json=confirmation_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Router notified of confirmation: {tx_hash}")
            else:
                logger.error(f"Failed to notify router: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error notifying router: {e}")

# Initialize Agent B
agent_b = AgentB()

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "Agent B - Seller Logic",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "cost_threshold": agent_b.cost_threshold,
        "arduino_connected": agent_b.arduino_connection is not None
    })

@app.route('/respond', methods=['POST'])
def respond_to_offer():
    """
    Receive and respond to offers from router
    """
    try:
        offer_data = request.get_json()
        logger.info(f"Received offer: {offer_data}")
        
        # Make decision
        decision = agent_b.make_decision(offer_data)
        
        # If accepted, initiate payment
        if decision["decision"] == "accept":
            tx_hash = agent_b.initiate_payment(offer_data)
            decision["tx_hash"] = tx_hash
            
            if tx_hash:
                # Start monitoring transaction in background
                threading.Thread(
                    target=monitor_transaction,
                    args=(tx_hash,),
                    daemon=True
                ).start()
        
        return jsonify(decision)
        
    except Exception as e:
        logger.error(f"Error responding to offer: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transaction_status/<tx_hash>')
def get_transaction_status(tx_hash):
    """
    Get status of a specific transaction
    """
    try:
        status = agent_b.check_transaction_status(tx_hash)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting transaction status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transactions')
def get_all_transactions():
    """
    Get all pending transactions
    """
    return jsonify({"transactions": agent_b.pending_transactions})

@app.route('/confirm_tx', methods=['POST'])
def confirm_transaction():
    """
    Manual transaction confirmation endpoint
    """
    try:
        data = request.get_json()
        tx_hash = data.get("tx_hash")
        
        if tx_hash in agent_b.pending_transactions:
            transaction = agent_b.pending_transactions[tx_hash]
            transaction["status"] = "completed"
            agent_b.handle_confirmed_transaction(tx_hash, transaction)
            
            return jsonify({"status": "confirmed", "tx_hash": tx_hash})
        else:
            return jsonify({"error": "Transaction not found"}), 404
            
    except Exception as e:
        logger.error(f"Error confirming transaction: {e}")
        return jsonify({"error": str(e)}), 500

def monitor_transaction(tx_hash: str):
    """
    Background task to monitor transaction status
    """
    max_attempts = 30  # 5 minutes with 10-second intervals
    attempt = 0
    
    while attempt < max_attempts:
        try:
            status = agent_b.check_transaction_status(tx_hash)
            
            if status.get("status") == "completed":
                logger.info(f"Transaction {tx_hash} confirmed after {attempt} attempts")
                break
            elif status.get("status") == "failed":
                logger.error(f"Transaction {tx_hash} failed")
                break
            
            time.sleep(10)  # Wait 10 seconds before next check
            attempt += 1
            
        except Exception as e:
            logger.error(f"Error monitoring transaction {tx_hash}: {e}")
            break
    
    if attempt >= max_attempts:
        logger.warning(f"Transaction {tx_hash} monitoring timed out")

if __name__ == "__main__":
    port = int(os.getenv("AGENT_B_PORT", "8002"))
    logger.info(f"Starting Agent B on port {port}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("DEBUG", "true").lower() == "true"
    )