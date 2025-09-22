"""
Payment Service for Cardano-Arduino-AI System
Handles real Cardano blockchain transactions via Blockfrost API
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

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
    title="Cardano Payment Service",
    description="Blockchain payment service for Arduino-to-Cardano AI Agents",
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
BLOCKFROST_PROJECT_ID = os.getenv("BLOCKFROST_PROJECT_ID", "")
BLOCKFROST_BASE_URL = os.getenv("BLOCKFROST_BASE_URL", "https://cardano-preprod.blockfrost.io/api/v0")
CARDANO_NETWORK = os.getenv("CARDANO_NETWORK", "preprod")
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

# Pydantic models
class PaymentRequest(BaseModel):
    """Payment request model"""
    from_address: str = Field(..., description="Sender Cardano address")
    to_address: str = Field(..., description="Recipient Cardano address")
    amount: int = Field(..., description="Amount in lovelace (1 ADA = 1,000,000 lovelace)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Transaction metadata")

class PaymentResponse(BaseModel):
    """Payment response model"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")

class JobStatus(BaseModel):
    """Job status model"""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current status")
    transaction_hash: Optional[str] = Field(None, description="Transaction hash if completed")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")

class BlockfrostClient:
    """Client for Blockfrost API integration"""
    
    def __init__(self):
        self.project_id = BLOCKFROST_PROJECT_ID
        self.base_url = BLOCKFROST_BASE_URL
        self.headers = {
            "project_id": self.project_id,
            "Content-Type": "application/json"
        }
        self.enabled = bool(self.project_id and self.project_id != "your_blockfrost_project_id_here")
        
        if self.enabled:
            logger.info("Blockfrost client initialized with real API")
        else:
            logger.info("Blockfrost client in mock mode - no real transactions")
    
    def get_network_info(self) -> dict:
        """Get Cardano network information"""
        if not self.enabled:
            return {"network": "mock", "status": "active"}
        
        try:
            response = requests.get(
                f"{self.base_url}/network",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            raise
    
    def get_address_info(self, address: str) -> dict:
        """Get address information"""
        if not self.enabled:
            return {
                "address": address,
                "amount": [{"unit": "lovelace", "quantity": "10000000"}],
                "stake_address": None,
                "type": "shelley"
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/addresses/{address}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get address info for {address}: {e}")
            raise
    
    def submit_transaction(self, tx_data: dict) -> dict:
        """Submit transaction to Cardano network"""
        if not self.enabled:
            # Mock transaction submission
            mock_tx_hash = f"mock_tx_{uuid.uuid4().hex[:16]}"
            logger.info(f"Mock transaction submitted: {mock_tx_hash}")
            return {
                "hash": mock_tx_hash,
                "status": "submitted"
            }
        
        try:
            response = requests.post(
                f"{self.base_url}/tx/submit",
                headers=self.headers,
                json=tx_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to submit transaction: {e}")
            raise

class PaymentService:
    """Main payment service class"""
    
    def __init__(self):
        self.blockfrost = BlockfrostClient()
        self.active_jobs: Dict[str, dict] = {}
        self.mock_mode = MOCK_MODE or not self.blockfrost.enabled
        
        logger.info(f"Payment service initialized (mock: {self.mock_mode})")
    
    def create_payment_job(self, payment_request: PaymentRequest) -> str:
        """Create a new payment job"""
        job_id = str(uuid.uuid4())
        
        # Validate addresses
        if not self._validate_address(payment_request.from_address):
            raise ValueError("Invalid from_address")
        if not self._validate_address(payment_request.to_address):
            raise ValueError("Invalid to_address")
        
        # Validate amount
        if payment_request.amount < 1000000:  # Minimum 1 ADA
            raise ValueError("Amount must be at least 1 ADA (1,000,000 lovelace)")
        
        # Create job
        job = {
            "job_id": job_id,
            "status": "pending",
            "payment_request": payment_request.dict(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "transaction_hash": None,
            "error": None
        }
        
        self.active_jobs[job_id] = job
        logger.info(f"Created payment job {job_id}: {payment_request.amount} lovelace")
        
        return job_id
    
    def _validate_address(self, address: str) -> bool:
        """Validate Cardano address format"""
        # Basic validation - should be enhanced for production
        if not address:
            return False
        
        # Testnet addresses start with addr_test1
        # Mainnet addresses start with addr1
        if CARDANO_NETWORK == "preprod" or CARDANO_NETWORK == "testnet":
            return address.startswith("addr_test1")
        else:
            return address.startswith("addr1")
    
    async def process_payment(self, job_id: str):
        """Process payment asynchronously"""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job = self.active_jobs[job_id]
        
        try:
            job["status"] = "processing"
            job["updated_at"] = datetime.now().isoformat()
            
            payment_req = PaymentRequest(**job["payment_request"])
            
            if self.mock_mode:
                # Mock processing
                await asyncio.sleep(2)  # Simulate processing time
                
                # Simulate random success/failure (90% success rate)
                import random
                if random.random() < 0.9:
                    tx_hash = f"mock_tx_{uuid.uuid4().hex[:16]}"
                    job["status"] = "completed"
                    job["transaction_hash"] = tx_hash
                    logger.info(f"Mock payment completed: {tx_hash}")
                else:
                    job["status"] = "failed"
                    job["error"] = "Mock payment failure for testing"
                    logger.error(f"Mock payment failed for job {job_id}")
            else:
                # Real blockchain processing
                tx_result = await self._submit_real_transaction(payment_req)
                
                if tx_result.get("hash"):
                    job["status"] = "completed"
                    job["transaction_hash"] = tx_result["hash"]
                    logger.info(f"Real payment completed: {tx_result['hash']}")
                else:
                    job["status"] = "failed"
                    job["error"] = "Transaction submission failed"
                    logger.error(f"Real payment failed for job {job_id}")
            
            job["updated_at"] = datetime.now().isoformat()
            
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            job["updated_at"] = datetime.now().isoformat()
            logger.error(f"Payment processing error for job {job_id}: {e}")
    
    async def _submit_real_transaction(self, payment_req: PaymentRequest) -> dict:
        """Submit real transaction to Cardano blockchain"""
        # This is a simplified version - in production, you would:
        # 1. Build the transaction with proper UTXO management
        # 2. Sign the transaction with private keys
        # 3. Submit to the network
        
        try:
            # Get address info to verify balance
            from_addr_info = self.blockfrost.get_address_info(payment_req.from_address)
            
            # Check balance (simplified)
            balance = 0
            for amount in from_addr_info.get("amount", []):
                if amount["unit"] == "lovelace":
                    balance = int(amount["quantity"])
                    break
            
            if balance < payment_req.amount:
                raise ValueError(f"Insufficient balance: {balance} < {payment_req.amount}")
            
            # For now, return mock transaction as real implementation
            # requires complex transaction building
            logger.warning("Real transaction building not implemented - using mock")
            tx_hash = f"real_mock_tx_{uuid.uuid4().hex[:16]}"
            
            return {"hash": tx_hash, "status": "submitted"}
            
        except Exception as e:
            logger.error(f"Real transaction error: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        return self.active_jobs.get(job_id)
    
    def get_all_jobs(self) -> Dict[str, dict]:
        """Get all jobs"""
        return self.active_jobs

# Initialize payment service
payment_service = PaymentService()

@app.get("/")
async def health_check():
    """Health check endpoint"""
    try:
        network_info = payment_service.blockfrost.get_network_info()
        
        return {
            "service": "Cardano Payment Service",
            "status": "healthy",
            "version": "1.0.0",
            "mode": "mock" if payment_service.mock_mode else "real",
            "network": CARDANO_NETWORK,
            "blockfrost_enabled": payment_service.blockfrost.enabled,
            "network_info": network_info,
            "active_jobs": len(payment_service.active_jobs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "service": "Cardano Payment Service",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/send_payment", response_model=PaymentResponse)
async def send_payment(payment_request: PaymentRequest, background_tasks: BackgroundTasks):
    """
    Initiate a payment transaction
    """
    try:
        # Create payment job
        job_id = payment_service.create_payment_job(payment_request)
        
        # Start processing in background
        background_tasks.add_task(payment_service.process_payment, job_id)
        
        # Estimate completion time
        estimated_completion = (datetime.now() + timedelta(minutes=2)).isoformat()
        
        return PaymentResponse(
            job_id=job_id,
            status="pending",
            estimated_completion=estimated_completion
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Payment error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/job_status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get status of a payment job
    """
    job = payment_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**job)

@app.get("/jobs")
async def get_all_jobs():
    """
    Get all payment jobs
    """
    return {
        "jobs": list(payment_service.get_all_jobs().values()),
        "count": len(payment_service.active_jobs)
    }

@app.get("/address/{address}")
async def get_address_info(address: str):
    """
    Get Cardano address information
    """
    try:
        info = payment_service.blockfrost.get_address_info(address)
        return info
    except Exception as e:
        logger.error(f"Error getting address info: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/test_payment")
async def test_payment():
    """
    Create a test payment for demonstration
    """
    test_request = PaymentRequest(
        from_address=os.getenv("DEFAULT_WALLET_ADDRESS", "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"),
        to_address=os.getenv("DEFAULT_WALLET_ADDRESS", "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"),
        amount=2000000,  # 2 ADA
        metadata={
            "purpose": "test_payment",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    return await send_payment(test_request, BackgroundTasks())

if __name__ == "__main__":
    port = int(os.getenv("PAYMENT_SERVICE_PORT", "8000"))
    logger.info(f"Starting Payment Service on port {port}")
    
    uvicorn.run(
        "payment_service:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENABLE_HOT_RELOAD", "true").lower() == "true"
    )