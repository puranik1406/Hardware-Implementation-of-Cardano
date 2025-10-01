"""
Sokosumi Integration Service for Arduino-Brisumi-Satoshi System
Provides web search and research capabilities using Sokosumi AI agents
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SOKOSUMI_API_KEY = os.getenv("SOKOSUMI_API_KEY", "TBLHiLvybvTcoBzujMOzIoKoEVWrSAEXpWYsTByfTlfKfqAfsxwRlJoeWOnEgQZU")
SOKOSUMI_BASE_URL = "https://app.sokosumi.com/api"
PORT = int(os.getenv("SOKOSUMI_SERVICE_PORT", 7003))

# Create FastAPI app
app = FastAPI(title="Sokosumi Integration Service")

# Output directory for reports
REPORTS_DIR = Path(__file__).parent / "research_reports"
REPORTS_DIR.mkdir(exist_ok=True)

class ResearchRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None
    max_credits: int = 1000
    name: Optional[str] = None

class JobStatusRequest(BaseModel):
    job_id: str

class SokosumiClient:
    """Client for interacting with Sokosumi API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = SOKOSUMI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized Sokosumi client with API key: {api_key[:8]}...")
    
    async def list_agents(self) -> list:
        """List all available agents"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/agents",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            raise
    
    async def get_agent_schema(self, agent_id: str) -> dict:
        """Get input schema for specific agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/agents/{agent_id}/input-schema",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting agent schema: {e}")
            raise
    
    async def create_job(self, agent_id: str, input_data: dict, max_credits: int = 1000, name: str = None) -> dict:
        """Create a new job"""
        try:
            payload = {
                "agentId": agent_id,
                "maxAcceptedCredits": max_credits,
                "input": input_data
            }
            if name:
                payload["name"] = name
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/jobs",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise
    
    async def get_job(self, job_id: str) -> dict:
        """Get job status and results"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting job: {e}")
            raise
    
    async def get_user_profile(self) -> dict:
        """Get current user profile"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise

# Global client instance
sokosumi_client = SokosumiClient(SOKOSUMI_API_KEY)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sokosumi-integration",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/agents")
async def list_agents():
    """List all available Sokosumi agents"""
    try:
        agents = await sokosumi_client.list_agents()
        logger.info(f"Retrieved {len(agents)} agents")
        return {
            "success": True,
            "agents": agents,
            "count": len(agents)
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error listing agents: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Sokosumi API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}/schema")
async def get_agent_schema(agent_id: str):
    """Get input schema for a specific agent"""
    try:
        schema = await sokosumi_client.get_agent_schema(agent_id)
        logger.info(f"Retrieved schema for agent {agent_id}")
        return {
            "success": True,
            "agent_id": agent_id,
            "schema": schema
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting schema: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Sokosumi API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error getting agent schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def create_research_job(request: ResearchRequest):
    """
    Create a research job using Sokosumi AI agents
    This can be called after a successful transaction to generate reports
    """
    try:
        # If no agent specified, find a suitable research agent
        if not request.agent_id:
            agents = await sokosumi_client.list_agents()
            research_keywords = ["research", "web", "search", "linkedin", "company"]
            
            research_agent = None
            for agent in agents:
                name_lower = agent.get("name", "").lower()
                desc_lower = agent.get("description", "").lower()
                if any(kw in name_lower or kw in desc_lower for kw in research_keywords):
                    research_agent = agent
                    break
            
            if not research_agent and agents:
                research_agent = agents[0]  # Use first available agent
            
            if not research_agent:
                raise HTTPException(status_code=404, detail="No agents available")
            
            agent_id = research_agent["id"]
            logger.info(f"Auto-selected agent: {research_agent['name']} (ID: {agent_id})")
        else:
            agent_id = request.agent_id
        
        # Get agent schema
        schema = await sokosumi_client.get_agent_schema(agent_id)
        
        # Prepare input data based on schema
        if schema and isinstance(schema, dict):
            first_key = next(iter(schema.keys()), "query")
            input_data = {first_key: request.query}
        else:
            input_data = {"query": request.query}
        
        # Create job
        job = await sokosumi_client.create_job(
            agent_id=agent_id,
            input_data=input_data,
            max_credits=request.max_credits,
            name=request.name or f"Research: {request.query[:50]}"
        )
        
        job_id = job.get("id")
        logger.info(f"Created research job: {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "agent_id": agent_id,
            "status": job.get("status"),
            "message": "Research job created successfully. Use /api/job/{job_id} to check status."
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error creating job: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Sokosumi API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error creating research job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get status and results of a job"""
    try:
        job = await sokosumi_client.get_job(job_id)
        
        status = job.get("status")
        logger.info(f"Job {job_id} status: {status}")
        
        # If completed, save report
        if status == "completed" and job.get("output"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = REPORTS_DIR / f"research_report_{job_id}_{timestamp}.txt"
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write(f"Sokosumi Research Report\n")
                f.write(f"Job ID: {job_id}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 70 + "\n\n")
                
                output = job.get("output", {})
                if isinstance(output, dict):
                    for key, value in output.items():
                        f.write(f"\n{key.upper()}:\n")
                        f.write("-" * 70 + "\n")
                        f.write(str(value) + "\n")
                else:
                    f.write(str(output) + "\n")
            
            logger.info(f"Saved report to {report_file}")
            job["report_file"] = str(report_file.absolute())
        
        return {
            "success": True,
            "job": job
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting job: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Sokosumi API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/profile")
async def get_user_profile():
    """Get current user profile"""
    try:
        profile = await sokosumi_client.get_user_profile()
        logger.info(f"Retrieved user profile: {profile.get('email', 'N/A')}")
        return {
            "success": True,
            "profile": profile
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting profile: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Sokosumi API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transaction-research")
async def post_transaction_research(tx_hash: str, agent_ids: list[str]):
    """
    Automatically generate research report after a successful transaction
    This integrates with the Cardano transaction pipeline
    """
    try:
        query = f"Generate a comprehensive blockchain transaction analysis report for transaction hash {tx_hash}. Include transaction details, participants, and network statistics."
        
        # Create research job
        agents = await sokosumi_client.list_agents()
        if not agents:
            raise HTTPException(status_code=404, detail="No agents available")
        
        # Use first available agent
        agent = agents[0]
        agent_id = agent["id"]
        
        # Get schema and create job
        schema = await sokosumi_client.get_agent_schema(agent_id)
        first_key = next(iter(schema.keys()), "query") if schema else "query"
        input_data = {first_key: query}
        
        job = await sokosumi_client.create_job(
            agent_id=agent_id,
            input_data=input_data,
            max_credits=1000,
            name=f"Transaction Analysis: {tx_hash[:8]}"
        )
        
        logger.info(f"Created post-transaction research job: {job.get('id')}")
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "job_id": job.get("id"),
            "message": "Post-transaction research initiated"
        }
        
    except Exception as e:
        logger.error(f"Error in post-transaction research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("Sokosumi Integration Service")
    logger.info(f"Port: {PORT}")
    logger.info(f"API Key: {SOKOSUMI_API_KEY[:8]}...")
    logger.info(f"Reports Directory: {REPORTS_DIR.absolute()}")
    logger.info("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
