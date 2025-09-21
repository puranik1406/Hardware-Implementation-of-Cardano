#!/usr/bin/env python3
"""
Setup script for Unified Agent System
Installs dependencies and prepares the system for use
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "unified_requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def main():
    """Main setup function"""
    print("\n🚀 Unified Agent System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n🎯 Next steps:")
    print("   1. Run: python unified_agent_system.py")
    print("   2. Answer 'yes' when prompted")
    print("   3. Access: http://localhost:5000/send_request")
    print("\n💡 The system will display the transaction address for ADA payments")

if __name__ == "__main__":
    main()
