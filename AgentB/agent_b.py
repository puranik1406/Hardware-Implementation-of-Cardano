#!/usr/bin/env python3
"""
Agent B - Seller Logic
Responsible for listening for offers, deciding whether to accept,
and displaying transaction hash when payment is confirmed.
"""

import json
import time
import requests
import threading
from flask import Flask, request, jsonify
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class AgentB:
    def __init__(self):
        self.cost_threshold = 100.0  # Minimum acceptable offer amount
        self.blockchain_service_url = "http://localhost:5002"  # Blockchain Service URL
        self.arduino_serial_port = "COM3"  # Arduino serial port (Windows)
        self.pending_transactions = {}  # Track pending transactions
        
    def make_decision(self, offer_data):
        """
        Rule-based decision logic for offers
        Accept if amount > cost_threshold
        """
        try:
            amount = float(offer_data.get('amount', 0))
            product = offer_data.get('product', '')
            
            logger.info(f"Evaluating offer: {amount} for {product}")
            
            if amount >= self.cost_threshold:
                decision = "accept"
                logger.info(f"✅ ACCEPTED: Offer of {amount} for {product}")
            else:
                decision = "reject"
                logger.info(f"❌ REJECTED: Offer of {amount} too low (min: {self.cost_threshold})")
            
            return {
                "decision": decision,
                "amount": amount,
                "product": product,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in decision logic: {e}")
            return {
                "decision": "reject",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def send_payment_request(self, offer_data):
        """
        Send payment request to Blockchain Service
        """
        try:
            payment_data = {
                "amount": offer_data.get('amount'),
                "recipient": offer_data.get('buyer_address'),
                "product": offer_data.get('product'),
                "seller_id": "agent_b"
            }
            
            logger.info(f"Sending payment request: {payment_data}")
            
            # For now, simulate payment request (mock)
            # In real implementation, this would call the blockchain service
            mock_tx_hash = f"mock_tx_{int(time.time())}_{offer_data.get('amount', 0)}"
            
            # Store pending transaction
            self.pending_transactions[mock_tx_hash] = {
                "status": "pending",
                "amount": offer_data.get('amount'),
                "product": offer_data.get('product'),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Payment request sent, tx_hash: {mock_tx_hash}")
            return mock_tx_hash
            
        except Exception as e:
            logger.error(f"Error sending payment request: {e}")
            return None
    
    def poll_transaction_status(self, tx_hash):
        """
        Poll transaction status until confirmed
        """
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Mock implementation - simulate confirmation after 3 attempts
                if attempt >= 2:  # Simulate confirmation
                    self.pending_transactions[tx_hash]["status"] = "confirmed"
                    logger.info(f"✅ Transaction confirmed: {tx_hash}")
                    return True
                else:
                    logger.info(f"⏳ Polling transaction {tx_hash}, attempt {attempt + 1}")
                    time.sleep(2)  # Wait 2 seconds between polls
                    attempt += 1
                    
            except Exception as e:
                logger.error(f"Error polling transaction status: {e}")
                return False
        
        logger.error(f"Transaction {tx_hash} not confirmed after {max_attempts} attempts")
        return False
    
    def send_to_arduino(self, tx_hash):
        """
        Send transaction hash to Arduino B for display
        """
        try:
            # For now, just log the transaction hash
            # In real implementation, this would send via serial to Arduino
            logger.info(f"📱 Sending to Arduino B: ✅ CONFIRMED: {tx_hash}")
            
            # Simulate Arduino display
            print(f"Arduino B Display: ✅ CONFIRMED: {tx_hash}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending to Arduino: {e}")
            return False

# Initialize Agent B
agent_b = AgentB()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Agent B - Seller Logic",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/respond', methods=['POST'])
def respond_to_offer():
    """
    Receive offer from Router and decide accept/reject/counter
    """
    try:
        offer_data = request.get_json()
        logger.info(f"Received offer: {offer_data}")
        
        # Make decision
        decision = agent_b.make_decision(offer_data)
        
        if decision["decision"] == "accept":
            # Send payment request
            tx_hash = agent_b.send_payment_request(offer_data)
            
            if tx_hash:
                # Start polling in background thread
                def poll_and_confirm():
                    if agent_b.poll_transaction_status(tx_hash):
                        agent_b.send_to_arduino(tx_hash)
                
                thread = threading.Thread(target=poll_and_confirm)
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "status": "accepted",
                    "tx_hash": tx_hash,
                    "message": "Payment initiated, confirmation in progress",
                    "decision": decision
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to initiate payment",
                    "decision": decision
                }), 500
        else:
            return jsonify({
                "status": decision["decision"],
                "message": f"Offer {decision['decision']}ed",
                "decision": decision
            })
            
    except Exception as e:
        logger.error(f"Error processing offer: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/confirm_tx', methods=['POST'])
def confirm_transaction():
    """
    Handle transaction confirmation from Blockchain Service
    """
    try:
        tx_data = request.get_json()
        tx_hash = tx_data.get('tx_hash')
        status = tx_data.get('status')
        
        logger.info(f"Transaction confirmation: {tx_hash} - {status}")
        
        if tx_hash in agent_b.pending_transactions:
            agent_b.pending_transactions[tx_hash]["status"] = status
            
            if status == "confirmed":
                # Send to Arduino for display
                agent_b.send_to_arduino(tx_hash)
                
                return jsonify({
                    "status": "success",
                    "message": f"Transaction {tx_hash} confirmed and sent to Arduino"
                })
            else:
                return jsonify({
                    "status": "updated",
                    "message": f"Transaction {tx_hash} status updated to {status}"
                })
        else:
            return jsonify({
                "status": "error",
                "message": f"Transaction {tx_hash} not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error confirming transaction: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """
    Get current status of Agent B
    """
    return jsonify({
        "service": "Agent B - Seller Logic",
        "cost_threshold": agent_b.cost_threshold,
        "pending_transactions": len(agent_b.pending_transactions),
        "blockchain_service_url": agent_b.blockchain_service_url,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Agent B - Seller Logic")
    logger.info(f"Cost threshold: {agent_b.cost_threshold}")
    logger.info(f"Blockchain service: {agent_b.blockchain_service_url}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
