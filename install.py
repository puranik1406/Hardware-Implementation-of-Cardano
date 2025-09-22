#!/usr/bin/env python3
"""
🚀 Cardano-Arduino-AI Hackathon - Quick Installer
Simplified setup script for immediate hackathon use
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print project banner"""
    print("🎉" * 50)
    print("🚀 CARDANO-ARDUINO-AI HACKATHON SETUP 🚀")
    print("🎉" * 50)
    print()

def check_python():
    """Check Python version"""
    print("📋 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ required")
        return False
    
    print("✅ Python version OK")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def check_env_file():
    """Check and create .env file"""
    print("\n⚙️ Checking environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    
    print("📝 Creating .env file...")
    env_content = """# Cardano-Arduino-AI Hackathon Environment
BLOCKFROST_PROJECT_ID=preprodYOUR_KEY_HERE
BLOCKFROST_BASE_URL=https://cardano-preprod.blockfrost.io/api/v0

# Payment modes
PAYMENT_MODE=mock
MOCK_MODE=true

# Service ports
AGENT_A_PORT=8001
AGENT_B_PORT=8002
ROUTER_PORT=8003
PAYMENT_PORT=8000

# Logging
LOG_LEVEL=INFO
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Remember to update BLOCKFROST_PROJECT_ID with your API key")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_imports():
    """Test critical imports"""
    print("\n🧪 Testing critical imports...")
    
    critical_modules = [
        "fastapi",
        "flask", 
        "requests",
        "pydantic",
        "uvicorn"
    ]
    
    failed = []
    for module in critical_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Missing modules: {failed}")
        print("💡 Try: pip install " + " ".join(failed))
        return False
    
    print("✅ All critical imports successful")
    return True

def show_next_steps():
    """Show next steps"""
    print("\n🎯 NEXT STEPS:")
    print("1. Update .env with your Blockfrost API key:")
    print("   BLOCKFROST_PROJECT_ID=preprodYOUR_ACTUAL_KEY")
    print()
    print("2. Start the system:")
    print("   python main.py")
    print()
    print("3. Run the demo:")
    print("   python scripts/demo.py")
    print()
    print("4. Upload Arduino code:")
    print("   - src/arduino/arduino_a.ino → Arduino A")
    print("   - src/arduino/arduino_b.ino → Arduino B")
    print()
    print("🚀 You're ready for the hackathon!")

def main():
    """Main setup function"""
    print_banner()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = True
    
    # Check Python
    if not check_python():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Check env file
    if success and not check_env_file():
        success = False
    
    # Test imports
    if success and not test_imports():
        success = False
    
    if success:
        print("\n🎉 SETUP COMPLETE! 🎉")
        show_next_steps()
    else:
        print("\n❌ Setup failed. Please check errors above.")
        print("💡 Try manually installing: pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())