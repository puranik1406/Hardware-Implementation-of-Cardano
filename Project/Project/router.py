#!/usr/bin/env python3
"""
Router and Serial Bridge for Arduino-to-Cardano AI Agents
Acts as the traffic controller between Arduino A, Agent A, Agent B, and blockchain service.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import jsonschema
from jsonschema import validate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# In-memory stores
offers_store: Dict[str, dict] = {}
responses_store: Dict[str, dict] = {}
transaction_store: Dict[str, dict] = {}

# Load JSON schemas
def load_schema(schema_file: str) -> dict:
    """Load JSON schema from file"""
    try:
        with open(f'schemas/{schema_file}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Schema file {schema_file} not found")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in schema file {schema_file}: {e}")
        return {}

offer_schema = load_schema('offer.json')
response_schema = load_schema('response.json')

class OfferManager:
    """Manages offer lifecycle and state"""
    
    def __init__(self):
        self.offers = offers_store
        self.responses = responses_store
        self.transactions = transaction_store
    
    def create_offer(self, offer_data: dict) -> str:
        """Create a new offer and return offer_id"""
        offer_id = str(uuid.uuid4())
        
        # Add metadata
        offer_data['offer_id'] = offer_id
        offer_data['status'] = 'pending'
        offer_data['created_at'] = datetime.now(timezone.utc).isoformat()
        
        # Store offer
        self.offers[offer_id] = offer_data
        
        logger.info(f"Created offer {offer_id}: {offer_data['amount']} {offer_data['currency']}")
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
                self.offers[offer_id]['metadata'] = metadata
            logger.info(f"Updated offer {offer_id} status to {status}")
    
    def add_response(self, response_data: dict) -> str:
        """Add agent response"""
        response_id = str(uuid.uuid4())
        response_data['response_id'] = response_id
        response_data['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        self.responses[response_id] = response_data
        
        # Update offer status based on response
        offer_id = response_data.get('offer_id')
        if offer_id and offer_id in self.offers:
            self.update_offer_status(offer_id, response_data['status'])
        
        logger.info(f"Added response {response_id} for offer {offer_id}")
        return response_id
    
    def add_transaction(self, offer_id: str, tx_hash: str, block_height: int = None):
        """Add transaction details"""
        transaction_data = {
            'offer_id': offer_id,
            'tx_hash': tx_hash,
            'block_height': block_height,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.transactions[tx_hash] = transaction_data
        self.update_offer_status(offer_id, 'completed', {'tx_hash': tx_hash})
        
        logger.info(f"Added transaction {tx_hash} for offer {offer_id}")

# Initialize offer manager
offer_manager = OfferManager()

def validate_json(data: dict, schema: dict, schema_name: str) -> tuple[bool, str]:
    """Validate JSON data against schema"""
    try:
        validate(instance=data, schema=schema)
        return True, ""
    except jsonschema.ValidationError as e:
        error_msg = f"Validation error in {schema_name}: {e.message}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error validating {schema_name}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'offers_count': len(offers_store),
        'responses_count': len(responses_store)
    })

@app.route('/send_offer', methods=['POST'])
def send_offer():
    """Receive payment offer from Agent A"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate offer schema (excluding offer_id which is generated by router)
        if offer_schema:
            # Create a copy without offer_id for validation
            validation_data = data.copy()
            validation_data.pop('offer_id', None)  # Remove offer_id if present
            
            # Create a modified schema without offer_id requirement
            validation_schema = offer_schema.copy()
            if 'required' in validation_schema:
                validation_schema['required'] = [req for req in validation_schema['required'] if req != 'offer_id']
            
            is_valid, error_msg = validate_json(validation_data, validation_schema, 'offer')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # Create offer
        offer_id = offer_manager.create_offer(data)
        
        # Log the offer
        logger.info(f"Received offer from {data.get('from_agent')} to {data.get('to_agent')}: {data.get('amount')} {data.get('currency')}")
        
        # Forward to Agent B (mock for now)
        forward_to_agent_b(offer_id, data)
        
        return jsonify({
            'status': 'success',
            'offer_id': offer_id,
            'message': 'Offer received and forwarded'
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing offer: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/status/<offer_id>', methods=['GET'])
def get_offer_status(offer_id: str):
    """Get offer status by ID"""
    try:
        offer = offer_manager.get_offer(offer_id)
        if not offer:
            return jsonify({'error': 'Offer not found'}), 404
        
        # Get related responses
        related_responses = [
            resp for resp in responses_store.values() 
            if resp.get('offer_id') == offer_id
        ]
        
        # Get transaction if exists
        transaction = None
        if offer.get('status') == 'completed':
            tx_hash = offer.get('metadata', {}).get('tx_hash')
            if tx_hash:
                transaction = transaction_store.get(tx_hash)
        
        return jsonify({
            'offer': offer,
            'responses': related_responses,
            'transaction': transaction
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting offer status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/mock_agent_b', methods=['POST'])
def mock_agent_b():
    """Mock Agent B response endpoint for testing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate response schema (excluding response_id and timestamp which are generated by router)
        if response_schema:
            # Create a copy without generated fields for validation
            validation_data = data.copy()
            validation_data.pop('response_id', None)  # Remove response_id if present
            validation_data.pop('timestamp', None)    # Remove timestamp if present
            
            # Create a modified schema without generated fields requirement
            validation_schema = response_schema.copy()
            if 'required' in validation_schema:
                validation_schema['required'] = [req for req in validation_schema['required'] 
                                               if req not in ['response_id', 'timestamp']]
            
            is_valid, error_msg = validate_json(validation_data, validation_schema, 'response')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # Add response
        response_id = offer_manager.add_response(data)
        
        # If accepted, simulate transaction
        if data.get('status') == 'accepted':
            simulate_transaction(data.get('offer_id'))
        
        return jsonify({
            'status': 'success',
            'response_id': response_id,
            'message': 'Response processed'
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing mock response: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/offers', methods=['GET'])
def list_offers():
    """List all offers (for debugging)"""
    return jsonify({
        'offers': list(offers_store.values()),
        'count': len(offers_store)
    }), 200

def forward_to_agent_b(offer_id: str, offer_data: dict):
    """Forward offer to Agent B (mock implementation)"""
    logger.info(f"Forwarding offer {offer_id} to Agent B")
    
    # In a real implementation, this would make an HTTP request to Agent B
    # For now, we'll simulate Agent B accepting the offer after a delay
    import threading
    import time
    
    def simulate_agent_b_response():
        time.sleep(2)  # Simulate processing time
        
        # Create mock response
        mock_response = {
            'offer_id': offer_id,
            'from_agent': 'agent_b',
            'status': 'accepted',
            'message': 'Mock Agent B accepted the offer'
        }
        
        # Add response
        offer_manager.add_response(mock_response)
        
        # Simulate transaction
        simulate_transaction(offer_id)
    
    # Start simulation in background thread
    thread = threading.Thread(target=simulate_agent_b_response)
    thread.daemon = True
    thread.start()

def simulate_transaction(offer_id: str):
    """Simulate blockchain transaction"""
    # Generate mock transaction hash
    tx_hash = f"mock_tx_{uuid.uuid4().hex[:16]}"
    
    # Add transaction
    offer_manager.add_transaction(offer_id, tx_hash, 12345)
    
    logger.info(f"Simulated transaction {tx_hash} for offer {offer_id}")
    
    # In a real implementation, this would trigger Arduino B notification
    notify_arduino_b(offer_id, tx_hash)

def notify_arduino_b(offer_id: str, tx_hash: str):
    """Notify Arduino B of transaction completion"""
    logger.info(f"Notifying Arduino B: Offer {offer_id} completed with tx {tx_hash}")
    
    # In a real implementation, this would send data to Arduino B via serial
    # For now, just log the notification
    notification = {
        'offer_id': offer_id,
        'tx_hash': tx_hash,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'completed'
    }
    
    logger.info(f"Arduino B notification: {json.dumps(notification)}")

if __name__ == '__main__':
    logger.info("Starting Router and Serial Bridge...")
    logger.info("Available endpoints:")
    logger.info("  POST /send_offer - Receive offers from Agent A")
    logger.info("  GET /status/{offer_id} - Get offer status")
    logger.info("  POST /mock_agent_b - Mock Agent B responses")
    logger.info("  GET /offers - List all offers")
    logger.info("  GET /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
