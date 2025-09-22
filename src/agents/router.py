"""
Router Service - Traffic Controller
Coordinates communication between Agent A, Agent B, and Arduino devices
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

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
AGENT_A_URL = f"http://localhost:{os.getenv('AGENT_A_PORT', '8001')}"
AGENT_B_URL = f"http://localhost:{os.getenv('AGENT_B_PORT', '8002')}"
PAYMENT_SERVICE_URL = f"http://localhost:{os.getenv('PAYMENT_SERVICE_PORT', '8000')}"

# In-memory stores
offers_store: Dict[str, dict] = {}
responses_store: Dict[str, dict] = {}
transaction_store: Dict[str, dict] = {}

class RouterService:
    """Main router service for coordinating agent communications"""
    
    def __init__(self):
        self.offers = offers_store
        self.responses = responses_store
        self.transactions = transaction_store
        
    def create_offer(self, offer_data: dict) -> str:
        """Create and store a new offer"""
        offer_id = offer_data.get('offer_id') or str(uuid.uuid4())
        
        # Add metadata
        offer_data['offer_id'] = offer_id
        offer_data['status'] = 'pending'
        offer_data['created_at'] = datetime.now(timezone.utc).isoformat()
        offer_data['router_timestamp'] = datetime.now().isoformat()
        
        # Store offer
        self.offers[offer_id] = offer_data
        
        logger.info(f"Created offer {offer_id}: {offer_data.get('amount')} ADA for {offer_data.get('product')}")
        return offer_id
    
    def get_offer(self, offer_id: str) -> Optional[dict]:
        """Get offer by ID"""
        return self.offers.get(offer_id)
    
    def update_offer_status(self, offer_id: str, status: str, metadata: dict = None):
        """Update offer status"""
        if offer_id in self.offers:
            self.offers[offer_id]['status'] = status
            self.offers[offer_id]['updated_at'] = datetime.now(timezone.utc).isoformat()
            if metadata:
                self.offers[offer_id].update(metadata)
            logger.info(f"Updated offer {offer_id} status to {status}")
    
    def route_offer_to_agent_b(self, offer_data: dict) -> dict:
        """Route offer to Agent B for evaluation"""
        try:
            logger.info(f"Routing offer {offer_data.get('offer_id')} to Agent B")
            
            response = requests.post(
                f"{AGENT_B_URL}/respond",
                json=offer_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Store response
                response_id = str(uuid.uuid4())
                response_data['response_id'] = response_id
                response_data['timestamp'] = datetime.now().isoformat()
                self.responses[response_id] = response_data
                
                # Update offer status
                offer_id = offer_data.get('offer_id')
                if offer_id:
                    self.update_offer_status(
                        offer_id, 
                        response_data.get('decision', 'unknown'),
                        {'agent_b_response': response_data}
                    )
                
                logger.info(f"Agent B responded: {response_data.get('decision')} for offer {offer_id}")
                return response_data
            else:
                logger.error(f"Agent B error: {response.status_code}")
                return {"decision": "error", "error": f"Agent B returned {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error routing to Agent B: {e}")
            return {"decision": "error", "error": str(e)}
    
    def notify_agent_a_response(self, offer_id: str, response_data: dict):
        """Notify Agent A of Agent B's response"""
        try:
            logger.info(f"Notifying Agent A of response for offer {offer_id}")
            
            evaluation_request = {
                "offer_id": offer_id,
                "counter_offer": response_data if response_data.get('decision') == 'counter_offer' else None,
                "context": {"agent_b_response": response_data}
            }
            
            response = requests.post(
                f"{AGENT_A_URL}/evaluate_response",
                json=evaluation_request,
                timeout=30
            )
            
            if response.status_code == 200:
                evaluation = response.json()
                logger.info(f"Agent A evaluation: {evaluation.get('status')} for offer {offer_id}")
                
                # Update offer with final status
                self.update_offer_status(
                    offer_id,
                    evaluation.get('status', 'unknown'),
                    {'agent_a_evaluation': evaluation}
                )
                
                return evaluation
            else:
                logger.error(f"Agent A evaluation error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error notifying Agent A: {e}")
            return None
    
    def record_transaction(self, tx_data: dict):
        """Record transaction details"""
        tx_id = tx_data.get('tx_hash') or str(uuid.uuid4())
        tx_data['tx_id'] = tx_id
        tx_data['recorded_at'] = datetime.now().isoformat()
        
        self.transactions[tx_id] = tx_data
        logger.info(f"Recorded transaction: {tx_id}")

# Initialize router service
router_service = RouterService()

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "Router - Traffic Controller",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "agents": {
            "agent_a_url": AGENT_A_URL,
            "agent_b_url": AGENT_B_URL,
            "payment_service_url": PAYMENT_SERVICE_URL
        },
        "stats": {
            "active_offers": len(router_service.offers),
            "responses": len(router_service.responses),
            "transactions": len(router_service.transactions)
        }
    })

