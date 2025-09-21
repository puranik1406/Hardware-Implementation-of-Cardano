"""
Real Payment Service for Arduino-to-Cardano AI Agents
Integrates Masumi protocol with Cardano blockchain via Blockfrost API
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Import our blockchain clients
from blockfrost_client import BlockfrostClient
from masumi_client import get_masumi_client, MasumiConfig

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Payment Service (Real Blockchain)",
    description="Real blockchain payment service for Arduino-to-Cardano AI Agents",
    version="1.0.0-real"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
blockfrost_client: Optional[BlockfrostClient] = None
masumi_client = None

# In-memory storage (in production, use Redis or database)
active_jobs: Dict[str, dict] = {}

class PaymentRequest(BaseModel):
    from_address: str = Field(..., description="Source wallet address")
    to_address: str = Field(..., description="Destination wallet address")
    amount: int = Field(..., gt=0, description="Amount in lovelace")
    metadata: Optional[Dict] = Field(None, description="Optional transaction metadata")

class PaymentResponse(BaseModel):
    job_id: str
    tx_hash: Optional[str] = None
    status: str
    masumi_tx_id: Optional[str] = None
    estimated_confirmation_time: int

class TransactionStatus(BaseModel):
    job_id: str
    tx_hash: Optional[str] = None
    masumi_tx_id: Optional[str] = None
    status: str  # "pending", "submitted", "confirmed", "failed"
    confirmations: int
    created_at: datetime
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    block_height: Optional[int] = None
    fee: Optional[int] = None
    error_message: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize blockchain clients on startup"""
    global blockfrost_client, masumi_client
    
    try:
        # Initialize Blockfrost client
        blockfrost_client = BlockfrostClient()
        logger.info("✅ Blockfrost client initialized")
        
        # Test Blockfrost connectivity
        network_info = blockfrost_client.get_network_info()
        logger.info(f"✅ Connected to Cardano {network_info.get('network_name', 'unknown')}")
        
        # Initialize Masumi client
        use_mock_masumi = os.getenv("MASUMI_MOCK_MODE", "true").lower() == "true"
        masumi_client = get_masumi_client(use_mock=use_mock_masumi)
        logger.info(f"✅ Masumi client initialized (mock: {use_mock_masumi})")
        
        # Test Masumi connectivity
        masumi_status = masumi_client.get_network_status()
        logger.info(f"✅ Masumi network status: {masumi_status.get('status')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize blockchain clients: {e}")
        raise e

def generate_job_id() -> str:
    """Generate unique job identifier"""
    return f"real_job_{uuid.uuid4().hex[:16]}"

async def process_transaction_confirmation(job_id: str):
    """Background task to monitor transaction confirmation"""
    try:
        job_data = active_jobs.get(job_id)
        if not job_data:
            logger.error(f"Job {job_id} not found for confirmation processing")
            return
        
        masumi_tx_id = job_data.get("masumi_tx_id")
        if not masumi_tx_id:
            logger.error(f"No Masumi transaction ID for job {job_id}")
            return
        
        # Poll Masumi for transaction status
        max_wait_time = 300  # 5 minutes
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < max_wait_time:
            try:
                # Check status via Masumi
                masumi_status = masumi_client.get_transaction_status(masumi_tx_id)
                
                if masumi_status.get("status") == "confirmed":
                    # Transaction confirmed via Masumi
                    cardano_tx_hash = masumi_status.get("cardano_tx_hash")
                    
                    if cardano_tx_hash and blockfrost_client:
                        # Verify on Cardano blockchain via Blockfrost
                        try:
                            tx_info = blockfrost_client.get_transaction(cardano_tx_hash)
                            confirmations = blockfrost_client.get_transaction_confirmations(cardano_tx_hash)
                            
                            # Update job with confirmation details
                            active_jobs[job_id].update({
                                "status": "confirmed",
                                "tx_hash": cardano_tx_hash,
                                "confirmed_at": datetime.now(),
                                "confirmations": confirmations,
                                "block_height": tx_info.get("block_height"),
                                "fee": tx_info.get("fees")
                            })
                            
                            logger.info(f"✅ Transaction {cardano_tx_hash} confirmed for job {job_id}")
                            return
                            
                        except Exception as e:
                            logger.warning(f"Could not verify transaction on Cardano: {e}")
                            # Still mark as confirmed based on Masumi
                            active_jobs[job_id].update({
                                "status": "confirmed",
                                "tx_hash": cardano_tx_hash,
                                "confirmed_at": datetime.now(),
                                "confirmations": 1  # At least 1 confirmation via Masumi
                            })
                            return
                    
                elif masumi_status.get("status") == "failed":
                    # Transaction failed
                    active_jobs[job_id].update({
                        "status": "failed",
                        "error_message": masumi_status.get("error", "Transaction failed")
                    })
                    logger.error(f"❌ Transaction failed for job {job_id}")
                    return
                
                # Still pending, wait and retry
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.warning(f"Error checking transaction status: {e}")
                await asyncio.sleep(10)
        
        # Timeout - mark as failed
        active_jobs[job_id].update({
            "status": "failed",
            "error_message": "Transaction confirmation timeout"
        })
        logger.error(f"❌ Transaction confirmation timeout for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in confirmation processing: {e}")
        if job_id in active_jobs:
            active_jobs[job_id].update({
                "status": "failed",
                "error_message": str(e)
            })

