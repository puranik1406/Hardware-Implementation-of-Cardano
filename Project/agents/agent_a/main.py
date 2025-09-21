"""
Agent A (Buyer Logic) Service
Handles offer creation and decision-making using AWS Bedrock with fallback logic
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import logging
import uuid
from datetime import datetime
import os
from router_integration import RouterIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent A - Buyer Logic",
    description="AI agent for making and evaluating payment offers",
    version="1.0.0"
)

# Pydantic models for request/response validation
class TriggerRequest(BaseModel):
    """Request model for trigger input"""
    trigger_type: str = Field(..., description="Type of trigger (arduino, manual, etc.)")
    amount: Optional[float] = Field(None, description="Suggested amount for offer")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    timestamp: Optional[str] = Field(None, description="Trigger timestamp")

class OfferResponse(BaseModel):
    """Response model for offer creation"""
    status: str = Field(..., description="Status of the offer (accepted, rejected, pending)")
    amount: float = Field(..., description="Offer amount in lovelace")
    offer_id: str = Field(..., description="Unique offer identifier")
    decision_reason: str = Field(..., description="Reason for the decision")
    timestamp: str = Field(..., description="Offer creation timestamp")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")

class DecisionRequest(BaseModel):
    """Request model for decision evaluation"""
    offer_id: str = Field(..., description="Offer ID to evaluate")
    counter_offer: Optional[Dict[str, Any]] = Field(None, description="Counter offer details")
    context: Optional[Dict[str, Any]] = Field(None, description="Decision context")

class DecisionResponse(BaseModel):
    """Response model for decision evaluation"""
    status: str = Field(..., description="Decision status (accepted, rejected)")
    amount: float = Field(..., description="Final agreed amount")
    offer_id: str = Field(..., description="Offer identifier")
    decision_reason: str = Field(..., description="Reason for decision")
    timestamp: str = Field(..., description="Decision timestamp")

# Configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
FALLBACK_THRESHOLD = float(os.getenv("FALLBACK_THRESHOLD", "1000000"))  # 1 ADA in lovelace
USE_MOCK_BEDROCK = os.getenv("USE_MOCK_BEDROCK", "true").lower() == "true"

class BedrockService:
    """Service for AWS Bedrock integration with fallback logic"""
    
    def __init__(self):
        self.use_mock = USE_MOCK_BEDROCK
        if not self.use_mock:
            try:
                import boto3
                self.bedrock_client = boto3.client('bedrock-runtime')
                logger.info("AWS Bedrock client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock client: {e}")
                self.use_mock = True
    
    def create_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Create offer decision using Bedrock or fallback logic"""
        
        if self.use_mock:
            return self._mock_offer_decision(trigger)
        
        try:
            return self._bedrock_offer_decision(trigger)
        except Exception as e:
            logger.error(f"Bedrock decision failed: {e}")
            return self._fallback_offer_decision(trigger)
    
    def evaluate_counter_offer(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Evaluate counter offer using Bedrock or fallback logic"""
        
        if self.use_mock:
            return self._mock_counter_offer_decision(decision_req)
        
        try:
            return self._bedrock_counter_offer_decision(decision_req)
        except Exception as e:
            logger.error(f"Bedrock counter-offer evaluation failed: {e}")
            return self._fallback_counter_offer_decision(decision_req)
    
    def _mock_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Mock offer decision for testing"""
        amount = trigger.amount or 1000000  # Default 1 ADA
        return {
            "status": "accepted",
            "amount": amount,
            "offer_id": str(uuid.u4()),
            "decision_reason": "Mock decision - offer accepted for testing",
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_counter_offer_decision(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Mock counter offer decision for testing"""
        return {
            "status": "accepted",
            "amount": 1000000,
            "offer_id": decision_req.offer_id,
            "decision_reason": "Mock decision - counter offer accepted",
            "timestamp": datetime.now().isoformat()
        }
    
    def _bedrock_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Use AWS Bedrock for offer decision"""
        prompt = self._create_offer_prompt(trigger)
        
        # Call Bedrock API
        response = self.bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        decision_text = response_body['completion']
        
        # Parse JSON response from Bedrock
        try:
            decision = json.loads(decision_text)
            logger.info(f"Bedrock offer decision: {decision}")
            return decision
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Bedrock response: {decision_text}")
            return self._fallback_offer_decision(trigger)
    
    def _bedrock_counter_offer_decision(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Use AWS Bedrock for counter offer decision"""
        prompt = self._create_counter_offer_prompt(decision_req)
        
        response = self.bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        decision_text = response_body['completion']
        
        try:
            decision = json.loads(decision_text)
            logger.info(f"Bedrock counter-offer decision: {decision}")
            return decision
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Bedrock response: {decision_text}")
            return self._fallback_counter_offer_decision(decision_req)
    
    def _fallback_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Fallback rule-based offer decision"""
        amount = trigger.amount or FALLBACK_THRESHOLD
        
        # Simple rule: accept if amount is reasonable
        if amount >= FALLBACK_THRESHOLD:
            status = "accepted"
            reason = f"Fallback rule: amount {amount} meets threshold {FALLBACK_THRESHOLD}"
        else:
            status = "rejected"
            reason = f"Fallback rule: amount {amount} below threshold {FALLBACK_THRESHOLD}"
        
        return {
            "status": status,
            "amount": amount,
            "offer_id": str(uuid.uuid4()),
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_counter_offer_decision(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Fallback rule-based counter offer decision"""
        # Simple rule: accept counter offers above threshold
        counter_amount = decision_req.counter_offer.get('amount', 0) if decision_req.counter_offer else 0
        
        if counter_amount >= FALLBACK_THRESHOLD:
            status = "accepted"
            reason = f"Fallback rule: counter offer amount {counter_amount} meets threshold"
        else:
            status = "rejected"
            reason = f"Fallback rule: counter offer amount {counter_amount} below threshold"
        
        return {
            "status": status,
            "amount": counter_amount,
            "offer_id": decision_req.offer_id,
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_offer_prompt(self, trigger: TriggerRequest) -> str:
        """Create structured prompt for offer decision"""
        return f"""
You are Agent A, a buyer AI agent in a blockchain payment system. You need to decide whether to create an offer.

Context:
- Trigger type: {trigger.trigger_type}
- Suggested amount: {trigger.amount}
- Additional context: {trigger.context}

Please respond with a JSON object in this exact format:
{{
    "status": "accepted" or "rejected",
    "amount": <number in lovelace>,
    "offer_id": "<uuid>",
    "decision_reason": "<explanation>",
    "timestamp": "<ISO timestamp>"
}}

Consider:
- Is the amount reasonable for a test transaction?
- Does the trigger context make sense?
- Would this be a good test of the payment system?

Respond with ONLY the JSON object, no other text.
"""
    
    def _create_counter_offer_prompt(self, decision_req: DecisionRequest) -> str:
        """Create structured prompt for counter offer decision"""
        return f"""
You are Agent A, a buyer AI agent. You need to evaluate a counter offer.

Context:
- Original offer ID: {decision_req.offer_id}
- Counter offer: {decision_req.counter_offer}
- Additional context: {decision_req.context}

Please respond with a JSON object in this exact format:
{{
    "status": "accepted" or "rejected",
    "amount": <final amount in lovelace>,
    "offer_id": "<original offer id>",
    "decision_reason": "<explanation>",
    "timestamp": "<ISO timestamp>"
}}

Consider:
- Is the counter offer reasonable?
- Does it meet your buying criteria?
- Would you accept this counter offer?

Respond with ONLY the JSON object, no other text.
"""

# Initialize services
bedrock_service = BedrockService()
router_integration = RouterIntegration()

@app.get("/")
async def root():
    """Health check endpoint"""
    router_status = router_integration.get_router_status()
    return {
        "service": "Agent A - Buyer Logic",
        "status": "running",
        "version": "1.0.0",
        "bedrock_mode": "mock" if USE_MOCK_BEDROCK else "real",
        "router_integration": router_status
    }

@app.post("/agentA/propose", response_model=OfferResponse)
async def propose_offer(trigger: TriggerRequest):
    """
    Create a new offer based on trigger input
    """
    try:
        logger.info(f"Received trigger: {trigger.dict()}")
        
        # Get decision from Bedrock service
        decision = bedrock_service.create_offer_decision(trigger)
        
        # Validate and format response
        response = OfferResponse(
            status=decision["status"],
            amount=decision["amount"],
            offer_id=decision["offer_id"],
            decision_reason=decision["decision_reason"],
            timestamp=decision["timestamp"]
        )
        
        logger.info(f"Generated offer: {response.dict()}")
        return response
        
    except Exception as e:
        logger.error(f"Error in propose_offer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/agentA/decide", response_model=DecisionResponse)
async def decide_offer(decision_req: DecisionRequest):
    """
    Evaluate a counter offer and make a decision
    """
    try:
        logger.info(f"Received decision request: {decision_req.dict()}")
        
        # Get decision from Bedrock service
        decision = bedrock_service.evaluate_counter_offer(decision_req)
        
        # Validate and format response
        response = DecisionResponse(
            status=decision["status"],
            amount=decision["amount"],
            offer_id=decision["offer_id"],
            decision_reason=decision["decision_reason"],
            timestamp=decision["timestamp"]
        )
        
        logger.info(f"Generated decision: {response.dict()}")
        return response
        
    except Exception as e:
        logger.error(f"Error in decide_offer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/agentA/send_to_router")
async def send_to_router(trigger: TriggerRequest):
    """
    Send offer directly to Router service (Vansh's endpoint)
    """
    try:
        logger.info(f"Received trigger for Router: {trigger.dict()}")
        
        # Convert lovelace to ADA for Router
        amount_ada = (trigger.amount or 1000000) / 1000000  # Convert lovelace to ADA
        
        # Send to Router
        router_result = router_integration.send_offer(
            amount=amount_ada,
            description=f"Agent A offer from {trigger.trigger_type}",
            metadata={
                "arduino_trigger": trigger.trigger_type == "arduino",
                "button_type": trigger.context.get("button_type", "button_1") if trigger.context else "button_1",
                "priority": trigger.context.get("priority", "medium") if trigger.context else "medium",
                "source": trigger.source or "agent_a",
                "original_amount_lovelace": trigger.amount
            }
        )
        
        if router_result["success"]:
            return {
                "status": "sent_to_router",
                "router_response": router_result["router_response"],
                "amount_ada": amount_ada,
                "amount_lovelace": trigger.amount,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Router integration failed: {router_result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Error in send_to_router: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/agentA/router_status")
async def router_status():
    """
    Check Router service status
    """
    status = router_integration.get_router_status()
    return {
        "router_status": status,
        "router_url": router_integration.router_url,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