@app.route('/receive_offer', methods=['POST'])
def receive_offer():
    """
    Receive offer from Agent A and route to Agent B
    """
    try:
        offer_data = request.get_json()
        logger.info(f"Received offer from Agent A: {offer_data}")
        
        # Validate offer data
        required_fields = ['offer_id', 'amount', 'agent_id']
        for field in required_fields:
            if field not in offer_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create offer in router
        offer_id = router_service.create_offer(offer_data)
        
        # Route to Agent B
        response_data = router_service.route_offer_to_agent_b(offer_data)
        
        # If Agent B accepts, transaction will be initiated by Agent B
        # If Agent B rejects or counters, notify Agent A
        if response_data.get('decision') in ['reject', 'counter_offer']:
            evaluation = router_service.notify_agent_a_response(offer_id, response_data)
            response_data['agent_a_evaluation'] = evaluation
        
        return jsonify({
            "status": "routed",
            "offer_id": offer_id,
            "agent_b_response": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error receiving offer: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transaction_confirmed', methods=['POST'])
def transaction_confirmed():
    """
    Receive transaction confirmation from Agent B
    """
    try:
        tx_data = request.get_json()
        logger.info(f"Transaction confirmed: {tx_data}")
        
        # Record transaction
        router_service.record_transaction(tx_data)
        
        # Update related offer status
        offer_id = tx_data.get('offer_id')
        if offer_id:
            router_service.update_offer_status(
                offer_id,
                'completed',
                {'transaction': tx_data}
            )
        
        return jsonify({
            "status": "recorded",
            "tx_hash": tx_data.get('tx_hash'),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error recording transaction confirmation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/offers')
def get_offers():
    """Get all offers"""
    return jsonify({
        "offers": list(router_service.offers.values()),
        "count": len(router_service.offers)
    })

@app.route('/offers/<offer_id>')
def get_offer(offer_id):
    """Get specific offer"""
    offer = router_service.get_offer(offer_id)
    if not offer:
        return jsonify({"error": "Offer not found"}), 404
    return jsonify(offer)

@app.route('/responses')
def get_responses():
    """Get all agent responses"""
    return jsonify({
        "responses": list(router_service.responses.values()),
        "count": len(router_service.responses)
    })

@app.route('/transactions')
def get_transactions():
    """Get all transactions"""
    return jsonify({
        "transactions": list(router_service.transactions.values()),
        "count": len(router_service.transactions)
    })

@app.route('/status')
def get_system_status():
    """Get comprehensive system status"""
    
    # Check agent connectivity
    agents_status = {}
    
    for agent_name, url in [("agent_a", AGENT_A_URL), ("agent_b", AGENT_B_URL), ("payment_service", PAYMENT_SERVICE_URL)]:
        try:
            response = requests.get(f"{url}/", timeout=5)
            agents_status[agent_name] = {
                "status": "online" if response.status_code == 200 else "error",
                "response_time": response.elapsed.total_seconds(),
                "url": url
            }
        except Exception as e:
            agents_status[agent_name] = {
                "status": "offline",
                "error": str(e),
                "url": url
            }
    
    return jsonify({
        "router_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": agents_status,
        "system_stats": {
            "total_offers": len(router_service.offers),
            "pending_offers": len([o for o in router_service.offers.values() if o.get('status') == 'pending']),
            "completed_offers": len([o for o in router_service.offers.values() if o.get('status') == 'completed']),
            "total_responses": len(router_service.responses),
            "total_transactions": len(router_service.transactions)
        }
    })

@app.route('/arduino_trigger', methods=['POST'])
def arduino_trigger():
    """
    Special endpoint for Arduino-triggered offers
    Forwards Arduino data to Agent A
    """
    try:
        arduino_data = request.get_json()
        logger.info(f"Arduino trigger received: {arduino_data}")
        
        # Forward to Agent A
        response = requests.post(
            f"{AGENT_A_URL}/arduino_trigger",
            json=arduino_data,
            timeout=30
        )
        
        if response.status_code == 200:
            agent_a_response = response.json()
            
            # If Agent A creates an offer, it will be sent back through /receive_offer
            return jsonify({
                "status": "forwarded",
                "agent_a_response": agent_a_response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": f"Agent A error: {response.status_code}"}), 500
            
    except Exception as e:
        logger.error(f"Error processing Arduino trigger: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_system():
    """Reset all stored data (for testing)"""
    router_service.offers.clear()
    router_service.responses.clear()
    router_service.transactions.clear()
    
    logger.info("System data reset")
    return jsonify({
        "status": "reset",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("ROUTER_PORT", "8003"))
    logger.info(f"Starting Router service on port {port}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("DEBUG", "true").lower() == "true"
    )