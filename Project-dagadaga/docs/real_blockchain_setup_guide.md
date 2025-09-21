# Real Blockchain Setup Guide - Masumi + Cardano Integration

## 🌐 Overview

This guide will set up real blockchain transactions using the **official Masumi Network infrastructure**:

- **Masumi Payment Service**: Official Docker-based payment processing (localhost:3001)
- **Masumi Registry Service**: Blockchain querying operations (localhost:3000)  
- **Cardano Preprod**: Real testnet blockchain for transactions
- **PyCardano**: Python library for transaction building
- **Blockfrost API**: Blockchain data and submission service

## 🏗️ Masumi Architecture

Based on the official documentation, Masumi consists of:

1. **Payment Service** (Port 3001): Handles wallet management, transactions, and token swapping
2. **Registry Service** (Port 3000): Provides blockchain querying for registered agents
3. **PostgreSQL Database** (Port 5432): Stores encrypted wallet data and transaction history

## 📋 Prerequisites

1. **Docker & Docker Compose** installed
2. **Git** for repository management
3. **Blockfrost API Account** (free tier available)
4. **PostgreSQL** (included in Docker setup)

## 🚀 Step-by-Step Setup

### Step 1: Clone Official Masumi Repository

```bash
# Clone the official Masumi quickstart repository
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git
cd masumi-services-dev-quickstart
```

### Step 2: Get Blockfrost API Key

1. **Sign up**: Go to https://blockfrost.io/
2. **Create Project**: Select "Cardano Preprod Testnet"
3. **Copy Project ID**: Format: `preprod[random_string]`
4. **Note**: Free tier allows 100K requests/day

### Step 3: Configure Environment Variables

Copy and configure the environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Database Configuration
POSTGRES_DB=masumi_db
POSTGRES_USER=masumi_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://masumi_user:your_secure_password_here@localhost:5432/masumi_db

# Masumi Security
ENCRYPTION_KEY=your_64_character_encryption_key_for_wallet_secrets_here_must_be_secure
ADMIN_KEY=your_admin_key_minimum_15_characters_secure

# Blockfrost API Configuration  
BLOCKFROST_API_KEY_PREPROD=preprod1234567890abcdef  # Your actual Blockfrost project ID

# Wallet Configuration (Generate these with Masumi tools)
PURCHASE_WALLET_PREPROD_MNEMONIC="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art"
SELLING_WALLET_PREPROD_MNEMONIC="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

# Collection wallet address (where fees are collected)
COLLECTION_WALLET_PREPROD_ADDRESS=addr_test1qp8f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z

# Network Configuration
CARDANO_NETWORK=preprod
NODE_ENV=development

# Service Ports
PAYMENT_SERVICE_PORT=3001
REGISTRY_SERVICE_PORT=3000
DATABASE_PORT=5432

# CORS and Security
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000,http://localhost:8001
JWT_SECRET=your_jwt_secret_for_api_authentication_here

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

### Step 4: Generate Encryption Key

Generate a secure 64-character encryption key:

```bash
# Using OpenSSL (recommended)
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using PowerShell
[System.Web.Security.Membership]::GeneratePassword(64, 0)
```

### Step 5: Start Masumi Services

Make sure Docker Desktop is running, then start the services:

```bash
# Start all Masumi services with Docker Compose
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

### Step 6: Verify Service Connectivity

Check that all services are running:

```bash
# Payment Service API Documentation
curl http://localhost:3001/docs

# Registry Service API Documentation  
curl http://localhost:3000/docs

# Payment Service Admin Dashboard
# Open browser: http://localhost:3001/admin

