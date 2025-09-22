#!/usr/bin/env python3
"""
Arduino Test Script
Tests serial communication with Arduino devices
"""

import serial
import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()

def test_arduino_connection(port, baud_rate=9600, timeout=5):
    """Test connection to Arduino"""
    try:
        print(f"🔌 Attempting to connect to Arduino on {port}...")
        
        with serial.Serial(port, baud_rate, timeout=timeout) as ser:
            print(f"✅ Connected to Arduino on {port}")
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Send test command
            test_command = "STATUS\n"
            print(f"📤 Sending test command: {test_command.strip()}")
            ser.write(test_command.encode())
            
            # Read response
            time.sleep(1)
            response = ""
            while ser.in_waiting > 0:
                response += ser.read(ser.in_waiting).decode()
            
            if response:
                print(f"📥 Arduino response: {response.strip()}")
            else:
                print("⚠️ No response from Arduino")
            
            return True
            
    except serial.SerialException as e:
        print(f"❌ Failed to connect to Arduino on {port}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_arduino_a_workflow():
    """Test Arduino A (trigger) workflow"""
    port = os.getenv("ARDUINO_A_PORT", "COM3")
    
    print("\n🔧 Testing Arduino A (Trigger Device)...")
    
    if not test_arduino_connection(port):
        return False
    
    try:
        with serial.Serial(port, 9600, timeout=5) as ser:
            time.sleep(2)  # Wait for Arduino initialization
            
            # Test commands for Arduino A
            test_commands = [
                "STATUS",
                "RESET",
                "OFFER_ACCEPTED:test_offer_123:mock_tx_abc123",
                "TX_CONFIRMED:mock_tx_abc123"
            ]
            
            for command in test_commands:
                print(f"📤 Testing command: {command}")
                ser.write(f"{command}\n".encode())
                time.sleep(2)
                
                # Read any response
                response = ""
                while ser.in_waiting > 0:
                    response += ser.read(ser.in_waiting).decode()
                
                if response:
                    print(f"📥 Response: {response.strip()}")
                
                time.sleep(1)
            
            print("✅ Arduino A workflow test completed")
            return True
            
    except Exception as e:
        print(f"❌ Arduino A workflow test failed: {e}")
        return False

def test_arduino_b_workflow():
    """Test Arduino B (display) workflow"""
    port = os.getenv("ARDUINO_B_PORT", "COM4")
    
    print("\n🔧 Testing Arduino B (Display Device)...")
    
    if not test_arduino_connection(port):
        return False
    
    try:
        with serial.Serial(port, 9600, timeout=5) as ser:
            time.sleep(2)  # Wait for Arduino initialization
            
            # Test commands for Arduino B
            test_commands = [
                "STATUS",
                "OFFER:150.5:Arduino Sensor Data",
                "ACCEPTED:test_tx_12345",
                "PROCESSING:test_tx_12345", 
                "CONFIRMED:test_tx_12345",
                "HISTORY",
                "RESET"
            ]
            
            for command in test_commands:
                print(f"📤 Testing command: {command}")
                ser.write(f"{command}\n".encode())
                time.sleep(3)  # Longer delay for display updates
                
                # Read any response
                response = ""
                while ser.in_waiting > 0:
                    response += ser.read(ser.in_waiting).decode()
                
                if response:
                    print(f"📥 Response: {response.strip()}")
                
                time.sleep(1)
            
            print("✅ Arduino B workflow test completed")
            return True
            
    except Exception as e:
        print(f"❌ Arduino B workflow test failed: {e}")
        return False

def list_available_ports():
    """List all available serial ports"""
    import serial.tools.list_ports
    
    print("\n🔍 Scanning for available serial ports...")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found")
        return []
    
    available_ports = []
    for port in ports:
        print(f"✅ Found port: {port.device} - {port.description}")
        available_ports.append(port.device)
    
    return available_ports

def interactive_arduino_test():
    """Interactive Arduino testing"""
    print("\n🎮 Interactive Arduino Test Mode")
    print("Type commands to send to Arduino (or 'quit' to exit)")
    
    port = input(f"Enter Arduino port [{os.getenv('ARDUINO_A_PORT', 'COM3')}]: ").strip()
    if not port:
        port = os.getenv('ARDUINO_A_PORT', 'COM3')
    
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            print(f"✅ Connected to Arduino on {port}")
            print("Available commands: STATUS, RESET, OFFER:amount:product, CONFIRMED:tx_hash")
            time.sleep(2)
            
            while True:
                command = input("\nArduino> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not command:
                    continue
                
                # Send command
                ser.write(f"{command}\n".encode())
                print(f"📤 Sent: {command}")
                
                # Wait and read response
                time.sleep(1)
                response = ""
                start_time = time.time()
                
                while time.time() - start_time < 3:  # 3 second timeout
                    if ser.in_waiting > 0:
                        response += ser.read(ser.in_waiting).decode()
                    time.sleep(0.1)
                
                if response:
                    print(f"📥 Arduino: {response.strip()}")
                else:
                    print("⚠️ No response")
            
            print("👋 Interactive test session ended")
            
    except Exception as e:
        print(f"❌ Interactive test failed: {e}")

def run_demo_sequence():
    """Run a complete demo sequence"""
    print("\n🎬 Running Arduino Demo Sequence...")
    
    # Test both Arduinos
    arduino_a_port = os.getenv("ARDUINO_A_PORT", "COM3")
    arduino_b_port = os.getenv("ARDUINO_B_PORT", "COM4")
    
    print("This demo simulates the complete workflow:")
    print("1. Arduino A triggers an offer")
    print("2. Agent system processes the offer")
    print("3. Arduino B displays transaction confirmation")
    
    # Test Arduino A
    print(f"\n📡 Testing Arduino A on {arduino_a_port}...")
    if test_arduino_connection(arduino_a_port):
        print("✅ Arduino A is ready")
    else:
        print("❌ Arduino A not available")
    
    # Test Arduino B  
    print(f"\n📺 Testing Arduino B on {arduino_b_port}...")
    if test_arduino_connection(arduino_b_port):
        print("✅ Arduino B is ready")
        
        # Send demo sequence to Arduino B
        try:
            with serial.Serial(arduino_b_port, 9600, timeout=5) as ser:
                time.sleep(2)
                
                demo_sequence = [
                    ("Offer Received", "OFFER:150.0:Demo Sensor Data"),
                    ("Offer Accepted", "ACCEPTED:demo_tx_abc123"),
                    ("Payment Processing", "PROCESSING:demo_tx_abc123"),
                    ("Transaction Confirmed", "CONFIRMED:demo_tx_abc123")
                ]
                
                for step, command in demo_sequence:
                    print(f"\n🎭 Demo Step: {step}")
                    print(f"📤 Sending: {command}")
                    ser.write(f"{command}\n".encode())
                    time.sleep(4)  # Allow time to see display update
                
                print("\n🎉 Demo sequence completed!")
                
        except Exception as e:
            print(f"❌ Demo sequence failed: {e}")
    else:
        print("❌ Arduino B not available")

def main():
    """Main test function"""
    print("🔧 Arduino Test Script")
    print("=====================")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("\nSelect test mode:")
        print("1. Quick connection test")
        print("2. Arduino A workflow test")
        print("3. Arduino B workflow test")
        print("4. List available ports")
        print("5. Interactive test")
        print("6. Demo sequence")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        mode_map = {
            "1": "quick",
            "2": "arduino_a",
            "3": "arduino_b", 
            "4": "list",
            "5": "interactive",
            "6": "demo"
        }
        
        mode = mode_map.get(choice, "quick")
    
    if mode == "quick":
        print("\n🚀 Quick Connection Test")
        arduino_a_port = os.getenv("ARDUINO_A_PORT", "COM3")
        arduino_b_port = os.getenv("ARDUINO_B_PORT", "COM4")
        
        print("Testing Arduino A...")
        test_arduino_connection(arduino_a_port)
        
        print("\nTesting Arduino B...")
        test_arduino_connection(arduino_b_port)
        
    elif mode == "arduino_a":
        test_arduino_a_workflow()
        
    elif mode == "arduino_b":
        test_arduino_b_workflow()
        
    elif mode == "list":
        list_available_ports()
        
    elif mode == "interactive":
        interactive_arduino_test()
        
    elif mode == "demo":
        run_demo_sequence()
        
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Available modes: quick, arduino_a, arduino_b, list, interactive, demo")

if __name__ == "__main__":
    main()