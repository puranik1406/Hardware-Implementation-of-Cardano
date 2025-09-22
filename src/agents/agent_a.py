"""
Agent A - Buyer Logic Service
AI-powered buyer agent that creates offers and makes intelligent purchasing decisions
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent A - Buyer Logic",
    description="AI-powered buyer agent for Arduino-to-Cardano system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ROUTER_URL = f"http://localhost:{os.getenv('ROUTER_PORT', '8003')}"
PAYMENT_SERVICE_URL = f"http://localhost:{os.getenv('PAYMENT_SERVICE_PORT', '8000')}"
USE_MOCK_BEDROCK = os.getenv("USE_MOCK_BEDROCK", "true").lower() == "true"
FALLBACK_THRESHOLD = float(os.getenv("FALLBACK_THRESHOLD", "1000000"))  # 1 ADA in lovelace

# Pydantic models
class TriggerRequest(BaseModel):
    """Request model for trigger input"""
    trigger_type: str = Field(..., description="Type of trigger (arduino, manual, etc.)")
    amount: Optional[float] = Field(None, description="Suggested amount for offer")
    product: Optional[str] = Field(None, description="Product being purchased")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class OfferResponse(BaseModel):
    """Response model for offer creation"""
    status: str = Field(..., description="Status of the offer")
    amount: float = Field(..., description="Offer amount in ADA")
    offer_id: str = Field(..., description="Unique offer identifier")
    decision_reason: str = Field(..., description="Reason for the decision")
    timestamp: str = Field(..., description="Offer creation timestamp")

class DecisionRequest(BaseModel):
    """Request model for decision evaluation"""
    offer_id: str = Field(..., description="Offer ID to evaluate")
    counter_offer: Optional[Dict[str, Any]] = Field(None, description="Counter offer details")
    context: Optional[Dict[str, Any]] = Field(None, description="Decision context")

class BedrockService:
    """Mock AI service for decision making"""
    
    def __init__(self):
        self.use_mock = USE_MOCK_BEDROCK
        logger.info(f"BedrockService initialized (mock: {self.use_mock})")
    
    def create_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Create offer decision using AI logic"""
        
        if self.use_mock:
            return self._mock_offer_decision(trigger)
        
        # In a real implementation, this would call AWS Bedrock
        try:
            return self._bedrock_offer_decision(trigger)
        except Exception as e:
            logger.error(f"Bedrock decision failed: {e}")
            return self._fallback_offer_decision(trigger)
    
    def _mock_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Mock AI decision for testing"""
        suggested_amount = trigger.amount or 150.0
        product = trigger.product or "Arduino Sensor Data"
        
        # Simple AI logic: base decision on amount and product type
        if suggested_amount > 200:
            decision = "reject"
            reason = f"Amount too high ({suggested_amount} ADA) for {product}"
            final_amount = 0
        elif suggested_amount < 50:
            decision = "counter_offer"
            reason = f"Amount too low, counter-offering higher amount for {product}"
            final_amount = 75.0
        else:
            decision = "accept"
            reason = f"Fair price for {product}"
            final_amount = suggested_amount
        
        return {
            "decision": decision,
            "amount": final_amount,
            "reason": reason,
            "confidence": 0.85,
            "product": product
        }
    
    def _fallback_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Fallback decision logic"""
        amount = trigger.amount or 100.0
        product = trigger.product or "Arduino Data"
        
        if amount <= FALLBACK_THRESHOLD / 1000000:  # Convert lovelace to ADA
            decision = "accept"
            reason = "Amount within acceptable threshold"
        else:
            decision = "reject"
            reason = "Amount exceeds fallback threshold"
        
        return {
            "decision": decision,
            "amount": amount,
            "reason": reason,
            "confidence": 0.7,
            "product": product
        }

# Initialize services
bedrock_service = BedrockService()

