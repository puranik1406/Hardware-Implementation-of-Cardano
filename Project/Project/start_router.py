#!/usr/bin/env python3
"""
Startup script for Router and Serial Bridge
Starts both the Router API and Serial Bridge in the correct order
"""

import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

class RouterManager:
    def __init__(self):
        self.router_process = None
        self.serial_process = None
        self.running = False
    
    def start_router(self):
        """Start the Router API"""
        print("🚀 Starting Router API...")
        try:
            self.router_process = subprocess.Popen([
                sys.executable, 'router.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for router to start
            time.sleep(3)
            
            # Check if router is running
            if self.router_process.poll() is None:
                print("✅ Router API started successfully")
                return True
            else:
                print("❌ Router API failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Router API: {e}")
            return False
    
    def start_serial_bridge(self, simulate=False, port=None):
        """Start the Serial Bridge"""
        print("🔌 Starting Serial Bridge...")
        try:
            cmd = [sys.executable, 'serial_bridge.py', '--router-url', 'http://localhost:5000']
            
            if simulate:
                cmd.append('--simulate')
                print("   (Running in simulation mode)")
            elif port:
                cmd.extend(['--port', port])
                print(f"   (Using port: {port})")
            else:
                print("   (Auto-detecting Arduino port)")
            
            self.serial_process = subprocess.Popen(cmd)
            
            # Wait a moment for serial bridge to start
            time.sleep(2)
            
            # Check if serial bridge is running
            if self.serial_process.poll() is None:
                print("✅ Serial Bridge started successfully")
                return True
            else:
                print("❌ Serial Bridge failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Serial Bridge: {e}")
            return False
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all processes...")
        self.running = False
        
        if self.serial_process and self.serial_process.poll() is None:
            self.serial_process.terminate()
            print("   Serial Bridge stopped")
        
        if self.router_process and self.router_process.poll() is None:
            self.router_process.terminate()
            print("   Router API stopped")
    
    def run(self, simulate=False, port=None):
        """Run the complete system"""
        print("🌐 Arduino-to-Cardano AI Agents - Router and Serial Bridge")
        print("=" * 60)
        
        # Check if required files exist
        required_files = ['router.py', 'serial_bridge.py', 'schemas/offer.json', 'schemas/response.json']
        for file in required_files:
            if not Path(file).exists():
                print(f"❌ Required file not found: {file}")
                return False
        
        # Start Router API
        if not self.start_router():
            return False
        
        # Start Serial Bridge
        if not self.start_serial_bridge(simulate=simulate, port=port):
            self.stop_all()
            return False
        
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down...")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("\n✅ System is running!")
        print("   Router API: http://localhost:5000")
        print("   Health check: http://localhost:5000/health")
        print("   List offers: http://localhost:5000/offers")
        print("\nPress Ctrl+C to stop all services")
        
        try:
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.router_process and self.router_process.poll() is not None:
                    print("❌ Router API stopped unexpectedly")
                    break
                
                if self.serial_process and self.serial_process.poll() is not None:
                    print("❌ Serial Bridge stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Start Router and Serial Bridge')
    parser.add_argument('--simulate', action='store_true', 
                       help='Run Serial Bridge in simulation mode (no Arduino required)')
    parser.add_argument('--port', help='Serial port for Arduino A (auto-detect if not specified)')
    parser.add_argument('--router-only', action='store_true',
                       help='Start only the Router API (for testing)')
    
    args = parser.parse_args()
    
    manager = RouterManager()
    
    if args.router_only:
        print("🔧 Starting Router API only...")
        success = manager.start_router()
        if success:
            print("✅ Router API is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                manager.stop_all()
    else:
        success = manager.run(simulate=args.simulate, port=args.port)
        if not success:
            sys.exit(1)

if __name__ == '__main__':
    main()
