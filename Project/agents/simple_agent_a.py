"""
Simple Agent A Service for Testing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import logging
import uuid
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent A - Buyer Logic",
    description="AI agent for making and evaluating payment offers",
    version="1.0.0"
)

# Pydantic models
class TriggerRequest(BaseModel):
    """Request model for trigger input"""
    trigger_type: str = Field(..., description="Type of trigger (arduino, manual, etc.)")
    amount: Optional[float] = Field(None, description="Suggested amount for offer")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    timestamp: Optional[str] = Field(None, description="Trigger timestamp")
    source: Optional[str] = Field(None, description="Source of the trigger")

class OfferResponse(BaseModel):
    """Response model for offer creation"""
    status: str = Field(..., description="Status of the offer")
    amount: float = Field(..., description="Offer amount in lovelace")
    offer_id: str = Field(..., description="Unique offer identifier")
    decision_reason: str = Field(..., description="Reason for the decision")
    timestamp: str = Field(..., description="Offer creation timestamp")

# Configuration
USE_MOCK_BEDROCK = True
ROUTER_URL = "http://localhost:5000"

def send_to_router(amount_ada: float, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Send offer to Router service"""
    try:
        payload = {
            "from_agent": "agent_a",
            "to_agent": "agent_b",
            "amount": amount_ada,
            "currency": "ADA",
            "description": description,
            "timestamp": datetime.now().isoformat() + "Z",
            "metadata": metadata
        }
        
        logger.info(f"Sending to Router: {payload}")
        
        response = requests.post(
            f"{ROUTER_URL}/send_offer",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return {"success": True, "response": response.json()}
        else:
            return {"success": False, "error": f"Router error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Router error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Agent A - Buyer Logic",
        "status": "running",
        "version": "1.0.0",
        "bedrock_mode": "mock",
        "router_url": ROUTER_URL
    }

@app.post("/agentA/propose", response_model=OfferResponse)
async def propose_offer(trigger: TriggerRequest):
    """Create a new offer based on trigger input"""
    try:
        logger.info(f"Received trigger: {trigger.dict()}")
        
        # Mock decision logic
        amount = trigger.amount or 1000000
        status = "accepted" if amount >= 100000 else "rejected"
        
        response = OfferResponse(
            status=status,
            amount=amount,
            offer_id=str(uuid.uuid4()),
            decision_reason=f"Mock decision - amount {amount}",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Generated offer: {response.dict()}")
        return response
        
    except Exception as e:
        logger.error(f"Error in propose_offer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/agentA/send_to_router")
async def send_to_router_endpoint(trigger: TriggerRequest):
    """Send offer directly to Router service"""
    try:
        logger.info(f"Received trigger for Router: {trigger.dict()}")
        
        # Convert lovelace to ADA
        amount_ada = (trigger.amount or 1000000) / 1000000
        
        # Send to Router
        result = send_to_router(
            amount_ada=amount_ada,
            description=f"Agent A offer from {trigger.trigger_type}",
            metadata={
                "arduino_trigger": trigger.trigger_type == "arduino",
                "button_type": trigger.context.get("button_type", "button_1") if trigger.context else "button_1",
                "priority": trigger.context.get("priority", "medium") if trigger.context else "medium",
                "source": trigger.source or "agent_a",
                "original_amount_lovelace": trigger.amount
            }
        )
        
        if result["success"]:
            return {
                "status": "sent_to_router",
                "router_response": result["response"],
                "amount_ada": amount_ada,
                "amount_lovelace": trigger.amount,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Router integration failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Error in send_to_router: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/agentA/router_status")
async def router_status():
    """Check Router service status"""
    try:
        response = requests.get(f"{ROUTER_URL}/", timeout=10)
        return {
            "router_status": "connected",
            "router_url": ROUTER_URL,
            "response_code": response.status_code,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "router_status": "disconnected",
            "router_url": ROUTER_URL,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
