#!/usr/bin/env python3
"""
Arduino Masumi Network Bridge
Manages communication between PC, Arduino Uno, and ESP32
Integrates with Satoshi AI agents via MCP
"""

import asyncio
import json
import logging
import time
from datetime import datetime
import serial
import serial.tools.list_ports
import httpx
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('arduino_bridge.log')
    ]
)
logger = logging.getLogger(__name__)

class ArduinoBridge:
    def __init__(self):
        self.arduino_uno: Optional[serial.Serial] = None
        self.esp32: Optional[serial.Serial] = None
        self.masumi_registry_url = "http://localhost:3000"
        self.masumi_payment_url = "http://localhost:3001"
        self.transaction_history = []
        self.running = True
        
    async def initialize(self):
        """Initialize connections to Arduino boards"""
        logger.info("Initializing Arduino Bridge...")
        
        # Detect and connect to Arduino boards
        await self.detect_arduino_boards()
        
        if self.arduino_uno:
            logger.info(f"Arduino Uno connected on {self.arduino_uno.port}")
            # Send initial setup command
            self.send_to_arduino("SET_AGENT:arduino_uno_sender:Payment Sender")
            
        if self.esp32:
            logger.info(f"ESP32 connected on {self.esp32.port}")
            # Send initial setup command
            self.send_to_esp32("SET_WIFI:YourWiFi:YourPassword")  # Update with real credentials
    
    async def detect_arduino_boards(self):
        """Detect and connect to Arduino Uno and ESP32"""
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            try:
                # Try to connect and identify the board
                ser = serial.Serial(port.device, 115200, timeout=2)
                time.sleep(2)  # Wait for Arduino to initialize
                
                # Send identification command
                ser.write(b"GET_STATUS\n")
                time.sleep(1)
                
                response = ""
                while ser.in_waiting:
                    line = ser.readline().decode().strip()
                    response += line + "\n"
                
                # Identify board type based on response
                if "arduino_uno" in response.lower():
                    self.arduino_uno = ser
                    logger.info(f"Arduino Uno detected on {port.device}")
                elif "esp32" in response.lower() or "ESP32" in port.description:
                    self.esp32 = ser
                    logger.info(f"ESP32 detected on {port.device}")
                else:
                    # Try to identify by port description
                    if "Arduino" in port.description or "CH340" in port.description:
                        self.arduino_uno = ser
                        logger.info(f"Arduino Uno (by description) on {port.device}")
                    elif "CP210" in port.description or "ESP32" in port.description:
                        self.esp32 = ser
                        logger.info(f"ESP32 (by description) on {port.device}")
                    else:
                        ser.close()
                        
            except Exception as e:
                logger.warning(f"Could not connect to {port.device}: {e}")
    
    def send_to_arduino(self, command: str) -> str:
        """Send command to Arduino Uno and get response"""
        if not self.arduino_uno:
            logger.error("Arduino Uno not connected")
            return "ERROR: Arduino Uno not connected"
        
        try:
            self.arduino_uno.write(f"{command}\n".encode())
            logger.info(f"Sent to Arduino: {command}")
            
            # Wait for response
            response = ""
            start_time = time.time()
            
            while (time.time() - start_time) < 10:  # 10 second timeout
                if self.arduino_uno.in_waiting:
                    line = self.arduino_uno.readline().decode().strip()
                    response += line + "\n"
                    logger.info(f"Arduino response: {line}")
                    
                    if "COMPLETE" in line or "ERROR" in line:
                        break
                time.sleep(0.1)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error communicating with Arduino: {e}")
            return f"ERROR: {e}"
    
    def send_to_esp32(self, command: str) -> str:
        """Send command to ESP32 and get response"""
        if not self.esp32:
            logger.error("ESP32 not connected")
            return "ERROR: ESP32 not connected"
        
        try:
            self.esp32.write(f"{command}\n".encode())
            logger.info(f"Sent to ESP32: {command}")
            
            # Wait for response
            response = ""
            start_time = time.time()
            
            while (time.time() - start_time) < 10:  # 10 second timeout
                if self.esp32.in_waiting:
                    line = self.esp32.readline().decode().strip()
                    response += line + "\n"
                    logger.info(f"ESP32 response: {line}")
                    
                    if "COMPLETE" in line or "TX_RECEIVED" in line:
                        break
                time.sleep(0.1)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error communicating with ESP32: {e}")
            return f"ERROR: {e}"
    
    async def send_payment(self, amount: float, recipient: str = "esp32_receiver") -> Dict[str, Any]:
        """Complete payment flow: Arduino Uno -> Masumi Network -> ESP32"""
        try:
            logger.info(f"Starting payment flow: {amount} ADA to {recipient}")
            
            # Step 1: Send payment command to Arduino Uno
            arduino_command = f"SEND_PAYMENT:{amount}:{recipient}"
            arduino_response = self.send_to_arduino(arduino_command)
            
            if "ERROR" in arduino_response:
                return {"success": False, "error": arduino_response}
            
            # Step 2: Process payment through Masumi Network
            payment_result = await self.process_masumi_payment(amount, recipient)
            
            # Step 3: Send result to ESP32
            if payment_result["success"]:
                tx_hash = payment_result["txHash"]
                esp32_command = f"DISPLAY_TX:{tx_hash}:{amount}:SUCCESS"
                esp32_response = self.send_to_esp32(esp32_command)
                
                # Store transaction
                transaction = {
                    "timestamp": datetime.now().isoformat(),
                    "amount": amount,
                    "recipient": recipient,
                    "tx_hash": tx_hash,
                    "status": "success",
                    "arduino_response": arduino_response,
                    "esp32_response": esp32_response,
                    "explorer_url": f"https://preprod.cardanoscan.io/transaction/{tx_hash}"
                }
                
                self.transaction_history.append(transaction)
                
                logger.info(f"Payment completed successfully: {tx_hash}")
                return {
                    "success": True,
                    "transaction": transaction
                }
            else:
                # Send error to ESP32
                esp32_command = f"DISPLAY_TX:ERROR:{amount}:FAILED"
                self.send_to_esp32(esp32_command)
                
                return {
                    "success": False,
                    "error": payment_result.get("error", "Payment failed")
                }
                
        except Exception as e:
            logger.error(f"Payment flow error: {e}")
            
            # Try to send error to ESP32
            try:
                esp32_command = f"DISPLAY_TX:ERROR:{amount}:FAILED"
                self.send_to_esp32(esp32_command)
            except:
                pass
            
            return {"success": False, "error": str(e)}
    
    async def process_masumi_payment(self, amount: float, recipient: str) -> Dict[str, Any]:
        """Process payment through Masumi Network"""
        try:
            # Use predefined wallet addresses (your funded wallets)
            sender_address = "addr_test1qrffhpxs9ky88sxfm9788mr8a4924e0uhl4fexvy9z5pt084p3q2uhgh9wvft4ejrjhx5yes2xpmy2cuufmzljdwtf7qvgt5rz"
            recipient_address = "addr_test1qqxdsjedg0fpurjt345lymmyxrs2r4u7etwchfwze7fwvfx76eyhp6agt96xprlux3tgph0zm5degavwkge2f9jmszqqg3p703"
            
            async with httpx.AsyncClient() as client:
                payment_data = {
                    "fromWalletAddress": sender_address,
                    "toWalletAddress": recipient_address,
                    "amount": amount,
                    "metadata": {
                        "source": "arduino_bridge",
                        "recipient": recipient,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                response = await client.post(
                    f"{self.masumi_payment_url}/send",
                    json=payment_data,
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "txHash": result.get("txHash", f"demo_tx_{int(time.time())}"),
                        "explorerUrl": result.get("explorerUrl", "")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Masumi API error: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Masumi payment error: {e}")
            return {"success": False, "error": str(e)}
    
    async def monitor_arduino_buttons(self):
        """Monitor Arduino for button presses and automatic payments"""
        logger.info("Starting Arduino button monitoring...")
        
        while self.running:
            try:
                # Check Arduino Uno for button press events
                if self.arduino_uno and self.arduino_uno.in_waiting:
                    line = self.arduino_uno.readline().decode().strip()
                    
                    if "BUTTON_PRESSED" in line:
                        logger.info("🔘 Button pressed on Arduino Uno - triggering Satoshi AI agent decision")
                        # Instead of direct payment, trigger AI agent decision
                        await self.trigger_satoshi_ai_transaction()
                    
                    elif "HEARTBEAT:" in line:
                        # Handle heartbeat data
                        heartbeat_data = line.split("HEARTBEAT:")[1]
                        logger.debug(f"Arduino heartbeat: {heartbeat_data}")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Button monitoring error: {e}")
                await asyncio.sleep(1)
    
    async def trigger_satoshi_ai_transaction(self):
        """Trigger Satoshi AI agent to make autonomous transaction decision"""
        try:
            logger.info("🤖 Triggering Satoshi AI agent autonomous transaction...")
            
            # In real implementation, this would call the MCP server
            # For now, simulate AI decision and transaction
            
            # Simulate AI agent decision process
            import random
            confidence = random.uniform(0.6, 0.95)
            amount = round(random.uniform(0.5, 3.0), 2)
            
            logger.info(f"🧠 AI Agent Decision: Confidence {confidence:.2f}, Amount {amount} ADA")
            
            if confidence > 0.7:  # AI decides to transact
                logger.info(f"✅ AI Agent approves transaction: {amount} ADA")
                
                # Execute the payment
                result = await self.send_payment(amount, "ai_agent_decision")
                
                if result["success"]:
                    logger.info(f"🎉 Satoshi AI agent successfully executed autonomous transaction!")
                    logger.info(f"TX Hash: {result['transaction']['tx_hash']}")
                    
                    # Send special notification to Arduino
                    self.send_to_arduino(f"AI_SUCCESS:{amount}:{result['transaction']['tx_hash'][:8]}")
                    
                else:
                    logger.error(f"❌ AI agent transaction failed: {result['error']}")
                    self.send_to_arduino("AI_FAILED:0:ERROR")
            else:
                logger.info(f"🚫 AI Agent declined transaction (low confidence: {confidence:.2f})")
                self.send_to_arduino(f"AI_DECLINED:{confidence:.2f}:LOW_CONFIDENCE")
                
        except Exception as e:
            logger.error(f"Error in AI transaction trigger: {e}")
            self.send_to_arduino("AI_ERROR:0:EXCEPTION")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all components"""
        return {
            "arduino_uno_connected": self.arduino_uno is not None,
            "esp32_connected": self.esp32 is not None,
            "arduino_uno_port": self.arduino_uno.port if self.arduino_uno else None,
            "esp32_port": self.esp32.port if self.esp32 else None,
            "transactions_processed": len(self.transaction_history),
            "last_transaction": self.transaction_history[-1] if self.transaction_history else None
        }
    
    def close(self):
        """Close all connections"""
        logger.info("Closing Arduino Bridge connections...")
        self.running = False
        
        if self.arduino_uno:
            self.arduino_uno.close()
            
        if self.esp32:
            self.esp32.close()

# Interactive CLI for testing
async def main():
    bridge = ArduinoBridge()
    await bridge.initialize()
    
    # Start button monitoring in background
    monitor_task = asyncio.create_task(bridge.monitor_arduino_buttons())
    
    print("\n=== Arduino Masumi Bridge CLI ===")
    print("Commands:")
    print("  pay <amount> - Send payment (e.g., 'pay 2.5')")
    print("  status - Show system status")
    print("  history - Show transaction history")
    print("  arduino <command> - Send command to Arduino Uno")
    print("  esp32 <command> - Send command to ESP32")
    print("  quit - Exit")
    print("=====================================\n")
    
    try:
        while True:
            command = input("Bridge> ").strip().lower()
            
            if command.startswith("pay "):
                try:
                    amount = float(command.split()[1])
                    result = await bridge.send_payment(amount)
                    if result["success"]:
                        print(f"✅ Payment successful!")
                        print(f"   TX Hash: {result['transaction']['tx_hash']}")
                        print(f"   Explorer: {result['transaction']['explorer_url']}")
                    else:
                        print(f"❌ Payment failed: {result['error']}")
                except (IndexError, ValueError):
                    print("Usage: pay <amount> (e.g., 'pay 2.5')")
            
            elif command == "status":
                status = bridge.get_status()
                print(json.dumps(status, indent=2))
            
            elif command == "history":
                if bridge.transaction_history:
                    for i, tx in enumerate(bridge.transaction_history[-5:], 1):  # Last 5
                        print(f"{i}. {tx['timestamp']} - {tx['amount']} ADA - {tx['status']}")
                        print(f"   TX: {tx['tx_hash']}")
                else:
                    print("No transactions yet")
            
            elif command.startswith("arduino "):
                cmd = command[8:]
                response = bridge.send_to_arduino(cmd)
                print(f"Arduino response: {response}")
            
            elif command.startswith("esp32 "):
                cmd = command[6:]
                response = bridge.send_to_esp32(cmd)
                print(f"ESP32 response: {response}")
            
            elif command in ["quit", "exit", "q"]:
                break
            
            else:
                print("Unknown command. Type 'quit' to exit.")
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        monitor_task.cancel()
        bridge.close()

if __name__ == "__main__":
    asyncio.run(main())