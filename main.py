#!/usr/bin/env python3
"""
Cardano-Arduino-AI System Launcher
Main entry point for the complete hackathon system
"""

import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from typing import List, Dict, Any
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemLauncher:
    """Main system launcher and coordinator"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.services = {
            "payment_service": {
                "cmd": [sys.executable, "src/blockchain/payment_service.py"],
                "port": int(os.getenv("PAYMENT_SERVICE_PORT", "8000")),
                "health_path": "/",
                "required": True
            },
            "router": {
                "cmd": [sys.executable, "src/agents/router.py"],
                "port": int(os.getenv("ROUTER_PORT", "8003")),
                "health_path": "/",
                "required": True
            },
            "agent_a": {
                "cmd": [sys.executable, "src/agents/agent_a.py"],
                "port": int(os.getenv("AGENT_A_PORT", "8001")),
                "health_path": "/",
                "required": True
            },
            "agent_b": {
                "cmd": [sys.executable, "src/agents/agent_b.py"],
                "port": int(os.getenv("AGENT_B_PORT", "8002")),
                "health_path": "/",
                "required": True
            }
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_modules = [
            "fastapi", "uvicorn", "flask", "requests", 
            "pydantic", "python-dotenv", "pyserial"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module.replace("-", "_"))
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            logger.error(f"Missing required modules: {missing_modules}")
            logger.error("Please run: pip install -r requirements.txt")
            return False
        
        logger.info("✅ All dependencies satisfied")
        return True
    
    def check_ports(self) -> bool:
        """Check if required ports are available"""
        import socket
        
        logger.info("Checking port availability...")
        
        for service_name, config in self.services.items():
            port = config["port"]
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(("localhost", port))
                if result == 0:
                    logger.error(f"Port {port} already in use (required for {service_name})")
                    return False
        
        logger.info("✅ All required ports available")
        return True
    
    def start_service(self, service_name: str, config: Dict[str, Any]) -> subprocess.Popen:
        """Start a single service"""
        logger.info(f"Starting {service_name} on port {config['port']}...")
        
        try:
            process = subprocess.Popen(
                config["cmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Give the service a moment to start
            time.sleep(2)
            
            if process.poll() is None:
                logger.info(f"✅ {service_name} started successfully (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service_name} failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error starting {service_name}: {e}")
            return None
    
    def check_service_health(self, service_name: str, config: Dict[str, Any]) -> bool:
        """Check if a service is healthy"""
        import requests
        
        try:
            url = f"http://localhost:{config['port']}{config['health_path']}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"✅ {service_name} health check passed")
                return True
            else:
                logger.warning(f"⚠️ {service_name} health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ {service_name} health check failed: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Start all services in the correct order"""
        logger.info("🚀 Starting Cardano-Arduino-AI System...")
        
        # Start services in dependency order
        service_order = ["payment_service", "router", "agent_a", "agent_b"]
        
        for service_name in service_order:
            config = self.services[service_name]
            process = self.start_service(service_name, config)
            
            if process:
                self.processes.append(process)
                
                # Wait a bit more for critical services
                if service_name in ["payment_service", "router"]:
                    time.sleep(3)
            else:
                if config["required"]:
                    logger.error(f"❌ Failed to start required service: {service_name}")
                    return False
                else:
                    logger.warning(f"⚠️ Optional service {service_name} failed to start")
        
        # Health check all services
        logger.info("Performing health checks...")
        time.sleep(5)  # Give services time to fully initialize
        
        all_healthy = True
        for service_name, config in self.services.items():
            if not self.check_service_health(service_name, config):
                if config["required"]:
                    all_healthy = False
        
        if all_healthy:
            logger.info("🎉 All services started successfully!")
            self.display_system_info()
            return True
        else:
            logger.error("❌ Some required services failed health checks")
            return False
    
    def display_system_info(self):
        """Display system information and access URLs"""
        print("\n" + "="*60)
        print("🎉 CARDANO-ARDUINO-AI SYSTEM READY!")
        print("="*60)
        print(f"🔗 Router (Traffic Controller): http://localhost:{os.getenv('ROUTER_PORT', '8003')}")
        print(f"🤖 Agent A (Buyer AI): http://localhost:{os.getenv('AGENT_A_PORT', '8001')}")
        print(f"🛒 Agent B (Seller): http://localhost:{os.getenv('AGENT_B_PORT', '8002')}")
        print(f"💰 Payment Service: http://localhost:{os.getenv('PAYMENT_SERVICE_PORT', '8000')}")
        print(f"📊 System Status: http://localhost:{os.getenv('ROUTER_PORT', '8003')}/status")
        print("\n📱 Test Commands:")
        print("• Test Payment: curl http://localhost:8000/test_payment")
        print("• Arduino Trigger: curl -X POST http://localhost:8003/arduino_trigger -H 'Content-Type: application/json' -d '{\"amount\": 150, \"product\": \"Sensor Data\"}'")
        print("• System Status: curl http://localhost:8003/status")
        print("\n🔌 Arduino Connections:")
        print(f"• Arduino A: {os.getenv('ARDUINO_A_PORT', 'COM3')} @ {os.getenv('ARDUINO_BAUD_RATE', '9600')} baud")
        print(f"• Arduino B: {os.getenv('ARDUINO_B_PORT', 'COM4')} @ {os.getenv('ARDUINO_BAUD_RATE', '9600')} baud")
        print("\n💡 Tips:")
        print("• Upload arduino_a.ino to your first Arduino")
        print("• Upload arduino_b.ino to your second Arduino")
        print("• Configure .env file with your Blockfrost API key for real blockchain")
        print("• Press Ctrl+C to stop all services")
        print("="*60)
    
    def monitor_services(self):
        """Monitor running services"""
        logger.info("🔍 Monitoring services... (Press Ctrl+C to stop)")
        
        try:
            while True:
                time.sleep(30)  # Check every 30 seconds
                
                failed_services = []
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        service_name = list(self.services.keys())[i]
                        failed_services.append(service_name)
                        logger.error(f"❌ Service {service_name} has stopped unexpectedly")
                
                if failed_services:
                    logger.error(f"Failed services detected: {failed_services}")
                    # In a production system, you might want to restart failed services
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
    
    def shutdown(self):
        """Shutdown all services gracefully"""
        logger.info("🛑 Shutting down all services...")
        
        for i, process in enumerate(self.processes):
            service_name = list(self.services.keys())[i]
            
            if process.poll() is None:
                logger.info(f"Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ {service_name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Force killing {service_name}")
                    process.kill()
                    process.wait()
        
        self.processes.clear()
        logger.info("🔚 All services stopped")
    
    def run(self):
        """Main run method"""
        try:
            # Pre-flight checks
            if not self.check_dependencies():
                return False
            
            if not self.check_ports():
                return False
            
            # Start all services
            if not self.start_all_services():
                self.shutdown()
                return False
            
            # Monitor services
            self.monitor_services()
            
        except Exception as e:
            logger.error(f"❌ System error: {e}")
            self.shutdown()
            return False
        finally:
            self.shutdown()
        
        return True

def main():
    """Main entry point"""
    print("🚀 Cardano-Arduino-AI System Launcher")
    print("=====================================")
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (where requirements.txt is located)")
        sys.exit(1)
    
    # Create and run launcher
    launcher = SystemLauncher()
    success = launcher.run()
    
    if success:
        print("✅ System shutdown complete")
        sys.exit(0)
    else:
        print("❌ System failed to start properly")
        sys.exit(1)

if __name__ == "__main__":
    main()