# In-memory storage
active_offers: Dict[str, dict] = {}

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "Agent A - Buyer Logic",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "router_url": ROUTER_URL,
        "payment_service_url": PAYMENT_SERVICE_URL
    }

@app.post("/trigger", response_model=OfferResponse)
async def trigger_offer(trigger: TriggerRequest, background_tasks: BackgroundTasks):
    """
    Trigger offer creation from Arduino or manual input
    """
    try:
        logger.info(f"Received trigger: {trigger.trigger_type} for {trigger.product}")
        
        # Get AI decision
        decision_data = bedrock_service.create_offer_decision(trigger)
        
        # Create offer
        offer_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        offer = {
            "offer_id": offer_id,
            "agent_id": "agent_a",
            "amount": decision_data["amount"],
            "currency": "ADA",
            "product": decision_data["product"],
            "status": "pending",
            "created_at": timestamp,
            "trigger_type": trigger.trigger_type,
            "decision_reason": decision_data["reason"],
            "confidence": decision_data.get("confidence", 0.8)
        }
        
        # Store offer locally
        active_offers[offer_id] = offer
        
        # Send to router if decision is accept or counter_offer
        if decision_data["decision"] in ["accept", "counter_offer"]:
            background_tasks.add_task(send_offer_to_router, offer)
        
        return OfferResponse(
            status=decision_data["decision"],
            amount=decision_data["amount"],
            offer_id=offer_id,
            decision_reason=decision_data["reason"],
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"Error processing trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/offers")
async def get_offers():
    """Get all active offers"""
    return {"offers": list(active_offers.values())}

@app.get("/offers/{offer_id}")
async def get_offer(offer_id: str):
    """Get specific offer by ID"""
    if offer_id not in active_offers:
        raise HTTPException(status_code=404, detail="Offer not found")
    return active_offers[offer_id]

@app.post("/evaluate_response")
async def evaluate_response(decision_req: DecisionRequest):
    """
    Evaluate response from Agent B and make final decision
    """
    try:
        offer_id = decision_req.offer_id
        
        if offer_id not in active_offers:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # Get current offer
        offer = active_offers[offer_id]
        
        # Simple evaluation logic
        if decision_req.counter_offer:
            counter_amount = decision_req.counter_offer.get("amount", 0)
            if counter_amount <= offer["amount"] * 1.2:  # Accept if within 20% increase
                decision = "accept"
                final_amount = counter_amount
                reason = "Counter offer acceptable"
            else:
                decision = "reject"
                final_amount = offer["amount"]
                reason = "Counter offer too high"
        else:
            decision = "accept"
            final_amount = offer["amount"]
            reason = "Original offer accepted"
        
        # Update offer
        offer["status"] = decision
        offer["final_amount"] = final_amount
        offer["evaluation_reason"] = reason
        offer["updated_at"] = datetime.now().isoformat()
        
        return {
            "status": decision,
            "amount": final_amount,
            "offer_id": offer_id,
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error evaluating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_offer_to_router(offer: dict):
    """Send offer to router service"""
    try:
        response = requests.post(
            f"{ROUTER_URL}/receive_offer",
            json=offer,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Offer {offer['offer_id']} sent to router successfully")
        else:
            logger.error(f"Failed to send offer to router: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending offer to router: {e}")

@app.post("/arduino_trigger")
async def arduino_trigger(data: dict):
    """Special endpoint for Arduino triggers"""
    trigger = TriggerRequest(
        trigger_type="arduino",
        amount=data.get("amount", 100.0),
        product=data.get("product", "Arduino Sensor Data"),
        context=data.get("context", {})
    )
    
    return await trigger_offer(trigger, BackgroundTasks())

if __name__ == "__main__":
    port = int(os.getenv("AGENT_A_PORT", "8001"))
    logger.info(f"Starting Agent A on port {port}")
    
    uvicorn.run(
        "agent_a:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENABLE_HOT_RELOAD", "true").lower() == "true"
    )