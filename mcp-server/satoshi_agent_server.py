#!/usr/bin/env python3
"""
Satoshi AI Agent MCP Server for Arduino Masumi Network
Provides AI agent capabilities for autonomous blockchain operations
"""

import asyncio
import json
import logging
import serial
import serial.tools.list_ports
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("satoshi-agent")

# Configure logging to stderr (not stdout for MCP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Global variables for serial connections
arduino_uno_port = None
esp32_port = None

# Masumi API configuration
MASUMI_REGISTRY_URL = "http://localhost:3000"
MASUMI_PAYMENT_URL = "http://localhost:3001"

class SatoshiAgent:
    """Autonomous AI agent for blockchain operations"""
    
    def __init__(self, agent_id: str, wallet_address: str, private_key: str = None):
        self.agent_id = agent_id
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.balance = 0
        self.transaction_history = []
        self.autonomous_mode = False
        
    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "wallet_address": self.wallet_address,
            "balance": self.balance,
            "autonomous_mode": self.autonomous_mode,
            "transaction_count": len(self.transaction_history)
        }

# Active Satoshi agents
active_agents: Dict[str, SatoshiAgent] = {}

@mcp.tool()
async def detect_arduino_boards() -> str:
    """Detect connected Arduino boards (Arduino Uno and ESP32)"""
    global arduino_uno_port, esp32_port
    
    ports = serial.tools.list_ports.comports()
    detected = []
    
    for port in ports:
        port_info = {
            "port": port.device,
            "description": port.description,
            "hwid": port.hwid
        }
        
        # Try to identify Arduino Uno
        if "Arduino" in port.description or "CH340" in port.description:
            arduino_uno_port = port.device
            port_info["type"] = "Arduino Uno"
            
        # Try to identify ESP32
        elif "CP210" in port.description or "ESP32" in port.description:
            esp32_port = port.device
            port_info["type"] = "ESP32"
        else:
            port_info["type"] = "Unknown"
            
        detected.append(port_info)
    
    logger.info(f"Detected {len(detected)} serial ports")
    return json.dumps(detected, indent=2)

@mcp.tool()
async def create_satoshi_agent(agent_name: str, initial_balance: float = 1000.0) -> str:
    """Create a new autonomous Satoshi AI agent for blockchain operations"""
    
    try:
        # Register agent with Masumi Network
        async with httpx.AsyncClient() as client:
            agent_data = {
                "name": agent_name,
                "type": "satoshi_ai",
                "network": "preprod",
                "metadata": {
                    "autonomous": True,
                    "ai_powered": True,
                    "created_by": "arduino_simulator"
                }
            }
            
            response = await client.post(
                f"{MASUMI_REGISTRY_URL}/agents",
                json=agent_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                agent_info = response.json()
                
                # Create Satoshi agent
                agent = SatoshiAgent(
                    agent_id=agent_info.get("agentId", f"satoshi_{agent_name}"),
                    wallet_address=agent_info.get("walletAddress", "addr_test1..."),
                )
                agent.balance = initial_balance
                
                active_agents[agent.agent_id] = agent
                
                logger.info(f"Created Satoshi agent: {agent.agent_id}")
                return json.dumps({
                    "success": True,
                    "agent": agent.to_dict(),
                    "message": f"Satoshi AI agent '{agent_name}' created successfully"
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to register agent: {response.text}"
                })
                
    except Exception as e:
        logger.error(f"Error creating Satoshi agent: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
async def send_arduino_command(command: str, board_type: str = "uno") -> str:
    """Send command to Arduino board (Uno or ESP32)"""
    
    port = arduino_uno_port if board_type == "uno" else esp32_port
    
    if not port:
        return json.dumps({
            "success": False,
            "error": f"No {board_type} detected. Please connect your Arduino board."
        })
    
    try:
        # Connect to Arduino
        with serial.Serial(port, 115200, timeout=2) as ser:
            # Wait for Arduino to initialize
            await asyncio.sleep(2)
            
            # Send command
            ser.write(f"{command}\n".encode())
            
            # Read response
            response = ""
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < 5:  # 5 second timeout
                if ser.in_waiting:
                    line = ser.readline().decode().strip()
                    response += line + "\n"
                    if "COMPLETE" in line or "ERROR" in line:
                        break
                await asyncio.sleep(0.1)
        
        logger.info(f"Arduino {board_type} command sent: {command}")
        return json.dumps({
            "success": True,
            "board": board_type,
            "command": command,
            "response": response.strip()
        })
        
    except Exception as e:
        logger.error(f"Error communicating with Arduino {board_type}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
async def initiate_payment_from_arduino(amount: float, recipient_agent_id: str) -> str:
    """Initiate a Cardano payment from Arduino Uno and send result to ESP32"""
    
    try:
        # Step 1: Send payment command to Arduino Uno
        payment_command = f"SEND_PAYMENT:{amount}:{recipient_agent_id}"
        arduino_result = await send_arduino_command(payment_command, "uno")
        
        if not json.loads(arduino_result)["success"]:
            return arduino_result
        
        # Step 2: Process payment through Masumi Network
        sender_agent = list(active_agents.values())[0] if active_agents else None
        
        if not sender_agent:
            return json.dumps({
                "success": False,
                "error": "No active Satoshi agents available"
            })
        
        # Call Masumi Payment API
        async with httpx.AsyncClient() as client:
            payment_data = {
                "fromWalletAddress": sender_agent.wallet_address,
                "toWalletAddress": active_agents.get(recipient_agent_id, {}).wallet_address if recipient_agent_id in active_agents else "addr_test1...",
                "amount": amount,
                "metadata": {
                    "source": "arduino_uno",
                    "agent": sender_agent.agent_id,
                    "autonomous": True
                }
            }
            
            response = await client.post(
                f"{MASUMI_PAYMENT_URL}/send",
                json=payment_data,
                timeout=15.0
            )
            
            if response.status_code == 200:
                tx_result = response.json()
                tx_hash = tx_result.get("txHash", f"demo_tx_{asyncio.get_event_loop().time()}")
                
                # Step 3: Send transaction hash to ESP32
                esp32_command = f"DISPLAY_TX:{tx_hash}:{amount}:SUCCESS"
                esp32_result = await send_arduino_command(esp32_command, "esp32")
                
                # Update agent balances
                sender_agent.balance -= amount
                sender_agent.transaction_history.append({
                    "tx_hash": tx_hash,
                    "amount": -amount,
                    "type": "send",
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                return json.dumps({
                    "success": True,
                    "transaction": {
                        "tx_hash": tx_hash,
                        "amount": amount,
                        "sender": sender_agent.agent_id,
                        "recipient": recipient_agent_id,
                        "explorer_url": f"https://preprod.cardanoscan.io/transaction/{tx_hash}",
                        "arduino_response": json.loads(arduino_result),
                        "esp32_response": json.loads(esp32_result)
                    }
                })
            else:
                error_msg = f"Payment failed: {response.text}"
                
                # Send error to ESP32
                esp32_command = f"DISPLAY_TX:ERROR:{amount}:FAILED"
                await send_arduino_command(esp32_command, "esp32")
                
                return json.dumps({
                    "success": False,
                    "error": error_msg
                })
                
    except Exception as e:
        logger.error(f"Error in Arduino payment flow: {e}")
        
        # Send error to ESP32
        try:
            esp32_command = f"DISPLAY_TX:ERROR:0:FAILED"
            await send_arduino_command(esp32_command, "esp32")
        except:
            pass
            
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
async def get_agent_status() -> str:
    """Get status of all active Satoshi AI agents"""
    
    if not active_agents:
        return json.dumps({
            "active_agents": 0,
            "message": "No active Satoshi agents"
        })
    
    agents_status = []
    for agent in active_agents.values():
        # Get real balance from blockchain
        try:
            async with httpx.AsyncClient() as client:
                balance_response = await client.get(
                    f"https://preprod.koios.rest/api/v1/address_info?_address={agent.wallet_address}",
                    timeout=5.0
                )
                if balance_response.status_code == 200:
                    data = balance_response.json()
                    if data and len(data) > 0:
                        agent.balance = int(data[0].get("balance", 0)) / 1000000  # Convert lovelace to ADA
        except:
            pass  # Use cached balance if API fails
            
        agents_status.append(agent.to_dict())
    
    return json.dumps({
        "active_agents": len(active_agents),
        "agents": agents_status
    })

@mcp.tool()
async def enable_autonomous_mode(agent_id: str, enable: bool = True) -> str:
    """Enable or disable autonomous mode for a Satoshi AI agent"""
    
    if agent_id not in active_agents:
        return json.dumps({
            "success": False,
            "error": f"Agent {agent_id} not found"
        })
    
    agent = active_agents[agent_id]
    agent.autonomous_mode = enable
    
    logger.info(f"Agent {agent_id} autonomous mode: {enable}")
    
    return json.dumps({
        "success": True,
        "agent_id": agent_id,
        "autonomous_mode": enable,
        "message": f"Autonomous mode {'enabled' if enable else 'disabled'} for agent {agent_id}"
    })

if __name__ == "__main__":
    logger.info("Starting Satoshi AI Agent MCP Server...")
    logger.info("Available tools: detect_arduino_boards, create_satoshi_agent, send_arduino_command, initiate_payment_from_arduino, get_agent_status, enable_autonomous_mode")
    
    # Run the MCP server
    mcp.run(transport='stdio')