"""
ActuAlte Robotics Research Script using Sokosumi MCP
Generates a comprehensive LinkedIn research report about ActuAlte Robotics company
"""

import os
import sys
import json
import time
import asyncio
import httpx
from pathlib import Path

# Configuration
SOKOSUMI_API_KEY = "TBLHiLvybvTcoBzujMOzIoKoEVWrSAEXpWYsTByfTlfKfqAfsxwRlJoeWOnEgQZU"
SOKOSUMI_BASE_URL = "https://app.sokosumi.com/api"
OUTPUT_DIR = Path("research_reports")
OUTPUT_DIR.mkdir(exist_ok=True)

class SokosumiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = SOKOSUMI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def list_agents(self):
        """List all available Sokosumi agents"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/agents",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_agent_schema(self, agent_id: str):
        """Get input schema for a specific agent"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/agents/{agent_id}/input-schema",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def create_job(self, agent_id: str, input_data: dict, max_credits: int = 1000, name: str = None):
        """Create a job for an agent"""
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
    
    async def get_job(self, job_id: str):
        """Get job status and results"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/jobs/{job_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def wait_for_job(self, job_id: str, max_wait: int = 600):
        """Wait for job completion"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            job = await self.get_job(job_id)
            status = job.get("status")
            
            print(f"Job status: {status}")
            
            if status in ["completed", "failed", "cancelled"]:
                return job
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        raise TimeoutError(f"Job {job_id} did not complete within {max_wait} seconds")

async def find_research_agent(client: SokosumiClient):
    """Find the best agent for LinkedIn/web research"""
    print("🔍 Finding research agents...")
    agents = await client.list_agents()
    
    # Look for LinkedIn, research, or web search agents
    research_keywords = ["linkedin", "research", "web", "search", "company", "profile"]
    
    research_agents = []
    for agent in agents:
        name_lower = agent.get("name", "").lower()
        desc_lower = agent.get("description", "").lower()
        tags = [tag.lower() for tag in agent.get("tags", [])]
        
        if any(keyword in name_lower or keyword in desc_lower or keyword in " ".join(tags) 
               for keyword in research_keywords):
            research_agents.append(agent)
    
    if not research_agents:
        print("⚠️ No specific research agent found, using first available agent")
        return agents[0] if agents else None
    
    # Sort by relevance and price
    research_agents.sort(key=lambda x: x.get("price", 9999))
    return research_agents[0]

async def generate_actualte_report():
    """Generate comprehensive research report about ActuAlte Robotics"""
    print("=" * 70)
    print("ActuAlte Robotics Research Report Generator")
    print("Using Sokosumi MCP AI Agents")
    print("=" * 70)
    
    client = SokosumiClient(SOKOSUMI_API_KEY)
    
    try:
        # Step 1: Find suitable research agent
        agent = await find_research_agent(client)
        if not agent:
            print("❌ No agents available")
            return
        
        print(f"\n✅ Selected Agent: {agent['name']}")
        print(f"   ID: {agent['id']}")
        print(f"   Description: {agent.get('description', 'N/A')}")
        print(f"   Price: {agent.get('price', 'N/A')} credits")
        
        # Step 2: Get agent input schema
        print("\n📋 Getting agent input schema...")
        schema = await client.get_agent_schema(agent['id'])
        print(f"   Input Schema: {json.dumps(schema, indent=2)}")
        
        # Step 3: Prepare research query
        research_query = {
            "company": "ActuAlte Robotics",
            "platform": "LinkedIn",
            "query": "ActuAlte Robotics company profile, products, services, team, and recent activities on LinkedIn",
            "search_terms": "ActuAlte Robotics LinkedIn",
            "depth": "comprehensive",
            "include": ["company_profile", "products", "services", "team", "posts", "updates"]
        }
        
        # Adapt to agent's schema (use first available field)
        if schema and isinstance(schema, dict):
            first_key = next(iter(schema.keys()), "query")
            input_data = {first_key: json.dumps(research_query)}
        else:
            input_data = {"query": "Research ActuAlte Robotics company on LinkedIn - provide comprehensive information about their company profile, products, services, team members, and recent posts/updates"}
        
        # Step 4: Create job
        print(f"\n🚀 Creating research job...")
        job = await client.create_job(
            agent_id=agent['id'],
            input_data=input_data,
            max_credits=1000,
            name="ActuAlte Robotics LinkedIn Research"
        )
        
        job_id = job.get("id")
        print(f"   Job Created: {job_id}")
        print(f"   Status: {job.get('status')}")
        
        # Step 5: Wait for completion
        print(f"\n⏳ Waiting for job completion (this may take several minutes)...")
        completed_job = await client.wait_for_job(job_id)
        
        # Step 6: Extract results
        print(f"\n✅ Job completed!")
        print(f"   Final Status: {completed_job.get('status')}")
        print(f"   Credits Used: {completed_job.get('price', 'N/A')}")
        
        output = completed_job.get("output", {})
        
        # Step 7: Save report
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = OUTPUT_DIR / f"actualte_robotics_research_{timestamp}.txt"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("ActuAlte Robotics - LinkedIn Research Report\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Agent: {agent['name']} (ID: {agent['id']})\n")
            f.write(f"Job ID: {job_id}\n")
            f.write("=" * 70 + "\n\n")
            
            if isinstance(output, dict):
                for key, value in output.items():
                    f.write(f"\n{key.upper()}:\n")
                    f.write("-" * 70 + "\n")
                    f.write(str(value) + "\n")
            else:
                f.write(str(output) + "\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("End of Report\n")
            f.write("=" * 70 + "\n")
        
        print(f"\n📄 Report saved to: {report_file}")
        print(f"\n📊 Summary:")
        print(f"   - Research completed successfully")
        print(f"   - Agent: {agent['name']}")
        print(f"   - Job ID: {job_id}")
        print(f"   - Credits used: {completed_job.get('price', 'N/A')}")
        print(f"   - Report location: {report_file.absolute()}")
        
        return report_file
        
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🤖 Starting ActuAlte Robotics Research with Sokosumi AI...")
    asyncio.run(generate_actualte_report())