# Health check endpoints
curl http://localhost:3001/health
curl http://localhost:3000/health
```

### Step 7: Create and Fund Wallets

#### Option A: Using Masumi Admin Dashboard

1. **Access Admin Dashboard**: http://localhost:3001/admin
2. **Login with ADMIN_KEY**: Use the key from your .env file
3. **Create Wallets**: Generate wallets for Agent A, Agent B, Arduino A, Arduino B
4. **Fund Treasury**: Get preprod ADA from https://testnets.cardano.org/en/testnets/cardano/tools/faucet/

#### Option B: Using Masumi API Directly

```bash
# Create a new wallet via API
curl -X POST "http://localhost:3001/api/wallets" \
  -H "Authorization: Bearer YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agent_A_Wallet",
    "description": "Wallet for AI Agent A payments"
  }'

# Get wallet balance
curl -X GET "http://localhost:3001/api/wallets/{wallet_id}/balance" \
  -H "Authorization: Bearer YOUR_ADMIN_KEY"

# Send payment between wallets
curl -X POST "http://localhost:3001/api/payments" \
  -H "Authorization: Bearer YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_wallet_id": "agent_a_wallet_id",
    "to_address": "addr_test1vr5f4n4zk8gx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4zx4z",
    "amount": 1000000,
    "metadata": {
      "agent": "Agent_A",
      "purpose": "AI decision payment"
    }
  }'
```

### Step 8: Update Our Payment Service Integration

Now update our existing payment service to integrate with the official Masumi services:

Create `masumi_integration.py`:

```python
"""
Official Masumi Network Integration
Connects our payment service with the real Masumi Payment Service
"""

