#!/usr/bin/env python3
"""
Simple Agent A - Returns Wallet Address for ADA Transactions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent A - Simple Wallet Service", version="1.0.0")

# Wallet address provided by user
WALLET_ADDRESS = "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"

class TriggerRequest(BaseModel):
    trigger_type: str = "arduino"
    amount: float = 1000000  # lovelace
    source: str = "agent_a"
    context: dict = {}

class WalletResponse(BaseModel):
    wallet_address: str
    amount_ada: float
    amount_lovelace: float
    transaction_id: str
    timestamp: str
    status: str

@app.get("/")
async def health_check():
    """Simple health check"""
    return {
        "service": "Agent A - Simple Wallet Service",
        "status": "running",
        "wallet_address": WALLET_ADDRESS,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agentA/get_wallet", response_model=WalletResponse)
async def get_wallet_address(trigger: TriggerRequest):
    """
    Simple endpoint - just returns wallet address for ADA transaction
    """
    try:
        # Convert lovelace to ADA
        amount_ada = trigger.amount / 1000000
        
        # Generate transaction ID
        transaction_id = f"tx_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"Wallet request: {amount_ada} ADA to {WALLET_ADDRESS}")
        
        return WalletResponse(
            wallet_address=WALLET_ADDRESS,
            amount_ada=amount_ada,
            amount_lovelace=trigger.amount,
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            status="ready_for_transaction"
        )
        
    except Exception as e:
        logger.error(f"Error processing wallet request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agentA/simple_transaction")
async def simple_transaction(trigger: TriggerRequest):
    """
    Simplified transaction endpoint - returns what Router/Blockchain needs
    """
    try:
        amount_ada = trigger.amount / 1000000
        
        # This is what goes to Router/Blockchain
        blockchain_data = {
            "recipient_wallet": WALLET_ADDRESS,
            "amount": amount_ada,
            "currency": "ADA",
            "transaction_type": "send",
            "timestamp": datetime.now().isoformat(),
            "source": trigger.source,
            "trigger_type": trigger.trigger_type
        }
        
        logger.info(f"Simple transaction: {amount_ada} ADA → {WALLET_ADDRESS}")
        
        return {
            "status": "transaction_ready",
            "blockchain_data": blockchain_data,
            "summary": f"Send {amount_ada} ADA to {WALLET_ADDRESS}"
        }
        
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Simple Agent A")
    print(f"💰 Wallet Address: {WALLET_ADDRESS}")
    print(f"🔗 Server: http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
