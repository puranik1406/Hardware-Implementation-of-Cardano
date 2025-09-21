#!/usr/bin/env python3
"""
Startup script for Agent B - Seller Logic
Handles dependencies and starts the service
"""

import subprocess
import sys
import os
import time

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_port_availability(port=5001):
    """Check if port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ Port {port} is available")
            return True
    except OSError:
        print(f"❌ Port {port} is already in use")
        print(f"   Please stop any service using port {port} or change the port")
        return False

def start_agent_b():
    """Start Agent B service"""
    print("🚀 Starting Agent B - Seller Logic...")
    print("=" * 50)
    print("Service will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the service")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from agent_b import app
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Agent B stopped by user")
    except Exception as e:
        print(f"❌ Error starting Agent B: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 Agent B - Seller Logic Startup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check port availability
    if not check_port_availability():
        return False
    
    # Start Agent B
    print("\n" + "=" * 50)
    return start_agent_b()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
