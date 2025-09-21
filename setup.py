#!/usr/bin/env python3
"""
Setup Script for Unified Arduino-to-Cardano AI Agents System
Helps configure the real blockchain integration
"""

import os
import sys
import requests
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n🔧 Installing requirements...")
    
    requirements_files = [
        "requirements.txt",
        "../Project-dagadaga/blockchain/requirements.txt"
    ]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"📦 Installing from {req_file}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], 
                             check=True, capture_output=True)
                print(f"✅ Installed requirements from {req_file}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Failed to install some packages from {req_file}")
                print(f"   You may need to install them manually")
        else:
            print(f"⚠️  Requirements file not found: {req_file}")

def check_blockfrost_setup():
    """Check if Blockfrost is configured"""
    print("\n🔗 Checking Blockfrost configuration...")
    
    env_file = "../Project-dagadaga/blockchain/.env"
    
    if not os.path.exists(env_file):
        print("❌ No .env file found")
        print("📝 Please copy .env.example to .env and configure it")
        return False
    
    # Read environment file
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        if "your_blockfrost_project_id_here" in env_content:
            print("❌ Blockfrost project ID not configured")
            print("📝 Please edit .env file and add your Blockfrost project ID")
            return False
        
        print("✅ .env file exists and appears configured")
        return True
    
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def test_blockfrost_connection():
    """Test connection to Blockfrost API"""
    print("\n🌐 Testing Blockfrost connection...")
    
    try:
        # Import and test
        sys.path.append("../Project-dagadaga/blockchain/src")
        from blockfrost_client import BlockfrostClient
        
        client = BlockfrostClient()
        network_info = client.get_network_info()
        
        print(f"✅ Connected to Cardano {network_info.get('network_name', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Blockfrost connection failed: {e}")
        print("📝 Please check your Blockfrost project ID in .env file")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Creating .env file...")
    
    env_example = ".env.example"
    env_target = "../Project-dagadaga/blockchain/.env"
    
    if os.path.exists(env_example):
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            # Create target directory if it doesn't exist
            os.makedirs(os.path.dirname(env_target), exist_ok=True)
            
            with open(env_target, 'w') as f:
                f.write(content)
            
            print(f"✅ Created {env_target}")
            print("📝 Please edit this file and add your Blockfrost project ID")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print(f"❌ Template file {env_example} not found")
        return False

def main():
    """Main setup function"""
    print("🚀 Arduino-to-Cardano AI Agents Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    install_requirements()
    
    # Check if .env exists, create if not
    env_file = "../Project-dagadaga/blockchain/.env"
    if not os.path.exists(env_file):
        print("\n📋 No .env file found. Creating from template...")
        if create_env_file():
            print("\n⚠️  NEXT STEPS:")
            print("1. Get a free Blockfrost API key from: https://blockfrost.io/")
            print("2. Create a project for 'Cardano Preprod'")
            print(f"3. Edit {env_file}")
            print("4. Replace 'your_blockfrost_project_id_here' with your actual project ID")
            print("5. Run this setup script again to test the connection")
            print("6. Run main.py to start the system")
            return
    
    # Check Blockfrost setup
    if not check_blockfrost_setup():
        return
    
    # Test connection
    if test_blockfrost_connection():
        print("\n🎉 Setup completed successfully!")
        print("✅ All systems ready for real blockchain integration")
        print("\n🚀 Run 'python main.py' to start the system")
    else:
        print("\n❌ Setup incomplete")
        print("📝 Please check your .env configuration")

if __name__ == "__main__":
    main()