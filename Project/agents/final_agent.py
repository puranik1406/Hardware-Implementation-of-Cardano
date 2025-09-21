#!/usr/bin/env python3
"""
Final Agent A - Simple Wallet Service
Returns wallet address for ADA transactions - Nothing else!
"""

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI(title="Agent A - Final", version="1.0.0")

# The wallet address that receives ADA
WALLET_ADDRESS = "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"

class TriggerRequest(BaseModel):
    amount: float = 1000000  # lovelace

@app.get("/")
def health():
    """Health check"""
    return {
        "service": "Agent A - Final",
        "wallet": WALLET_ADDRESS,
        "status": "ready"
    }

@app.post("/wallet")
def get_wallet(trigger: TriggerRequest):
    """
    Simple: Return wallet address and ADA amount
    This is what Router/Blockchain needs
    """
    amount_ada = trigger.amount / 1000000
    
    return {
        "wallet_address": WALLET_ADDRESS,
        "amount_ada": amount_ada,
        "currency": "ADA",
        "action": "send_to_wallet"
    }

if __name__ == "__main__":
    print("🚀 Final Agent A - Simple Wallet Service")
    print(f"💰 Wallet: {WALLET_ADDRESS}")
    print("🔗 Running on: http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