import requests
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MasumiPaymentClient:
    """Client for the official Masumi Payment Service"""
    
    def __init__(self):
        self.base_url = "http://localhost:3001"
        self.admin_key = os.getenv("MASUMI_ADMIN_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.admin_key}",
            "Content-Type": "application/json"
        }
    
    def create_wallet(self, name: str, description: str = "") -> Dict:
        """Create a new wallet in Masumi"""
        data = {
            "name": name,
            "description": description
        }
        response = requests.post(f"{self.base_url}/api/wallets", json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_wallet_balance(self, wallet_id: str) -> Dict:
        """Get wallet balance from Masumi"""
        response = requests.get(f"{self.base_url}/api/wallets/{wallet_id}/balance", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def send_payment(self, from_wallet_id: str, to_address: str, amount: int, metadata: Optional[Dict] = None) -> Dict:
        """Send payment via Masumi Payment Service"""
        data = {
            "from_wallet_id": from_wallet_id,
            "to_address": to_address,
            "amount": amount,
            "metadata": metadata or {}
        }
        response = requests.post(f"{self.base_url}/api/payments", json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_payment_status(self, payment_id: str) -> Dict:
        """Get payment status from Masumi"""
        response = requests.get(f"{self.base_url}/api/payments/{payment_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_wallets(self) -> List[Dict]:
        """List all wallets in Masumi"""
        response = requests.get(f"{self.base_url}/api/wallets", headers=self.headers)
        response.raise_for_status()
        return response.json()
```

### Step 9: Create Updated Real Payment Service

Update `real_payment_service.py` to use official Masumi:

```python
"""
Updated Real Payment Service with Official Masumi Integration
"""

import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, Optional
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Import our Masumi integration
from masumi_integration import MasumiPaymentClient

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Arduino-to-Cardano Payment Service (Real Masumi)",
    description="Real blockchain payment service using official Masumi Network",
    version="2.0.0-masumi"
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
masumi_client: Optional[MasumiPaymentClient] = None

# Team wallet mapping (will be populated from Masumi)
TEAM_WALLETS = {}

# Job tracking
active_jobs: Dict[str, dict] = {}

class PaymentRequest(BaseModel):
    from_address: str = Field(..., description="Source wallet address")
    to_address: str = Field(..., description="Destination wallet address")
    amount: int = Field(..., gt=0, description="Amount in lovelace")
    metadata: Optional[Dict] = Field(None, description="Optional transaction metadata")

class PaymentResponse(BaseModel):
    job_id: str
    payment_id: str
    tx_hash: Optional[str] = None
    status: str
    estimated_confirmation_time: int

@app.on_event("startup")
async def startup_event():
    """Initialize Masumi client and load team wallets"""
    global masumi_client, TEAM_WALLETS
    
    try:
        # Initialize Masumi client
        masumi_client = MasumiPaymentClient()
        logger.info("✅ Masumi Payment Client initialized")
        
        # Load existing wallets
        wallets = masumi_client.list_wallets()
        for wallet in wallets:
            TEAM_WALLETS[wallet["name"]] = wallet
        
        logger.info(f"✅ Loaded {len(TEAM_WALLETS)} team wallets from Masumi")
        
        # Create team wallets if they don't exist
        required_wallets = [
            ("Agent_A_Wallet", "Wallet for AI Agent A payments and triggers"),
            ("Agent_B_Wallet", "Wallet for AI Agent B receipts and confirmations"),
            ("Arduino_A_Wallet", "Wallet for Arduino A hardware trigger payments"),
            ("Arduino_B_Wallet", "Wallet for Arduino B hardware response confirmations")
        ]
        
        for wallet_name, description in required_wallets:
            if wallet_name not in TEAM_WALLETS:
                try:
                    new_wallet = masumi_client.create_wallet(wallet_name, description)
                    TEAM_WALLETS[wallet_name] = new_wallet
                    logger.info(f"✅ Created wallet: {wallet_name}")
                except Exception as e:
                    logger.warning(f"Could not create wallet {wallet_name}: {e}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Masumi integration: {e}")
        raise e

@app.get("/")
async def root():
    """Health check endpoint"""
    try:
        return {
            "service": "Arduino-to-Cardano Payment Service",
            "mode": "real-masumi",
            "status": "running",
            "version": "2.0.0-masumi",
            "masumi_connection": "connected" if masumi_client else "disconnected",
            "team_wallets": len(TEAM_WALLETS),
            "active_jobs": len(active_jobs),
            "endpoints": {
                "send_payment": "POST /send_payment",
                "tx_status": "GET /tx_status/{job_id}",
                "wallets": "GET /wallets",
                "wallet_balance": "GET /wallet/{wallet_name}/balance"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service health check failed: {str(e)}")

@app.get("/wallets")
async def list_team_wallets():
    """List all team wallets"""
    wallet_info = {}
    for name, wallet in TEAM_WALLETS.items():
        try:
            balance = masumi_client.get_wallet_balance(wallet["id"])
            wallet_info[name] = {
                "id": wallet["id"],
                "address": wallet["address"],
                "balance_ada": balance.get("balance_ada", 0),
                "balance_lovelace": balance.get("balance_lovelace", 0)
            }
        except Exception as e:
            wallet_info[name] = {
                "id": wallet["id"],
                "address": wallet.get("address", "unknown"),
                "error": str(e)
            }
    
    return {"wallets": wallet_info}

@app.post("/send_payment", response_model=PaymentResponse)
async def send_payment(payment: PaymentRequest, background_tasks: BackgroundTasks):
    """Send payment via Masumi Payment Service"""
    try:
        if not masumi_client:
            raise HTTPException(status_code=503, detail="Masumi client not initialized")
        
        # Find source wallet by address
        from_wallet = None
        for wallet in TEAM_WALLETS.values():
            if wallet.get("address") == payment.from_address:
                from_wallet = wallet
                break
        
        if not from_wallet:
            raise HTTPException(status_code=400, detail="Source wallet not found in team wallets")
        
        # Generate job ID
        job_id = f"masumi_job_{uuid.uuid4().hex[:16]}"
        
        # Send payment via Masumi
        masumi_payment = masumi_client.send_payment(
            from_wallet_id=from_wallet["id"],
            to_address=payment.to_address,
            amount=payment.amount,
            metadata=payment.metadata
        )
        
        # Store job data
        active_jobs[job_id] = {
            "job_id": job_id,
            "payment_id": masumi_payment["id"],
            "from_wallet": from_wallet["name"],
            "to_address": payment.to_address,
            "amount": payment.amount,
            "metadata": payment.metadata,
            "status": "submitted",
            "created_at": datetime.now(),
            "masumi_payment": masumi_payment
        }
        
        return PaymentResponse(
            job_id=job_id,
            payment_id=masumi_payment["id"],
            tx_hash=masumi_payment.get("tx_hash"),
            status="submitted",
            estimated_confirmation_time=60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")

@app.get("/tx_status/{job_id}")
async def get_transaction_status(job_id: str):
    """Get transaction status from Masumi"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job_data = active_jobs[job_id]
    payment_id = job_data["payment_id"]
    
    try:
        # Get current status from Masumi
        masumi_status = masumi_client.get_payment_status(payment_id)
        
        # Update job data
        job_data.update({
            "status": masumi_status.get("status", "unknown"),
            "tx_hash": masumi_status.get("tx_hash"),
            "confirmations": masumi_status.get("confirmations", 0),
            "confirmed_at": masumi_status.get("confirmed_at")
        })
        
        return job_data
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return job_data  # Return cached data if Masumi is unavailable

@app.get("/wallet/{wallet_name}/balance")
async def get_wallet_balance(wallet_name: str):
    """Get wallet balance by name"""
    if wallet_name not in TEAM_WALLETS:
        raise HTTPException(status_code=404, detail=f"Wallet {wallet_name} not found")
    
    try:
        wallet = TEAM_WALLETS[wallet_name]
        balance = masumi_client.get_wallet_balance(wallet["id"])
        
        return {
            "wallet_name": wallet_name,
            "address": wallet["address"],
            "balance_lovelace": balance.get("balance_lovelace", 0),
            "balance_ada": balance.get("balance_ada", 0)
        }
        
    except Exception as e:
        logger.error(f"Balance query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Balance query failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PAYMENT_SERVICE_PORT", "8001"))
    host = os.getenv("PAYMENT_SERVICE_HOST", "localhost")
    
    print(f"""
🚀 Real Payment Service Starting (Masumi Integration)...

🌐 Service URL: http://{host}:{port}
📋 API Docs: http://{host}:{port}/docs
🔍 Health Check: http://{host}:{port}/

🔗 Masumi Integration:
• Payment Service: http://localhost:3001
• Registry Service: http://localhost:3000
• Admin Dashboard: http://localhost:3001/admin

⚠️  REAL MODE - Uses actual Masumi + Cardano preprod!
    """)
    
    uvicorn.run(
        "real_payment_service:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
```

### Step 10: Test Complete Integration

Create `test_masumi_integration.py`:

```python
import requests
import time
import json

def test_complete_integration():
    """Test the complete Masumi + Arduino-to-Cardano integration"""
    print("🧪 Testing Complete Masumi Integration...")
    print("=" * 60)
    
    # Test Masumi Payment Service directly
    print("1. Testing Masumi Payment Service...")
    try:
        masumi_response = requests.get("http://localhost:3001/health")
        if masumi_response.status_code == 200:
            print("   ✅ Masumi Payment Service: Connected")
        else:
            print("   ❌ Masumi Payment Service: Error")
            return False
    except:
        print("   ❌ Masumi Payment Service: Not running")
        return False
    
    # Test our integrated payment service
    print("2. Testing Integrated Payment Service...")
    try:
        response = requests.get("http://localhost:8001/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Payment Service: {data['mode']}")
            print(f"   ✅ Team Wallets: {data['team_wallets']}")
        else:
            print("   ❌ Payment Service: Error")
            return False
    except:
        print("   ❌ Payment Service: Not running")
        return False
    
    # Test wallet listing
    print("3. Testing Wallet Management...")
    try:
        response = requests.get("http://localhost:8001/wallets")
        if response.status_code == 200:
            wallets = response.json()["wallets"]
            print(f"   ✅ Found {len(wallets)} team wallets")
            for name, wallet in wallets.items():
                if "error" not in wallet:
                    print(f"   • {name}: {wallet['balance_ada']} ADA")
                else:
                    print(f"   • {name}: Error - {wallet['error']}")
        else:
            print("   ❌ Wallet listing failed")
    except Exception as e:
        print(f"   ❌ Wallet listing error: {e}")
    
    # Test payment flow (if wallets have balance)
    print("4. Testing Payment Flow...")
    try:
        # Get Agent A wallet address
        wallets_response = requests.get("http://localhost:8001/wallets")
        wallets = wallets_response.json()["wallets"]
        
        agent_a_wallet = wallets.get("Agent_A_Wallet")
        agent_b_wallet = wallets.get("Agent_B_Wallet")
        
        if agent_a_wallet and agent_b_wallet and agent_a_wallet.get("balance_ada", 0) > 1:
            print("   💰 Attempting test payment...")
            
            payment_data = {
                "from_address": agent_a_wallet["address"],
                "to_address": agent_b_wallet["address"],
                "amount": 1000000,  # 1 ADA
                "metadata": {
                    "test": "masumi_integration",
                    "agent": "Agent_A",
                    "purpose": "Real blockchain test"
                }
            }
            
            payment_response = requests.post("http://localhost:8001/send_payment", json=payment_data)
            if payment_response.status_code == 200:
                result = payment_response.json()
                job_id = result["job_id"]
                payment_id = result["payment_id"]
                
                print(f"   ✅ Payment submitted!")
                print(f"   • Job ID: {job_id}")
                print(f"   • Payment ID: {payment_id}")
                
                # Monitor status
                print("   🔍 Monitoring confirmation...")
                for i in range(6):  # Check for 1 minute
                    time.sleep(10)
                    status_response = requests.get(f"http://localhost:8001/tx_status/{job_id}")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"   • Status: {status['status']}")
                        
                        if status['status'] == 'confirmed':
                            tx_hash = status.get('tx_hash')
                            print(f"   ✅ Payment confirmed!")
                            if tx_hash:
                                print(f"   🔗 TX Hash: {tx_hash}")
                                print(f"   🌐 Explorer: https://preprod.cardanoscan.io/transaction/{tx_hash}")
                            break
                    else:
                        print(f"   ⚠️  Status check failed")
            else:
                print(f"   ❌ Payment failed: {payment_response.text}")
        else:
            print("   ⚠️  Insufficient balance for test payment")
            print("   💡 Fund Agent_A_Wallet with preprod ADA to test payments")
    
    except Exception as e:
        print(f"   ❌ Payment test error: {e}")
    
    print("\n🎯 Integration Test Complete!")
    print("\nNext steps:")
    print("1. Fund wallets with preprod ADA from faucet")
    print("2. Test with team members' integration code")
    print("3. Monitor transactions on Cardano Explorer")

if __name__ == "__main__":
    test_complete_integration()
```

## 🎯 Quick Start Commands (Updated)

```bash
# 1. Clone and setup Masumi
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git
cd masumi-services-dev-quickstart
cp .env.example .env
# Edit .env with your Blockfrost API key and other settings

# 2. Start Masumi services
docker compose up -d

# 3. Start our integrated payment service
cd ../blockchain
python src/real_payment_service.py

# 4. Test complete integration
python test_masumi_integration.py
```

## 🔍 Verification Checklist

- [ ] **Masumi Payment Service**: Running on http://localhost:3001 ✓
- [ ] **Masumi Registry Service**: Running on http://localhost:3000 ✓
- [ ] **PostgreSQL Database**: Running on localhost:5432 ✓
- [ ] **Blockfrost API**: Connected and authenticated ✓
- [ ] **Team Wallets**: Created in Masumi ✓
- [ ] **Payment Service**: Integrated with Masumi ✓
- [ ] **Test Payments**: Working end-to-end ✓

## 🌐 Service URLs

- **Masumi Payment API**: http://localhost:3001/docs
- **Masumi Admin Dashboard**: http://localhost:3001/admin
- **Masumi Registry API**: http://localhost:3000/docs
- **Our Payment Service**: http://localhost:8001/docs
- **Cardano Explorer**: https://preprod.cardanoscan.io/

This updated setup integrates with the official Masumi Network infrastructure for production-ready blockchain payments!