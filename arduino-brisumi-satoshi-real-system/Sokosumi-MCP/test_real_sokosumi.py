"""
Real Sokosumi MCP Integration - Plant Health Analysis
Uses the official MCP URL for direct API access
"""

import os
import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sokosumi MCP Configuration
SOKOSUMI_MCP_URL = os.getenv('SOKOSUMI_MCP_URL', 'https://mcp.sokosumi.com/mcp?api_key=xwcmVJcusixxmlPuNmqYWnBJlXMvhwDCelosFVMoGopdPZLpDZmZjpICLkNmKBzQ&network=mainnet')
SOKOSUMI_API_KEY = os.getenv('SOKOSUMI_API_KEY', 'xwcmVJcusixxmlPuNmqYWnBJlXMvhwDCelosFVMoGopdPZLpDZmZjpICLkNmKBzQ')
SOKOSUMI_NETWORK = os.getenv('SOKOSUMI_NETWORK', 'mainnet')

# Report Storage
REPORTS_DIR = Path("../plant_reports")
REPORTS_DIR.mkdir(exist_ok=True)

class SokosumiMCPClient:
    """Client for Sokosumi MCP server using the direct URL approach"""
    
    def __init__(self, mcp_url: str = None, api_key: str = None):
        self.mcp_url = mcp_url or SOKOSUMI_MCP_URL
        self.api_key = api_key or SOKOSUMI_API_KEY
        self.base_url = "https://app.sokosumi.com/api"
        
        # Extract API key from URL if embedded
        if '?api_key=' in self.mcp_url:
            parts = self.mcp_url.split('?api_key=')
            if len(parts) > 1:
                self.api_key = parts[1].split('&')[0]
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"✅ Sokosumi MCP Client initialized")
        print(f"   API Key: {self.api_key[:10]}...{self.api_key[-10:]}")
        print(f"   Network: {SOKOSUMI_NETWORK}")
    
    async def test_connection(self):
        """Test connection to Sokosumi API"""
        try:
            # Try direct API with Bearer token
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try /v1/agents endpoint
                response = await client.get(
                    f"{self.base_url}/v1/agents",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    agents = response.json()
                    print(f"✅ Connection successful! Found {len(agents)} agents")
                    return True, agents
                
                # Try without /v1
                response = await client.get(
                    f"{self.base_url}/agents",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    agents = response.json()
                    print(f"✅ Connection successful! Found {len(agents)} agents")
                    return True, agents
                
                # Try with API key as query parameter
                response = await client.get(
                    f"{self.base_url}/agents?api_key={self.api_key}"
                )
                
                if response.status_code == 200:
                    agents = response.json()
                    print(f"✅ Connection successful! Found {len(agents)} agents")
                    return True, agents
                else:
                    print(f"⚠️ All API attempts returned status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return False, None
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False, None
    
    async def get_user_profile(self):
        """Get user profile information"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/user/profile",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"⚠️ Profile request returned {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ Profile request failed: {e}")
            return None
    
    async def list_agents(self):
        """List all available Sokosumi agents"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/agents",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"⚠️ Agents list returned {response.status_code}: {response.text[:200]}")
                    return []
                    
        except Exception as e:
            print(f"❌ Failed to list agents: {e}")
            return []
    
    async def create_plant_analysis_job(self, plant_data: dict):
        """
        Create a job for plant health analysis
        """
        try:
            # Find a suitable agent for plant analysis
            agents = await self.list_agents()
            if not agents:
                print("⚠️ No agents available, using local analysis")
                return None
            
            # Look for research/analysis agents
            suitable_agent = None
            for agent in agents:
                name_lower = agent.get('name', '').lower()
                desc_lower = agent.get('description', '').lower()
                
                if any(keyword in name_lower or keyword in desc_lower 
                       for keyword in ['research', 'analysis', 'data', 'report']):
                    suitable_agent = agent
                    break
            
            if not suitable_agent:
                suitable_agent = agents[0]  # Use first available agent
            
            print(f"\n📊 Using agent: {suitable_agent['name']}")
            print(f"   ID: {suitable_agent['id']}")
            print(f"   Price: {suitable_agent.get('price', 'N/A')} credits")
            
            # Prepare job input
            job_input = {
                "query": f"""Analyze this Aloe Vera plant health data and provide recommendations:
                
Plant Type: {plant_data['plant_type']}
Soil Moisture: {plant_data['sensor_data']['soil_moisture']}%
Temperature: {plant_data['sensor_data']['temperature']}°C
Humidity: {plant_data['sensor_data']['humidity']}%

Please provide:
1. Health status assessment
2. Watering recommendations
3. Any warnings or concerns
4. Care tips specific to Aloe Vera
"""
            }
            
            # Create job
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/jobs",
                    headers=self.headers,
                    json={
                        "agentId": suitable_agent['id'],
                        "maxAcceptedCredits": 100,
                        "input": job_input,
                        "name": f"Plant Health Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                )
                
                if response.status_code in [200, 201]:
                    job = response.json()
                    print(f"✅ Job created: {job.get('id')}")
                    return job
                else:
                    print(f"⚠️ Job creation failed: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"❌ Failed to create job: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def wait_for_job(self, job_id: str, max_wait: int = 300):
        """Wait for job completion"""
        print(f"\n⏳ Waiting for job {job_id} to complete...")
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                while (datetime.now() - start_time).seconds < max_wait:
                    response = await client.get(
                        f"{self.base_url}/jobs/{job_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        job = response.json()
                        status = job.get('status')
                        print(f"   Status: {status}", end='\r')
                        
                        if status in ['completed', 'failed', 'cancelled']:
                            print(f"\n✅ Job {status}!")
                            return job
                    
                    await asyncio.sleep(5)  # Check every 5 seconds
                
                print(f"\n⚠️ Job timeout after {max_wait}s")
                return None
                
        except Exception as e:
            print(f"\n❌ Failed to check job status: {e}")
            return None

async def analyze_plant_with_sokosumi(plant_data: dict):
    """
    Analyze plant health using real Sokosumi MCP
    """
    print("\n" + "=" * 70)
    print("🤖 SOKOSUMI MCP - REAL PLANT HEALTH ANALYSIS")
    print("=" * 70)
    
    client = SokosumiMCPClient()
    
    # Test connection
    print("\n🔌 Testing Sokosumi connection...")
    connected, agents = await client.test_connection()
    
    if not connected:
        print("\n⚠️ Cannot connect to Sokosumi - using local analysis")
        return None
    
    # Get user profile
    print("\n👤 Fetching user profile...")
    profile = await client.get_user_profile()
    if profile:
        print(f"   User: {profile.get('name', 'N/A')}")
        print(f"   Email: {profile.get('email', 'N/A')}")
    
    # Create analysis job
    print("\n🚀 Creating plant analysis job...")
    job = await client.create_plant_analysis_job(plant_data)
    
    if not job:
        print("\n⚠️ Could not create job - using local analysis")
        return None
    
    # Wait for results
    completed_job = await client.wait_for_job(job['id'])
    
    if completed_job and completed_job.get('status') == 'completed':
        output = completed_job.get('output', {})
        print("\n✅ Analysis complete!")
        print("\n📊 Sokosumi AI Analysis:")
        print("-" * 70)
        print(json.dumps(output, indent=2))
        print("-" * 70)
        return output
    else:
        print("\n⚠️ Job did not complete successfully")
        return None

async def test_real_sokosumi():
    """Test real Sokosumi integration with plant data"""
    
    # Mock plant data for testing
    plant_data = {
        "plant_type": "Aloe Vera",
        "plant_id": "aloe_001",
        "location": "Indoor Garden - Arduino Station",
        "sensor_data": {
            "soil_moisture": 65,
            "soil_moisture_raw": 350,
            "temperature": 24.5,
            "humidity": 55,
            "light_level": "medium",
            "digital_threshold": False
        },
        "timestamp": datetime.now().isoformat(),
        "arduino_id": "COM6"
    }
    
    print("\n📋 Plant Data:")
    print(json.dumps(plant_data, indent=2))
    
    # Analyze with Sokosumi
    result = await analyze_plant_with_sokosumi(plant_data)
    
    if result:
        print("\n🎉 SUCCESS! Sokosumi MCP is working!")
    else:
        print("\n⚠️ Sokosumi MCP not available, but system still works with local analysis")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    print("\n🌱 Testing Real Sokosumi MCP Integration")
    asyncio.run(test_real_sokosumi())
