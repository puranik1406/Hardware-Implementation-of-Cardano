#!/usr/bin/env python3
"""
Serial Bridge for Arduino A (Wokwi) Integration
Listens to Arduino A button presses and converts them to payment offers.
"""

import json
import logging
import time
import threading
from datetime import datetime, timezone
from typing import Optional
import serial
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('serial_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SerialBridge:
    """Handles communication between Arduino A and Router"""
    
    def __init__(self, port: str = None, baudrate: int = 9600, router_url: str = "http://localhost:5000"):
        self.port = port
        self.baudrate = baudrate
        self.router_url = router_url
        self.serial_connection: Optional[serial.Serial] = None
        self.running = False
        
        # Setup HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Mock offer templates for different button presses
        self.offer_templates = {
            'button_1': {
                'amount': 10.0,
                'currency': 'ADA',
                'description': 'Coffee payment - Button 1 pressed'
            },
            'button_2': {
                'amount': 25.0,
                'currency': 'ADA', 
                'description': 'Lunch payment - Button 2 pressed'
            },
            'button_3': {
                'amount': 50.0,
                'currency': 'ADA',
                'description': 'Dinner payment - Button 3 pressed'
            },
            'emergency': {
                'amount': 100.0,
                'currency': 'ADA',
                'description': 'Emergency payment - Emergency button pressed'
            }
        }
    
    def connect_serial(self) -> bool:
        """Connect to Arduino A via serial"""
        try:
            if self.port:
                self.serial_connection = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=1
                )
                logger.info(f"Connected to Arduino A on port {self.port}")
            else:
                # Auto-detect Arduino port
                available_ports = self._detect_arduino_ports()
                if available_ports:
                    self.port = available_ports[0]
                    self.serial_connection = serial.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        timeout=1
                    )
                    logger.info(f"Auto-detected and connected to Arduino A on port {self.port}")
                else:
                    logger.warning("No Arduino ports detected, running in simulation mode")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Arduino A: {str(e)}")
            return False
    
    def _detect_arduino_ports(self) -> list:
        """Auto-detect Arduino ports"""
        import serial.tools.list_ports
        
        arduino_ports = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Common Arduino identifiers
            if any(identifier in port.description.lower() for identifier in 
                   ['arduino', 'usb serial', 'usb2.0-serial', 'ch340', 'cp210']):
                arduino_ports.append(port.device)
                logger.info(f"Found potential Arduino port: {port.device} - {port.description}")
        
        return arduino_ports
    
    def start_listening(self):
        """Start listening for Arduino A signals"""
        if not self.connect_serial():
            logger.info("Starting in simulation mode (no Arduino connected)")
            self._simulate_arduino_input()
            return
        
        self.running = True
        logger.info("Started listening for Arduino A signals...")
        
        try:
            while self.running:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    try:
                        # Read data from Arduino
                        data = self.serial_connection.readline().decode('utf-8').strip()
                        if data:
                            self._process_arduino_signal(data)
                    except Exception as e:
                        logger.error(f"Error reading from Arduino: {str(e)}")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            logger.info("Stopping serial bridge...")
        finally:
            self.stop()
    
    def _simulate_arduino_input(self):
        """Simulate Arduino input for testing when no hardware is connected"""
        logger.info("Simulation mode: Press Ctrl+C to stop, or wait for auto-generated signals")
        
        # Simulate button presses every 10 seconds
        button_sequence = ['button_1', 'button_2', 'button_3', 'emergency']
        button_index = 0
        
        try:
            while True:
                time.sleep(10)  # Wait 10 seconds between simulated presses
                
                button = button_sequence[button_index % len(button_sequence)]
                logger.info(f"Simulating Arduino button press: {button}")
                self._process_arduino_signal(button)
                
                button_index += 1
                
        except KeyboardInterrupt:
            logger.info("Stopping simulation...")
    
    def _process_arduino_signal(self, signal: str):
        """Process signal from Arduino A"""
        logger.info(f"Received Arduino signal: {signal}")
        
        # Parse signal to determine button pressed
        button_type = self._parse_signal(signal)
        if not button_type:
            logger.warning(f"Unknown signal format: {signal}")
            return
        
        # Create offer based on button press
        offer = self._create_offer_from_signal(button_type)
        if offer:
            self._send_offer_to_router(offer)
    
    def _parse_signal(self, signal: str) -> Optional[str]:
        """Parse Arduino signal to determine button type"""
        signal = signal.lower().strip()
        
        # Handle different signal formats
        if 'button1' in signal or 'btn1' in signal or signal == '1':
            return 'button_1'
        elif 'button2' in signal or 'btn2' in signal or signal == '2':
            return 'button_2'
        elif 'button3' in signal or 'btn3' in signal or signal == '3':
            return 'button_3'
        elif 'emergency' in signal or 'panic' in signal or signal == 'e':
            return 'emergency'
        else:
            # Try to extract button number from signal
            import re
            match = re.search(r'(\d+)', signal)
            if match:
                button_num = int(match.group(1))
                if button_num == 1:
                    return 'button_1'
                elif button_num == 2:
                    return 'button_2'
                elif button_num == 3:
                    return 'button_3'
        
        return None
    
    def _create_offer_from_signal(self, button_type: str) -> Optional[dict]:
        """Create payment offer from Arduino signal"""
        if button_type not in self.offer_templates:
            logger.error(f"Unknown button type: {button_type}")
            return None
        
        template = self.offer_templates[button_type]
        
        offer = {
            'from_agent': 'agent_a',
            'to_agent': 'agent_b',
            'amount': template['amount'],
            'currency': template['currency'],
            'description': template['description'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metadata': {
                'arduino_trigger': True,
                'button_type': button_type,
                'priority': 'high' if button_type == 'emergency' else 'medium'
            }
        }
        
        logger.info(f"Created offer: {offer['amount']} {offer['currency']} - {offer['description']}")
        return offer
    
    def _send_offer_to_router(self, offer: dict):
        """Send offer to Router API"""
        try:
            response = self.session.post(
                f"{self.router_url}/send_offer",
                json=offer,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Successfully sent offer to router: {result.get('offer_id')}")
            else:
                logger.error(f"Failed to send offer to router: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending offer to router: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error sending offer: {str(e)}")
    
    def stop(self):
        """Stop the serial bridge"""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Serial connection closed")
    
    def test_router_connection(self) -> bool:
        """Test connection to Router API"""
        try:
            response = self.session.get(f"{self.router_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Router API is healthy and accessible")
                return True
            else:
                logger.error(f"Router API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Cannot connect to Router API: {str(e)}")
            return False

def main():
    """Main function to run the Serial Bridge"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Serial Bridge for Arduino A')
    parser.add_argument('--port', help='Serial port for Arduino A (auto-detect if not specified)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Serial baudrate')
    parser.add_argument('--router-url', default='http://localhost:5000', help='Router API URL')
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode')
    
    args = parser.parse_args()
    
    # Create and configure serial bridge
    bridge = SerialBridge(
        port=args.port if not args.simulate else None,
        baudrate=args.baudrate,
        router_url=args.router_url
    )
    
    # Test router connection
    if not bridge.test_router_connection():
        logger.error("Cannot connect to Router API. Make sure router.py is running.")
        return
    
    # Start listening
    try:
        if args.simulate:
            logger.info("Starting in simulation mode...")
            bridge._simulate_arduino_input()
        else:
            bridge.start_listening()
    except KeyboardInterrupt:
        logger.info("Serial bridge stopped by user")
    finally:
        bridge.stop()

if __name__ == '__main__':
    main()