@app.get("/")
async def root():
    """Health check endpoint"""
    try:
        # Check client status
        blockfrost_status = "connected" if blockfrost_client else "disconnected"
        masumi_status = "connected" if masumi_client else "disconnected"
        
        # Get network info if available
        network_info = {}
        if blockfrost_client:
            try:
                network_info = blockfrost_client.get_network_info()
            except:
                pass
        
        return {
            "service": "Payment Service",
            "mode": "real",
            "status": "running",
            "version": "1.0.0-real",
            "clients": {
                "blockfrost": blockfrost_status,
                "masumi": masumi_status
            },
            "network": network_info.get("network_name", "unknown"),
            "active_jobs": len(active_jobs),
            "endpoints": {
                "send_payment": "POST /send_payment",
                "tx_status": "GET /tx_status/{job_id}",
                "list_jobs": "GET /jobs"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service health check failed: {str(e)}")

@app.post("/send_payment", response_model=PaymentResponse)
async def send_payment(payment: PaymentRequest, background_tasks: BackgroundTasks):
    """
    Initiate a real payment transaction via Masumi + Cardano
    """
    try:
        # Validate clients are available
        if not blockfrost_client or not masumi_client:
            raise HTTPException(status_code=503, detail="Blockchain clients not initialized")
        
        # Validate addresses using Blockfrost
        if not blockfrost_client.validate_address(payment.from_address):
            raise HTTPException(status_code=400, detail="Invalid from_address")
        
        if not blockfrost_client.validate_address(payment.to_address):
            raise HTTPException(status_code=400, detail="Invalid to_address")
        
        # Check sender balance
        try:
            sender_info = blockfrost_client.get_address_info(payment.from_address)
            balance = int(sender_info.get("amount", [{"quantity": "0"}])[0]["quantity"])
            
            if balance < payment.amount + 200000:  # Amount + estimated fee
                raise HTTPException(status_code=400, detail="Insufficient balance")
        except Exception as e:
            logger.warning(f"Could not check balance for {payment.from_address}: {e}")
        
        # Generate job ID
        job_id = generate_job_id()
        
        # Create transaction via Masumi
        tx_request = {
            "from_address": payment.from_address,
            "to_address": payment.to_address,
            "amount": payment.amount,
            "metadata": payment.metadata or {}
        }
        
        masumi_result = masumi_client.create_transaction(tx_request)
        masumi_tx_id = masumi_result.get("tx_id")
        
        if not masumi_tx_id:
            raise HTTPException(status_code=500, detail="Failed to create Masumi transaction")
        
        # Store job data
        active_jobs[job_id] = {
            "job_id": job_id,
            "masumi_tx_id": masumi_tx_id,
            "tx_hash": None,
            "status": "pending",
            "confirmations": 0,
            "created_at": datetime.now(),
            "submitted_at": None,
            "confirmed_at": None,
            "from_address": payment.from_address,
            "to_address": payment.to_address,
            "amount": payment.amount,
            "metadata": payment.metadata,
            "block_height": None,
            "fee": masumi_result.get("estimated_fee"),
            "error_message": None
        }
        
        # Submit transaction via Masumi
        try:
            submit_result = masumi_client.submit_transaction({"tx_id": masumi_tx_id})
            cardano_tx_hash = submit_result.get("cardano_tx_hash")
            
            # Update job with submission details
            active_jobs[job_id].update({
                "status": "submitted",
                "tx_hash": cardano_tx_hash,
                "submitted_at": datetime.now()
            })
            
            # Start background confirmation monitoring
            background_tasks.add_task(process_transaction_confirmation, job_id)
            
            return PaymentResponse(
                job_id=job_id,
                tx_hash=cardano_tx_hash,
                status="submitted",
                masumi_tx_id=masumi_tx_id,
                estimated_confirmation_time=masumi_result.get("estimated_confirmation_time", 60)
            )
            
        except Exception as e:
            logger.error(f"Transaction submission failed: {e}")
            active_jobs[job_id].update({
                "status": "failed",
                "error_message": f"Submission failed: {str(e)}"
            })
            raise HTTPException(status_code=500, detail=f"Transaction submission failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")

@app.get("/tx_status/{job_id}", response_model=TransactionStatus)
async def get_transaction_status(job_id: str):
    """Get transaction status by job ID"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job_data = active_jobs[job_id]
    
    # If transaction is confirmed and we have a tx_hash, get live confirmations
    if job_data["status"] == "confirmed" and job_data.get("tx_hash") and blockfrost_client:
        try:
            confirmations = blockfrost_client.get_transaction_confirmations(job_data["tx_hash"])
            job_data["confirmations"] = max(job_data["confirmations"], confirmations)
        except Exception as e:
            logger.warning(f"Could not update confirmations: {e}")
    
    return TransactionStatus(**job_data)

@app.get("/jobs")
async def list_all_jobs():
    """List all payment jobs"""
    return {
        "total_jobs": len(active_jobs),
        "jobs": list(active_jobs.values())
    }

@app.get("/wallet/{address}/balance")
async def get_wallet_balance(address: str):
    """Get wallet balance via Blockfrost"""
    try:
        if not blockfrost_client:
            raise HTTPException(status_code=503, detail="Blockfrost client not available")
        
        address_info = blockfrost_client.get_address_info(address)
        
        # Parse balance from Blockfrost response
        balance_lovelace = 0
        amounts = address_info.get("amount", [])
        for amount in amounts:
            if amount.get("unit") == "lovelace":
                balance_lovelace = int(amount.get("quantity", 0))
                break
        
        utxos = blockfrost_client.get_address_utxos(address)
        
        return {
            "address": address,
            "balance_lovelace": balance_lovelace,
            "balance_ada": balance_lovelace / 1_000_000,
            "utxos_count": len(utxos)
        }
        
    except Exception as e:
        logger.error(f"Balance query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Balance query failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PAYMENT_SERVICE_PORT", "8001"))
    host = os.getenv("PAYMENT_SERVICE_HOST", "localhost")
    
    print(f"""
🚀 Real Payment Service Starting...

🌐 Service URL: http://{host}:{port}
📋 API Docs: http://{host}:{port}/docs
🔍 Health Check: http://{host}:{port}/

🔗 Blockchain Integration:
• Blockfrost API: {os.getenv('BLOCKFROST_BASE_URL', 'Not configured')}
• Masumi Network: {os.getenv('MASUMI_NETWORK_URL', 'http://localhost:3001')}

⚠️  REAL MODE - Uses actual testnet ADA!
    """)
    
    uvicorn.run(
        "real_payment_service:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )