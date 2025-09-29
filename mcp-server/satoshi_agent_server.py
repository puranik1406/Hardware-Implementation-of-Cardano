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
    """Autonomous AI agent for blockchain operations with decision-making capabilities"""
    
    def __init__(self, agent_id: str, wallet_address: str, private_key: str = None):
        self.agent_id = agent_id
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.balance = 0
        self.transaction_history = []
        self.autonomous_mode = False
        self.strategy = "conservative"
        self.decision_threshold = 0.7
        self.max_transaction_amount = 100
        self.last_decision_time = 0
        self.decision_cooldown = 30  # seconds between decisions
        self.market_sentiment = 0.5  # 0-1 scale
        self.risk_tolerance = 0.3    # 0-1 scale
        
    def should_make_transaction(self) -> dict:
        """AI decision engine - determines if agent should make a transaction"""
        import random
        import time
        
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_decision_time < self.decision_cooldown:
            return {"should_transact": False, "reason": "Cooldown period active"}
        
        # Simulate AI analysis factors
        factors = {
            "balance_sufficient": self.balance > 1.0,
            "market_conditions": random.uniform(0, 1) > 0.3,  # Simulated market analysis
            "network_congestion": random.uniform(0, 1) < 0.8,  # Low congestion is good
            "risk_assessment": random.uniform(0, 1) < self.risk_tolerance + 0.4,
            "opportunity_detected": random.uniform(0, 1) > 0.6,
            "sentiment_positive": self.market_sentiment > 0.4
        }
        
        # Calculate confidence score
        confidence = sum(factors.values()) / len(factors)
        
        # Make decision based on strategy
        if self.strategy == "aggressive":
            should_transact = confidence > 0.4
            amount = min(self.max_transaction_amount, self.balance * random.uniform(0.05, 0.15))
        elif self.strategy == "conservative":
            should_transact = confidence > 0.7
            amount = min(self.max_transaction_amount, self.balance * random.uniform(0.02, 0.08))
        else:  # balanced
            should_transact = confidence > 0.55
            amount = min(self.max_transaction_amount, self.balance * random.uniform(0.03, 0.12))
        
        if should_transact:
            self.last_decision_time = current_time
            
        return {
            "should_transact": should_transact,
            "confidence": confidence,
            "amount": round(amount, 2) if should_transact else 0,
            "factors": factors,
            "reason": f"AI analysis complete - Confidence: {confidence:.2f}"
        }
    
    def update_market_sentiment(self, sentiment: float):
        """Update agent's market sentiment (0-1 scale)"""
        self.market_sentiment = max(0, min(1, sentiment))
        
    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "wallet_address": self.wallet_address,
            "balance": self.balance,
            "autonomous_mode": self.autonomous_mode,
            "strategy": getattr(self, 'strategy', 'conservative'),
            "transaction_count": len(self.transaction_history),
            "market_sentiment": getattr(self, 'market_sentiment', 0.5),
            "risk_tolerance": getattr(self, 'risk_tolerance', 0.3),
            "last_decision": getattr(self, 'last_decision_time', 0)
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
async def create_satoshi_agent(agent_name: str, initial_balance: float = 1000.0, strategy: str = "conservative") -> str:
    """Create a new autonomous Satoshi AI agent for blockchain operations with trading strategy"""
    
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
                    "created_by": "arduino_simulator",
                    "strategy": strategy
                }
            }
            
            response = await client.post(
                f"{MASUMI_REGISTRY_URL}/agents",
                json=agent_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                agent_info = response.json()
                
                # Create Satoshi agent with AI capabilities
                agent = SatoshiAgent(
                    agent_id=agent_info.get("agentId", f"satoshi_{agent_name}_{int(time.time())}"),
                    wallet_address=agent_info.get("walletAddress", "addr_test1qrffhpxs9ky88sxfm9788mr8a4924e0uhl4fexvy9z5pt084p3q2uhgh9wvft4ejrjhx5yes2xpmy2cuufmzljdwtf7qvgt5rz"),
                )
                agent.balance = initial_balance
                agent.strategy = strategy
                agent.decision_threshold = 0.7 if strategy == "conservative" else 0.5
                agent.max_transaction_amount = initial_balance * 0.1  # Max 10% per transaction
                
                active_agents[agent.agent_id] = agent
                
                logger.info(f"Created Satoshi AI agent: {agent.agent_id} with {strategy} strategy")
                return json.dumps({
                    "success": True,
                    "agent": agent.to_dict(),
                    "message": f"Satoshi AI agent '{agent_name}' created successfully with {strategy} strategy"
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

@mcp.tool()
async def ai_agent_decision_cycle() -> str:
    """Run AI decision cycle for all autonomous agents - they decide when to make transactions"""
    
    results = []
    
    for agent in active_agents.values():
        if not agent.autonomous_mode:
            continue
            
        try:
            # Agent makes AI decision
            decision = agent.should_make_transaction()
            
            agent_result = {
                "agent_id": agent.agent_id,
                "decision": decision,
                "action_taken": None
            }
            
            if decision["should_transact"]:
                # Agent decides to make a transaction
                amount = decision["amount"]
                
                logger.info(f"🤖 Agent {agent.agent_id} decided to transact {amount} ADA (Confidence: {decision['confidence']:.2f})")
                
                # Execute autonomous transaction
                tx_result = await autonomous_agent_transaction(agent, amount)
                agent_result["action_taken"] = tx_result
                
                # Update agent's transaction history
                agent.transaction_history.append({
                    "timestamp": asyncio.get_event_loop().time(),
                    "amount": amount,
                    "decision_confidence": decision["confidence"],
                    "tx_result": tx_result,
                    "autonomous": True
                })
                
            results.append(agent_result)
            
        except Exception as e:
            logger.error(f"Error in AI decision cycle for agent {agent.agent_id}: {e}")
            results.append({
                "agent_id": agent.agent_id,
                "error": str(e)
            })
    
    return json.dumps({
        "success": True,
        "autonomous_agents_processed": len([r for r in results if "error" not in r]),
        "transactions_initiated": len([r for r in results if r.get("action_taken")]),
        "results": results
    })

@mcp.tool()
async def satoshi_agent_autonomous_transaction(agent_id: str) -> str:
    """Force a specific Satoshi AI agent to make an autonomous transaction decision"""
    
    if agent_id not in active_agents:
        return json.dumps({
            "success": False,
            "error": f"Agent {agent_id} not found"
        })
    
    agent = active_agents[agent_id]
    
    try:
        # Force agent to make decision
        decision = agent.should_make_transaction()
        
        logger.info(f"🎯 Forced decision for agent {agent_id}: {decision}")
        
        if decision["should_transact"]:
            amount = decision["amount"]
            
            # Execute the autonomous transaction
            tx_result = await autonomous_agent_transaction(agent, amount)
            
            # Update agent state
            agent.transaction_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "amount": amount,
                "decision_confidence": decision["confidence"],
                "tx_result": tx_result,
                "autonomous": True,
                "forced": True
            })
            
            return json.dumps({
                "success": True,
                "agent_id": agent_id,
                "decision": decision,
                "transaction": tx_result,
                "message": f"Agent {agent_id} executed autonomous transaction of {amount} ADA"
            })
        else:
            return json.dumps({
                "success": True,
                "agent_id": agent_id,
                "decision": decision,
                "message": f"Agent {agent_id} decided not to transact: {decision['reason']}"
            })
            
    except Exception as e:
        logger.error(f"Error in autonomous transaction for agent {agent_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def autonomous_agent_transaction(agent: SatoshiAgent, amount: float) -> dict:
    """Execute autonomous transaction initiated by AI agent"""
    
    try:
        # Recipient wallet (ESP32 display wallet)
        recipient_address = "addr_test1qqxdsjedg0fpurjt345lymmyxrs2r4u7etwchfwze7fwvfx76eyhp6agt96xprlux3tgph0zm5degavwkge2f9jmszqqg3p703"
        
        # Call Masumi Payment API
        async with httpx.AsyncClient() as client:
            payment_data = {
                "fromWalletAddress": agent.wallet_address,
                "toWalletAddress": recipient_address,
                "amount": amount,
                "metadata": {
                    "source": "satoshi_ai_agent",
                    "agent_id": agent.agent_id,
                    "autonomous": True,
                    "strategy": agent.strategy,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            
            response = await client.post(
                f"{MASUMI_PAYMENT_URL}/send",
                json=payment_data,
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                tx_hash = result.get("txHash", f"ai_tx_{int(asyncio.get_event_loop().time())}")
                
                # Update agent balance
                agent.balance = max(0, agent.balance - amount)
                
                # Send to ESP32 for display
                if esp32_port:
                    esp32_command = f"DISPLAY_TX:{tx_hash}:{amount}:AI_SUCCESS"
                    await send_arduino_command(esp32_command, "esp32")
                
                # Send to Arduino for notification
                if arduino_uno_port:
                    arduino_command = f"AI_TRANSACTION:{agent.agent_id}:{amount}:{tx_hash[:8]}"
                    await send_arduino_command(arduino_command, "uno")
                
                logger.info(f"✅ Autonomous AI transaction complete: {tx_hash}")
                
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount": amount,
                    "explorer_url": f"https://preprod.cardanoscan.io/transaction/{tx_hash}",
                    "agent_initiated": True,
                    "autonomous": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Payment API error: {response.text}"
                }
                
    except Exception as e:
        logger.error(f"Autonomous transaction error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Background AI Agent Loop
async def continuous_ai_agent_loop():
    """Continuously run AI decision cycles for autonomous agents"""
    logger.info("🤖 Starting continuous AI agent decision loop...")
    
    while True:
        try:
            # Run AI decision cycle every 30 seconds
            if active_agents:
                autonomous_count = len([a for a in active_agents.values() if a.autonomous_mode])
                if autonomous_count > 0:
                    logger.info(f"🧠 Running AI decision cycle for {autonomous_count} autonomous agents...")
                    
                    # Update market sentiment (simulate real market data)
                    import random
                    market_sentiment = random.uniform(0.2, 0.8)
                    
                    for agent in active_agents.values():
                        if agent.autonomous_mode:
                            agent.update_market_sentiment(market_sentiment)
                    
                    # Run decision cycle
                    await ai_agent_decision_cycle()
            
            # Wait 30 seconds before next cycle
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in continuous AI loop: {e}")
            await asyncio.sleep(10)  # Shorter wait on error

if __name__ == "__main__":
    logger.info("🚀 Starting Satoshi AI Agent MCP Server...")
    logger.info("Available tools:")
    logger.info("  - detect_arduino_boards: Find connected Arduino devices")
    logger.info("  - create_satoshi_agent: Create autonomous AI agents")
    logger.info("  - send_arduino_command: Send commands to hardware")
    logger.info("  - initiate_payment_from_arduino: Arduino-triggered payments")
    logger.info("  - get_agent_status: Monitor agent activities")
    logger.info("  - enable_autonomous_mode: Toggle AI autonomy")
    logger.info("  - ai_agent_decision_cycle: Run AI decision engine")
    logger.info("  - satoshi_agent_autonomous_transaction: Force AI transaction")
    logger.info("")
    logger.info("🤖 AI agents will automatically make transaction decisions when autonomous mode is enabled")
    logger.info("🎯 This showcases autonomous blockchain operations - perfect for hackathon demo!")
    
    # Start background AI loop
    asyncio.create_task(continuous_ai_agent_loop())
    
    # Run the MCP server
    mcp.run(transport='stdio')